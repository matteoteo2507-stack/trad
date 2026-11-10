"""Simulatore di esecuzione degli OB di VTOB (realistico e conservativo), compilato con numba.

Convenzione dei prezzi (la stessa del motore di riferimento e di una strategy() di TradingView sul grafico BID):
- tutti i livelli (ingresso di riferimento, stop, target, parziali, BE, trailing) sono prezzi BID e scattano sul BID;
- lo spread si paga una volta per trade: spread della candela d'ingresso (x spread_mult) tolto dal P/L;
- slippage: importo fisso per lato (ingresso + uscita = 2 x slippage) tolto dal P/L; commissione per trade.
Regole d'esecuzione:
- ordini decisi alla chiusura della candela, eseguiti dalla successiva;
  * croce di retest: a mercato all'open della candela dopo il segnale;
  * limit: attivo dalla candela dopo la conferma dell'OB, eseguito se il prezzo tocca il livello (gap -> open);
- candela ambigua: se tocca stop e target vince lo stop; sulla candela d'ingresso del limit si controlla solo lo stop;
- break-even e trailing calcolati a candela chiusa, validi dalla candela successiva;
- time stop, uscita del venerdì / a fine sessione e al cambio di trend: decise a candela chiusa,
  eseguite all'open della candela successiva (come strategy.close() in TradingView);
- una posizione alla volta, un trade per OB (opzionale: rientro sullo stesso OB dopo uno stop pieno).
R di un trade = P/L netto ($ per 1 oncia) / rischio iniziale r, con r = |ingresso - stop| (prezzi BID).
"""
from __future__ import annotations

import numpy as np
from numba import njit

# ---------------------------------------------------------------- vettore di configurazione (indici)
C_ENTRY, C_EFRAC, C_EXPIRY = 0, 1, 2                 # ingresso: 0 croce, 1 limit; frazione dentro la zona; scadenza
C_SLM, C_SLX = 3, 4                                  # stop: modo, valore (x atr / $ / buffer x atr)
C_TPM, C_TPX = 5, 6                                  # target: modo, valore (R / $ / R minimo per lo swing)
C_P1F, C_P1R, C_P2F, C_P2R, C_PBE = 7, 8, 9, 10, 11  # parziali: frazione e livello in R; stop a BE dopo il parziale
C_BET, C_BEO = 12, 13                                # break-even: trigger in R, offset in R
C_TRM, C_TRK, C_TRS = 14, 15, 16                     # trailing: modo, x atr, partenza (0 subito, 1 dopo BE, 2 dopo parziale)
C_TIME, C_TRX, C_XFL = 17, 18, 19                    # time stop (candele), uscita al cambio trend, uscita forzata
C_DIR, C_HMASK, C_SH1, C_WDM = 20, 21, 22, 23        # direzione (1, -1, 0 = entrambe), ore permesse (maschera, ora italiana), -, giorni
C_SPM, C_SLIP, C_COMM, C_REENT, C_LIMTR = 24, 25, 26, 27, 28
C_NCFG = 29

E_CROCE, E_LIMIT = 0, 1
S_ATR, S_USD, S_OB, S_SWING = 0, 1, 2, 3
T_RR, T_USD, T_SWING, T_NONE = 0, 1, 2, 3
TR_NONE, TR_ATR, TR_ST, TR_CHAND, TR_SWING = 0, 1, 2, 3, 4
# esiti del trade
X_SL, X_TP, X_BE, X_PARZ, X_TRAIL, X_TEMPO, X_TREND, X_FORZ = 0, 1, 2, 3, 4, 5, 6, 7
ESITI = ["SL", "TP", "BE", "PARZ", "TRAIL", "TEMPO", "TREND", "FORZATA"]
# colonne della matrice dei trade
COLONNE = ["i_in", "i_out", "dir", "entrata", "uscita", "R", "pnl", "esito", "ob", "rischio", "n_parz", "R_lordo", "costo",
           "i_rf"]                                  # i_rf: prima candela con lo stop a pareggio o oltre (-1 = mai)


