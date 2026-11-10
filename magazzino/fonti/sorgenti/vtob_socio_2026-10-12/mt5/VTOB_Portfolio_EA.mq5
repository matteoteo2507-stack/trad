//+------------------------------------------------------------------+
//| VTOB_Portfolio_EA.mq5                                            |
//| Portafoglio di strategie VTOB (order block) su XAUUSD in un solo |
//| EA: fino a 5 slot, ognuno con il suo timeframe e le sue regole.  |
//| Logica OB derivata da "Volume-Trend Order Block Engine" di       |
//| BigBeluga (CC BY-NC-SA 4.0). Uso non commerciale.                |
//|                                                                  |
//| Regole (identiche al motore Python vtob del pacchetto):          |
//|  - indicatore ricalcolato sulle ultime N candele CHIUSE del TF   |
//|    dello slot: volatilità = SMA(high-low,50), Supertrend custom, |
//|    pivot (sinistra stretto, destra >=), un solo OB attivo,       |
//|    filtri età trend / EMA del TF superiore (candela chiusa) /    |
//|    distanza dalla linea, invalidazione, croce di retest;         |
//|  - ingresso a mercato all'apertura della candela dopo il segnale;|
//|  - stop = SL x volatilità della candela del segnale, target R:R; |
//|  - pareggio e trailing decisi alla chiusura delle candele del TF  |
//|    dello slot e applicati subito dopo; parziali sul tick che     |
//|    tocca il livello; time stop e chiusura del venerdì all'open;  |
//|  - un trade per OB (ultimo OB tradato salvato in GlobalVariable).|
//| Rischio di portafoglio: rischio % per trade x peso dello slot,   |
//| tetto al rischio aperto (le posizioni a pareggio contano 0),     |
//| perdita giornaliera/settimanale massima, riduzione dopo N        |
//| perdite di fila, dimensionamento per regime (trend D1).          |
//|                                                                  |
//| USARE PRIMA IN STRATEGY TESTER E SU CONTO DEMO.                  |
//+------------------------------------------------------------------+
#property copyright "VTOB Portfolio"
#property version   "2.10"
#property description "Portafoglio VTOB: fino a 5 strategie OB sul simbolo del grafico (un'istanza per simbolo)"
//| v2.10: pausa dalla dashboard (file <Id>.paused), stato JSON ed eventi per la dashboard, file nella cartella
//|        comune di MT5 (Terminal\Common\Files) se InpFileComuni = true. Logica dei segnali invariata.

#include <Trade\Trade.mqh>

enum ENUM_VTOB_TRAIL
  {
   TRAIL_NESSUNO    = 0,  // Nessuno
   TRAIL_SUPERTREND = 1,  // Linea Supertrend (trend stop)
   TRAIL_ATR        = 2,  // Chiusura - K x volatilità
   TRAIL_CHANDELIER = 3,  // Estremo dall'ingresso - K x volatilità
   TRAIL_SWING      = 4   // Ultimo pivot - K x volatilità
  };

enum ENUM_VTOB_TRAIL_START
  {
   TRAIL_SUBITO     = 0,  // Subito
   TRAIL_DOPO_BE    = 1,  // Dopo il pareggio
   TRAIL_DOPO_PARZ  = 2   // Dopo il primo parziale
  };

//--- portafoglio
input group "=== Portafoglio ==="
input string InpId              = "VTOB";   // Identificativo (GlobalVariable e file)
input double InpRischioBase     = 0.5;      // Rischio base per trade (% del balance)
input double InpTettoRischio    = 2.0;      // Tetto rischio aperto (x rischio base, 0 = off)
input double InpPerditaGiorno   = 3.0;      // Perdita giornaliera massima % (0 = off)
input double InpPerditaSett     = 6.0;      // Perdita settimanale massima % (0 = off)
input int    InpPerditeFila     = 3;        // Dopo N perdite di fila rischio ridotto (0 = off)
input double InpFattorePerdite  = 0.5;      // Fattore del rischio dopo N perdite
input bool   InpRegime          = true;     // Dimensionamento per regime (slot abilitati)
input double InpRegimeForte     = 0.093;    // Trend forte: pendenza EMA50 D1 / (20 x ATR14 D1) >=
input double InpRegimeDebole    = 0.027;    // Trend debole: pendenza <
input double InpMoltForte       = 1.25;     // Moltiplicatore rischio con trend forte
input double InpMoltDebole      = 0.75;     // Moltiplicatore rischio con trend debole
input bool   InpTrendLungo      = false;    // Solo a favore della EMA200 D1 (crescente/decrescente)
input double InpSpreadMax       = 1.00;     // Spread massimo per entrare ($ di prezzo)
input bool   InpPausaWeekend    = false;    // Nessun nuovo ingresso dal venerdì sera
input int    InpVenerdiOra      = 21;       // Venerdì sera da quest'ora (ora italiana)
input int    InpOreServerItalia = 1;        // Ora italiana = ora server - N
input int    InpBarre           = 3000;     // Candele ricalcolate per lo slot
input int    InpDeviazione      = 50;       // Deviazione massima (punti)
input bool   InpLogCSV          = true;     // File CSV dei trade
input bool   InpFileComuni      = true;     // File (CSV, stato, eventi, pausa) nella cartella comune (dashboard)
input int    InpStatoSec        = 30;       // Stato per la dashboard ogni N secondi (0 = mai)
input bool   InpPannello        = true;     // Pannello sul grafico

//--- slot 1
input group "=== Slot 1 ==="
input bool                  S1_Attivo   = true;          // Attivo
input string                S1_Nome     = "A_M15";       // Nome
input ENUM_TIMEFRAMES       S1_TF       = PERIOD_M15;    // Timeframe
input int                   S1_PivSx    = 7;             // Pivot: candele a sinistra
input int                   S1_PivDx    = 3;             // Pivot: candele a destra
input int                   S1_Eta      = 20;            // Età minima del trend (candele)
input ENUM_TIMEFRAMES       S1_HtfTF    = PERIOD_H1;     // TF della EMA filtro
input int                   S1_HtfLen   = 200;           // Periodo EMA filtro
input double                S1_Dist     = 0.0;           // Distanza minima dalla linea (x vol)
input double                S1_Zona     = 1.0;           // Altezza OB (x vol)
input double                S1_SL       = 6.0;           // Stop (x volatilità)
input double                S1_RR       = 3.0;           // Target R:R (0 = nessun target)
input double                S1_BeTrig   = 1.0;           // Pareggio: trigger in R (0 = off)
input double                S1_BeOff    = 0.1;           // Pareggio: offset in R
input double                S1_P1R      = 1.5;           // Parziale 1: livello in R (0 = off)
input double                S1_P1Pct    = 50.0;          // Parziale 1: % del volume iniziale
input double                S1_P2R      = 0.0;           // Parziale 2: livello in R (0 = off)
input double                S1_P2Pct    = 0.0;           // Parziale 2: % del volume iniziale
input bool                  S1_ParzBE   = true;          // Dopo il parziale stop a pareggio
input ENUM_VTOB_TRAIL       S1_Trail    = TRAIL_NESSUNO; // Trailing
input double                S1_TrailK   = 3.0;           // Trailing: K (x volatilità)
input ENUM_VTOB_TRAIL_START S1_TrailDa  = TRAIL_DOPO_BE; // Trailing: parte
input int                   S1_TimeStop = 0;             // Time stop in candele (0 = off)
input bool                  S1_Venerdi  = false;         // Chiudi il venerdì sera
input bool                  S1_Long     = true;          // Long
input bool                  S1_Short    = false;         // Short
input double                S1_Peso     = 1.0;           // Peso del rischio
input bool                  S1_Regime   = false;         // Usa il dimensionamento per regime
input long                  S1_Magic    = 7303001;       // Magic number
input string                S1_OreNo    = "";            // Ore italiane vietate per i segnali (es. "10-13")

