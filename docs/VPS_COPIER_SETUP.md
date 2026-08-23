# Setup VPS per il signal copier — guida passo passo

> Obiettivo: copier attivo **24/7** su demo, per raccogliere i dati del test di esecuzione
> ([COPIER_EXECUTION_PREREGISTRATION.md](COPIER_EXECUTION_PREREGISTRATION.md)).
> Ogni fase finisce con una **verifica**: se non passa, non si va avanti.
>
> Scritta 2026-08-14. Il copier gira su conto e macchina **separati** dal forward test degli EA.

---

## 0. Scelta del VPS

| Requisito | Valore |
|---|---|
| Sistema | **Windows Server** (2019/2022) — MT5 e il pacchetto Python sono Windows-only |
| CPU / RAM | 2 vCPU / **4 GB** |
| Disco | 60 GB SSD |
| Costo atteso | **~13-15 €/mese** |

⚠️ **Non serve un "forex VPS" a bassa latenza** (30-40 €/mese). Quelli vendono latenza
sub-millisecondo verso i server broker: il nostro edge sopravvive fino a **60 minuti** di ritardo
(misurato nell'audit), quindi la latenza è irrilevante. Serve solo che la macchina sia **sempre
accesa**.

⚠️ **Evitare i VPS Linux economici** (es. Contabo): la licenza Windows si paga a parte (~19 $/mese) e
il totale supera i 45. MT5 sotto Wine è instabile.

---

## 1. Primo accesso

1. Ordina il VPS, annota **IP**, **utente** (di solito `Administrator`) e **password**.
2. Da Windows: `Win+R` → `mstsc` → inserisci l'IP → Connetti → credenziali.

> **Regola d'oro per tutta la vita del VPS**: quando hai finito, chiudi la finestra RDP con la **X**
> (disconnetti). **Non fare "Disconnessione" / "Log off"**: il logoff termina la sessione utente e
> **chiude MT5**, fermando tutto in silenzio. È l'errore più comune sui VPS di trading.

**Verifica**: ti connetti e vedi il desktop.

---

## 2. Blindare il sistema (10 minuti, evita il 90% dei guasti)

### 2a. Windows Update — il riavvio non richiesto è il killer numero uno

*Impostazioni → Windows Update → Opzioni avanzate*:
- Attiva **"Ore di inattività"** il più ampio possibile.
- Disattiva **"Riavvia il dispositivo il prima possibile"**.

Non serve bloccare gli aggiornamenti: serve che **non riavviino da soli**. Al §6 configuriamo
comunque la ripartenza automatica dopo un riavvio, così anche nel caso peggiore si riprende da solo.

### 2b. Niente sospensione

*Impostazioni → Sistema → Alimentazione* → **Mai** su schermo e sospensione.

### 2c. Fuso orario: UTC

*Impostazioni → Data/ora* → fuso **(UTC) Coordinated Universal Time**, disattiva l'ora legale
automatica.

> Perché UTC: i timestamp dei log e del journal devono essere confrontabili con le serie prezzi e con
> i messaggi Telegram. Il 2026-08-07 un disallineamento di **un'ora** tra fusi ha prodotto uno scarto
> mediano di $10,53 nell'analisi dei segnali e ha invalidato una prima lettura dei risultati. Un
> fuso ambiguo è un bug che si paga dopo.

**Verifica**: `Get-TimeZone` in PowerShell restituisce UTC.

---

## 3. MetaTrader 5

1. Scarica MT5 (dal sito MetaQuotes o dal broker) e installa con percorso **predefinito**.
2. Accedi al conto demo: **5054470558**, server **MetaQuotes-Demo**.
3. *Strumenti → Opzioni → Expert Advisors* → spunta **"Consenti trading algoritmico"**.
4. Nel **Market Watch**: tasto destro → *Mostra tutto*, poi assicurati che **XAUUSD** sia presente e
   mostri **bid/ask vivi** (non 0).
5. Annota il percorso di `terminal64.exe` (di norma `C:\Program Files\MetaTrader 5\terminal64.exe`).

**Verifica**: XAUUSD quota in tempo reale e in basso a destra la connessione mostra i kb/s.

---

## 4. Python e dipendenze

1. Installa **Python 3.12** da python.org — spunta **"Add python.exe to PATH"**.
2. In PowerShell:

```powershell
pip install MetaTrader5 telethon python-dotenv pyyaml pandas yfinance
```

> Sono le dipendenze **effettive** del copier, non l'intero `pyproject.toml` (che tira dentro scipy,
> ib-insync e altro inutile qui). `pandas`/`yfinance` entrano dalla catena di import di `brokers/`.

