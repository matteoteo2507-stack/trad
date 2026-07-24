//+------------------------------------------------------------------+
//|                                                  orb_nasdaq.mq5   |
//|                          Trading System Workspace - Forward Test  |
//|                                                                   |
//|  EA MECCANICO per il WALK-FORWARD LIVE dell'Opening-Range         |
//|  Breakout v2 su NAS100 ("strategia socio", criteri utente 1:3).   |
//|  Port fedele di analysis/opening_range/backtest_v2.py.            |
//|                                                                   |
//|  ! STATUS: NO-GO sui 14.5y di backtest. Il forward serve SOLO a  |
//|  risolvere la domanda aperta: il marginale-positivo 2020-2026 e'  |
//|  rumore o vero cambio di microstruttura post-COVID? Aspettativa   |
//|  pre-registrata: ~0/negativa. Regole CONGELATE.                   |
//|                                                                   |
//|  LOGICA (NAS100, M5):                                             |
//|   1. Opening range = 09:30-10:00 ET (ORH/ORL).                    |
//|   2. Sessione 10:00-12:00 ET: primo bar che CHIUDE oltre l'OR     |
//|      decide il lato; level = low(SELL)/high(BUY) del bar rottura. |
//|   3. Trail del level finche' un bar CHIUDE oltre level = conferma.|
//|   4. Entry = retest del level (LIMIT). SL = ORL+10 (SELL) /       |
//|      ORH-10 (BUY). TP = 1:3 dallo SL. BE a +2R.                   |
//|   5. Filtro ADX(14) >= 25 alla conferma. Pending scade 12:00 ET.  |
//|      Un solo trade al giorno.                                     |
//|                                                                   |
//|  ! TIMEZONE: l'OR e' ancorato all'ora di NEW YORK (ET) con DST   |
//|  USA, calcolata da TimeGMT(). VERIFICA nel cross-check che l'OR    |
//|  catturi davvero le 09:30-10:00 ET sul tuo broker (in Strategy     |
//|  Tester TimeGMT puo' comportarsi diversamente dal live).          |
//|                                                                   |
//|  CROSS-CHECK: gira nello Strategy Tester su NAS100 M5 sullo stesso |
//|  periodo di backtest_v2.py e verifica win%/E[R] per anno          |
//|  (TRAIN '12-'19 neg, TEST '20-'26 marginale). Divergenza = bug.   |
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
input group "=== Sessione (ora di New York, ET) - CONGELATA ==="
input ENUM_TIMEFRAMES InpTimeframe = PERIOD_M5;
input int    InpOrStartEtH   = 9;    // OR start 09:30 ET
input int    InpOrStartEtM   = 30;
input int    InpOrEndEtH      = 10;   // OR end / inizio sessione 10:00 ET
input int    InpOrEndEtM      = 0;
input int    InpExpiryEtH     = 12;   // scadenza pending 12:00 ET
input int    InpExpiryEtM     = 0;

input group "=== Soglie - CONGELATE ==="
input double InpBufferPoints  = 10.0; // SL = ORL+buffer (SELL) / ORH-buffer (BUY), in punti indice (prezzo)
input double InpRR            = 3.0;  // TP = 1:3 dallo SL
input double InpBeAtR         = 2.0;  // break-even a +2R
input int    InpAdxPeriod     = 14;   // periodo ADX (M5)
input double InpAdxMin        = 25.0; // filtro volatilita' alla conferma
input int    InpMaxHoldBars   = 1440; // max hold M5 (~5 giorni)

input group "=== Sizing ==="
input double InpRiskPerTradePct = 0.01;
input double InpFallbackVolume   = 0.10;

input group "=== Telegram (opzionale) ==="
input string InpTelegramBotToken = "";
input string InpTelegramChatId   = "";

input group "=== Identificazione ==="
input ulong  InpMagicNumber      = 26052;   // distinto (london=26050, fade=26071)
input string InpStrategyName      = "orb_nasdaq";

