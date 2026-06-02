//+------------------------------------------------------------------+
//|                                          london_breakout.mq5    |
//|                          Trading System Workspace - Stage 2.5   |
//|                                                                  |
//|  Strategia automatica meccanica: rottura del range della         |
//|  sessione asiatica all'apertura di Londra. Versione MQL5         |
//|  della logica Python `strategies/london_breakout/`.              |
//|                                                                  |
//|  Riferimenti edge:                                               |
//|   Osler, "Currency Orders and Exchange-Rate Dynamics", AER 2003. |
//|   Kathy Lien, "Day Trading and Swing Trading the Currency        |
//|     Market", 3rd ed. 2016.                                       |
//|                                                                  |
//|  Logica:                                                         |
//|   00:00-07:00 UTC = costruzione range Asia (high/low di tutte    |
//|     le M15 della sessione).                                      |
//|   07:00 UTC = piazzamento di DUE stop orders:                    |
//|     buy_stop  = high + breakout_buffer_atr × ATR(14, D1)         |
//|     sell_stop = low  - breakout_buffer_atr × ATR(14, D1)         |
//|     SL = lato opposto del range.                                 |
//|     TP = 1.5R (configurabile).                                   |
//|   07:00-10:00 UTC = finestra di entry. Dopo cancella i pendenti. |
//|   16:00 UTC = time stop: chiude posizioni residue.               |
//|                                                                  |
//|  Filtri:                                                         |
//|   - skip se range Asia >= max_range_to_atr_ratio × ATR_D1        |
//|   - skip primo venerdì del mese (NFP)                            |
//|   - skip se data UTC è in fomc_blackout_dates_csv                |
//+------------------------------------------------------------------+
#property copyright "Trading System Workspace"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>

#include <TradingSystemWorkspace/telegram.mqh>
#include <TradingSystemWorkspace/helpers.mqh>

//+------------------------------------------------------------------+
//| Inputs (esposti nel dialog dell'EA)                              |
//+------------------------------------------------------------------+

input group "=== Sessioni ==="
input int    InpAsiaStartHourUtc      = 0;     // Inizio sessione Asia (UTC)
input int    InpAsiaStartMinUtc       = 0;
input int    InpAsiaEndHourUtc        = 7;     // Fine sessione Asia / piazzamento ordini
input int    InpAsiaEndMinUtc         = 0;
input int    InpEntryWindowEndHourUtc = 10;    // Cancellazione ordini non scattati
input int    InpEntryWindowEndMinUtc  = 0;
input int    InpTimeStopHourUtc       = 16;    // Chiusura forzata posizioni
input int    InpTimeStopMinUtc        = 0;

input group "=== Soglie ==="
input double InpBreakoutBufferAtr     = 0.10;  // Buffer (frazione di ATR_D1)
input double InpTpRMultiple           = 1.5;   // TP come multiplo di R (usato in FIXED_RR e PARTIAL_TRAIL)
input double InpMaxRangeToAtrRatio    = 1.5;   // Skip se range >= ratio × ATR_D1
input int    InpAtrPeriod             = 14;    // ATR periodi (su D1)

input group "=== Exit mode (A/B/C in parallelo su account demo distinti) ==="
// FIXED_RR     = baseline: TP fisso a InpTpRMultiple × R (variante A).
// PARTIAL_TRAIL= TP parziale 50% a 1R, trailing ATR(M15)·InpTrailAtrMult sul resto (B).
// FULL_TRAIL   = no TP fisso; trailing ATR(M15)·InpTrailAtrMult dall'apertura (C).
input int    InpExitMode              = 0;     // 0=FIXED_RR, 1=PARTIAL_TRAIL, 2=FULL_TRAIL
input double InpPartialAtR            = 1.0;   // R-multiplo del partial close (PARTIAL_TRAIL)
input double InpPartialFraction       = 0.5;   // Frazione di volume chiusa al partial (0..1)
input int    InpTrailAtrPeriod        = 14;    // Periodi ATR per trailing (M15)
input double InpTrailAtrMult          = 1.5;   // Distanza trailing = mult × ATR_M15

