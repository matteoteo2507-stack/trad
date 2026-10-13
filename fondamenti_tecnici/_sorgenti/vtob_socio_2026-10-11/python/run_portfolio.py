"""Riproduce i risultati del portafoglio: statistiche per strategia, portafoglio, rendimento mensile in %.
Uso:  python run_portfolio.py [--rischio 0.01] [--strategie A_M15,B_H1,C_M30] [--da 2022-07-12] [--a 2026-10-10]
Salva in ../risultati: trade_<strategia>.csv, portafoglio_trade.csv, portafoglio_mensile.csv"""
import argparse, os, numpy as np, pandas as pd
from strategie import STRATEGIE, trades, st2, HERE

ap = argparse.ArgumentParser()
ap.add_argument('--rischio', type=float, default=0.01)
ap.add_argument('--strategie', default='A_M15,B_H1,C_M30')
ap.add_argument('--da', default='2022-07-12'); ap.add_argument('--a', default='2026-10-10')
ap.add_argument('--split', default='2025-07-01', help='inizio periodo out-of-sample')
a = ap.parse_args()
OUT = os.path.join(HERE, '..', 'risultati'); os.makedirs(OUT, exist_ok=True)

allT = []
for nm in a.strategie.split(','):
    T, df = trades(nm)
    W = (df.index[-1] - df.index[0]).days / 7
    print(f'{nm}:', st2(T, a.split, W))
    T.to_csv(os.path.join(OUT, f'trade_{nm}.csv'), index=False)
    allT.append(T)
P = pd.concat(allT)
P = P[(P.t >= a.da) & (P.t < a.a)].sort_values('tx').reset_index(drop=True)
r = a.rischio
P['equity'] = (1 + r * P.R).cumprod()
P.to_csv(os.path.join(OUT, 'portafoglio_trade.csv'), index=False)
wk = (pd.Timestamp(a.a) - pd.Timestamp(a.da)).days / 7
dd = ((P.equity.cummax() - P.equity) / P.equity.cummax()).max() * 100
me = P.groupby(P.tx.dt.to_period('M')).equity.last()
mon = (me / me.shift(1).fillna(1.0) - 1) * 100
allm = pd.period_range(pd.Timestamp(a.da), pd.Timestamp(a.a) - pd.Timedelta(days=1), freq='M')
mon = mon.reindex(allm, fill_value=0.0)
mon.rename('rendimento_%').to_csv(os.path.join(OUT, 'portafoglio_mensile.csv'))
w = P[P.R > 0].R.sum(); l = -P[P.R < 0].R.sum(); eqR = P.R.cumsum()
rng = np.random.default_rng(0); mc = []
for _ in range(2000):
    e = np.cumprod(1 + r * rng.permutation(P.R.values)); mc.append(((np.maximum.accumulate(e) - e) / np.maximum.accumulate(e)).max() * 100)
print(f'\nPORTAFOGLIO {a.strategie} | rischio {r*100:.2f}% per trade | {a.da} -> {a.a}')
print(f'trade {len(P)} ({len(P)/wk:.2f}/settimana) | PF {w/l:.2f} | {P.R.sum():.1f} R | DD {(eqR.cummax()-eqR).max():.1f} R')
print(f'rendimento composto {(P.equity.iloc[-1]-1)*100:.0f}% | DD max {dd:.1f}% | DD Monte Carlo 95% {np.percentile(mc,95):.1f}%')
print(f'mese medio {mon.mean():.2f}% | mediano {mon.median():.2f}% | peggiore {mon.min():.1f}% | mesi positivi {(mon>0).sum()}/{len(mon)}')
print('R per anno:', P.groupby(P.tx.dt.year).R.sum().round(1).to_dict())
