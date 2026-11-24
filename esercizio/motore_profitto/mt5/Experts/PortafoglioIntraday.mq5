//+------------------------------------------------------------------+
//| PortafoglioIntraday.mq5 - portafoglio SOLO forex, indici, oro e   |
//| petrolio USOIL (niente crypto, niente altre materie prime).       |
//| Motore Profitto, 05/11/2026. Un solo grafico qualsiasi (es. XAUUSD|
//| M5) + preset: PortafoglioIntraday_F25K (FTMO 25k, simboli FTMO)   |
//| oppure PortafoglioIntraday_R1000 (conto PU 1000 $).               |
//| Dentro: 6 regole intraday (GER40, NAS100 x2, oro, SP500, petrolio)|
//| FlipLotteria (SP500/NAS100/US30), oro news NFP/CPI/FOMC, momentum |
//| su indici + oro + forex + USOIL. Stessi magic di PortafoglioUnico:|
//| NON usarli insieme sullo stesso conto.                            |
//+------------------------------------------------------------------+
#property copyright "Motore Profitto"
#property version   "1.10"
#include <Trade/Trade.mqh>
#property tester_file "news_eventi.csv"

input string Insieme        = "INTRADAY";   // nome del set (solo promemoria)
input bool   UsaIntraday    = true;      // 8 regole intraday (3 moduli)
input bool   UsaFlip        = false;      // FlipLotteria: SP500 compra il calo + NAS100 Noise Area
input bool   UsaNews        = true;      // oro sulle news NFP, CPI, FOMC (3 moduli)
input bool   UsaMomento     = false;      // momentum tra mercati
input double IP_RischioA    = 0.0;      // rischio % a trade regole 6-7 (SP500 e NAS100 NR-ORB)
input double IP_RischioB    = 0.66;      // rischio % a trade regole 3-5-8 (NAS100 prima ora, ETH, petrolio)
input double IP_RischioC    = 0.15;      // rischio % a trade regole 1-2-4 (GER40, BTC, oro fade)
input string IP_Attive_A    = "67";      // regole del gruppo A (cifre 1..8)
input string IP_Attive_B    = "38";      // regole del gruppo B
input string IP_Attive_C    = "14";      // regole del gruppo C
input bool   IP_MinimoSempre = false;     // lotto sotto il minimo: apre il minimo (conti piccoli)
input string IP_Simboli     = "GER40.cash,BTCUSD,US100.cash,XAUUSD,ETHUSD,US500.cash,US100.cash,USOIL.cash"; // simboli regole 1..8
input double FL_Esposizione = 1.26;      // FlipLotteria: esposizione (volte il conto)
input string FL_Suffisso    = ".cash";      // FlipLotteria: suffisso simboli (PU ".s", FTMO ".cash")
input string SR_Simbolo     = "XAUUSD";// oro news: simbolo dell'oro
input double SR_Lotti       = 0.80;      // oro news: lotti
input double MM_Scala       = 0.24;      // momentum: scala nel portafoglio
input string MM_Simboli     = "US30.cash,SPN35.cash,EU50.cash,FRA40.cash,GER40.cash,HK50.cash,US100.cash,JP225.cash,US500.cash,AUS200.cash,US2000.cash,XAUUSD,XAUEUR,EURUSD,GBPUSD,AUDUSD,NZDUSD,USDJPY,USDCHF,USDCAD,USOIL.cash"; // momentum: mercati
input double GS_StopGiorno  = 4;         // GUARDIANO: perdita % nel giorno (dal saldo a mezzanotte server) -> chiude tutto, fermo fino a domani (0 = spento)
input double GS_Obiettivo   = 0;         // GUARDIANO: guadagno % sul saldo di partenza -> chiude tutto e si ferma (fase passata; 0 = spento)
input double GS_SaldoPartenza = 0;       // GUARDIANO: saldo di partenza della fase (0 = saldo all'avvio)
input bool   GS_NewsProporzionali = true; // news oro: lotti che crescono con l'equity (SR_Lotti = lotti al saldo di partenza)
input bool   GS_Registro    = true;      // GUARDIANO: scrive il registro giornaliero in Common\Files

bool PU_Timer(int s) { return true; }
void PU_Kill() { }
void PU_Comment(string a0 = "", string a1 = "", string a2 = "", string a3 = "", string a4 = "", string a5 = "", string a6 = "", string a7 = "", string a8 = "", string a9 = "", string a10 = "", string a11 = "", string a12 = "", string a13 = "", string a14 = "", string a15 = "", string a16 = "", string a17 = "", string a18 = "", string a19 = "", string a20 = "", string a21 = "", string a22 = "", string a23 = "", string a24 = "", string a25 = "", string a26 = "", string a27 = "", string a28 = "", string a29 = "") { }
bool PU_ObjectCreate(long a, string b, ENUM_OBJECT c, int d, datetime e, double f) { return true; }
bool PU_ObjectSetInteger(long a, string b, ENUM_OBJECT_PROPERTY_INTEGER c, long d) { return true; }
bool PU_ObjectSetString(long a, string b, ENUM_OBJECT_PROPERTY_STRING c, string d) { return true; }
bool PU_ObjectDelete(long a, string b) { return true; }
//==================== MODULO IP1_ = IntradayPortafoglio ====================
//+------------------------------------------------------------------+
//| IntradayPortafoglio.mq5 - le 8 regole intraday in UN solo EA     |
//| (Motore Profitto, 02/11/2026). Mettilo su UN grafico qualsiasi.  |
//| Lavora da solo sugli 8 mercati con le barre M5 di ciascuno:      |
//|  1 GER40  fade Londra 30m      5 ETHUSD  IP1_NR-ORB30 New York        |
//|  2 BTCUSD fade NY 15m          6 SP500   IP1_NR-ORB30 New York        |
//|  3 NAS100 prima ora NY 60m     7 NAS100  IP1_NR-ORB30 New York        |
//|  4 XAUUSD fade NY 5m           8 USOUSD  IP1_NR-ORB30 Londra          |
//| Stesse regole e stessi magic (881001-881008) dell'EA Intraday4.  |
//| Rischio = IP1_InpRischio % dell'equity per IP1_trade, 1 IP1_trade al giorno  |
//| per regola, tutto chiuso a fine sessione.                        |
//+------------------------------------------------------------------+

double IP1_InpRischio = 0.5;      // rischio % dell'equity per ogni IP1_trade
string IP1_InpAttive = "12345678"; // regole attive (togli una cifra per spegnerla)
bool IP1_InpMinimoSempre = true; // se il lotto e' sotto il minimo apre comunque il lotto minimo (rischio un po' piu' alto)
string IP1_InpSimboli = "GER40.s,BTCUSD,NAS100.s,XAUUSD.s,ETHUSD,SP500.s,NAS100.s,USOUSD.s"; // simboli delle regole 1..8

#define IP1_NR 8
int    IP1_REG[IP1_NR]   = {1, 2, 3, 4, 5, 5, 5, 5};      // tipo: 1 fade 30 Londra, 2 fade 15 NY, 3 prima ora, 4 fade 5 NY, 5 IP1_NR-ORB30
bool   IP1_LON[IP1_NR]   = {true, false, false, false, false, false, false, true};
string IP1_g_sym[IP1_NR]; bool IP1_g_on[IP1_NR];
int    IP1_g_giorno[IP1_NR]; bool IP1_g_fatto[IP1_NR]; double IP1_g_rh[IP1_NR], IP1_g_rl[IP1_NR], IP1_g_est[IP1_NR]; int IP1_g_rott[IP1_NR];
datetime IP1_g_barra[IP1_NR]; double IP1_g_hs[IP1_NR], IP1_g_ls[IP1_NR]; bool IP1_g_stretta[IP1_NR]; bool IP1_g_primo[IP1_NR];
double IP1_g_rng[IP1_NR][40]; int IP1_g_nr[IP1_NR];
CTrade IP1_trade;

// --- ora legale (server PU = ora di Atene) -------------------------
datetime IP1_Domenica(int anno, int mese, int n)
  {
   MqlDateTime t; t.year = anno; t.mon = mese; t.day = 1; t.hour = 0; t.min = 0; t.sec = 0;
   datetime d = StructToTime(t);
   if(n > 0) { MqlDateTime x; TimeToStruct(d, x); return d + ((7 - x.day_of_week) % 7 + 7 * (n - 1)) * 86400; }
   t.mon = mese + 1; if(t.mon > 12) { t.mon = 1; t.year++; }
   datetime fine = StructToTime(t) - 86400; MqlDateTime y; TimeToStruct(fine, y);
   return fine - y.day_of_week * 86400;
  }
bool IP1_EstateUE(datetime u) { MqlDateTime t; TimeToStruct(u, t); return u >= IP1_Domenica(t.year, 3, -1) + 3600 && u < IP1_Domenica(t.year, 10, -1) + 3600; }
bool IP1_EstateUSA(datetime u) { MqlDateTime t; TimeToStruct(u, t); return u >= IP1_Domenica(t.year, 3, 2) + 7 * 3600 && u < IP1_Domenica(t.year, 11, 1) + 6 * 3600; }
datetime IP1_Locale(datetime server, bool ny)
  {
   datetime u = server - 2 * 3600; if(IP1_EstateUE(u)) u = server - 3 * 3600;
   if(ny) return u - (IP1_EstateUSA(u) ? 4 : 5) * 3600;
   return u + (IP1_EstateUE(u) ? 3600 : 0);
  }

long IP1_Magic(int i) { return 881001 + i; }
bool IP1_InPos(int i)
  {
   for(int k = PositionsTotal() - 1; k >= 0; k--)
      if(PositionGetTicket(k) && PositionGetString(POSITION_SYMBOL) == IP1_g_sym[i] && PositionGetInteger(POSITION_MAGIC) == IP1_Magic(i)) return true;
   return false;
  }
void IP1_Chiudi(int i)
  {
   for(int k = PositionsTotal() - 1; k >= 0; k--)
     {
      ulong t = PositionGetTicket(k);
      if(t && PositionGetString(POSITION_SYMBOL) == IP1_g_sym[i] && PositionGetInteger(POSITION_MAGIC) == IP1_Magic(i))
        { IP1_trade.SetExpertMagicNumber(IP1_Magic(i)); IP1_trade.PositionClose(t); }
     }
  }
double IP1_Lotti(string s, double dist)
  {
   double tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
   if(dist <= 0 || tv <= 0 || ts <= 0) return 0;
   double v = IP1_InpRischio / 100.0 * AccountInfoDouble(ACCOUNT_EQUITY) / (dist / ts * tv);
   double st = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN), mx = SymbolInfoDouble(s, SYMBOL_VOLUME_MAX);
   v = MathFloor(v / st + 1e-9) * st;
   if(v < mn) v = (IP1_InpMinimoSempre || v >= 0.5 * mn) ? mn : 0;
   return NormalizeDouble(MathMin(v, mx), 2);
  }
void IP1_Entra(int i, int lato, double stop)
  {
   string s = IP1_g_sym[i]; IP1_g_fatto[i] = true;
   double px = lato > 0 ? SymbolInfoDouble(s, SYMBOL_ASK) : SymbolInfoDouble(s, SYMBOL_BID);
   if((lato > 0 && stop >= px) || (lato < 0 && stop <= px)) return;
   double l = IP1_Lotti(s, MathAbs(px - stop));
   if(l <= 0) { PrintFormat("Regola %d %s: lotto sotto il minimo, salto", i + 1, s); return; }
   int dig = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   IP1_trade.SetExpertMagicNumber(IP1_Magic(i)); IP1_trade.SetTypeFillingBySymbol(s);
   bool ok = lato > 0 ? IP1_trade.Buy(l, s, 0, NormalizeDouble(stop, dig), 0, "intraday" + IntegerToString(i + 1))
                      : IP1_trade.Sell(l, s, 0, NormalizeDouble(stop, dig), 0, "intraday" + IntegerToString(i + 1));
   PrintFormat("Regola %d %s: %s %.2f lotti, stop %s (%s)", i + 1, s, lato > 0 ? "BUY" : "SELL", l, DoubleToString(stop, dig), ok ? "ok" : IP1_trade.ResultRetcodeDescription());
  }

void IP1_Processa(int i)
  {
   string s = IP1_g_sym[i];
   datetime b = iTime(s, PERIOD_M5, 0);
   if(b == 0 || b == IP1_g_barra[i]) return;
   IP1_g_barra[i] = b;
   bool ny = !IP1_LON[i]; int tipo = IP1_REG[i];
   int inizio = ny ? 9 * 60 + 30 : 8 * 60, fine = ny ? 16 * 60 : 16 * 60 + 30;
   int N = tipo == 1 ? 30 : tipo == 2 ? 15 : tipo == 3 ? 60 : tipo == 5 ? 30 : 5;
   MqlDateTime t; TimeToStruct(IP1_Locale(b, ny), t);
   if(t.day_of_week == 0 || t.day_of_week == 6) return;
   int m = t.hour * 60 + t.min;
   if(t.day_of_year != IP1_g_giorno[i])
     {
      if(tipo == 5) { IP1_Precarica(i, false); IP1_g_hs[i] = 0; }   // 20/11: range dei giorni passati dallo storico M5
      if(IP1_g_hs[i] > 0)
        {
         if(IP1_g_nr[i] < 40) IP1_g_rng[i][IP1_g_nr[i]++] = IP1_g_hs[i] - IP1_g_ls[i];
         else { for(int k = 1; k < 40; k++) IP1_g_rng[i][k - 1] = IP1_g_rng[i][k]; IP1_g_rng[i][39] = IP1_g_hs[i] - IP1_g_ls[i]; }
        }
      int n = IP1_g_nr[i]; double media = 0; int k0 = MathMax(0, n - 11);
      for(int k = k0; k < n - 1; k++) media += IP1_g_rng[i][k];
      IP1_g_stretta[i] = (n >= 11) && IP1_g_rng[i][n - 1] < 0.7 * media / (n - 1 - k0);
      if(tipo == 5 && IP1_g_on[i] && n >= 11) PrintFormat("Regola %d %s: range ieri %.3f, soglia %.3f -> %s", i + 1, IP1_g_sym[i], IP1_g_rng[i][n - 1], 0.7 * media / (n - 1 - k0), IP1_g_stretta[i] ? "giorno calmo, attiva" : "salta oggi");
      IP1_g_giorno[i] = t.day_of_year; IP1_g_fatto[i] = false; IP1_g_rott[i] = 0; IP1_g_rh[i] = 0; IP1_g_rl[i] = 0; IP1_g_hs[i] = 0; IP1_g_ls[i] = 0;
     }
   if(m >= fine) { if(IP1_InPos(i)) IP1_Chiudi(i); return; }
   if(m > inizio)
     {
      double hh = iHigh(s, PERIOD_M5, 1), ll = iLow(s, PERIOD_M5, 1);
      IP1_g_hs[i] = IP1_g_hs[i] == 0 ? hh : MathMax(IP1_g_hs[i], hh); IP1_g_ls[i] = IP1_g_ls[i] == 0 ? ll : MathMin(IP1_g_ls[i], ll);
     }
   if(m < inizio + N || !IP1_g_on[i]) return;
   int nb = (m - inizio) / 5;
   double o[], h[], l[], c[];
   if(CopyOpen(s, PERIOD_M5, 1, nb, o) < nb || CopyHigh(s, PERIOD_M5, 1, nb, h) < nb || CopyLow(s, PERIOD_M5, 1, nb, l) < nb || CopyClose(s, PERIOD_M5, 1, nb, c) < nb) return;
   int k = N / 5;
   if(IP1_g_rh[i] == 0) { IP1_g_rh[i] = h[ArrayMaximum(h, 0, k)]; IP1_g_rl[i] = l[ArrayMinimum(l, 0, k)]; }
   if(IP1_g_fatto[i]) return;
   double ultima = c[nb - 1];
   // avvio a sessione gia' iniziata: se il segnale di oggi e' gia' scattato su una barra precedente, oggi non entra piu'
   if(IP1_g_primo[i])
     {
      IP1_g_primo[i] = false;
      if(nb > k)
        {
         if(tipo == 3) { IP1_g_fatto[i] = true; return; }
         int rott = 0;
         for(int q = k; q < nb - 1; q++)
           {
            if(tipo == 5) { if(c[q] > IP1_g_rh[i] || c[q] < IP1_g_rl[i]) { IP1_g_fatto[i] = true; return; } continue; }
            if(rott == 0) { if(c[q] > IP1_g_rh[i]) { rott = 1; IP1_g_est[i] = h[q]; } else if(c[q] < IP1_g_rl[i]) { rott = -1; IP1_g_est[i] = l[q]; } continue; }
            IP1_g_est[i] = rott > 0 ? MathMax(IP1_g_est[i], h[q]) : MathMin(IP1_g_est[i], l[q]);
            if((rott > 0 && c[q] < IP1_g_rh[i]) || (rott < 0 && c[q] > IP1_g_rl[i])) { IP1_g_fatto[i] = true; return; }
           }
         IP1_g_rott[i] = rott;
        }
     }
   if(tipo == 5)
     {
      if(!IP1_g_stretta[i]) { IP1_g_fatto[i] = true; return; }
      if(ultima > IP1_g_rh[i]) IP1_Entra(i, 1, IP1_g_rl[i]); else if(ultima < IP1_g_rl[i]) IP1_Entra(i, -1, IP1_g_rh[i]);
      return;
     }
   if(tipo == 3)
     {
      if(nb == k) { int lato = c[k - 1] > o[0] ? 1 : -1; IP1_Entra(i, lato, lato > 0 ? IP1_g_rl[i] : IP1_g_rh[i]); }
      return;
     }
   if(IP1_g_rott[i] == 0)
     {
      if(ultima > IP1_g_rh[i]) { IP1_g_rott[i] = 1; IP1_g_est[i] = h[nb - 1]; }
      else if(ultima < IP1_g_rl[i]) { IP1_g_rott[i] = -1; IP1_g_est[i] = l[nb - 1]; }
      return;
     }
   IP1_g_est[i] = IP1_g_rott[i] > 0 ? MathMax(IP1_g_est[i], h[nb - 1]) : MathMin(IP1_g_est[i], l[nb - 1]);
   if((IP1_g_rott[i] > 0 && ultima < IP1_g_rh[i]) || (IP1_g_rott[i] < 0 && ultima > IP1_g_rl[i]))
     {
      double sp = SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID);
      IP1_Entra(i, -IP1_g_rott[i], IP1_g_rott[i] > 0 ? IP1_g_est[i] + sp : IP1_g_est[i]);
     }
  }


// all'avvio: range delle ultime sessioni dallo storico M5 (serve alle regole IP1_NR-ORB per non aspettare 2 settimane)
void IP1_Precarica(int i, bool stampa = true)
  {
   IP1_g_nr[i] = 0;   // 20/11: ricalcolo completo dallo storico
   MqlRates r[]; int n = CopyRates(IP1_g_sym[i], PERIOD_M5, 0, 12000, r);
   if(n <= 0) return;
   bool ny = !IP1_LON[i]; int inizio = ny ? 9 * 60 + 30 : 8 * 60, fine = ny ? 16 * 60 : 16 * 60 + 30;
   int giorno = -1; double hs = 0, ls = 0;
   for(int k = 0; k < n; k++)
     {
      MqlDateTime t; TimeToStruct(IP1_Locale(r[k].time, ny), t);
      if(t.day_of_week == 0 || t.day_of_week == 6) continue;
      MqlDateTime tc; TimeToStruct(IP1_Locale(r[k].time + 300, ny), tc); int m = tc.hour * 60 + tc.min;   // 20/11: ora di CHIUSURA della candela
      if(t.day_of_year != giorno)
        {
         if(hs > 0 && k < n - 1) { if(IP1_g_nr[i] < 40) IP1_g_rng[i][IP1_g_nr[i]++] = hs - ls; else { for(int q = 1; q < 40; q++) IP1_g_rng[i][q - 1] = IP1_g_rng[i][q]; IP1_g_rng[i][39] = hs - ls; } }
         giorno = t.day_of_year; hs = 0; ls = 0;
        }
      if(m > inizio && m < fine) { hs = hs == 0 ? r[k].high : MathMax(hs, r[k].high); ls = ls == 0 ? r[k].low : MathMin(ls, r[k].low); }
     }
   // 20/11: l'ultima sessione dello storico conta se e' gia' finita (giorno diverso da oggi), es. il venerdi' quando parte nel weekend
   MqlDateTime oggi; TimeToStruct(IP1_Locale(TimeTradeServer(), ny), oggi);
   if(hs > 0 && giorno != oggi.day_of_year) { if(IP1_g_nr[i] < 40) IP1_g_rng[i][IP1_g_nr[i]++] = hs - ls; else { for(int q = 1; q < 40; q++) IP1_g_rng[i][q - 1] = IP1_g_rng[i][q]; IP1_g_rng[i][39] = hs - ls; } }
   if(!stampa) return;
   PrintFormat("Regola %d %s: caricate %d sessioni passate", i + 1, IP1_g_sym[i], IP1_g_nr[i]);
  }

