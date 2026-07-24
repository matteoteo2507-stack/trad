//+------------------------------------------------------------------+
//|                                                    nxt_fade.mq5   |
//|                          Trading System Workspace - Forward Test  |
//|                                                                   |
//|  EA MECCANICO per il WALK-FORWARD LIVE della variante "fade"      |
//|  (mean-reversion) emersa dall'analisi di NXT. Porta fedele della  |
//|  config A1 di analysis/nxt/closure.py.                            |
//|                                                                   |
//|  ! STATUS: LEAD DATA-DERIVED, NON un edge dimostrato. Questo EA  |
//|  serve a RACCOGLIERE trade forward OOS su DEMO. Regole CONGELATE:  |
//|  non modificare i parametri della strategia durante il test.      |
//|  Spec: fondamenti_tecnici/strategie_candidate/fade_mr_walkforward_socio.md
//|                                                                   |
//|  LOGICA (H1, per-simbolo - aggancia l'EA a ogni grafico H1):      |
//|   1. Swing via fractale k=5 (uno swing e' confermato k barre dopo).|
//|   2. Gamba impulsiva = ultima L->H (up) / H->L (down) con filtro   |
//|      trend HH&HL (up) / LH&LL (down) e ampiezza >= 1*ATR(14).      |
//|   3. FADE = posizione CONTRO il trend: up-leg -> SHORT, down -> LONG|
//|      Entry al 50% di ritracciamento. R = 28.6% dell'ampiezza gamba.|
//|      SL = 1R (lato trend), TP = 3R (lato fade). BE a +2R.          |
//|      Pending valido 48 barre H1 dallo swing di fine; max hold 480. |
//|                                                                   |
//|  CROSS-CHECK: prima della demo, girare nello Strategy Tester sullo |
//|  stesso periodo del backtest Python e verificare che i numeri      |
//|  combacino (~31% win @1:3, E[R]~+0.35R pess). Se divergono, il     |
//|  port ha un bug -> NON deployare.                                  |
//+------------------------------------------------------------------+
#property copyright "Trading System Workspace"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <TradingSystemWorkspace/telegram.mqh>
#include <TradingSystemWorkspace/helpers.mqh>

//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+
input group "=== Strategia (fade / mean-reversion) - CONGELATA ==="
input ENUM_TIMEFRAMES InpTimeframe   = PERIOD_H1;  // timeframe operativo
input int    InpFractalK             = 5;          // semi-finestra fractale swing
input int    InpAtrPeriod            = 14;         // periodo ATR (H1)
input double InpMinLegAtr            = 1.0;        // ampiezza minima gamba (x ATR)
input double InpEntryFib             = 0.5;        // ritracciamento d'ingresso
input double InpRiskLegFrac          = 0.286;      // R in frazione di ampiezza (mirror A1)
input double InpRR                   = 3.0;        // take-profit in R
input double InpBeAtR                = 2.0;        // break-even a +NR
input int    InpFillWindowBars       = 48;         // barre max per il fill dallo swing di fine
input int    InpMaxHoldBars          = 480;        // barre max di holding (~20 giorni H1)
input int    InpLookbackBars         = 400;        // finestra barre per la detection

input group "=== Sizing (fixed fractional) ==="
input double InpRiskPerTradePct      = 0.01;       // % equity rischiata per trade
input double InpFallbackVolume       = 0.10;       // lotti di fallback

input group "=== Telegram (opzionale) ==="
input string InpTelegramBotToken     = "";
input string InpTelegramChatId       = "";

input group "=== Identificazione ==="
input ulong  InpMagicNumber          = 26071;      // magic distinto (london=26050)
input string InpStrategyName         = "nxt_fade";

//+------------------------------------------------------------------+
//| Stato                                                            |
//+------------------------------------------------------------------+
CTrade   g_trade;
int      g_atr_handle       = INVALID_HANDLE;
datetime g_last_bar_time    = 0;
datetime g_last_armed_leg   = 0;   // endtime della gamba gia' armata (no doppio arm)
datetime g_pending_swingend = 0;   // endtime della gamba del pending attivo (per expiry)

