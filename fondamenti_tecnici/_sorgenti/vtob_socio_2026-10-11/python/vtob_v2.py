"""Engine v2: multiple active OBs, retest entries, advanced exits (BE, partial, trailing, time stop).
Uses core() from vtob_bt. No lookahead: OBs exist from confirmation bar; signals at bar close; entry next open;
SL checked before any profit level within a bar (conservative)."""
import numpy as np, pandas as pd
from vtob_bt import core, load, stats

D2 = dict(min_age=20, dist_mult=0.0, use_htf=True, use_age=True, use_dist=True, max_obs=1,
          k=6.0, rr=3.0, be_at=1.0, be_off=0.1, part_at=None, part_frac=0.5, trail=None, trail_k=3.0,
          max_bars=None, longs=True, shorts=False, sess=None, one_per_ob=True, spread='data', start=None, end=None)

def run2(K, **kw):
    P = dict(D2); P.update(kw)
    o, h, l, c = K['o'], K['h'], K['l'], K['c']
    atr, trend, tstop, age, he = K['atr'], K['trend'], K['tstop'], K['age'], K['htf_ema']
    pl, ph, chg, hour, idx, spr = K['pl'], K['ph'], K['chg'], K['hour'], K['idx'], K['spr']
    n, L = K['n'], K['L']
    obs = []           # dicts: top, bot, d, id, prev_ref
    oid = 0
    pos = None; pend = None; trades = []
    t0 = pd.Timestamp(P['start']) if P['start'] else None
    t1 = pd.Timestamp(P['end']) if P['end'] else None
    def SP(i):
        if P['spread'] == 'data':
            x = spr[i]; return 0.4 if np.isnan(x) else x
        return P['spread']
    for i in range(1, n):
        # ---- entry at open
        if pend is not None and pos is None:
            d, ob_id, a = pend; pend = None
            e = o[i]; D = P['k'] * a
            pos = dict(d=d, e=e, D=D, sl=e - d * D, tp=(e + d * P['rr'] * D) if P['rr'] else None, i=i, be=False,
                       part=False, booked=0.0, w=1.0, ext=e, id=ob_id, sp=SP(i))
        # ---- manage position on bar i
        if pos is not None:
            d, e, D = pos['d'], pos['e'], pos['D']
            x = None
            # stop first
            if (d == 1 and l[i] <= pos['sl']) or (d == -1 and h[i] >= pos['sl']):
                x = pos['sl'] if not ((d == 1 and o[i] < pos['sl']) or (d == -1 and o[i] > pos['sl'])) else o[i]
            else:
                # partial
                if P['part_at'] and not pos['part']:
                    lv = e + d * P['part_at'] * D
                    if (d == 1 and h[i] >= lv) or (d == -1 and l[i] <= lv):
                        pos['booked'] += P['part_frac'] * P['part_at']; pos['w'] -= P['part_frac']; pos['part'] = True
                if pos['tp'] is not None and ((d == 1 and h[i] >= pos['tp']) or (d == -1 and l[i] <= pos['tp'])):
                    x = pos['tp'] if not ((d == 1 and o[i] > pos['tp']) or (d == -1 and o[i] < pos['tp'])) else o[i]
                elif P['max_bars'] and i - pos['i'] >= P['max_bars']:
                    x = c[i]
            if x is not None:
                R = pos['booked'] + pos['w'] * (x - e) * d / D - pos['sp'] / D
                trades.append(dict(t=idx[pos['i']], tx=idx[i], d=d, R=R, bars=i - pos['i']))
                pos = None
            else:
                # updates effective from next bar
                pos['ext'] = max(pos['ext'], h[i]) if d == 1 else min(pos['ext'], l[i])
                if P['be_at'] is not None and not pos['be'] and (pos['ext'] - e) * d >= P['be_at'] * D:
                    pos['be'] = True
                    nsl = e + d * P['be_off'] * D
                    pos['sl'] = max(pos['sl'], nsl) if d == 1 else min(pos['sl'], nsl)
                if P['trail'] and (pos['be'] or P['be_at'] is None):
                    if P['trail'] == 'atr':
                        nsl = pos['ext'] - d * P['trail_k'] * atr[i]
                    else:  # supertrend line
                        nsl = tstop[i] if trend[i] == d else pos['sl']
                    pos['sl'] = max(pos['sl'], nsl) if d == 1 else min(pos['sl'], nsl)
        # ---- indicator update at close
        if np.isnan(atr[i]): continue
        for d, piv in ((1, pl[i]), (-1, ph[i])):
            if trend[i] != d or not piv: continue
            p = i - L
            if d == 1: top = min(o[p], c[p]); bot = top - atr[i]
            else: bot = max(o[p], c[p]); top = bot + atr[i]
            if any(not (bot > ob['top'] or top < ob['bot']) for ob in obs): continue
            ok = True
            if P['use_age'] and age[i] < P['min_age']: ok = False
            if P['use_dist'] and ((bot - tstop[i]) if d == 1 else (tstop[i] - top)) < P['dist_mult'] * atr[i]: ok = False
            if P['use_htf'] and (np.isnan(he[i]) or ((c[i] <= he[i]) if d == 1 else (c[i] >= he[i]))): ok = False
            if not ok: continue
            oid += 1
            obs.append(dict(top=top, bot=bot, d=d, id=oid, prev=None, traded=False))
            if len(obs) > P['max_obs']: obs.pop(0)
        # breaks
        obs = [ob for ob in obs if not ((ob['d'] == 1 and h[i] < ob['bot']) or (ob['d'] == -1 and l[i] > ob['top']))]
        # signals
        inr = (t0 is None or idx[i] >= t0) and (t1 is None or idx[i] < t1)
        sess_ok = P['sess'] is None or (P['sess'][0] <= hour[i] < P['sess'][1])
        for ob in reversed(obs):  # most recent first
            if pos is None and pend is None and inr and sess_ok and not chg[i] and not (P['one_per_ob'] and ob['traded']):
                if ob['d'] == 1 and P['longs'] and not pl[i] and ob['prev'] is not None and l[i] > ob['top'] and l[i - 1] <= ob['prev']:
                    pend = (1, ob['id'], atr[i]); ob['traded'] = True
                elif ob['d'] == -1 and P['shorts'] and not ph[i] and ob['prev'] is not None and h[i] < ob['bot'] and h[i - 1] >= ob['prev']:
                    pend = (-1, ob['id'], atr[i]); ob['traded'] = True
            ob['prev'] = ob['top'] if ob['d'] == 1 else ob['bot']
    return pd.DataFrame(trades)

def st2(T, split=None, weeks=None):
    if len(T) == 0: return dict(n=0)
    T = T.sort_values('tx')
    eq = T.R.cumsum(); dd = (eq.cummax() - eq).max()
    w = T[T.R > 0].R.sum(); lo = -T[T.R < 0].R.sum()
    out = dict(n=len(T), PF=round(w / lo, 2) if lo > 0 else 99, R=round(T.R.sum(), 1), dd=round(dd, 1),
               RoDD=round(T.R.sum() / dd, 2) if dd > 0 else 99,
               cons=int((T.R < 0).astype(int).groupby((T.R >= 0).cumsum()).sum().max()))
    if weeks: out['tr_wk'] = round(len(T) / weeks, 2)
    if split is not None:
        I = T[T.t < split]; O = T[T.t >= split]
        for nm, X in (('IS', I), ('OOS', O)):
            ww = X[X.R > 0].R.sum(); ll = -X[X.R < 0].R.sum()
            out['PF_' + nm] = round(ww / ll, 2) if ll > 0 else 99
            out['R_' + nm] = round(X.R.sum(), 1)
    m = T.groupby(T.tx.dt.to_period('M')).R.sum()
    out['mesi_pos'] = f"{(m > 0).sum()}/{len(m)}"
    return out
