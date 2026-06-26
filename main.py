from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse

from collectors.backlog_reader import read_backlog_zip
from core.normalizer import normalize_backlog
from core.schedule_rules import apply_schedule_rules
from core.loading_matrix import build_loading_tables
from core.factory_mapping import load_factory_mapping, apply_factory_mapping
from core.validator import validate_report_inputs, validate_output
from reports.dvt_report_writer import write_dvt_report
from utils.logger import setup_logging, write_run_summary, new_run_id, get_log_paths


def generate_report(zip_path, as_of_date, include_tbd=True, output_dir="outputs", log_dir="logs", validation_dir="validation", sheet_mode="first", selected_sheets=None, exclude_green=True, factory_mapping_path=None):
    """Generate DVT-style production planning report with runtime/error/data-quality logs."""
    run_id = new_run_id()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logging(run_id, base_dir=log_dir)
    started = datetime.now()
    logger.info("RUN_START | run_id=%s | as_of_date=%s | zip_path=%s | include_tbd=%s | sheet_mode=%s | exclude_green=%s | selected_sheets=%s | factory_mapping_path=%s", run_id, as_of_date, zip_path, include_tbd, sheet_mode, exclude_green, selected_sheets, factory_mapping_path)
    summary = {
        "as_of_date": as_of_date,
        "input_zip": str(zip_path),
        "include_tbd": include_tbd,
        "sheet_mode": sheet_mode,
        "selected_sheets": selected_sheets or {},
        "exclude_green": exclude_green,
        "factory_mapping_path": str(factory_mapping_path) if factory_mapping_path else "",
        "output_dir": str(output_dir),
    }
    try:
        raw = read_backlog_zip(zip_path, as_of_date=as_of_date, logger=logger, sheet_mode=sheet_mode, selected_sheets=selected_sheets)
        std = normalize_backlog(raw, logger=logger)
        factory_rules = load_factory_mapping(factory_mapping_path, logger=logger)
        std = apply_factory_mapping(std, factory_rules, logger=logger)
        excluded_rows = [r for r in std if r.get("is_model_strikethrough")]
        non_excluded_rows = [r for r in std if not r.get("is_model_strikethrough")]
        shipped_rows = [r for r in non_excluded_rows if r.get("is_shipped_green")]
        if exclude_green:
            active_rows = [r for r in non_excluded_rows if not r.get("is_shipped_green")]
        else:
            active_rows = list(non_excluded_rows)
        logger.info(
            "ROW_SPLIT | total_rows=%s | report_rows=%s | shipped_green_rows=%s | model_strikethrough_excluded_rows=%s | exclude_green=%s",
            len(std),
            len(active_rows),
            len(shipped_rows),
            len(excluded_rows),
            exclude_green,
        )
        checked = validate_report_inputs(active_rows, logger=logger)
        classified = apply_schedule_rules(checked, include_tbd=include_tbd, logger=logger)
        tables = build_loading_tables(classified, logger=logger)
        out = output_dir / f"DVT_Production_Schedule_{as_of_date}_{run_id}.xlsx"
        write_dvt_report(tables, classified, out, logger=logger, shipped_rows=shipped_rows, all_rows=std, excluded_rows=excluded_rows, sheet_mode=sheet_mode, exclude_green=exclude_green)
        validation_path = validate_output(classified, tables, run_id, validation_dir=validation_dir, logger=logger)
        elapsed = round((datetime.now() - started).total_seconds(), 2)
        final_summary = {
            **summary,
            "status": "SUCCESS",
            "run_id": run_id,
            "output": str(out),
            "validation_log": str(validation_path),
            "raw_rows": len(raw),
            "standard_rows": len(std),
            "report_rows": len(active_rows),
            "shipped_green_rows": len(shipped_rows),
            "model_strikethrough_excluded_rows": len(excluded_rows),
            "exclude_green": exclude_green,
            "factory_mapping_rules": len(factory_rules),
            "factory_mapping_missing_rows": sum(1 for r in std if r.get("factory_mapping_status") == "MISSING"),
            "duration_seconds": elapsed,
        }
        write_run_summary(run_id, "SUCCESS", final_summary, base_dir=log_dir)
        logger.info("RUN_END | status=SUCCESS | run_id=%s | duration_seconds=%s | output=%s", run_id, elapsed, out)
        return {
            "run_id": run_id,
            "output": str(out),
            "validation_log": str(validation_path),
            **get_log_paths(run_id, log_dir),
        }
    except Exception as exc:
        elapsed = round((datetime.now() - started).total_seconds(), 2)
        logger.exception("CRITICAL | RUN_FAILED | run_id=%s | duration_seconds=%s | error=%s", run_id, elapsed, exc)
        write_run_summary(run_id, "FAILED", {**summary, "error": str(exc), "duration_seconds": elapsed}, base_dir=log_dir)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PPIP DVT production planning report generator")
    parser.add_argument("zip_path")
    parser.add_argument("--as-of-date", required=True)
    parser.add_argument("--include-tbd", action="store_true", default=True)
    parser.add_argument("--sheet-mode", choices=["first", "all", "manual"], default="first", help="first=只讀每個Excel最左邊Sheet；all=讀取全部Sheet；manual=搭配GUI選擇Sheet")
    parser.add_argument("--include-green", action="store_true", help="保留綠色已出貨列在主報表；預設會排除綠色列")
    parser.add_argument("--factory-mapping", default="", help="Factory mapping xlsx/csv path")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--validation-dir", default="validation")
    args = parser.parse_args()
    result = generate_report(args.zip_path, args.as_of_date, args.include_tbd, args.output_dir, args.log_dir, args.validation_dir, sheet_mode=args.sheet_mode, exclude_green=not args.include_green, factory_mapping_path=args.factory_mapping or None)
    print(result)
