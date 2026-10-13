"""Backtest engine that replicates 'Volume-Trend Order Block Engine [BigBeluga]' bar by bar,
plus the quality-score filters of VTOB_Indicator_Pro.pine. No lookahead: an OB exists only
from its confirmation bar (pivot + pivot_len)."""
import numpy as np, pandas as pd, io, re, sys

# ---------------------------------------------------------------- data
def load(path):
    raw = open(path, 'rb').read()
    for enc in ('utf-8-sig', 'utf-16', 'latin-1'):
        try:
            txt = raw.decode(enc); break
        except Exception:
            continue
    sep = '\t' if txt.count('\t') > txt.count(',') else (';' if txt.count(';') > txt.count(',') else ',')
    df = pd.read_csv(io.StringIO(txt), sep=sep)
    cols = {c: re.sub(r'[<>\s]', '', c).lower() for c in df.columns}
    df = df.rename(columns=cols)
    if 'date' in df.columns and 'time' in df.columns:            # MT5 export
        ts = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str), format='mixed')
    elif 'time' in df.columns:                                   # TradingView export
        t = df['time']
        ts = pd.to_datetime(t, unit='s') if pd.api.types.is_numeric_dtype(t) else pd.to_datetime(t.astype(str), format='mixed')
    else:
        ts = pd.to_datetime(df.iloc[:, 0], format='mixed')
    vol = None
    for c in ('tickvol', 'tick_volume', 'volume', 'vol'):
        if c in df.columns and df[c].astype(float).sum() > 0:
            vol = df[c].astype(float); break
    out = pd.DataFrame({'open': df['open'].astype(float), 'high': df['high'].astype(float),
                        'low': df['low'].astype(float), 'close': df['close'].astype(float),
                        'volume': vol if vol is not None else 1.0,
                        'spread': df['spread'].astype(float) * 0.01 if 'spread' in df.columns else np.nan})
    out.index = ts
    return out[~out.index.duplicated()].sort_index()

# ---------------------------------------------------------------- indicator core
def core(df, st_len=50, st_mult=3.5, pivot_len=7, htf='60min', htf_len=200, pivot_left=None):
    LL_ = pivot_len if pivot_left is None else pivot_left
    o, h, l, c, v = (df[k].values for k in ('open', 'high', 'low', 'close', 'volume'))
    n = len(df)
    atr = pd.Series(h - l).rolling(st_len).mean().values
    src = (h + l) / 2
    ub0, lb0 = src + st_mult * atr, src - st_mult * atr
    ub, lb = np.full(n, np.nan), np.full(n, np.nan)
    trend = np.zeros(n, int); tstop = np.full(n, np.nan)
    for i in range(n):
        plb = 0.0 if i == 0 or np.isnan(lb[i-1]) else lb[i-1]
        pub = 0.0 if i == 0 or np.isnan(ub[i-1]) else ub[i-1]
        pc = c[i-1] if i > 0 else np.nan
        x = lb0[i]
        lb[i] = x if (x > plb or (i > 0 and pc < plb)) else plb
        x = ub0[i]
        ub[i] = x if (x < pub or (i > 0 and pc > pub)) else pub
        if i == 0 or np.isnan(atr[i-1]):
            trend[i] = 1
        elif tstop[i-1] == pub:
            trend[i] = 1 if c[i] > ub[i] else -1
        else:
            trend[i] = -1 if c[i] < lb[i] else 1
        tstop[i] = lb[i] if trend[i] == 1 else ub[i]
    # pivots (confirmed at i, pivot at i-pivot_len)
    pl = np.zeros(n, bool); ph = np.zeros(n, bool)
    L = pivot_len
    for i in range(L + LL_, n):
        p = i - L
        lw = l[p - LL_:p]; rw = l[p + 1:i + 1]
        if l[p] < lw.min() and l[p] <= rw.min(): pl[i] = True
        hw = h[p - LL_:p]; rh = h[p + 1:i + 1]
        if h[p] > hw.max() and h[p] >= rh.max(): ph[i] = True
    chg = np.r_[False, trend[1:] != trend[:-1]]
    age = np.zeros(n, int); a = 100000
    for i in range(n):
        a = 0 if chg[i] else a + 1; age[i] = a
    hh = pd.Series(h).rolling(L).max().values
    ll = pd.Series(l).rolling(L).min().values
    vavg = pd.Series(v).rolling(20).mean().values
    # HTF EMA of the last *closed* HTF bar
    hc = df['close'].resample(htf, label='left', closed='left').last().dropna()
    hema = hc.ewm(span=htf_len, adjust=False).mean().shift(1)
    bucket = df.index.floor(htf)
    htf_ema = hema.reindex(bucket).values
    return dict(o=o, h=h, l=l, c=c, v=v, atr=atr, trend=trend, tstop=tstop, pl=pl, ph=ph,
                chg=chg, age=age, hh=hh, ll=ll, vavg=vavg, htf_ema=htf_ema, n=n, L=L,
                hour=(df.index - pd.Timedelta(hours=1)).hour.values, idx=df.index,
                spr=df['spread'].values if 'spread' in df else np.full(n, np.nan))

