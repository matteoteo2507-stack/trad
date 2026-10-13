"""Definizione delle 4 strategie del portafoglio VTOB e caricamento dati.
Ogni strategia = (timeframe, parametri indicatore per core(), parametri trade per run2())."""
import os, pandas as pd
from vtob_bt import load, core
from vtob_v2 import run2, st2

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
AGG = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'spread': 'median'}

def dati(tf):
    """tf: 'M5','M15','M30','H1','H4'. M30/H1/H4 sono ricampionati dal M15 (stessi orari del server MT5)."""
    if tf == 'M5':
        return load(os.path.join(DATA, 'XAUUSD_M5.csv'))
    m15 = load(os.path.join(DATA, 'XAUUSD_M15.csv'))
    if tf == 'M15':
        return m15
    rule = {'M30': '30min', 'H1': '60min', 'H4': '240min'}[tf]
    return m15.resample(rule, label='left', closed='left').agg(AGG).dropna(subset=['open'])

STRATEGIE = {
    # nome: (tf, parametri indicatore, parametri trade)
    'A_M15': ('M15', dict(pivot_left=7,  pivot_len=3, htf='60min'),   dict(min_age=20, shorts=False, k=6, rr=3, be_at=1.0)),
    'B_H1':  ('H1',  dict(pivot_left=10, pivot_len=3, htf='1440min'), dict(min_age=10, shorts=True,  k=3, rr=4, be_at=1.0)),
    'C_M30': ('M30', dict(pivot_left=5,  pivot_len=2, htf='240min'),  dict(min_age=20, shorts=True,  k=8, rr=3, be_at=1.0)),
    'D_M5':  ('M5',  dict(pivot_left=10, pivot_len=5, htf='60min'),   dict(min_age=20, shorts=False, k=6, rr=4, be_at=1.0)),
}

def trades(nome, **override):
    tf, ck, rk = STRATEGIE[nome]
    df = dati(tf)
    K = core(df, **ck)
    T = run2(K, **{**rk, **override})
    T['strategia'] = nome
    return T, df