input group "=== Filtri eventi ==="
input bool   InpSkipNfp               = true;  // Skip primo venerdì del mese
input string InpFomcBlackoutDatesCsv  =        // YYYY-MM-DD separati da ","
   "2026-05-13,2026-06-17,2026-07-29,2026-09-16,2026-11-04,2026-12-16";

input group "=== Sizing (fixed fractional) ==="
input double InpRiskPerTradePct       = 0.01;  // % equity rischiata per trade (0.01 = 1%)
input double InpFallbackVolume        = 0.10;  // Lotti di fallback se sizing fallisce

input group "=== Telegram (opzionale) ==="
input string InpTelegramBotToken      = "";    // Vuoto → niente Telegram
input string InpTelegramChatId        = "";

input group "=== Identificazione ==="
input ulong  InpMagicNumber           = 26050; // Magic number per riconoscere ordini propri
input string InpStrategyName          = "london_breakout";

//+------------------------------------------------------------------+
//| Stato persistente del giorno corrente                            |
//+------------------------------------------------------------------+
struct DayState
{
   string   iso_date;          // "YYYY-MM-DD" del giorno corrente
   bool     plan_built;        // ordini già piazzati per oggi (anche se skip)
   ulong    buy_ticket;        // ticket pending buy_stop
   ulong    sell_ticket;       // ticket pending sell_stop
   bool     one_side_filled;   // una posizione si è aperta
   // Stato per PARTIAL_TRAIL / FULL_TRAIL:
   bool     partial_done;      // true dopo aver chiuso la quota parziale a 1R
   double   entry_price;       // prezzo medio di apertura (long o short)
   double   initial_risk;      // |entry - SL| iniziale, usato per il partial trigger
   long     position_type;     // POSITION_TYPE_BUY / POSITION_TYPE_SELL
   double   current_sl;        // SL corrente (potenzialmente trailato)
};

