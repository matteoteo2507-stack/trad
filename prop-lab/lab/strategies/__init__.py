"""Ogni file .py in questa cartella (tranne base) è una FAMIGLIA di strategie.
Per aggiungerne una nuova: crea lab/strategies/<famiglia>.py (vedi skill famiglia-strategie)."""
import importlib
import pkgutil


def load_all():
    for m in pkgutil.iter_modules(__path__):
        if m.name != "base":
            importlib.import_module(f"{__name__}.{m.name}")