> ⚠️ **NON installare il pacchetto PyPI `notifiers`** (era in questo elenco fino al 2026-08-22, ed è
> un errore che rompe l'avvio). `notifiers` è un **package locale del repo** (`notifiers/_pip_table.py`,
> importato da `signal_copier/planner.py`) e **non ha `__init__.py`**: è un namespace package PEP 420.
> Un package regolare con lo stesso nome in `site-packages` ha la **precedenza** su un namespace
> package, quindi installandolo l'import si risolve su quello sbagliato e fallisce con
> `ModuleNotFoundError: No module named 'notifiers._pip_table'`. Se è già installato:
> `pip uninstall -y notifiers`.

**Verifica**:

```powershell
python -c "import MetaTrader5, telethon, yaml, dotenv; print('deps ok')"
```

---

## 5. Progetto, segreti e sessione

### 5a. Codice

Copia sul VPS le cartelle `signal_copier/`, `brokers/`, `core/` e il file `pyproject.toml`
(via clipboard RDP o `git clone` se hai un remoto). Suggerito: `C:\trading\`.

### 5b. Segreti — **mai** via git

`.env` e i file `.session` sono gitignored: vanno trasferiti a mano (copia/incolla RDP).
Nel `.env` sul VPS servono solo:

```
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELEGRAM_SESSION=signal_copier
MT5_DEMO3_LOGIN=5054470558
MT5_DEMO3_PASSWORD=...
MT5_DEMO3_SERVER=MetaQuotes-Demo
```

### 5c. Sessione Telethon — **creala sul VPS, non copiarla**

```powershell
cd C:\trading
python -m signal_copier.login
```

> ⚠️ **Non copiare** `signal_copier.session` dal PC. La stessa sessione usata da due IP diversi può
> essere **revocata da Telegram** — ed è già successo una volta (sessione dell'8 giugno terminata per
> inattività). Meglio una sessione dedicata al VPS.
>
> Il codice **non arriva per SMS** se hai altre sessioni attive: lo trovi nella chat ufficiale
> **"Telegram"** (spunta blu) dentro l'app.

**Verifica**: lo script stampa il tuo nome utente e l'elenco dei canali XAU visibili —
`XAUUSD_AnalysisLab` deve comparire.

### 5d. Configurazione

In `signal_copier/config.yaml` allinea `terminal_path` al percorso del VPS (§3.5):

```yaml
terminal_path: "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
```

**Verifica**: `python -m signal_copier dryrun --channel xauusd_analysislab --samples signal_copier/samples/xau_analysis_lab.txt`
→ deve chiudere con *"Dry-run completato: 8 messaggi processati"*.

---

## 6. Avvio automatico e resistenza ai guasti

Il reader usa `run_until_disconnected()`: Telethon si riconnette da solo sui cali di rete, ma su una
**disconnessione piena il processo esce**. Serve supervisione dal sistema operativo.

### 6a. Wrapper con riavvio automatico

Crea `C:\trading\run_copier.bat`:

```bat
@echo off
cd /d C:\trading
:loop
echo [%date% %time%] avvio copier >> logs\supervisor.log
python -m signal_copier live --mode %COPIER_MODE%
echo [%date% %time%] copier uscito (codice %errorlevel%), riavvio tra 60s >> logs\supervisor.log
timeout /t 60 /nobreak > nul
goto loop
```

La pausa di 60 secondi evita che un errore sistematico martelli il server. `supervisor.log` registra
ogni riavvio: **se si riempie, è il sintomo di un problema**, non un dettaglio.

Imposta la modalità (`dry_run` per la fase di validazione, `live` dopo):

```powershell
setx COPIER_MODE dry_run
```

### 6b. Avvio al riavvio della macchina

*Utilità di pianificazione* → **Crea attività**:
- **Generale**: "Esegui solo se l'utente ha eseguito l'accesso" (MT5 è un'app grafica e richiede la
  sessione desktop attiva). Nome: `copier`.
- **Attivazione**: *All'accesso*.
- **Azioni**: avvia `C:\trading\run_copier.bat`.
- **Condizioni**: togli la spunta *"Avvia solo se il computer è alimentato a corrente alternata"*.
- **Impostazioni**: spunta *"Se l'attività non riesce, riavvia ogni"* → 1 minuto, fino a 3 volte.

Aggiungi anche MT5 all'avvio: `Win+R` → `shell:startup` → crea un collegamento a `terminal64.exe`.

**Verifica**: riavvia il VPS, riconnettiti dopo qualche minuto e controlla che MT5 sia aperto e
`supervisor.log` mostri un avvio recente.

---

## 7. Sequenza di go-live

Nell'ordine, senza saltare passaggi.

| Fase | Durata | Comando | Cosa si verifica |
|---|---|---|---|
| **1. Dry-run** | 3-5 giorni | `COPIER_MODE=dry_run` | Ogni messaggio del canale è parsato bene: segnali, `TP1 SUCCESSFUL`, `Close your trades`. Nessun ordine aperto |
| **2. Smoke test** | 1 segnale | `live` | 3 gambe con ticket distinti, SL/TP armati sul broker, BE dopo TP1, flatten su `Close` |
| **3. Live** | 8 settimane / 60 trade | `live` | Parte il conteggio della pre-registrazione |

Il **dry-run non è una formalità**: il parser è stato validato su messaggi di **giugno**, e
nell'export di agosto compaiono formati nuovi (inclusi messaggi promozionali da ignorare). Se un
`TP1 SUCCESSFUL` non viene riconosciuto, il break-even non scatta.

---

## 8. Monitoraggio settimanale

```powershell
python analysis/ops/deployment_healthcheck.py 7
```

Da lanciare **sul VPS** (si aggancia al terminale in esecuzione). Nota che `EXPECTED_LOGIN` nello
script punta al conto degli EA: sul VPS del copier segnalerà "conto sbagliato" — è corretto, lì
guardi altro.

Cosa controllare ogni settimana:
- `logs/supervisor.log` — riavvii frequenti = problema da indagare
- `logs/signal_copier_journal.jsonl` — segnali accettati e scartati, con `slip_pips`
- `logs/messages_received.jsonl` — messaggi non parsati
- MT5: la connessione al server è viva

---

## 9. Modi di rottura noti — e cosa li tradisce

| Guasto | Sintomo | Prevenzione |
|---|---|---|
| Logoff invece di disconnessione RDP | Tutto fermo, nessun errore | §1: chiudi con la **X** |
| Riavvio da Windows Update | Buco nei log, poi ripartenza | §2a + §6b |
| Sessione Telethon revocata | `is_user_authorized() = False`, nessun messaggio ricevuto | §5c, sessione dedicata |
| Conto demo scaduto per inattività | `Invalid account` al login MT5 | Il copier attivo lo tiene vivo da solo |
| Simbolo con suffisso diverso | Ordini rifiutati, storico vuoto | `symbol_overrides` in `config.yaml` |
| Margine insufficiente | `[No money]`, dropout **non casuale** | Rischio 1% su 100k demo: ampio margine |

> Il filo comune: **quasi tutti si manifestano come assenza di qualcosa**, non come un errore. È il
> motivo per cui il monitoraggio guarda cosa *manca*, non cosa c'è.