DayState g_day = { "", false, 0, 0, false, false, 0.0, 0.0, -1, 0.0 };
CTrade   g_trade;
string   g_fomc_dates[];

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_trade.SetDeviationInPoints(20);

   // Parse della lista FOMC.
   StringSplit(InpFomcBlackoutDatesCsv, ',', g_fomc_dates);
   for(int i=0; i<ArraySize(g_fomc_dates); i++)
   {
      g_fomc_dates[i] = TrimSpaces(g_fomc_dates[i]);
   }

   PrintFormat("[%s] EA avviato. Magic=%I64u Symbol=%s",
               InpStrategyName, InpMagicNumber, _Symbol);

   if(StringLen(InpTelegramBotToken) > 0 && StringLen(InpTelegramChatId) > 0)
   {
      string msg = StringFormat(
         "🚀 [%s] EA avviato su %s",
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
   PrintFormat("[%s] EA fermato (reason=%d)", InpStrategyName, reason);
   if(StringLen(InpTelegramBotToken) > 0 && StringLen(InpTelegramChatId) > 0)
   {
      string msg = StringFormat("🛑 [%s] EA fermato su %s (reason=%d)",
                                InpStrategyName, _Symbol, reason);
      TG_SendMessage(InpTelegramBotToken, InpTelegramChatId, msg);
   }
}

//+------------------------------------------------------------------+
//| OnTick — chiamato a ogni nuovo tick                              |
//+------------------------------------------------------------------+
void OnTick()
{
   datetime now = TimeCurrent();
   string today = H_DateIso(now);

   // Reset stato a nuovo giorno UTC.
   if(g_day.iso_date != today)
   {
      g_day.iso_date        = today;
      g_day.plan_built      = false;
      g_day.buy_ticket      = 0;
      g_day.sell_ticket     = 0;
      g_day.one_side_filled = false;
      g_day.partial_done    = false;
      g_day.entry_price     = 0.0;
      g_day.initial_risk    = 0.0;
      g_day.position_type   = -1;
      g_day.current_sl      = 0.0;
   }

   // 1. Time stop: chiudi posizioni aperte oltre l'orario.
   if(H_AfterTime(now, InpTimeStopHourUtc, InpTimeStopMinUtc))
   {
      MaybeCloseOnTimeStop();
   }

   // 2. Cancella pendenti se finestra chiusa e nessun fill.
   if(H_AfterTime(now, InpEntryWindowEndHourUtc, InpEntryWindowEndMinUtc)
      && !g_day.one_side_filled)
   {
      CancelPendingIfAny(/*keep_filled=*/"");
   }

   // 3. Se uno dei due si è fillato → cancella l'altro.
   if(!g_day.one_side_filled && DetectFill())
   {
      g_day.one_side_filled = true;
      CancelOrphanedAfterFill();
   }

   // 3b. Gestione exit avanzati per PARTIAL_TRAIL e FULL_TRAIL.
   if(g_day.one_side_filled && InpExitMode != 0)
   {
      ManageActivePositionExits();
   }

   // 4. Build piano se siamo nella finestra entry e non ancora costruito.
   if(!g_day.plan_built && InEntryWindow(now))
   {
      TryBuildAndPlace(now);
   }
}

//+------------------------------------------------------------------+
//| Helper: siamo in [asia_end, entry_window_end) UTC?               |
//+------------------------------------------------------------------+
bool InEntryWindow(const datetime now)
{
   return H_InTimeWindow(now,
                         InpAsiaEndHourUtc, InpAsiaEndMinUtc,
                         InpEntryWindowEndHourUtc, InpEntryWindowEndMinUtc);
}

//+------------------------------------------------------------------+
//| Costruisce piano e piazza i due stop orders.                     |
//+------------------------------------------------------------------+
void TryBuildAndPlace(const datetime now)
{
   // 1. Range Asia.
   double asia_high = 0, asia_low = 0;
   bool ok = H_TodayRangeUtc(_Symbol, PERIOD_M15,
                             InpAsiaStartHourUtc, InpAsiaStartMinUtc,
                             InpAsiaEndHourUtc, InpAsiaEndMinUtc,
                             asia_high, asia_low);
   if(!ok)
   {
      PrintFormat("[%s] Range Asia non disponibile per %s.", InpStrategyName, _Symbol);
      return;
   }

   // 2. ATR D1.
   double atr_d1 = H_ATR(_Symbol, PERIOD_D1, InpAtrPeriod);
   if(atr_d1 <= 0)
   {
      PrintFormat("[%s] ATR D1 non disponibile.", InpStrategyName);
      return;
   }

   double range_width = asia_high - asia_low;

   // 3. Filtro range esaurito.
   if(range_width >= InpMaxRangeToAtrRatio * atr_d1)
   {
      g_day.plan_built = true;
      string msg = StringFormat(
         "⏭ %s skip: range %.5f >= %.2f × ATR_D1 %.5f",
         _Symbol, range_width, InpMaxRangeToAtrRatio, atr_d1);
      PrintFormat("[%s] %s", InpStrategyName, msg);
      NotifyTelegram(msg);
      return;
   }

   // 4. Filtro NFP/FOMC.
   if(IsBlackoutDay(now))
   {
      g_day.plan_built = true;
      string msg = StringFormat("⏭ %s skip: giorno NFP/FOMC %s",
                                _Symbol, g_day.iso_date);
      PrintFormat("[%s] %s", InpStrategyName, msg);
      NotifyTelegram(msg);
      return;
   }

   // 5. Calcolo stop orders.
   double buffer    = InpBreakoutBufferAtr * atr_d1;
   double buy_entry = NormalizePrice(asia_high + buffer);
   double sell_entry= NormalizePrice(asia_low  - buffer);
   double buy_sl    = NormalizePrice(asia_low);
   double sell_sl   = NormalizePrice(asia_high);
   double risk_long = buy_entry - buy_sl;
   double risk_short= sell_sl - sell_entry;

   if(risk_long <= 0 || risk_short <= 0)
   {
      PrintFormat("[%s] Risk non valido (long=%.5f short=%.5f). Skip.",
                  InpStrategyName, risk_long, risk_short);
      return;
   }

   // TP fisso solo in FIXED_RR e PARTIAL_TRAIL (in PARTIAL_TRAIL serve come
   // anchor del partial close); in FULL_TRAIL non lo settiamo (0 = nessun TP).
   double buy_tp  = 0.0;
   double sell_tp = 0.0;
   if(InpExitMode == 0)
   {
      // FIXED_RR
      buy_tp  = NormalizePrice(buy_entry  + InpTpRMultiple * risk_long);
      sell_tp = NormalizePrice(sell_entry - InpTpRMultiple * risk_short);
   }
   else if(InpExitMode == 1)
   {
      // PARTIAL_TRAIL — il partial close è gestito dinamicamente, ma settiamo
      // comunque un TP "sicurezza" molto largo (= 5R) per evitare posizioni
      // infinite in caso di crash dell'EA.
      buy_tp  = NormalizePrice(buy_entry  + 5.0 * risk_long);
      sell_tp = NormalizePrice(sell_entry - 5.0 * risk_short);
   }
   // InpExitMode == 2 (FULL_TRAIL) → no TP.

   // 6. Sizing.
   double volume = ComputeVolume(risk_long);

   // 7. Piazzamento.
   // Il `comment` dell'ordine viene scritto nella colonna Comment della
   // history MT5 → riconoscibilità immediata della variante senza dover
   // guardare il magic. InpStrategyName è settabile per istanza dell'EA
   // (es. "LB_FIXED_RR", "LB_PARTIAL_TRAIL", "LB_FULL_TRAIL").
   string order_comment = InpStrategyName;
   bool buy_ok  = g_trade.BuyStop(volume, buy_entry, _Symbol, buy_sl, buy_tp,
                                  ORDER_TIME_GTC, 0, order_comment);
   ulong buy_ticket = (buy_ok ? g_trade.ResultOrder() : 0);

   bool sell_ok = g_trade.SellStop(volume, sell_entry, _Symbol, sell_sl, sell_tp,
                                   ORDER_TIME_GTC, 0, order_comment);
   ulong sell_ticket = (sell_ok ? g_trade.ResultOrder() : 0);

   if(!buy_ok || !sell_ok)
   {
      PrintFormat("[%s] Errore piazzamento. buy_ok=%s sell_ok=%s last_err=%d",
                  InpStrategyName,
                  (string)buy_ok, (string)sell_ok,
                  GetLastError());
      // Cancella eventuale ordine già piazzato per evitare disallineamento
      if(buy_ok)  g_trade.OrderDelete(buy_ticket);
      if(sell_ok) g_trade.OrderDelete(sell_ticket);
      return;
   }

   g_day.plan_built  = true;
   g_day.buy_ticket  = buy_ticket;
   g_day.sell_ticket = sell_ticket;

   string exit_label = (InpExitMode == 0 ? "FIXED_RR" :
                        (InpExitMode == 1 ? "PARTIAL_TRAIL" : "FULL_TRAIL"));
   string msg = StringFormat(
      "📌 London Breakout %s %s [%s]\nrange %.5f, buffer %.5f, TP_anchor %.1fR\n"
      "BUY  stop @ %s SL %s TP %s\n"
      "SELL stop @ %s SL %s TP %s\nvol=%.2f",
      _Symbol, g_day.iso_date, exit_label, range_width, buffer, InpTpRMultiple,
      DoubleToString(buy_entry,  _Digits),
      DoubleToString(buy_sl,     _Digits),
      DoubleToString(buy_tp,     _Digits),
      DoubleToString(sell_entry, _Digits),
      DoubleToString(sell_sl,    _Digits),
      DoubleToString(sell_tp,    _Digits),
      volume);
   PrintFormat("[%s] %s", InpStrategyName, msg);
   NotifyTelegram(msg);
}

//+------------------------------------------------------------------+
//| Sizing fixed fractional: `risk_pct` di equity / risk_price.      |
//+------------------------------------------------------------------+
double ComputeVolume(const double risk_price)
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= 0 || risk_price <= 0) return InpFallbackVolume;

   double risk_money = equity * InpRiskPerTradePct;

   // Conversione "punto monetario" per 1 lotto.
   double tick_size  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tick_size <= 0 || tick_value <= 0) return InpFallbackVolume;

   double money_per_unit = (risk_price / tick_size) * tick_value;
   if(money_per_unit <= 0) return InpFallbackVolume;

   double raw = risk_money / money_per_unit;

   // Round al lotto step minimo.
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
//| Verifica giornata di blackout (NFP primo venerdì + FOMC list).   |
//+------------------------------------------------------------------+
bool IsBlackoutDay(const datetime d)
{
   if(InpSkipNfp && H_IsFirstFridayOfMonth(d)) return true;
   if(H_IsoDateInList(g_day.iso_date, g_fomc_dates)) return true;
   return false;
}

