"""
Pytest configuration: make the src/ modules importable.

The src/ modules use flat imports (e.g. `from recommender import ...`,
`from logging_config import ...`), matching how the app runs (`python src/main.py`
puts src/ on the path). Adding src/ to sys.path here lets the test suite import
them the same way, so `from retriever import Retriever` etc. resolve correctly.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
