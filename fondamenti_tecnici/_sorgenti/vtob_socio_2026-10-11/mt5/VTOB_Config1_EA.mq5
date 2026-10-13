//+------------------------------------------------------------------+
//| VTOB_Config1_EA.mq5                                              |
//| Expert Advisor della "Configurazione 1" della strategia VTOB PRO |
//| (logica OB derivata da "Volume-Trend Order Block Engine"         |
//|  di BigBeluga, CC BY-NC-SA 4.0)                                  |
//|                                                                  |
//| Backtest XAUUSD M15 lug 2022 - ott 2026 (simulatore Python):     |
//|   199 trade, PF 2.03, +83R, drawdown max 8.9R                    |
//|                                                                  |
//| Regole:                                                          |
//|  - OB sui pivot (7 a sinistra / 3 a destra) nella direzione del  |
//|    Supertrend custom; zona = min(open,close) del pivot - 1x vol  |
//|  - Filtri obbligatori: trend da >= 20 candele, OB oltre la linea |
//|    di trend, close sopra (long) / sotto (short) EMA200 H1 chiusa |
//|  - Segnale: low incrocia sopra il top dell'OB (a candela chiusa) |
//|  - Ingresso a mercato all'apertura della candela successiva      |
//|  - SL 6x volatilità, TP 3R, stop a pareggio +0.1R quando il      |
//|    massimo di una candela chiusa tocca +1R                       |
//|  - Un solo trade per OB, una sola posizione alla volta           |
//|                                                                  |
//| USARE PRIMA SU CONTO DEMO. Grafico: XAUUSD M15.                  |
//+------------------------------------------------------------------+
#property copyright "VTOB Config 1"
#property version   "1.00"

#include <Trade\Trade.mqh>

input group "Rischio"
input double InpRiskPct     = 0.5;    // Rischio per trade (% del balance)
input double InpFixedLots   = 0.0;    // Lotto fisso (se > 0 ignora il rischio %)
input double InpMaxSpread   = 1.00;   // Spread massimo per entrare ($ di prezzo)

input group "Gestione trade"
input bool   InpAllowLong   = true;   // Long
input bool   InpAllowShort  = false;  // Short
input double InpSlMult      = 6.0;    // Stop = X volte la volatilità
input double InpRR          = 3.0;    // Target (R)
input double InpBeR         = 1.0;    // Pareggio a +X R (0 = off)
input double InpBeOff       = 0.1;    // Offset pareggio (R)

input group "Indicatore"
input int    InpStLen       = 50;     // Volatilità: SMA del range
input double InpStMult      = 3.5;    // Supertrend multiplier
input int    InpPivL        = 7;      // Pivot: candele a sinistra
input int    InpPivR        = 3;      // Pivot: candele a destra
input int    InpMinAge      = 20;     // Trend avviato da almeno N candele
input double InpDistMult    = 0.0;    // Distanza minima dalla linea di trend (x vol)
input ENUM_TIMEFRAMES InpHtf = PERIOD_H1; // TF superiore per la EMA
input int    InpHtfLen      = 200;    // EMA TF superiore
input int    InpBars        = 3000;   // Candele ricalcolate a ogni nuova barra

input group "Varie"
input long   InpMagic       = 7303001; // Magic number
input string InpComment     = "VTOB_C1";

CTrade   trade;
int      g_ema = INVALID_HANDLE;
datetime g_lastBar = 0;
string   g_gvName;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(_Period != PERIOD_M15)
      Print("ATTENZIONE: la configurazione è stata testata su M15. Timeframe attuale: ", EnumToString(_Period));
   g_ema = iMA(_Symbol, InpHtf, InpHtfLen, 0, MODE_EMA, PRICE_CLOSE);
   if(g_ema == INVALID_HANDLE) { Print("Errore creazione EMA HTF"); return(INIT_FAILED); }
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(50);
   g_gvName = "VTOB_C1_" + _Symbol + "_" + IntegerToString(InpMagic) + "_lastOB";
   if(!GlobalVariableCheck(g_gvName)) GlobalVariableSet(g_gvName, 0);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { if(g_ema != INVALID_HANDLE) IndicatorRelease(g_ema); }

//+------------------------------------------------------------------+
bool HasPosition(ulong &ticket)
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic)
        { ticket = t; return(true); }
     }
   return(false);
  }

