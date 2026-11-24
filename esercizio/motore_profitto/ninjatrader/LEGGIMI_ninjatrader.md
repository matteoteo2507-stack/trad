MOTORE PROFITTO - BOT PER NINJATRADER 8 (configurazione concordata 13/11, AGGIORNATA 20/11/2026)
================================================================================
Conto: FundedNext Futures Rapid Daily 25k (Tradovate, ambiente Simulation).
I valori predefiniti dei bot sono GIA' quelli concordati: basta scegliere il conto e abilitare.

*** NOVITA' 20/11 ***
 a) OroOrderFlowNT - FILTRO VOLATILITA' sul FADE (gia' acceso nei predefiniti): se IERI il range dell'oro 08:20-13:30 NY
    (in % del prezzo) e' nel terzo piu' alto degli ultimi 120 giorni, il FADE di oggi SALTA. GROSSI non cambia.
    Test 1 anno: i FADE saltati valgono -0,53R in entrambe le meta'. Prova (prudente) 77% -> 83%, 5 prelievi 66% -> 75%.
    Nuove impostazioni: "Filtro volatilita'" = SI, soglia 0,667, giorni 120. Il bot carica da solo lo storico 5 minuti.
    Nell'Output, verso le 15:50: "FADE: salto per il filtro volatilita' ..." oppure "FADE ok".
 b) OroOrderFlowNT - conta anche le perdite di fila di SPINTA: se SPINTA ha 2 perdite di fila, anche il bot oro dimezza
    (SPINTA lo faceva gia' al contrario). Nessuna impostazione nuova: si spegne con "Riduci il rischio dopo N perdite" = 0.
    Simulazione dal saldo di oggi, caso prudente: prova 80% -> 86%, 5 prelievi 80% -> 90% (circa 2 giorni piu' lenta).
    Nell'Output all'avvio: "conta anche le perdite di fila di SPINTA (ora N)".
 c) 4 indicatori NUOVI (solo grafica, non toccano gli ordini), da mettere sul grafico GC con Tick Replay:
    - RadarSegnaliOF: pannello sotto il grafico, quanto manca a un segnale GROSSI (barra, soglia 2,5) e SPINTA (linea, 2,75)
    - FootprintAvanzatoOF: footprint con candele verdi/viola, sbilanciamenti e POC della candela
    - BolleGrossiOF: bolle sugli scambi grossi (>= 40 contratti)
    - ZoneReazioneOF: livelli oggettivi (POC/VAH/VAL di ieri, massimi/minimi, ecc.). Attenzione: test 1 anno = i livelli
      classici sull'oro reagiscono come livelli a caso; e' solo un aiuto visivo, NON un segnale.
 d) SPINTA, PortafoglioIntradayNT e CuscinettoMP: invariati rispetto al 19/11.
 e) Lasciare fare ai bot: i trade saltati (es. "contratti 0" con cuscinetto basso e stop largo) sono voluti e gia'
    contati nelle simulazioni. Entrare a mano dopo non e' il trade testato.
 Aggiornamento: a mercato fermo, senza posizioni, Importa lo zip (sovrascrivi SI), poi rimetti/riabilita le strategie.