//+------------------------------------------------------------------+
//| Detect fill: c'è una posizione aperta con il nostro magic?       |
//+------------------------------------------------------------------+
bool DetectFill()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| Cancella i pendenti del giorno se ancora attivi.                 |
//| `keep_filled` = "buy" o "sell" se uno dei due si è fillato.      |
//+------------------------------------------------------------------+
void CancelPendingIfAny(const string keep_filled)
{
   if(g_day.buy_ticket  > 0 && keep_filled != "buy")
   {
      if(OrderSelect(g_day.buy_ticket))
      {
         g_trade.OrderDelete(g_day.buy_ticket);
      }
      g_day.buy_ticket = 0;
   }
   if(g_day.sell_ticket > 0 && keep_filled != "sell")
   {
      if(OrderSelect(g_day.sell_ticket))
      {
         g_trade.OrderDelete(g_day.sell_ticket);
      }
      g_day.sell_ticket = 0;
   }
}

//+------------------------------------------------------------------+
//| Quando una posizione si fila, cancella l'altro pendente.         |
//+------------------------------------------------------------------+
void CancelOrphanedAfterFill()
{
   string side = "";
   for(int i=0; i<PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      side = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? "buy" : "sell";
      break;
   }
   CancelPendingIfAny(side);
   if(side != "")
   {
      double fill_price = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl_price   = PositionGetDouble(POSITION_SL);
      string direction  = (side == "buy") ? "BUY" : "SELL";

      // Cache stato per la gestione trailing/partial.
      g_day.entry_price   = fill_price;
      g_day.current_sl    = sl_price;
      g_day.position_type = (side == "buy") ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;
      g_day.initial_risk  = MathAbs(fill_price - sl_price);
      g_day.partial_done  = false;

      string msg = TG_FormatFill(InpStrategyName, _Symbol, direction, fill_price);
      PrintFormat("[%s] %s", InpStrategyName, msg);
      NotifyTelegram(msg);
   }
}

