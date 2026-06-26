from __future__ import annotations

from pathlib import Path
from typing import Any
import logging
import pandas as pd

MAPPING_COLUMNS = ["region", "model_keyword", "Factory"]


def _clean_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def load_factory_mapping(mapping_path=None, logger: logging.Logger | None = None) -> list[dict]:
    """Load factory mapping from xlsx/csv.

    Expected columns:
    - region: optional region condition. Use ALL or blank to match any region.
    - model_keyword: keyword contained in model_normalized or model_raw.
    - Factory: factory name to output.
    """
    if not mapping_path:
        return []
    path = Path(mapping_path)
    if not path.exists():
        if logger:
            logger.warning("FACTORY_MAPPING_NOT_FOUND | path=%s", path)
        return []
    try:
        if path.suffix.lower() in [".xlsx", ".xlsm", ".xls"]:
            df = pd.read_excel(path, dtype=object)
        else:
            df = pd.read_csv(path, dtype=object)
    except Exception as exc:
        if logger:
            logger.exception("FACTORY_MAPPING_LOAD_FAILED | path=%s | error=%s", path, exc)
        raise
    df.columns = [str(c).strip() for c in df.columns]
    # Allow lowercase user headers.
    rename = {}
    for col in df.columns:
        key = col.strip().lower().replace(" ", "_")
        if key == "factory":
            rename[col] = "Factory"
        elif key in ["model_keyword", "model", "model_name", "model_normalized"]:
            rename[col] = "model_keyword"
        elif key == "region":
            rename[col] = "region"
    if rename:
        df = df.rename(columns=rename)
    missing = [c for c in MAPPING_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Factory mapping缺少欄位: {missing}; 需要欄位: {MAPPING_COLUMNS}")
    mappings: list[dict] = []
    for _, row in df.iterrows():
        factory = _clean_text(row.get("Factory"))
        keyword = _clean_text(row.get("model_keyword"))
        region = _clean_text(row.get("region"))
        if not factory or not keyword:
            continue
        mappings.append({
            "region": region or "ALL",
            "model_keyword": keyword,
            "factory": factory,
        })
    # Match longer/more specific keywords first.
    mappings.sort(key=lambda x: len(x.get("model_keyword", "")), reverse=True)
    if logger:
        logger.info("FACTORY_MAPPING_LOADED | path=%s | valid_rules=%s", path, len(mappings))
    return mappings


def _rule_matches_model(rule: dict, model_text: str) -> bool:
    keyword = _clean_text(rule.get("model_keyword")).lower()
    return bool(keyword) and keyword in model_text


def apply_factory_mapping(rows: list[dict], mappings: list[dict], logger: logging.Logger | None = None) -> list[dict]:
    """Apply Factory value to each normalized backlog row.

    Match priority:
    1. Same region + model_keyword contained in model_normalized/model_raw.
    2. ALL/blank/* region + model_keyword contained in model_normalized/model_raw.
    3. Model-only fallback: when a model keyword matches exactly one Factory across all regions,
       apply that Factory even if the mapping region differs from the source region.
    4. If model-only fallback finds multiple possible factories, mark as CONFLICT and keep Unknown.

    This prevents false Unknown results when the mapping list contains a model under a different
    region, while still avoiding unsafe guesses when one model maps to multiple factories.
    """
    if not rows:
        return rows

    matched = 0
    missing = 0
    conflicts = 0
    model_only = 0
    exact_region = 0
    all_region = 0

    for row in rows:
        region = _clean_text(row.get("region")).lower()
        model_text = f"{_clean_text(row.get('model_normalized'))} {_clean_text(row.get('model_raw'))}".lower()
        selected = None
        status = "MISSING"
        method = ""

        # Priority 1: same region match.
        for rule in mappings:
            rule_region = _clean_text(rule.get("region")).lower()
            if rule_region == region and _rule_matches_model(rule, model_text):
                selected = rule
                status = "MATCHED"
                method = "REGION_MODEL"
                exact_region += 1
                break

        # Priority 2: global/ALL region match.
        if selected is None:
            for rule in mappings:
                rule_region = _clean_text(rule.get("region")).lower()
                if rule_region in ["", "all", "*"] and _rule_matches_model(rule, model_text):
                    selected = rule
                    status = "MATCHED"
                    method = "ALL_MODEL"
                    all_region += 1
                    break

        # Priority 3/4: model-only unique fallback.
        if selected is None:
            candidates = [rule for rule in mappings if _rule_matches_model(rule, model_text)]
            factory_names = sorted({ _clean_text(rule.get("factory")) for rule in candidates if _clean_text(rule.get("factory")) })
            if len(factory_names) == 1 and candidates:
                selected = candidates[0]
                status = "MATCHED"
                method = "MODEL_ONLY_UNIQUE"
                model_only += 1
            elif len(factory_names) > 1:
                status = "CONFLICT"
                method = "MODEL_ONLY_CONFLICT"
                conflicts += 1

        if selected:
            row["factory"] = selected.get("factory", "")
            row["factory_mapping_status"] = status
            row["factory_mapping_method"] = method
            row["factory_mapping_rule"] = f"{selected.get('region')} + {selected.get('model_keyword')}"
            matched += 1
        else:
            row["factory"] = "Unknown"
            row["factory_mapping_status"] = status
            row["factory_mapping_method"] = method
            row["factory_mapping_rule"] = ""
            if status == "MISSING":
                missing += 1

    if logger:
        logger.info(
            "FACTORY_MAPPING_APPLIED | rows=%s | matched=%s | missing=%s | conflicts=%s | region_model=%s | all_model=%s | model_only_unique=%s",
            len(rows), matched, missing, conflicts, exact_region, all_region, model_only,
        )
        if missing or conflicts:
            examples = []
            seen = set()
            for r in rows:
                if r.get("factory_mapping_status") in ["MISSING", "CONFLICT"]:
                    key = (r.get("factory_mapping_status"), r.get("region"), r.get("model_normalized"))
                    if key not in seen:
                        examples.append(key)
                        seen.add(key)
                    if len(examples) >= 20:
                        break
            logger.warning("FACTORY_MAPPING_REVIEW_EXAMPLES | examples=%s", examples)
    return rows