//+------------------------------------------------------------------+
//| Ricalcola indicatore e OB sulle ultime InpBars candele chiuse.    |
//| sig = +1 / -1 / 0 sulla candela appena chiusa; obId = tempo pivot |
//+------------------------------------------------------------------+
bool Evaluate(int &sig, long &obId, double &vol)
  {
   sig = 0; obId = 0; vol = 0;
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int n = CopyRates(_Symbol, _Period, 1, InpBars, r);   // r[n-1] = ultima candela chiusa
   if(n < InpStLen + InpPivL + InpPivR + 50) { Print("Storico insufficiente: ", n); return(false); }

   int need = (int)(n * PeriodSeconds(_Period) / PeriodSeconds(InpHtf)) + InpHtfLen + 200;
   double ema[];
   ArraySetAsSeries(ema, true);
   int hn = CopyBuffer(g_ema, 0, 0, need, ema);
   if(hn <= 0) { Print("EMA HTF non pronta"); return(false); }

   double v[], ub[], lb[], ts[];
   int tr[], age[];
   ArrayResize(v, n); ArrayResize(ub, n); ArrayResize(lb, n); ArrayResize(ts, n);
   ArrayResize(tr, n); ArrayResize(age, n);

   double sumR = 0;
   double aTop = EMPTY_VALUE, aBot = EMPTY_VALUE, prevTop = EMPTY_VALUE, prevBot = EMPTY_VALUE;
   int    aDir = 0;
   long   aId = 0;

   for(int i = 0; i < n; i++)
     {
      // volatilità = SMA(high-low, InpStLen)
      sumR += r[i].high - r[i].low;
      if(i >= InpStLen) sumR -= r[i - InpStLen].high - r[i - InpStLen].low;
      bool vok = (i >= InpStLen - 1);
      v[i] = vok ? sumR / InpStLen : EMPTY_VALUE;

      // Supertrend custom (come nel Pine)
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
      else { lb[i] = pLB; ub[i] = pUB; }
      if(i == 0 || v[i - 1] == EMPTY_VALUE) tr[i] = 1;
      else if(ts[i - 1] == pUB)             tr[i] = (r[i].close > ub[i]) ? 1 : -1;
      else                                  tr[i] = (r[i].close < lb[i]) ? -1 : 1;
      ts[i] = (tr[i] == 1) ? lb[i] : ub[i];
      bool chg = (i > 0 && tr[i] != tr[i - 1]);
      age[i] = (i == 0) ? 100000 : (chg ? 0 : age[i - 1] + 1);

      // pivot confermati sulla candela i (pivot su p = i - InpPivR)
      bool pl = false, ph = false;
      if(i >= InpPivL + InpPivR)
        {
         int p = i - InpPivR;
         pl = true; ph = true;
         for(int k = p - InpPivL; k < p; k++)
           { if(r[k].low <= r[p].low) pl = false; if(r[k].high >= r[p].high) ph = false; }
         for(int k = p + 1; k <= i; k++)
           { if(r[k].low < r[p].low) pl = false; if(r[k].high > r[p].high) ph = false; }
        }

      // EMA dell'ultima candela HTF chiusa
      double e = EMPTY_VALUE;
      int s = iBarShift(_Symbol, InpHtf, r[i].time, false);
      if(s >= 0 && s + 1 < hn) e = ema[s + 1];

      if(vok)
        {
         // OB long
         if(tr[i] == 1 && pl)
           {
            int p = i - InpPivR;
            double t = MathMin(r[p].open, r[p].close), bt = t - v[i];
            bool ov = (aTop != EMPTY_VALUE && aBot != EMPTY_VALUE) && !(bt > aTop || t < aBot);
            if(!ov && age[i] >= InpMinAge && bt - ts[i] >= InpDistMult * v[i] && e != EMPTY_VALUE && r[i].close > e)
              { aTop = t; aBot = bt; aDir = 1; aId = (long)r[p].time; }
           }
         // OB short
         if(tr[i] == -1 && ph)
           {
            int p = i - InpPivR;
            double bt = MathMax(r[p].open, r[p].close), t = bt + v[i];
            bool ov = (aTop != EMPTY_VALUE && aBot != EMPTY_VALUE) && !(bt > aTop || t < aBot);
            if(!ov && age[i] >= InpMinAge && ts[i] - t >= InpDistMult * v[i] && e != EMPTY_VALUE && r[i].close < e)
              { aTop = t; aBot = bt; aDir = -1; aId = (long)r[p].time; }
           }
        }
      // rottura OB
      if(aDir == 1 && r[i].high < aBot)      { aTop = EMPTY_VALUE; aBot = EMPTY_VALUE; aDir = 0; }
      else if(aDir == -1 && r[i].low > aTop) { aTop = EMPTY_VALUE; aBot = EMPTY_VALUE; aDir = 0; }

      // segnale sull'ultima candela chiusa (crossover come ta.crossover)
      if(i == n - 1 && i > 0)
        {
         if(aDir == 1 && !pl && !chg && prevTop != EMPTY_VALUE && aTop != EMPTY_VALUE &&
            r[i].low > aTop && r[i - 1].low <= prevTop)
            sig = 1;
         if(aDir == -1 && !ph && !chg && prevBot != EMPTY_VALUE && aBot != EMPTY_VALUE &&
            r[i].high < aBot && r[i - 1].high >= prevBot)
            sig = -1;
         obId = aId; vol = v[i];
        }
      prevTop = aTop;
      prevBot = aBot;
     }
   return(true);
  }