//+------------------------------------------------------------------+
//| ManageActivePositionExits — chiamato a ogni tick quando una      |
//| posizione è aperta e InpExitMode != FIXED_RR.                    |
//|                                                                  |
//| PARTIAL_TRAIL (1): se non ancora fatto, chiudi `InpPartialFraction|
//|   del volume al raggiungimento di InpPartialAtR × initial_risk;  |
//|   poi trailing ATR(M15)·InpTrailAtrMult sul resto.               |
//| FULL_TRAIL (2): trailing ATR(M15)·InpTrailAtrMult dal fill.      |
//+------------------------------------------------------------------+
void ManageActivePositionExits()
{
   if(g_day.initial_risk <= 0 || g_day.entry_price <= 0) return;

   // Trova la posizione attiva.
   ulong pos_ticket = 0;
   double pos_volume = 0;
   double pos_tp = 0;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      pos_ticket = t;
      pos_volume = PositionGetDouble(POSITION_VOLUME);
      // Cattura il TP ORA che la posizione è selezionata: dopo una
      // PositionClosePartial la selezione decade e PositionGetDouble
      // tornerebbe 0, cancellando di fatto il TP nella PositionModify.
      // La parziale preserva il TP sul residuo, quindi questo valore resta
      // valido per entrambi i rami sotto.
      pos_tp = PositionGetDouble(POSITION_TP);
      break;
   }
   if(pos_ticket == 0) return;  // posizione chiusa (TP/SL)

   bool is_long = (g_day.position_type == POSITION_TYPE_BUY);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double mark = is_long ? bid : ask;

   // === Partial close (solo PARTIAL_TRAIL) ===
   if(InpExitMode == 1 && !g_day.partial_done)
   {
      double trigger = is_long
         ? g_day.entry_price + InpPartialAtR * g_day.initial_risk
         : g_day.entry_price - InpPartialAtR * g_day.initial_risk;
      bool hit = is_long ? (mark >= trigger) : (mark <= trigger);
      if(hit)
      {
         double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
         double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
         if(step <= 0) step = 0.01;
         double close_vol = MathFloor((pos_volume * InpPartialFraction) / step) * step;
         if(close_vol >= vmin && close_vol < pos_volume)
         {
            if(g_trade.PositionClosePartial(pos_ticket, close_vol))
            {
               g_day.partial_done = true;
               // BE shift: SL al breakeven sulla parte residua.
               double new_sl = NormalizePrice(g_day.entry_price);
               g_trade.PositionModify(pos_ticket, new_sl, pos_tp);
               g_day.current_sl = new_sl;

               string msg = StringFormat(
                  "✂ %s partial close %.2f @ %s (≈%.1fR), SL→BE %s",
                  _Symbol, close_vol, DoubleToString(mark, _Digits),
                  InpPartialAtR, DoubleToString(new_sl, _Digits));
               PrintFormat("[%s] %s", InpStrategyName, msg);
               NotifyTelegram(msg);
            }
         }
      }
   }

   // === Trailing stop (PARTIAL_TRAIL dopo partial, oppure FULL_TRAIL sempre) ===
   bool do_trail = (InpExitMode == 2) ||
                   (InpExitMode == 1 && g_day.partial_done);
   if(do_trail)
   {
      double atr_m15 = H_ATR(_Symbol, PERIOD_M15, InpTrailAtrPeriod);
      if(atr_m15 <= 0) return;
      double trail_dist = InpTrailAtrMult * atr_m15;
      double candidate_sl = is_long ? (mark - trail_dist) : (mark + trail_dist);
      candidate_sl = NormalizePrice(candidate_sl);

      // Solo mosse favorevoli al PnL (SL non torna mai indietro).
      bool improving = is_long
         ? (candidate_sl > g_day.current_sl)
         : (candidate_sl < g_day.current_sl || g_day.current_sl == 0.0);
      if(improving)
      {
         if(g_trade.PositionModify(pos_ticket, candidate_sl, pos_tp))
         {
            g_day.current_sl = candidate_sl;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Time-stop: chiudi posizioni residue.                             |
//+------------------------------------------------------------------+
void MaybeCloseOnTimeStop()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagicNumber) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;

      string direction = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? "BUY" : "SELL";
      bool ok = g_trade.PositionClose(ticket);
      if(ok)
      {
         string msg = TG_FormatInfo(InpStrategyName, _Symbol,
                                    "⏰ Time stop: posizione " + direction + " chiusa");
         PrintFormat("[%s] %s", InpStrategyName, msg);
         NotifyTelegram(msg);
      }
   }
   // Cancella eventuali pendenti rimasti (caso edge)
   CancelPendingIfAny("");
}

//+------------------------------------------------------------------+
//| Helper: arrotonda al tick del simbolo.                           |
//+------------------------------------------------------------------+
double NormalizePrice(const double price)
{
   double tick = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tick <= 0) return NormalizeDouble(price, _Digits);
   double normalized = MathRound(price / tick) * tick;
   return NormalizeDouble(normalized, _Digits);
}

//+------------------------------------------------------------------+
//| Trim spazi da una stringa.                                       |
//+------------------------------------------------------------------+
string TrimSpaces(const string s)
{
   string out = s;
   StringTrimLeft(out);
   StringTrimRight(out);
   return out;
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
