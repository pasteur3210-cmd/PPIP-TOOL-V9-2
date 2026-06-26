from __future__ import annotations

import os
import sys
from pathlib import Path

from streamlit.web import cli as stcli


def resource_path(relative_path: str) -> str:
    """Return path for PyInstaller one-file/one-dir execution."""
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return str(Path(base_path) / relative_path)


if __name__ == "__main__":
    app_path = resource_path("app.py")
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())
