"""Smoke test for PPIP integrated logging edition.
Run from project root:
    python tests/smoke_test.py
"""
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile
import tempfile
import sys
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from main import generate_report  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    wb = Workbook()
    ws = wb.active
    ws.title = "Forecast"
    ws.append(["Customer", "Model", "Q'ty of order", "Q'ty of shipment", "SOR request FCD", "Current FCD", "Actual date", "Remark"])
    ws.append(["C1", "M1", 100, 100, "2026-06-20", "2026-06-24", "", "OK"])
    ws.append(["C2", "M2", 50, 50, "2026-06-21", "TBD", "", "Hold payment"])
    xlsx = tmp / "EU-Spain.xlsx"
    wb.save(xlsx)
    zip_path = tmp / "production_schedule.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.write(xlsx, "EU-Spain.xlsx")
    result = generate_report(zip_path, "2026-06-24", output_dir=tmp / "outputs", log_dir=tmp / "logs", validation_dir=tmp / "validation")
    for key in ["output", "validation_log", "runtime_log", "error_log", "data_quality_log", "run_summary"]:
        assert Path(result[key]).exists(), f"missing {key}: {result[key]}"
    print("SMOKE_TEST_PASS", result["run_id"])
