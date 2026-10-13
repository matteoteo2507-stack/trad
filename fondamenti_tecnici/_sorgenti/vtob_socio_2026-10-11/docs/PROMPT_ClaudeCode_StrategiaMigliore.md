# Missione: trovare la strategia più profittevole e robusta basata sull'indicatore "VTOB PRO" (XAUUSD)

Sei Claude Code e stai lavorando sul mio PC. TradingView è aperto sul desktop: puoi usare il browser (estensione Claude in Chrome o computer use) per aprirlo. Ho tutti gli abbonamenti e le funzionalità che servono.

**Obiettivo:** partendo dall'indicatore Pine qui sotto, trova, migliora e rendi automatizzabile la strategia **più profittevole possibile, ma reale e robusta**. Requisiti:
- opera abbastanza spesso: **almeno 1 trade a settimana in media**, idealmente qualche trade ogni settimana;
- **win rate e profit factor alti**;
- **drawdown basso**;
- **regole 100% meccaniche**, eseguibili da un EA MT5 e da una strategy() TradingView.

Non fermarti alla prima soluzione. Itera: testa, analizza cosa non funziona, migliora l'indicatore (per esempio meno OB ma migliori, filtri migliori, gestione del trade migliore) e ritesta. Vai avanti finché trovi una strategia che rispetta i criteri qui sotto, oppure finché puoi dimostrare con i dati che non si può fare meglio.

## Come lavorare (importante)
1. **Il motore di ricerca è Python, non i click su TradingView.** Ottimizzare cliccando nello Strategy Tester permette poche decine di prove ed è lento. Fai la ricerca in Python sugli export MT5 che trovi nella cartella del progetto (`XAUUSD_M5.csv`, `XAUUSD_M15.csv`, e gli altri timeframe se ci sono):
   - colonne: `time,open,high,low,close,tick_volume,spread,real_volume`;
   - `time` = ora del server, cioè UTC+3 d'estate e UTC+2 d'inverno; l'ora italiana è quella del server meno 1 ora;
   - `spread` in punti: 1 punto = 0,01 $;
   - prezzi BID.

   Se vuoi più storico M5/M1, chiedimi di riesportarlo dopo aver impostato in MT5 "Barre massime nel grafico = Illimitato".
2. **TradingView serve per tre cose:**
   - (a) caricare l'indicatore e controllare a vista che i tuoi OB in Python coincidano con quelli disegnati;
   - (b) caricare le strategy() Pine finali e leggere i risultati dello Strategy Tester;
   - (c) creare gli alert.

   Per incollare il codice usa il Pine Editor. Non salvare script pubblici e non modificare le impostazioni dell'account.
3. Se ci sono, parti dai miei file:
   - `motore_riferimento_vtob_bt.py`: motore validato;
   - `vtob_v2.py`: motore con più OB attivi, BE, parziali, trailing, time stop;
   - `STRATEGIA_VTOB_Config1.md`: la specifica della strategia migliore trovata finora;
   - `PORTAFOGLIO_VTOB.md`, `VTOB_Strategy_Portafoglio.pine`, `VTOB_Config1_EA.mq5`: il portafoglio, la strategy TradingView e l'EA.

## Punto di partenza (risultati già ottenuti, con spread reale e senza lookahead)
- **Config 1, M15** (lug 2022 – ott 2026). Regole: pivot 7/3, filtri "trend da ≥20 candele" + "OB oltre la linea Supertrend" + "close sopra EMA200 H1", ingresso alla croce di retest, SL 6×vol, TP 3R, BE a +1R, solo long.

  Risultato: **199 trade (0,9 a settimana), PF 2,03, +83 R, maxDD 8,9 R**, 5 anni positivi su 5.
- **M5** (mag 2025 – ott 2026). Regole: pivot 10/3, trend da ≥60 candele, EMA200 H1, SL 8×vol, TP 4R, BE 1R, long e short.

  Risultato: **87 trade, PF 1,74, +26,6 R, DD 7,8 R**.
