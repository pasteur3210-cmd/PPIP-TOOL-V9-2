from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any
import pandas as pd

FIELD_CANDIDATES = {
    "model_raw": ["Model", "model", "Model Name"],
    "customer": ["Customer", "customer", "Customer Name"],
    "order_qty": ["Q'ty of order", "Qty of order", "Order Qty", "order_qty"],
    "shipment_qty": ["Q'ty of shipment", "Qty of shipment", "Shipment Qty", "shipment_qty"],
    "sor_request_fcd": ["SOR request FCD", "SOR Request FCD", "sor_request_fcd"],
    "current_fcd": ["Current FCD", "current_fcd", "FCD"],
    "actual_date": ["Actual date", "Actual Date", "actual_date"],
    "remark": ["remark", "Remark", "Remark ", "Abnormal Record", "Abnormal record"],
    "freight_term": ["Freight Term", "freight_term"],
}


def _first_value(row: dict[str, Any], candidates: list[str]) -> Any:
    for key in candidates:
        if key in row and pd.notna(row[key]):
            return row[key]
    # tolerate trimmed key mismatch
    normalized = {str(k).strip(): v for k, v in row.items()}
    for key in candidates:
        if key.strip() in normalized and pd.notna(normalized[key.strip()]):
            return normalized[key.strip()]
    return None


def _to_qty(value: Any, logger: logging.Logger | None, row_id: int, field: str) -> int:
    if value is None or (isinstance(value, float) and pd.isna(value)) or str(value).strip() == "":
        return 0
    try:
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if cleaned.upper() in ["TBD", "NA", "N/A", "-"]:
                return 0
            return int(float(cleaned))
        return int(float(value))
    except Exception:
        if logger:
            logger.error("ERROR | QTY_PARSE_ERROR | row=%s | field=%s | value=%r", row_id, field, value)
        return 0


def _to_date(value: Any, logger: logging.Logger | None, row_id: int, field: str):
    if value is None or (isinstance(value, float) and pd.isna(value)) or str(value).strip() == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if text.upper() in ["TBD", "NA", "N/A", "-"]:
        if logger:
            logger.warning("DATA_QUALITY | DATE_TBD | row=%s | field=%s | value=%s", row_id, field, text)
        return "TBD"
    try:
        return pd.to_datetime(value).date()
    except Exception:
        if logger:
            logger.warning("DATA_QUALITY | INVALID_DATE | row=%s | field=%s | value=%r", row_id, field, value)
        return text


def _normalize_model(model: Any) -> tuple[str, str]:
    raw = "" if model is None else str(model).strip()
    text = re.sub(r"\s+", " ", raw)
    # preserve raw, but normalize grouping key by removing trailing parenthetical notes.
    normalized = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
    return raw, normalized or raw


def normalize_backlog(raw_rows: list[dict], logger: logging.Logger | None = None) -> list[dict]:
    std: list[dict] = []
    for idx, row in enumerate(raw_rows, start=1):
        model_raw_value = _first_value(row, FIELD_CANDIDATES["model_raw"])
        model_raw, model_normalized = _normalize_model(model_raw_value)
        order_qty = _to_qty(_first_value(row, FIELD_CANDIDATES["order_qty"]), logger, idx, "order_qty")
        shipment_qty = _to_qty(_first_value(row, FIELD_CANDIDATES["shipment_qty"]), logger, idx, "shipment_qty")
        current_fcd = _to_date(_first_value(row, FIELD_CANDIDATES["current_fcd"]), logger, idx, "current_fcd")
        sor_request_fcd = _to_date(_first_value(row, FIELD_CANDIDATES["sor_request_fcd"]), logger, idx, "sor_request_fcd")
        remark = _first_value(row, FIELD_CANDIDATES["remark"])
        record = {
            "row_id": idx,
            "region": row.get("region", "UNKNOWN"),
            "source_file": row.get("__source_file", ""),
            "sheet_name": row.get("__sheet_name", ""),
            "customer": _first_value(row, FIELD_CANDIDATES["customer"]) or "",
            "model_raw": model_raw,
            "model_normalized": model_normalized,
            "order_qty": order_qty,
            "shipment_qty": shipment_qty,
            "sor_request_fcd": sor_request_fcd,
            "current_fcd": current_fcd,
            "actual_date": _to_date(_first_value(row, FIELD_CANDIDATES["actual_date"]), logger, idx, "actual_date"),
            "remark": "" if remark is None else str(remark).strip(),
            "freight_term": _first_value(row, FIELD_CANDIDATES["freight_term"]) or "",
            "is_shipped_green": bool(row.get("__is_shipped", False)),
            "is_model_strikethrough": bool(row.get("__is_strikethrough", False)),
            "excluded_reason": "Model strikethrough" if bool(row.get("__is_strikethrough", False)) else "",
            "excel_row": row.get("__excel_row", ""),
            "green_cells": row.get("__green_cells", 0),
            "green_checked_cells": row.get("__green_checked_cells", 0),
            "strikethrough_checked_column": row.get("__strikethrough_checked_column", ""),
        }
        if not model_normalized and logger:
            logger.warning("DATA_QUALITY | MISSING_MODEL | row=%s | source=%s", idx, record["source_file"])
        std.append(record)
    if logger:
        total_qty = sum(r["shipment_qty"] for r in std)
        logger.info("NORMALIZE_DONE | rows=%s | total_shipment_qty=%s", len(std), total_qty)
    return std