*** NOVITA' 19/11 (decisa dai soci): REGOLA DEL CUSCINETTO sui 3 bot ***
 CUSCINETTO = soldi che mancano prima di toccare il limite di perdita FundedNext (1.000 $ sotto il saldo massimo di fine giornata).
 Rischio di ogni trade = rischio normale x (cuscinetto / 1.000), minimo 35%. Con 1.000 $ di cuscinetto si rischia come prima;
 dopo le perdite il rischio scende da solo, appena si torna a guadagnare risale. Vale per GROSSI/FADE, SPINTA, regole intraday e news.
 Simulazione: prova superata 88% -> 93%, 5 prelievi completi 61% -> 81% (prudente 48% -> 75%).
 File nuovo: AddOns\CuscinettoMP.cs (modulo comune). Nuova impostazione in ogni bot: "Usa cuscinetto" = SI (gia' predefinita).

 !!! PRIMA DI RIACCENDERE: crea il file Documenti\NinjaTrader 8\cuscinetto_stato.txt con i TUOI numeri !!!
   - dashboard FundedNext del tuo conto > Overview > riquadro "Max loss limit": sotto la barra, il numero a SINISTRA
     (es. $24,614.6) e' il tuo LIMITE. Il tuo SALDO MASSIMO = limite + 1000 (es. 25614.6).
   - scrivi nel file UNA riga cosi' (punto per i decimali):   saldo massimo;data di oggi;saldo attuale
         esempio:   25614.6;2026-11-19;25614.4
     Da li' in poi il bot lo aggiorna da solo ogni sera (fine giornata FundedNext = 23:00 italiane).
   - Se il file manca, il bot parte come se il saldo massimo fosse 25.000 (sbagliato se sei in guadagno).
 Controllo: nella finestra Output ogni bot scrive "CUSCINETTO acceso: cuscinetto ... $ (saldo ..., limite ...)".
   Il LIMITE deve essere uguale a quello della dashboard.

*** NOVITA' 18/11 (decise in riunione) ***
 a) OroOrderFlowNT - filtro POC "almeno uno": GROSSI entra se va verso il POC di ieri OPPURE verso il POC di oggi
    (profilo dalle 08:20 NY = 14:20 IT fino al segnale). Salta solo se va via da entrambi.
    Nuova impostazione "Filtro POC: vale anche il POC di oggi (almeno uno)" = SI.
 b) OroOrderFlowNT - FADE stop minimo 5 punti: se lo stop e' piu' vicino di 5 punti lo allarga a 5.
    Nuova impostazione "FADE: stop minimo in punti" = 5.
 c) PortafoglioIntradayNT - regola 4 (oro fade) SPENTA: regole C = "1" (prima "14").
 d) PortafoglioIntradayNT - news oro SOLO NFP: Tipi news = "1" (prima "124").
 e) Indicatori aggiornati: MonitorOroOF disegna anche la linea azzurra 'POC di oggi' (oltre a quella gialla di ieri) e lo
    scrive nel pannello; SegnaliOroOF mostra la FADE con lo stop minimo 5 punti. Rischio base del Monitor: 0,75.
 Le novita' 'a' e 'b' cambiano il file del bot. Le novita' 'c' e 'd' sono solo impostazioni (gia' giuste nei predefiniti).

SE HAI GIA' I BOT INSTALLATI (aggiornamento), a mercato fermo e SENZA posizioni aperte (dopo le 22 o prima delle 09:40):
 1. Disabilita le strategie e rimuovile dai grafici.
 2. Installa come al punto 1 qui sotto (Importa lo zip; se chiede di sovrascrivere: SI).
 3. Rimetti le strategie con le impostazioni del punto 2 e controlla le 4 novita' qui sopra.
 4. Crea il file cuscinetto_stato.txt (vedi NOVITA' 19/11), poi Abilita. Nell'Output: "filtro POC: ACCESO" e "CUSCINETTO acceso" con il limite giusto.

------------------------------------------------------------------
1) INSTALLAZIONE
------------------------------------------------------------------
Metodo A (consigliato): NinjaTrader > Strumenti > Importa > NinjaScript Add-On...
   scegli il file 1_IMPORTA_in_NinjaTrader.zip -> si installano 3 strategie + 5 indicatori + il modulo cuscinetto e si compila da solo.
Metodo B (se A da' errore): copia a mano
   2_copia_manuale\Strategies\*.cs  ->  Documenti\NinjaTrader 8\bin\Custom\Strategies
   2_copia_manuale\Indicators\*.cs  ->  Documenti\NinjaTrader 8\bin\Custom\Indicators
   2_copia_manuale\AddOns\*.cs      ->  Documenti\NinjaTrader 8\bin\Custom\AddOns
   poi NinjaTrader > Nuovo > NinjaScript Editor > F5 (compila).
In entrambi i casi: copia 2_copia_manuale\news_eventi.csv in Documenti\NinjaTrader 8 (calendario news oro).

Accesso: nella schermata di login di NinjaTrader usare le credenziali TRADOVATE di FundedNext (non Google).
Dati: Level 1 ("Top of Book") basta, NON comprare la profondita'.

------------------------------------------------------------------
2) GRAFICI E STRATEGIE (tasto destro sul grafico > Strategie)
------------------------------------------------------------------
Grafico A: GC 12-26, 5 minuti, TICK REPLAY ATTIVO (Serie di dati > Tick Replay), almeno 30 giorni caricati
   (per vedere l'opzione Tick Replay: Strumenti > Opzioni > Dati di mercato > "Mostra Tick Replay")
   - OroOrderFlowNT   Rischio 0,75 | max 15 MGC | stop giorno 490 | conto virtuale 0 | GROSSI+FADE si
                      segnali 15 / z 2,5 / 600 / pausa 30 | dimezza dopo 2 perdite (x0,5) | max 2 perdite/giorno
                      filtro POC si + POC anche oggi si | FADE stop minimo 5 | aggiunta si (+1R, mezza posizione, max 10 iniziali)
   - OroSpintaNT      Rischio 0,75 | max 10 / conto 15 MGC | stop giorno 490 | conto virtuale 0
                      scambi grossi 20, z 2,75, 600, stop 0,5 candela, target 4R, uscita 60 min, 1 al giorno
   - Indicatori utili (solo grafica): FootprintOro, SegnaliOroOF, MonitorOroOF, MonitorSpintaOF,
                      RadarSegnaliOF, FootprintAvanzatoOF, BolleGrossiOF, ZoneReazioneOF (nuovi 20/11)
Grafico B: MGC 12-26, 5 minuti, 60 giorni caricati (Tick Replay NON serve)
   - PortafoglioIntradayNT   set RAPID_DAILY_25K | Backtest NO | conto virtuale 0
                      rischio A/B/C 0,25 / 0,22 / 0,15 | regole A 67, B 38, C 1 (regola 4 spenta) | "apri comunque 1 contratto" NO
                      news oro SI: MGC 12-26, 30 once, tipi 1 (solo NFP) | stop giorno 490 | max 20 micro
Per OGNI strategia, nel gruppo "Impostare": Conto = il conto FundedNext (se vuoto NON si abilita), poi Abilitato.

------------------------------------------------------------------
3) RISCHIO PER TRADE (25k)
------------------------------------------------------------------
(con cuscinetto pieno; dopo le perdite scende fino al 35%) Bot oro ~187 $ (dopo 2 perdite di fila ~94 $; con aggiunta al massimo ~280 $) | SPINTA ~187 $ |
regole intraday 37-62 $ | news ~150 $ (fino a ~300 se sbaglia in entrambe le direzioni) | stop di tutto a -490 $/giorno.

------------------------------------------------------------------
4) GUARDIANO (facoltativo, avvisi Telegram)
------------------------------------------------------------------
3_guardiano_telegram: guardiano_nt.py + telegram.py nella stessa cartella. Serve Python e un proprio bot Telegram:
   python telegram.py collega <TOKEN>   (prima scrivere /start al bot)   poi   python guardiano_nt.py
Nessun token/password e' incluso nel pacchetto.

------------------------------------------------------------------
5) ATTENZIONE
------------------------------------------------------------------
- 23-25/11: CAMBIO CONTRATTO ORO 12-26 -> 02-27 (grafici GC/MGC + contratto ordini dei 3 bot + OroNews).
- Grafico GC: TICK REPLAY SEMPRE ACCESO (senza, il POC e' sbagliato e il filtro non funziona).
- Bot accesi PRIMA delle 09:40 (regola 8 petrolio entra alle 09:40-09:45).
- 26/11 Thanksgiving: mercati USA chiusi/ridotti.
- PC sempre acceso, niente standby, cavo di rete: entrare 1 minuto in ritardo dimezza il guadagno.
- NON usare copiatori di segnali altrui sulla prop (vietato da FundedNext).
- Nessuna modifica ai bot senza accordo fra i soci.
Attese (test 1 anno, tutto incluso, 20/11): prova da zero ~92% normale / ~93% prudente; 5 prelievi completi ~88-90%.
Sono stime su 1 anno di dati futures: si confrontano ogni settimana col reale.
