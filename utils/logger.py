"""PPIP runtime/error/data-quality logging utilities.

V1 acceptance requirement:
- Every report run must have one run_id.
- runtime/error/data_quality/run_summary/validation files must share the same run_id.
- Any uncaught exception must be written to error.log with traceback.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s"


def new_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def setup_logging(run_id: str, base_dir: str | Path = "logs", console: bool = True) -> logging.Logger:
    """Create PPIP logger with runtime, error and data-quality handlers."""
    base = Path(base_dir)
    for sub in ["runtime", "error", "data_quality", "run_summary"]:
        (base / sub).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("ppip")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False
    formatter = logging.Formatter(LOG_FORMAT)

    runtime_handler = RotatingFileHandler(
        base / "runtime" / f"ppip_{run_id}.log",
        maxBytes=5_000_000,
        backupCount=10,
        encoding="utf-8",
    )
    runtime_handler.setLevel(logging.INFO)
    runtime_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        base / "error" / f"error_{run_id}.log",
        maxBytes=5_000_000,
        backupCount=20,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    data_quality_handler = RotatingFileHandler(
        base / "data_quality" / f"data_quality_{run_id}.log",
        maxBytes=5_000_000,
        backupCount=20,
        encoding="utf-8",
    )
    data_quality_handler.setLevel(logging.WARNING)
    data_quality_handler.setFormatter(formatter)

    logger.addHandler(runtime_handler)
    logger.addHandler(error_handler)
    logger.addHandler(data_quality_handler)

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_log_paths(run_id: str, base_dir: str | Path = "logs") -> dict[str, str]:
    base = Path(base_dir)
    return {
        "runtime_log": str(base / "runtime" / f"ppip_{run_id}.log"),
        "error_log": str(base / "error" / f"error_{run_id}.log"),
        "data_quality_log": str(base / "data_quality" / f"data_quality_{run_id}.log"),
        "run_summary": str(base / "run_summary" / f"run_summary_{run_id}.json"),
    }


def write_run_summary(run_id: str, status: str, payload: dict[str, Any], base_dir: str | Path = "logs") -> Path:
    path = Path(base_dir) / "run_summary" / f"run_summary_{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "run_id": run_id,
        "status": status,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **payload,
        "log_paths": get_log_paths(run_id, base_dir),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
