//+------------------------------------------------------------------+
//|                                                    telegram.mqh  |
//|  Helper riutilizzabile per inviare messaggi Telegram da MQL5 EA. |
//|  Usa WebRequest() verso api.telegram.org/bot<TOKEN>/sendMessage. |
//|                                                                  |
//|  Setup richiesto sul terminale MT5:                              |
//|    Tools -> Options -> Expert Advisors -> Allow WebRequest       |
//|    aggiungere URL: https://api.telegram.org                      |
//+------------------------------------------------------------------+
#property copyright "Trading System Workspace"
#property strict

#ifndef __TRAD_TELEGRAM_MQH__
#define __TRAD_TELEGRAM_MQH__

//--- input dati: il token e chat id devono essere passati come input dell'EA
//    chiamante. Questo file è solo helper, non li dichiara come input qui.

//+------------------------------------------------------------------+
//| Encoding URL minimale per i caratteri che Telegram non accetta   |
//| crudi nel POST x-www-form-urlencoded.                            |
//+------------------------------------------------------------------+
string TG_UrlEncode(const string text)
{
   string out = "";
   int n = StringLen(text);
   for(int i=0; i<n; i++)
   {
      ushort c = StringGetCharacter(text, i);
      if((c>='A' && c<='Z') || (c>='a' && c<='z') || (c>='0' && c<='9')
         || c=='-' || c=='_' || c=='.' || c=='~')
      {
         out += ShortToString(c);
      }
      else if(c == ' ')
      {
         out += "+";
      }
      else
      {
         // UTF-8 multi-byte: ShortToString restituisce 1-3 byte; codifichiamo
         // ognuno come %HH.
         string ch = ShortToString(c);
         uchar bytes[];
         StringToCharArray(ch, bytes, 0, WHOLE_ARRAY, CP_UTF8);
         int blen = ArraySize(bytes) - 1;  // rimuovi NUL terminatore
         for(int b=0; b<blen; b++)
         {
            out += StringFormat("%%%02X", bytes[b]);
         }
      }
   }
   return out;
}

//+------------------------------------------------------------------+
//| Invia un messaggio Telegram. Restituisce true se HTTP 200 + ok.  |
//+------------------------------------------------------------------+
bool TG_SendMessage(const string bot_token, const string chat_id, const string text)
{
   if(StringLen(bot_token) == 0 || StringLen(chat_id) == 0)
   {
      Print("TG_SendMessage: bot_token o chat_id mancanti");
      return false;
   }

   string url = "https://api.telegram.org/bot" + bot_token + "/sendMessage";
   string body = "chat_id=" + chat_id + "&text=" + TG_UrlEncode(text);

   uchar post[];
   StringToCharArray(body, post, 0, WHOLE_ARRAY, CP_UTF8);
   // Rimuovi il NUL finale dato da StringToCharArray
   int post_len = ArraySize(post) - 1;
   ArrayResize(post, post_len);

   uchar result[];
   string headers = "Content-Type: application/x-www-form-urlencoded\r\n";
   string result_headers;
   ResetLastError();

   int http_status = WebRequest(
      "POST",
      url,
      headers,
      5000,            // timeout ms
      post,
      result,
      result_headers
   );

   if(http_status == -1)
   {
      int err = GetLastError();
      Print("TG_SendMessage: WebRequest fallita err=", err,
            ". Verificare che https://api.telegram.org sia consentito in ",
            "Tools -> Options -> Expert Advisors -> Allow WebRequest.");
      return false;
   }

   if(http_status != 200)
   {
      string resp = CharArrayToString(result, 0, WHOLE_ARRAY, CP_UTF8);
      Print("TG_SendMessage: HTTP ", http_status, " body=", resp);
      return false;
   }

   return true;
}

//+------------------------------------------------------------------+
//| Helper: format messaggio con emoji per ordini piazzati.          |
//| direction = "BUY" o "SELL".                                      |
//+------------------------------------------------------------------+
string TG_FormatOrderPlaced(
   const string strategy_name,
   const string symbol,
   const string direction,
   const double entry,
   const double sl,
   const double tp,
   const double size
)
{
   string emoji = (direction == "BUY") ? "🟢" : "🔴";
   int    digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);

   return StringFormat(
      "%s %s %s\nStrategia: %s\n\n📍 Entry: %s\n🛑 SL:    %s\n🎯 TP:    %s\n💰 Size: %.2f",
      emoji, direction, symbol,
      strategy_name,
      DoubleToString(entry, digits),
      DoubleToString(sl, digits),
      DoubleToString(tp, digits),
      size
   );
}

//+------------------------------------------------------------------+
//| Helper: format messaggio per fill confermati.                    |
//+------------------------------------------------------------------+
string TG_FormatFill(
   const string strategy_name,
   const string symbol,
   const string direction,
   const double fill_price
)
{
   int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
   return StringFormat(
      "✅ FILL %s %s\nStrategia: %s\nPrezzo eseguito: %s",
      direction, symbol,
      strategy_name,
      DoubleToString(fill_price, digits)
   );
}

//+------------------------------------------------------------------+
//| Helper: format messaggio per ordini cancellati o time stop.      |
//+------------------------------------------------------------------+
string TG_FormatInfo(const string strategy_name, const string symbol, const string detail)
{
   return StringFormat("ℹ️ %s %s\n%s", strategy_name, symbol, detail);
}

#endif // __TRAD_TELEGRAM_MQH__
//+------------------------------------------------------------------+
