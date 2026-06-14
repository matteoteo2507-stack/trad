# Deploy Level Analyzer (Fase A) su Hetzner — guida passo passo

Replica l'infrastruttura della Confluence: **Hetzner Linux + yfinance + systemd + Telegram**.
Backend dati = `yfinance` (nessun MT5). Oro = `GC=F` futures (la notifica avvisa di
riconfermare sul grafico spot); BTC = `BTC-USD` (~spot).

Legenda: 🧑 = lo fai TU (io non posso) · 🤖 = già pronto nel repo.

---

## 1. 🧑 Telegram (bot + canale)
1. **@BotFather** → `/newbot` → nome + username → copia il **token**.
2. Crea un **canale Telegram privato** dedicato (es. "Level Analyzer — Signals").
3. Aggiungi il bot come **amministratore** del canale.
4. **chat_id**: posta un messaggio nel canale, apri
   `https://api.telegram.org/bot<TOKEN>/getUpdates`, leggi `"chat":{"id":-100...}`.
   Quel numero (negativo, `-100…`) è il `telegram_chat_id`.

## 2. 🧑 Crea il server Hetzner
Hetzner Cloud Console → **Add Server**:
- **Image:** Ubuntu 24.04 · **Type:** CX22 (2 vCPU, 4GB) · **Location:** Helsinki (hel1)
- **SSH key:** carica la tua `~/.ssh/id_ed25519.pub` (riusa quella esistente)
- Crea. Annota l'**IP pubblico**.

## 3. 🧑 Primo accesso e utente
```bash
ssh root@<IP>
adduser matteo && usermod -aG sudo matteo
rsync --archive --chown=matteo:matteo ~/.ssh /home/matteo   # copia la chiave
# da ora: ssh matteo@<IP>
```

## 4. 🧑 Dipendenze + repo
```bash
ssh matteo@<IP>
sudo apt update && sudo apt install -y python3-venv git
git clone https://github.com/matteoteo2507-stack/trad.git ~/trad   # usa il PAT read-only
cd ~/trad
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install yfinance pandas pyyaml requests
```

## 5. 🧑 Secret (SOLO i 2 valori Telegram)
> ⚠️ **NON copiare l'intero `.env` locale sul server**: contiene chiavi broker (Bybit,
> Binance, MT5…). Sul server servono solo questi due:
```bash
cat > ~/trad/.env <<'EOF'
TELEGRAM_BOT_TOKEN=<IL_TUO_TOKEN>
TELEGRAM_CHAT_ID=<IL_TUO_CHAT_ID>
EOF
chmod 600 ~/trad/.env
```
`data_backend: yfinance` è già in `config.yaml`; il `telegram_chat_id` viene letto dal `.env`
(puoi lasciarlo vuoto in config).

## 6. 🧑 Prova manuale (prima del service)
```bash
cd ~/trad
./venv/bin/python -m level_analyzer scan --notify
```
Devi vedere le zone in console e (se ce ne sono entro `proximity_atr`) un **messaggio nel canale**.

## 7. 🧑 systemd service (always-on)
Genera il service col TUO utente/home (auto-detect → evita l'errore `217/USER`):
```bash
U=$(whoami); H="$HOME"
sudo tee /etc/systemd/system/level-analyzer.service >/dev/null <<EOF
[Unit]
Description=Level Analyzer (Fase A)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$U
WorkingDirectory=$H/trad
ExecStart=$H/trad/venv/bin/python -m level_analyzer run
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now level-analyzer
sudo systemctl status level-analyzer --no-pager
sudo journalctl -u level-analyzer -f --no-pager      # log live
```

## 8. Aggiornamenti futuri
```bash
cd ~/trad && git pull && sudo systemctl restart level-analyzer
```

---

## Note
- **Forward log**: `~/trad/level_analyzer/signals_log.csv` (gitignored). Scarica periodicamente
  (`scp matteo@<IP>:~/trad/level_analyzer/signals_log.csv .`) e compila la colonna `outcome`
  con l'esito reale: è il dataset per validare i guardrail.
- **Costo**: ~€3.79/mese (CX22). Per spegnere senza fatturare va **eliminato** in console.
- **Upgrade a spot (oro)**: quando passeremo a semi/full-auto, sostituiremo yfinance con un
  bridge dal tuo MT5 FPM (`data_backend: mt5` + `initialize(path=...terminal64.exe)` del
  terminale dedicato demo4).