//--- slot 2
input group "=== Slot 2 ==="
input bool                  S2_Attivo   = true;
input string                S2_Nome     = "B_H1";
input ENUM_TIMEFRAMES       S2_TF       = PERIOD_H1;
input int                   S2_PivSx    = 10;
input int                   S2_PivDx    = 3;
input int                   S2_Eta      = 10;
input ENUM_TIMEFRAMES       S2_HtfTF    = PERIOD_D1;
input int                   S2_HtfLen   = 200;
input double                S2_Dist     = 0.0;
input double                S2_Zona     = 1.0;
input double                S2_SL       = 3.0;
input double                S2_RR       = 4.0;
input double                S2_BeTrig   = 1.0;
input double                S2_BeOff    = 0.1;
input double                S2_P1R      = 1.0;
input double                S2_P1Pct    = 33.0;
input double                S2_P2R      = 2.0;
input double                S2_P2Pct    = 33.0;
input bool                  S2_ParzBE   = true;
input ENUM_VTOB_TRAIL       S2_Trail    = TRAIL_NESSUNO;
input double                S2_TrailK   = 3.0;
input ENUM_VTOB_TRAIL_START S2_TrailDa  = TRAIL_DOPO_BE;
input int                   S2_TimeStop = 0;
input bool                  S2_Venerdi  = false;
input bool                  S2_Long     = true;
input bool                  S2_Short    = true;
input double                S2_Peso     = 1.0;
input bool                  S2_Regime   = true;
input long                  S2_Magic    = 7306001;
input string                S2_OreNo    = "";

//--- slot 3
input group "=== Slot 3 ==="
input bool                  S3_Attivo   = true;
input string                S3_Nome     = "C_M30";
input ENUM_TIMEFRAMES       S3_TF       = PERIOD_M30;
input int                   S3_PivSx    = 5;
input int                   S3_PivDx    = 2;
input int                   S3_Eta      = 20;
input ENUM_TIMEFRAMES       S3_HtfTF    = PERIOD_H4;
input int                   S3_HtfLen   = 200;
input double                S3_Dist     = 0.0;
input double                S3_Zona     = 1.0;
input double                S3_SL       = 8.0;
input double                S3_RR       = 3.0;
input double                S3_BeTrig   = 1.0;
input double                S3_BeOff    = 0.1;
input double                S3_P1R      = 0.0;
input double                S3_P1Pct    = 0.0;
input double                S3_P2R      = 0.0;
input double                S3_P2Pct    = 0.0;
input bool                  S3_ParzBE   = false;
input ENUM_VTOB_TRAIL       S3_Trail    = TRAIL_NESSUNO;
input double                S3_TrailK   = 3.0;
input ENUM_VTOB_TRAIL_START S3_TrailDa  = TRAIL_DOPO_BE;
input int                   S3_TimeStop = 0;
input bool                  S3_Venerdi  = false;
input bool                  S3_Long     = true;
input bool                  S3_Short    = true;
input double                S3_Peso     = 1.0;
input bool                  S3_Regime   = true;
input long                  S3_Magic    = 7330001;
input string                S3_OreNo    = "";

//--- slot 4
input group "=== Slot 4 ==="
input bool                  S4_Attivo   = false;
input string                S4_Nome     = "D_M5";
input ENUM_TIMEFRAMES       S4_TF       = PERIOD_M5;
input int                   S4_PivSx    = 10;
input int                   S4_PivDx    = 5;
input int                   S4_Eta      = 20;
input ENUM_TIMEFRAMES       S4_HtfTF    = PERIOD_H1;
input int                   S4_HtfLen   = 200;
input double                S4_Dist     = 0.0;
input double                S4_Zona     = 1.0;
input double                S4_SL       = 6.0;
input double                S4_RR       = 4.0;
input double                S4_BeTrig   = 1.0;
input double                S4_BeOff    = 0.1;
input double                S4_P1R      = 0.0;
input double                S4_P1Pct    = 0.0;
input double                S4_P2R      = 0.0;
input double                S4_P2Pct    = 0.0;
input bool                  S4_ParzBE   = false;
input ENUM_VTOB_TRAIL       S4_Trail    = TRAIL_NESSUNO;
input double                S4_TrailK   = 3.0;
input ENUM_VTOB_TRAIL_START S4_TrailDa  = TRAIL_DOPO_BE;
input int                   S4_TimeStop = 0;
input bool                  S4_Venerdi  = false;
input bool                  S4_Long     = true;
input bool                  S4_Short    = false;
input double                S4_Peso     = 1.0;
input bool                  S4_Regime   = false;
input long                  S4_Magic    = 7305001;
input string                S4_OreNo    = "";

//--- slot 5
input group "=== Slot 5 ==="
input bool                  S5_Attivo   = false;
input string                S5_Nome     = "E";
input ENUM_TIMEFRAMES       S5_TF       = PERIOD_H4;
input int                   S5_PivSx    = 5;
input int                   S5_PivDx    = 2;
input int                   S5_Eta      = 20;
input ENUM_TIMEFRAMES       S5_HtfTF    = PERIOD_D1;
input int                   S5_HtfLen   = 200;
input double                S5_Dist     = 0.0;
input double                S5_Zona     = 1.0;
input double                S5_SL       = 6.0;
input double                S5_RR       = 3.0;
input double                S5_BeTrig   = 1.0;
input double                S5_BeOff    = 0.1;
input double                S5_P1R      = 0.0;
input double                S5_P1Pct    = 0.0;
input double                S5_P2R      = 0.0;
input double                S5_P2Pct    = 0.0;
input bool                  S5_ParzBE   = false;
input ENUM_VTOB_TRAIL       S5_Trail    = TRAIL_NESSUNO;
input double                S5_TrailK   = 3.0;
input ENUM_VTOB_TRAIL_START S5_TrailDa  = TRAIL_DOPO_BE;
input int                   S5_TimeStop = 0;
input bool                  S5_Venerdi  = false;
input bool                  S5_Long     = true;
input bool                  S5_Short    = false;
input double                S5_Peso     = 1.0;
input bool                  S5_Regime   = false;
input long                  S5_Magic    = 7340001;
input string                S5_OreNo    = "";

//--- indicatore (comune a tutti gli slot, come nel Pine)
input group "=== Indicatore (comune) ==="
input int    InpVolLen  = 50;   // Volatilità: SMA del range (candele)
input double InpStMult  = 3.5;  // Supertrend: moltiplicatore

#define NSLOT 5
#define F_BE   1                 // flag della posizione: pareggio fatto
#define F_P1   2                 // parziale 1 fatto
#define F_P2   4                 // parziale 2 fatto
#define F_TR   8                 // trailing partito
#define F_BEP  16                // pareggio da applicare (dopo il parziale)

struct SlotCfg
  {
   bool              on;
   string            nome;
   ENUM_TIMEFRAMES   tf;
   int               pl, pr, eta;
   ENUM_TIMEFRAMES   htf;
   int               htfLen;
   double            dist, zona, sl, rr, beT, beO, p1R, p1P, p2R, p2P;
   bool              parzBE;
   int               trail;
   double            trK;
   int               trDa;
   int               timeStop;
   bool              venerdi, lng, sht;
   double            peso;
   bool              regime;
   long              magic;
   bool              oreNo[24];
   //--- stato
   int               hEma;
   datetime          lastBar;
   int               sig;        // +1 / -1 / 0 sull'ultima candela chiusa
   long              obId;       // id dell'OB del segnale (orario del pivot)
   double            vol;        // volatilità dell'ultima candela chiusa
   double            tstop;      // linea trend stop
   int               trend;      // trend Supertrend
   double            swLo, swHi; // ultimo minimo / massimo di pivot confermato
   string            stato;      // per il pannello
  };

SlotCfg  G[NSLOT];
CTrade   trade;
int      hEma50D1 = INVALID_HANDLE, hAtrD1 = INVALID_HANDLE, hEma200D1 = INVALID_HANDLE;
string   g_csv = "";
int      g_flagFile = 0;          // FILE_COMMON se i file vanno nella cartella comune
string   g_stato = "", g_eventi = "";

//+------------------------------------------------------------------+
//| Dashboard: pausa (file <Id>.paused), eventi, testo JSON           |
//+------------------------------------------------------------------+
bool InPausa() { return(FileIsExist(InpId + ".paused", g_flagFile)); }

void Log(const string s)
  {
   Print(s);
   if(g_eventi == "")
      return;
   int h = FileOpen(g_eventi, FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_SHARE_READ | g_flagFile);
   if(h == INVALID_HANDLE)
      return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, TimeToString(TimeCurrent(), TIME_DATE | TIME_SECONDS) + ";" + _Symbol + ";" + s + "\r\n");
   FileClose(h);
  }

string Js(const string s)
  {
   string t = s;
   StringReplace(t, "\\", "/");
   StringReplace(t, "\"", "'");
   return("\"" + t + "\"");
  }