//+------------------------------------------------------------------+
//| Stato del giorno                                                 |
//+------------------------------------------------------------------+
struct DayState
{
   string   et_date;       // "YYYY-MM-DD" ET del giorno
   bool     or_built;      // OR calcolato
   double   orh, orl;
   bool     broke;         // primo break avvenuto
   int      side;          // +1 BUY, -1 SELL, 0 nessuno
   double   level;         // livello trailato (low/high del break)
   bool     confirmed;     // conferma (chiusura oltre level) -> pending piazzato
   bool     done;          // giornata conclusa (trade piazzato o skip)
   ulong    pend_ticket;   // pending retest
   bool     filled;        // posizione aperta
   double   entry, sl0, tp, be_trig, risk;
   bool     be_done;
   datetime fill_time;
};

DayState g_d;
CTrade   g_trade;
int      g_adx_handle    = INVALID_HANDLE;
datetime g_last_bar_time = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_trade.SetDeviationInPoints(30);

   g_adx_handle = iADX(_Symbol, InpTimeframe, InpAdxPeriod);
   if(g_adx_handle == INVALID_HANDLE)
   {
      PrintFormat("[%s] iADX handle non creato.", InpStrategyName);
      return INIT_FAILED;
   }
   ResetDay("");
   PrintFormat("[%s] EA avviato. Magic=%I64u Symbol=%s", InpStrategyName, InpMagicNumber, _Symbol);
   NotifyTelegram(StringFormat("[START] [%s] avviato su %s (ORB v2 forward, DEMO)", InpStrategyName, _Symbol));
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_adx_handle != INVALID_HANDLE) IndicatorRelease(g_adx_handle);
   PrintFormat("[%s] EA fermato (reason=%d)", InpStrategyName, reason);
   NotifyTelegram(StringFormat("[STOP] [%s] fermato su %s (reason=%d)", InpStrategyName, _Symbol, reason));
}

void ResetDay(const string et_date)
{
   g_d.et_date   = et_date;
   g_d.or_built  = false;
   g_d.orh = 0; g_d.orl = 0;
   g_d.broke     = false;
   g_d.side      = 0;
   g_d.level     = 0;
   g_d.confirmed = false;
   g_d.done      = false;
   g_d.pend_ticket = 0;
   g_d.filled    = false;
   g_d.entry = 0; g_d.sl0 = 0; g_d.tp = 0; g_d.be_trig = 0; g_d.risk = 0;
   g_d.be_done   = false;
   g_d.fill_time = 0;
}

//+------------------------------------------------------------------+
//| US Eastern DST attivo al tempo GMT dato? (2a dom mar -> 1a dom nov)|
//+------------------------------------------------------------------+
bool UsEastDst(const datetime gmt)
{
   MqlDateTime t; TimeToStruct(gmt, t);
   int y = t.year;
   datetime marSecondSun = NthSundayUtc(y, 3, 2) + 7 * 3600;  // switch ~07:00 UTC
   datetime novFirstSun  = NthSundayUtc(y, 11, 1) + 6 * 3600; // switch ~06:00 UTC
   return (gmt >= marSecondSun && gmt < novFirstSun);
}

datetime NthSundayUtc(const int year, const int month, const int nth)
{
   MqlDateTime f; f.year=year; f.mon=month; f.day=1; f.hour=0; f.min=0; f.sec=0;
   datetime first = StructToTime(f);
   MqlDateTime ff; TimeToStruct(first, ff);
   int dow = ff.day_of_week;                 // 0=domenica
   int firstSunDay = 1 + ((7 - dow) % 7);
   int day = firstSunDay + (nth - 1) * 7;
   MqlDateTime s; s.year=year; s.mon=month; s.day=day; s.hour=0; s.min=0; s.sec=0;
   return StructToTime(s);
}

int EtOffsetSec(const datetime gmt) { return UsEastDst(gmt) ? 4*3600 : 5*3600; }