- **M15 + M5 insieme:** 154 trade in 17 mesi (circa 2 a settimana), PF 1,94, +57 R. Con l'1% di rischio per trade: +73% in 17 mesi e maxDD 10,4%. Ma il **mese mediano è solo +0,3%**: i guadagni sono concentrati nelle fasi di trend forte.
- **AGGIORNAMENTO, portafoglio multi-timeframe (miglior risultato finora).** Dettagli in `PORTAFOGLIO_VTOB.md`; strategy TradingView `VTOB_Strategy_Portafoglio.pine` con preset A/B/C/D.
  - Composizione: A = M15 (sopra); B = H1 pivot 10/3 + EMA200 D1, long+short, SL 3×vol, TP 4R, BE 1R; C = M30 pivot 5/2 + EMA200 H4, long+short, SL 8×vol, TP 3R, BE 1R.
  - Risultato A+B+C, 4 anni: **424 trade (1,9/sett), PF 2,14, +197 R, DD 13,7 R, tutti gli anni positivi**. Con lo 0,5% di rischio: +163% e DD 6,7%.
  - **Il tuo primo compito è verificare e provare a battere questo portafoglio**, non ripartire da zero. Verificalo anche su TradingView: carica la strategy con ogni preset sul TF giusto e confronta i numeri.
- **Cosa ha funzionato:** filtri trend/HTF/distanza dalla linea; conferma pivot veloce (3 candele); stop largo (4-8×vol), perché con stop stretti lo spread mangia tutto; R:R 3-4 con BE a 1R; ingresso alla croce.
- **Cosa NON ha funzionato:** filtro impulso; filtro volume; percentuali Buy/Sell; zona sullo stoppino; ingresso più dentro la zona; stop subito oltre la zona; pivot lenti. Gli short sono deboli nel periodo rialzista.

## Spazio di ricerca suggerito (oltre a quello già fatto)
- **Timeframe:** M1, M5, M15, M30, H1, H4 (puoi ricampionare dai TF più bassi) e **portafogli multi-timeframe**.
- **Struttura OB:** uno o più OB attivi; definizioni diverse di pivot/zona; OB "freschi" (primo tocco) contro ritocchi; zone da fair value gap o da break of structure come varianti.
- **Filtri:** HTF diversi (H1/H4/D1); regime di volatilità (per esempio non tradare se la volatilità è sotto o sopra un certo percentile); sessioni (Londra / New York); giorni della settimana; news (se trovi un calendario affidabile).
- **Uscite:**
  - SL in volatilità o in $;
  - TP 1-5R;
  - BE a 0,5-2R;
  - parziali (50% a 1R ecc.);
  - trailing (ATR, linea Supertrend, swing);
  - time stop;
  - uscita al cambio trend.
- **Short:** solo con HTF ribassista forte (per esempio sotto EMA H4 e D1).
- **Gestione del rischio** del portafoglio: rischio massimo aperto e correlazione tra le strategie.

## Regole anti-autoinganno (OBBLIGATORIE)
- **Niente lookahead:**
  - pivot e OB esistono solo dalla candela di conferma;
  - segnali a candela chiusa, ingresso all'open successivo;
  - EMA HTF solo da candele HTF chiuse;
  - se una stessa candela tocca SL e TP, conta lo SL;
  - spread reale per candela e slippage di almeno 0,10 $.
- **Scelta dei parametri SOLO sul primo 60-65% dei dati.** Verifica sul resto (out-of-sample) e fai anche un walk-forward. Riporta sempre IS e OOS separati.
- **Robustezza:** tieni solo configurazioni su un "plateau", cioè che restano buone se cambi i parametri di ±1 step. Riporta anche quante configurazioni hai testato in totale.
- **Monte Carlo** sull'ordine dei trade: drawdown al 95° percentile.
- **Minimo statistico:** almeno 100 trade in totale e almeno 30 in OOS.
- **Non promettere rendimenti:** se il risultato migliore è modesto, dillo chiaramente.

## Criteri di "strategia trovata" (tutti in OOS, con spread)
- almeno 1 trade a settimana in media;
- PF ≥ 1,5;
- maxDD ≤ 10 R (e DD Monte Carlo al 95° ≤ 15 R);
- almeno il 60% dei mesi positivi;
- nessun anno negativo.