int IP1_OnInit()
  {
   string parti[]; if(StringSplit(IP1_InpSimboli, ',', parti) != IP1_NR) { Print("InpSimboli: servono 8 simboli separati da virgola"); return INIT_PARAMETERS_INCORRECT; }
   for(int i = 0; i < IP1_NR; i++)
     {
      IP1_g_sym[i] = parti[i]; StringTrimLeft(IP1_g_sym[i]); StringTrimRight(IP1_g_sym[i]);
      IP1_g_on[i] = StringFind(IP1_InpAttive, IntegerToString(i + 1)) >= 0;
      IP1_g_giorno[i] = -1; IP1_g_barra[i] = 0; IP1_g_nr[i] = 0; IP1_g_primo[i] = true; IP1_g_hs[i] = 0; IP1_g_ls[i] = 0; IP1_g_stretta[i] = false;
      if(!SymbolSelect(IP1_g_sym[i], true)) PrintFormat("ATTENZIONE: simbolo %s non trovato (regola %d)", IP1_g_sym[i], i + 1);
      else if(IP1_REG[i] == 5) IP1_Precarica(i);
     }
   IP1_trade.SetDeviationInPoints(50);
   PU_Timer(2);
   PrintFormat("IntradayPortafoglio avviato: regole attive %s, rischio %.2f%% a IP1_trade", IP1_InpAttive, IP1_InpRischio);
   return INIT_SUCCEEDED;
  }
void IP1_OnDeinit(const int r) { PU_Kill(); PU_Comment(""); }
void IP1_OnTimer()
  {
   string riga = "IntradayPortafoglio - rischio " + DoubleToString(IP1_InpRischio, 2) + "%\n";
   for(int i = 0; i < IP1_NR; i++)
     {
      IP1_Processa(i);
      riga += StringFormat("%d %s: %s%s\n", i + 1, IP1_g_sym[i], IP1_g_on[i] ? "attiva" : "spenta", IP1_InPos(i) ? " - IN POSIZIONE" : (IP1_g_fatto[i] ? " - fatto oggi" : ""));
     }
   PU_Comment(riga);
  }
void IP1_OnTick() {}

//==================== MODULO IP2_ = IntradayPortafoglio ====================
//+------------------------------------------------------------------+
//| IntradayPortafoglio.mq5 - le 8 regole intraday in UN solo EA     |
//| (Motore Profitto, 02/11/2026). Mettilo su UN grafico qualsiasi.  |
//| Lavora da solo sugli 8 mercati con le barre M5 di ciascuno:      |
//|  1 GER40  fade Londra 30m      5 ETHUSD  IP2_NR-ORB30 New York        |
//|  2 BTCUSD fade NY 15m          6 SP500   IP2_NR-ORB30 New York        |
//|  3 NAS100 prima ora NY 60m     7 NAS100  IP2_NR-ORB30 New York        |
//|  4 XAUUSD fade NY 5m           8 USOUSD  IP2_NR-ORB30 Londra          |
//| Stesse regole e stessi magic (881001-881008) dell'EA Intraday4.  |
//| Rischio = IP2_InpRischio % dell'equity per IP2_trade, 1 IP2_trade al giorno  |
//| per regola, tutto chiuso a fine sessione.                        |
//+------------------------------------------------------------------+

double IP2_InpRischio = 0.5;      // rischio % dell'equity per ogni IP2_trade
string IP2_InpAttive = "12345678"; // regole attive (togli una cifra per spegnerla)
bool IP2_InpMinimoSempre = true; // se il lotto e' sotto il minimo apre comunque il lotto minimo (rischio un po' piu' alto)
string IP2_InpSimboli = "GER40.s,BTCUSD,NAS100.s,XAUUSD.s,ETHUSD,SP500.s,NAS100.s,USOUSD.s"; // simboli delle regole 1..8

#define IP2_NR 8
int    IP2_REG[IP2_NR]   = {1, 2, 3, 4, 5, 5, 5, 5};      // tipo: 1 fade 30 Londra, 2 fade 15 NY, 3 prima ora, 4 fade 5 NY, 5 IP2_NR-ORB30
bool   IP2_LON[IP2_NR]   = {true, false, false, false, false, false, false, true};
string IP2_g_sym[IP2_NR]; bool IP2_g_on[IP2_NR];
int    IP2_g_giorno[IP2_NR]; bool IP2_g_fatto[IP2_NR]; double IP2_g_rh[IP2_NR], IP2_g_rl[IP2_NR], IP2_g_est[IP2_NR]; int IP2_g_rott[IP2_NR];
datetime IP2_g_barra[IP2_NR]; double IP2_g_hs[IP2_NR], IP2_g_ls[IP2_NR]; bool IP2_g_stretta[IP2_NR]; bool IP2_g_primo[IP2_NR];
double IP2_g_rng[IP2_NR][40]; int IP2_g_nr[IP2_NR];
CTrade IP2_trade;

// --- ora legale (server PU = ora di Atene) -------------------------
datetime IP2_Domenica(int anno, int mese, int n)
  {
   MqlDateTime t; t.year = anno; t.mon = mese; t.day = 1; t.hour = 0; t.min = 0; t.sec = 0;
   datetime d = StructToTime(t);
   if(n > 0) { MqlDateTime x; TimeToStruct(d, x); return d + ((7 - x.day_of_week) % 7 + 7 * (n - 1)) * 86400; }
   t.mon = mese + 1; if(t.mon > 12) { t.mon = 1; t.year++; }
   datetime fine = StructToTime(t) - 86400; MqlDateTime y; TimeToStruct(fine, y);
   return fine - y.day_of_week * 86400;
  }
bool IP2_EstateUE(datetime u) { MqlDateTime t; TimeToStruct(u, t); return u >= IP2_Domenica(t.year, 3, -1) + 3600 && u < IP2_Domenica(t.year, 10, -1) + 3600; }
bool IP2_EstateUSA(datetime u) { MqlDateTime t; TimeToStruct(u, t); return u >= IP2_Domenica(t.year, 3, 2) + 7 * 3600 && u < IP2_Domenica(t.year, 11, 1) + 6 * 3600; }
datetime IP2_Locale(datetime server, bool ny)
  {
   datetime u = server - 2 * 3600; if(IP2_EstateUE(u)) u = server - 3 * 3600;
   if(ny) return u - (IP2_EstateUSA(u) ? 4 : 5) * 3600;
   return u + (IP2_EstateUE(u) ? 3600 : 0);
  }

long IP2_Magic(int i) { return 881001 + i; }
bool IP2_InPos(int i)
  {
   for(int k = PositionsTotal() - 1; k >= 0; k--)
      if(PositionGetTicket(k) && PositionGetString(POSITION_SYMBOL) == IP2_g_sym[i] && PositionGetInteger(POSITION_MAGIC) == IP2_Magic(i)) return true;
   return false;
  }
void IP2_Chiudi(int i)
  {
   for(int k = PositionsTotal() - 1; k >= 0; k--)
     {
      ulong t = PositionGetTicket(k);
      if(t && PositionGetString(POSITION_SYMBOL) == IP2_g_sym[i] && PositionGetInteger(POSITION_MAGIC) == IP2_Magic(i))
        { IP2_trade.SetExpertMagicNumber(IP2_Magic(i)); IP2_trade.PositionClose(t); }
     }
  }
double IP2_Lotti(string s, double dist)
  {
   double tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
   if(dist <= 0 || tv <= 0 || ts <= 0) return 0;
   double v = IP2_InpRischio / 100.0 * AccountInfoDouble(ACCOUNT_EQUITY) / (dist / ts * tv);
   double st = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN), mx = SymbolInfoDouble(s, SYMBOL_VOLUME_MAX);
   v = MathFloor(v / st + 1e-9) * st;
   if(v < mn) v = (IP2_InpMinimoSempre || v >= 0.5 * mn) ? mn : 0;
   return NormalizeDouble(MathMin(v, mx), 2);
  }
void IP2_Entra(int i, int lato, double stop)
  {
   string s = IP2_g_sym[i]; IP2_g_fatto[i] = true;
   double px = lato > 0 ? SymbolInfoDouble(s, SYMBOL_ASK) : SymbolInfoDouble(s, SYMBOL_BID);
   if((lato > 0 && stop >= px) || (lato < 0 && stop <= px)) return;
   double l = IP2_Lotti(s, MathAbs(px - stop));
   if(l <= 0) { PrintFormat("Regola %d %s: lotto sotto il minimo, salto", i + 1, s); return; }
   int dig = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   IP2_trade.SetExpertMagicNumber(IP2_Magic(i)); IP2_trade.SetTypeFillingBySymbol(s);
   bool ok = lato > 0 ? IP2_trade.Buy(l, s, 0, NormalizeDouble(stop, dig), 0, "intraday" + IntegerToString(i + 1))
                      : IP2_trade.Sell(l, s, 0, NormalizeDouble(stop, dig), 0, "intraday" + IntegerToString(i + 1));
   PrintFormat("Regola %d %s: %s %.2f lotti, stop %s (%s)", i + 1, s, lato > 0 ? "BUY" : "SELL", l, DoubleToString(stop, dig), ok ? "ok" : IP2_trade.ResultRetcodeDescription());
  }

void IP2_Processa(int i)
  {
   string s = IP2_g_sym[i];
   datetime b = iTime(s, PERIOD_M5, 0);
   if(b == 0 || b == IP2_g_barra[i]) return;
   IP2_g_barra[i] = b;
   bool ny = !IP2_LON[i]; int tipo = IP2_REG[i];
   int inizio = ny ? 9 * 60 + 30 : 8 * 60, fine = ny ? 16 * 60 : 16 * 60 + 30;
   int N = tipo == 1 ? 30 : tipo == 2 ? 15 : tipo == 3 ? 60 : tipo == 5 ? 30 : 5;
   MqlDateTime t; TimeToStruct(IP2_Locale(b, ny), t);
   if(t.day_of_week == 0 || t.day_of_week == 6) return;
   int m = t.hour * 60 + t.min;
   if(t.day_of_year != IP2_g_giorno[i])
     {
      if(tipo == 5) { IP2_Precarica(i, false); IP2_g_hs[i] = 0; }   // 20/11: range dei giorni passati dallo storico M5
      if(IP2_g_hs[i] > 0)
        {
         if(IP2_g_nr[i] < 40) IP2_g_rng[i][IP2_g_nr[i]++] = IP2_g_hs[i] - IP2_g_ls[i];
         else { for(int k = 1; k < 40; k++) IP2_g_rng[i][k - 1] = IP2_g_rng[i][k]; IP2_g_rng[i][39] = IP2_g_hs[i] - IP2_g_ls[i]; }
        }
      int n = IP2_g_nr[i]; double media = 0; int k0 = MathMax(0, n - 11);
      for(int k = k0; k < n - 1; k++) media += IP2_g_rng[i][k];
      IP2_g_stretta[i] = (n >= 11) && IP2_g_rng[i][n - 1] < 0.7 * media / (n - 1 - k0);
      if(tipo == 5 && IP2_g_on[i] && n >= 11) PrintFormat("Regola %d %s: range ieri %.3f, soglia %.3f -> %s", i + 1, IP2_g_sym[i], IP2_g_rng[i][n - 1], 0.7 * media / (n - 1 - k0), IP2_g_stretta[i] ? "giorno calmo, attiva" : "salta oggi");
      IP2_g_giorno[i] = t.day_of_year; IP2_g_fatto[i] = false; IP2_g_rott[i] = 0; IP2_g_rh[i] = 0; IP2_g_rl[i] = 0; IP2_g_hs[i] = 0; IP2_g_ls[i] = 0;
     }
   if(m >= fine) { if(IP2_InPos(i)) IP2_Chiudi(i); return; }
   if(m > inizio)
     {
      double hh = iHigh(s, PERIOD_M5, 1), ll = iLow(s, PERIOD_M5, 1);
      IP2_g_hs[i] = IP2_g_hs[i] == 0 ? hh : MathMax(IP2_g_hs[i], hh); IP2_g_ls[i] = IP2_g_ls[i] == 0 ? ll : MathMin(IP2_g_ls[i], ll);
     }
   if(m < inizio + N || !IP2_g_on[i]) return;
   int nb = (m - inizio) / 5;
   double o[], h[], l[], c[];
   if(CopyOpen(s, PERIOD_M5, 1, nb, o) < nb || CopyHigh(s, PERIOD_M5, 1, nb, h) < nb || CopyLow(s, PERIOD_M5, 1, nb, l) < nb || CopyClose(s, PERIOD_M5, 1, nb, c) < nb) return;
   int k = N / 5;
   if(IP2_g_rh[i] == 0) { IP2_g_rh[i] = h[ArrayMaximum(h, 0, k)]; IP2_g_rl[i] = l[ArrayMinimum(l, 0, k)]; }
   if(IP2_g_fatto[i]) return;
   double ultima = c[nb - 1];
   // avvio a sessione gia' iniziata: se il segnale di oggi e' gia' scattato su una barra precedente, oggi non entra piu'
   if(IP2_g_primo[i])
     {
      IP2_g_primo[i] = false;
      if(nb > k)
        {
         if(tipo == 3) { IP2_g_fatto[i] = true; return; }
         int rott = 0;
         for(int q = k; q < nb - 1; q++)
           {
            if(tipo == 5) { if(c[q] > IP2_g_rh[i] || c[q] < IP2_g_rl[i]) { IP2_g_fatto[i] = true; return; } continue; }
            if(rott == 0) { if(c[q] > IP2_g_rh[i]) { rott = 1; IP2_g_est[i] = h[q]; } else if(c[q] < IP2_g_rl[i]) { rott = -1; IP2_g_est[i] = l[q]; } continue; }
            IP2_g_est[i] = rott > 0 ? MathMax(IP2_g_est[i], h[q]) : MathMin(IP2_g_est[i], l[q]);
            if((rott > 0 && c[q] < IP2_g_rh[i]) || (rott < 0 && c[q] > IP2_g_rl[i])) { IP2_g_fatto[i] = true; return; }
           }
         IP2_g_rott[i] = rott;
        }
     }
   if(tipo == 5)
     {
      if(!IP2_g_stretta[i]) { IP2_g_fatto[i] = true; return; }
      if(ultima > IP2_g_rh[i]) IP2_Entra(i, 1, IP2_g_rl[i]); else if(ultima < IP2_g_rl[i]) IP2_Entra(i, -1, IP2_g_rh[i]);
      return;
     }
   if(tipo == 3)
     {
      if(nb == k) { int lato = c[k - 1] > o[0] ? 1 : -1; IP2_Entra(i, lato, lato > 0 ? IP2_g_rl[i] : IP2_g_rh[i]); }
      return;
     }
   if(IP2_g_rott[i] == 0)
     {
      if(ultima > IP2_g_rh[i]) { IP2_g_rott[i] = 1; IP2_g_est[i] = h[nb - 1]; }
      else if(ultima < IP2_g_rl[i]) { IP2_g_rott[i] = -1; IP2_g_est[i] = l[nb - 1]; }
      return;
     }
   IP2_g_est[i] = IP2_g_rott[i] > 0 ? MathMax(IP2_g_est[i], h[nb - 1]) : MathMin(IP2_g_est[i], l[nb - 1]);
   if((IP2_g_rott[i] > 0 && ultima < IP2_g_rh[i]) || (IP2_g_rott[i] < 0 && ultima > IP2_g_rl[i]))
     {
      double sp = SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID);
      IP2_Entra(i, -IP2_g_rott[i], IP2_g_rott[i] > 0 ? IP2_g_est[i] + sp : IP2_g_est[i]);
     }
  }


// all'avvio: range delle ultime sessioni dallo storico M5 (serve alle regole IP2_NR-ORB per non aspettare 2 settimane)
void IP2_Precarica(int i, bool stampa = true)
  {
   IP2_g_nr[i] = 0;   // 20/11: ricalcolo completo dallo storico
   MqlRates r[]; int n = CopyRates(IP2_g_sym[i], PERIOD_M5, 0, 12000, r);
   if(n <= 0) return;
   bool ny = !IP2_LON[i]; int inizio = ny ? 9 * 60 + 30 : 8 * 60, fine = ny ? 16 * 60 : 16 * 60 + 30;
   int giorno = -1; double hs = 0, ls = 0;
   for(int k = 0; k < n; k++)
     {
      MqlDateTime t; TimeToStruct(IP2_Locale(r[k].time, ny), t);
      if(t.day_of_week == 0 || t.day_of_week == 6) continue;
      MqlDateTime tc; TimeToStruct(IP2_Locale(r[k].time + 300, ny), tc); int m = tc.hour * 60 + tc.min;   // 20/11: ora di CHIUSURA della candela
      if(t.day_of_year != giorno)
        {
         if(hs > 0 && k < n - 1) { if(IP2_g_nr[i] < 40) IP2_g_rng[i][IP2_g_nr[i]++] = hs - ls; else { for(int q = 1; q < 40; q++) IP2_g_rng[i][q - 1] = IP2_g_rng[i][q]; IP2_g_rng[i][39] = hs - ls; } }
         giorno = t.day_of_year; hs = 0; ls = 0;
        }
      if(m > inizio && m < fine) { hs = hs == 0 ? r[k].high : MathMax(hs, r[k].high); ls = ls == 0 ? r[k].low : MathMin(ls, r[k].low); }
     }
   // 20/11: l'ultima sessione dello storico conta se e' gia' finita (giorno diverso da oggi), es. il venerdi' quando parte nel weekend
   MqlDateTime oggi; TimeToStruct(IP2_Locale(TimeTradeServer(), ny), oggi);
   if(hs > 0 && giorno != oggi.day_of_year) { if(IP2_g_nr[i] < 40) IP2_g_rng[i][IP2_g_nr[i]++] = hs - ls; else { for(int q = 1; q < 40; q++) IP2_g_rng[i][q - 1] = IP2_g_rng[i][q]; IP2_g_rng[i][39] = hs - ls; } }
   if(!stampa) return;
   PrintFormat("Regola %d %s: caricate %d sessioni passate", i + 1, IP2_g_sym[i], IP2_g_nr[i]);
  }

int IP2_OnInit()
  {
   string parti[]; if(StringSplit(IP2_InpSimboli, ',', parti) != IP2_NR) { Print("InpSimboli: servono 8 simboli separati da virgola"); return INIT_PARAMETERS_INCORRECT; }
   for(int i = 0; i < IP2_NR; i++)
     {
      IP2_g_sym[i] = parti[i]; StringTrimLeft(IP2_g_sym[i]); StringTrimRight(IP2_g_sym[i]);
      IP2_g_on[i] = StringFind(IP2_InpAttive, IntegerToString(i + 1)) >= 0;
      IP2_g_giorno[i] = -1; IP2_g_barra[i] = 0; IP2_g_nr[i] = 0; IP2_g_primo[i] = true; IP2_g_hs[i] = 0; IP2_g_ls[i] = 0; IP2_g_stretta[i] = false;
      if(!SymbolSelect(IP2_g_sym[i], true)) PrintFormat("ATTENZIONE: simbolo %s non trovato (regola %d)", IP2_g_sym[i], i + 1);
      else if(IP2_REG[i] == 5) IP2_Precarica(i);
     }
   IP2_trade.SetDeviationInPoints(50);
   PU_Timer(2);
   PrintFormat("IntradayPortafoglio avviato: regole attive %s, rischio %.2f%% a IP2_trade", IP2_InpAttive, IP2_InpRischio);
   return INIT_SUCCEEDED;
  }
void IP2_OnDeinit(const int r) { PU_Kill(); PU_Comment(""); }
void IP2_OnTimer()
  {
   string riga = "IntradayPortafoglio - rischio " + DoubleToString(IP2_InpRischio, 2) + "%\n";
   for(int i = 0; i < IP2_NR; i++)
     {
      IP2_Processa(i);
      riga += StringFormat("%d %s: %s%s\n", i + 1, IP2_g_sym[i], IP2_g_on[i] ? "attiva" : "spenta", IP2_InPos(i) ? " - IN POSIZIONE" : (IP2_g_fatto[i] ? " - fatto oggi" : ""));
     }
   PU_Comment(riga);
  }
void IP2_OnTick() {}

