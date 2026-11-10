"""Aggiunge la radice di trad al sys.path, cosi' i test importano `motore.*` e `magazzino.*`."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
