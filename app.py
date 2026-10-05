"""MarketSphere application entry point.

Run ``streamlit run app.py`` from the repository root. The UI lives in
``MarketSphere/MarketSphereAI`` and uses the root data and ML pipeline.
"""

from __future__ import annotations

import runpy
from pathlib import Path


UI_APP = Path(__file__).resolve().parent / "MarketSphere" / "MarketSphereAI" / "app.py"

if __name__ == "__main__":
    runpy.run_path(str(UI_APP), run_name="__main__")