## Consegne
1. `report.md` in italiano:
   - tabella delle migliori configurazioni per timeframe;
   - il portafoglio consigliato;
   - equity curve;
   - rendimento mensile in % con l'1% di rischio per trade;
   - limiti e rischi.
2. L'indicatore migliorato `VTOB_PRO_v2.pine`, con le regole finali, SL/TP/BE disegnati e gli alert.
3. Una `strategy()` Pine per ogni configurazione finale. Caricala su TradingView, esegui lo Strategy Tester e riporta i risultati confrontandoli con quelli Python, spiegando le differenze.
4. Un EA MT5 (`.mq5`) per ogni configurazione finale. Requisiti:
   - parametri in input;
   - magic number diversi;
   - rischio in % del balance;
   - un trade per OB;
   - log chiari;
   - da testare nello Strategy Tester di MT5 con "ogni tick basato su tick reali".
5. La specifica testuale di ogni strategia, nel formato di `STRATEGIA_VTOB_Config1.md`.

Lavora per gradi e aggiornami a ogni traguardo:
1. replica e validazione;
2. primi risultati per TF;
3. miglioramenti all'indicatore;
4. portafoglio finale.

Se ti serve una decisione mia (rischio, broker, orari), chiedi.

## Codice Pine di partenza (indicatore VTOB PRO)
```pinescript
// This work is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
// https://creativecommons.org/licenses/by-nc-sa/4.0/
// © BigBeluga — versione modificata con selezione OB a punteggio
//
// Differenze dall'originale:
// - Ogni OB riceve un PUNTEGGIO DI QUALITÀ calcolato nel momento in cui nasce (solo dati già disponibili, niente futuro).
// - Vengono disegnati solo gli OB con punteggio >= al minimo scelto. Gli altri non compaiono proprio.
// - Gli OB non vengono mai cancellati: quando il prezzo li sfonda si fermano lì e diventano grigi.
// - Croci di retest solo sugli OB selezionati, con filtro orario opzionale. Alert pronti.
// - Default scelti dal backtest su XAUUSD M15 (lug 2022 - ott 2026): fattori 2+3+4 attivi, punteggio minimo 3,
//   ingresso sulla croce di retest, stop 4x volatilità, target 1:2. Impulso e volume non hanno migliorato i risultati.
// - Pivot 7 a sinistra / 3 a destra: conferma in 3 candele invece di 7 (OB disegnato 45 min dopo il minimo/massimo
//   invece di 1h45 sul 15m). Zona alta 1x volatilità e ingresso sul bordo: le varianti testate andavano peggio.

//@version=6
indicator('Volume-Trend Order Block Engine PRO [BigBeluga mod]', overlay = true, max_boxes_count = 500, max_lines_count = 500, max_labels_count = 500)

// ＩＮＰＵＴＳ ――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――{

gp_st = 'Custom Supertrend Settings'
st_len = input.int(50, title = 'Volatility SMA Length', group = gp_st)
st_mult = input.float(3.5, title = 'Multiplier', step = 0.1, group = gp_st)
show_fill = input.bool(true, title = 'Show Trend Cloud Fill', group = gp_st)

gp_cloud = 'Trend Cloud Settings'
cloud_bull_col = input.color(#00ffcc, title = 'Bullish Cloud Color', group = gp_cloud)
cloud_bear_col = input.color(#ff007f, title = 'Bearish Cloud Color', group = gp_cloud)

gp_ob = 'Order Block Settings'
pivot_left = input.int(7, title = 'Pivot: candele a sinistra', minval = 1, group = gp_ob, tooltip = 'Quante candele PRIMA del minimo/massimo devono essere meno estreme. Non crea ritardo.')
pivot_len = input.int(3, title = 'Pivot: candele a destra (ritardo conferma)', minval = 1, group = gp_ob, tooltip = 'Dopo quante candele l\'OB viene confermato e disegnato. Originale 7. Backtest: 3 dà risultati migliori e OB 4 candele prima.')
bull_col = input.color(#00ffcc, title = 'Bullish OB Color', group = gp_ob)
bear_col = input.color(#ff007f, title = 'Bearish OB Color', group = gp_ob)
txt_col = input.color(#e0e0e0, title = 'OB Text Label Color', group = gp_ob)
broken_col = input.color(color.new(color.gray, 60), title = 'Colore OB sfondato', group = gp_ob)

gp_q = 'Selezione OB — Punteggio qualità'
min_score = input.int(3, title = 'Punteggio minimo per mostrare un OB', minval = 0, maxval = 5, group = gp_q, tooltip = 'Ogni fattore attivo che l\'OB rispetta vale 1 punto. Più alto = meno OB ma più selezionati. 0 = mostra tutti (come l\'originale).')
use_imp = input.bool(false, title = '1. Impulso: il prezzo è scappato dalla zona', inline = 'imp', group = gp_q, tooltip = 'Nelle candele di conferma il prezzo si è allontanato dall\'OB di almeno X volte la volatilità media. Zona da cui il mercato è ripartito con forza.')
imp_mult = input.float(1.0, title = 'x volatilità', step = 0.25, minval = 0.0, inline = 'imp', group = gp_q)
use_age = input.bool(true, title = '2. Trend già avviato (non appena girato)', inline = 'age', group = gp_q, tooltip = 'Il trend deve durare da almeno N candele. Gli OB nati subito dopo un cambio di trend sono più fragili.')
min_trend_bars = input.int(20, title = 'candele', minval = 0, inline = 'age', group = gp_q)
use_htf = input.bool(true, title = '3. D\'accordo col timeframe superiore', inline = 'htf', group = gp_q, tooltip = 'Long: prezzo sopra la EMA del TF superiore. Short: sotto. Usa la candela HTF già chiusa, quindi non ridisegna.')
htf_tf = input.timeframe('60', title = 'TF', inline = 'htf', group = gp_q)
htf_len = input.int(200, title = 'EMA', minval = 1, inline = 'htf', group = gp_q)
use_dist = input.bool(true, title = '4. Zona lontana dalla linea di trend', inline = 'dist', group = gp_q, tooltip = 'Tutto l\'OB deve stare oltre la linea Trend Stop di almeno X volte la volatilità. Una zona appoggiata sulla linea, se toccata, spesso gira il trend.')
dist_mult = input.float(0.0, title = 'x volatilità', step = 0.25, minval = 0.0, inline = 'dist', group = gp_q)
use_vol = input.bool(false, title = '5. Volume sopra la media sul pivot', inline = 'vol', group = gp_q, tooltip = 'La candela del pivot ha un volume almeno X volte la media delle 20 precedenti.')
vol_mult = input.float(1.2, title = 'x media', step = 0.1, minval = 0.0, inline = 'vol', group = gp_q)
show_score = input.bool(true, title = 'Scrivi il punteggio dentro l\'OB', group = gp_q)
show_rej = input.bool(false, title = 'Mostra in grigio gli OB scartati', group = gp_q)

gp_sig = 'Segnali di Retest'
show_bull_retest = input.bool(true, title = 'Segnali Long (croce)', inline = 'b', group = gp_sig)
bull_sig_col = input.color(#00ffcc, title = '', inline = 'b', group = gp_sig)
show_bear_retest = input.bool(true, title = 'Segnali Short (croce)', inline = 's', group = gp_sig)
bear_sig_col = input.color(#ff007f, title = '', inline = 's', group = gp_sig)
use_sess = input.bool(false, title = 'Segnali solo in questa fascia (ora italiana)', inline = 'ses', group = gp_sig)
sess = input.session('0900-1900', title = '', inline = 'ses', group = gp_sig)
show_htf_line = input.bool(false, title = 'Mostra EMA del timeframe superiore', group = gp_sig)
dir_mode = input.string('Long e Short', title = 'Direzione segnali', options = ['Long e Short', 'Solo Long', 'Solo Short'], group = gp_sig, tooltip = 'Nel backtest 2022-2026 gli short hanno perso anche con i filtri (oro in forte rialzo). Valuta Solo Long finché il trend di fondo resta rialzista.')
show_lvls = input.bool(true, title = 'Disegna Stop e Target sul segnale', group = gp_sig)
sl_mult = input.float(4.0, title = 'Stop = X volte la volatilità', step = 0.5, minval = 0.5, inline = 'lv', group = gp_sig, tooltip = 'Volatilità = media del range delle candele (la stessa usata per l\'altezza degli OB). Backtest: 4x.')
rr = input.float(2.0, title = 'Target R:R', step = 0.5, minval = 0.5, inline = 'lv', group = gp_sig)
lvl_len = input.int(24, title = 'Lunghezza linee (candele)', minval = 1, group = gp_sig)

// }
// ＣＡＬＣＵＬＡＴＩＯＮＳ――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――{
src = hl2
custom_atr = ta.sma(high - low, st_len)
upper_band = src + st_mult * custom_atr
lower_band = src - st_mult * custom_atr
prevLowerBand = nz(lower_band[1])
prevUpperBand = nz(upper_band[1])

lower_band := lower_band > prevLowerBand or close[1] < prevLowerBand ? lower_band : prevLowerBand
upper_band := upper_band < prevUpperBand or close[1] > prevUpperBand ? upper_band : prevUpperBand
int market_trend = na
float trend_stop = na
prevSuperTrend = trend_stop[1]
if na(custom_atr[1])
    market_trend := 1
else if prevSuperTrend == prevUpperBand
    market_trend := close > upper_band ? 1 : -1
else
    market_trend := close < lower_band ? -1 : 1
trend_stop := market_trend == 1 ? lower_band : upper_band

pivot_low = ta.pivotlow(low, pivot_left, pivot_len)
pivot_high = ta.pivothigh(high, pivot_left, pivot_len)

// --- Fattori per il punteggio (solo dati già chiusi al momento della conferma) ---
float hh_after = ta.highest(high, pivot_len)
float ll_after = ta.lowest(low, pivot_len)
int trend_age = nz(ta.barssince(market_trend != market_trend[1]), 100000)
float vol_avg = ta.sma(volume, 20)
bool vol_ok = not na(vol_avg[pivot_len + 1]) and volume[pivot_len] >= vol_mult * vol_avg[pivot_len + 1]
float htf_ema = request.security(syminfo.tickerid, htf_tf, ta.ema(close, htf_len)[1], lookahead = barmerge.lookahead_on)
bool in_sess = not na(time(timeframe.period, sess, 'Europe/Rome'))

ob_score(int dir, float top, float bot) =>
    int sc = 0
    if use_imp and (dir == 1 ? hh_after - top >= imp_mult * custom_atr : bot - ll_after >= imp_mult * custom_atr)
        sc += 1
    if use_age and trend_age >= min_trend_bars
        sc += 1
    if use_htf and not na(htf_ema) and (dir == 1 ? close > htf_ema : close < htf_ema)
        sc += 1
    if use_dist and (dir == 1 ? bot - trend_stop >= dist_mult * custom_atr : trend_stop - top >= dist_mult * custom_atr)
        sc += 1
    if use_vol and vol_ok
        sc += 1
    sc

int max_score = (use_imp ? 1 : 0) + (use_age ? 1 : 0) + (use_htf ? 1 : 0) + (use_dist ? 1 : 0) + (use_vol ? 1 : 0)
int need_score = math.min(min_score, max_score)

var box active_top_box = na
var box active_bot_box = na
var float active_top = na
var float active_bot = na
var float active_buy_ratio = na
var int active_ob_trend = 0
var int active_score = 0

is_overlapping(float new_top, float new_bot) =>
    if na(active_top) or na(active_bot)
        false
    else
        not(new_bot > active_top or new_top < active_bot)

p_idx = bar_index - pivot_len

get_window_volume_ratio(int lookback_len) =>
    float buy_vol = 0.0
    float sell_vol = 0.0
    for i = 0 to lookback_len by 1
        if close[i] >= open[i]
            buy_vol := buy_vol + volume[i]
        else
            sell_vol := sell_vol + volume[i]
    total_vol = buy_vol + sell_vol
    float buy_pct = total_vol > 0 ? buy_vol / total_vol : 0.5
    buy_pct

score_txt(int sc) =>
    show_score ? '  |  Q ' + str.tostring(sc) + '/' + str.tostring(max_score) : ''

draw_rejected(float top, float bot, int sc) =>
    if show_rej
        box.new(left = p_idx, top = top, right = bar_index, bottom = bot, bgcolor = color.new(color.gray, 88), border_color = color.new(color.gray, 60), border_style = line.style_dotted, text = 'Q ' + str.tostring(sc) + '/' + str.tostring(max_score), text_color = color.new(color.gray, 30), text_size = size.tiny, text_halign = text.align_right)

bool new_bull_ob = false
bool new_bear_ob = false

// 1. Uptrend Order Blocks
if market_trend == 1 and not na(pivot_low)
    ob_top = math.min(open[pivot_len], close[pivot_len])
    ob_bot = ob_top - custom_atr
    if not is_overlapping(ob_top, ob_bot)
        int sc = ob_score(1, ob_top, ob_bot)
        if sc < need_score
            draw_rejected(ob_top, ob_bot, sc)
        else
            if not na(active_top_box)
                box.set_right(active_top_box, p_idx)
                box.set_right(active_bot_box, p_idx)
            active_top := ob_top
            active_bot := ob_bot
            active_ob_trend := 1
            active_score := sc
            new_bull_ob := true
            float buy_ratio = get_window_volume_ratio(7)
            active_buy_ratio := buy_ratio
            float split_price = active_bot + (active_top - active_bot) * buy_ratio
            string top_text = 'Sell: ' + str.tostring(math.round((1.0 - buy_ratio) * 100)) + '%' + score_txt(sc)
            string bot_text = 'Buy: ' + str.tostring(math.round(buy_ratio * 100)) + '%'
            active_top_box := box.new(left = p_idx, top = active_top, right = bar_index, bottom = split_price, bgcolor = color.new(bull_col, 85), border_color = color.new(bull_col, 40), text = top_text, text_color = txt_col, text_size = size.small, text_valign = text.align_center, text_halign = text.align_right)
            active_bot_box := box.new(left = p_idx, top = split_price, right = bar_index, bottom = active_bot, bgcolor = color.new(bull_col, 75), border_color = color.new(bull_col, 40), text = bot_text, text_color = txt_col, text_size = size.small, text_valign = text.align_center, text_halign = text.align_right)

// 2. Downtrend Order Blocks
if market_trend == -1 and not na(pivot_high)
    ob_bot = math.max(open[pivot_len], close[pivot_len])
    ob_top = ob_bot + custom_atr
    if not is_overlapping(ob_top, ob_bot)
        int sc = ob_score(-1, ob_top, ob_bot)
        if sc < need_score
            draw_rejected(ob_top, ob_bot, sc)
        else
            if not na(active_top_box)
                box.set_right(active_top_box, p_idx)
                box.set_right(active_bot_box, p_idx)
            active_top := ob_top
            active_bot := ob_bot
            active_ob_trend := -1
            active_score := sc
            new_bear_ob := true
            float buy_ratio = get_window_volume_ratio(7)
            active_buy_ratio := buy_ratio
            float split_price = active_bot + (active_top - active_bot) * buy_ratio
            string top_text = 'Sell: ' + str.tostring(math.round((1.0 - buy_ratio) * 100)) + '%' + score_txt(sc)
            string bot_text = 'Buy: ' + str.tostring(math.round(buy_ratio * 100)) + '%'
            active_top_box := box.new(left = p_idx, top = active_top, right = bar_index, bottom = split_price, bgcolor = color.new(bear_col, 75), border_color = color.new(bear_col, 40), text = top_text, text_color = txt_col, text_size = size.small, text_valign = text.align_center, text_halign = text.align_right)
            active_bot_box := box.new(left = p_idx, top = split_price, right = bar_index, bottom = active_bot, bgcolor = color.new(bear_col, 85), border_color = color.new(bear_col, 40), text = bot_text, text_color = txt_col, text_size = size.small, text_valign = text.align_center, text_halign = text.align_right)

// OB sfondato: NON viene cancellato. Si ferma alla candela di rottura e diventa grigio; da lì niente più segnali su di lui.
if not na(active_top) and not na(active_bot)
    bool is_broken = (active_ob_trend == 1 and high < active_bot) or (active_ob_trend == -1 and low > active_top)
    if is_broken
        box.set_right(active_top_box, bar_index)
        box.set_right(active_bot_box, bar_index)
        box.set_border_color(active_top_box, broken_col)
        box.set_border_color(active_bot_box, broken_col)
        box.set_bgcolor(active_top_box, color.new(color.gray, 85))
        box.set_bgcolor(active_bot_box, color.new(color.gray, 80))
        active_top_box := na
        active_bot_box := na
        active_top := na
        active_bot := na
        active_ob_trend := 0

if not na(active_top_box) and not na(active_bot_box)
    box.set_right(active_top_box, bar_index)
    box.set_right(active_bot_box, bar_index)

// Segnali di retest (a candela chiusa) solo sugli OB selezionati
marketChange = market_trend != market_trend[1]
bool sess_ok = not use_sess or in_sess
bool long_dir = dir_mode != 'Solo Short'
bool short_dir = dir_mode != 'Solo Long'

bool buy_retest = ta.crossover(low, active_top) and show_bull_retest and active_ob_trend == 1 and na(pivot_low) and not na(active_top) and not marketChange and sess_ok and long_dir and barstate.isconfirmed
bool sell_retest = ta.crossunder(high, active_bot) and show_bear_retest and active_ob_trend == -1 and na(pivot_high) and not na(active_bot) and not marketChange and sess_ok and short_dir and barstate.isconfirmed

// }
// ＰＬＯＴ ――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――{

st_plot = plot(market_trend != market_trend[1] ? float(na) : trend_stop, title = 'Trend Stop', color = market_trend == 1 ? cloud_bull_col : cloud_bear_col, linewidth = 1, style = plot.style_linebr)
price_plot = plot(close, title = 'Close Price Reference', display = display.none)
fill_color = show_fill ? market_trend == 1 ? color.new(cloud_bull_col, 80) : color.new(cloud_bear_col, 80) : na
fill(price_plot, st_plot, close, trend_stop, fill_color, color(na))

plot(show_htf_line ? htf_ema : na, title = 'EMA timeframe superiore', color = color.new(color.orange, 20), linewidth = 2)

plotshape(buy_retest, title = 'Retest Long', style = shape.cross, location = location.belowbar, color = bull_sig_col, size = size.tiny)
plotshape(sell_retest, title = 'Retest Short', style = shape.cross, location = location.abovebar, color = bear_sig_col, size = size.tiny)

// Stop e Target del segnale (ingresso indicativo = chiusura della candela del segnale)
draw_levels(int d) =>
    float e = close
    float sl = e - d * sl_mult * custom_atr
    float tp = e + d * rr * sl_mult * custom_atr
    line.new(bar_index, e, bar_index + lvl_len, e, color = color.new(color.white, 30), style = line.style_dotted)
    line.new(bar_index, sl, bar_index + lvl_len, sl, color = color.new(color.red, 10), width = 2)
    line.new(bar_index, tp, bar_index + lvl_len, tp, color = color.new(color.lime, 10), width = 2)
    label.new(bar_index + lvl_len, sl, 'SL ' + str.tostring(sl, format.mintick), style = label.style_label_left, color = color.new(color.red, 70), textcolor = color.white, size = size.tiny)
    label.new(bar_index + lvl_len, tp, 'TP ' + str.tostring(tp, format.mintick), style = label.style_label_left, color = color.new(color.lime, 70), textcolor = color.white, size = size.tiny)

if show_lvls and buy_retest
    draw_levels(1)
if show_lvls and sell_retest
    draw_levels(-1)

// ＡＬＥＲＴ ――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――{
alertcondition(new_bull_ob, title = 'Nuovo OB Long selezionato', message = '{{ticker}} {{interval}}: nuovo OB LONG di qualità')
alertcondition(new_bear_ob, title = 'Nuovo OB Short selezionato', message = '{{ticker}} {{interval}}: nuovo OB SHORT di qualità')
alertcondition(buy_retest, title = 'Retest Long', message = '{{ticker}} {{interval}}: retest LONG su OB selezionato')
alertcondition(sell_retest, title = 'Retest Short', message = '{{ticker}} {{interval}}: retest SHORT su OB selezionato')
// }
```
