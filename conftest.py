"""Aggiunge la root del workspace al sys.path per consentire `import strategies.*` nei test."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
