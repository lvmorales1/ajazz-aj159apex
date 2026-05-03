from __future__ import annotations

import sys
from pathlib import Path


root = Path(__file__).resolve().parent.parent
src = root / "src"
if src.exists():
    src_path = str(src)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