bool     g_pos_open   = false;
bool     g_pos_short  = false;
bool     g_pos_be_done= false;
double   g_pos_entry  = 0.0;
double   g_pos_risk   = 0.0;       // rischio iniziale |entry - SL| al fill
datetime g_pos_fill_t = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_trade.SetDeviationInPoints(20);

   g_atr_handle = iATR(_Symbol, InpTimeframe, InpAtrPeriod);
   if(g_atr_handle == INVALID_HANDLE)
   {
      PrintFormat("[%s] iATR handle non creato.", InpStrategyName);
      return INIT_FAILED;
   }

   PrintFormat("[%s] EA avviato. Magic=%I64u Symbol=%s TF=%d",
               InpStrategyName, InpMagicNumber, _Symbol, (int)InpTimeframe);
   NotifyTelegram(StringFormat("[START] [%s] avviato su %s (forward fade, DEMO)",
                               InpStrategyName, _Symbol));
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(g_atr_handle != INVALID_HANDLE) IndicatorRelease(g_atr_handle);
   PrintFormat("[%s] EA fermato (reason=%d)", InpStrategyName, reason);
   NotifyTelegram(StringFormat("[STOP] [%s] fermato su %s (reason=%d)",
                               InpStrategyName, _Symbol, reason));
}

//+------------------------------------------------------------------+
void OnTick()
{
   // Gestione tick-level (fill detect, break-even, max-hold).
   ManageOpenPosition();

   // Logica bar-level (arm nuove gambe, expiry pendenti): solo a nuova barra.
   datetime cur = iTime(_Symbol, InpTimeframe, 0);
   if(cur != g_last_bar_time)
   {
      g_last_bar_time = cur;
      OnNewBar();
   }
}

//+------------------------------------------------------------------+
//| Gestione posizione aperta: fill detect, BE, max-hold (tick).     |
//+------------------------------------------------------------------+
void ManageOpenPosition()
{
   ulong  pt = 0;
   double entry=0, sl=0, tp=0; long ptype=-1;
   for(int i = PositionsTotal()-1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      pt    = t;
      entry = PositionGetDouble(POSITION_PRICE_OPEN);
      sl    = PositionGetDouble(POSITION_SL);
      tp    = PositionGetDouble(POSITION_TP);
      ptype = PositionGetInteger(POSITION_TYPE);
      break;
   }

   if(pt == 0)
   {
      if(g_pos_open)  // era aperta, ora chiusa (TP/SL/hold)
      {
         g_pos_open = false; g_pos_be_done = false;
         NotifyTelegram(StringFormat("[OK] [%s] %s posizione chiusa", InpStrategyName, _Symbol));
      }
      return;
   }

   // Fill appena avvenuto -> cattura stato iniziale.
   if(!g_pos_open)
   {
      g_pos_open   = true;
      g_pos_short  = (ptype == POSITION_TYPE_SELL);
      g_pos_entry  = entry;
      g_pos_risk   = MathAbs(entry - sl);
      g_pos_be_done= false;
      g_pos_fill_t = TimeCurrent();
      NotifyTelegram(StringFormat("[FILL] [%s] %s FILL %s @ %s (R=%s)",
         InpStrategyName, _Symbol, (g_pos_short ? "SHORT" : "LONG"),
         DoubleToString(entry, _Digits), DoubleToString(g_pos_risk, _Digits)));
   }

   // Break-even a +NR.
   if(!g_pos_be_done && g_pos_risk > 0)
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      bool hit = g_pos_short
                 ? (ask <= g_pos_entry - InpBeAtR * g_pos_risk)   // short in profitto = prezzo scende
                 : (bid >= g_pos_entry + InpBeAtR * g_pos_risk);
      if(hit)
      {
         double be = NormalizePrice(g_pos_entry);
         if(g_trade.PositionModify(pt, be, tp))
         {
            g_pos_be_done = true;
            NotifyTelegram(StringFormat("[BE] [%s] %s SL->BE (%s @ +%.1fR)",
               InpStrategyName, _Symbol, DoubleToString(be, _Digits), InpBeAtR));
         }
      }
   }

   // Max hold.
   int held = iBarShift(_Symbol, InpTimeframe, g_pos_fill_t);
   if(held > InpMaxHoldBars)
   {
      if(g_trade.PositionClose(pt))
         NotifyTelegram(StringFormat("[HOLD] [%s] %s chiusa per max-hold (%d barre)",
            InpStrategyName, _Symbol, InpMaxHoldBars));
   }
}

