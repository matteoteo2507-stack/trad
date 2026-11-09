//+------------------------------------------------------------------+
//|                                                 tsmom_jpy.mq5    |
//|                          Trading System Workspace - Stage 2.6   |
//|                                                                  |
//|  Time Series Momentum (Moskowitz-Ooi-Pedersen 2012) su D1.       |
//|  Porting MQL5 della logica Python `strategies/tsmom/`.           |
//|                                                                  |
//|  Riferimenti edge:                                               |
//|   Moskowitz, Ooi, Pedersen (2012) "Time Series Momentum", JFE.   |
//|   Hurst, Ooi, Pedersen (2017) "A Century of Evidence on Trend-   |
//|     Following Investing", AQR.                                   |
//|   Harvey, Hoyle, Korgaonkar (2018) "The Impact of Volatility     |
//|     Targeting", JPM (sizing vol-target).                         |
//|                                                                  |
//|  Logica (valutata UNA volta a ogni nuova barra D1):              |
//|   s_long = sign(close[1] - close[1 + L])         L = 252         |
//|   s_fast = sign(EMA(close,fast)[1] - EMA(close,slow)[1])         |
//|   pos    = s_long  se s_long == s_fast,  altrimenti 0 (flat)     |
//|                                                                  |
//|   Entry: a mercato all'apertura della nuova barra quando `pos`   |
//|     cambia rispetto alla posizione corrente.                     |
//|   Stop:  entry ± atr_mult × ATR(atr_period, D1). Niente TP.      |
//|   Exit:  signal flip (chiusura a mercato) oppure SL colpito.     |
//|                                                                  |
//|  Sizing vol-target:                                              |
//|   size_factor = vol_target_annual / realized_vol_60d_annual      |
//|                 (cap a size_cap_mult)                            |
//|   risk_money  = equity × account_risk_pct × size_factor          |
//|   volume      = risk_money / (sl_dist convertito in $/lotto)     |
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

input group "=== Signal ==="
input int    InpLookbackLongBars   = 252;    // Lookback momentum lungo (barre D1)
input int    InpEwmaFast           = 20;     // Span EMA veloce
input int    InpEwmaSlow           = 60;     // Span EMA lenta

input group "=== Stop loss ==="
input int    InpAtrPeriod          = 20;     // Periodi ATR (D1)
input double InpAtrMult            = 3.0;    // SL = entry ± mult × ATR

input group "=== Sizing (vol-target) ==="
input double InpVolTargetAnnual    = 0.15;   // Vol annua target del singolo asset
input int    InpRealizedVolWindow  = 60;     // Barre D1 per la realized vol
input double InpAccountRiskPct     = 0.01;   // Frazione equity a rischio se realized = target
input double InpSizeCapMult        = 3.0;    // Cap al size_factor (anti-leva)
input double InpFallbackVolume     = 0.10;   // Lotti di fallback se sizing fallisce

input group "=== Storico minimo ==="
input int    InpMinHistoryBars     = 312;    // 252 + 60: sotto questo, skip

input group "=== Telegram (opzionale) ==="
input string InpTelegramBotToken   = "";     // Vuoto → niente Telegram
input string InpTelegramChatId     = "";

input group "=== Identificazione ==="
input ulong  InpMagicNumber        = 26060;  // Magic number ordini propri
input string InpStrategyName       = "tsmom_jpy";

//+------------------------------------------------------------------+
//| Stato globale                                                    |
//+------------------------------------------------------------------+
CTrade   g_trade;
int      g_ema_fast_handle = INVALID_HANDLE;
int      g_ema_slow_handle = INVALID_HANDLE;
datetime g_last_eval_bar   = 0;   // ultima barra D1 valutata (anti doppia valutazione)

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_trade.SetDeviationInPoints(20);

   g_ema_fast_handle = iMA(_Symbol, PERIOD_D1, InpEwmaFast, 0, MODE_EMA, PRICE_CLOSE);
   g_ema_slow_handle = iMA(_Symbol, PERIOD_D1, InpEwmaSlow, 0, MODE_EMA, PRICE_CLOSE);
   if(g_ema_fast_handle == INVALID_HANDLE || g_ema_slow_handle == INVALID_HANDLE)
   {
      PrintFormat("[%s] iMA handle non creato (fast=%d slow=%d).",
                  InpStrategyName, g_ema_fast_handle, g_ema_slow_handle);
      return INIT_FAILED;
   }

   PrintFormat("[%s] EA avviato. Magic=%I64u Symbol=%s TF=D1",
               InpStrategyName, InpMagicNumber, _Symbol);

   if(StringLen(InpTelegramBotToken) > 0 && StringLen(InpTelegramChatId) > 0)
   {
      string msg = StringFormat("🚀 [%s] EA avviato su %s (D1, TSMOM)",
                                InpStrategyName, _Symbol);
      TG_SendMessage(InpTelegramBotToken, InpTelegramChatId, msg);
   }
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| OnDeinit                                                         |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(g_ema_fast_handle != INVALID_HANDLE) IndicatorRelease(g_ema_fast_handle);
   if(g_ema_slow_handle != INVALID_HANDLE) IndicatorRelease(g_ema_slow_handle);

   PrintFormat("[%s] EA fermato (reason=%d)", InpStrategyName, reason);
   if(StringLen(InpTelegramBotToken) > 0 && StringLen(InpTelegramChatId) > 0)
   {
      string msg = StringFormat("🛑 [%s] EA fermato su %s (reason=%d)",
                                InpStrategyName, _Symbol, reason);
      TG_SendMessage(InpTelegramBotToken, InpTelegramChatId, msg);
   }
}