def cfg_vettore(entry="croce", entry_frac=0.0, expiry=0, sl="atr", sl_x=6.0, tp="rr", tp_x=3.0,
                p1=(0.0, 0.0), p2=(0.0, 0.0), parz_be=False, be=(0.0, 0.0), trail="none", trail_k=3.0,
                trail_start="be", time_stop=0, exit_trend=False, exit_forzata=False, direzione="long",
                sess=(0, 24), giorni=(0, 1, 2, 3, 4, 5, 6), spread_mult=1.0, slippage=0.10, commissione=0.0,
                rientro=False, limit_trend=True) -> np.ndarray:
    """Vettore di configurazione da parametri leggibili (vedi docstring del modulo)."""
    c = np.zeros(C_NCFG)
    c[C_ENTRY] = {"croce": E_CROCE, "limit": E_LIMIT}[entry]
    c[C_EFRAC] = entry_frac
    c[C_EXPIRY] = expiry
    c[C_SLM] = {"atr": S_ATR, "usd": S_USD, "ob": S_OB, "swing": S_SWING}[sl]
    c[C_SLX] = sl_x
    c[C_TPM] = {"rr": T_RR, "usd": T_USD, "swing": T_SWING, "none": T_NONE}[tp]
    c[C_TPX] = tp_x
    c[C_P1F], c[C_P1R] = p1
    c[C_P2F], c[C_P2R] = p2
    c[C_PBE] = float(parz_be)
    c[C_BET], c[C_BEO] = be
    c[C_TRM] = {"none": TR_NONE, "atr": TR_ATR, "st": TR_ST, "chandelier": TR_CHAND, "swing": TR_SWING}[trail]
    c[C_TRK] = trail_k
    c[C_TRS] = {"subito": 0, "be": 1, "parz": 2}[trail_start]
    c[C_TIME] = time_stop
    c[C_TRX] = float(exit_trend)
    c[C_XFL] = float(exit_forzata)
    c[C_DIR] = {"long": 1, "short": -1, "entrambe": 0}[direzione]
    ore = range(sess[0], sess[1]) if isinstance(sess, tuple) else sess          # (h0, h1) oppure elenco di ore
    c[C_HMASK] = float(sum(1 << int(h) for h in ore)); c[C_SH1] = 0.0
    c[C_WDM] = sum(1 << g for g in giorni)
    c[C_SPM] = spread_mult
    c[C_SLIP] = slippage
    c[C_COMM] = commissione
    c[C_REENT] = float(rientro)
    c[C_LIMTR] = float(limit_trend)
    return c


@njit(cache=True)
def _livelli(d, e, i, oid, slm, slx, tpm, tpx, atr, h, l, ob_piv, ob_top, ob_bot):
    """Stop, target e rischio per un ingresso al prezzo BID e alla candela i (volatilità di riferimento: candela i-1).
    Ritorna (ok, sl, tp, r)."""
    ref = atr[i - 1]
    if slm == S_ATR:
        sl = e - d * slx * ref
    elif slm == S_USD:
        sl = e - d * slx
    elif slm == S_OB:                                   # oltre il bordo opposto dell'OB + buffer
        sl = (ob_bot[oid] - slx * ref) if d == 1 else (ob_top[oid] + slx * ref)
    else:                                               # oltre lo swing del pivot + buffer
        p = ob_piv[oid]
        sl = (l[p] - slx * ref) if d == 1 else (h[p] + slx * ref)
    r = (e - sl) * d
    if not (r > 0):
        return False, sl, np.nan, r
    tp = np.nan
    if tpm == T_RR:
        tp = e + d * tpx * r
    elif tpm == T_USD:
        tp = e + d * tpx
    elif tpm == T_SWING:                                # estremo dello swing tra il pivot e la candela prima dell'ingresso
        p = ob_piv[oid]
        sw = h[p] if d == 1 else l[p]
        for k in range(p, i):
            if d == 1:
                if h[k] > sw:
                    sw = h[k]
            else:
                if l[k] < sw:
                    sw = l[k]
        tp = sw
        if (tp - e) * d < tpx * r:                      # target più vicino di tpx R: trade scartato
            return False, sl, tp, r
    return True, sl, tp, r