//+------------------------------------------------------------------+
//| Utilità: GlobalVariable con prefisso                             |
//+------------------------------------------------------------------+
string GvNome(const string s) { return(InpId + "_" + s); }
double GvGet(const string s, const double def)
  {
   string n = GvNome(s);
   if(!GlobalVariableCheck(n))
      return(def);
   return(GlobalVariableGet(n));
  }
void GvSet(const string s, const double v) { GlobalVariableSet(GvNome(s), v); }
void GvDel(const string s) { GlobalVariableDel(GvNome(s)); }
string GvPos(const ulong ticket, const string campo) { return("pos" + IntegerToString((long)ticket) + "_" + campo); }

//+------------------------------------------------------------------+
//| Ore vietate: "10-13" o "10-13,22-23" (fine esclusa)              |
//+------------------------------------------------------------------+
void LeggiOre(const string s, bool &ore[])
  {
   for(int h = 0; h < 24; h++)
      ore[h] = false;
   string parti[];
   int n = StringSplit(s, ',', parti);
   for(int k = 0; k < n; k++)
     {
      string p = parti[k];
      StringTrimLeft(p);
      StringTrimRight(p);
      if(StringLen(p) == 0)
         continue;
      string ab[];
      if(StringSplit(p, '-', ab) == 2)
        {
         int a = (int)StringToInteger(ab[0]), b = (int)StringToInteger(ab[1]);
         for(int h = a; h < b && h < 24; h++)
            if(h >= 0)
               ore[h] = true;
        }
      else
        {
         int h1 = (int)StringToInteger(p);
         if(h1 >= 0 && h1 < 24)
            ore[h1] = true;
        }
     }
  }

void Carica(const int k, const bool on, const string nome, const ENUM_TIMEFRAMES tf, const int pl, const int pr,
            const int eta, const ENUM_TIMEFRAMES htf, const int htfLen, const double dist, const double zona,
            const double sl, const double rr, const double beT, const double beO, const double p1R, const double p1P,
            const double p2R, const double p2P, const bool parzBE, const ENUM_VTOB_TRAIL trail, const double trK,
            const ENUM_VTOB_TRAIL_START trDa, const int timeStop, const bool venerdi, const bool lng, const bool sht,
            const double peso, const bool regime, const long magic, const string oreNo)
  {
   G[k].on = on; G[k].nome = nome; G[k].tf = tf; G[k].pl = pl; G[k].pr = pr; G[k].eta = eta;
   G[k].htf = htf; G[k].htfLen = htfLen; G[k].dist = dist; G[k].zona = zona; G[k].sl = sl; G[k].rr = rr;
   G[k].beT = beT; G[k].beO = beO; G[k].p1R = p1R; G[k].p1P = p1P; G[k].p2R = p2R; G[k].p2P = p2P;
   G[k].parzBE = parzBE; G[k].trail = (int)trail; G[k].trK = trK; G[k].trDa = (int)trDa; G[k].timeStop = timeStop;
   G[k].venerdi = venerdi; G[k].lng = lng; G[k].sht = sht; G[k].peso = peso; G[k].regime = regime;
   G[k].magic = magic;
   LeggiOre(oreNo, G[k].oreNo);
   G[k].hEma = INVALID_HANDLE; G[k].lastBar = 0; G[k].sig = 0; G[k].obId = 0; G[k].vol = 0.0;
   G[k].tstop = 0.0; G[k].trend = 0; G[k].swLo = 0.0; G[k].swHi = 0.0; G[k].stato = on ? "in attesa" : "spento";
  }

//+------------------------------------------------------------------+
int OnInit()
  {
   Carica(0, S1_Attivo, S1_Nome, S1_TF, S1_PivSx, S1_PivDx, S1_Eta, S1_HtfTF, S1_HtfLen, S1_Dist, S1_Zona, S1_SL, S1_RR,
          S1_BeTrig, S1_BeOff, S1_P1R, S1_P1Pct, S1_P2R, S1_P2Pct, S1_ParzBE, S1_Trail, S1_TrailK, S1_TrailDa,
          S1_TimeStop, S1_Venerdi, S1_Long, S1_Short, S1_Peso, S1_Regime, S1_Magic, S1_OreNo);
   Carica(1, S2_Attivo, S2_Nome, S2_TF, S2_PivSx, S2_PivDx, S2_Eta, S2_HtfTF, S2_HtfLen, S2_Dist, S2_Zona, S2_SL, S2_RR,
          S2_BeTrig, S2_BeOff, S2_P1R, S2_P1Pct, S2_P2R, S2_P2Pct, S2_ParzBE, S2_Trail, S2_TrailK, S2_TrailDa,
          S2_TimeStop, S2_Venerdi, S2_Long, S2_Short, S2_Peso, S2_Regime, S2_Magic, S2_OreNo);
   Carica(2, S3_Attivo, S3_Nome, S3_TF, S3_PivSx, S3_PivDx, S3_Eta, S3_HtfTF, S3_HtfLen, S3_Dist, S3_Zona, S3_SL, S3_RR,
          S3_BeTrig, S3_BeOff, S3_P1R, S3_P1Pct, S3_P2R, S3_P2Pct, S3_ParzBE, S3_Trail, S3_TrailK, S3_TrailDa,
          S3_TimeStop, S3_Venerdi, S3_Long, S3_Short, S3_Peso, S3_Regime, S3_Magic, S3_OreNo);
   Carica(3, S4_Attivo, S4_Nome, S4_TF, S4_PivSx, S4_PivDx, S4_Eta, S4_HtfTF, S4_HtfLen, S4_Dist, S4_Zona, S4_SL, S4_RR,
          S4_BeTrig, S4_BeOff, S4_P1R, S4_P1Pct, S4_P2R, S4_P2Pct, S4_ParzBE, S4_Trail, S4_TrailK, S4_TrailDa,
          S4_TimeStop, S4_Venerdi, S4_Long, S4_Short, S4_Peso, S4_Regime, S4_Magic, S4_OreNo);
   Carica(4, S5_Attivo, S5_Nome, S5_TF, S5_PivSx, S5_PivDx, S5_Eta, S5_HtfTF, S5_HtfLen, S5_Dist, S5_Zona, S5_SL, S5_RR,
          S5_BeTrig, S5_BeOff, S5_P1R, S5_P1Pct, S5_P2R, S5_P2Pct, S5_ParzBE, S5_Trail, S5_TrailK, S5_TrailDa,
          S5_TimeStop, S5_Venerdi, S5_Long, S5_Short, S5_Peso, S5_Regime, S5_Magic, S5_OreNo);
   for(int k = 0; k < NSLOT; k++)
     {
      if(!G[k].on)
         continue;
      if(PeriodSeconds(G[k].htf) <= PeriodSeconds(G[k].tf))
         PrintFormat("ATTENZIONE slot %s: il TF della EMA (%s) non è superiore al TF dello slot (%s)",
                     G[k].nome, EnumToString(G[k].htf), EnumToString(G[k].tf));
      G[k].hEma = iMA(_Symbol, G[k].htf, G[k].htfLen, 0, MODE_EMA, PRICE_CLOSE);
      if(G[k].hEma == INVALID_HANDLE)
        {
         PrintFormat("Slot %s: errore nella creazione della EMA %s", G[k].nome, EnumToString(G[k].htf));
         return(INIT_FAILED);
        }
      for(int j = 0; j < k; j++)
         if(G[j].on && G[j].magic == G[k].magic)
           {
            PrintFormat("Slot %s e %s hanno lo stesso magic number: usane due diversi", G[j].nome, G[k].nome);
            return(INIT_PARAMETERS_INCORRECT);
           }
     }
   hEma50D1 = iMA(_Symbol, PERIOD_D1, 50, 0, MODE_EMA, PRICE_CLOSE);
   hAtrD1 = iATR(_Symbol, PERIOD_D1, 14);
   hEma200D1 = iMA(_Symbol, PERIOD_D1, 200, 0, MODE_EMA, PRICE_CLOSE);
   if(hEma50D1 == INVALID_HANDLE || hAtrD1 == INVALID_HANDLE || hEma200D1 == INVALID_HANDLE)
     {
      Print("Errore nella creazione degli indicatori D1 del regime");
      return(INIT_FAILED);
     }
   trade.SetDeviationInPoints(InpDeviazione);
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.LogLevel(LOG_LEVEL_ERRORS);
   g_flagFile = InpFileComuni ? FILE_COMMON : 0;
   if(InpLogCSV)
      g_csv = InpId + "_" + _Symbol + "_trade.csv";
   g_stato = InpId + "_" + _Symbol + "_stato.json";
   g_eventi = InpId + "_" + _Symbol + "_eventi.log";
   RipristinaPosizioni();
   Log(StringFormat("VTOB Portfolio avviato su %s: rischio base %.2f%%, tetto %.1fx, perdita max giorno %.1f%% / settimana %.1f%%%s",
                    _Symbol, InpRischioBase, InpTettoRischio, InpPerditaGiorno, InpPerditaSett,
                    InPausa() ? " (IN PAUSA dalla dashboard: nessun nuovo ingresso)" : ""));
   if(InpStatoSec > 0)
      EventSetTimer(InpStatoSec);
   ScriviStato(true);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   if(g_stato != "")
      ScriviStato(false);
   for(int k = 0; k < NSLOT; k++)
      if(G[k].hEma != INVALID_HANDLE)
         IndicatorRelease(G[k].hEma);
   if(hEma50D1 != INVALID_HANDLE)
      IndicatorRelease(hEma50D1);
   if(hAtrD1 != INVALID_HANDLE)
      IndicatorRelease(hAtrD1);
   if(hEma200D1 != INVALID_HANDLE)
      IndicatorRelease(hEma200D1);
   Comment("");
  }