// ET "wall clock" corrente come MqlDateTime.
void NowEt(MqlDateTime &et)
{
   datetime gmt = TimeGMT();
   datetime etdt = gmt - EtOffsetSec(gmt);
   TimeToStruct(etdt, et);
}

// Converte un orario ET (h:m del giorno ET corrente) in datetime SERVER.
datetime EtTodayToServer(const int h, const int m)
{
   datetime gmt = TimeGMT();
   int etoff = EtOffsetSec(gmt);
   datetime etdt = gmt - etoff;
   MqlDateTime e; TimeToStruct(etdt, e);
   e.hour = h; e.min = m; e.sec = 0;
   datetime et_wall = StructToTime(e);
   long srv_off = (long)TimeCurrent() - (long)TimeGMT();
   return (datetime)((long)et_wall + etoff + srv_off);
}

int EtNowMinutes()
{
   MqlDateTime et; NowEt(et);
   return et.hour * 60 + et.min;
}

// Minuti-del-giorno ET di un timestamp SERVER (per gating della barra chiusa).
int ServerToEtMinutes(const datetime server)
{
   long srv_off = (long)TimeCurrent() - (long)TimeGMT();
   datetime gmt = (datetime)((long)server - srv_off);
   datetime etdt = gmt - EtOffsetSec(gmt);
   MqlDateTime et; TimeToStruct(etdt, et);
   return et.hour * 60 + et.min;
}

//+------------------------------------------------------------------+
void OnTick()
{
   // Nuovo giorno ET -> reset.
   MqlDateTime et; NowEt(et);
   string etdate = StringFormat("%04d-%02d-%02d", et.year, et.mon, et.day);
   if(g_d.et_date != etdate) ResetDay(etdate);

   ManageOpenPosition();  // tick-level: fill/BE/max-hold

   datetime cur = iTime(_Symbol, InpTimeframe, 0);
   if(cur != g_last_bar_time)
   {
      g_last_bar_time = cur;
      OnNewBar();
   }
}

//+------------------------------------------------------------------+
//| Logica a nuova barra M5.                                         |
//+------------------------------------------------------------------+
void OnNewBar()
{
   int etmin = EtNowMinutes();
   int or_end = InpOrEndEtH * 60 + InpOrEndEtM;
   int expiry = InpExpiryEtH * 60 + InpExpiryEtM;

   // 1. Costruisci OR a partire dalle 10:00 ET.
   if(!g_d.or_built && etmin >= or_end)
      BuildOpeningRange();

   // 2. Scadenza pending a 12:00 ET.
   if(g_d.pend_ticket > 0 && etmin >= expiry && !g_d.filled)
   {
      if(OrderSelect(g_d.pend_ticket) && g_trade.OrderDelete(g_d.pend_ticket))
         NotifyTelegram(StringFormat("[EXPIRE] [%s] pending scaduto 12:00 ET", InpStrategyName));
      g_d.pend_ticket = 0;
      g_d.done = true;
   }

   // 3. Break/trail/conferma: valuta l'ULTIMO bar chiuso solo se la SUA ora ET
   //    cade nella sessione 10:00-12:00 (non l'ora attuale: alle 10:00 il bar
   //    chiuso e' quello delle 9:55, ancora nell'OR).
   if(g_d.or_built && !g_d.confirmed && !g_d.done)
   {
      int barEt = ServerToEtMinutes(iTime(_Symbol, InpTimeframe, 1));
      if(barEt >= or_end && barEt < expiry)
         ProcessBreak();
   }
}

