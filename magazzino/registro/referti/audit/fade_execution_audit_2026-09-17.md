# Audit di esecuzione FADE (magic 26071)

Generato il 2026-09-17. Protocollo: docs/FADE_LIVE_AUDIT_PROTOCOL.md

**Questo report non contiene P&L, per costruzione.** Misura la conformita'
dell'esecuzione alla spec congelata, non il risultato della strategia.

> ATTENZIONE: simboli fuori dall'universo pre-registrato: BTCUSD, EURGBP.r

## Conteggi per fase

| fase | ingressi | pendenti | a mercato |
|---|---|---|---|
| prima del 2026-08-13 | 11 | 6 | **5** |
| dopo 2026-08-13 (riaggancio simboli .r + stacco BTCUSD (prereg sez.9)) | 27 | 18 | **9** |
| dopo 2026-08-27 (fix pendenti orfani / strumento congelato (prereg sez.10)) | 49 | 25 | **24** |
| dopo 2026-09-17 (v1.10: rimosso l'ingresso a mercato, setup saltato (SKIP)) | 3 | 1 | **2** |

## Verifiche

| # | verifica | conformi | non conformi | non valutabili |
|---|---|---|---|---|
| V1 | tipo di ordine e' pendente **FALLITA** | 50 | 40 | 0 |
| V2 | fill al prezzo pre-registrato | 50 | 0 | 40 |
| V3 | rischio reale = rischio inteso **FALLITA** | 51 | 39 | 0 |
| V4 | rapporto SL/TP = 1:3 **FALLITA** | 51 | 39 | 0 |
| V5 | un solo setup attivo per strumento **FALLITA** | 89 | 1 | - |

## V6 - selezione del campione

Setup entrati a mercato, cioe' che la regola pre-registrata **non avrebbe
preso**: **40 su 90** (44%).

Ognuno ha occupato lo slot dello strumento (un solo setup attivo), quindi
ha impedito i setup successivi. Il ramo pendente non e' un sottoinsieme
casuale: e' il complemento di questa selezione (protocollo sez.3).

## Multipli di rischio piu' alti osservati

Il rischio inteso e' ricostruito da |tp - sl| / 4, cioe' la distanza su cui
l'EA ha dimensionato il volume. Un multiplo di 2,00x significa che il conto
ha rischiato il doppio dell'1% previsto su quel trade.

| simbolo | data | ingresso | rischio reale / inteso | RR reale |
|---|---|---|---|---|
| XAUUSD.cyr | 2026-08-13 12:32 | mercato | **4.01x** | 1:0.00 |
| US100 | 2026-07-31 04:00 | mercato | **3.95x** | 1:0.01 |
| US100 | 2026-08-31 05:00 | mercato | **3.84x** | 1:0.04 |
| US100 | 2026-07-31 01:47 | mercato | **3.74x** | 1:0.07 |
| EURUSD.r | 2026-09-08 17:00 | mercato | **3.70x** | 1:0.08 |
| US100 | 2026-09-01 21:00 | mercato | **3.63x** | 1:0.10 |
| XAUUSD.cyr | 2026-08-13 11:00 | mercato | **3.62x** | 1:0.11 |
| XAUUSD.cyr | 2026-08-13 15:00 | mercato | **3.51x** | 1:0.14 |

Trade che hanno rischiato piu' del previsto: **39 su 90**, fino a **4.01x**.

## Come si legge questo report

Se V1 non e' 100% conforme, i trade raccolti **non sono la strategia**
pre-registrata e il campione non serve a stimare E[R], ne' ora ne' mai
(protocollo sez.5). Nessun ramo di questo audit puo' produrre un GO.