//+------------------------------------------------------------------+
//| Posizione dello slot (una sola per slot)                         |
//+------------------------------------------------------------------+
bool PosizioneSlot(const int k, ulong &ticket)
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == G[k].magic)
        {
         ticket = t;
         return(true);
        }
     }
   return(false);
  }

int SlotDaMagic(const long magic)
  {
   for(int k = 0; k < NSLOT; k++)
      if(G[k].on && G[k].magic == magic)
         return(k);
   return(-1);
  }

//+------------------------------------------------------------------+
//| Ora italiana e calendario                                        |
//+------------------------------------------------------------------+
datetime OraItalia(const datetime t) { return(t - InpOreServerItalia * 3600); }
bool VenerdiSera(const datetime aperturaCandela, const ENUM_TIMEFRAMES tf)
  {
   MqlDateTime d;
   TimeToStruct(OraItalia(aperturaCandela), d);
   if(d.day_of_week == 5 && d.hour >= InpVenerdiOra)
      return(true);
   // penultima candela prima della chiusura del venerdì (serve per H4 / D1)
   MqlDateTime e;
   TimeToStruct(OraItalia(aperturaCandela + 2 * PeriodSeconds(tf)), e);
   return(e.day_of_week == 6 || (e.day_of_week == 5 && e.hour >= 23));
  }

//+------------------------------------------------------------------+
//| Regime D1 dell'ultima candela D1 chiusa                          |
//+------------------------------------------------------------------+
bool PendenzaD1(double &pend)
  {
   double e[], a[];
   ArraySetAsSeries(e, true);
   ArraySetAsSeries(a, true);
   if(CopyBuffer(hEma50D1, 0, 1, 21, e) < 21 || CopyBuffer(hAtrD1, 0, 1, 1, a) < 1 || a[0] <= 0)
      return(false);
   pend = (e[0] - e[20]) / (20.0 * a[0]);
   return(true);
  }

bool TrendLungoOk(const int dir)
  {
   double e[], c[];
   ArraySetAsSeries(e, true);
   ArraySetAsSeries(c, true);
   if(CopyBuffer(hEma200D1, 0, 1, 21, e) < 21 || CopyClose(_Symbol, PERIOD_D1, 1, 1, c) < 1)
      return(false);
   if(dir == 1)
      return(c[0] > e[0] && e[0] > e[20]);
   return(c[0] < e[0] && e[0] < e[20]);
  }

//+------------------------------------------------------------------+
//| Indicatore sulle ultime candele chiuse del TF dello slot.        |
//| Imposta sig/obId/vol/tstop/trend/swLo/swHi dell'ultima candela.  |
//+------------------------------------------------------------------+
bool Valuta(const int k)
  {
   SlotCfg s = G[k];
   G[k].sig = 0;
   G[k].obId = 0;
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int n = CopyRates(_Symbol, s.tf, 1, InpBarre, r);     // r[n-1] = ultima candela chiusa
   if(n < InpVolLen + s.pl + s.pr + 50)
     {
      G[k].stato = "storico insufficiente (" + IntegerToString(n) + ")";
      return(false);
     }
   // EMA del TF superiore: per la candela i vale la EMA della candela HTF PRECEDENTE a quella che la contiene
   int nh = (int)((double)n * PeriodSeconds(s.tf) / PeriodSeconds(s.htf)) + 10;
   double eh[];
   datetime th[];
   ArraySetAsSeries(eh, false);
   ArraySetAsSeries(th, false);
   int ce = CopyBuffer(s.hEma, 0, 0, nh, eh);
   int ct = CopyTime(_Symbol, s.htf, 0, nh, th);
   if(ce <= 1 || ct != ce)
     {
      G[k].stato = "EMA " + EnumToString(s.htf) + " non pronta";
      return(false);
     }
   double v[], ub[], lb[], ts[];
   int tr[], age[];
   ArrayResize(v, n); ArrayResize(ub, n); ArrayResize(lb, n); ArrayResize(ts, n);
   ArrayResize(tr, n); ArrayResize(age, n);
   double sumR = 0.0;
   double aTop = 0.0, aBot = 0.0, prevTop = 0.0, prevBot = 0.0;
   bool   aOk = false, prevOk = false;
   int    aDir = 0;
   long   aId = 0;
   double swLo = 0.0, swHi = 0.0;
   int    jh = 0;
   for(int i = 0; i < n; i++)
     {
      // volatilità = SMA(high - low)
      sumR += r[i].high - r[i].low;
      if(i >= InpVolLen)
         sumR -= r[i - InpVolLen].high - r[i - InpVolLen].low;
      bool vok = (i >= InpVolLen - 1);
      v[i] = vok ? sumR / InpVolLen : 0.0;
      // Supertrend custom (nz(banda[1]) = 0 come nel Pine)
      double src = (r[i].high + r[i].low) / 2.0;
      double pLB = (i > 0) ? lb[i - 1] : 0.0;
      double pUB = (i > 0) ? ub[i - 1] : 0.0;
      if(vok)
        {
         double x = src - InpStMult * v[i];
         lb[i] = (x > pLB || (i > 0 && r[i - 1].close < pLB)) ? x : pLB;
         x = src + InpStMult * v[i];
         ub[i] = (x < pUB || (i > 0 && r[i - 1].close > pUB)) ? x : pUB;
        }
      else
        {
         lb[i] = pLB;
         ub[i] = pUB;
        }
      bool prevVolOk = (i > 0 && i - 1 >= InpVolLen - 1);
      if(i == 0 || !prevVolOk)
         tr[i] = 1;
      else
         if(ts[i - 1] == pUB)
            tr[i] = (r[i].close > ub[i]) ? 1 : -1;
         else
            tr[i] = (r[i].close < lb[i]) ? -1 : 1;
      ts[i] = (tr[i] == 1) ? lb[i] : ub[i];
      bool chg = (i > 0 && tr[i] != tr[i - 1]);
      age[i] = (i == 0) ? 100000 : (chg ? 0 : age[i - 1] + 1);
      // pivot confermati sulla candela i (pivot sulla candela p = i - pr)
      bool pl = false, ph = false;
      if(i >= s.pl + s.pr)
        {
         int p = i - s.pr;
         pl = true;
         ph = true;
         for(int q = p - s.pl; q < p; q++)
           {
            if(r[q].low <= r[p].low)
               pl = false;
            if(r[q].high >= r[p].high)
               ph = false;
           }
         for(int q = p + 1; q <= i; q++)
           {
            if(r[q].low < r[p].low)
               pl = false;
            if(r[q].high > r[p].high)
               ph = false;
           }
         if(pl)
            swLo = r[p].low;
         if(ph)
            swHi = r[p].high;
        }
      // EMA dell'ultima candela HTF chiusa
      while(jh + 1 < ct && th[jh + 1] <= r[i].time)
         jh++;
      bool eok = (th[jh] <= r[i].time && jh >= 1);
      double e = eok ? eh[jh - 1] : 0.0;
      if(vok)
        {
         int p = i - s.pr;
         if(tr[i] == 1 && pl)
           {
            double t = MathMin(r[p].open, r[p].close), bt = t - s.zona * v[i];
            bool ov = aOk && !(bt > aTop || t < aBot);
            if(!ov && age[i] >= s.eta && bt - ts[i] >= s.dist * v[i] && eok && r[i].close > e)
              {
               aTop = t; aBot = bt; aDir = 1; aId = (long)r[p].time; aOk = true;
              }
           }
         if(tr[i] == -1 && ph)
           {
            double bt = MathMax(r[p].open, r[p].close), t = bt + s.zona * v[i];
            bool ov = aOk && !(bt > aTop || t < aBot);
            if(!ov && age[i] >= s.eta && ts[i] - t >= s.dist * v[i] && eok && r[i].close < e)
              {
               aTop = t; aBot = bt; aDir = -1; aId = (long)r[p].time; aOk = true;
              }
           }
        }
      // rottura dell'OB
      if(aOk && ((aDir == 1 && r[i].high < aBot) || (aDir == -1 && r[i].low > aTop)))
        {
         aOk = false;
         aDir = 0;
        }
      // segnale sull'ultima candela chiusa (crossover come ta.crossover)
      if(i == n - 1 && i > 0 && aOk && prevOk && !chg)
        {
         if(aDir == 1 && !pl && r[i].low > aTop && r[i - 1].low <= prevTop)
            G[k].sig = 1;
         if(aDir == -1 && !ph && r[i].high < aBot && r[i - 1].high >= prevBot)
            G[k].sig = -1;
         G[k].obId = aId;
        }
      prevTop = aTop;
      prevBot = aBot;
      prevOk = aOk;
     }
   G[k].vol = v[n - 1];
   G[k].tstop = ts[n - 1];
   G[k].trend = tr[n - 1];
   G[k].swLo = swLo;
   G[k].swHi = swHi;
   return(true);
  }