//==================== MODULO IP3_ = IntradayPortafoglio ====================
//+------------------------------------------------------------------+
//| IntradayPortafoglio.mq5 - le 8 regole intraday in UN solo EA     |
//| (Motore Profitto, 02/11/2026). Mettilo su UN grafico qualsiasi.  |
//| Lavora da solo sugli 8 mercati con le barre M5 di ciascuno:      |
//|  1 GER40  fade Londra 30m      5 ETHUSD  IP3_NR-ORB30 New York        |
//|  2 BTCUSD fade NY 15m          6 SP500   IP3_NR-ORB30 New York        |
//|  3 NAS100 prima ora NY 60m     7 NAS100  IP3_NR-ORB30 New York        |
//|  4 XAUUSD fade NY 5m           8 USOUSD  IP3_NR-ORB30 Londra          |
//| Stesse regole e stessi magic (881001-881008) dell'EA Intraday4.  |
//| Rischio = IP3_InpRischio % dell'equity per IP3_trade, 1 IP3_trade al giorno  |
//| per regola, tutto chiuso a fine sessione.                        |
//+------------------------------------------------------------------+

double IP3_InpRischio = 0.5;      // rischio % dell'equity per ogni IP3_trade
string IP3_InpAttive = "12345678"; // regole attive (togli una cifra per spegnerla)
bool IP3_InpMinimoSempre = true; // se il lotto e' sotto il minimo apre comunque il lotto minimo (rischio un po' piu' alto)
string IP3_InpSimboli = "GER40.s,BTCUSD,NAS100.s,XAUUSD.s,ETHUSD,SP500.s,NAS100.s,USOUSD.s"; // simboli delle regole 1..8

#define IP3_NR 8
int    IP3_REG[IP3_NR]   = {1, 2, 3, 4, 5, 5, 5, 5};      // tipo: 1 fade 30 Londra, 2 fade 15 NY, 3 prima ora, 4 fade 5 NY, 5 IP3_NR-ORB30
bool   IP3_LON[IP3_NR]   = {true, false, false, false, false, false, false, true};
string IP3_g_sym[IP3_NR]; bool IP3_g_on[IP3_NR];
int    IP3_g_giorno[IP3_NR]; bool IP3_g_fatto[IP3_NR]; double IP3_g_rh[IP3_NR], IP3_g_rl[IP3_NR], IP3_g_est[IP3_NR]; int IP3_g_rott[IP3_NR];
datetime IP3_g_barra[IP3_NR]; double IP3_g_hs[IP3_NR], IP3_g_ls[IP3_NR]; bool IP3_g_stretta[IP3_NR]; bool IP3_g_primo[IP3_NR];
double IP3_g_rng[IP3_NR][40]; int IP3_g_nr[IP3_NR];
CTrade IP3_trade;

// --- ora legale (server PU = ora di Atene) -------------------------
datetime IP3_Domenica(int anno, int mese, int n)
  {
   MqlDateTime t; t.year = anno; t.mon = mese; t.day = 1; t.hour = 0; t.min = 0; t.sec = 0;
   datetime d = StructToTime(t);
   if(n > 0) { MqlDateTime x; TimeToStruct(d, x); return d + ((7 - x.day_of_week) % 7 + 7 * (n - 1)) * 86400; }
   t.mon = mese + 1; if(t.mon > 12) { t.mon = 1; t.year++; }
   datetime fine = StructToTime(t) - 86400; MqlDateTime y; TimeToStruct(fine, y);
   return fine - y.day_of_week * 86400;
  }
bool IP3_EstateUE(datetime u) { MqlDateTime t; TimeToStruct(u, t); return u >= IP3_Domenica(t.year, 3, -1) + 3600 && u < IP3_Domenica(t.year, 10, -1) + 3600; }
bool IP3_EstateUSA(datetime u) { MqlDateTime t; TimeToStruct(u, t); return u >= IP3_Domenica(t.year, 3, 2) + 7 * 3600 && u < IP3_Domenica(t.year, 11, 1) + 6 * 3600; }
datetime IP3_Locale(datetime server, bool ny)
  {
   datetime u = server - 2 * 3600; if(IP3_EstateUE(u)) u = server - 3 * 3600;
   if(ny) return u - (IP3_EstateUSA(u) ? 4 : 5) * 3600;
   return u + (IP3_EstateUE(u) ? 3600 : 0);
  }

long IP3_Magic(int i) { return 881001 + i; }
bool IP3_InPos(int i)
  {
   for(int k = PositionsTotal() - 1; k >= 0; k--)
      if(PositionGetTicket(k) && PositionGetString(POSITION_SYMBOL) == IP3_g_sym[i] && PositionGetInteger(POSITION_MAGIC) == IP3_Magic(i)) return true;
   return false;
  }
void IP3_Chiudi(int i)
  {
   for(int k = PositionsTotal() - 1; k >= 0; k--)
     {
      ulong t = PositionGetTicket(k);
      if(t && PositionGetString(POSITION_SYMBOL) == IP3_g_sym[i] && PositionGetInteger(POSITION_MAGIC) == IP3_Magic(i))
        { IP3_trade.SetExpertMagicNumber(IP3_Magic(i)); IP3_trade.PositionClose(t); }
     }
  }
double IP3_Lotti(string s, double dist)
  {
   double tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
   if(dist <= 0 || tv <= 0 || ts <= 0) return 0;
   double v = IP3_InpRischio / 100.0 * AccountInfoDouble(ACCOUNT_EQUITY) / (dist / ts * tv);
   double st = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN), mx = SymbolInfoDouble(s, SYMBOL_VOLUME_MAX);
   v = MathFloor(v / st + 1e-9) * st;
   if(v < mn) v = (IP3_InpMinimoSempre || v >= 0.5 * mn) ? mn : 0;
   return NormalizeDouble(MathMin(v, mx), 2);
  }
void IP3_Entra(int i, int lato, double stop)
  {
   string s = IP3_g_sym[i]; IP3_g_fatto[i] = true;
   double px = lato > 0 ? SymbolInfoDouble(s, SYMBOL_ASK) : SymbolInfoDouble(s, SYMBOL_BID);
   if((lato > 0 && stop >= px) || (lato < 0 && stop <= px)) return;
   double l = IP3_Lotti(s, MathAbs(px - stop));
   if(l <= 0) { PrintFormat("Regola %d %s: lotto sotto il minimo, salto", i + 1, s); return; }
   int dig = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   IP3_trade.SetExpertMagicNumber(IP3_Magic(i)); IP3_trade.SetTypeFillingBySymbol(s);
   bool ok = lato > 0 ? IP3_trade.Buy(l, s, 0, NormalizeDouble(stop, dig), 0, "intraday" + IntegerToString(i + 1))
                      : IP3_trade.Sell(l, s, 0, NormalizeDouble(stop, dig), 0, "intraday" + IntegerToString(i + 1));
   PrintFormat("Regola %d %s: %s %.2f lotti, stop %s (%s)", i + 1, s, lato > 0 ? "BUY" : "SELL", l, DoubleToString(stop, dig), ok ? "ok" : IP3_trade.ResultRetcodeDescription());
  }

void IP3_Processa(int i)
  {
   string s = IP3_g_sym[i];
   datetime b = iTime(s, PERIOD_M5, 0);
   if(b == 0 || b == IP3_g_barra[i]) return;
   IP3_g_barra[i] = b;
   bool ny = !IP3_LON[i]; int tipo = IP3_REG[i];
   int inizio = ny ? 9 * 60 + 30 : 8 * 60, fine = ny ? 16 * 60 : 16 * 60 + 30;
   int N = tipo == 1 ? 30 : tipo == 2 ? 15 : tipo == 3 ? 60 : tipo == 5 ? 30 : 5;
   MqlDateTime t; TimeToStruct(IP3_Locale(b, ny), t);
   if(t.day_of_week == 0 || t.day_of_week == 6) return;
   int m = t.hour * 60 + t.min;
   if(t.day_of_year != IP3_g_giorno[i])
     {
      if(tipo == 5) { IP3_Precarica(i, false); IP3_g_hs[i] = 0; }   // 20/11: range dei giorni passati dallo storico M5
      if(IP3_g_hs[i] > 0)
        {
         if(IP3_g_nr[i] < 40) IP3_g_rng[i][IP3_g_nr[i]++] = IP3_g_hs[i] - IP3_g_ls[i];
         else { for(int k = 1; k < 40; k++) IP3_g_rng[i][k - 1] = IP3_g_rng[i][k]; IP3_g_rng[i][39] = IP3_g_hs[i] - IP3_g_ls[i]; }
        }
      int n = IP3_g_nr[i]; double media = 0; int k0 = MathMax(0, n - 11);
      for(int k = k0; k < n - 1; k++) media += IP3_g_rng[i][k];
      IP3_g_stretta[i] = (n >= 11) && IP3_g_rng[i][n - 1] < 0.7 * media / (n - 1 - k0);
      if(tipo == 5 && IP3_g_on[i] && n >= 11) PrintFormat("Regola %d %s: range ieri %.3f, soglia %.3f -> %s", i + 1, IP3_g_sym[i], IP3_g_rng[i][n - 1], 0.7 * media / (n - 1 - k0), IP3_g_stretta[i] ? "giorno calmo, attiva" : "salta oggi");
      IP3_g_giorno[i] = t.day_of_year; IP3_g_fatto[i] = false; IP3_g_rott[i] = 0; IP3_g_rh[i] = 0; IP3_g_rl[i] = 0; IP3_g_hs[i] = 0; IP3_g_ls[i] = 0;
     }
   if(m >= fine) { if(IP3_InPos(i)) IP3_Chiudi(i); return; }
   if(m > inizio)
     {
      double hh = iHigh(s, PERIOD_M5, 1), ll = iLow(s, PERIOD_M5, 1);
      IP3_g_hs[i] = IP3_g_hs[i] == 0 ? hh : MathMax(IP3_g_hs[i], hh); IP3_g_ls[i] = IP3_g_ls[i] == 0 ? ll : MathMin(IP3_g_ls[i], ll);
     }
   if(m < inizio + N || !IP3_g_on[i]) return;
   int nb = (m - inizio) / 5;
   double o[], h[], l[], c[];
   if(CopyOpen(s, PERIOD_M5, 1, nb, o) < nb || CopyHigh(s, PERIOD_M5, 1, nb, h) < nb || CopyLow(s, PERIOD_M5, 1, nb, l) < nb || CopyClose(s, PERIOD_M5, 1, nb, c) < nb) return;
   int k = N / 5;
   if(IP3_g_rh[i] == 0) { IP3_g_rh[i] = h[ArrayMaximum(h, 0, k)]; IP3_g_rl[i] = l[ArrayMinimum(l, 0, k)]; }
   if(IP3_g_fatto[i]) return;
   double ultima = c[nb - 1];
   // avvio a sessione gia' iniziata: se il segnale di oggi e' gia' scattato su una barra precedente, oggi non entra piu'
   if(IP3_g_primo[i])
     {
      IP3_g_primo[i] = false;
      if(nb > k)
        {
         if(tipo == 3) { IP3_g_fatto[i] = true; return; }
         int rott = 0;
         for(int q = k; q < nb - 1; q++)
           {
            if(tipo == 5) { if(c[q] > IP3_g_rh[i] || c[q] < IP3_g_rl[i]) { IP3_g_fatto[i] = true; return; } continue; }
            if(rott == 0) { if(c[q] > IP3_g_rh[i]) { rott = 1; IP3_g_est[i] = h[q]; } else if(c[q] < IP3_g_rl[i]) { rott = -1; IP3_g_est[i] = l[q]; } continue; }
            IP3_g_est[i] = rott > 0 ? MathMax(IP3_g_est[i], h[q]) : MathMin(IP3_g_est[i], l[q]);
            if((rott > 0 && c[q] < IP3_g_rh[i]) || (rott < 0 && c[q] > IP3_g_rl[i])) { IP3_g_fatto[i] = true; return; }
           }
         IP3_g_rott[i] = rott;
        }
     }
   if(tipo == 5)
     {
      if(!IP3_g_stretta[i]) { IP3_g_fatto[i] = true; return; }
      if(ultima > IP3_g_rh[i]) IP3_Entra(i, 1, IP3_g_rl[i]); else if(ultima < IP3_g_rl[i]) IP3_Entra(i, -1, IP3_g_rh[i]);
      return;
     }
   if(tipo == 3)
     {
      if(nb == k) { int lato = c[k - 1] > o[0] ? 1 : -1; IP3_Entra(i, lato, lato > 0 ? IP3_g_rl[i] : IP3_g_rh[i]); }
      return;
     }
   if(IP3_g_rott[i] == 0)
     {
      if(ultima > IP3_g_rh[i]) { IP3_g_rott[i] = 1; IP3_g_est[i] = h[nb - 1]; }
      else if(ultima < IP3_g_rl[i]) { IP3_g_rott[i] = -1; IP3_g_est[i] = l[nb - 1]; }
      return;
     }
   IP3_g_est[i] = IP3_g_rott[i] > 0 ? MathMax(IP3_g_est[i], h[nb - 1]) : MathMin(IP3_g_est[i], l[nb - 1]);
   if((IP3_g_rott[i] > 0 && ultima < IP3_g_rh[i]) || (IP3_g_rott[i] < 0 && ultima > IP3_g_rl[i]))
     {
      double sp = SymbolInfoDouble(s, SYMBOL_ASK) - SymbolInfoDouble(s, SYMBOL_BID);
      IP3_Entra(i, -IP3_g_rott[i], IP3_g_rott[i] > 0 ? IP3_g_est[i] + sp : IP3_g_est[i]);
     }
  }


// all'avvio: range delle ultime sessioni dallo storico M5 (serve alle regole IP3_NR-ORB per non aspettare 2 settimane)
void IP3_Precarica(int i, bool stampa = true)
  {
   IP3_g_nr[i] = 0;   // 20/11: ricalcolo completo dallo storico
   MqlRates r[]; int n = CopyRates(IP3_g_sym[i], PERIOD_M5, 0, 12000, r);
   if(n <= 0) return;
   bool ny = !IP3_LON[i]; int inizio = ny ? 9 * 60 + 30 : 8 * 60, fine = ny ? 16 * 60 : 16 * 60 + 30;
   int giorno = -1; double hs = 0, ls = 0;
   for(int k = 0; k < n; k++)
     {
      MqlDateTime t; TimeToStruct(IP3_Locale(r[k].time, ny), t);
      if(t.day_of_week == 0 || t.day_of_week == 6) continue;
      MqlDateTime tc; TimeToStruct(IP3_Locale(r[k].time + 300, ny), tc); int m = tc.hour * 60 + tc.min;   // 20/11: ora di CHIUSURA della candela
      if(t.day_of_year != giorno)
        {
         if(hs > 0 && k < n - 1) { if(IP3_g_nr[i] < 40) IP3_g_rng[i][IP3_g_nr[i]++] = hs - ls; else { for(int q = 1; q < 40; q++) IP3_g_rng[i][q - 1] = IP3_g_rng[i][q]; IP3_g_rng[i][39] = hs - ls; } }
         giorno = t.day_of_year; hs = 0; ls = 0;
        }
      if(m > inizio && m < fine) { hs = hs == 0 ? r[k].high : MathMax(hs, r[k].high); ls = ls == 0 ? r[k].low : MathMin(ls, r[k].low); }
     }
   // 20/11: l'ultima sessione dello storico conta se e' gia' finita (giorno diverso da oggi), es. il venerdi' quando parte nel weekend
   MqlDateTime oggi; TimeToStruct(IP3_Locale(TimeTradeServer(), ny), oggi);
   if(hs > 0 && giorno != oggi.day_of_year) { if(IP3_g_nr[i] < 40) IP3_g_rng[i][IP3_g_nr[i]++] = hs - ls; else { for(int q = 1; q < 40; q++) IP3_g_rng[i][q - 1] = IP3_g_rng[i][q]; IP3_g_rng[i][39] = hs - ls; } }
   if(!stampa) return;
   PrintFormat("Regola %d %s: caricate %d sessioni passate", i + 1, IP3_g_sym[i], IP3_g_nr[i]);
  }

int IP3_OnInit()
  {
   string parti[]; if(StringSplit(IP3_InpSimboli, ',', parti) != IP3_NR) { Print("InpSimboli: servono 8 simboli separati da virgola"); return INIT_PARAMETERS_INCORRECT; }
   for(int i = 0; i < IP3_NR; i++)
     {
      IP3_g_sym[i] = parti[i]; StringTrimLeft(IP3_g_sym[i]); StringTrimRight(IP3_g_sym[i]);
      IP3_g_on[i] = StringFind(IP3_InpAttive, IntegerToString(i + 1)) >= 0;
      IP3_g_giorno[i] = -1; IP3_g_barra[i] = 0; IP3_g_nr[i] = 0; IP3_g_primo[i] = true; IP3_g_hs[i] = 0; IP3_g_ls[i] = 0; IP3_g_stretta[i] = false;
      if(!SymbolSelect(IP3_g_sym[i], true)) PrintFormat("ATTENZIONE: simbolo %s non trovato (regola %d)", IP3_g_sym[i], i + 1);
      else if(IP3_REG[i] == 5) IP3_Precarica(i);
     }
   IP3_trade.SetDeviationInPoints(50);
   PU_Timer(2);
   PrintFormat("IntradayPortafoglio avviato: regole attive %s, rischio %.2f%% a IP3_trade", IP3_InpAttive, IP3_InpRischio);
   return INIT_SUCCEEDED;
  }
void IP3_OnDeinit(const int r) { PU_Kill(); PU_Comment(""); }
void IP3_OnTimer()
  {
   string riga = "IntradayPortafoglio - rischio " + DoubleToString(IP3_InpRischio, 2) + "%\n";
   for(int i = 0; i < IP3_NR; i++)
     {
      IP3_Processa(i);
      riga += StringFormat("%d %s: %s%s\n", i + 1, IP3_g_sym[i], IP3_g_on[i] ? "attiva" : "spenta", IP3_InPos(i) ? " - IN POSIZIONE" : (IP3_g_fatto[i] ? " - fatto oggi" : ""));
     }
   PU_Comment(riga);
  }
void IP3_OnTick() {}

//==================== MODULO FL_ = FlipLotteria ====================
//+------------------------------------------------------------------+
//| FlipLotteria.mq5                                                  |
//| Flip "a lotteria" con i vantaggi veri della ricerca web           |
//| (31/10-01/11/2026, test onesti 2020-2026, Sharpe ~1):             |
//|  - MR: compra dopo il calo (IBS<0.2 e RSI2<30 sul giornaliero     |
//|    che chiude alle 16:00 NY), esce quando chiude sopra la media 5 |
//|    o dopo 10 giorni. SP500, NAS100, US30.                          |
//|  - NA: Noise Area (Zarattini) NAS100 m=1.0 e SP500 m=1.5,         |
//|    controlli ogni mezz'ora 10:00-15:30 NY, tutto chiuso alle 16:00.|
//| Dimensione: FL_InpEsposizione = posizioni totali / equity quando     |
//| tutti e 5 i pezzi sono aperti (pesi del test), ridotta quando il  |
//| mercato e' agitato (FL_InpVolMan, Moreira-Muir). Serve leva 1:500.   |
//| Flip 30 giorni (test 2020-26, prudente | tester MT5):              |
//|    80x arriva 3-4%  brucia 10-16%                                  |
//|   110x arriva 6-9%  brucia 19-28%  finale medio 121-155 (DEFAULT)  |
//|   140x arriva 12%+  brucia 34-39%  (oltre il limite del 30%)       |
//| Flip 90 giorni: 60x arriva 13-15% brucia 19-21% medio 148-175      |
//| Flip: chiude tutto e si ferma a FL_InpObiettivo o sotto FL_InpMinimo.   |
//| Usare su un conto DEMO DEDICATO da 100 (l'obiettivo e' sull'equity |
//| di tutto il conto).                                               |
//+------------------------------------------------------------------+


bool FL_InpUsaRegista = false;   // moltiplica i lotti per MP_SCALA del Regista (portafoglio a volatilita' costante)
double FL_ScalaRegista()
  {
   if(!FL_InpUsaRegista || !GlobalVariableCheck("MP_SCALA")) return 1.0;
   if(TimeCurrent() - GlobalVariableTime("MP_SCALA") > 3 * 86400) return 1.0;   // regista fermo da 3 giorni: nessuna scala
   return GlobalVariableGet("MP_SCALA");
  }

