"""Ricerca a griglia su un timeframe (stessa griglia usata per trovare il portafoglio: 11.520 varianti per TF).
Uso:  python run_grid.py M15   (oppure M5, M30, H1)   -> ../risultati/griglia_<TF>.csv
Su un PC con molti core è veloce (multiprocessing). Modifica le liste qui sotto per esplorare altro."""
import sys, os, itertools, pandas as pd
from multiprocessing import Pool
from strategie import dati, HERE
from vtob_bt import core
from vtob_v2 import run2, st2

TF = sys.argv[1] if len(sys.argv) > 1 else 'M15'
df = dati(TF)
SPLIT = '2026-02-01' if TF == 'M5' else '2025-07-01'
W = (df.index[-1] - df.index[0]).days / 7
HTFS = {'M5': ['60min', '240min'], 'M15': ['60min', '240min'], 'M30': ['240min', '1440min'], 'H1': ['240min', '1440min'], 'H4': ['1440min']}[TF]
PIVS = [(7, 3), (10, 3), (14, 4), (10, 5)] if TF == 'M5' else [(5, 2), (7, 3), (10, 3), (7, 4)]
AGES = [20, 60, 120] if TF == 'M5' else [10, 20, 40]
EXITS = [e for e in itertools.product([2.0, 3.0, 4.0, None], [None, 1.0], [None, ('atr', 2.0), ('atr', 3.0), ('st', 0)], [None, 1.0])
         if not (e[0] is None and e[2] is None)]

def job(args):
    (pl, pr), htf = args
    K = core(df, pivot_len=pr, pivot_left=pl, htf=htf)
    rows = []
    for age, dirs, k, (rr, be, tr, pa) in itertools.product(AGES, ['long', 'both'], [3, 4, 6, 8], EXITS):
        T = run2(K, min_age=age, shorts=(dirs == 'both'), k=k, rr=rr, be_at=be,
                 trail=tr[0] if tr else None, trail_k=tr[1] if tr else 0, part_at=pa)
        s = st2(T, SPLIT, W)
        if s['n']:
            rows.append(dict(tf=TF, piv=f'{pl}/{pr}', htf=htf, age=age, dir=dirs, k=k, rr=rr, be=be, trail=str(tr), part=pa, **s))
    return rows

if __name__ == '__main__':
    jobs = list(itertools.product(PIVS, HTFS))
    with Pool(min(len(jobs), os.cpu_count())) as p:
        res = p.map(job, jobs)
    D = pd.DataFrame([r for rr in res for r in rr])
    out = os.path.join(HERE, '..', 'risultati', f'griglia_{TF}.csv'); D.to_csv(out, index=False)
    print(TF, len(D), 'varianti ->', out)