//+------------------------------------------------------------------+
//| Rischio in denaro di una distanza di prezzo per 1 lotto          |
//+------------------------------------------------------------------+
double PerditaPerLotto(const double dist)
  {
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);
   if(tickVal <= 0)
      tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tickSize <= 0)
      return(0.0);
   return(dist / tickSize * tickVal);
  }

//+------------------------------------------------------------------+
//| Rischio aperto di tutte le posizioni del portafoglio (% balance) |
//| Le posizioni con lo stop a pareggio o oltre contano 0.           |
//+------------------------------------------------------------------+
double RischioAperto()
  {
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   if(bal <= 0)
      return(0.0);
   double tot = 0.0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0 || PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(SlotDaMagic(PositionGetInteger(POSITION_MAGIC)) < 0)
         continue;
      double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
      double vol = PositionGetDouble(POSITION_VOLUME);
      double dist = 0.0;
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
         dist = (sl > 0) ? op - sl : 0.0;
      else
         dist = (sl > 0) ? sl - op : 0.0;
      if(dist > 0)
         tot += PerditaPerLotto(dist) * vol;
     }
   return(tot / bal * 100.0);
  }

//+------------------------------------------------------------------+
//| Perdita del giorno / della settimana (equity vs saldo iniziale)  |
//+------------------------------------------------------------------+
string ChiaveGiorno(const datetime t)
  {
   MqlDateTime d;
   TimeToStruct(t, d);
   return(StringFormat("%04d%02d%02d", d.year, d.mon, d.day));
  }

void AggiornaInizioPeriodo()
  {
   datetime now = TimeCurrent();
   string g = "g_" + ChiaveGiorno(now);
   if(!GlobalVariableCheck(GvNome(g)))
      GvSet(g, AccountInfoDouble(ACCOUNT_BALANCE));
   MqlDateTime d;
   TimeToStruct(now, d);
   int giorniDaLun = (d.day_of_week + 6) % 7;
   string w = "s_" + ChiaveGiorno(now - giorniDaLun * 86400);
   if(!GlobalVariableCheck(GvNome(w)))
      GvSet(w, AccountInfoDouble(ACCOUNT_BALANCE));
  }

bool LimitiPerditaOk(string &motivo)
  {
   datetime now = TimeCurrent();
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double g0 = GvGet("g_" + ChiaveGiorno(now), 0.0);
   if(InpPerditaGiorno > 0 && g0 > 0 && (eq - g0) / g0 * 100.0 <= -InpPerditaGiorno)
     {
      motivo = "perdita giornaliera massima raggiunta";
      return(false);
     }
   MqlDateTime d;
   TimeToStruct(now, d);
   double s0 = GvGet("s_" + ChiaveGiorno(now - ((d.day_of_week + 6) % 7) * 86400), 0.0);
   if(InpPerditaSett > 0 && s0 > 0 && (eq - s0) / s0 * 100.0 <= -InpPerditaSett)
     {
      motivo = "perdita settimanale massima raggiunta";
      return(false);
     }
   return(true);
  }

//+------------------------------------------------------------------+
//| Invio ordini con gestione degli errori (solo tentativi immediati)|
//+------------------------------------------------------------------+
bool Ritentabile(const uint rc)
  {
   return(rc == TRADE_RETCODE_REQUOTE || rc == TRADE_RETCODE_PRICE_CHANGED || rc == TRADE_RETCODE_PRICE_OFF ||
          rc == TRADE_RETCODE_TIMEOUT || rc == TRADE_RETCODE_CONNECTION);
  }

bool Apri(const int k, const int dir, const double lotti, const double sl, const double tp)
  {
   string com = InpId + "_" + G[k].nome;
   trade.SetExpertMagicNumber(G[k].magic);
   for(int tent = 0; tent < 3; tent++)
     {
      bool ok = (dir == 1) ? trade.Buy(lotti, _Symbol, 0.0, sl, tp, com) : trade.Sell(lotti, _Symbol, 0.0, sl, tp, com);
      uint rc = trade.ResultRetcode();
      if(ok && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_PLACED))
         return(true);
      PrintFormat("Slot %s: ordine fallito (%u %s)%s", G[k].nome, rc, trade.ResultRetcodeDescription(),
                  Ritentabile(rc) ? ", nuovo tentativo" : "");
      if(!Ritentabile(rc))
         return(false);
      Sleep(200);
     }
   return(false);
  }

bool Chiudi(const ulong ticket, const string motivo)
  {
   for(int tent = 0; tent < 3; tent++)
     {
      if(trade.PositionClose(ticket))
        {
         uint rc = trade.ResultRetcode();
         if(rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_PLACED)
           {
            PrintFormat("Posizione %I64u chiusa: %s", ticket, motivo);
            return(true);
           }
        }
      uint rc2 = trade.ResultRetcode();
      PrintFormat("Chiusura %I64u fallita (%u %s)", ticket, rc2, trade.ResultRetcodeDescription());
      if(!Ritentabile(rc2))
         return(false);
      Sleep(200);
     }
   return(false);
  }

//+------------------------------------------------------------------+
//| Sposta lo stop (nuovo livello migliore). Se il prezzo è già oltre|
//| il nuovo stop, chiude a mercato.                                  |
//+------------------------------------------------------------------+
void SpostaStop(const ulong ticket, const double nuovoSL, const string motivo)
  {
   if(!PositionSelectByTicket(ticket))
      return;
   bool buy = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
   double sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
   double nsl = NormalizeDouble(nuovoSL, _Digits);
   if(sl > 0 && ((buy && nsl <= sl) || (!buy && nsl >= sl)))
      return;                                                   // non migliora
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double lvl = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   if((buy && bid <= nsl + lvl) || (!buy && ask >= nsl - lvl))
     {
      Chiudi(ticket, motivo + ": prezzo già oltre il nuovo stop, chiusura a mercato");
      return;
     }
   if(trade.PositionModify(ticket, nsl, tp))
      PrintFormat("Posizione %I64u: %s, stop %s", ticket, motivo, DoubleToString(nsl, _Digits));
   else
      PrintFormat("Posizione %I64u: modifica stop fallita (%u %s)", ticket, trade.ResultRetcode(),
                  trade.ResultRetcodeDescription());
  }

