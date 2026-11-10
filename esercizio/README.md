# esercizio — cio' che gira con soldi veri o in demo

Quarta macro del repo, in ordine di processo (DECISIONS 2026-11-09): qui sta cio' che **esegue** dopo un verdetto, e
la sua sorveglianza. Gli studi che hanno portato fin qui (pre-registrazioni, referti) restano nel registro.

**Stato al 09/11/2026:** gira solo il **PAC**, sul broker e fuori dal repo. Nessun EA e' acceso; il copier e' fermo
(test di esecuzione CLOSED il 13/10). Lo stato vero si legge alla fonte, non qui (sotto, regola 1).

| Cartella | Cosa contiene | Come si usa |
|---|---|---|
| [`mql5/`](mql5/README.md) | Expert Advisor MQL5, tutti spenti e conservati come storia; guida di conversione | l'agente `mql5-converter` legge [`mql5/CONVERSION_GUIDE.md`](mql5/CONVERSION_GUIDE.md) |
| [`signal_copier/`](signal_copier/README.md) | copia dei segnali Telegram → MT5 | `python -m esercizio.signal_copier ...` dalla radice di `trad`; la guida di installazione sul VPS (`esercizio/signal_copier/VPS_COPIER_SETUP.md`) e' fuori da git |
| `sorveglianza/` | script di controllo di cio' che gira e i loro report datati (`report/`) | `python esercizio/sorveglianza/weekly_healthcheck.py`, `deployment_healthcheck.py`, `report_socio.py` |
| [`pac/`](pac/INVESTING_PILLAR_PLAN.md) | il piano operativo del PAC | revisione una volta l'anno, a settembre |
| [`prop/`](prop/PROP_FIRM_CRITERIA.md) | i criteri nostri per scegliere una prop e i regolamenti letti | nessuna decisione con soldi finche' gli URL dei regolamenti non sono verificati |

## Regole

1. **Lo stato di un sistema si verifica alla fonte**: MT5 (magic, storico, ordini e posizioni) o il broker, con la
   finestra dichiarata. Un report del repo e' una fotografia, non lo stato.
2. **Mai live senza risk gate**; `paper_mode` di default ([CONVENTIONS](../motore/CONVENTIONS.md)).
3. **Si entra qui solo dopo un verdetto**, con la sorveglianza scritta in codice
   ([STRATEGY_LIFECYCLE §8bis](../motore/metodo/STRATEGY_LIFECYCLE.md)).
4. **Quando un sistema si spegne**, la decisione va in `DECISIONS.md` e il README della sua cartella lo dice in testa
   ("⚠️ Superato").
