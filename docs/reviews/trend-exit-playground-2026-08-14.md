# Trend following: coda aperta **NO-GO** · playground **LEAD** (primo ordinamento confermato)

**Data**: 2026-08-14 · **Verdetti**: **Q1 NO-GO** (kill-switch pre-registrato) · **Q2 LEAD**
**Pre-registrazione**: [TREND_EXIT_PLAYGROUND_PREREGISTRATION.md](../TREND_EXIT_PLAYGROUND_PREREGISTRATION.md)
**Motori**: [`analysis/trend/export_d1.py`](../../analysis/trend/export_d1.py) ·
[`backtest.py`](../../analysis/trend/backtest.py) · [`q2_checks.py`](../../analysis/trend/q2_checks.py)
**Fonte esterna**: Pavel Kichev — spec e claim presi da lui, non inventati da noi.

---

## Campione

Feed **omogeneo** Dukascopy D1, 27 strumenti su 8 gruppi. **W1** = 2012→2026 (17 strumenti,
14,6 anni, 1.264 segnali a lookback 100); **W2** = 2017-12→2026 (tutti e 27, 1.169 segnali).
Esclusi per **copertura** e mai per risultato: USTBOND, XPT, XPD (inizio dopo il 2018).

### Due difetti dei dati trovati e corretti prima del test

1. **Barre di weekend**. Il D1 grezzo Dukascopy contiene sessioni **parziali** di sabato/domenica:
   EURUSD ha 761 barre domenicali con range mediano **0,137%** contro **0,65%** dei feriali; NAS100
   574; barre di sabato a range **esattamente zero**. Tenerle diluisce l'ATR(20) verso il basso → R
   troppo piccolo → **ogni multiplo di R gonfiato**, e trasforma il "Donchian 100 giorni" in ~83
   giorni reali. Corretto **fondendo il weekend nella barra feriale successiva** (la crypto tratta
   davvero 7 giorni: lì non si fonde). Dopo il fix tutti gli strumenti stanno a 250-261 barre/anno.
2. **Bug mio nel fix**: la chiave di raggruppamento nasceva da un `cumsum` invertito e restituiva la
   serie **in ordine temporale inverso**. Intercettato da un controllo di sanità (barre/anno
   negative) prima di qualunque backtest.

*Nota per l'audit richiesto*: il **feed broker legacy** (`data/*_D1.csv`, quello di NXT, ricerca
livelli e TSMOM) è **pulito** — 258-260 barre/anno, zero barre domenicali: il broker già aggrega.
Questo difetto **non contamina i risultati passati**.

---

## Q1 — La coda aperta: **NO-GO**

Quattro uscite sulle **identiche** entrate Donchian, tre lookback (50 primario 100, 200):

| lookback | **E1 trail SMA10** | E1b trail+stop | E2 stop1R/target3R | **E3 uscita a 20g** | E1 vs random |
|---|---|---|---|---|---|
| 50 | +0,015 | +0,057 | +0,067 | **+0,131** | −0,004 [−0,107, +0,098] |
| **100** | **−0,038** | −0,008 | +0,045 | **+0,110** | −0,076 [−0,202, +0,053] |
| 200 | −0,024 | +0,028 | +0,057 | **+0,137** | −0,125 [−0,269, +0,021] |

**Il trail è l'uscita peggiore o quasi in tutte e tre le varianti. L'uscita a tempo — la più stupida
possibile — è la migliore in tutte e tre.** A lookback 100 la differenza appaiata **E1 − E3 =
−0,147, BCa95 [−0,285, −0,014]**: esclude lo zero dal lato sfavorevole.

Kill-switch pre-registrato: **E1 non batte il baseline random** in nessuna variante (CI sempre a
cavallo dello zero) → **NO-GO**. In aggiunta: anni positivi **6/15** (W1) e **2/9** (W2); a **3×
costi** E[R] = **−0,100** in W1.

**Il residuo onesto — e la sua spiegazione più probabile.** Il **soffitto** delle entrate reali è
significativamente più alto del random: oracolo **+2,05 vs +1,24**, diff **+0,81 [+0,669, +0,959]**.
L'entrata Donchian *seleziona* momenti con più escursione disponibile — ma **nessuna delle quattro
uscite la raccoglie**. Attenzione a non innamorarsene: un breakout avviene **per costruzione** quando
la volatilità si espande rispetto all'ATR trailing, quindi R sottostima il range successivo e il
soffitto in unità di R si gonfia da solo. È probabilmente lo stesso artefatto meccanico misurato in
C1 qui sotto, non un edge latente.

### Risposta alla domanda dell'utente sul trail

**No, e la risposta non dipende dal fatto che l'entrata abbia edge.** Il confronto E1 vs E3 è
**appaiato sulle stesse entrate**: qualunque sia il valore dell'ingresso, troncare a 20 giorni ha
reso più che lasciar correre, su 15 anni, 3 lookback, 17-27 strumenti. Questo è il secondo test
indipendente della stessa tesi nella stessa giornata, su un veicolo **costruito apposta** perché la
coda aperta fosse la regola nativa e non un innesto.

---

## W3 — Stazionarietà: il "post-2020" si ripresenta, **col segno opposto**

| finestra | n | E[R] E1 | BCa95 | vs random |
|---|---|---|---|---|
| pre-2020 | 634 | +0,078 | [−0,095, +0,250] | +0,010 [−0,172, +0,177] |
| post-2020 | 586 | **−0,208** | [−0,350, −0,034] | **−0,323 [−0,487, −0,157]** |

