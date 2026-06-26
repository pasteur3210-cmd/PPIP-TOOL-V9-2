from __future__ import annotations

import logging
from datetime import date

RISK_KEYWORDS = ["TBD", "Hold", "Payment", "ETA", "shortage", "FW", "rework", "pull in", "delay", "waiting"]


def _risk_level(row: dict) -> str:
    text = " ".join(str(row.get(k, "")) for k in ["current_fcd", "actual_date", "remark"]).lower()
    if any(k.lower() in text for k in ["hold", "payment", "shortage"]):
        return "HIGH"
    if "tbd" in text or "delay" in text or "waiting" in text:
        return "MEDIUM"
    if row.get("current_fcd") in [None, "", "TBD"]:
        return "MEDIUM"
    return "LOW"


def apply_schedule_rules(rows: list[dict], include_tbd=True, logger: logging.Logger | None = None) -> list[dict]:
    output = []
    for row in rows:
        current_fcd = row.get("current_fcd")
        include = bool(row.get("shipment_qty", 0) > 0 and isinstance(current_fcd, date))
        risk = _risk_level(row)
        if current_fcd == "TBD" and include_tbd:
            risk = "MEDIUM" if risk == "LOW" else risk
        row = {**row, "include_in_schedule": include, "risk_level": risk}
        output.append(row)
    if logger:
        sched_rows = sum(1 for r in output if r["include_in_schedule"])
        risk_rows = sum(1 for r in output if r["risk_level"] in ["MEDIUM", "HIGH"])
        logger.info("RULES_DONE | schedule_rows=%s | risk_rows=%s | include_tbd=%s", sched_rows, risk_rows, include_tbd)
    return output