# ---------------------------------------------------------------- run
DEF = dict(min_score=0, use_imp=True, imp_mult=1.0, use_age=True, min_age=20, use_htf=True,
           use_dist=True, dist_mult=0.5, use_vol=True, vol_mult=1.2,
           entry='limit', sl_mode='ob', sl_buf=0.5, sl_fixed=20.0, rr=1.0, spread=0.40,
           max_age=None, sess=None, longs=True, shorts=True, start=None, end=None,
           max_risk_atr=None, zone_mode='atr', zone_h=1.0, entry_frac=0.0, min_h=0.15, be_at=None, be_off=0.1)

def run(K, **kw):
    P = dict(DEF); P.update(kw)
    o, h, l, c, v, atr, trend, tstop = (K[k] for k in ('o', 'h', 'l', 'c', 'v', 'atr', 'trend', 'tstop'))
    n, L = K['n'], K['L']
    idx = K['idx']
    act_top = act_bot = np.nan; act_dir = 0; act_id = -1; act_conf = -1; act_score = 0; act_feat = {}
    ob_id = 0; traded = set()
    pos = 0; e = sl = tp = 0.0; trades = []; pend = None  # pend for retest market entries
    n_ob = n_rej = 0
    prev_top = np.nan
    maxs = sum([P['use_imp'], P['use_age'], P['use_htf'], P['use_dist'], P['use_vol']])
    need = min(P['min_score'], maxs)
    t0 = pd.Timestamp(P['start']) if P['start'] else None
    t1 = pd.Timestamp(P['end']) if P['end'] else None

    def SP(i):
        if P['spread'] == 'data':
            x = K['spr'][i]
            return 0.4 if np.isnan(x) else x
        return P['spread']

    def score(d, top, bot, i):
        s = 0
        if P['use_imp'] and ((K['hh'][i] - top if d == 1 else bot - K['ll'][i]) >= P['imp_mult'] * atr[i]): s += 1
        if P['use_age'] and K['age'][i] >= P['min_age']: s += 1
        he = K['htf_ema'][i]
        if P['use_htf'] and not np.isnan(he) and ((c[i] > he) if d == 1 else (c[i] < he)): s += 1
        if P['use_dist'] and ((bot - tstop[i]) if d == 1 else (tstop[i] - top)) >= P['dist_mult'] * atr[i]: s += 1
        va = K['vavg'][i - L - 1] if i - L - 1 >= 0 else np.nan
        if P['use_vol'] and not np.isnan(va) and v[i - L] >= P['vol_mult'] * va: s += 1
        return s

    for i in range(1, n):
        ts = idx[i]
        inrange = (t0 is None or ts >= t0) and (t1 is None or ts < t1)
        # ---------- manage open position on this bar (orders placed at previous bar close)
        if pend is not None and pos == 0:
            d, pid, pa_top, pa_bot = pend; pend = None
            e = o[i]
            risk_ref = atr[i - 1]
            if P['sl_mode'] == 'ob':
                sl = pa_bot - P['sl_buf'] * risk_ref if d == 1 else pa_top + P['sl_buf'] * risk_ref
            else:
                k = P['sl_fixed'] * (risk_ref if P['sl_mode'] == 'atr' else 1)
                sl = e - k if d == 1 else e + k
            r = abs(e - sl)
            if r > 0 and (d == 1 and sl < e or d == -1 and sl > e):
                tp = e + P['rr'] * r * d; pos = d; ent_i = i; ent_id = pid; r0 = r; be_on = False; tr_feat = dict(act_feat); tr_conf = act_conf
        # limit entry: order resting from previous bar on active OB
        if pos == 0 and P['entry'] == 'limit' and inrange and act_dir != 0 and act_id not in traded and act_conf < i:
            d = act_dir
            ok = (d == 1 and P['longs'] and trend[i - 1] == 1) or (d == -1 and P['shorts'] and trend[i - 1] == -1)
            if P['max_age'] is not None and i - act_conf > P['max_age']: ok = False
            if P['sess'] is not None and not (P['sess'][0] <= K['hour'][i] < P['sess'][1]): ok = False
            if ok:
                lim = act_top - P['entry_frac'] * (act_top - act_bot) if d == 1 else act_bot + P['entry_frac'] * (act_top - act_bot)
                touched = (l[i] <= lim) if d == 1 else (h[i] >= lim)
                if touched:
                    e = min(o[i], lim) if d == 1 else max(o[i], lim)
                    risk_ref = atr[i - 1]
                    if P['sl_mode'] == 'ob':
                        sl = act_bot - P['sl_buf'] * risk_ref if d == 1 else act_top + P['sl_buf'] * risk_ref
                    else:
                        k = P['sl_fixed'] * (risk_ref if P['sl_mode'] == 'atr' else 1)
                        sl = e - k if d == 1 else e + k
                    r = abs(e - sl)
                    if r > 0 and (P['max_risk_atr'] is None or r <= P['max_risk_atr'] * risk_ref):
                        tp = e + P['rr'] * r * d; pos = d; ent_i = i; ent_id = act_id; r0 = r; be_on = False; traded.add(act_id); tr_feat = dict(act_feat); tr_conf = act_conf
                        # same-bar stop check (conservative): if bar also crosses stop after fill
                        if (d == 1 and l[i] <= sl) or (d == -1 and h[i] >= sl):
                            trades.append(dict(t=idx[i], d=d, e=e, x=sl, R=-1 - SP(i) / r, pnl=(sl - e) * d - SP(i), bars=0, score=act_score, wait=i - act_conf, hr=K['hour'][i], **act_feat))
                            pos = 0
        if pos != 0 and i > ent_i or (pos != 0 and P['entry'] != 'limit' and i == ent_i):
            r = r0; d = pos
            if be_on:
                sl = e + d * P['be_off'] * r0
            hit_sl = (l[i] <= sl) if d == 1 else (h[i] >= sl)
            hit_tp = (h[i] >= tp) if d == 1 else (l[i] <= tp)
            x = None
            if hit_sl: x = sl if not ((d == 1 and o[i] < sl) or (d == -1 and o[i] > sl)) else o[i]
            elif hit_tp: x = tp if not ((d == 1 and o[i] > tp) or (d == -1 and o[i] < tp)) else o[i]
            if x is not None:
                pnl = (x - e) * d - SP(ent_i)
                trades.append(dict(t=idx[ent_i], d=d, e=e, x=x, R=pnl / r, pnl=pnl, bars=i - ent_i, score=act_score, wait=ent_i - tr_conf, hr=K['hour'][ent_i], **tr_feat))
                pos = 0
            elif P['be_at'] is not None and not be_on and ((h[i] - e) * d if d == 1 else (e - l[i])) >= P['be_at'] * r0:
                be_on = True   # stop a pareggio dalla candela successiva
        # ---------- indicator update at close of bar i
        if np.isnan(atr[i]):
            prev_top = act_top; continue
        for d, piv in ((1, K['pl'][i]), (-1, K['ph'][i])):
            if trend[i] != d or not piv: continue
            p = i - L
            if d == 1:
                top = min(o[p], c[p])
                bot = top - P['zone_h'] * atr[i] if P['zone_mode'] == 'atr' else min(l[p], top - P['min_h'] * atr[i])
            else:
                bot = max(o[p], c[p])
                top = bot + P['zone_h'] * atr[i] if P['zone_mode'] == 'atr' else max(h[p], bot + P['min_h'] * atr[i])
            overlap = not (np.isnan(act_top) or np.isnan(act_bot)) and not (bot > act_top or top < act_bot)
            if overlap: continue
            s = score(d, top, bot, i)
            he = K['htf_ema'][i]; va = K['vavg'][i - L - 1] if i - L - 1 >= 0 else np.nan
            w = slice(i - L, i + 1); bv = v[w][c[w] >= o[w]].sum(); tv = v[w].sum()
            feat = dict(f_imp=((K['hh'][i] - top) if d == 1 else (bot - K['ll'][i])) / atr[i],
                        f_age=K['age'][i], f_htf=(np.nan if np.isnan(he) else float((c[i] > he) == (d == 1))),
                        f_dist=((bot - tstop[i]) if d == 1 else (tstop[i] - top)) / atr[i],
                        f_vol=(v[i - L] / va if va and not np.isnan(va) else np.nan),
                        f_bias=((bv / tv) if d == 1 else (1 - bv / tv)) if tv > 0 else 0.5,
                        conf_i=i)
            if s < need:
                n_rej += 1; continue
            n_ob += 1; ob_id += 1
            act_top, act_bot, act_dir, act_id, act_conf, act_score = top, bot, d, ob_id, i, s
            act_feat = feat
        if act_dir != 0:
            if (act_dir == 1 and h[i] < act_bot) or (act_dir == -1 and l[i] > act_top):
                act_top = act_bot = np.nan; act_dir = 0
        # retest signal (crossover of low over top / crossunder of high under bottom)
        if P['entry'] == 'retest' and pos == 0 and pend is None and inrange and act_dir != 0 and act_id not in traded:
            chg = K['chg'][i]
            if act_dir == 1 and P['longs'] and not K['pl'][i] and not chg and l[i] > act_top and l[i-1] <= act_top:
                if P['sess'] is None or P['sess'][0] <= K['hour'][i] < P['sess'][1]:
                    pend = (1, act_id, act_top, act_bot); traded.add(act_id)
            if act_dir == -1 and P['shorts'] and not K['ph'][i] and not chg and h[i] < act_bot and h[i-1] >= act_bot:
                if P['sess'] is None or P['sess'][0] <= K['hour'][i] < P['sess'][1]:
                    pend = (-1, act_id, act_top, act_bot); traded.add(act_id)
    T = pd.DataFrame(trades)
    return T, n_ob, n_rej

def stats(T):
    if len(T) == 0:
        return dict(trades=0, win=np.nan, PF=np.nan, R=0.0, avgR=np.nan, maxDD_R=0.0, pnl=0.0)
    w = T[T.R > 0]; ls = T[T.R <= 0]
    eq = T.R.cumsum(); dd = (eq.cummax() - eq).max()
    return dict(trades=len(T), win=round(100 * len(w) / len(T), 1),
                PF=round(w.R.sum() / -ls.R.sum(), 2) if len(ls) and ls.R.sum() < 0 else np.inf,
                R=round(T.R.sum(), 1), avgR=round(T.R.mean(), 3), maxDD_R=round(dd, 1),
                pnl=round(T.pnl.sum(), 1))
