# Guida operativa — Deploy e workflow weekly

> Documento step-by-step per portare il workspace dal PC di casa al deploy ibrido cloud-native (post-pivot 2026-05-05). Include: deploy Componente 1 su VPS Linux, deploy Componente 2 (EA MQL5) su demo locale e poi MetaQuotes VPS, workflow weekend con Stock Selector.

## Indice

1. [Componente 1 — Confluence Levels su VPS Linux](#componente-1)
2. [Componente 2 — London Breakout EA su MT5 demo](#componente-2)
3. [Componente 2.5 — Migrazione a MetaQuotes VPS](#componente-25)
4. [Workflow weekend — Stock Selector e levels.yaml](#workflow-weekend)
5. [Cheatsheet comandi](#cheatsheet)

---

## Componente 1 — Confluence Levels su VPS Linux <a id="componente-1"></a>

### A. Scelta del provider VPS

Tre opzioni reali. Sceglierne una sola.

| Opzione | Costo | Pro | Contro |
|---|---|---|---|
| **Oracle Cloud Always Free** | 0€ | Gratis a vita, 4 ARM cores + 24GB RAM, niente carta scadenze | Account verification a volte rifiuta utenti EU; provisioning in regioni a volte sature |
| **Hetzner CX11** | ~3.5€/mese | Setup velocissimo (3 minuti), datacenter Falkenstein/Helsinki, fatturazione trasparente | Non gratis |
| **fly.io free tier** | 0€ (3 small VMs gratis) | Deploy via Dockerfile, scaling automatico | Curva d'apprendimento Docker, può cambiare i limiti free |

**Raccomandazione**: parti con **Hetzner CX11** se vuoi minimizzare l'attrito. 1 caffè al mese, setup in 30 minuti totali.

### B. Step Hetzner CX11 — provisioning

1. Vai su [console.hetzner.cloud](https://console.hetzner.cloud) → registrati (richiede SEPA o carta). Verifica email.
2. Click "New Project" → nome a piacere (es. `trading`).
3. Click "Add Server":
   - **Location**: Falkenstein (Germania) — vicino e veloce.
   - **Image**: Ubuntu 24.04 LTS.
   - **Type**: CX11 (1 vCPU, 2GB RAM, 20GB SSD, 20TB traffic) — €3.29/mese.
   - **SSH Keys**: aggiungi la tua chiave pubblica. Se non l'hai mai generata, su Windows PowerShell:
     ```powershell
     ssh-keygen -t ed25519 -C "matteoteo2507@gmail.com"
     # accetta default path: C:\Users\mmbus\.ssh\id_ed25519
     # passphrase a tua scelta (anche vuota)
     cat C:\Users\mmbus\.ssh\id_ed25519.pub
     ```
     Copia l'output e incollalo nel campo SSH Key di Hetzner.
   - **Cloud config / volume / firewall**: salta tutto.
   - **Name**: `trad-confluence`.
   - Click "Create & Buy now".
4. Dopo 30s, dashboard mostra l'IP pubblico, es. `95.217.123.45`. Annotalo.

### C. Primo accesso al VPS

Da PowerShell di Windows:

```powershell
ssh root@95.217.123.45
# accetta fingerprint la prima volta
```

Una volta dentro:

```bash
# Update sistema
apt update && apt upgrade -y

# Crea utente non-root (best practice security)
adduser matteo
usermod -aG sudo matteo

# Copia la chiave SSH dal root al nuovo user
mkdir -p /home/matteo/.ssh
cp ~/.ssh/authorized_keys /home/matteo/.ssh/
chown -R matteo:matteo /home/matteo/.ssh
chmod 700 /home/matteo/.ssh
chmod 600 /home/matteo/.ssh/authorized_keys

# Disabilita login root via SSH (security hardening base)
sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh

# Esci e rientra come matteo
exit
```

Da PowerShell:

```powershell
ssh matteo@95.217.123.45
```

### D. Installa Python e dipendenze base

```bash
sudo apt install -y python3 python3-pip python3-venv git tmux
python3 --version  # deve essere 3.12+
```

### E. Carica il workspace sul VPS

**Opzione 1 — via GitHub** (consigliata se vuoi usare git per i deploy futuri):

1. Sul tuo PC Windows, crea un repo privato su github.com (es. `trad`).
2. Push del workspace locale:
   ```powershell
   cd c:\Users\mmbus\Desktop\lavoro\trad
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/<tuo-user>/trad.git
   git push -u origin main
   ```
3. Sul VPS:
   ```bash
   cd ~
   git clone https://github.com/<tuo-user>/trad.git
   cd trad
   ```

**Opzione 2 — via SCP** (più rapido se non vuoi git ora):

Da PowerShell di Windows:
```powershell
cd c:\Users\mmbus\Desktop\lavoro
scp -r trad matteo@95.217.123.45:~/
```

Sul VPS poi:
```bash
cd ~/trad
```

### F. Setup ambiente Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install yfinance pandas pydantic pyyaml typer rich python-dotenv requests pytest scipy
```

(In alternativa, se hai poetry o un `requirements.txt` definitivo, usalo. Se vuoi che lo crei ora, dimmelo).

### G. Configura `.env` sul VPS

Il file `.env` non viene committato, quindi va creato a mano:

```bash
nano .env
```

Incolla:
```
TELEGRAM_BOT_TOKEN=7840693535:AAHmocfjx9hb6DbGaH9pOIZFXkgwQSkwlDM
TELEGRAM_CHAT_ID=1238922215
LOG_LEVEL=INFO
LOG_DIR=./logs
```

`Ctrl+O`, Enter, `Ctrl+X`.

Tutte le altre variabili MT5/Alpaca/Binance non servono perché su VPS Linux fai solo Confluence con yfinance.

### H. Carica `levels.yaml`

`levels.yaml` è gitignored quindi non c'è. Crealo:

```bash
nano strategies/confluence_levels/levels.yaml
```

Incolla il contenuto del tuo `levels.yaml` locale (compilato durante il weekend).

### I. Prima esecuzione test

```bash
python -m strategies.confluence_levels validate-levels
python -m strategies.confluence_levels run --once --verbose
```

Atteso: una sola passata, log verbose, messaggio Telegram di start e poi di stop.

Se ricevi i messaggi Telegram, è tutto a posto.

### J. Far girare il runner H24 — `tmux`

```bash
tmux new -s confluence
source venv/bin/activate
python -m strategies.confluence_levels run
# vedi i log scorrere in console
# Ctrl+B poi D = "detach" (lascia il runner girare in background)
```

Per riattaccarti al runner:
```bash
tmux attach -t confluence
```

Per stoppare il runner: dentro tmux, `Ctrl+C`. Poi `exit`.

### K. (Opzionale) systemd unit per auto-restart al boot

Soluzione più professionale di tmux: il runner riparte da solo se il VPS si riavvia.

```bash
sudo nano /etc/systemd/system/confluence.service
```

Incolla:
```ini
[Unit]
Description=Confluence Levels Runner
After=network.target

[Service]
Type=simple
User=matteo
WorkingDirectory=/home/matteo/trad
Environment="PATH=/home/matteo/trad/venv/bin"
ExecStart=/home/matteo/trad/venv/bin/python -m strategies.confluence_levels run
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

`Ctrl+O`, Enter, `Ctrl+X`. Poi:

```bash
sudo systemctl daemon-reload
sudo systemctl enable confluence
sudo systemctl start confluence
sudo systemctl status confluence  # verifica che sia "active (running)"
```

Per vedere i log live:
```bash
journalctl -u confluence -f
```

Per stoppare:
```bash
sudo systemctl stop confluence
```

### L. Update `levels.yaml` ogni weekend

Ogni domenica, dopo aver compilato il file in locale:

```powershell
# Da PowerShell Windows
scp c:\Users\mmbus\Desktop\lavoro\trad\strategies\confluence_levels\levels.yaml matteo@95.217.123.45:~/trad/strategies/confluence_levels/levels.yaml
```

Il runner rilegge il file al ciclo successivo (entro 60s). Niente restart necessario.

Se preferisci usare git: `git push` da locale, poi `git pull` sul VPS, restart del service.

---

## Componente 2 — London Breakout EA su MT5 demo <a id="componente-2"></a>

### A. Trova la cartella MQL5 Data Folder del tuo terminale

1. Apri MT5 desktop sul demo MetaQuotes (DEMO2).
2. Menu `File → Open Data Folder`. Si apre Esplora Risorse a un path tipo:
   ```
   C:\Users\mmbus\AppData\Roaming\MetaQuotes\Terminal\<HASH>\
   ```
3. Annotati questo path. Dentro c'è la cartella `MQL5/`.

### B. Copia i file dell'EA

Crea (se non esiste) la sottocartella `MQL5/Experts/TradingSystemWorkspace/` e copia:

```
DA: c:\Users\mmbus\Desktop\lavoro\trad\mql5\london_breakout.mq5
A:  <DataFolder>\MQL5\Experts\TradingSystemWorkspace\london_breakout.mq5
```

Crea (se non esiste) `MQL5/Include/TradingSystemWorkspace/` e copia:

```
DA: c:\Users\mmbus\Desktop\lavoro\trad\mql5\include\telegram.mqh
A:  <DataFolder>\MQL5\Include\TradingSystemWorkspace\telegram.mqh

DA: c:\Users\mmbus\Desktop\lavoro\trad\mql5\include\helpers.mqh
A:  <DataFolder>\MQL5\Include\TradingSystemWorkspace\helpers.mqh
```

**Importante**: nel file `london_breakout.mq5` ci sono due `#include`:
```cpp
#include "include/telegram.mqh"
#include "include/helpers.mqh"
```

Visto che ora gli `.mqh` sono in una cartella diversa (`Include` invece di `Experts/include`), devi cambiare gli include in:
```cpp
#include <TradingSystemWorkspace/telegram.mqh>
#include <TradingSystemWorkspace/helpers.mqh>
```

(Le parentesi angolari `<>` dicono al compilatore di cercare in `MQL5/Include/`.)

Salva.

### C. Compila l'EA

1. Apri MT5 desktop. Menu `Tools → MetaQuotes Language Editor` (o premi `F4`).
2. In MetaEditor, nella pannello sinistro "Navigator" naviga a `Experts/TradingSystemWorkspace/` e doppio click su `london_breakout.mq5`.
3. Premi `F7` per compilare. La barra in basso deve dire `0 errors, X warnings`.
4. Se ci sono **errors**, copiami il messaggio e li sistemiamo. Warnings sono ok.

### D. Abilita WebRequest verso Telegram

Sul terminale MT5:
1. `Tools → Options → Expert Advisors`.
2. Spunta:
   - ☑️ `Allow algorithmic trading`
   - ☑️ `Allow DLL imports`
   - ☑️ `Allow WebRequest for listed URL`
3. Clicca dentro la lista URL (è una textbox in basso). Aggiungi:
   ```
   https://api.telegram.org
   ```
4. Click `OK`.

### E. Aggancia l'EA al grafico GBPUSD M15

1. Apri un grafico **GBPUSD M15** (se non c'è, dal Market Watch click destro su GBPUSD → Chart Window, poi cambia timeframe a M15 dalla toolbar).
2. Nella Navigator (`View → Navigator` o `Ctrl+N`), espandi `Expert Advisors → TradingSystemWorkspace → london_breakout`.
3. Trascinalo sul grafico GBPUSD M15.
4. Si apre il dialogo **Inputs**. Imposta:

| Input | Valore |
|---|---|
| `InpAsiaStartHourUtc` / Min | 0 / 0 |
| `InpAsiaEndHourUtc` / Min | 7 / 0 |
| `InpEntryWindowEndHourUtc` / Min | 10 / 0 |
| `InpTimeStopHourUtc` / Min | 16 / 0 |
| `InpBreakoutBufferAtr` | 0.10 |
| `InpTpRMultiple` | 1.5 |
| `InpMaxRangeToAtrRatio` | 1.5 |
| `InpAtrPeriod` | 14 |
| `InpSkipNfp` | true |
| `InpFomcBlackoutDatesCsv` | (lascia il default) |
| `InpRiskPerTradePct` | 0.01 |
| `InpFallbackVolume` | 0.10 |
| `InpTelegramBotToken` | `7840693535:AAHmocfjx9hb6DbGaH9pOIZFXkgwQSkwlDM` |
| `InpTelegramChatId` | `1238922215` |
| `InpMagicNumber` | `26050` |
| `InpStrategyName` | `london_breakout` |

5. Tab **Common**: spunta `Allow algorithmic trading`. Click `OK`.

6. Verifica: in alto a destra del grafico GBPUSD M15 deve apparire **una faccia sorridente verde** (smiley happy). Se è triste o ha una croce rossa, AutoTrading globale è ancora off → click sul pulsante "Auto Trading" verde nella toolbar principale.

7. Subito dopo dovresti ricevere su Telegram:
   ```
   🚀 [london_breakout] EA avviato su GBPUSD
   ```

### F. Test in Strategy Tester (backtest)

1. Apri Strategy Tester: `View → Strategy Tester` o `Ctrl+R`.
2. **Expert**: seleziona `Experts\TradingSystemWorkspace\london_breakout`.
3. **Symbol**: `GBPUSD`.
4. **Period**: `M15`.
5. **Date**: ultimi 6 mesi.
6. **Modeling**: `Every tick based on real ticks`.
7. **Forward**: No.
8. **Inputs**: lascia i default che hai messo prima. Tieni `InpTelegramBotToken` vuoto durante il backtest, altrimenti riceverai 100 messaggi.
9. **Visual mode**: utile la prima volta per vedere visualmente i trade. Dopo lo disattivi per andare più veloce.
10. Click `Start`.

A fine test (10-30 min reali a seconda di tick density), tab **Backtest** in basso:
- Net profit, Profit factor, Total trades, Win rate, Max drawdown.
- **Atteso**: 60-120 trade in 6 mesi (10-20/mese), win rate 45-55%, profit factor > 1.0, max DD < 10%.

Se i numeri sono molto diversi: copiami lo screenshot del risultato e ne parliamo prima di andare live.

### G. Test demo live (1-2 settimane)

Dopo Strategy Tester promosso, lascia l'EA agganciato al grafico per **1-2 settimane** sul demo. Verifica ogni giorno:

| Cosa controllare | Dove |
|---|---|
| EA ancora attivo (smiley verde) | Grafico GBPUSD M15 |
| Stop orders piazzati alle 09:00 ora italiana (07:00 UTC) | Tab "Trade" del terminale |
| Notifica Telegram con BUY/SELL stop | Telegram |
| Cancellazione ordini alle 12:00 ora italiana se nessuno scatta | Tab "Trade" deve svuotarsi |
| Time stop alle 18:00 ora italiana se ho una posizione | Tab "History" |
| Skip in giorni NFP (primo venerdì) e FOMC | Telegram messaggio "⏭ skip" |

Annota su un file `notes/london_breakout_week1.md`:
- Trade aperti, P&L, durata.
- Falsi positivi/negativi.
- Eventuali errori MT5 (Journal tab).

---

## Componente 2.5 — Migrazione a MetaQuotes VPS <a id="componente-25"></a>

**Solo dopo** che l'EA ha girato 1-2 settimane sul demo locale senza problemi.

### A. Sottoscrivi VPS dal terminale

1. MT5 desktop (PC), barra in basso click destro su tab "Trade" → `Virtual Hosting → Register Virtual Server` (oppure menu `Tools → Virtual Hosting`).
2. Si apre un wizard. Scegli **regione** vicina al server del broker. Per AvaTrade tipicamente Londra; per MetaQuotes-Demo qualsiasi va bene.
3. Scegli piano (10$/mese standard, può variare). Inserisci metodo di pagamento.
4. **Subscribe**.

### B. Migra il terminale al VPS

1. Sempre dal wizard Virtual Hosting, click `Migrate to Virtual Server`.
2. Il terminale **trasferisce automaticamente**:
   - L'EA agganciato al grafico GBPUSD M15.
   - I parametri (Telegram token, ecc.).
   - La whitelist WebRequest (api.telegram.org).
3. Dopo qualche minuto: il VPS è in esecuzione con il tuo terminale clonato. Da quel momento il PC di casa può essere spento.

### C. Verifica che il VPS stia girando

1. Dall'app **mobile MT5** (iOS/Android, gratuita):
   - Login con le stesse credenziali del demo MetaQuotes.
   - Tab "Profile" o icona menu → "Virtual Server" / "VPS".
   - Vedi: stato online, EA attivi, tempo di uptime, equity attuale.
2. Click sul VPS → vedi log dell'EA, posizioni aperte, possibilità di stop/restart.

### D. Quando aggiornare l'EA dopo modifiche

Se modifichi `london_breakout.mq5` in locale:
1. Ricompila in MetaEditor.
2. Riavvia il terminale MT5 desktop.
3. Rimuovi l'EA dal grafico (clic destro → Expert Advisors → Remove).
4. Ritrascina l'EA dal Navigator. Stessi input.
5. Tools → Virtual Hosting → `Migrate to Virtual Server` di nuovo.

Le modifiche entrano in vigore sul VPS dopo qualche minuto.

---

## Workflow weekend — Stock Selector e levels.yaml <a id="workflow-weekend"></a>

Il sabato o domenica, dal **PC di casa** (acceso solo per questa sessione), fai due cose:

### A. Compila `levels.yaml` per la settimana entrante

Tempo stimato: 30-45 minuti.

1. Apri TradingView (browser, piano Free va bene).
2. Per ogni pair che monitori (`EURUSD`, `XAUUSD`):
   - Vista Monthly + Weekly: identifica le S/R major.
   - Scendi a H4/H1: identifica zone di Supply/Demand.
   - Aggiungi Fibonacci dell'ultimo swing significativo.
   - Marca i livelli dove convergono ≥ 2 criteri.
3. Apri `c:\Users\mmbus\Desktop\lavoro\trad\strategies\confluence_levels\levels.yaml`.
4. Aggiungi/aggiorna i livelli secondo il formato (vedi `levels.example.yaml` come riferimento). Ricorda:
   - `id` univoco per livello.
   - `confluence` ≥ 2 elementi.
   - `valid_until` = domenica successiva.
   - `tp_target_price` = prossimo livello strutturale.
5. Valida:
   ```powershell
   cd c:\Users\mmbus\Desktop\lavoro\trad
   python -m strategies.confluence_levels validate-levels
   ```
   Verifica che la tabella stampata sia tutta verde.

6. **Sincronizza sul VPS** (vedi sezione 1.L sopra):
   ```powershell
   scp strategies\confluence_levels\levels.yaml matteo@95.217.123.45:~/trad/strategies/confluence_levels/levels.yaml
   ```

Il runner sul VPS rilegge il file entro 60 secondi. Niente restart.

### B. Esegui Stock Selector

Tempo stimato: 5-10 minuti (download dati + analisi 503 ticker SP500).

1. Da PowerShell:
   ```powershell
   cd c:\Users\mmbus\Desktop\lavoro\trad
   ```

2. Decidi i due input macro:
   - **Risk-free rate** USA: il rendimento attuale del Treasury 10Y. Lo trovi su [investing.com](https://it.investing.com/rates-bonds/u.s.-10-year-bond-yield) o su TradingView ticker `US10Y`. È un numero tipo `4.2` (percentuale).
   - **Trend liquidità banche centrali**: stai guardando il bilancio aggregato (FED + ECB + BoJ). In espansione → `increasing`, in contrazione → `decreasing`. Se non hai una view, parti da `decreasing` (prudente, scenario "DEFENSIVE").

3. Lancia:
   ```powershell
   python -m strategies.stock_selector --risk-free 4.2 --liquidity decreasing
   ```

   Output console: scenario rilevato, progress bar download SP500, tabella delle Top Picks.

4. Output file:
   - `Top_Picks.xlsx` — i titoli con score ≥ 5 (formattati con highlight verde sui RRG=LEADING e Macro Match=SI).
   - `Analisi_Completa.xlsx` — tutti i 503 titoli ordinati.

5. Apri `Top_Picks.xlsx` in Excel. Tipicamente avrai 10-30 titoli. Filtra per:
   - **RRG Trend = LEADING** (sta sovraperformando il benchmark).
   - **TARGET MATCH = SI** (matcha lo scenario macro).
   - **Settori** che ti interessano (es. evita energy se sei convinto di un crollo del petrolio).

6. Da quella shortlist, eventualmente fai analisi qualitative (Damodaran, Buffett-style, ecc.) — questo è quello che diventerà Stage 4 con i 4 personas LLM.

7. Per ora: usi le top picks come **watchlist** da monitorare nella settimana, non come segnali di entry diretti. La Confluence sui forex è automatica per le notifiche; le azioni le tradi a mano se ti convince il contesto.

### C. (Opzionale) Workflow combinato

Se vuoi essere efficiente, fai il sabato pomeriggio in 1 ora:

1. Lancia Stock Selector mentre fai analisi grafici TradingView in parallelo (lo Stock Selector prende 5 minuti, tu sei già su TV a guardare i livelli).
2. Mentre Stock Selector finisce, finisci di compilare `levels.yaml` su TradingView.
3. Valida `levels.yaml`.
4. Sync sul VPS.
5. Apri Top_Picks.xlsx, ti fai una watchlist mentale per la settimana.

Spegni il PC di casa fino al weekend successivo.

---

## Cheatsheet comandi <a id="cheatsheet"></a>

### Locale (Windows PowerShell)

```powershell
cd c:\Users\mmbus\Desktop\lavoro\trad

# Test offline
python -m pytest tests/

# Confluence
python -m strategies.confluence_levels validate-levels
python -m strategies.confluence_levels dry-run --symbol EURUSD --price 1.16700
python -m strategies.confluence_levels run --once --verbose

# Stock Selector
python -m strategies.stock_selector --risk-free 4.2 --liquidity decreasing

# Sync levels.yaml al VPS
scp strategies\confluence_levels\levels.yaml matteo@<IP-VPS>:~/trad/strategies/confluence_levels/levels.yaml
```

### Sul VPS Linux (SSH)

```bash
# Connect
ssh matteo@<IP-VPS>

# Status del runner (se usi systemd)
sudo systemctl status confluence
journalctl -u confluence -f          # log live
sudo systemctl restart confluence    # se serve restart manuale

# Status del runner (se usi tmux)
tmux attach -t confluence            # rientra
# Ctrl+B poi D = detach
tmux kill-session -t confluence      # ammazza la sessione
```

### MT5 desktop / MetaQuotes VPS

| Operazione | Dove |
|---|---|
| Compile EA | MetaEditor (F7) |
| Aggancia EA al grafico | Trascina dalla Navigator |
| Vedi posizioni aperte | Tab "Trade" |
| Vedi storico | Tab "History" |
| Vedi log EA | Tab "Experts" o "Journal" |
| Migra a VPS | Tools → Virtual Hosting → Migrate |
| Monitor da telefono | App mobile MT5 → tab VPS |

---

## Quando torni qui dopo qualche giorno

Ordine di lettura suggerito:

1. [docs/ARCHITECTURE_v2.md](ARCHITECTURE_v2.md) — visione d'insieme.
2. Questo file (`OPERATIONAL_GUIDE.md`) — step concreti.
3. [strategies/confluence_levels/README.md](../strategies/confluence_levels/README.md) — dettagli Confluence.
4. [mql5/README.md](../mql5/README.md) — dettagli EA.

Se ci sono dubbi o problemi specifici (errori del runner, EA che non parte, sync fallito), apri Claude Code e chiedi diretto. Tutto il contesto è nei plan file e nella memoria persistente.