double FL_InpEsposizione = 110.0;  // Esposizione massima (volte il conto, tutti i pezzi aperti; max 500)
double FL_InpObiettivo = 100000000.0;  // Obiettivo equity: chiude tutto e si ferma
double FL_InpMinimo = 500.0;   // Equity minima: chiude tutto e si ferma
bool FL_InpUsaMR = true;   // Usa MR (compra dopo il calo) su SP500, NAS100, US30
bool FL_InpUsaNA = true;   // Usa Noise Area su NAS100 e SP500
bool FL_InpVolMan = true;   // Posizioni piu' piccole quando il mercato e' agitato (Moreira-Muir)
string FL_InpSuffisso = ".s";   // Suffisso simboli (PU Prime: .s)
long FL_InpMagic = 770500; // Magic base
bool FL_InpRiparti = false;  // true = cancella lo stato "fermo" e riparte

#define FL_NP 5
// pezzi: 0 MR SP500, 1 MR NAS100, 2 MR US30, 3 NA NAS100, 4 NA SP500
string   FL_P_NOME[FL_NP]  = {"MR SP500", "MR NAS100", "MR US30", "NA NAS100", "NA SP500"};
string   FL_P_BASE[FL_NP]  = {"SP500", "NAS100", "DJ30", "NAS100", "SP500"};
double   FL_P_PESO[FL_NP]  = {0.293, 0.255, 0.300, 0.486, 0.669};      // nozionale/equity a moltiplicatore 1 (somma 2.003)
bool     FL_P_MR[FL_NP]    = {true, true, true, false, false};
double   FL_P_M[FL_NP]     = {0, 0, 0, 1.0, 1.5};
#define  FL_SOMMA_PESI 2.003
// volatility management: mediana della vol 20 giorni 2020-22 e media della scala nel 2020-22 (dal test)
double   FL_P_VMED[FL_NP]  = {0.011578, 0.015400, 0.010064, 0.015400, 0.011578};
double   FL_P_VMS[FL_NP]   = {1.1412, 1.1346, 1.0600, 1.1346, 1.1412};
double   FL_g_scala[FL_NP];
datetime FL_g_scalaGiorno[FL_NP];
string   FL_g_sym[FL_NP];
bool     FL_g_ok[FL_NP];
double   FL_g_molt = 0;                // moltiplicatore = esposizione / somma pesi
datetime FL_g_fattoMR = 0;             // giorno NY in cui MR e' gia' stato valutato
datetime FL_g_fattoNA[FL_NP];             // ultimo slot NA valutato (ora NY)
string   FL_GV_FERMO;
CTrade   FL_trade;

//------------------------------------------------------------------ ora (server Europe/Athens -> New York)
datetime FL_NthSunday(int y, int mon, int n)
{
   MqlDateTime d; ZeroMemory(d); d.year = y; d.mon = mon; d.day = 1;
   datetime t = StructToTime(d);
   MqlDateTime x; TimeToStruct(t, x);
   int add = (7 - x.day_of_week) % 7;
   return t + (add + 7 * (n - 1)) * 86400;
}
datetime FL_LastSunday(int y, int mon)
{
   MqlDateTime d; ZeroMemory(d); d.year = (mon == 12) ? y + 1 : y; d.mon = (mon == 12) ? 1 : mon + 1; d.day = 1;
   datetime t = StructToTime(d) - 86400;                            // ultimo giorno del mese
   MqlDateTime x; TimeToStruct(t, x);
   return t - x.day_of_week * 86400;
}
int FL_OffAtene(datetime utc)
{
   MqlDateTime d; TimeToStruct(utc, d);
   datetime a = FL_LastSunday(d.year, 3) + 3600, b = FL_LastSunday(d.year, 10) + 3600;
   return (utc >= a && utc < b) ? 3 : 2;
}
int FL_OffNY(datetime utc)
{
   MqlDateTime d; TimeToStruct(utc, d);
   datetime a = FL_NthSunday(d.year, 3, 2) + 7 * 3600, b = FL_NthSunday(d.year, 11, 1) + 6 * 3600;
   return (utc >= a && utc < b) ? -4 : -5;
}
datetime FL_ServerANY(datetime srv)
{
   datetime utc = srv - FL_OffAtene(srv - 2 * 3600) * 3600;
   return utc + FL_OffNY(utc) * 3600;
}
datetime FL_Giorno(datetime t)          { return t - (t % 86400); }
int      FL_MinutoDelGiorno(datetime t) { return (int)((t % 86400) / 60); }
int      FL_GiornoSett(datetime t)      { MqlDateTime d; TimeToStruct(t, d); return d.day_of_week; }

//------------------------------------------------------------------ simboli
string FL_Trova(string base)
{
   // nomi alternativi (FTMO e altri broker: US30.cash, US500.cash, US100.cash con FL_InpSuffisso=".cash")
   string alt = (base == "DJ30") ? "US30" : (base == "SP500") ? "US500" : (base == "NAS100") ? "US100" : "";
   string c[6];
   c[0] = base + FL_InpSuffisso; c[1] = base; c[2] = base + ".p";
   c[3] = alt == "" ? "" : alt + FL_InpSuffisso; c[4] = alt; c[5] = alt == "" ? "" : alt + ".p";
   for(int i = 0; i < 6; i++)
   {
      if(c[i] == "") continue;
      if(SymbolSelect(c[i], true) && SymbolInfoDouble(c[i], SYMBOL_POINT) > 0) return c[i];
   }
   return "";
}

//------------------------------------------------------------------ posizioni
bool FL_Posizione(int k, ulong &ticket, int &lato, datetime &aperta)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != FL_InpMagic + k) continue;
      if(PositionGetString(POSITION_SYMBOL) != FL_g_sym[k]) continue;
      ticket = t;
      lato = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1;
      aperta = (datetime)PositionGetInteger(POSITION_TIME);
      return true;
   }
   return false;
}
void FL_Chiudi(int k)
{
   ulong t; int l; datetime a;
   for(int tentativi = 0; tentativi < 5 && FL_Posizione(k, t, l, a); tentativi++)
      if(!FL_trade.PositionClose(t)) Print(FL_P_NOME[k], ": chiusura fallita ", FL_trade.ResultRetcode(), " ", FL_trade.ResultComment());
}
void FL_ChiudiTutto() { for(int k = 0; k < FL_NP; k++) if(FL_g_sym[k] != "") FL_Chiudi(k); }

double FL_Lotti(int k, int lato)
{
   string s = FL_g_sym[k];
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double nozionale = FL_g_molt * FL_P_PESO[k] * eq * (FL_InpVolMan ? FL_g_scala[k] : 1.0) * FL_ScalaRegista();   // in valuta del conto
   double tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
   double px = lato > 0 ? SymbolInfoDouble(s, SYMBOL_ASK) : SymbolInfoDouble(s, SYMBOL_BID);
   if(tv <= 0 || ts <= 0 || px <= 0) return 0;
   double perLotto = px / ts * tv;                                  // valore di 1 lotto in valuta del conto
   double grezzi = nozionale / perLotto;
   double step = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN),
          mx = SymbolInfoDouble(s, SYMBOL_VOLUME_MAX);
   double lot = MathFloor(grezzi / step + 1e-9) * step;
   if(lot < mn) lot = (grezzi >= 0.5 * mn) ? mn : 0;
   if(lot > mx) lot = mx;
   // margine: al massimo l'80% del margine libero
   double marg;
   ENUM_ORDER_TYPE tipo = lato > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   if(lot > 0 && OrderCalcMargin(tipo, s, lot, px, marg) && marg > 0)
   {
      double libero = AccountInfoDouble(ACCOUNT_MARGIN_FREE) * 0.8;
      if(marg > libero)
      {
         Print(FL_P_NOME[k], StringFormat(": margine %.2f > 80%% del libero %.2f, riduco i lotti", marg, libero));
         lot = MathFloor(lot * libero / marg / step) * step;
      }
      if(lot < mn) lot = 0;
   }
   return NormalizeDouble(lot, 2);
}
bool FL_Apri(int k, int lato)
{
   double lot = FL_Lotti(k, lato);
   if(lot <= 0) { Print(FL_P_NOME[k], ": lotti troppo piccoli o margine insufficiente, salto"); return false; }
   FL_trade.SetExpertMagicNumber(FL_InpMagic + k);
   bool ok = lato > 0 ? FL_trade.Buy(lot, FL_g_sym[k], 0, 0, 0, FL_P_NOME[k]) : FL_trade.Sell(lot, FL_g_sym[k], 0, 0, 0, FL_P_NOME[k]);
   if(!ok) Print(FL_P_NOME[k], ": ordine fallito ", FL_trade.ResultRetcode(), " ", FL_trade.ResultComment());
   else    Print(FL_P_NOME[k], lato > 0 ? ": BUY " : ": SELL ", DoubleToString(lot, 2), " ", FL_g_sym[k]);
   return ok;
}

//------------------------------------------------------------------ dati M30 in ora NY (piu' vecchia -> piu' recente)
int FL_CaricaM30(string s, int n, MqlRates &r[], datetime &ny[])
{
   ArraySetAsSeries(r, false);
   int got = CopyRates(s, PERIOD_M30, 0, n, r);
   if(got <= 0) return 0;
   ArrayResize(ny, got);
   for(int i = 0; i < got; i++) ny[i] = FL_ServerANY(r[i].time);
   return got;
}

//------------------------------------------------------------------ chiusure giornaliere (16:00 NY), solo giorni completi
int FL_Chiusure(string s, datetime nowSrv, double &c2[], double &h2[], double &l2[], datetime &g2[])
{
   MqlRates r[]; datetime ny[];
   int n = FL_CaricaM30(s, 4000, r, ny);
   if(n < 1000) return 0;
   double H[], L[], C[]; datetime G[]; int nb[]; datetime ult[];
   ArrayResize(H, n); ArrayResize(L, n); ArrayResize(C, n); ArrayResize(G, n); ArrayResize(nb, n); ArrayResize(ult, n);
   int m = 0;
   for(int i = 0; i < n; i++)
   {
      if(r[i].time + 1800 > nowSrv) break;
      datetime g = FL_Giorno(ny[i] + 1800 - 16 * 3600 - 1) + 86400;
      if(m == 0 || G[m - 1] != g)
      {
         G[m] = g; H[m] = r[i].high; L[m] = r[i].low; C[m] = r[i].close; nb[m] = 1; ult[m] = ny[i];
         m++;
      }
      else
      {
         H[m - 1] = MathMax(H[m - 1], r[i].high); L[m - 1] = MathMin(L[m - 1], r[i].low); C[m - 1] = r[i].close;
         nb[m - 1]++; ult[m - 1] = ny[i];
      }
   }
   ArrayResize(c2, m); ArrayResize(h2, m); ArrayResize(l2, m); ArrayResize(g2, m);
   int q = 0;
   for(int i = 0; i < m; i++)
   {
      int wd = FL_GiornoSett(G[i]);
      if(wd == 0 || wd == 6 || nb[i] < 8) continue;
      if(ult[i] + 1800 != G[i] + 16 * 3600) continue;
      c2[q] = C[i]; h2[q] = H[i]; l2[q] = L[i]; g2[q] = G[i]; q++;
   }
   return q;
}
// scala = clip(mediana / vol20, 0.25, 2) / media, con vol20 = dev. std. dei 20 rendimenti fino a c2[ultimo] compreso
double FL_Scala(int k, const double &c2[], int ultimo)
{
   if(ultimo < 21) return 1.0;
   double r[20], mu = 0;
   for(int i = 0; i < 20; i++) { r[i] = c2[ultimo - 19 + i] / c2[ultimo - 20 + i] - 1; mu += r[i]; }
   mu /= 20;
   double v = 0; for(int i = 0; i < 20; i++) v += (r[i] - mu) * (r[i] - mu);
   v = MathSqrt(v / 19);
   if(v <= 0) return 1.0;
   double s = MathMax(0.25, MathMin(2.0, FL_P_VMED[k] / v));
   return s / FL_P_VMS[k];
}

//------------------------------------------------------------------ MR (alle 16:00 NY)
void FL_PassoMR(int k, datetime oggiNY, datetime nowSrv)
{
   double c2[], h2[], l2[]; datetime g2[];
   int q = FL_Chiusure(FL_g_sym[k], nowSrv, c2, h2, l2, g2);
   if(q < 30) { Print(FL_P_NOME[k], ": troppi pochi giorni completi (", q, ")"); return; }
   if(g2[q - 1] != oggiNY) { Print(FL_P_NOME[k], ": la giornata di oggi non arriva alle 16:00 (festivo?), salto"); return; }
   // RSI(2) di Wilder, identico al test: primo scarto 0, media esponenziale alpha 1/2
   double up = 0, dn = 0, rsi = 50;
   for(int i = 0; i < q; i++)
   {
      double d = (i == 0) ? 0 : c2[i] - c2[i - 1];
      double u = d > 0 ? d : 0, w = d < 0 ? -d : 0;
      if(i == 0) { up = u; dn = w; }
      else       { up = 0.5 * u + 0.5 * up; dn = 0.5 * w + 0.5 * dn; }
      rsi = 100 - 100 / (1 + up / (dn == 0 ? 1e-12 : dn));
   }
   double c = c2[q - 1], hh = h2[q - 1], ll = l2[q - 1];
   double ibs = (hh - ll > 0) ? (c - ll) / (hh - ll) : 0.5;
   double sma5 = 0; for(int i = q - 5; i < q; i++) sma5 += c2[i]; sma5 /= 5;
   PrintFormat("%s: giorno %s chiusura %.2f IBS %.2f RSI2 %.1f media5 %.2f", FL_P_NOME[k], TimeToString(oggiNY, TIME_DATE), c, ibs, rsi, sma5);
   ulong t; int lato; datetime aperta;
   if(FL_Posizione(k, t, lato, aperta))
   {
      datetime gIn = FL_Giorno(FL_ServerANY(aperta));                       // entrata alle 16:00 del giorno del segnale
      int tenuti = 0; for(int i = 0; i < q; i++) if(g2[i] > gIn) tenuti++;
      if(c > sma5 || tenuti >= 10)
      {
         PrintFormat("%s: esce (chiusura %.2f, media5 %.2f, giorni %d)", FL_P_NOME[k], c, sma5, tenuti);
         FL_Chiudi(k);
      }
      else return;
   }
   if(ibs < 0.2 && rsi < 30)
   {
      FL_g_scala[k] = FL_Scala(k, c2, q - 2);                               // vol fino a ieri
      PrintFormat("%s: scala volatilita' %.2f", FL_P_NOME[k], FL_g_scala[k]);
      FL_Apri(k, 1);
   }
}

//------------------------------------------------------------------ NA (ogni mezz'ora 10:00-15:30 NY)
void FL_PassoNA(int k, int slot, datetime oggiNY, datetime nowSrv)
{
   MqlRates r[]; datetime ny[];
   int n = FL_CaricaM30(FL_g_sym[k], 1500, r, ny);
   if(n < 600) { Print(FL_P_NOME[k], ": storico M30 insufficiente (", n, ")"); return; }
   // ultimi 14 giorni completi (tutte le 14 mezz'ore 9:30..16:00): sigma dello slot e chiusura di ieri (16:00)
   double sigma = 0, C1 = 0; int contati = 0; bool haC1 = false;
   for(int i = n - 1; i >= 0 && contati < 14; i--)
   {
      datetime g = FL_Giorno(ny[i]);
      if(g >= oggiNY || FL_MinutoDelGiorno(ny[i]) != 570) continue;      // barra delle 9:30 di un giorno passato
      double Pt = 0, P16 = 0; int trovate = 0; bool okT = false, ok16 = false;
      for(int j = i; j < n && FL_Giorno(ny[j]) == g; j++)
      {
         int mm = FL_MinutoDelGiorno(ny[j]);
         if(mm >= 570 && mm <= 960) trovate++;
         if(mm == slot) { Pt = r[j].open; okT = true; }
         if(mm == 960)  { P16 = r[j].open; ok16 = true; }
      }
      if(trovate < 14 || !okT || !ok16) continue;
      if(!haC1) { C1 = P16; haC1 = true; }
      sigma += MathAbs(Pt / r[i].open - 1);
      contati++;
   }
   if(contati < 14) { Print(FL_P_NOME[k], ": meno di 14 giorni completi, salto"); return; }
   sigma /= 14;
   // oggi: apertura 9:30 e VWAP delle barre chiuse 9:30..slot
   double O = 0, pv = 0, v = 0; bool okO = false;
   for(int i = n - 1; i >= 0; i--)
   {
      datetime g = FL_Giorno(ny[i]);
      if(g > oggiNY) continue;
      if(g < oggiNY) break;
      int mm = FL_MinutoDelGiorno(ny[i]);
      if(mm == 570) { O = r[i].open; okO = true; }
      if(mm >= 570 && mm < slot && r[i].time + 1800 <= nowSrv)
      {
         pv += (r[i].high + r[i].low + r[i].close) / 3.0 * (double)r[i].tick_volume;
         v  += (double)r[i].tick_volume;
      }
   }
   if(!okO) { Print(FL_P_NOME[k], ": manca la barra delle 9:30 di oggi, salto"); return; }
   double vw = v > 0 ? pv / v : 0;
   double p  = SymbolInfoDouble(FL_g_sym[k], SYMBOL_BID);
   double ub = MathMax(O, C1) * (1 + FL_P_M[k] * sigma), lb = MathMin(O, C1) * (1 - FL_P_M[k] * sigma);
   ulong t; int lato; datetime aperta;
   bool pos = FL_Posizione(k, t, lato, aperta);
   if(pos)
   {
      if(lato > 0 && p < MathMax(ub, vw > 0 ? vw : ub))      { FL_Chiudi(k); pos = false; }
      else if(lato < 0 && p > MathMin(lb, vw > 0 ? vw : lb)) { FL_Chiudi(k); pos = false; }
   }
   if(!pos && (p > ub || p < lb))
   {
      if(FL_g_scalaGiorno[k] != oggiNY)
      {
         double c2[], h2[], l2[]; datetime g2[];
         int q = FL_Chiusure(FL_g_sym[k], nowSrv, c2, h2, l2, g2);
         FL_g_scala[k] = 1.0;
         if(q > 0 && g2[q - 1] < oggiNY) FL_g_scala[k] = FL_Scala(k, c2, q - 1);   // vol fino a ieri
         FL_g_scalaGiorno[k] = oggiNY;
      }
      FL_Apri(k, p > ub ? 1 : -1);
   }
}

//------------------------------------------------------------------ eventi
int FL_OnInit()
{
   if(FL_InpEsposizione <= 0 || FL_InpEsposizione > 500) { Print("Esposizione deve essere tra 1 e 500"); return INIT_PARAMETERS_INCORRECT; }
   FL_g_molt = FL_InpEsposizione / FL_SOMMA_PESI;
   FL_GV_FERMO = "FlipLotteria_fermo_" + (string)AccountInfoInteger(ACCOUNT_LOGIN) + "_" + (string)FL_InpMagic;
   if(FL_InpRiparti && GlobalVariableCheck(FL_GV_FERMO)) GlobalVariableDel(FL_GV_FERMO);
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
      Print("ATTENZIONE: il conto non e' 'hedging': MR e NA sullo stesso indice si sommano in una sola posizione.");
   if(AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL)
      Print("ATTENZIONE: conto REALE. Questo EA va provato prima su un conto demo dedicato.");
   PrintFormat("Leva del conto 1:%d | esposizione massima %.0fx il conto", (int)AccountInfoInteger(ACCOUNT_LEVERAGE), FL_InpEsposizione);
   int altri = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(PositionGetTicket(i) > 0 && (PositionGetInteger(POSITION_MAGIC) < FL_InpMagic || PositionGetInteger(POSITION_MAGIC) >= FL_InpMagic + FL_NP)) altri++;
   if(altri > 0) Print("ATTENZIONE: sul conto ci sono ", altri, " posizioni di altri EA: obiettivo e minimo valgono su TUTTO il conto.");
   int trovati = 0;
   for(int k = 0; k < FL_NP; k++)
   {
      FL_g_sym[k] = FL_Trova(FL_P_BASE[k]);
      FL_g_ok[k] = FL_g_sym[k] != "" && (FL_P_MR[k] ? FL_InpUsaMR : FL_InpUsaNA);
      FL_g_fattoNA[k] = 0; FL_g_scala[k] = 1.0; FL_g_scalaGiorno[k] = 0;
      if(FL_g_ok[k]) trovati++;
      Print(FL_P_NOME[k], " -> ", FL_g_sym[k] == "" ? "NON TROVATO" : FL_g_sym[k], FL_g_ok[k] ? "" : " (spento)");
   }
   if(trovati == 0) return INIT_FAILED;
   FL_trade.SetDeviationInPoints(1000);
   PU_Timer(5);
   return INIT_SUCCEEDED;
}
void FL_OnDeinit(const int reason) { PU_Kill(); PU_Comment(""); }
void FL_OnTick()  { FL_Passo(); }
void FL_OnTimer() { FL_Passo(); }