//+------------------------------------------------------------------+
//| Calcola ORH/ORL dai bar M5 tra 09:30 e 10:00 ET.                |
//+------------------------------------------------------------------+
void BuildOpeningRange()
{
   datetime srv_start = EtTodayToServer(InpOrStartEtH, InpOrStartEtM);
   datetime srv_end   = EtTodayToServer(InpOrEndEtH,   InpOrEndEtM);
   if(srv_end <= srv_start) return;

   MqlRates r[];
   ArraySetAsSeries(r, false);
   int copied = CopyRates(_Symbol, InpTimeframe, srv_start, srv_end, r);
   if(copied < 3) return;   // dati insufficienti (mercato chiuso/holiday)

   double hi = -DBL_MAX, lo = DBL_MAX;
   for(int i = 0; i < copied; i++)
   {
      if(r[i].time >= srv_end) break;
      if(r[i].high > hi) hi = r[i].high;
      if(r[i].low  < lo) lo = r[i].low;
   }
   if(hi <= -DBL_MAX || lo >= DBL_MAX) return;
   g_d.orh = hi; g_d.orl = lo; g_d.or_built = true;
   PrintFormat("[%s] OR %s ORH=%s ORL=%s", InpStrategyName, g_d.et_date,
               DoubleToString(hi,_Digits), DoubleToString(lo,_Digits));
}

//+------------------------------------------------------------------+
//| Break del primo bar oltre l'OR, trail del level, conferma.       |
//| Valuta l'ULTIMO bar CHIUSO (shift 1).                            |
//+------------------------------------------------------------------+
void ProcessBreak()
{
   double c = iClose(_Symbol, InpTimeframe, 1);
   double h = iHigh(_Symbol, InpTimeframe, 1);
   double l = iLow(_Symbol, InpTimeframe, 1);
   if(c == 0) return;

   if(!g_d.broke)
   {
      if(c < g_d.orl)      { g_d.broke = true; g_d.side = -1; g_d.level = l; }
      else if(c > g_d.orh) { g_d.broke = true; g_d.side = +1; g_d.level = h; }
      return;
   }

   // broke ma non confermato -> trail finche' chiusura oltre level.
   if(g_d.side < 0)  // SELL
   {
      if(c < g_d.level) Confirm();
      else if(l < g_d.level) g_d.level = l;
   }
   else              // BUY
   {
      if(c > g_d.level) Confirm();
      else if(h > g_d.level) g_d.level = h;
   }
}

//+------------------------------------------------------------------+
//| Conferma: filtro ADX, calcolo livelli, piazza pending retest.    |
//+------------------------------------------------------------------+
void Confirm()
{
   g_d.confirmed = true;

   // ADX(14) sull'ultimo bar chiuso (conferma).
   double adxbuf[];
   ArraySetAsSeries(adxbuf, false);
   double adxv = 0.0;
   if(CopyBuffer(g_adx_handle, 0, 1, 1, adxbuf) > 0) adxv = adxbuf[0];
   if(adxv < InpAdxMin)
   {
      g_d.done = true;
      NotifyTelegram(StringFormat("[SKIP] [%s] %s skip: ADX %.1f < %.1f",
         InpStrategyName, g_d.et_date, adxv, InpAdxMin));
      return;
   }

   double entry = NormalizePrice(g_d.level);
   double sl0, tp, be_trig, risk;
   if(g_d.side < 0)  // SELL
   {
      sl0  = NormalizePrice(g_d.orl + InpBufferPoints);
      risk = sl0 - entry;
      tp      = NormalizePrice(entry - InpRR * risk);
      be_trig = entry - InpBeAtR * risk;
   }
   else              // BUY
   {
      sl0  = NormalizePrice(g_d.orh - InpBufferPoints);
      risk = entry - sl0;
      tp      = NormalizePrice(entry + InpRR * risk);
      be_trig = entry + InpBeAtR * risk;
   }
   if(risk <= 0) { g_d.done = true; return; }

   double vol   = ComputeVolume(risk);
   double stops = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   string cm = InpStrategyName;
   bool ok = false;
   ulong ticket = 0;

   // Entry = retest del level -> LIMIT.
   if(g_d.side < 0)  // SELL LIMIT (fill quando il prezzo risale al level)
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      if(entry > bid + stops) { ok = g_trade.SellLimit(vol, entry, _Symbol, sl0, tp, ORDER_TIME_GTC, 0, cm); ticket = ok?g_trade.ResultOrder():0; }
      else                    { ok = g_trade.Sell(vol, _Symbol, 0.0, sl0, tp, cm); }  // gia' oltre -> market
   }
   else              // BUY LIMIT
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      if(entry < ask - stops) { ok = g_trade.BuyLimit(vol, entry, _Symbol, sl0, tp, ORDER_TIME_GTC, 0, cm); ticket = ok?g_trade.ResultOrder():0; }
      else                    { ok = g_trade.Buy(vol, _Symbol, 0.0, sl0, tp, cm); }
   }

   if(ok)
   {
      g_d.pend_ticket = ticket;   // 0 se market (verra' gestito come posizione)
      g_d.entry = entry; g_d.sl0 = sl0; g_d.tp = tp; g_d.be_trig = be_trig; g_d.risk = risk;
      NotifyTelegram(StringFormat("[ORDER] [%s] %s %s | entry %s SL %s TP %s (ADX %.0f) vol %.2f",
         InpStrategyName, g_d.et_date, (g_d.side<0?"SELL":"BUY"),
         DoubleToString(entry,_Digits), DoubleToString(sl0,_Digits),
         DoubleToString(tp,_Digits), adxv, vol));
   }
   else
   {
      g_d.done = true;
      PrintFormat("[%s] conferma: ordine fallito err=%d", InpStrategyName, GetLastError());
   }
}