Terzo incontro col fenomeno, dopo ORB e le finestre disomogenee del TSMOM. **Ma qui il segno è
rovesciato**: l'ORB era *negativo pre-2020 e positivo post-2020*; questo è *piatto pre-2020 e
significativamente peggiore del random post-2020*.

**Lettura.** Se esistesse un "regime post-2020" che rende buoni i risultati, dovrebbe spingere nella
stessa direzione strategie della stessa famiglia. Due breakout (uno intraday su indici, uno
giornaliero multi-asset) che si spezzano in **direzioni opposte** alla stessa data sono più coerenti
con **due estrazioni di rumore** che con una rottura di microstruttura — esattamente la tesi di
[[feedback_backtest_long_history_falsification]]. Non è una prova, ma **sposta il prior**: rafforza
la decisione di lasciar correre il forward ORB, che resta l'unico modo di risolverlo davvero.

---

## Q2 — Il playground: **SUPPORTATO** (regola pre-registrata) → **LEAD**

Spearman fra volatilità realizzata media di gruppo ed E[R] medio, **n = 8 gruppi**:

| gruppo | vol ann. | E[R] reale | E[R] random | **differenza** |
|---|---|---|---|---|
| fx_cross | 8,1% | −0,524 | −0,092 | **−0,431** |
| bond | 8,2% | +0,166 | +0,206 | −0,040 |
| fx_major | 8,3% | −0,397 | +0,072 | **−0,469** |
| index | 21,0% | −0,120 | +0,131 | −0,251 |
| metal | 25,5% | +0,464 | +0,199 | +0,264 |
| agri | 28,9% | +0,242 | +0,054 | +0,188 |
| energy | 51,2% | +0,396 | +0,280 | +0,116 |
| crypto | 63,5% | +1,099 | +0,285 | **+0,814** |

- **Primario**: ρ = **+0,857**, p(perm) = **0,0060** → soglia pre-registrata superata.
- **C1 — canale meccanico**: il random da solo mostra ρ = +0,619 (p = 0,062) → **una parte
  dell'effetto è meccanica** (vol-of-vol + uscita asimmetrica gonfiano gli R sugli asset volatili).
  Il test **controllato** sulla differenza reale−random tiene comunque: ρ = **+0,786**, p = **0,0135**.
- **C3 — rumore**: bootstrap ricampionando gli **strumenti dentro i gruppi** → ρ mediano +0,786,
  CI95 [+0,476, +0,952], **P(ρ>0) = 100%**. Togliendo la crypto: ρ +0,786 p = 0,023. Togliendo
  crypto **ed** energia: ρ +0,771 p = 0,050. **Non è trainato da un solo gruppo.**

### Perché è un LEAD e non un GO — i caveat che devono viaggiare col risultato

1. **C2 — è in larga parte un fenomeno del lato lungo.** Solo **3 gruppi su 8** sono positivi su
   **entrambi** i lati. Su metalli (BUY +0,640 / SELL +0,017), agri (+0,577 / −0,236) e bond
   (+0,747 / −0,117) il risultato è quasi tutto long, in una finestra in cui oro, cacao, caffè,
   energia e crypto sono saliti molto. Il baseline random controlla il drift solo in parte.
2. **Solo 2 gruppi su 8** hanno E[R] individualmente significativo positivo (crypto [+0,42, +1,96],
   metalli [+0,05, +1,02]); agri, bond, energy, index includono lo zero.
3. **n = 8 punti.** Il test può cogliere solo un ordinamento forte, come dichiarato prima.
4. **La finestra W2 è per ~2/3 post-2020**, cioè il periodo in cui W3 dice che la regola fa
   *peggio* del random. Il gradiente è un'affermazione **relativa** dentro una finestra dove il
   livello assoluto è cattivo.
5. **La mia pre-registrazione non ha definito un holdout sigillato per Q2.** È una lacuna reale: il
   risultato è in-sample sulla finestra scelta e **non ha superato un gate G2**.

**Cosa significa davvero.** *Non* significa "abbiamo un edge su crypto e commodities" — la regola
Donchian è NO-GO. Significa che **il campo su cui abbiamo cercato per un anno è il peggiore
possibile**: sui major FX la stessa regola fa **−0,47R peggio del random**, sui gruppi volatili fa
meglio. È una spiegazione ex-ante della nostra serie di null, arrivata da una fonte che i nostri dati
non li ha mai visti — e resta valida come **direzione di ricerca**, non come strategia.

---

## Contabilità

- **Trial**: 12 dichiarati (4 uscite × 3 lookback). Famiglia trend **round 2 di 3** (round 1 = TSMOM
  canonico). DSR non calcolato: Q1 è già NO-GO per kill-switch e la deflazione può solo peggiorarlo.
- **Budget fonti esterne**: **2ª di 2-3** del trimestre.
- **Asset riusabili**: feed Dukascopy D1 omogeneo a 27 strumenti su 8 classi (**bond, energia,
  agricoli e metalli industriali entrano per la prima volta nel workspace**), motore Donchian
  multi-uscita con baseline oracolo + random.

## Cosa NON è stato fatto

Nessun holdout sigillato per Q2; nessun forward. Se il playground va perseguito, richiede una
**pre-registrazione propria** con G2 e validazione indipendente — non è promuovibile così.