void FL_Passo()
{
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   bool fermo = GlobalVariableCheck(FL_GV_FERMO);
   if(!fermo && (eq >= FL_InpObiettivo || eq <= FL_InpMinimo))
   {
      Print(eq >= FL_InpObiettivo ? "OBIETTIVO RAGGIUNTO: " : "CONTO BRUCIATO: ", eq, " -> chiudo tutto e mi fermo");
      FL_ChiudiTutto();
      GlobalVariableSet(FL_GV_FERMO, eq);
      fermo = true;
   }
   datetime srv = TimeTradeServer();
   datetime nyNow = FL_ServerANY(srv);
   datetime oggi = FL_Giorno(nyNow);
   int mm = FL_MinutoDelGiorno(nyNow), wd = FL_GiornoSett(nyNow);
   PU_Comment(StringFormat("FlipLotteria | esposizione %.0fx | equity %.2f | obiettivo %.0f | %s\nora New York %s",
           FL_InpEsposizione, eq, FL_InpObiettivo, fermo ? "FERMO (obiettivo o minimo raggiunto)" : "attivo",
           TimeToString(nyNow, TIME_DATE | TIME_MINUTES)));
   if(fermo || wd == 0 || wd == 6) return;
   // NA: slot 10:00-15:30 (primi 3 minuti), chiusura alle 16:00
   for(int k = 0; k < FL_NP; k++)
   {
      if(!FL_g_ok[k] || FL_P_MR[k]) continue;
      if(mm >= 960 && mm < 975)
      {
         ulong t; int l; datetime a;
         if(FL_Posizione(k, t, l, a)) { Print(FL_P_NOME[k], ": chiusura delle 16:00"); FL_Chiudi(k); }
         continue;
      }
      if(mm < 600 || mm >= 960) continue;
      int slot = 600 + ((mm - 600) / 30) * 30;
      if(mm - slot > 3) continue;
      datetime chiave = oggi + slot * 60;
      if(FL_g_fattoNA[k] == chiave) continue;
      FL_g_fattoNA[k] = chiave;
      FL_PassoNA(k, slot, oggi, srv);
   }
   // MR: alle 16:00 NY (entro 10 minuti), una volta al giorno
   if(mm >= 960 && mm < 970 && FL_g_fattoMR != oggi)
   {
      FL_g_fattoMR = oggi;
      for(int k = 0; k < FL_NP; k++) if(FL_g_ok[k] && FL_P_MR[k]) FL_PassoMR(k, oggi, srv);
   }
}
//+------------------------------------------------------------------+

//==================== MODULO SR1_ = StopReverse_news ====================
string SR1_SYM = "";
//+------------------------------------------------------------------+
//|                                                StopReverseEA.mq5 |
//|  Solo Buy Stop e Sell Stop a distanza fissa, nessuno SL/TP.      |
//|  Quando scatta uno, l'altro lo chiude (inversione) e viceversa.  |
//|  Gli ordini pendenti seguono il prezzo, sempre a distanza fissa. |
//|  v1.10: filtro orario (ora server), opera solo nella finestra.    |
//+------------------------------------------------------------------+
// COPIA DI TEST (Claude, 01/11/2026): pip e lotti proporzionali al prezzo (1 pip = 0.10 $ e lotto = SR1_InpLots con oro a 4100)


bool SR1_InpUsaRegista = false;   // moltiplica i lotti per MP_SCALA del Regista (portafoglio a volatilita' costante)
double SR1_ScalaRegista()
  {
   if(!SR1_InpUsaRegista || !GlobalVariableCheck("MP_SCALA")) return 1.0;
   if(TimeCurrent() - GlobalVariableTime("MP_SCALA") > 3 * 86400) return 1.0;   // regista fermo da 3 giorni: nessuna scala
   return GlobalVariableGet("MP_SCALA");
  }
int SR1_InpTipoNews = 1;      // 1 NFP, 2 CPI, 3 PCE, 4 FOMC, 0 tutte
int SR1_InpFinestraMin = 1;   // minuti di finestra dall'uscita della news
datetime SR1_g_news[]; int SR1_g_nNews = 0;
void SR1_CaricaNews()
  {
   int h = FileOpen("news_eventi.csv", FILE_READ | FILE_ANSI | FILE_TXT);
   if(h == INVALID_HANDLE) { Print("news_eventi.csv non trovato"); return; }
   while(!FileIsEnding(h))
     {
      string r = FileReadString(h); string p[];
      if(StringSplit(r, ';', p) < 2) continue;
      if(SR1_InpTipoNews != 0 && (int)StringToInteger(p[0]) != SR1_InpTipoNews) continue;
      ArrayResize(SR1_g_news, SR1_g_nNews + 1); SR1_g_news[SR1_g_nNews++] = StringToTime(p[1]);
     }
   FileClose(h); PrintFormat("News caricate: %d (tipo %d)", SR1_g_nNews, SR1_InpTipoNews);
  }

//--- Strategia
double SR1_InpDistancePips = 50.0;     // Distanza fissa degli ordini (pip)
double SR1_InpLots = 0.10;     // Lotto fisso
double SR1_InpStepPips = 10.0;      // Spostamento minimo dell'ordine pendente (pip)

//--- Filtri e sicurezza
double SR1_InpMaxSpreadPips = 0.0;      // Spread max per piazzare la prima coppia (pip, 0 = nessun limite)
int SR1_InpDeviation = 10;       // Slippage massimo (punti)
long SR1_InpMagic = 20261401; // Magic number
double SR1_InpPipSizeOverride = 0.0;      // Dimensione pip manuale (0 = automatica)

//--- Filtro orario (ORA DEL SERVER DEL BROKER, la stessa del grafico e del Tester)
bool SR1_InpUseTimeFilter = true;     // Usa il filtro orario
int SR1_InpStartHour = 15;       // Ora di inizio (0-23)
int SR1_InpStartMinute = 25;       // Minuto di inizio (0-59)
int SR1_InpEndHour = 16;       // Ora di fine (0-23)
int SR1_InpEndMinute = 30;       // Minuto di fine (0-59)
bool SR1_InpCloseAtEnd = true;     // A fine finestra chiudi anche le posizioni aperte

//--- Controllo
bool SR1_InpStartActive = true;     // Parti già attivo (altrimenti premi il pulsante)
bool SR1_InpCloseOnOff = true;     // Con pulsante su FERMO chiudi anche le posizioni aperte

CTrade   SR1_trade;
double   SR1_g_pip      = 0.0;
bool     SR1_g_active   = true;
bool     SR1_g_hedging  = true;
datetime SR1_g_lastTry  = 0;
datetime SR1_g_lastMsg  = 0;
string   SR1_g_status   = "avvio...";
string   SR1_BTN        = "SAR_ToggleBtn";

//+------------------------------------------------------------------+
int SR1_OnInit()
  {
   int digits = (int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS);
   if(SR1_InpPipSizeOverride > 0.0)
      SR1_g_pip = SR1_InpPipSizeOverride;
   else
     {
      string up = SR1_SYM;
      StringToUpper(up);
      if(StringFind(up, "XAU") >= 0 || StringFind(up, "GOLD") >= 0)
         SR1_g_pip = 0.1;                       // oro: 1 pip = 0.10
      else if(StringFind(up, "XAG") >= 0 || StringFind(up, "SILVER") >= 0)
         SR1_g_pip = 0.01;                      // argento: 1 pip = 0.01
      else
         SR1_g_pip = (digits == 3 || digits == 5) ? SymbolInfoDouble(SR1_SYM, SYMBOL_POINT) * 10.0 : SymbolInfoDouble(SR1_SYM, SYMBOL_POINT);
     }

   SR1_CaricaNews();
   SR1_g_hedging = (AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);

   SR1_trade.SetExpertMagicNumber(SR1_InpMagic);
   SR1_trade.SetDeviationInPoints(SR1_InpDeviation);

   SR1_g_active = SR1_InpStartActive;
   SR1_CreateButton();
   SR1_UpdateButton();

   PU_Timer(1);
   PrintFormat("StopReverseEA avviato su %s. 1 pip = %s, conto %s, attivo=%d",
               SR1_SYM, DoubleToString(SR1_g_pip, digits), SR1_g_hedging ? "hedging" : "netting", (int)SR1_g_active);
   return(INIT_SUCCEEDED);
  }

void SR1_OnDeinit(const int reason)
  {
   PU_Kill();
   PU_ObjectDelete(0, SR1_BTN);
   PU_Comment("");
  }

void SR1_OnTick() { SR1_Manage(); }

void SR1_OnTimer()
  {
   SR1_Manage();
   PU_Comment("StopReverseEA\n",
           "Stato: ", SR1_g_status, "\n",
           "Spread: ", DoubleToString((SymbolInfoDouble(SR1_SYM, SYMBOL_ASK) - SymbolInfoDouble(SR1_SYM, SYMBOL_BID)) / SR1_g_pip, 1),
           " pip | 1 pip = ", DoubleToString(SR1_g_pip, ((int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS))), "\n",
           "Pendenti: ", SR1_CountPendings(), " | Posizioni: ", SR1_CountPositions());
  }

//+------------------------------------------------------------------+
//| Pulsante ON/OFF                                                  |
//+------------------------------------------------------------------+
void SR1_CreateButton()
  {
   PU_ObjectDelete(0, SR1_BTN);
   PU_ObjectCreate(0, SR1_BTN, OBJ_BUTTON, 0, 0, 0);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_XDISTANCE, 10);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_YDISTANCE, 25);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_XSIZE, 140);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_YSIZE, 28);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_FONTSIZE, 10);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_COLOR, clrWhite);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_SELECTABLE, false);
  }

void SR1_UpdateButton()
  {
   PU_ObjectSetString(0, SR1_BTN, OBJPROP_TEXT, SR1_g_active ? "EA: ATTIVO (clicca)" : "EA: FERMO (clicca)");
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_BGCOLOR, SR1_g_active ? clrSeaGreen : clrFireBrick);
   PU_ObjectSetInteger(0, SR1_BTN, OBJPROP_STATE, false);
   ChartRedraw();
  }

void SR1_OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
  {
   if(id == CHARTEVENT_OBJECT_CLICK && sparam == SR1_BTN)
     {
      SR1_g_active = !SR1_g_active;
      SR1_UpdateButton();
      SR1_Manage();
     }
  }

//+------------------------------------------------------------------+
//| Utilità                                                          |
//+------------------------------------------------------------------+
void SR1_LogOnce(string msg)
  {
   SR1_g_status = msg;
   if(TimeCurrent() - SR1_g_lastMsg >= 10)
     {
      SR1_g_lastMsg = TimeCurrent();
      Print("StopReverseEA: ", msg);
     }
  }

// true se l'ora del server e' dentro la finestra (supporta anche finestre a cavallo della mezzanotte)
bool SR1_InTimeWindow()
  {
   datetime now = TimeCurrent();
   for(int i = 0; i < SR1_g_nNews; i++)
      if(now >= SR1_g_news[i] && now < SR1_g_news[i] + SR1_InpFinestraMin * 60) return true;
   return false;
  }

double SR1_MinDistance()
  {
   long lvl = SymbolInfoInteger(SR1_SYM, SYMBOL_TRADE_STOPS_LEVEL);
   long frz = SymbolInfoInteger(SR1_SYM, SYMBOL_TRADE_FREEZE_LEVEL);
   return (double)MathMax(lvl, frz) * SymbolInfoDouble(SR1_SYM, SYMBOL_POINT) + SymbolInfoDouble(SR1_SYM, SYMBOL_POINT);
  }

double SR1_NormalizeLots(double lots)
  {
   double vmin  = SymbolInfoDouble(SR1_SYM, SYMBOL_VOLUME_MIN);
   double vmax  = SymbolInfoDouble(SR1_SYM, SYMBOL_VOLUME_MAX);
   double vstep = SymbolInfoDouble(SR1_SYM, SYMBOL_VOLUME_STEP);
   if(vstep > 0) lots = MathFloor(lots / vstep + 1e-9) * vstep;
   lots = MathMax(vmin, MathMin(vmax, lots));
   return NormalizeDouble(lots, 2);
  }

bool SR1_TradingAllowed()
  {
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED))
     {
      SR1_LogOnce("Trading algoritmico NON consentito: attiva il pulsante 'Trading algoritmico' e spunta 'Consenti trading algoritmico'.");
      return false;
     }
   if(SymbolInfoInteger(SR1_SYM, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL)
     {
      SR1_LogOnce("Il simbolo non permette il trading in questo momento (mercato chiuso?).");
      return false;
     }
   return true;
  }

int SR1_CountPositions()
  {
   int n = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR1_SYM && PositionGetInteger(POSITION_MAGIC) == SR1_InpMagic)
         n++;
     }
   return n;
  }

int SR1_CountPendings()
  {
   int n = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) == SR1_SYM && OrderGetInteger(ORDER_MAGIC) == SR1_InpMagic)
         n++;
     }
   return n;
  }

void SR1_DeletePendings()
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) == SR1_SYM && OrderGetInteger(ORDER_MAGIC) == SR1_InpMagic)
         SR1_trade.OrderDelete(t);
     }
  }

void SR1_CloseAllPositions()
  {
   SR1_trade.SetTypeFillingBySymbol(SR1_SYM);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR1_SYM && PositionGetInteger(POSITION_MAGIC) == SR1_InpMagic)
         SR1_trade.PositionClose(t);
     }
  }

// Restituisce la posizione piu' recente (quella che e' appena scattata)
bool SR1_LatestPosition(ulong &ticket, long &type, double &open)
  {
   long bestTime = -1;
   ticket = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != SR1_SYM || PositionGetInteger(POSITION_MAGIC) != SR1_InpMagic)
         continue;
      long tm = PositionGetInteger(POSITION_TIME_MSC);
      if(tm > bestTime)
        {
         bestTime = tm;
         ticket   = t;
         type     = PositionGetInteger(POSITION_TYPE);
         open     = PositionGetDouble(POSITION_PRICE_OPEN);
        }
     }
   return (ticket != 0);
  }

// Chiude tutte le posizioni tranne quella indicata (la vecchia, dopo l'inversione)
void SR1_CloseOthers(ulong keep)
  {
   SR1_trade.SetTypeFillingBySymbol(SR1_SYM);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0 || t == keep) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR1_SYM && PositionGetInteger(POSITION_MAGIC) == SR1_InpMagic)
         SR1_trade.PositionClose(t);
     }
  }

bool SR1_PlacePending(ENUM_ORDER_TYPE t, double price, double lots)
  {
   SR1_trade.SetTypeFilling(ORDER_FILLING_RETURN);   // valido per gli ordini pendenti
   bool ok;
   if(t == ORDER_TYPE_BUY_STOP)
      ok = SR1_trade.BuyStop(lots, price, SR1_SYM, 0.0, 0.0, ORDER_TIME_GTC, 0, "SAR");
   else
      ok = SR1_trade.SellStop(lots, price, SR1_SYM, 0.0, 0.0, ORDER_TIME_GTC, 0, "SAR");

   if(!ok)
      PrintFormat("StopReverseEA: %s rifiutato: %s (codice %d) prezzo=%s lotti=%s",
                  EnumToString(t), SR1_trade.ResultRetcodeDescription(), SR1_trade.ResultRetcode(),
                  DoubleToString(price, ((int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS))), DoubleToString(lots, 2));
   return ok;
  }

//+------------------------------------------------------------------+
//| Prima coppia: Buy Stop e Sell Stop a distanza fissa              |
//+------------------------------------------------------------------+
void SR1_PlacePair()
  {
   if(TimeCurrent() - SR1_g_lastTry < 3) return;
   SR1_g_lastTry = TimeCurrent();

   if(!SR1_TradingAllowed()) return;

   double ask = SymbolInfoDouble(SR1_SYM, SYMBOL_ASK);
   double bid = SymbolInfoDouble(SR1_SYM, SYMBOL_BID);
   if(ask <= 0 || bid <= 0)
     {
      SR1_LogOnce("Prezzi non disponibili.");
      return;
     }
   if(SR1_InpMaxSpreadPips > 0.0 && (ask - bid) > SR1_InpMaxSpreadPips * SR1_g_pip)
     {
      SR1_LogOnce(StringFormat("Spread troppo alto: %.1f pip (max %.1f). Alza SR1_InpMaxSpreadPips o mettilo a 0.",
                           (ask - bid) / SR1_g_pip, SR1_InpMaxSpreadPips));
      return;
     }

   double dist = MathMax(SR1_InpDistancePips * SR1_g_pip, SR1_MinDistance());
   double lots = SR1_NormalizeLots(SR1_InpLots * 4100.0 / SymbolInfoDouble(SR1_SYM, SYMBOL_BID) * SR1_ScalaRegista());

   bool okBuy  = SR1_PlacePending(ORDER_TYPE_BUY_STOP,  NormalizeDouble(ask + dist, ((int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS))), lots);
   bool okSell = SR1_PlacePending(ORDER_TYPE_SELL_STOP, NormalizeDouble(bid - dist, ((int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS))), lots);

   if(okBuy && okSell)
      SR1_g_status = "coppia di ordini pendenti piazzata, in attesa";
   else
     {
      SR1_g_status = "errore piazzamento ordini (vedi scheda Esperti)";
      SR1_DeletePendings();
     }
  }

//+------------------------------------------------------------------+
//| Sposta un ordine pendente solo verso il prezzo (mai indietro),   |
//| cosi' resta sempre alla distanza fissa                           |
//+------------------------------------------------------------------+
void SR1_TrailPending(ulong ticket, ENUM_ORDER_TYPE type, double curPrice)
  {
   double dist = MathMax(SR1_InpDistancePips * SR1_g_pip, SR1_MinDistance());
   double step = MathMax(SR1_InpStepPips * SR1_g_pip, SymbolInfoDouble(SR1_SYM, SYMBOL_POINT));

   double newPrice;
   if(type == ORDER_TYPE_SELL_STOP)
     {
      newPrice = NormalizeDouble(SymbolInfoDouble(SR1_SYM, SYMBOL_BID) - dist, ((int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS)));
      if(newPrice < curPrice + step) return;       // sale solo se il prezzo sale
     }
   else
     {
      newPrice = NormalizeDouble(SymbolInfoDouble(SR1_SYM, SYMBOL_ASK) + dist, ((int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS)));
      if(newPrice > curPrice - step) return;       // scende solo se il prezzo scende
     }

   if(!SR1_trade.OrderModify(ticket, newPrice, 0.0, 0.0, ORDER_TIME_GTC, 0))
      SR1_LogOnce(StringFormat("Spostamento ordine rifiutato: %s (codice %d)",
                           SR1_trade.ResultRetcodeDescription(), SR1_trade.ResultRetcode()));
  }

// Coppia iniziale (nessuna posizione): fa seguire entrambi gli ordini
void SR1_TrailPair()
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != SR1_SYM || OrderGetInteger(ORDER_MAGIC) != SR1_InpMagic) continue;
      SR1_TrailPending(t, (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE), OrderGetDouble(ORDER_PRICE_OPEN));
     }
  }

//+------------------------------------------------------------------+
//| Con posizione aperta: un solo ordine opposto, sempre a distanza  |
//| fissa dal prezzo (segue il prezzo come uno stop che inverte)     |
//+------------------------------------------------------------------+
void SR1_EnsureReversal(long type)
  {
   ENUM_ORDER_TYPE want = (type == POSITION_TYPE_BUY) ? ORDER_TYPE_SELL_STOP : ORDER_TYPE_BUY_STOP;

   int n = 0;
   ulong wt = 0;
   double wp = 0.0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != SR1_SYM || OrderGetInteger(ORDER_MAGIC) != SR1_InpMagic) continue;
      n++;
      if((ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE) == want)
        {
         wt = t;
         wp = OrderGetDouble(ORDER_PRICE_OPEN);
        }
     }

   if(n == 1 && wt != 0)
     {
      SR1_TrailPending(wt, want, wp);
      return;
     }

   if(TimeCurrent() - SR1_g_lastTry < 2) return;
   SR1_g_lastTry = TimeCurrent();

   if(n > 0) SR1_DeletePendings();

   double dist = MathMax(SR1_InpDistancePips * SR1_g_pip, SR1_MinDistance());
   double price = (want == ORDER_TYPE_SELL_STOP)
                  ? NormalizeDouble(SymbolInfoDouble(SR1_SYM, SYMBOL_BID) - dist, ((int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS)))
                  : NormalizeDouble(SymbolInfoDouble(SR1_SYM, SYMBOL_ASK) + dist, ((int)SymbolInfoInteger(SR1_SYM, SYMBOL_DIGITS)));

   // In conto netting l'ordine opposto deve avere il doppio del lotto per invertire davvero
   double lots = SR1_NormalizeLots(SR1_InpLots * 4100.0 / SymbolInfoDouble(SR1_SYM, SYMBOL_BID) * SR1_ScalaRegista() * (SR1_g_hedging ? 1.0 : 2.0));
   SR1_PlacePending(want, price, lots);
  }

