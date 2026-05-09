//+------------------------------------------------------------------+
//|                                                     helpers.mqh  |
//|  Funzioni di utilità per le EA del workspace:                    |
//|   - finestre temporali UTC                                       |
//|   - giorni di blackout (NFP primo venerdì del mese, FOMC list)   |
//|   - calcolo ATR su timeframe diverso                             |
//+------------------------------------------------------------------+
#property copyright "Trading System Workspace"
#property strict

#ifndef __TRAD_HELPERS_MQH__
#define __TRAD_HELPERS_MQH__

//+------------------------------------------------------------------+
//| Verifica se `now` cade nella finestra [start_h:start_m, end_h:end_m). |
//| Tutti gli orari in UTC. La finestra è semi-aperta a destra.       |
//+------------------------------------------------------------------+
bool H_InTimeWindow(const datetime now,
                    const int start_h, const int start_m,
                    const int end_h, const int end_m)
{
   MqlDateTime t;
   TimeToStruct(now, t);
   int now_min   = t.hour * 60 + t.min;
   int start_min = start_h * 60 + start_m;
   int end_min   = end_h   * 60 + end_m;
   return (now_min >= start_min && now_min < end_min);
}

//+------------------------------------------------------------------+
//| True se `now` è strettamente >= dell'orario `h:m`.               |
//+------------------------------------------------------------------+
bool H_AfterTime(const datetime now, const int h, const int m)
{
   MqlDateTime t;
   TimeToStruct(now, t);
   int now_min = t.hour * 60 + t.min;
   int ref_min = h * 60 + m;
   return now_min >= ref_min;
}

//+------------------------------------------------------------------+
//| True se `d` è il primo venerdì del mese (NFP day classico).      |
//+------------------------------------------------------------------+
bool H_IsFirstFridayOfMonth(const datetime d)
{
   MqlDateTime t;
   TimeToStruct(d, t);
   if(t.day_of_week != 5) return false;  // 5 = Venerdì in MQL5
   // Calcola il primo venerdì del mese.
   MqlDateTime first;
   first.year       = t.year;
   first.mon        = t.mon;
   first.day        = 1;
   first.hour       = 0;
   first.min        = 0;
   first.sec        = 0;
   datetime first_dt = StructToTime(first);
   MqlDateTime f;
   TimeToStruct(first_dt, f);
   int first_dow = f.day_of_week;
   int first_friday_day = 1 + ((5 - first_dow + 7) % 7);
   return t.day == first_friday_day;
}

//+------------------------------------------------------------------+
//| True se la stringa "YYYY-MM-DD" è in `list[]`.                   |
//+------------------------------------------------------------------+
bool H_IsoDateInList(const string iso_date, const string &list[])
{
   int n = ArraySize(list);
   for(int i=0; i<n; i++)
   {
      if(list[i] == iso_date) return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| Formatta una datetime come "YYYY-MM-DD" (UTC).                   |
//+------------------------------------------------------------------+
string H_DateIso(const datetime dt)
{
   MqlDateTime t;
   TimeToStruct(dt, t);
   return StringFormat("%04d-%02d-%02d", t.year, t.mon, t.day);
}

//+------------------------------------------------------------------+
//| Calcola ATR(period) sull'ultima candela chiusa per `symbol`+`tf`.|
//| Restituisce -1 se i dati non sono disponibili.                   |
//+------------------------------------------------------------------+
double H_ATR(const string symbol, const ENUM_TIMEFRAMES tf, const int period)
{
   int handle = iATR(symbol, tf, period);
   if(handle == INVALID_HANDLE) return -1.0;
   double buf[];
   if(CopyBuffer(handle, 0, 1, 1, buf) <= 0)  // shift=1: ultima candela CHIUSA
   {
      IndicatorRelease(handle);
      return -1.0;
   }
   double v = buf[0];
   IndicatorRelease(handle);
   return v;
}

//+------------------------------------------------------------------+
//| High e Low di tutte le M15 (o tf passato) tra le 00:00 e le      |
//| `end_h:end_m` UTC del giorno corrente. Restituisce false se non  |
//| ci sono dati sufficienti (es. mercato chiuso).                   |
//+------------------------------------------------------------------+
bool H_TodayRangeUtc(const string symbol, const ENUM_TIMEFRAMES tf,
                     const int start_h, const int start_m,
                     const int end_h, const int end_m,
                     double &out_high, double &out_low)
{
   datetime now = TimeCurrent();
   MqlDateTime t;
   TimeToStruct(now, t);

   MqlDateTime s = t;
   s.hour = start_h; s.min = start_m; s.sec = 0;
   datetime range_start = StructToTime(s);

   MqlDateTime e = t;
   e.hour = end_h; e.min = end_m; e.sec = 0;
   datetime range_end = StructToTime(e);

   if(range_end <= range_start) return false;

   MqlRates rates[];
   int copied = CopyRates(symbol, tf, range_start, range_end, rates);
   if(copied <= 0) return false;

   out_high = -DBL_MAX;
   out_low  =  DBL_MAX;
   for(int i=0; i<copied; i++)
   {
      // CopyRates(start, stop) include la candela che CONTIENE `stop` se chiusa
      // dopo. Filtriamo per essere certi di restare nella finestra.
      if(rates[i].time >= range_end) break;
      if(rates[i].high > out_high) out_high = rates[i].high;
      if(rates[i].low  < out_low)  out_low  = rates[i].low;
   }
   return (out_high > -DBL_MAX && out_low < DBL_MAX);
}

#endif // __TRAD_HELPERS_MQH__
//+------------------------------------------------------------------+
