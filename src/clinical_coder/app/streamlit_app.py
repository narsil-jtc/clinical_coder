"""Streamlit entrypoint compatibility wrapper."""

from pathlib import Path
import sys

_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from clinical_coder.ui.app import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