//+------------------------------------------------------------------+
//| Logica principale                                                |
//+------------------------------------------------------------------+
void SR1_Manage()
  {
   double bq = SymbolInfoDouble(SR1_SYM, SYMBOL_BID);
   if(bq > 0) SR1_g_pip = 0.1 * bq / 4100.0;
   if(!SR1_g_active)
     {
      SR1_g_status = "FERMO (pulsante OFF)";
      SR1_DeletePendings();
      if(SR1_InpCloseOnOff) SR1_CloseAllPositions();
      return;
     }

   // Fuori dalla finestra oraria: niente ordini, cancella i pendenti (e opzionalmente chiude le posizioni)
   if(!SR1_InTimeWindow())
     {
      SR1_g_status = StringFormat("fuori orario (finestra %02d:%02d-%02d:%02d ora server)",
                              SR1_InpStartHour, SR1_InpStartMinute, SR1_InpEndHour, SR1_InpEndMinute);
      if(SR1_CountPendings() > 0) SR1_DeletePendings();
      if(SR1_InpCloseAtEnd && SR1_CountPositions() > 0) SR1_CloseAllPositions();
      return;
     }

   ulong  tk;
   long   type;
   double open;
   if(SR1_LatestPosition(tk, type, open))
     {
      SR1_CloseOthers(tk);          // dopo l'inversione chiude la posizione vecchia
      SR1_g_status = (type == POSITION_TYPE_BUY ? "BUY aperto" : "SELL aperto");
      SR1_g_status += ", inversione a " + DoubleToString(SR1_InpDistancePips, 1) + " pip";
      SR1_EnsureReversal(type);
      return;
     }

   int pend = SR1_CountPendings();
   if(pend == 2)
     {
      SR1_g_status = "coppia di ordini pendenti che seguono il prezzo";
      SR1_TrailPair();
      return;
     }
   if(pend > 0)
     {
      SR1_DeletePendings();         // ne e' rimasto uno solo: riparti da capo
      return;
     }
   SR1_PlacePair();
  }
//+------------------------------------------------------------------+

//==================== MODULO SR2_ = StopReverse_news ====================
string SR2_SYM = "";
//+------------------------------------------------------------------+
//|                                                StopReverseEA.mq5 |
//|  Solo Buy Stop e Sell Stop a distanza fissa, nessuno SL/TP.      |
//|  Quando scatta uno, l'altro lo chiude (inversione) e viceversa.  |
//|  Gli ordini pendenti seguono il prezzo, sempre a distanza fissa. |
//|  v1.10: filtro orario (ora server), opera solo nella finestra.    |
//+------------------------------------------------------------------+
// COPIA DI TEST (Claude, 01/11/2026): pip e lotti proporzionali al prezzo (1 pip = 0.10 $ e lotto = SR2_InpLots con oro a 4100)


bool SR2_InpUsaRegista = false;   // moltiplica i lotti per MP_SCALA del Regista (portafoglio a volatilita' costante)
double SR2_ScalaRegista()
  {
   if(!SR2_InpUsaRegista || !GlobalVariableCheck("MP_SCALA")) return 1.0;
   if(TimeCurrent() - GlobalVariableTime("MP_SCALA") > 3 * 86400) return 1.0;   // regista fermo da 3 giorni: nessuna scala
   return GlobalVariableGet("MP_SCALA");
  }
int SR2_InpTipoNews = 2;      // 1 NFP, 2 CPI, 3 PCE, 4 FOMC, 0 tutte
int SR2_InpFinestraMin = 1;   // minuti di finestra dall'uscita della news
datetime SR2_g_news[]; int SR2_g_nNews = 0;
void SR2_CaricaNews()
  {
   int h = FileOpen("news_eventi.csv", FILE_READ | FILE_ANSI | FILE_TXT);
   if(h == INVALID_HANDLE) { Print("news_eventi.csv non trovato"); return; }
   while(!FileIsEnding(h))
     {
      string r = FileReadString(h); string p[];
      if(StringSplit(r, ';', p) < 2) continue;
      if(SR2_InpTipoNews != 0 && (int)StringToInteger(p[0]) != SR2_InpTipoNews) continue;
      ArrayResize(SR2_g_news, SR2_g_nNews + 1); SR2_g_news[SR2_g_nNews++] = StringToTime(p[1]);
     }
   FileClose(h); PrintFormat("News caricate: %d (tipo %d)", SR2_g_nNews, SR2_InpTipoNews);
  }

//--- Strategia
double SR2_InpDistancePips = 50.0;     // Distanza fissa degli ordini (pip)
double SR2_InpLots = 0.10;     // Lotto fisso
double SR2_InpStepPips = 10.0;      // Spostamento minimo dell'ordine pendente (pip)

//--- Filtri e sicurezza
double SR2_InpMaxSpreadPips = 0.0;      // Spread max per piazzare la prima coppia (pip, 0 = nessun limite)
int SR2_InpDeviation = 10;       // Slippage massimo (punti)
long SR2_InpMagic = 20261402; // Magic number
double SR2_InpPipSizeOverride = 0.0;      // Dimensione pip manuale (0 = automatica)

//--- Filtro orario (ORA DEL SERVER DEL BROKER, la stessa del grafico e del Tester)
bool SR2_InpUseTimeFilter = true;     // Usa il filtro orario
int SR2_InpStartHour = 15;       // Ora di inizio (0-23)
int SR2_InpStartMinute = 25;       // Minuto di inizio (0-59)
int SR2_InpEndHour = 16;       // Ora di fine (0-23)
int SR2_InpEndMinute = 30;       // Minuto di fine (0-59)
bool SR2_InpCloseAtEnd = true;     // A fine finestra chiudi anche le posizioni aperte

//--- Controllo
bool SR2_InpStartActive = true;     // Parti già attivo (altrimenti premi il pulsante)
bool SR2_InpCloseOnOff = true;     // Con pulsante su FERMO chiudi anche le posizioni aperte

CTrade   SR2_trade;
double   SR2_g_pip      = 0.0;
bool     SR2_g_active   = true;
bool     SR2_g_hedging  = true;
datetime SR2_g_lastTry  = 0;
datetime SR2_g_lastMsg  = 0;
string   SR2_g_status   = "avvio...";
string   SR2_BTN        = "SAR_ToggleBtn";

//+------------------------------------------------------------------+
int SR2_OnInit()
  {
   int digits = (int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS);
   if(SR2_InpPipSizeOverride > 0.0)
      SR2_g_pip = SR2_InpPipSizeOverride;
   else
     {
      string up = SR2_SYM;
      StringToUpper(up);
      if(StringFind(up, "XAU") >= 0 || StringFind(up, "GOLD") >= 0)
         SR2_g_pip = 0.1;                       // oro: 1 pip = 0.10
      else if(StringFind(up, "XAG") >= 0 || StringFind(up, "SILVER") >= 0)
         SR2_g_pip = 0.01;                      // argento: 1 pip = 0.01
      else
         SR2_g_pip = (digits == 3 || digits == 5) ? SymbolInfoDouble(SR2_SYM, SYMBOL_POINT) * 10.0 : SymbolInfoDouble(SR2_SYM, SYMBOL_POINT);
     }

   SR2_CaricaNews();
   SR2_g_hedging = (AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);

   SR2_trade.SetExpertMagicNumber(SR2_InpMagic);
   SR2_trade.SetDeviationInPoints(SR2_InpDeviation);

   SR2_g_active = SR2_InpStartActive;
   SR2_CreateButton();
   SR2_UpdateButton();

   PU_Timer(1);
   PrintFormat("StopReverseEA avviato su %s. 1 pip = %s, conto %s, attivo=%d",
               SR2_SYM, DoubleToString(SR2_g_pip, digits), SR2_g_hedging ? "hedging" : "netting", (int)SR2_g_active);
   return(INIT_SUCCEEDED);
  }

void SR2_OnDeinit(const int reason)
  {
   PU_Kill();
   PU_ObjectDelete(0, SR2_BTN);
   PU_Comment("");
  }

void SR2_OnTick() { SR2_Manage(); }

void SR2_OnTimer()
  {
   SR2_Manage();
   PU_Comment("StopReverseEA\n",
           "Stato: ", SR2_g_status, "\n",
           "Spread: ", DoubleToString((SymbolInfoDouble(SR2_SYM, SYMBOL_ASK) - SymbolInfoDouble(SR2_SYM, SYMBOL_BID)) / SR2_g_pip, 1),
           " pip | 1 pip = ", DoubleToString(SR2_g_pip, ((int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS))), "\n",
           "Pendenti: ", SR2_CountPendings(), " | Posizioni: ", SR2_CountPositions());
  }

//+------------------------------------------------------------------+
//| Pulsante ON/OFF                                                  |
//+------------------------------------------------------------------+
void SR2_CreateButton()
  {
   PU_ObjectDelete(0, SR2_BTN);
   PU_ObjectCreate(0, SR2_BTN, OBJ_BUTTON, 0, 0, 0);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_XDISTANCE, 10);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_YDISTANCE, 25);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_XSIZE, 140);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_YSIZE, 28);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_FONTSIZE, 10);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_COLOR, clrWhite);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_SELECTABLE, false);
  }

void SR2_UpdateButton()
  {
   PU_ObjectSetString(0, SR2_BTN, OBJPROP_TEXT, SR2_g_active ? "EA: ATTIVO (clicca)" : "EA: FERMO (clicca)");
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_BGCOLOR, SR2_g_active ? clrSeaGreen : clrFireBrick);
   PU_ObjectSetInteger(0, SR2_BTN, OBJPROP_STATE, false);
   ChartRedraw();
  }

void SR2_OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
  {
   if(id == CHARTEVENT_OBJECT_CLICK && sparam == SR2_BTN)
     {
      SR2_g_active = !SR2_g_active;
      SR2_UpdateButton();
      SR2_Manage();
     }
  }

//+------------------------------------------------------------------+
//| Utilità                                                          |
//+------------------------------------------------------------------+
void SR2_LogOnce(string msg)
  {
   SR2_g_status = msg;
   if(TimeCurrent() - SR2_g_lastMsg >= 10)
     {
      SR2_g_lastMsg = TimeCurrent();
      Print("StopReverseEA: ", msg);
     }
  }

// true se l'ora del server e' dentro la finestra (supporta anche finestre a cavallo della mezzanotte)
bool SR2_InTimeWindow()
  {
   datetime now = TimeCurrent();
   for(int i = 0; i < SR2_g_nNews; i++)
      if(now >= SR2_g_news[i] && now < SR2_g_news[i] + SR2_InpFinestraMin * 60) return true;
   return false;
  }

double SR2_MinDistance()
  {
   long lvl = SymbolInfoInteger(SR2_SYM, SYMBOL_TRADE_STOPS_LEVEL);
   long frz = SymbolInfoInteger(SR2_SYM, SYMBOL_TRADE_FREEZE_LEVEL);
   return (double)MathMax(lvl, frz) * SymbolInfoDouble(SR2_SYM, SYMBOL_POINT) + SymbolInfoDouble(SR2_SYM, SYMBOL_POINT);
  }

double SR2_NormalizeLots(double lots)
  {
   double vmin  = SymbolInfoDouble(SR2_SYM, SYMBOL_VOLUME_MIN);
   double vmax  = SymbolInfoDouble(SR2_SYM, SYMBOL_VOLUME_MAX);
   double vstep = SymbolInfoDouble(SR2_SYM, SYMBOL_VOLUME_STEP);
   if(vstep > 0) lots = MathFloor(lots / vstep + 1e-9) * vstep;
   lots = MathMax(vmin, MathMin(vmax, lots));
   return NormalizeDouble(lots, 2);
  }

bool SR2_TradingAllowed()
  {
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED))
     {
      SR2_LogOnce("Trading algoritmico NON consentito: attiva il pulsante 'Trading algoritmico' e spunta 'Consenti trading algoritmico'.");
      return false;
     }
   if(SymbolInfoInteger(SR2_SYM, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL)
     {
      SR2_LogOnce("Il simbolo non permette il trading in questo momento (mercato chiuso?).");
      return false;
     }
   return true;
  }

int SR2_CountPositions()
  {
   int n = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR2_SYM && PositionGetInteger(POSITION_MAGIC) == SR2_InpMagic)
         n++;
     }
   return n;
  }

int SR2_CountPendings()
  {
   int n = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) == SR2_SYM && OrderGetInteger(ORDER_MAGIC) == SR2_InpMagic)
         n++;
     }
   return n;
  }

void SR2_DeletePendings()
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) == SR2_SYM && OrderGetInteger(ORDER_MAGIC) == SR2_InpMagic)
         SR2_trade.OrderDelete(t);
     }
  }

void SR2_CloseAllPositions()
  {
   SR2_trade.SetTypeFillingBySymbol(SR2_SYM);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR2_SYM && PositionGetInteger(POSITION_MAGIC) == SR2_InpMagic)
         SR2_trade.PositionClose(t);
     }
  }

// Restituisce la posizione piu' recente (quella che e' appena scattata)
bool SR2_LatestPosition(ulong &ticket, long &type, double &open)
  {
   long bestTime = -1;
   ticket = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != SR2_SYM || PositionGetInteger(POSITION_MAGIC) != SR2_InpMagic)
         continue;
      long tm = PositionGetInteger(POSITION_TIME_MSC);
      if(tm > bestTime)
        {
         bestTime = tm;
         ticket   = t;
         type     = PositionGetInteger(POSITION_TYPE);
         open     = PositionGetDouble(POSITION_PRICE_OPEN);
        }
     }
   return (ticket != 0);
  }

// Chiude tutte le posizioni tranne quella indicata (la vecchia, dopo l'inversione)
void SR2_CloseOthers(ulong keep)
  {
   SR2_trade.SetTypeFillingBySymbol(SR2_SYM);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0 || t == keep) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR2_SYM && PositionGetInteger(POSITION_MAGIC) == SR2_InpMagic)
         SR2_trade.PositionClose(t);
     }
  }

bool SR2_PlacePending(ENUM_ORDER_TYPE t, double price, double lots)
  {
   SR2_trade.SetTypeFilling(ORDER_FILLING_RETURN);   // valido per gli ordini pendenti
   bool ok;
   if(t == ORDER_TYPE_BUY_STOP)
      ok = SR2_trade.BuyStop(lots, price, SR2_SYM, 0.0, 0.0, ORDER_TIME_GTC, 0, "SAR");
   else
      ok = SR2_trade.SellStop(lots, price, SR2_SYM, 0.0, 0.0, ORDER_TIME_GTC, 0, "SAR");

   if(!ok)
      PrintFormat("StopReverseEA: %s rifiutato: %s (codice %d) prezzo=%s lotti=%s",
                  EnumToString(t), SR2_trade.ResultRetcodeDescription(), SR2_trade.ResultRetcode(),
                  DoubleToString(price, ((int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS))), DoubleToString(lots, 2));
   return ok;
  }

//+------------------------------------------------------------------+
//| Prima coppia: Buy Stop e Sell Stop a distanza fissa              |
//+------------------------------------------------------------------+
void SR2_PlacePair()
  {
   if(TimeCurrent() - SR2_g_lastTry < 3) return;
   SR2_g_lastTry = TimeCurrent();

   if(!SR2_TradingAllowed()) return;

   double ask = SymbolInfoDouble(SR2_SYM, SYMBOL_ASK);
   double bid = SymbolInfoDouble(SR2_SYM, SYMBOL_BID);
   if(ask <= 0 || bid <= 0)
     {
      SR2_LogOnce("Prezzi non disponibili.");
      return;
     }
   if(SR2_InpMaxSpreadPips > 0.0 && (ask - bid) > SR2_InpMaxSpreadPips * SR2_g_pip)
     {
      SR2_LogOnce(StringFormat("Spread troppo alto: %.1f pip (max %.1f). Alza SR2_InpMaxSpreadPips o mettilo a 0.",
                           (ask - bid) / SR2_g_pip, SR2_InpMaxSpreadPips));
      return;
     }

   double dist = MathMax(SR2_InpDistancePips * SR2_g_pip, SR2_MinDistance());
   double lots = SR2_NormalizeLots(SR2_InpLots * 4100.0 / SymbolInfoDouble(SR2_SYM, SYMBOL_BID) * SR2_ScalaRegista());

   bool okBuy  = SR2_PlacePending(ORDER_TYPE_BUY_STOP,  NormalizeDouble(ask + dist, ((int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS))), lots);
   bool okSell = SR2_PlacePending(ORDER_TYPE_SELL_STOP, NormalizeDouble(bid - dist, ((int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS))), lots);

   if(okBuy && okSell)
      SR2_g_status = "coppia di ordini pendenti piazzata, in attesa";
   else
     {
      SR2_g_status = "errore piazzamento ordini (vedi scheda Esperti)";
      SR2_DeletePendings();
     }
  }

//+------------------------------------------------------------------+
//| Sposta un ordine pendente solo verso il prezzo (mai indietro),   |
//| cosi' resta sempre alla distanza fissa                           |
//+------------------------------------------------------------------+
void SR2_TrailPending(ulong ticket, ENUM_ORDER_TYPE type, double curPrice)
  {
   double dist = MathMax(SR2_InpDistancePips * SR2_g_pip, SR2_MinDistance());
   double step = MathMax(SR2_InpStepPips * SR2_g_pip, SymbolInfoDouble(SR2_SYM, SYMBOL_POINT));

   double newPrice;
   if(type == ORDER_TYPE_SELL_STOP)
     {
      newPrice = NormalizeDouble(SymbolInfoDouble(SR2_SYM, SYMBOL_BID) - dist, ((int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS)));
      if(newPrice < curPrice + step) return;       // sale solo se il prezzo sale
     }
   else
     {
      newPrice = NormalizeDouble(SymbolInfoDouble(SR2_SYM, SYMBOL_ASK) + dist, ((int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS)));
      if(newPrice > curPrice - step) return;       // scende solo se il prezzo scende
     }

   if(!SR2_trade.OrderModify(ticket, newPrice, 0.0, 0.0, ORDER_TIME_GTC, 0))
      SR2_LogOnce(StringFormat("Spostamento ordine rifiutato: %s (codice %d)",
                           SR2_trade.ResultRetcodeDescription(), SR2_trade.ResultRetcode()));
  }

// Coppia iniziale (nessuna posizione): fa seguire entrambi gli ordini
void SR2_TrailPair()
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != SR2_SYM || OrderGetInteger(ORDER_MAGIC) != SR2_InpMagic) continue;
      SR2_TrailPending(t, (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE), OrderGetDouble(ORDER_PRICE_OPEN));
     }
  }

//+------------------------------------------------------------------+
//| Con posizione aperta: un solo ordine opposto, sempre a distanza  |
//| fissa dal prezzo (segue il prezzo come uno stop che inverte)     |
//+------------------------------------------------------------------+
void SR2_EnsureReversal(long type)
  {
   ENUM_ORDER_TYPE want = (type == POSITION_TYPE_BUY) ? ORDER_TYPE_SELL_STOP : ORDER_TYPE_BUY_STOP;

   int n = 0;
   ulong wt = 0;
   double wp = 0.0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != SR2_SYM || OrderGetInteger(ORDER_MAGIC) != SR2_InpMagic) continue;
      n++;
      if((ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE) == want)
        {
         wt = t;
         wp = OrderGetDouble(ORDER_PRICE_OPEN);
        }
     }

   if(n == 1 && wt != 0)
     {
      SR2_TrailPending(wt, want, wp);
      return;
     }

   if(TimeCurrent() - SR2_g_lastTry < 2) return;
   SR2_g_lastTry = TimeCurrent();

   if(n > 0) SR2_DeletePendings();

   double dist = MathMax(SR2_InpDistancePips * SR2_g_pip, SR2_MinDistance());
   double price = (want == ORDER_TYPE_SELL_STOP)
                  ? NormalizeDouble(SymbolInfoDouble(SR2_SYM, SYMBOL_BID) - dist, ((int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS)))
                  : NormalizeDouble(SymbolInfoDouble(SR2_SYM, SYMBOL_ASK) + dist, ((int)SymbolInfoInteger(SR2_SYM, SYMBOL_DIGITS)));

   // In conto netting l'ordine opposto deve avere il doppio del lotto per invertire davvero
   double lots = SR2_NormalizeLots(SR2_InpLots * 4100.0 / SymbolInfoDouble(SR2_SYM, SYMBOL_BID) * SR2_ScalaRegista() * (SR2_g_hedging ? 1.0 : 2.0));
   SR2_PlacePending(want, price, lots);
  }

