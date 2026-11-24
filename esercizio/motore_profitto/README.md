# motore_profitto — strategie dei soci in esercizio sulle prop

Strategie che i soci hanno testato e tengono accese sui conti prop. Sono arrivate il 20-22/11/2026 e sono entrate in
`esercizio/` il 23/11 per decisione di Matteo (DECISIONS 2026-11-23).

⚠️ **Il verdetto è dei soci, non di `trad`.** I test e le probabilità di passare la prova scritti nei LEGGIMI sono stime
dei soci su circa un anno di dati: `trad` non li ha verificati e non c'è nessun nullo di confronto. Per la divisione dei
ruoli del 09/11, `trad` fa la teoria e i soci fanno i test. Lo stato vero di un conto si legge in MT5 o su NinjaTrader
(regola 1 di [`esercizio/README.md`](../README.md)), non qui.

## Cosa c'è

| Percorso | Piattaforma | Cosa fa | Dove gira |
|---|---|---|---|
| `mt5/Experts/PortafoglioIntraday.mq5` | MT5, CFD | regole intraday 1, 3, 4, 6, 7 e 8 (DAX, NAS100 due volte, fade sull'oro, SP500, petrolio WTI) + stop-and-reverse sull'oro alle news NFP, CPI e FOMC + guardiano giornaliero. Versione corretta del 20/11 | conto 2-Step 15k su MT5 (preset `BIL_FN15K`), acceso il 23/11 |
| `mt5/Presets/*.set` | MT5 | `F25K` = FTMO 25k, `P25K` = PU Prime 25k, `BIL_` = versione bilanciata, `BIL_FN15K` = conto 2-Step 15k (sotto). File UTF-16 | — |
| `ninjatrader/Strategies/OroOrderFlowNT.cs`, `OroSpintaNT.cs` | NinjaTrader 8, futures GC/MGC | segnali sugli scambi grossi dei futures dell'oro (GROSSI, FADE, SPINTA). Servono il volume dei futures: **sui CFD non si possono usare** | conto Futures Rapid 25k dei soci |
| `ninjatrader/Strategies/PortafoglioIntradayNT.cs` | NinjaTrader 8, micro futures | versione futures del portafoglio MT5 (MNQ, MES, MCL, MGC) | conto Futures Rapid 25k dei soci |
| `ninjatrader/AddOns/CuscinettoMP.cs` | NinjaTrader 8 | rischio ridotto quando ci si avvicina al limite di perdita; drawdown trailing di 1.000 $ **scritto nel codice** (solo Rapid 25k) | — |
| `ninjatrader/Indicators/*.cs` | NinjaTrader 8 | solo grafica, nessun ordine | — |
| `ninjatrader/LEGGIMI_ninjatrader.md` | — | istruzioni dei soci per NinjaTrader, aggiornate al 20/11 | — |
| `LEGGIMI_pacchetto_2026-11-22.txt` | — | istruzioni dei soci per il pacchetto MT5 + NinjaTrader del 22/11 | — |
| `news_eventi.csv` | entrambe | calendario delle news (1 NFP, 2 CPI, 4 FOMC), orari del server (Atene) fino al 09/12/2026 | MT5: `MQL5\Files\`; NinjaTrader: `Documenti\NinjaTrader 8\` |
| `guardiano_telegram/` | Python | avvisi Telegram per NinjaTrader, solo lettura; nessun token incluso | facoltativo |

**Non tenuti** (23/11): l'`.ex5` del pacchetto, perché non si può verificare da quale sorgente è stato compilato (l'EA
si compila da `mt5/Experts/`), e la copia di `PortafoglioIntradayNT.cs` del 22/11. Era identica a quella tenuta tranne
tre valori predefiniti fermi a prima del 18/11 (gruppo C `"14"`, news `"124"`, stop giorno 400 $).

## Conto 2-Step 15k (MT5): come è configurato

Dati letti dal terminale il 23/11, in sola lettura (pacchetto Python `MetaTrader5` agganciato al terminale già loggato,
senza credenziali):
- ora del server UTC+2, cioè Atene, come presume l'EA;
- conto hedging, leva effettiva circa 1:25 su oro, indici e petrolio;
- simboli `GER30` (è il DAX 40), `NDX100`, `SPX500`, `XAUUSD`, `USOUSD` (WTI; `UKOUSD` è il Brent);
- margine delle news sull'oro a 0,36 lotti: circa 5.240 $.

Il preset `BIL_FN15K` è il BIL con quattro valori cambiati:

| Parametro | BIL 25k | 15k | Perché |
|---|---|---|---|
| `SR_Lotti` | 0,60 | 0,36 | lotti assoluti al saldo di partenza, riscalati a 15/25 |
| `GS_SaldoPartenza` | 0 | 15000 | con 0 la base dei lotti delle news si azzera a ogni riavvio |
| `GS_Obiettivo` | 0 | 8 | chiude e si ferma a fase 1 passata; **5 sul conto di fase 2** |
| simboli | `.cash` (FTMO) | nomi del server FundedNext | — |

Installazione: `.mq5` in `MQL5\Experts` (compilare con F7), `news_eventi.csv` in `MQL5\Files`, preset in
`MQL5\Presets`. Grafico XAUUSD M5, carica il preset, Algo Trading acceso. Nella scheda Esperti devono comparire
`PortafoglioIntraday avviato`, `News caricate: N` e `GUARDIANO: stop giorno 4.0%, obiettivo 8.0% su 15000.00`, senza
righe `ATTENZIONE`.

## Regole

1. **Una sola versione per file.** Un aggiornamento dei soci sostituisce il file qui. Il vecchio si cancella dopo un
   `diff` che mostra cosa cambia; quello che cambia si scrive in `## Aggiornamenti` sotto.
2. **Nessuna modifica alla logica senza accordo fra i soci** (LEGGIMI). Si cambiano solo le impostazioni di un conto,
   in un preset con il nome del conto.
3. **Repo pubblico**: niente nomi, numeri di conto, token o percorsi personali, nemmeno nei LEGGIMI.
4. **Magic number**: 881001-881008 (regole), 20261401-20261403 (news), gli stessi di `PortafoglioUnico` e `Intraday4`.
   Due di questi EA sullo stesso conto si chiudono le posizioni a vicenda.

## Come si rompe

- **Simbolo scritto male nel preset**: l'EA parte, scrive `ATTENZIONE: simbolo ... non trovato` e quella regola non
  apre mai.
- **Server con un altro fuso**: le sessioni di Londra e New York e le news si spostano. L'EA presume l'ora di Atene.
- **`news_eventi.csv` mancante** (per esempio su una VPS nuova): le news restano spente e il registro dice
  `news_eventi.csv non trovato`. Il calendario finisce il 09/12/2026 e va aggiornato prima.
- **Cambio di contratto dei futures** (NinjaTrader): i nomi dei contratti nelle impostazioni vanno aggiornati a ogni
  scadenza.
- **Bot NinjaTrader su un conto diverso dal Rapid 25k**: il cuscinetto calcola il rischio sul drawdown sbagliato.

## Aggiornamenti

| Data | Cosa | Da dove |
|---|---|---|
| 2026-11-23 | ingresso: EA MT5 del 20/11, bot NinjaTrader del 20/11, preset `BIL_FN15K` | pacchetti dei soci del 20/11 e del 22/11 |