//+------------------------------------------------------------------+
//| Gestione posizione: fill detect, break-even a +2R, max-hold.     |
//+------------------------------------------------------------------+
void ManageOpenPosition()
{
   ulong pt = 0; double entry=0, sl=0, tp=0; long ptype=-1;
   for(int i = PositionsTotal()-1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      pt = t; entry = PositionGetDouble(POSITION_PRICE_OPEN);
      sl = PositionGetDouble(POSITION_SL); tp = PositionGetDouble(POSITION_TP);
      ptype = PositionGetInteger(POSITION_TYPE);
      break;
   }

   if(pt == 0)
   {
      if(g_d.filled) { g_d.filled = false; NotifyTelegram(StringFormat("[OK] [%s] posizione chiusa", InpStrategyName)); }
      return;
   }

   if(!g_d.filled)
   {
      g_d.filled = true; g_d.pend_ticket = 0; g_d.be_done = false;
      g_d.fill_time = TimeCurrent();
      // usa i livelli calcolati alla conferma (be_trig/risk); se market, entry reale  level
      NotifyTelegram(StringFormat("[FILL] [%s] FILL %s @ %s",
         InpStrategyName, (ptype==POSITION_TYPE_SELL?"SELL":"BUY"), DoubleToString(entry,_Digits)));
   }

   // Break-even a +2R.
   if(!g_d.be_done && g_d.risk > 0)
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      bool hit = (ptype == POSITION_TYPE_SELL) ? (ask <= g_d.be_trig) : (bid >= g_d.be_trig);
      if(hit)
      {
         double be = NormalizePrice(g_d.entry);
         if(g_trade.PositionModify(pt, be, tp))
         {
            g_d.be_done = true;
            NotifyTelegram(StringFormat("[BE] [%s] SL->BE (%s)", InpStrategyName, DoubleToString(be,_Digits)));
         }
      }
   }

   // Max hold.
   if(iBarShift(_Symbol, InpTimeframe, g_d.fill_time) > InpMaxHoldBars)
   {
      if(g_trade.PositionClose(pt))
         NotifyTelegram(StringFormat("[HOLD] [%s] chiusa per max-hold", InpStrategyName));
   }
}

//+------------------------------------------------------------------+
//| Utility (come london_breakout / nxt_fade).                       |
//+------------------------------------------------------------------+
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