//+------------------------------------------------------------------+
//| Logica principale                                                |
//+------------------------------------------------------------------+
void SR2_Manage()
  {
   double bq = SymbolInfoDouble(SR2_SYM, SYMBOL_BID);
   if(bq > 0) SR2_g_pip = 0.1 * bq / 4100.0;
   if(!SR2_g_active)
     {
      SR2_g_status = "FERMO (pulsante OFF)";
      SR2_DeletePendings();
      if(SR2_InpCloseOnOff) SR2_CloseAllPositions();
      return;
     }

   // Fuori dalla finestra oraria: niente ordini, cancella i pendenti (e opzionalmente chiude le posizioni)
   if(!SR2_InTimeWindow())
     {
      SR2_g_status = StringFormat("fuori orario (finestra %02d:%02d-%02d:%02d ora server)",
                              SR2_InpStartHour, SR2_InpStartMinute, SR2_InpEndHour, SR2_InpEndMinute);
      if(SR2_CountPendings() > 0) SR2_DeletePendings();
      if(SR2_InpCloseAtEnd && SR2_CountPositions() > 0) SR2_CloseAllPositions();
      return;
     }

   ulong  tk;
   long   type;
   double open;
   if(SR2_LatestPosition(tk, type, open))
     {
      SR2_CloseOthers(tk);          // dopo l'inversione chiude la posizione vecchia
      SR2_g_status = (type == POSITION_TYPE_BUY ? "BUY aperto" : "SELL aperto");
      SR2_g_status += ", inversione a " + DoubleToString(SR2_InpDistancePips, 1) + " pip";
      SR2_EnsureReversal(type);
      return;
     }

   int pend = SR2_CountPendings();
   if(pend == 2)
     {
      SR2_g_status = "coppia di ordini pendenti che seguono il prezzo";
      SR2_TrailPair();
      return;
     }
   if(pend > 0)
     {
      SR2_DeletePendings();         // ne e' rimasto uno solo: riparti da capo
      return;
     }
   SR2_PlacePair();
  }
//+------------------------------------------------------------------+

//==================== MODULO SR3_ = StopReverse_news ====================
string SR3_SYM = "";
//+------------------------------------------------------------------+
//|                                                StopReverseEA.mq5 |
//|  Solo Buy Stop e Sell Stop a distanza fissa, nessuno SL/TP.      |
//|  Quando scatta uno, l'altro lo chiude (inversione) e viceversa.  |
//|  Gli ordini pendenti seguono il prezzo, sempre a distanza fissa. |
//|  v1.10: filtro orario (ora server), opera solo nella finestra.    |
//+------------------------------------------------------------------+
// COPIA DI TEST (Claude, 01/11/2026): pip e lotti proporzionali al prezzo (1 pip = 0.10 $ e lotto = SR3_InpLots con oro a 4100)


bool SR3_InpUsaRegista = false;   // moltiplica i lotti per MP_SCALA del Regista (portafoglio a volatilita' costante)
double SR3_ScalaRegista()
  {
   if(!SR3_InpUsaRegista || !GlobalVariableCheck("MP_SCALA")) return 1.0;
   if(TimeCurrent() - GlobalVariableTime("MP_SCALA") > 3 * 86400) return 1.0;   // regista fermo da 3 giorni: nessuna scala
   return GlobalVariableGet("MP_SCALA");
  }
int SR3_InpTipoNews = 4;      // 1 NFP, 2 CPI, 3 PCE, 4 FOMC, 0 tutte
int SR3_InpFinestraMin = 1;   // minuti di finestra dall'uscita della news
datetime SR3_g_news[]; int SR3_g_nNews = 0;
void SR3_CaricaNews()
  {
   int h = FileOpen("news_eventi.csv", FILE_READ | FILE_ANSI | FILE_TXT);
   if(h == INVALID_HANDLE) { Print("news_eventi.csv non trovato"); return; }
   while(!FileIsEnding(h))
     {
      string r = FileReadString(h); string p[];
      if(StringSplit(r, ';', p) < 2) continue;
      if(SR3_InpTipoNews != 0 && (int)StringToInteger(p[0]) != SR3_InpTipoNews) continue;
      ArrayResize(SR3_g_news, SR3_g_nNews + 1); SR3_g_news[SR3_g_nNews++] = StringToTime(p[1]);
     }
   FileClose(h); PrintFormat("News caricate: %d (tipo %d)", SR3_g_nNews, SR3_InpTipoNews);
  }

//--- Strategia
double SR3_InpDistancePips = 50.0;     // Distanza fissa degli ordini (pip)
double SR3_InpLots = 0.10;     // Lotto fisso
double SR3_InpStepPips = 10.0;      // Spostamento minimo dell'ordine pendente (pip)

//--- Filtri e sicurezza
double SR3_InpMaxSpreadPips = 0.0;      // Spread max per piazzare la prima coppia (pip, 0 = nessun limite)
int SR3_InpDeviation = 10;       // Slippage massimo (punti)
long SR3_InpMagic = 20261403; // Magic number
double SR3_InpPipSizeOverride = 0.0;      // Dimensione pip manuale (0 = automatica)

//--- Filtro orario (ORA DEL SERVER DEL BROKER, la stessa del grafico e del Tester)
bool SR3_InpUseTimeFilter = true;     // Usa il filtro orario
int SR3_InpStartHour = 15;       // Ora di inizio (0-23)
int SR3_InpStartMinute = 25;       // Minuto di inizio (0-59)
int SR3_InpEndHour = 16;       // Ora di fine (0-23)
int SR3_InpEndMinute = 30;       // Minuto di fine (0-59)
bool SR3_InpCloseAtEnd = true;     // A fine finestra chiudi anche le posizioni aperte

//--- Controllo
bool SR3_InpStartActive = true;     // Parti già attivo (altrimenti premi il pulsante)
bool SR3_InpCloseOnOff = true;     // Con pulsante su FERMO chiudi anche le posizioni aperte

CTrade   SR3_trade;
double   SR3_g_pip      = 0.0;
bool     SR3_g_active   = true;
bool     SR3_g_hedging  = true;
datetime SR3_g_lastTry  = 0;
datetime SR3_g_lastMsg  = 0;
string   SR3_g_status   = "avvio...";
string   SR3_BTN        = "SAR_ToggleBtn";

//+------------------------------------------------------------------+
int SR3_OnInit()
  {
   int digits = (int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS);
   if(SR3_InpPipSizeOverride > 0.0)
      SR3_g_pip = SR3_InpPipSizeOverride;
   else
     {
      string up = SR3_SYM;
      StringToUpper(up);
      if(StringFind(up, "XAU") >= 0 || StringFind(up, "GOLD") >= 0)
         SR3_g_pip = 0.1;                       // oro: 1 pip = 0.10
      else if(StringFind(up, "XAG") >= 0 || StringFind(up, "SILVER") >= 0)
         SR3_g_pip = 0.01;                      // argento: 1 pip = 0.01
      else
         SR3_g_pip = (digits == 3 || digits == 5) ? SymbolInfoDouble(SR3_SYM, SYMBOL_POINT) * 10.0 : SymbolInfoDouble(SR3_SYM, SYMBOL_POINT);
     }

   SR3_CaricaNews();
   SR3_g_hedging = (AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);

   SR3_trade.SetExpertMagicNumber(SR3_InpMagic);
   SR3_trade.SetDeviationInPoints(SR3_InpDeviation);

   SR3_g_active = SR3_InpStartActive;
   SR3_CreateButton();
   SR3_UpdateButton();

   PU_Timer(1);
   PrintFormat("StopReverseEA avviato su %s. 1 pip = %s, conto %s, attivo=%d",
               SR3_SYM, DoubleToString(SR3_g_pip, digits), SR3_g_hedging ? "hedging" : "netting", (int)SR3_g_active);
   return(INIT_SUCCEEDED);
  }

void SR3_OnDeinit(const int reason)
  {
   PU_Kill();
   PU_ObjectDelete(0, SR3_BTN);
   PU_Comment("");
  }

void SR3_OnTick() { SR3_Manage(); }

void SR3_OnTimer()
  {
   SR3_Manage();
   PU_Comment("StopReverseEA\n",
           "Stato: ", SR3_g_status, "\n",
           "Spread: ", DoubleToString((SymbolInfoDouble(SR3_SYM, SYMBOL_ASK) - SymbolInfoDouble(SR3_SYM, SYMBOL_BID)) / SR3_g_pip, 1),
           " pip | 1 pip = ", DoubleToString(SR3_g_pip, ((int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS))), "\n",
           "Pendenti: ", SR3_CountPendings(), " | Posizioni: ", SR3_CountPositions());
  }

//+------------------------------------------------------------------+
//| Pulsante ON/OFF                                                  |
//+------------------------------------------------------------------+
void SR3_CreateButton()
  {
   PU_ObjectDelete(0, SR3_BTN);
   PU_ObjectCreate(0, SR3_BTN, OBJ_BUTTON, 0, 0, 0);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_XDISTANCE, 10);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_YDISTANCE, 25);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_XSIZE, 140);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_YSIZE, 28);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_FONTSIZE, 10);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_COLOR, clrWhite);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_SELECTABLE, false);
  }

void SR3_UpdateButton()
  {
   PU_ObjectSetString(0, SR3_BTN, OBJPROP_TEXT, SR3_g_active ? "EA: ATTIVO (clicca)" : "EA: FERMO (clicca)");
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_BGCOLOR, SR3_g_active ? clrSeaGreen : clrFireBrick);
   PU_ObjectSetInteger(0, SR3_BTN, OBJPROP_STATE, false);
   ChartRedraw();
  }

void SR3_OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
  {
   if(id == CHARTEVENT_OBJECT_CLICK && sparam == SR3_BTN)
     {
      SR3_g_active = !SR3_g_active;
      SR3_UpdateButton();
      SR3_Manage();
     }
  }

//+------------------------------------------------------------------+
//| Utilità                                                          |
//+------------------------------------------------------------------+
void SR3_LogOnce(string msg)
  {
   SR3_g_status = msg;
   if(TimeCurrent() - SR3_g_lastMsg >= 10)
     {
      SR3_g_lastMsg = TimeCurrent();
      Print("StopReverseEA: ", msg);
     }
  }

// true se l'ora del server e' dentro la finestra (supporta anche finestre a cavallo della mezzanotte)
bool SR3_InTimeWindow()
  {
   datetime now = TimeCurrent();
   for(int i = 0; i < SR3_g_nNews; i++)
      if(now >= SR3_g_news[i] && now < SR3_g_news[i] + SR3_InpFinestraMin * 60) return true;
   return false;
  }

double SR3_MinDistance()
  {
   long lvl = SymbolInfoInteger(SR3_SYM, SYMBOL_TRADE_STOPS_LEVEL);
   long frz = SymbolInfoInteger(SR3_SYM, SYMBOL_TRADE_FREEZE_LEVEL);
   return (double)MathMax(lvl, frz) * SymbolInfoDouble(SR3_SYM, SYMBOL_POINT) + SymbolInfoDouble(SR3_SYM, SYMBOL_POINT);
  }

double SR3_NormalizeLots(double lots)
  {
   double vmin  = SymbolInfoDouble(SR3_SYM, SYMBOL_VOLUME_MIN);
   double vmax  = SymbolInfoDouble(SR3_SYM, SYMBOL_VOLUME_MAX);
   double vstep = SymbolInfoDouble(SR3_SYM, SYMBOL_VOLUME_STEP);
   if(vstep > 0) lots = MathFloor(lots / vstep + 1e-9) * vstep;
   lots = MathMax(vmin, MathMin(vmax, lots));
   return NormalizeDouble(lots, 2);
  }

bool SR3_TradingAllowed()
  {
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED))
     {
      SR3_LogOnce("Trading algoritmico NON consentito: attiva il pulsante 'Trading algoritmico' e spunta 'Consenti trading algoritmico'.");
      return false;
     }
   if(SymbolInfoInteger(SR3_SYM, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL)
     {
      SR3_LogOnce("Il simbolo non permette il trading in questo momento (mercato chiuso?).");
      return false;
     }
   return true;
  }

int SR3_CountPositions()
  {
   int n = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR3_SYM && PositionGetInteger(POSITION_MAGIC) == SR3_InpMagic)
         n++;
     }
   return n;
  }

int SR3_CountPendings()
  {
   int n = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) == SR3_SYM && OrderGetInteger(ORDER_MAGIC) == SR3_InpMagic)
         n++;
     }
   return n;
  }

void SR3_DeletePendings()
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) == SR3_SYM && OrderGetInteger(ORDER_MAGIC) == SR3_InpMagic)
         SR3_trade.OrderDelete(t);
     }
  }

void SR3_CloseAllPositions()
  {
   SR3_trade.SetTypeFillingBySymbol(SR3_SYM);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR3_SYM && PositionGetInteger(POSITION_MAGIC) == SR3_InpMagic)
         SR3_trade.PositionClose(t);
     }
  }

// Restituisce la posizione piu' recente (quella che e' appena scattata)
bool SR3_LatestPosition(ulong &ticket, long &type, double &open)
  {
   long bestTime = -1;
   ticket = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != SR3_SYM || PositionGetInteger(POSITION_MAGIC) != SR3_InpMagic)
         continue;
      long tm = PositionGetInteger(POSITION_TIME_MSC);
      if(tm > bestTime)
        {
         bestTime = tm;
         ticket   = t;
         type     = PositionGetInteger(POSITION_TYPE);
         open     = PositionGetDouble(POSITION_PRICE_OPEN);
        }
     }
   return (ticket != 0);
  }

// Chiude tutte le posizioni tranne quella indicata (la vecchia, dopo l'inversione)
void SR3_CloseOthers(ulong keep)
  {
   SR3_trade.SetTypeFillingBySymbol(SR3_SYM);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0 || t == keep) continue;
      if(PositionGetString(POSITION_SYMBOL) == SR3_SYM && PositionGetInteger(POSITION_MAGIC) == SR3_InpMagic)
         SR3_trade.PositionClose(t);
     }
  }

bool SR3_PlacePending(ENUM_ORDER_TYPE t, double price, double lots)
  {
   SR3_trade.SetTypeFilling(ORDER_FILLING_RETURN);   // valido per gli ordini pendenti
   bool ok;
   if(t == ORDER_TYPE_BUY_STOP)
      ok = SR3_trade.BuyStop(lots, price, SR3_SYM, 0.0, 0.0, ORDER_TIME_GTC, 0, "SAR");
   else
      ok = SR3_trade.SellStop(lots, price, SR3_SYM, 0.0, 0.0, ORDER_TIME_GTC, 0, "SAR");

   if(!ok)
      PrintFormat("StopReverseEA: %s rifiutato: %s (codice %d) prezzo=%s lotti=%s",
                  EnumToString(t), SR3_trade.ResultRetcodeDescription(), SR3_trade.ResultRetcode(),
                  DoubleToString(price, ((int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS))), DoubleToString(lots, 2));
   return ok;
  }

//+------------------------------------------------------------------+
//| Prima coppia: Buy Stop e Sell Stop a distanza fissa              |
//+------------------------------------------------------------------+
void SR3_PlacePair()
  {
   if(TimeCurrent() - SR3_g_lastTry < 3) return;
   SR3_g_lastTry = TimeCurrent();

   if(!SR3_TradingAllowed()) return;

   double ask = SymbolInfoDouble(SR3_SYM, SYMBOL_ASK);
   double bid = SymbolInfoDouble(SR3_SYM, SYMBOL_BID);
   if(ask <= 0 || bid <= 0)
     {
      SR3_LogOnce("Prezzi non disponibili.");
      return;
     }
   if(SR3_InpMaxSpreadPips > 0.0 && (ask - bid) > SR3_InpMaxSpreadPips * SR3_g_pip)
     {
      SR3_LogOnce(StringFormat("Spread troppo alto: %.1f pip (max %.1f). Alza SR3_InpMaxSpreadPips o mettilo a 0.",
                           (ask - bid) / SR3_g_pip, SR3_InpMaxSpreadPips));
      return;
     }

   double dist = MathMax(SR3_InpDistancePips * SR3_g_pip, SR3_MinDistance());
   double lots = SR3_NormalizeLots(SR3_InpLots * 4100.0 / SymbolInfoDouble(SR3_SYM, SYMBOL_BID) * SR3_ScalaRegista());

   bool okBuy  = SR3_PlacePending(ORDER_TYPE_BUY_STOP,  NormalizeDouble(ask + dist, ((int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS))), lots);
   bool okSell = SR3_PlacePending(ORDER_TYPE_SELL_STOP, NormalizeDouble(bid - dist, ((int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS))), lots);

   if(okBuy && okSell)
      SR3_g_status = "coppia di ordini pendenti piazzata, in attesa";
   else
     {
      SR3_g_status = "errore piazzamento ordini (vedi scheda Esperti)";
      SR3_DeletePendings();
     }
  }

//+------------------------------------------------------------------+
//| Sposta un ordine pendente solo verso il prezzo (mai indietro),   |
//| cosi' resta sempre alla distanza fissa                           |
//+------------------------------------------------------------------+
void SR3_TrailPending(ulong ticket, ENUM_ORDER_TYPE type, double curPrice)
  {
   double dist = MathMax(SR3_InpDistancePips * SR3_g_pip, SR3_MinDistance());
   double step = MathMax(SR3_InpStepPips * SR3_g_pip, SymbolInfoDouble(SR3_SYM, SYMBOL_POINT));

   double newPrice;
   if(type == ORDER_TYPE_SELL_STOP)
     {
      newPrice = NormalizeDouble(SymbolInfoDouble(SR3_SYM, SYMBOL_BID) - dist, ((int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS)));
      if(newPrice < curPrice + step) return;       // sale solo se il prezzo sale
     }
   else
     {
      newPrice = NormalizeDouble(SymbolInfoDouble(SR3_SYM, SYMBOL_ASK) + dist, ((int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS)));
      if(newPrice > curPrice - step) return;       // scende solo se il prezzo scende
     }

   if(!SR3_trade.OrderModify(ticket, newPrice, 0.0, 0.0, ORDER_TIME_GTC, 0))
      SR3_LogOnce(StringFormat("Spostamento ordine rifiutato: %s (codice %d)",
                           SR3_trade.ResultRetcodeDescription(), SR3_trade.ResultRetcode()));
  }

// Coppia iniziale (nessuna posizione): fa seguire entrambi gli ordini
void SR3_TrailPair()
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != SR3_SYM || OrderGetInteger(ORDER_MAGIC) != SR3_InpMagic) continue;
      SR3_TrailPending(t, (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE), OrderGetDouble(ORDER_PRICE_OPEN));
     }
  }

//+------------------------------------------------------------------+
//| Con posizione aperta: un solo ordine opposto, sempre a distanza  |
//| fissa dal prezzo (segue il prezzo come uno stop che inverte)     |
//+------------------------------------------------------------------+
void SR3_EnsureReversal(long type)
  {
   ENUM_ORDER_TYPE want = (type == POSITION_TYPE_BUY) ? ORDER_TYPE_SELL_STOP : ORDER_TYPE_BUY_STOP;

   int n = 0;
   ulong wt = 0;
   double wp = 0.0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != SR3_SYM || OrderGetInteger(ORDER_MAGIC) != SR3_InpMagic) continue;
      n++;
      if((ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE) == want)
        {
         wt = t;
         wp = OrderGetDouble(ORDER_PRICE_OPEN);
        }
     }

   if(n == 1 && wt != 0)
     {
      SR3_TrailPending(wt, want, wp);
      return;
     }

   if(TimeCurrent() - SR3_g_lastTry < 2) return;
   SR3_g_lastTry = TimeCurrent();

   if(n > 0) SR3_DeletePendings();

   double dist = MathMax(SR3_InpDistancePips * SR3_g_pip, SR3_MinDistance());
   double price = (want == ORDER_TYPE_SELL_STOP)
                  ? NormalizeDouble(SymbolInfoDouble(SR3_SYM, SYMBOL_BID) - dist, ((int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS)))
                  : NormalizeDouble(SymbolInfoDouble(SR3_SYM, SYMBOL_ASK) + dist, ((int)SymbolInfoInteger(SR3_SYM, SYMBOL_DIGITS)));

   // In conto netting l'ordine opposto deve avere il doppio del lotto per invertire davvero
   double lots = SR3_NormalizeLots(SR3_InpLots * 4100.0 / SymbolInfoDouble(SR3_SYM, SYMBOL_BID) * SR3_ScalaRegista() * (SR3_g_hedging ? 1.0 : 2.0));
   SR3_PlacePending(want, price, lots);
  }