//+------------------------------------------------------------------+
//| Logica a nuova barra: expiry pendenti + arm nuova gamba.         |
//+------------------------------------------------------------------+
void OnNewBar()
{
   ulong pend = GetOwnPendingTicket();
   if(pend > 0)
   {
      // Expiry: pending valido 48 barre H1 dallo swing di fine.
      if(iBarShift(_Symbol, InpTimeframe, g_pending_swingend) > InpFillWindowBars)
      {
         if(g_trade.OrderDelete(pend))
            NotifyTelegram(StringFormat("[EXPIRE] [%s] %s pending scaduto (no fill in %d barre)",
               InpStrategyName, _Symbol, InpFillWindowBars));
      }
      return;  // un solo setup attivo per volta
   }

   if(g_pos_open || CountOwnPositions() > 0) return;

   bool is_short; double hi, lo, rng; datetime endtime;
   if(DetectLatestLeg(is_short, hi, lo, rng, endtime))
   {
      if(endtime == g_last_armed_leg) return;  // gia' gestita
      ArmSetup(is_short, hi, lo, rng, endtime);
   }
}

//+------------------------------------------------------------------+
//| Rilev l'ultima gamba valida (ZigZag da fractali + filtro trend).|
//| Ritorna true e i parametri del FADE se c'e' un setup.            |
//+------------------------------------------------------------------+
bool DetectLatestLeg(bool &is_short, double &hi, double &lo, double &rng, datetime &endtime)
{
   int N = InpLookbackBars;
   int K = InpFractalK;

   MqlRates r[];
   ArraySetAsSeries(r, false);
   int copied = CopyRates(_Symbol, InpTimeframe, 1, N, r);   // shift 1..N (chiuse), r[0]=piu' vecchia
   if(copied < 4 * K + 4) return false;

   double atrbuf[];
   ArraySetAsSeries(atrbuf, false);
   int ac = CopyBuffer(g_atr_handle, 0, 1, copied, atrbuf);
   if(ac <= 0) return false;
   int aoff = copied - ac;   // atrbuf allineato agli ULTIMI ac indici finestra

   // Pivot alternati (H/L).
   double pp[];  int ptv[];  int pidx[];
   ArrayResize(pp, copied); ArrayResize(ptv, copied); ArrayResize(pidx, copied);
   int pc = 0;

   for(int i = K; i <= copied - 1 - K; i++)
   {
      bool fh = true, fl = true;
      for(int j = i - K; j <= i + K; j++)
      {
         if(r[j].high > r[i].high) fh = false;
         if(r[j].low  < r[i].low)  fl = false;
      }
      if(fh && !(r[i].high > r[i-1].high)) fh = false;   // no flat
      if(fl && !(r[i].low  < r[i-1].low))  fl = false;

      int    type;  double price;
      if(fh)      { type = 1; price = r[i].high; }
      else if(fl) { type = 0; price = r[i].low;  }
      else continue;

      if(pc == 0)
      {
         pp[pc] = price; ptv[pc] = type; pidx[pc] = i; pc++;
      }
      else if(ptv[pc-1] == type)   // stesso tipo -> tieni il piu' estremo
      {
         if((type == 1 && price >= pp[pc-1]) || (type == 0 && price <= pp[pc-1]))
         { pp[pc-1] = price; pidx[pc-1] = i; }
      }
      else
      {
         pp[pc] = price; ptv[pc] = type; pidx[pc] = i; pc++;
      }
   }

   if(pc < 4) return false;
   int i0 = pc-4, i1 = pc-3, i2 = pc-2, i3 = pc-1;

   // ATR alla gamba di partenza (pivot p2).
   int startIdx = pidx[i2];
   if(startIdx - aoff < 0 || startIdx - aoff >= ac) return false;
   double atr_start = atrbuf[startIdx - aoff];
   if(atr_start <= 0) return false;

   // Pattern L,H,L,H -> BUY leg (uptrend) -> FADE SHORT.
   if(ptv[i0]==0 && ptv[i1]==1 && ptv[i2]==0 && ptv[i3]==1)
   {
      double s_lo = pp[i2], e_hi = pp[i3];
      double range = e_hi - s_lo;
      if(range <= 0 || range < InpMinLegAtr * atr_start) return false;
      if(!(pp[i3] > pp[i1] && pp[i2] > pp[i0])) return false;   // HH & HL
      is_short = true; hi = e_hi; lo = s_lo; rng = range; endtime = r[pidx[i3]].time;
      return true;
   }

   // Pattern H,L,H,L -> SELL leg (downtrend) -> FADE LONG.
   if(ptv[i0]==1 && ptv[i1]==0 && ptv[i2]==1 && ptv[i3]==0)
   {
      double s_hi = pp[i2], e_lo = pp[i3];
      double range = s_hi - e_lo;
      if(range <= 0 || range < InpMinLegAtr * atr_start) return false;
      if(!(pp[i2] < pp[i0] && pp[i3] < pp[i1])) return false;   // LH & LL
      is_short = false; hi = s_hi; lo = e_lo; rng = range; endtime = r[pidx[i3]].time;
      return true;
   }

   return false;
}

