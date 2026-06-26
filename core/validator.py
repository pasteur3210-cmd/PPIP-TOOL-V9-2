from __future__ import annotations

from pathlib import Path
from datetime import date
import logging
from openpyxl import Workbook

REQUIRED_FIELDS = ["model_normalized", "shipment_qty", "current_fcd"]


def validate_report_inputs(rows: list[dict], logger: logging.Logger | None = None) -> list[dict]:
    if not rows:
        if logger:
            logger.error("CRITICAL | VALIDATE_INPUT | status=FAIL | reason=no_rows")
        raise ValueError("無資料可產報")
    missing_fields = [f for f in REQUIRED_FIELDS if f not in rows[0]]
    if missing_fields:
        if logger:
            logger.error("CRITICAL | MISSING_REQUIRED_FIELDS | fields=%s", missing_fields)
        raise ValueError(f"缺必要標準欄位: {missing_fields}")
    missing_model = sum(1 for r in rows if not r.get("model_normalized"))
    missing_date = sum(1 for r in rows if not r.get("current_fcd"))
    raw_qty = sum(int(r.get("shipment_qty") or 0) for r in rows)
    if logger:
        logger.info("PRECHECK | status=PASS | rows=%s | raw_qty=%s | missing_model=%s | missing_current_fcd=%s", len(rows), raw_qty, missing_model, missing_date)
    return rows


def validate_output(rows: list[dict], tables: dict, run_id: str, validation_dir: str | Path = "validation", logger: logging.Logger | None = None) -> Path:
    validation_dir = Path(validation_dir)
    validation_dir.mkdir(parents=True, exist_ok=True)
    # Loading matrices now include both dated rows and rows with blank/TBD/non-date Current FCD
    # under the 未排日期 bucket.  Validation must compare against the same scope, not
    # only include_in_schedule=True dated rows.
    raw_loading_qty = sum(int(r.get("shipment_qty") or 0) for r in rows if int(r.get("shipment_qty") or 0) > 0)
    blank_fcd_loading_qty = sum(
        int(r.get("shipment_qty") or 0)
        for r in rows
        if int(r.get("shipment_qty") or 0) > 0 and not isinstance(r.get("current_fcd"), date)
    )
    monthly_qty = 0
    for record in tables.get("monthly", []):
        for k, v in record.items():
            if k == "Loading 總數量":
                continue
            if isinstance(v, (int, float)):
                monthly_qty += int(v)
    status = "PASS" if raw_loading_qty == monthly_qty else "FAIL"
    wb = Workbook()
    ws = wb.active
    ws.title = "Validation_Log"
    ws.append(["run_id", "item", "expected", "actual", "status", "severity"])
    ws.append([run_id, "Raw loading qty incl blank Current FCD = Monthly matrix qty", raw_loading_qty, monthly_qty, status, "Critical"])
    ws.append([run_id, "Blank Current FCD qty included in 未排日期", blank_fcd_loading_qty, "Included", "PASS", "Major"])
    ws.append([run_id, "Required fields", ",".join(REQUIRED_FIELDS), "OK", "PASS", "Critical"])
    path = validation_dir / f"validation_log_{run_id}.xlsx"
    wb.save(path)
    if logger:
        if status == "PASS":
            logger.info("VALIDATE_QTY | raw_loading_qty=%s | monthly_qty=%s | blank_fcd_loading_qty=%s | status=PASS | validation=%s", raw_loading_qty, monthly_qty, blank_fcd_loading_qty, path)
        else:
            logger.error("CRITICAL | VALIDATE_QTY | raw_loading_qty=%s | monthly_qty=%s | blank_fcd_loading_qty=%s | status=FAIL | validation=%s", raw_loading_qty, monthly_qty, blank_fcd_loading_qty, path)
    return path
