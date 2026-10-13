"""VTOB lab: replica dell'indicatore VTOB_Indicator_Pro.pine, simulatore d'esecuzione e metriche.

Moduli:
- dati:        caricamento e controllo degli export barre MT5 (file originali mai modificati);
- indicatore:  replica candela per candela dell'indicatore (OB, punteggio, invalidazione, croci di retest);
- simulatore:  esecuzione realistica e conservativa delle varianti di gestione (numba);
- metriche:    statistiche, IS/OOS, anni, Monte Carlo;
- motore:      collante (calendario, uscite forzate, tabelle dei trade).
"""