//+------------------------------------------------------------------+
//| Parziali: controllati a ogni tick (livello toccato dal prezzo)   |
//+------------------------------------------------------------------+
void GestisciParziali(const int k)
  {
   if(G[k].p1R <= 0 && G[k].p2R <= 0)
      return;
   ulong tk;
   if(!PosizioneSlot(k, tk) || !PositionSelectByTicket(tk))
      return;
   double B = GvGet(GvPos(tk, "B"), 0.0), D = GvGet(GvPos(tk, "D"), 0.0), V0 = GvGet(GvPos(tk, "V0"), 0.0);
   int fl = (int)GvGet(GvPos(tk, "F"), 0.0);
   if(B <= 0 || D <= 0 || V0 <= 0)
      return;
   int dir = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? 1 : -1;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   for(int q = 0; q < 2; q++)
     {
      double lr = (q == 0) ? G[k].p1R : G[k].p2R, pc = (q == 0) ? G[k].p1P : G[k].p2P;
      int bit = (q == 0) ? F_P1 : F_P2;
      if(lr <= 0 || pc <= 0 || (fl & bit) != 0)
         continue;
      double lv = B + dir * lr * D;                             // livello in prezzo BID, come nel backtest
      if((dir == 1 && bid < lv) || (dir == -1 && bid > lv))
         continue;
      double volNow = PositionGetDouble(POSITION_VOLUME);
      double vchiudi = MathFloor(V0 * pc / 100.0 / step) * step;
      if(vchiudi < vmin)
        {
         fl |= bit;
         PrintFormat("Slot %s: parziale %d troppo piccolo per il lotto minimo, saltato", G[k].nome, q + 1);
         continue;
        }
      if(volNow - vchiudi < vmin - 1e-9)
         vchiudi = volNow;                                      // resto sotto il minimo: chiude tutto
      if(trade.PositionClosePartial(tk, vchiudi))
        {
         fl |= bit;
         if(G[k].parzBE)
            fl |= F_BEP;                                        // pareggio alla prossima chiusura di candela
         if(G[k].trDa == TRAIL_DOPO_PARZ)
            fl |= F_TR;
         PrintFormat("Slot %s: parziale %d chiuso (%.2f lotti a %.2fR)", G[k].nome, q + 1, vchiudi, lr);
        }
      else
         PrintFormat("Slot %s: parziale fallito (%u %s)", G[k].nome, trade.ResultRetcode(), trade.ResultRetcodeDescription());
      GvSet(GvPos(tk, "F"), (double)fl);
      if(!PositionSelectByTicket(tk))
         return;
     }
  }

//+------------------------------------------------------------------+
//| Gestione alla chiusura di una candela del TF dello slot:          |
//| pareggio, trailing, time stop, chiusura del venerdì.              |
//+------------------------------------------------------------------+
void GestisciPosizione(const int k, const datetime aperturaChiusa)
  {
   ulong tk;
   if(!PosizioneSlot(k, tk) || !PositionSelectByTicket(tk))
      return;
   double B = GvGet(GvPos(tk, "B"), 0.0), D = GvGet(GvPos(tk, "D"), 0.0);
   datetime tIn = (datetime)GvGet(GvPos(tk, "T"), 0.0);
   int fl = (int)GvGet(GvPos(tk, "F"), 0.0);
   if(B <= 0 || D <= 0 || tIn == 0)
      return;
   int dir = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? 1 : -1;
   double spread = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double adj = (dir == -1) ? spread : 0.0;                     // short: stop sul prezzo ASK = livello BID + spread
   int barre = iBarShift(_Symbol, G[k].tf, tIn, false);         // candele dall'ingresso (la candela d'ingresso è chiusa)
   // uscite decise alla chiusura: time stop e venerdì sera -> a mercato ora (apertura della candela dopo)
   if(G[k].timeStop > 0 && barre >= G[k].timeStop + 1)
     {
      Chiudi(tk, "time stop");
      return;
     }
   if(G[k].venerdi && VenerdiSera(aperturaChiusa, G[k].tf))
     {
      Chiudi(tk, "chiusura del venerdì sera");
      return;
     }
   // pareggio: massimo (minimo) delle candele chiuse dall'ingresso
   if(barre >= 1)
     {
      double estremo = 0.0;
      if(dir == 1)
        {
         int ih = iHighest(_Symbol, G[k].tf, MODE_HIGH, barre, 1);
         estremo = (ih >= 0) ? iHigh(_Symbol, G[k].tf, ih) : 0.0;
        }
      else
        {
         int il = iLowest(_Symbol, G[k].tf, MODE_LOW, barre, 1);
         estremo = (il >= 0) ? iLow(_Symbol, G[k].tf, il) : 0.0;
        }
      bool armaBE = (G[k].beT > 0 && estremo > 0 && (estremo - B) * dir >= G[k].beT * D);
      if(((fl & F_BE) == 0 && armaBE) || (fl & F_BEP) != 0)
        {
         fl |= F_BE;
         fl &= ~F_BEP;
         if(G[k].trDa == TRAIL_DOPO_BE)
            fl |= F_TR;
         GvSet(GvPos(tk, "F"), (double)fl);
         SpostaStop(tk, B + dir * G[k].beO * D + adj, "pareggio");
         if(!PositionSelectByTicket(tk))
            return;
        }
      // trailing (calcolato sulla candela appena chiusa)
      if(G[k].trDa == TRAIL_SUBITO)
         fl |= F_TR;
      if(G[k].trail != TRAIL_NESSUNO && (fl & F_TR) != 0)
        {
         double cand = 0.0;
         if(G[k].trail == TRAIL_ATR)
            cand = iClose(_Symbol, G[k].tf, 1) - dir * G[k].trK * G[k].vol;
         else
            if(G[k].trail == TRAIL_CHANDELIER)
               cand = estremo - dir * G[k].trK * G[k].vol;
            else
               if(G[k].trail == TRAIL_SUPERTREND)
                  cand = (G[k].trend == dir) ? G[k].tstop : 0.0;
               else
                  if(G[k].trail == TRAIL_SWING)
                    {
                     double sw = (dir == 1) ? G[k].swLo : G[k].swHi;
                     cand = (sw > 0) ? sw - dir * G[k].trK * G[k].vol : 0.0;
                    }
         if(cand > 0)
            SpostaStop(tk, cand + adj, "trailing");
        }
      GvSet(GvPos(tk, "F"), (double)fl);
     }
  }