@njit(cache=True)
def simula(o, h, l, c, spr, atr, trend, tstop, swlo, swhi, ora, wday, xflag, filtro,
           act_id, act_dir, act_top, act_bot, sig_l, sig_s, ob_conf, ob_piv, ob_top, ob_bot, cfg):
    """Simula una configurazione su tutta la serie. Ritorna la matrice dei trade (colonne COLONNE).
    filtro[i]: regime della candela i (bit 0 = long permessi, bit 1 = short permessi), calcolato con dati chiusi."""
    n = len(c)
    entry_m = int(cfg[C_ENTRY]); efrac = cfg[C_EFRAC]; expiry = int(cfg[C_EXPIRY])
    slm = int(cfg[C_SLM]); slx = cfg[C_SLX]; tpm = int(cfg[C_TPM]); tpx = cfg[C_TPX]
    p1f = cfg[C_P1F]; p1r = cfg[C_P1R]; p2f = cfg[C_P2F]; p2r = cfg[C_P2R]; pbe = cfg[C_PBE] > 0
    bet = cfg[C_BET]; beo = cfg[C_BEO]; trm = int(cfg[C_TRM]); trk = cfg[C_TRK]; trs = int(cfg[C_TRS])
    tstop_n = int(cfg[C_TIME]); trx = cfg[C_TRX] > 0; xfl = cfg[C_XFL] > 0
    dirf = int(cfg[C_DIR]); hmask = int(cfg[C_HMASK]); wdm = int(cfg[C_WDM])
    spm = cfg[C_SPM]; slip = cfg[C_SLIP]; comm = cfg[C_COMM]; reent = cfg[C_REENT] > 0; limtr = cfg[C_LIMTR] > 0

    traded = np.zeros(len(ob_conf) + 1, np.bool_)
    out = np.zeros((n // 2 + 10, 14))
    nt = 0
    # stato della posizione
    pos = 0; e = 0.0; sl = 0.0; tp = np.nan; r0 = 0.0; ent_i = -1; ent_ob = -1; cost = 0.0
    rem = 1.0; realized = 0.0; nparz = 0; be_on = False; be_arm = False; tr_on = False; peak = 0.0
    sl_init = 0.0; bel = 0.0; lv1 = np.nan; lv2 = np.nan; limit_fill = False; exit_code = 0; i_rf = -1
    pend = 0; pend_ob = -1

    for i in range(1, n):
        esito = -1
        px = 0.0
        # ---- 0) uscita decisa alla chiusura precedente (time stop, venerdì/fine sessione, cambio di trend):
        #         eseguita all'open di questa candela (come strategy.close() in TradingView)
        if pos != 0 and exit_code > 0:
            px = o[i]
            realized += rem * (px - e) * pos
            esito = exit_code
        # ---- 1) ingresso a mercato dal segnale della candela precedente
        if pos == 0 and esito < 0 and pend != 0:
            d = pend
            ok, sl_, tp_, r_ = _livelli(d, o[i], i, pend_ob, slm, slx, tpm, tpx, atr, h, l, ob_piv, ob_top, ob_bot)
            if ok:
                pos = d; e = o[i]; sl = sl_; tp = tp_; r0 = r_; ent_i = i; ent_ob = pend_ob; limit_fill = False
            elif reent:
                traded[pend_ob] = False
            pend = 0
        # ---- 2) ordine limit sull'OB attivo alla chiusura precedente
        elif pos == 0 and esito < 0 and entry_m == E_LIMIT and act_dir[i - 1] != 0:
            oid = act_id[i - 1]; d = act_dir[i - 1]
            ok = not traded[oid]
            if ok and dirf != 0 and d != dirf:
                ok = False
            if ok and limtr and trend[i - 1] != d:
                ok = False
            if ok and expiry > 0 and i - ob_conf[oid] > expiry:
                ok = False
            if ok and ((hmask >> int(ora[i])) & 1) == 0:
                ok = False
            if ok and ((wdm >> wday[i]) & 1) == 0:
                ok = False
            if ok and ((filtro[i - 1] >> (0 if d == 1 else 1)) & 1) == 0:
                ok = False
            if ok:
                top = act_top[i - 1]; bot = act_bot[i - 1]
                if d == 1:
                    lim = top - efrac * (top - bot)
                    touched = l[i] <= lim
                    ef = o[i] if o[i] < lim else lim
                else:
                    lim = bot + efrac * (top - bot)
                    touched = h[i] >= lim
                    ef = o[i] if o[i] > lim else lim
                if touched:
                    ok2, sl_, tp_, r_ = _livelli(d, ef, i, oid, slm, slx, tpm, tpx, atr, h, l, ob_piv, ob_top, ob_bot)
                    traded[oid] = True
                    if ok2:
                        pos = d; e = ef; sl = sl_; tp = tp_; r0 = r_; ent_i = i; ent_ob = oid; limit_fill = True
                    elif reent:
                        traded[oid] = False
        if pos != 0 and ent_i == i and esito < 0:
            # inizializzazione della posizione appena aperta
            cost = spr[i] * spm + 2.0 * slip + comm
            rem = 1.0; realized = 0.0; nparz = 0; be_on = False; be_arm = False; tr_on = (trs == 0)
            peak = e; sl_init = sl; bel = e + pos * beo * r0; exit_code = 0; i_rf = -1
            lv1 = (e + pos * p1r * r0) if p1f > 0 else np.nan
            lv2 = (e + pos * p2r * r0) if p2f > 0 else np.nan
        # ---- 3) gestione della posizione sulla candela i
        if pos != 0 and esito < 0:
            d = pos
            primo_limit = limit_fill and i == ent_i
            if be_arm and not be_on:                    # BE armato alla chiusura precedente
                be_on = True
                if (bel - sl) * d > 0:
                    sl = bel
            if i_rf < 0 and (sl - e) * d >= 0:          # da qui il trade non rischia più (BE o trailing)
                i_rf = i
            if (d == 1 and l[i] <= sl) or (d == -1 and h[i] >= sl):
                # stop (prima di tutto: candela ambigua -> vince lo stop); gap oltre lo stop -> open
                gap = (o[i] < sl) if d == 1 else (o[i] > sl)
                px = o[i] if (gap and not primo_limit) else sl
                realized += rem * (px - e) * d
                if nparz > 0:
                    esito = X_PARZ
                elif abs(sl - sl_init) < 1e-9:
                    esito = X_SL
                elif be_on and abs(sl - bel) < 1e-9:
                    esito = X_BE
                else:
                    esito = X_TRAIL
            else:
                if not primo_limit:
                    # parziali e target (ordini limit: gap a favore -> open)
                    for k in range(3):
                        if k == 0:
                            lv = lv1; fr = p1f
                        elif k == 1:
                            lv = lv2; fr = p2f
                        else:
                            lv = tp; fr = rem
                        if np.isnan(lv) or rem <= 1e-9:
                            continue
                        if (d == 1 and h[i] >= lv) or (d == -1 and l[i] <= lv):
                            gap = (o[i] > lv) if d == 1 else (o[i] < lv)
                            pk = o[i] if gap else lv
                            if fr > rem:
                                fr = rem
                            realized += fr * (pk - e) * d
                            rem -= fr
                            px = pk
                            if k < 2:
                                nparz += 1
                                if k == 0:
                                    lv1 = np.nan
                                else:
                                    lv2 = np.nan
                                if pbe:                 # stop a BE dopo il parziale (dalla candela dopo)
                                    be_arm = True
                                if trs == 2:
                                    tr_on = True
                            if rem <= 1e-9:
                                esito = X_TP
                                break
            if esito < 0:
                # aggiornamenti a candela chiusa, validi dalla candela dopo: BE, trailing, cambio di trend
                fav = (h[i] - e) if d == 1 else (e - l[i])
                if bet > 0 and fav >= bet * r0:
                    be_arm = True
                if trs == 1 and (be_arm or be_on):
                    tr_on = True
                if d == 1:
                    if h[i] > peak:
                        peak = h[i]
                else:
                    if l[i] < peak:
                        peak = l[i]
                if trm != TR_NONE and tr_on:
                    if trm == TR_ATR:
                        cand = c[i] - d * trk * atr[i]
                    elif trm == TR_CHAND:
                        cand = peak - d * trk * atr[i]
                    elif trm == TR_SWING:                   # ultimo minimo/massimo di pivot confermato - buffer
                        sw = swlo[i] if d == 1 else swhi[i]
                        cand = sl if np.isnan(sw) else sw - d * trk * atr[i]
                    else:                               # linea trend_stop del Supertrend (solo se il trend è a favore)
                        cand = tstop[i] if trend[i] == d else sl
                    if (cand - sl) * d > 0:
                        sl = cand
                # uscite decise a candela chiusa, eseguite all'open della prossima
                if tstop_n > 0 and i - ent_i >= tstop_n:
                    exit_code = X_TEMPO
                elif xfl and xflag[i]:
                    exit_code = X_FORZ
                elif trx and trend[i] != d:
                    exit_code = X_TREND
        # ---- registrazione dell'uscita
        if esito >= 0:
            if esito >= X_TEMPO and nparz > 0:
                esito = X_PARZ
            pnl = realized - cost
            out[nt, 0] = ent_i; out[nt, 1] = i; out[nt, 2] = pos; out[nt, 3] = e; out[nt, 4] = px
            out[nt, 5] = pnl / r0; out[nt, 6] = pnl; out[nt, 7] = esito; out[nt, 8] = ent_ob; out[nt, 9] = r0
            out[nt, 10] = nparz; out[nt, 11] = realized / r0; out[nt, 12] = cost; out[nt, 13] = i_rf
            nt += 1
            if reent and esito == X_SL:
                traded[ent_ob] = False
            pos = 0
            exit_code = 0
        # ---- 4) segnale di retest alla chiusura della candela i -> ingresso all'open della prossima
        if entry_m == E_CROCE and pos == 0 and pend == 0 and act_dir[i] != 0:
            oid = act_id[i]; d = act_dir[i]
            sig = sig_l[i] if d == 1 else sig_s[i]
            if sig and not traded[oid] and (dirf == 0 or dirf == d) and ((hmask >> int(ora[i])) & 1) == 1 \
                    and ((wdm >> wday[i]) & 1) == 1 and ((filtro[i] >> (0 if d == 1 else 1)) & 1) == 1:
                pend = d; pend_ob = oid; traded[oid] = True
    # una posizione ancora aperta a fine dati non viene contata (come nel motore di riferimento)
    return out[:nt]