//+------------------------------------------------------------------+
//| Arma il setup: calcola entry/SL/TP e piazza l'ordine.            |
//+------------------------------------------------------------------+
void ArmSetup(const bool is_short, const double hi, const double lo,
              const double rng, const datetime endtime)
{
   double risk = InpRiskLegFrac * rng;
   if(risk <= 0) return;

   double entry, sl, tp;
   if(is_short) { entry = hi - InpEntryFib * rng; sl = entry + risk; tp = entry - InpRR * risk; }
   else         { entry = lo + InpEntryFib * rng; sl = entry - risk; tp = entry + InpRR * risk; }

   entry = NormalizePrice(entry);
   sl    = NormalizePrice(sl);
   tp    = NormalizePrice(tp);

   double vol = ComputeVolume(MathAbs(entry - sl));
   double stops = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   string cm = InpStrategyName;
   bool ok = false;

   if(is_short)
   {
      // Fill quando il prezzo SCENDE all'entry (retrace) -> SELL STOP sotto il mercato.
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      if(bid > entry + stops)
         ok = g_trade.SellStop(vol, entry, _Symbol, sl, tp, ORDER_TIME_GTC, 0, cm);
      else
         ok = g_trade.Sell(vol, _Symbol, 0.0, sl, tp, cm);   // prezzo gia' oltre -> market
   }
   else
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      if(ask < entry - stops)
         ok = g_trade.BuyStop(vol, entry, _Symbol, sl, tp, ORDER_TIME_GTC, 0, cm);
      else
         ok = g_trade.Buy(vol, _Symbol, 0.0, sl, tp, cm);
   }

   if(ok)
   {
      g_pending_swingend = endtime;
      g_last_armed_leg   = endtime;
      NotifyTelegram(StringFormat("[ORDER] [%s] %s ARM %s | entry %s SL %s TP %s (R=%s) vol %.2f",
         InpStrategyName, _Symbol, (is_short ? "SHORT-fade" : "LONG-fade"),
         DoubleToString(entry,_Digits), DoubleToString(sl,_Digits),
         DoubleToString(tp,_Digits), DoubleToString(risk,_Digits), vol));
   }
   else
   {
      PrintFormat("[%s] %s arm fallito, err=%d", InpStrategyName, _Symbol, GetLastError());
   }
}

//+------------------------------------------------------------------+
//| Utility                                                          |
//+------------------------------------------------------------------+
int CountOwnPositions()
{
   int c = 0;
   for(int i = PositionsTotal()-1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      c++;
   }
   return c;
}

ulong GetOwnPendingTicket()
{
   for(int i = OrdersTotal()-1; i >= 0; i--)
   {
      ulong t = OrderGetTicket(i);
      if(t == 0) continue;
      if(OrderGetInteger(ORDER_MAGIC) != (long)InpMagicNumber) continue;
      if(OrderGetString(ORDER_SYMBOL) != _Symbol) continue;
      return t;
   }
   return 0;
}

double ComputeVolume(const double risk_price)
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= 0 || risk_price <= 0) return InpFallbackVolume;

   double risk_money = equity * InpRiskPerTradePct;
   double tick_size  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tick_size <= 0 || tick_value <= 0) return InpFallbackVolume;

   double money_per_unit = (risk_price / tick_size) * tick_value;
   if(money_per_unit <= 0) return InpFallbackVolume;

   double raw  = risk_money / money_per_unit;
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0) step = 0.01;

   double v = MathFloor(raw / step) * step;
   if(v < vmin) v = vmin;
   if(vmax > 0 && v > vmax) v = vmax;
   return v;
}

double NormalizePrice(const double price)
{
   double tick = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tick <= 0) return NormalizeDouble(price, _Digits);
   return NormalizeDouble(MathRound(price / tick) * tick, _Digits);
}

void NotifyTelegram(const string text)
{
   if(StringLen(InpTelegramBotToken) == 0 || StringLen(InpTelegramChatId) == 0) return;
   TG_SendMessage(InpTelegramBotToken, InpTelegramChatId, text);
}
//+------------------------------------------------------------------+