//+------------------------------------------------------------------+
//| Nuovo segnale -> controlli di portafoglio -> ordine              |
//+------------------------------------------------------------------+
void ProvaIngresso(const int k, const datetime aperturaChiusa)
  {
   int sig = G[k].sig;
   if(sig == 0)
      return;
   string nome = G[k].nome;
   if((sig == 1 && !G[k].lng) || (sig == -1 && !G[k].sht))
      return;
   if(InPausa())
     {
      Log(StringFormat("Slot %s: segnale %s ignorato, EA in pausa dalla dashboard", nome, sig == 1 ? "BUY" : "SELL"));
      return;
     }
   MqlDateTime dt;
   TimeToStruct(OraItalia(aperturaChiusa), dt);
   if(G[k].oreNo[dt.hour])
     {
      Log(StringFormat("Slot %s: segnale ignorato, ora vietata (%02d:00 italiana)", nome, dt.hour));
      return;
     }
   string glob = "ob_" + IntegerToString(G[k].magic);
   if((double)G[k].obId == GvGet(glob, -1.0))
     {
      Log(StringFormat("Slot %s: segnale ignorato, OB già tradato", nome));
      return;
     }
   if(InpPausaWeekend && VenerdiSera(aperturaChiusa, G[k].tf))
     {
      Log(StringFormat("Slot %s: segnale ignorato, pausa del fine settimana", nome));
      return;
     }
   if(InpTrendLungo && !TrendLungoOk(sig))
     {
      Log(StringFormat("Slot %s: segnale ignorato, contro il trend lungo D1", nome));
      return;
     }
   string motivo = "";
   if(!LimitiPerditaOk(motivo))
     {
      Log(StringFormat("Slot %s: segnale ignorato, %s", nome, motivo));
      return;
     }
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double spread = ask - bid;
   if(spread > InpSpreadMax)
     {
      Log(StringFormat("Slot %s: segnale ignorato, spread %.2f > %.2f", nome, spread, InpSpreadMax));
      return;
     }
   // dimensione: rischio base x peso x regime x riduzione dopo N perdite
   double rischio = InpRischioBase * G[k].peso;
   if(InpRegime && G[k].regime)
     {
      double pend = 0.0;
      if(PendenzaD1(pend))
        {
         double fav = pend * sig;
         if(fav >= InpRegimeForte)
            rischio *= InpMoltForte;
         else
            if(fav < InpRegimeDebole)
               rischio *= InpMoltDebole;
        }
     }
   if(InpPerditeFila > 0 && (int)GvGet("fila", 0.0) >= InpPerditeFila)
      rischio *= InpFattorePerdite;
   if(InpTettoRischio > 0 && RischioAperto() + rischio > InpTettoRischio * InpRischioBase + 1e-9)
     {
      Log(StringFormat("Slot %s: segnale ignorato, rischio aperto %.2f%% + %.2f%% oltre il tetto %.2f%%", nome,
                       RischioAperto(), rischio, InpTettoRischio * InpRischioBase));
      return;
     }
   double D = G[k].sl * G[k].vol;
   if(D <= 0)
      return;
   double lvl = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   if(D <= lvl)
     {
      Log(StringFormat("Slot %s: segnale ignorato, stop troppo vicino per il broker", nome));
      return;
     }
   double perLotto = PerditaPerLotto(D + spread);
   if(perLotto <= 0)
      return;
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lotti = MathFloor(AccountInfoDouble(ACCOUNT_BALANCE) * rischio / 100.0 / perLotto / step) * step;
   if(lotti < vmin)
     {
      Log(StringFormat("Slot %s: segnale ignorato, lotto %.3f sotto il minimo %.2f (aumenta il rischio o il conto)",
                       nome, lotti, vmin));
      return;
     }
   lotti = MathMin(lotti, vmax);
   // livelli sul prezzo BID d'ingresso (B); per gli short stop e target scattano sull'ASK: livello BID + spread
   double B = bid;
   double sl = (sig == 1) ? B - D : B + D + spread;
   double tp = 0.0;
   if(G[k].rr > 0)
      tp = (sig == 1) ? B + G[k].rr * D : B - G[k].rr * D + spread;
   sl = NormalizeDouble(sl, _Digits);
   tp = NormalizeDouble(tp, _Digits);
   GvSet(glob, (double)G[k].obId);                              // un trade per OB: anche se l'ordine fallisce non riprova
   if(!Apri(k, sig, lotti, sl, tp))
      return;
   ulong tk;
   if(PosizioneSlot(k, tk))
     {
      GvSet(GvPos(tk, "B"), B);
      GvSet(GvPos(tk, "D"), D);
      GvSet(GvPos(tk, "V0"), lotti);
      GvSet(GvPos(tk, "F"), (double)((G[k].trDa == TRAIL_SUBITO) ? F_TR : 0));
      GvSet(GvPos(tk, "T"), (double)iTime(_Symbol, G[k].tf, 0));
      GvSet(GvPos(tk, "RM"), perLotto * lotti);
      GvSet(GvPos(tk, "SL0"), sl);
      GvSet(GvPos(tk, "S"), (double)k);
     }
   Log(StringFormat("Slot %s: APERTO %s %.2f lotti | prezzo %.2f | stop %.2f (distanza %.2f) | target %s | rischio %.2f%%", nome,
                    sig == 1 ? "BUY" : "SELL", lotti, B, sl, D, G[k].rr > 0 ? DoubleToString(tp, _Digits) : "nessuno", rischio));
   ScriviStato(true);
  }

//+------------------------------------------------------------------+
//| Ripresa dopo un riavvio: ricostruisce lo stato delle posizioni   |
//+------------------------------------------------------------------+
void RipristinaPosizioni()
  {
   for(int k = 0; k < NSLOT; k++)
     {
      if(!G[k].on)
         continue;
      ulong tk;
      if(!PosizioneSlot(k, tk) || !PositionSelectByTicket(tk))
         continue;
      if(GvGet(GvPos(tk, "B"), 0.0) > 0)
        {
         PrintFormat("Slot %s: ripresa la posizione %I64u", G[k].nome, tk);
         continue;
        }
      // stato perso: ricostruzione prudente dai dati della posizione
      bool buy = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
      double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
      double D = (sl > 0) ? MathAbs(op - sl) : 0.0;
      GvSet(GvPos(tk, "B"), op);
      GvSet(GvPos(tk, "D"), D);
      GvSet(GvPos(tk, "V0"), PositionGetDouble(POSITION_VOLUME));
      bool aPareggio = (sl > 0) && ((buy && sl >= op) || (!buy && sl <= op));
      GvSet(GvPos(tk, "F"), (double)(aPareggio ? (F_BE | F_P1 | F_P2) : 0));
      GvSet(GvPos(tk, "T"), (double)PositionGetInteger(POSITION_TIME));
      GvSet(GvPos(tk, "RM"), PerditaPerLotto(D) * PositionGetDouble(POSITION_VOLUME));
      GvSet(GvPos(tk, "SL0"), sl);
      GvSet(GvPos(tk, "S"), (double)k);
      PrintFormat("Slot %s: posizione %I64u senza stato salvato, ricostruito dai dati della posizione", G[k].nome, tk);
     }
  }

//+------------------------------------------------------------------+
//| Chiusura di una posizione: R, perdite di fila, CSV, pulizia      |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans, const MqlTradeRequest &request, const MqlTradeResult &result)
  {
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD || trans.deal == 0)
      return;
   if(!HistoryDealSelect(trans.deal))
      return;
   long entry = HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
   if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY)
      return;
   long magic = HistoryDealGetInteger(trans.deal, DEAL_MAGIC);
   int k = SlotDaMagic(magic);
   if(k < 0)
      return;
   ulong pid = (ulong)HistoryDealGetInteger(trans.deal, DEAL_POSITION_ID);
   if(PositionSelectByTicket(pid))
      return;                                                   // chiusura parziale: la posizione resta aperta
   if(!HistorySelectByPosition(pid))
      return;
   double profitto = 0.0, prezzoUscita = 0.0, prezzoIngresso = 0.0, volume = 0.0;
   datetime tIn = 0, tOut = 0;
   int dir = 0;
   for(int i = 0; i < HistoryDealsTotal(); i++)
     {
      ulong d = HistoryDealGetTicket(i);
      if(d == 0)
         continue;
      profitto += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_SWAP) +
                  HistoryDealGetDouble(d, DEAL_COMMISSION);
      long en = HistoryDealGetInteger(d, DEAL_ENTRY);
      if(en == DEAL_ENTRY_IN)
        {
         prezzoIngresso = HistoryDealGetDouble(d, DEAL_PRICE);
         volume = HistoryDealGetDouble(d, DEAL_VOLUME);
         tIn = (datetime)HistoryDealGetInteger(d, DEAL_TIME);
         dir = (HistoryDealGetInteger(d, DEAL_TYPE) == DEAL_TYPE_BUY) ? 1 : -1;
        }
      else
        {
         prezzoUscita = HistoryDealGetDouble(d, DEAL_PRICE);
         tOut = (datetime)HistoryDealGetInteger(d, DEAL_TIME);
        }
     }
   double rm = GvGet(GvPos(pid, "RM"), 0.0);
   double R = (rm > 0) ? profitto / rm : 0.0;
   int fila = (int)GvGet("fila", 0.0);
   if(R < -0.1)
      fila++;
   else
      if(R > 0.1)
         fila = 0;
   GvSet("fila", (double)fila);
   int fl = (int)GvGet(GvPos(pid, "F"), 0.0);
   Log(StringFormat("Slot %s: CHIUSO posizione %I64u, risultato %.2f (%.2fR); perdite di fila %d", G[k].nome, pid,
                    profitto, R, fila));
   if(InpLogCSV && g_csv != "")
     {
      int h = FileOpen(g_csv, FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_SHARE_READ | g_flagFile, ';');
      if(h != INVALID_HANDLE)
        {
         if(FileSize(h) == 0)
            FileWrite(h, "slot", "ticket", "direzione", "ingresso", "prezzo_ingresso", "B", "stop_iniziale",
                      "distanza_D", "lotti", "pareggio", "parziale1", "parziale2", "uscita", "prezzo_uscita",
                      "risultato", "R");
         FileSeek(h, 0, SEEK_END);
         FileWrite(h, G[k].nome, (long)pid, dir == 1 ? "BUY" : "SELL", TimeToString(tIn, TIME_DATE | TIME_MINUTES),
                   DoubleToString(prezzoIngresso, _Digits), DoubleToString(GvGet(GvPos(pid, "B"), 0.0), _Digits),
                   DoubleToString(GvGet(GvPos(pid, "SL0"), 0.0), _Digits), DoubleToString(GvGet(GvPos(pid, "D"), 0.0), 2),
                   DoubleToString(volume, 2), (fl & F_BE) != 0 ? "si" : "no", (fl & F_P1) != 0 ? "si" : "no",
                   (fl & F_P2) != 0 ? "si" : "no", TimeToString(tOut, TIME_DATE | TIME_MINUTES),
                   DoubleToString(prezzoUscita, _Digits), DoubleToString(profitto, 2), DoubleToString(R, 3));
         FileClose(h);
        }
     }
   string campi[] = {"B", "D", "V0", "F", "T", "RM", "SL0", "S"};
   for(int c = 0; c < ArraySize(campi); c++)
      GvDel(GvPos(pid, campi[c]));
   ScriviStato(true);
  }