//+------------------------------------------------------------------+
//| OnTick — agisce UNA volta per nuova barra D1                     |
//+------------------------------------------------------------------+
void OnTick()
{
   datetime cur_bar = iTime(_Symbol, PERIOD_D1, 0);
   if(cur_bar == 0 || cur_bar == g_last_eval_bar)
      return;  // nessuna nuova barra D1 → niente da fare

   // Storico sufficiente?
   if(Bars(_Symbol, PERIOD_D1) < InpMinHistoryBars)
   {
      PrintFormat("[%s] Storico D1 insufficiente (%d < %d). Skip.",
                  InpStrategyName, Bars(_Symbol, PERIOD_D1), InpMinHistoryBars);
      g_last_eval_bar = cur_bar;
      return;
   }

   g_last_eval_bar = cur_bar;
   EvaluateAndTrade();
}

//+------------------------------------------------------------------+
//| Valutazione del segnale e gestione posizione.                    |
//+------------------------------------------------------------------+
void EvaluateAndTrade()
{
   int desired = ComputeDesiredPosition();
   if(desired == INT_MIN)
      return;  // dati non disponibili: non tocchiamo nulla

   int current = CurrentPositionDir();

   if(desired == current)
      return;  // nessun cambio: hold

   // 1. Signal flip o uscita verso flat → chiudi la posizione corrente.
   if(current != 0)
   {
      CloseOwnPosition("signal flip");
   }

   // 2. Nuova direzione → apri a mercato con SL = entry ± mult×ATR, no TP.
   if(desired != 0)
   {
      OpenPosition(desired);
   }
}

//+------------------------------------------------------------------+
//| ComputeDesiredPosition: +1 / -1 / 0. INT_MIN se dati mancanti.   |
//+------------------------------------------------------------------+
int ComputeDesiredPosition()
{
   // --- s_long = sign(close[1] - close[1 + L]) ---
   int need = InpLookbackLongBars + 1;          // serve fino a shift (1+L)
   double closes[];
   ArraySetAsSeries(closes, true);
   if(CopyClose(_Symbol, PERIOD_D1, 1, need + 1, closes) < need + 1)
   {
      PrintFormat("[%s] CopyClose insufficiente per s_long.", InpStrategyName);
      return INT_MIN;
   }
   double close_1   = closes[0];                 // barra appena chiusa (shift 1)
   double close_1pL = closes[InpLookbackLongBars];
   int s_long = Sgn(close_1 - close_1pL);

   // --- s_fast = sign(EMA_fast[1] - EMA_slow[1]) ---
   double ef[], es[];
   ArraySetAsSeries(ef, true);
   ArraySetAsSeries(es, true);
   if(CopyBuffer(g_ema_fast_handle, 0, 1, 1, ef) < 1 ||
      CopyBuffer(g_ema_slow_handle, 0, 1, 1, es) < 1)
   {
      PrintFormat("[%s] CopyBuffer EMA non pronto.", InpStrategyName);
      return INT_MIN;
   }
   int s_fast = Sgn(ef[0] - es[0]);

   // pos = s_long se concorde con s_fast, altrimenti flat.
   return (s_long == s_fast) ? s_long : 0;
}

//+------------------------------------------------------------------+
//| Direzione della posizione propria corrente: +1 / -1 / 0.         |
//+------------------------------------------------------------------+
int CurrentPositionDir()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      return (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? 1 : -1;
   }
   return 0;
}

//+------------------------------------------------------------------+
//| Chiude la posizione propria (se esiste).                         |
//+------------------------------------------------------------------+
void CloseOwnPosition(const string reason)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;

      string dir = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? "BUY" : "SELL";
      if(g_trade.PositionClose(ticket))
      {
         string msg = TG_FormatInfo(InpStrategyName, _Symbol,
                                    StringFormat("↩ Exit %s (%s)", dir, reason));
         PrintFormat("[%s] %s", InpStrategyName, msg);
         NotifyTelegram(msg);
      }
      else
      {
         PrintFormat("[%s] PositionClose fallita ticket=%I64u err=%d",
                     InpStrategyName, ticket, GetLastError());
      }
   }
}

