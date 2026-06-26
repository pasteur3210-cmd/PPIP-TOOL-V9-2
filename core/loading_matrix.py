from __future__ import annotations

import logging
from datetime import date
import pandas as pd


def _empty_tables() -> dict[str, list[dict]]:
    return {"monthly": [], "weekly": [], "date_matrix": [], "top_model": [], "risk": []}


def _add_loading_total(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Insert Loading 總數量 after model_normalized for loading matrix reports."""
    if df.empty:
        return df
    df = df.copy()
    value_cols = [c for c in df.columns if c not in group_cols]
    df["Loading 總數量"] = df[value_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1).astype(int)
    cols = list(df.columns)
    cols.remove("Loading 總數量")
    insert_at = cols.index("model_normalized") + 1 if "model_normalized" in cols else len(group_cols)
    cols.insert(insert_at, "Loading 總數量")
    return df[cols]


UNSCHEDULED_LABEL = "未排日期"


def _is_dated_loading_row(row: dict) -> bool:
    return bool(row.get("shipment_qty", 0) > 0 and isinstance(row.get("current_fcd"), date))


def _is_blank_fcd_loading_row(row: dict) -> bool:
    """Rows with shipment qty but no usable Current FCD must still be counted in loading.

    They remain in Risk_List, and are aggregated into the loading matrices under
    the dedicated 未排日期 column so Date/Weekly/Monthly totals reconcile with
    the active backlog qty.
    """
    if not bool(row.get("shipment_qty", 0) > 0):
        return False
    current_fcd = row.get("current_fcd")
    return not isinstance(current_fcd, date)


def _order_matrix_columns(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Keep ID columns first, then Loading total, 未排日期, then sorted date/week/month buckets."""
    if df.empty:
        return df
    cols = list(df.columns)
    fixed = [c for c in group_cols + ["Loading 總數量", UNSCHEDULED_LABEL] if c in cols]
    remaining = [c for c in cols if c not in fixed]
    remaining = sorted(remaining, key=lambda x: str(x))
    return df[fixed + remaining]


def _build_pivot(df: pd.DataFrame, bucket_col: str, group_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=group_cols + ["Loading 總數量", UNSCHEDULED_LABEL])
    pivot = df.pivot_table(index=group_cols, columns=bucket_col, values="shipment_qty", aggfunc="sum", fill_value=0).reset_index()
    pivot.columns = [str(c) if c not in group_cols else c for c in pivot.columns]
    pivot = _add_loading_total(pivot, group_cols)
    return _order_matrix_columns(pivot, group_cols)


def build_loading_tables(rows: list[dict], logger: logging.Logger | None = None):
    dated_rows = [r for r in rows if _is_dated_loading_row(r)]
    blank_fcd_rows = [r for r in rows if _is_blank_fcd_loading_row(r)]
    loading_rows = dated_rows + blank_fcd_rows
    if not loading_rows:
        if logger:
            logger.error("CRITICAL | EMPTY_MATRIX | reason=no_loading_rows")
        return _empty_tables()

    df = pd.DataFrame(loading_rows)
    is_dated = df["current_fcd"].apply(lambda value: isinstance(value, date))
    dated_series = pd.to_datetime(df.loc[is_dated, "current_fcd"])
    df["month"] = UNSCHEDULED_LABEL
    df["week"] = UNSCHEDULED_LABEL
    df["date_bucket"] = UNSCHEDULED_LABEL
    df.loc[is_dated, "month"] = dated_series.dt.strftime("%Y-%m").values
    df.loc[is_dated, "week"] = dated_series.dt.strftime("%G-W%V").values
    df.loc[is_dated, "date_bucket"] = dated_series.dt.strftime("%Y-%m-%d").values

    group_cols = ["region", "factory", "model_normalized"]
    monthly = _build_pivot(df, "month", group_cols)
    weekly = _build_pivot(df, "week", group_cols)
    date_matrix = _build_pivot(df, "date_bucket", group_cols)
    top_model = df.groupby(["model_normalized"], dropna=False)["shipment_qty"].sum().reset_index().sort_values("shipment_qty", ascending=False).head(20)
    risk = pd.DataFrame([r for r in rows if r.get("risk_level") in ["MEDIUM", "HIGH"]])

    blank_fcd_qty = int(sum(int(r.get("shipment_qty") or 0) for r in blank_fcd_rows))
    if logger:
        logger.info(
            "BUILD_MATRIX | dated_rows=%s | blank_fcd_rows=%s | loading_rows=%s | loading_qty=%s | blank_fcd_qty=%s | monthly_qty=%s | weekly_qty=%s",
            len(dated_rows),
            len(blank_fcd_rows),
            len(loading_rows),
            int(df["shipment_qty"].sum()),
            blank_fcd_qty,
            int(monthly.drop(columns=["Loading 總數量"], errors="ignore").select_dtypes(include="number").sum().sum()),
            int(weekly.drop(columns=["Loading 總數量"], errors="ignore").select_dtypes(include="number").sum().sum()),
        )
    return {
        "monthly": monthly.to_dict("records"),
        "weekly": weekly.to_dict("records"),
        "date_matrix": date_matrix.to_dict("records"),
        "top_model": top_model.to_dict("records"),
        "risk": risk.to_dict("records") if not risk.empty else [],
    }