//+------------------------------------------------------------------+
//| Pannello                                                         |
//+------------------------------------------------------------------+
void Pannello()
  {
   datetime now = TimeCurrent();
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double g0 = GvGet("g_" + ChiaveGiorno(now), eq);
   MqlDateTime d;
   TimeToStruct(now, d);
   double s0 = GvGet("s_" + ChiaveGiorno(now - ((d.day_of_week + 6) % 7) * 86400), eq);
   string t = StringFormat("VTOB Portfolio [%s]  rischio base %.2f%%  |  rischio aperto %.2f%% (tetto %.2f%%)%s\n",
                           InpId, InpRischioBase, RischioAperto(), InpTettoRischio * InpRischioBase,
                           InPausa() ? "  |  IN PAUSA (dashboard): nessun nuovo ingresso" : "");
   t += StringFormat("PnL oggi %.2f%%  |  settimana %.2f%%  |  perdite di fila %d\n",
                     g0 > 0 ? (eq - g0) / g0 * 100.0 : 0.0, s0 > 0 ? (eq - s0) / s0 * 100.0 : 0.0, (int)GvGet("fila", 0.0));
   for(int k = 0; k < NSLOT; k++)
     {
      if(!G[k].on)
         continue;
      ulong tk;
      string pos = "nessuna posizione";
      if(PosizioneSlot(k, tk) && PositionSelectByTicket(tk))
        {
         int fl = (int)GvGet(GvPos(tk, "F"), 0.0);
         pos = StringFormat("%s %.2f lotti, P/L %.2f%s%s", PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? "BUY" : "SELL",
                            PositionGetDouble(POSITION_VOLUME), PositionGetDouble(POSITION_PROFIT),
                            (fl & F_BE) != 0 ? ", a pareggio" : "", (fl & F_P1) != 0 ? ", parziale preso" : "");
        }
      t += StringFormat("%s (%s): %s | %s\n", G[k].nome, EnumToString(G[k].tf), G[k].stato, pos);
     }
   Comment(t);
  }

//+------------------------------------------------------------------+
//| Stato per la dashboard (JSON, sovrascritto): conto, pausa,       |
//| rischio, P/L del giorno e della settimana, slot e posizioni.     |
//+------------------------------------------------------------------+
void ScriviStato(const bool attivo)
  {
   if(g_stato == "")
      return;
   datetime now = TimeCurrent();
   double eq = AccountInfoDouble(ACCOUNT_EQUITY), bal = AccountInfoDouble(ACCOUNT_BALANCE);
   double g0 = GvGet("g_" + ChiaveGiorno(now), eq);
   MqlDateTime d;
   TimeToStruct(now, d);
   double s0 = GvGet("s_" + ChiaveGiorno(now - ((d.day_of_week + 6) % 7) * 86400), eq);
   string j = "{";
   j += "\"id\":" + Js(InpId) + ",\"simbolo\":" + Js(_Symbol) + ",\"attivo\":" + (attivo ? "true" : "false");
   j += ",\"in_pausa\":" + (InPausa() ? "true" : "false");
   j += ",\"versione\":\"2.10\",\"login\":" + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN));
   j += ",\"server\":" + Js(AccountInfoString(ACCOUNT_SERVER)) + ",\"valuta\":" + Js(AccountInfoString(ACCOUNT_CURRENCY));
   j += ",\"ora_server\":" + Js(TimeToString(now, TIME_DATE | TIME_SECONDS));
   j += ",\"ora_locale\":" + Js(TimeToString(TimeLocal(), TIME_DATE | TIME_SECONDS));
   j += ",\"saldo\":" + DoubleToString(bal, 2) + ",\"equity\":" + DoubleToString(eq, 2);
   j += ",\"rischio_base\":" + DoubleToString(InpRischioBase, 2) + ",\"rischio_aperto\":" + DoubleToString(RischioAperto(), 3);
   j += ",\"tetto_rischio\":" + DoubleToString(InpTettoRischio * InpRischioBase, 2);
   j += ",\"pnl_oggi_pct\":" + DoubleToString(g0 > 0 ? (eq - g0) / g0 * 100.0 : 0.0, 3);
   j += ",\"pnl_sett_pct\":" + DoubleToString(s0 > 0 ? (eq - s0) / s0 * 100.0 : 0.0, 3);
   j += ",\"perdite_fila\":" + IntegerToString((int)GvGet("fila", 0.0));
   j += ",\"autotrading\":" + ((TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) && MQLInfoInteger(MQL_TRADE_ALLOWED)) ? "true" : "false");
   j += ",\"slot\":[";
   bool primo = true;
   for(int k = 0; k < NSLOT; k++)
     {
      if(!G[k].on)
         continue;
      string tf = EnumToString(G[k].tf);
      StringReplace(tf, "PERIOD_", "");
      j += (primo ? "" : ",") + "{\"nome\":" + Js(G[k].nome) + ",\"tf\":" + Js(tf) + ",\"magic\":" +
           IntegerToString(G[k].magic) + ",\"stato\":" + Js(G[k].stato) + ",\"posizione\":";
      primo = false;
      ulong tk;
      if(PosizioneSlot(k, tk) && PositionSelectByTicket(tk))
        {
         int fl = (int)GvGet(GvPos(tk, "F"), 0.0);
         j += "{\"ticket\":" + IntegerToString((long)tk) + ",\"dir\":" +
              Js(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? "BUY" : "SELL") +
              ",\"lotti\":" + DoubleToString(PositionGetDouble(POSITION_VOLUME), 2) +
              ",\"prezzo\":" + DoubleToString(PositionGetDouble(POSITION_PRICE_OPEN), _Digits) +
              ",\"stop\":" + DoubleToString(PositionGetDouble(POSITION_SL), _Digits) +
              ",\"target\":" + DoubleToString(PositionGetDouble(POSITION_TP), _Digits) +
              ",\"profitto\":" + DoubleToString(PositionGetDouble(POSITION_PROFIT), 2) +
              ",\"pareggio\":" + (((fl & F_BE) != 0) ? "true" : "false") +
              ",\"parziale\":" + (((fl & F_P1) != 0) ? "true" : "false") + "}";
        }
      else
         j += "null";
      j += "}";
     }
   j += "]}";
   int h = FileOpen(g_stato, FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_SHARE_READ | g_flagFile);
   if(h == INVALID_HANDLE)
      return;
   FileWriteString(h, j);
   FileClose(h);
  }

void OnTimer()
  {
   ScriviStato(true);
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   AggiornaInizioPeriodo();
   for(int k = 0; k < NSLOT; k++)
      if(G[k].on)
         GestisciParziali(k);
   for(int k = 0; k < NSLOT; k++)
     {
      if(!G[k].on)
         continue;
      datetime t0 = iTime(_Symbol, G[k].tf, 0);
      if(t0 == 0 || t0 == G[k].lastBar)
         continue;
      G[k].lastBar = t0;
      datetime aperturaChiusa = iTime(_Symbol, G[k].tf, 1);    // candela appena chiusa
      ulong tk;
      bool avevaPosizione = PosizioneSlot(k, tk);
      if(!Valuta(k))
         continue;
      G[k].stato = StringFormat("trend %s, vol %.2f", G[k].trend == 1 ? "su" : "giù", G[k].vol);
      if(avevaPosizione)
         GestisciPosizione(k, aperturaChiusa);
      // come nel backtest: un segnale vale solo se alla chiusura della candela lo slot non era in posizione
      if(!avevaPosizione)
         ProvaIngresso(k, aperturaChiusa);
     }
   if(InpPannello)
      Pannello();
  }
//+------------------------------------------------------------------+