//+------------------------------------------------------------------+
double LotsForRisk(double distPrice)
  {
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lots;
   if(InpFixedLots > 0) lots = InpFixedLots;
   else
     {
      double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
      double tickVal  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);
      if(tickVal <= 0) tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      double lossPerLot = distPrice / tickSize * tickVal;
      if(lossPerLot <= 0) return(0);
      double riskMoney = AccountInfoDouble(ACCOUNT_BALANCE) * InpRiskPct / 100.0;
      lots = riskMoney / lossPerLot;
     }
   lots = MathFloor(lots / step) * step;
   if(lots < vmin) { Print("Lotto calcolato sotto il minimo (", DoubleToString(lots, 2), "): trade saltato. Aumenta il rischio % o il conto."); return(0); }
   return(MathMin(lots, vmax));
  }

//+------------------------------------------------------------------+
//| Pareggio: controllato sulle candele chiuse dall'apertura          |
//+------------------------------------------------------------------+
void ManageBreakEven()
  {
   if(InpBeR <= 0) return;
   ulong tk;
   if(!HasPosition(tk) || !PositionSelectByTicket(tk)) return;
   long   type = PositionGetInteger(POSITION_TYPE);
   double sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
   double op = PositionGetDouble(POSITION_PRICE_OPEN);
   datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
   if(sl <= 0 || tp <= 0) return;
   int sh = iBarShift(_Symbol, _Period, ot, false);   // candela di ingresso
   if(sh < 1) return;                                  // nessuna candela chiusa dall'ingresso
   if(type == POSITION_TYPE_BUY && sl < op)
     {
      double dist = (tp - sl) / (InpRR + 1.0);
      double ref  = sl + dist;                         // prezzo di riferimento (bid all'ingresso)
      int hi = iHighest(_Symbol, _Period, MODE_HIGH, sh, 1);
      if(hi < 0) return;
      if(iHigh(_Symbol, _Period, hi) >= ref + InpBeR * dist)
        {
         double nsl = NormalizeDouble(ref + InpBeOff * dist, _Digits);
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         if(bid <= nsl) { trade.PositionClose(tk); Print("Pareggio: prezzo già sotto il livello, chiusura a mercato"); }
         else if(trade.PositionModify(tk, nsl, tp)) Print("Stop spostato a pareggio: ", nsl);
        }
     }
   if(type == POSITION_TYPE_SELL && sl > op)
     {
      double dist = (sl - tp) / (InpRR + 1.0);
      double ref  = sl - dist;
      int lo = iLowest(_Symbol, _Period, MODE_LOW, sh, 1);
      if(lo < 0) return;
      if(iLow(_Symbol, _Period, lo) <= ref - InpBeR * dist)
        {
         double nsl = NormalizeDouble(ref - InpBeOff * dist, _Digits);
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         if(ask >= nsl) { trade.PositionClose(tk); Print("Pareggio: prezzo già sopra il livello, chiusura a mercato"); }
         else if(trade.PositionModify(tk, nsl, tp)) Print("Stop spostato a pareggio: ", nsl);
        }
     }
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime t0 = iTime(_Symbol, _Period, 0);
   if(t0 == 0 || t0 == g_lastBar) return;
   g_lastBar = t0;

   ManageBreakEven();

   int sig; long obId; double vol;
   if(!Evaluate(sig, obId, vol) || sig == 0) return;
   if((sig == 1 && !InpAllowLong) || (sig == -1 && !InpAllowShort)) return;

   ulong tk;
   if(HasPosition(tk)) { Print("Segnale ignorato: posizione già aperta"); return; }
   if((double)obId == GlobalVariableGet(g_gvName)) { Print("Segnale ignorato: OB già tradato"); return; }

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double spread = ask - bid;
   if(spread > InpMaxSpread) { Print("Segnale ignorato: spread troppo alto ", DoubleToString(spread, 2)); return; }

   double dist = InpSlMult * vol;
   long stopsLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   if(dist < stopsLvl * _Point) { Print("Stop troppo vicino per il broker"); return; }

   double lots = LotsForRisk(dist + spread);
   if(lots <= 0) return;

   bool ok;
   if(sig == 1)
     {
      double sl = NormalizeDouble(bid - dist, _Digits), tp = NormalizeDouble(bid + InpRR * dist, _Digits);
      ok = trade.Buy(lots, _Symbol, 0.0, sl, tp, InpComment);
     }
   else
     {
      double sl = NormalizeDouble(ask + dist, _Digits), tp = NormalizeDouble(ask - InpRR * dist, _Digits);
      ok = trade.Sell(lots, _Symbol, 0.0, sl, tp, InpComment);
     }
   if(ok && (trade.ResultRetcode() == TRADE_RETCODE_DONE || trade.ResultRetcode() == TRADE_RETCODE_PLACED))
     {
      GlobalVariableSet(g_gvName, (double)obId);
      PrintFormat("Aperto %s %.2f lotti | stop %.2f$ | target %.2f$", sig == 1 ? "BUY" : "SELL", lots, dist, InpRR * dist);
     }
   else
      Print("Ordine fallito: ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
  }
//+------------------------------------------------------------------+