//+------------------------------------------------------------------+
//| Logica principale                                                |
//+------------------------------------------------------------------+
void SR3_Manage()
  {
   double bq = SymbolInfoDouble(SR3_SYM, SYMBOL_BID);
   if(bq > 0) SR3_g_pip = 0.1 * bq / 4100.0;
   if(!SR3_g_active)
     {
      SR3_g_status = "FERMO (pulsante OFF)";
      SR3_DeletePendings();
      if(SR3_InpCloseOnOff) SR3_CloseAllPositions();
      return;
     }

   // Fuori dalla finestra oraria: niente ordini, cancella i pendenti (e opzionalmente chiude le posizioni)
   if(!SR3_InTimeWindow())
     {
      SR3_g_status = StringFormat("fuori orario (finestra %02d:%02d-%02d:%02d ora server)",
                              SR3_InpStartHour, SR3_InpStartMinute, SR3_InpEndHour, SR3_InpEndMinute);
      if(SR3_CountPendings() > 0) SR3_DeletePendings();
      if(SR3_InpCloseAtEnd && SR3_CountPositions() > 0) SR3_CloseAllPositions();
      return;
     }

   ulong  tk;
   long   type;
   double open;
   if(SR3_LatestPosition(tk, type, open))
     {
      SR3_CloseOthers(tk);          // dopo l'inversione chiude la posizione vecchia
      SR3_g_status = (type == POSITION_TYPE_BUY ? "BUY aperto" : "SELL aperto");
      SR3_g_status += ", inversione a " + DoubleToString(SR3_InpDistancePips, 1) + " pip";
      SR3_EnsureReversal(type);
      return;
     }

   int pend = SR3_CountPendings();
   if(pend == 2)
     {
      SR3_g_status = "coppia di ordini pendenti che seguono il prezzo";
      SR3_TrailPair();
      return;
     }
   if(pend > 0)
     {
      SR3_DeletePendings();         // ne e' rimasto uno solo: riparti da capo
      return;
     }
   SR3_PlacePair();
  }
//+------------------------------------------------------------------+

//==================== MODULO MM_ = MomentoMercati ====================
//+------------------------------------------------------------------+
//| MomentoMercati.mq5 - momentum tra mercati (Motore Profitto, 04/11/2026)
//| Mettilo su UN grafico qualsiasi. Il primo giorno di borsa di ogni |
//| mese (dopo MM_InpOra del server) ordina i mercati per rendimento     |
//| degli ultimi 12 mesi escluso l'ultimo (12-1) e tiene LONG i primi |
//| MM_InpTop. Peso di ciascuno: MM_InpScala * MM_InpVolObiettivo / (vol 60g * |
//| radice(MM_InpTop)) dell'equity (massimo 3x MM_InpScala). Solo long.     |
//| Test (lab famiglie, 2023-ott 2026, costi e swap): +14,8%/anno,    |
//| Sharpe 1,0 a scala piena; nel portafoglio MIX12 si usa scala 0,23.|
//| Magic 993000.                                                     |
//+------------------------------------------------------------------+

string MM_InpSimboli = "CHINA50.s,CL-OIL.s,Cocoa-Cs,Coffee-Cs,COPPER-Cs,Cotton-Cs,DJ30.s,ES35.s,EU50.s,FRA40.s,GAS-Cs,GASOIL-Cs,GER40.s,HK50.s,NAS100.s,NG-Cs,Nikkei225.s,OJ-Cs,SP500.s,SPI200.s,Sugar-Cs,UKOUSD.s,US2000.s,USOUSD.s,Wheat-Cs,XAGUSD.s,XAUEUR.s,XAUUSD.s,BTCUSD,ETHUSD,EURUSD.s,GBPUSD.s,AUDUSD.s,NZDUSD.s,USDJPY.s,USDCHF.s,USDCAD.s"; // mercati
int MM_InpTop = 5;      // quanti mercati tenere
int MM_InpLookback = 252;    // giorni di borsa del momentum (12 mesi)
int MM_InpSalta = 21;     // giorni piu' recenti esclusi (1 mese)
int MM_InpVolGiorni = 60;     // giorni per la volatilita'
double MM_InpVolObiettivo = 0.1;   // volatilita' annua obiettivo per mercato (prima della scala)
double MM_InpScala = 0.23;   // scala nel portafoglio (1.0 = strategia piena; MIX12 = 0.23)
int MM_InpOra = 12;     // ora del server dopo cui ribilanciare (mercati aperti)
long MM_InpMagic = 993000; // numero magico
bool MM_InpRibilanciaOra = true; // true = ribilancia subito all'avvio (prova)

string MM_g_sym[]; int MM_g_n = 0; int MM_g_mese = -1;
CTrade MM_trade;

double MM_Momentum(string s)
  {
   double c[]; ArraySetAsSeries(c, true);
   if(CopyClose(s, PERIOD_D1, 1, MM_InpLookback + 1, c) < MM_InpLookback + 1) return EMPTY_VALUE;
   if(c[MM_InpLookback] <= 0) return EMPTY_VALUE;
   return c[MM_InpSalta] / c[MM_InpLookback] - 1.0;
  }
double MM_Vol(string s)
  {
   double c[]; ArraySetAsSeries(c, true);
   if(CopyClose(s, PERIOD_D1, 1, MM_InpVolGiorni + 1, c) < MM_InpVolGiorni + 1) return 0;
   double m = 0, q = 0; int n = MM_InpVolGiorni;
   for(int i = 0; i < n; i++) { double r = c[i] / c[i + 1] - 1; m += r; q += r * r; }
   m /= n; double v = q / n - m * m;
   return v > 0 ? MathSqrt(v) * MathSqrt(252.0) : 0;
  }
double MM_ValoreLotto(string s)
  {
   double px = SymbolInfoDouble(s, SYMBOL_BID), tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
   return (tv > 0 && ts > 0) ? px * tv / ts : 0;     // valore di 1 lotto nella valuta del conto
  }
double MM_LottiAttuali(string s, ulong &tk)
  {
   tk = 0; double v = 0;
   for(int k = PositionsTotal() - 1; k >= 0; k--)
     {
      ulong t = PositionGetTicket(k);
      if(t && PositionGetString(POSITION_SYMBOL) == s && PositionGetInteger(POSITION_MAGIC) == MM_InpMagic) { v += PositionGetDouble(POSITION_VOLUME); tk = t; }
     }
   return v;
  }
void MM_Chiudi(string s)
  {
   for(int k = PositionsTotal() - 1; k >= 0; k--)
     {
      ulong t = PositionGetTicket(k);
      if(t && PositionGetString(POSITION_SYMBOL) == s && PositionGetInteger(POSITION_MAGIC) == MM_InpMagic) MM_trade.PositionClose(t);
     }
  }
void MM_Ribilancia()
  {
   double mom[]; ArrayResize(mom, MM_g_n); int idx[]; ArrayResize(idx, MM_g_n);
   for(int i = 0; i < MM_g_n; i++) { mom[i] = MM_Momentum(MM_g_sym[i]); idx[i] = i; }
   for(int a = 0; a < MM_g_n - 1; a++)                       // ordina per momentum decrescente
      for(int b = a + 1; b < MM_g_n; b++)
         if(mom[idx[b]] != EMPTY_VALUE && (mom[idx[a]] == EMPTY_VALUE || mom[idx[b]] > mom[idx[a]])) { int t = idx[a]; idx[a] = idx[b]; idx[b] = t; }
   bool scelto[]; ArrayResize(scelto, MM_g_n); ArrayInitialize(scelto, false);
   int presi = 0;
   for(int a = 0; a < MM_g_n && presi < MM_InpTop; a++) if(mom[idx[a]] != EMPTY_VALUE) { scelto[idx[a]] = true; presi++; }
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   MM_trade.SetExpertMagicNumber(MM_InpMagic);
   for(int i = 0; i < MM_g_n; i++)
     {
      string s = MM_g_sym[i]; ulong tk; double ora = MM_LottiAttuali(s, tk);
      if(!scelto[i]) { if(ora > 0) { MM_Chiudi(s); PrintFormat("MomentoMercati: esce da %s", s); } continue; }
      double v = MM_Vol(s), vl = MM_ValoreLotto(s);
      if(v <= 0 || vl <= 0) { PrintFormat("MomentoMercati: %s senza dati, salto", s); continue; }
      double peso = MathMin(MM_InpScala * MM_InpVolObiettivo / (v * MathSqrt((double)MM_InpTop)), 3.0 * MM_InpScala);
      double st = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN), mx = SymbolInfoDouble(s, SYMBOL_VOLUME_MAX);
      double lot = MathFloor(peso * eq / vl / st + 1e-9) * st;
      if(lot < mn) { PrintFormat("MomentoMercati: %s lotto %.3f sotto il minimo %.2f (conto troppo piccolo), salto", s, lot, mn); if(ora > 0) MM_Chiudi(s); continue; }
      lot = MathMin(lot, mx);
      if(ora > 0 && MathAbs(ora - lot) <= 0.3 * lot) { PrintFormat("MomentoMercati: tiene %s (%.2f lotti)", s, ora); continue; }
      if(ora > 0) MM_Chiudi(s);
      MM_trade.SetTypeFillingBySymbol(s);
      bool ok = MM_trade.Buy(lot, s, 0, 0, 0, "momento");
      PrintFormat("MomentoMercati: LONG %s %.2f lotti (momentum %+.1f%%, vol %.0f%%, peso %.0f%% del conto) %s",
                  s, lot, mom[i] * 100, v * 100, peso * 100, ok ? "ok" : MM_trade.ResultRetcodeDescription());
     }
  }
int MM_OnInit()
  {
   string a[]; MM_g_n = StringSplit(MM_InpSimboli, ',', a); ArrayResize(MM_g_sym, MM_g_n);
   for(int i = 0; i < MM_g_n; i++) { MM_g_sym[i] = a[i]; StringTrimLeft(MM_g_sym[i]); StringTrimRight(MM_g_sym[i]); SymbolSelect(MM_g_sym[i], true); }
   PrintFormat("MomentoMercati avviato: %d mercati, top %d, scala %.2f", MM_g_n, MM_InpTop, MM_InpScala);
   if(MM_InpRibilanciaOra) MM_g_mese = -2;
   PU_Timer(60);
   return INIT_SUCCEEDED;
  }
void MM_OnDeinit(const int r) { PU_Kill(); }
void MM_OnTimer()
  {
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   if(t.day_of_week == 0 || t.day_of_week == 6 || t.hour < MM_InpOra) return;
   if(MM_g_mese == -1) { MM_g_mese = t.mon; return; }            // all'avvio aspetta il mese dopo (salvo MM_InpRibilanciaOra)
   if(t.mon == MM_g_mese) return;
   MM_g_mese = t.mon;
   MM_Ribilancia();
  }
void MM_OnTick() { }


//==================== GUARDIANO CHALLENGE ====================
int    gs_giorno = -1; bool gs_fermo = false, gs_finito = false; double gs_rif = 0, gs_min = 0, gs_part = 0; int gs_fh = INVALID_HANDLE;
bool GS_Mio(long m) { return (m >= 881001 && m <= 881008) || (m >= 770500 && m <= 770504) || (m >= 20261401 && m <= 20261403) || m == 993000; }
void GS_ChiudiTutto()
  {
   CTrade tr;
   for(int r = 0; r < 3; r++)
     {
      for(int k = PositionsTotal() - 1; k >= 0; k--)
        { ulong t = PositionGetTicket(k); if(t && GS_Mio(PositionGetInteger(POSITION_MAGIC))) { tr.SetExpertMagicNumber(PositionGetInteger(POSITION_MAGIC)); tr.PositionClose(t); } }
      for(int k = OrdersTotal() - 1; k >= 0; k--)
        { ulong t = OrderGetTicket(k); if(t && GS_Mio(OrderGetInteger(ORDER_MAGIC))) tr.OrderDelete(t); }
     }
  }
void GS_Scrivi(datetime g, double fine)
  {
   if(!GS_Registro) return;
   if(gs_fh == INVALID_HANDLE)
     {
      gs_fh = FileOpen("Sprint_" + Insieme + "_" + (string)AccountInfoInteger(ACCOUNT_LOGIN) + ".csv", FILE_WRITE | FILE_READ | FILE_CSV | FILE_COMMON | FILE_ANSI, ';');
      if(gs_fh == INVALID_HANDLE) return;
      FileSeek(gs_fh, 0, SEEK_END);
     }
   FileWrite(gs_fh, TimeToString(g, TIME_DATE), DoubleToString(gs_rif, 2), DoubleToString(gs_min, 2), DoubleToString(fine, 2), gs_fermo ? "stop" : "");
   FileFlush(gs_fh);
  }
// true = i moduli possono lavorare
bool GS_Controlla()
  {
   datetime t = TimeCurrent(); int g = (int)(t / 86400); double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(g != gs_giorno)
     {
      if(gs_giorno >= 0) GS_Scrivi((datetime)gs_giorno * 86400, eq);
      gs_giorno = g; gs_rif = AccountInfoDouble(ACCOUNT_BALANCE); gs_min = eq;
      if(gs_fermo) { gs_fermo = false; if(UsaMomento) MM_g_mese = -2; Print("GUARDIANO: nuovo giorno, si riparte"); }
      if(UsaNews && GS_NewsProporzionali && gs_part > 0) { double l = MathMax(0.01, NormalizeDouble(SR_Lotti * eq / gs_part, 2)); SR1_InpLots = l; SR2_InpLots = l; SR3_InpLots = l; }
     }
   gs_min = MathMin(gs_min, eq);
   if(gs_finito) return false;
   if(GS_Obiettivo > 0 && eq >= gs_part * (1 + GS_Obiettivo / 100))
     { gs_finito = true; GS_ChiudiTutto(); PrintFormat("GUARDIANO: obiettivo +%.1f%% raggiunto (equity %.2f): chiuso tutto, EA fermo", GS_Obiettivo, eq); return false; }
   if(gs_fermo) { if(PositionsTotal() > 0 || OrdersTotal() > 0) GS_ChiudiTutto(); return false; }
   if(GS_StopGiorno > 0 && eq <= gs_rif * (1 - GS_StopGiorno / 100))
     { gs_fermo = true; GS_ChiudiTutto(); PrintFormat("GUARDIANO: perdita del giorno -%.1f%% (equity %.2f, inizio %.2f): chiuso tutto, fermo fino a domani", GS_StopGiorno, eq, gs_rif); return false; }
   return true;
  }

int OnInit()
  {
   if(UsaIntraday) { IP1_InpRischio = IP_RischioA; IP1_InpAttive = IP_Attive_A; IP1_InpSimboli = IP_Simboli; IP1_InpMinimoSempre = IP_MinimoSempre; if(IP1_OnInit() != INIT_SUCCEEDED) { Print("PortafoglioIntraday: modulo IP1_IntradayPortafoglio non avviato"); return INIT_FAILED; } }
   if(UsaIntraday) { IP2_InpRischio = IP_RischioB; IP2_InpAttive = IP_Attive_B; IP2_InpSimboli = IP_Simboli; IP2_InpMinimoSempre = IP_MinimoSempre; if(IP2_OnInit() != INIT_SUCCEEDED) { Print("PortafoglioIntraday: modulo IP2_IntradayPortafoglio non avviato"); return INIT_FAILED; } }
   if(UsaIntraday) { IP3_InpRischio = IP_RischioC; IP3_InpAttive = IP_Attive_C; IP3_InpSimboli = IP_Simboli; IP3_InpMinimoSempre = IP_MinimoSempre; if(IP3_OnInit() != INIT_SUCCEEDED) { Print("PortafoglioIntraday: modulo IP3_IntradayPortafoglio non avviato"); return INIT_FAILED; } }
   if(UsaFlip) { FL_InpEsposizione = FL_Esposizione; FL_InpSuffisso = FL_Suffisso; if(FL_OnInit() != INIT_SUCCEEDED) { Print("PortafoglioIntraday: modulo FL_FlipLotteria non avviato"); return INIT_FAILED; } }
   if(UsaNews) { SR1_InpLots = SR_Lotti; SR1_SYM = SR_Simbolo; SymbolSelect(SR_Simbolo, true); if(SR1_OnInit() != INIT_SUCCEEDED) { Print("PortafoglioIntraday: modulo SR1_StopReverse_news non avviato"); return INIT_FAILED; } }
   if(UsaNews) { SR2_InpLots = SR_Lotti; SR2_SYM = SR_Simbolo; SymbolSelect(SR_Simbolo, true); if(SR2_OnInit() != INIT_SUCCEEDED) { Print("PortafoglioIntraday: modulo SR2_StopReverse_news non avviato"); return INIT_FAILED; } }
   if(UsaNews) { SR3_InpLots = SR_Lotti; SR3_SYM = SR_Simbolo; SymbolSelect(SR_Simbolo, true); if(SR3_OnInit() != INIT_SUCCEEDED) { Print("PortafoglioIntraday: modulo SR3_StopReverse_news non avviato"); return INIT_FAILED; } }
   if(UsaMomento) { MM_InpScala = MM_Scala; MM_InpSimboli = MM_Simboli; if(MM_OnInit() != INIT_SUCCEEDED) { Print("PortafoglioIntraday: modulo MM_MomentoMercati non avviato"); return INIT_FAILED; } }
   PrintFormat("PortafoglioIntraday avviato: set %s | intraday %s (%.2f/%.2f/%.2f%%) | flip %s (%.2fx) | news %s (%.2f lotti) | momentum %s (%.2f)",
               Insieme, UsaIntraday ? "si" : "no", IP_RischioA, IP_RischioB, IP_RischioC, UsaFlip ? "si" : "no", FL_Esposizione, UsaNews ? "si" : "no", SR_Lotti, UsaMomento ? "si" : "no", MM_Scala);
   gs_part = GS_SaldoPartenza > 0 ? GS_SaldoPartenza : AccountInfoDouble(ACCOUNT_BALANCE);
   PrintFormat("GUARDIANO: stop giorno %.1f%%, obiettivo %.1f%% su %.2f", GS_StopGiorno, GS_Obiettivo, gs_part);
   EventSetTimer(1);
   return INIT_SUCCEEDED;
  }
void OnDeinit(const int r)
  {
   EventKillTimer();
   if(gs_giorno >= 0) GS_Scrivi((datetime)gs_giorno * 86400, AccountInfoDouble(ACCOUNT_EQUITY));
   if(gs_fh != INVALID_HANDLE) FileClose(gs_fh);
   if(UsaIntraday) IP1_OnDeinit(r);
   if(UsaIntraday) IP2_OnDeinit(r);
   if(UsaIntraday) IP3_OnDeinit(r);
   if(UsaFlip) FL_OnDeinit(r);
   if(UsaNews) SR1_OnDeinit(r);
   if(UsaNews) SR2_OnDeinit(r);
   if(UsaNews) SR3_OnDeinit(r);
   if(UsaMomento) MM_OnDeinit(r);
  }
ulong g_secondi = 0;
void OnTimer()
  {
   g_secondi++;
   if(!GS_Controlla()) return;
   if(UsaIntraday && g_secondi % 2 == 0) IP1_OnTimer();
   if(UsaIntraday && g_secondi % 2 == 0) IP2_OnTimer();
   if(UsaIntraday && g_secondi % 2 == 0) IP3_OnTimer();
   if(UsaFlip && g_secondi % 5 == 0) FL_OnTimer();
   if(UsaNews && g_secondi % 1 == 0) SR1_OnTimer();
   if(UsaNews && g_secondi % 1 == 0) SR2_OnTimer();
   if(UsaNews && g_secondi % 1 == 0) SR3_OnTimer();
   if(UsaMomento && g_secondi % 60 == 0) MM_OnTimer();
  }
void OnTick()
  {
   if(!GS_Controlla()) return;
   if(UsaIntraday) IP1_OnTick();
   if(UsaIntraday) IP2_OnTick();
   if(UsaIntraday) IP3_OnTick();
   if(UsaFlip) FL_OnTick();
   if(UsaNews) SR1_OnTick();
   if(UsaNews) SR2_OnTick();
   if(UsaNews) SR3_OnTick();
   if(UsaMomento) MM_OnTick();
  }
