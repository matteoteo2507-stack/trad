---
tipo: referto
stato: da_decidere
aggiornato: 2026-09-30
decisione: "DECISIONS 2026-09-30 (round 3 assegnato a B2, potenza prima di spenderlo)"
metrica_corrente: "X=5: MDE 0,092-0,184 ATR contro costo 3x 0,081-0,099 → sotto potenza in ogni universo"
nota: "0 trial. Nessuna media direzionale calcolata. Motore: analysis/trend/b2_potenza.py"
---
# B2 — breakout Kichev: il test puo' vedere un effetto che conti? (passo 0, 0 trial)

> Richiesto dal quant-gatekeeper (parere del 29/09) prima di spendere il **round 3 di
> `trend_momentum`**, che l'utente ha assegnato a B2 il 30/09 (DECISIONS). Regola fissata prima:
> **se l'MDE del primario supera l'effetto minimo economico (il costo a 3x), il round non si spende** e
> B2 si chiude a 0 trial come *"non testabile a potenza utile"*, non come falsificata.

## Cosa e' stato misurato, e cosa no

Motore: [`analysis/trend/b2_potenza.py`](../analysis/trend/b2_potenza.py), feed Dukascopy D1 con il
loader che fonde il weekend. **Nessuna media direzionale** degli eventi e' stata calcolata: la varianza
viene dal **quadrato** del movimento dopo il trigger, identico per long e short, e dal quadrato del
movimento su tutti i giorni (controlli a lato casuale). L'ipotesi — dopo un breakout il prezzo
**continua** — resta non vista.

Specifica usata (scelte **nostre**; la fonte da' solo esempi: *"your sixth candle will move by 2%"*,
*"you have to do your research"*): range H-L ≥ 2 × media delle 5 barre precedenti; direzione = colore
della barra; ingresso all'apertura del giorno dopo, uscita a tempo dopo X giorni, nessuno stop; unita'
ATR(20); 3 controlli per evento; costo per gruppo di `analysis/trend/backtest.py`.

## Risultato (30/09/2026)

MDE in ATR sulla differenza appaiata (evento − media di 3 controlli), fattore 2,80 (alpha 5%, potenza
80%). "Per data": una sola osservazione per giorno con trigger, limite prudente per eventi simultanei.

| X | universo | strumenti | eventi | date | MDE indip. | MDE per data | costo 3x |
|---|---|---|---|---|---|---|---|
| **5** | tutti | 27 | 3.830 | 1.700 | 0,092 | 0,138 | 0,087 |
| **5** | fonte (commodities + crypto) | 13 | 1.812 | 1.174 | 0,140 | 0,174 | 0,081 |
| **5** | fonte senza crypto | 11 | 1.297 | 920 | 0,155 | 0,184 | 0,099 |
| 2 | tutti | 27 | 3.830 | 1.700 | **0,059** | 0,088 | 0,087 |
| 2 | fonte (commodities + crypto) | 13 | 1.812 | 1.174 | 0,087 | 0,108 | 0,081 |
| 2 | fonte senza crypto | 11 | 1.297 | 920 | 0,103 | 0,122 | 0,099 |

27 strumenti, non 30: la regola di copertura (inizio dopo il 2018-01-01) esclude USTBOND, XPT, XPD.

## Lettura

1. **Con X = 5, il primario proposto, il test e' sotto potenza in ogni universo**: l'MDE supera il costo
   a 3x anche contando gli eventi come indipendenti.
2. **L'unica configurazione con potenza sufficiente e' X = 2 su tutti gli strumenti**, e solo contando
   gli eventi come indipendenti (0,059 contro 0,087); con un'osservazione per data e' in pareggio (0,088).
3. Ma "tutti gli strumenti" comprende **FX e indici (47% degli eventi), dove Kichev stesso esclude il
   momentum breve** (`blocco-D.md`, 105-111, via gatekeeper). Un nullo su quell'universo **non falsifica la
   fonte**; nel suo universo (commodities + crypto) il test **non ha potenza** a nessun orizzonte.
4. Contaminazione gia' dichiarata: B3 ha misurato sugli stessi dati la continuazione dopo grandi movimenti
   (+0,011 a h = 2, MDE 0,106). L'esito massimo di B2 resta **LEAD**.

## Le strade (decisione dell'utente)

| strada | cosa succede | costo |
|---|---|---|
| **A — chiudere B2 a 0 trial** come "non testabile a potenza utile nell'universo della fonte" | il round 3 **non si spende** e resta alla famiglia (tornerebbe disponibile per A1 punto 3, che pero' e' fermo per potenza anch'esso) | nessuno |
| **B — spendere il round su X = 2, tutti gli strumenti** | test con potenza, ma su un universo che la fonte esclude: un nullo non la falsifica, un positivo vale al massimo LEAD. Se fallisce: famiglia chiusa, con A1 e D4 | round 3 + 1 slot esterno del Q4 |
| **C — spendere il round su X = 2, universo della fonte** | fedele alla fonte ma **sotto potenza** (0,087-0,108 contro 0,081): un nullo sarebbe "non dimostrato", e chiuderebbe la famiglia comunque | round 3 + 1 slot, con un esito che non decide |

**Raccomandazione di Claude: A.** La regola scritta prima dice di non spendere; B testa una domanda che
non e' quella della fonte e C spenderebbe l'ultimo round per un "non dimostrato". Riapertura di B2:
forward (~270 eventi l'anno sui 27 strumenti: anni) oppure un feed con piu' strumenti indipendenti ad
alta volatilita' (riga G9 del backlog), che servirebbe anche ad A1.