//+------------------------------------------------------------------+
//| Apre a mercato nella direzione data (+1 long / -1 short).        |
//+------------------------------------------------------------------+
void OpenPosition(const int dir)
{
   double atr_d1 = H_ATR(_Symbol, PERIOD_D1, InpAtrPeriod);
   if(atr_d1 <= 0)
   {
      PrintFormat("[%s] ATR D1 non disponibile. Skip apertura.", InpStrategyName);
      return;
   }
   double sl_dist = InpAtrMult * atr_d1;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double entry = (dir > 0) ? ask : bid;
   double sl    = NormalizePrice((dir > 0) ? entry - sl_dist : entry + sl_dist);

   double volume = ComputeVolumeVolTarget(sl_dist);
   if(volume <= 0)
   {
      PrintFormat("[%s] Volume nullo. Skip apertura.", InpStrategyName);
      return;
   }

   bool ok;
   if(dir > 0)
      ok = g_trade.Buy(volume, _Symbol, 0.0, sl, 0.0, InpStrategyName);
   else
      ok = g_trade.Sell(volume, _Symbol, 0.0, sl, 0.0, InpStrategyName);

   if(!ok)
   {
      PrintFormat("[%s] Apertura %s fallita err=%d", InpStrategyName,
                  (dir > 0 ? "BUY" : "SELL"), GetLastError());
      return;
   }

   double fill = g_trade.ResultPrice();
   string direction = (dir > 0) ? "BUY" : "SELL";
   string msg = StringFormat(
      "📌 TSMOM %s %s @ %s\nSL %s (%.1f×ATR=%.5f)\nvol=%.2f",
      _Symbol, direction,
      DoubleToString(fill > 0 ? fill : entry, _Digits),
      DoubleToString(sl, _Digits), InpAtrMult, sl_dist, volume);
   PrintFormat("[%s] %s", InpStrategyName, msg);
   NotifyTelegram(msg);
}

//+------------------------------------------------------------------+
//| Sizing vol-target: lotti per rischiare risk_pct×size_factor.     |
//+------------------------------------------------------------------+
double ComputeVolumeVolTarget(const double sl_dist)
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= 0 || sl_dist <= 0) return InpFallbackVolume;

   double size_factor = ComputeSizeFactor();
   if(size_factor <= 0) return 0.0;  // vol non stimabile → niente trade

   double risk_money = equity * InpAccountRiskPct * size_factor;

   double tick_size  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tick_size <= 0 || tick_value <= 0) return InpFallbackVolume;

   double money_per_unit = (sl_dist / tick_size) * tick_value;
   if(money_per_unit <= 0) return InpFallbackVolume;

   double raw = risk_money / money_per_unit;

   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0) step = 0.01;

   double v = MathFloor(raw / step) * step;
   if(v < vmin) v = vmin;
   if(vmax > 0 && v > vmax) v = vmax;
   return v;
}

//+------------------------------------------------------------------+
//| size_factor = vol_target / realized_vol_annual (cap). 0 se n/d.  |
//+------------------------------------------------------------------+
double ComputeSizeFactor()
{
   int w = InpRealizedVolWindow;
   double closes[];
   ArraySetAsSeries(closes, true);
   // Servono w+1 chiusure (a partire da shift 1) per w rendimenti.
   if(CopyClose(_Symbol, PERIOD_D1, 1, w + 1, closes) < w + 1)
      return 0.0;

   // Rendimenti semplici giornalieri r[i] = closes[i]/closes[i+1] - 1.
   double mean = 0.0;
   double rets[];
   ArrayResize(rets, w);
   for(int i = 0; i < w; i++)
   {
      double prev = closes[i + 1];
      rets[i] = (prev != 0.0) ? (closes[i] / prev - 1.0) : 0.0;
      mean += rets[i];
   }
   mean /= w;

   // Deviazione standard campionaria (ddof=1), come nel codice Python.
   double ss = 0.0;
   for(int i = 0; i < w; i++)
   {
      double d = rets[i] - mean;
      ss += d * d;
   }
   if(w <= 1) return 0.0;
   double std_daily = MathSqrt(ss / (w - 1));
   double realized_vol_annual = std_daily * MathSqrt(252.0);
   if(realized_vol_annual <= 0.0) return 0.0;

   double factor = InpVolTargetAnnual / realized_vol_annual;
   if(factor > InpSizeCapMult) factor = InpSizeCapMult;
   return factor;
}

//+------------------------------------------------------------------+
//| Segno: +1 / -1 / 0.                                              |
//+------------------------------------------------------------------+
int Sgn(const double x)
{
   if(x > 0.0) return 1;
   if(x < 0.0) return -1;
   return 0;
}

//+------------------------------------------------------------------+
//| Arrotonda al tick del simbolo.                                   |
//+------------------------------------------------------------------+
double NormalizePrice(const double price)
{
   double tick = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tick <= 0) return NormalizeDouble(price, _Digits);
   double normalized = MathRound(price / tick) * tick;
   return NormalizeDouble(normalized, _Digits);
}

//+------------------------------------------------------------------+
//| Wrapper Telegram: no-op se token o chat_id vuoti.                |
//+------------------------------------------------------------------+
void NotifyTelegram(const string text)
{
   if(StringLen(InpTelegramBotToken) == 0 || StringLen(InpTelegramChatId) == 0)
      return;
   TG_SendMessage(InpTelegramBotToken, InpTelegramChatId, text);
}
//+------------------------------------------------------------------+
