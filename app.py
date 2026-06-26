from __future__ import annotations

from pathlib import Path
import tempfile
import streamlit as st

from collectors.backlog_reader import inspect_backlog_zip_sheets
from main import generate_report

st.set_page_config(page_title="PPIP 生產排程產報", layout="wide")
st.title("PPIP 生產排程 DVT 報表產生器 - Integrated Logging Edition")

zip_file = st.file_uploader("上傳生產排程.zip", type=["zip"])
factory_mapping_file = st.file_uploader("上傳 Factory 對照表（factory_mapping.xlsx / csv，可選）", type=["xlsx", "xlsm", "xls", "csv"], help="欄位需包含 region, model_keyword, Factory。若不上傳，Factory會顯示Unknown。")
as_of_date = st.date_input("As-of Date / 報表基準日")
include_tbd = st.checkbox("TBD項目納入Risk List", value=True)

st.subheader("資料統計範圍")
sheet_mode_label = st.radio(
    "Sheet讀取模式",
    options=["使用 First Sheet only（預設）", "手動勾選存在的 Sheet", "讀取全部 Sheet"],
    index=0,
    help="預設維持舊版邏輯：每個Excel只讀最左邊第一個Sheet。",
)
if sheet_mode_label.startswith("使用 First"):
    sheet_mode = "first"
elif sheet_mode_label.startswith("手動"):
    sheet_mode = "manual"
else:
    sheet_mode = "all"

st.subheader("綠色已出貨列處理")
exclude_green = st.checkbox("排除綠色列，不列入主報表", value=True)
st.caption("不論是否排除，綠色列都會另外整理到『已出貨_Shipped』Sheet，並寫入 Check_Log。")

selected_sheets: dict[str, list[str]] = {}
if zip_file and sheet_mode == "manual":
    st.info("請先確認要納入統計的 Sheet；未勾選的 Sheet 不會進入統計。")
    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp) / "production_schedule.zip"
        temp.write_bytes(zip_file.getvalue())
        try:
            sheet_info = inspect_backlog_zip_sheets(temp)
        except Exception as exc:
            st.error(f"掃描 ZIP Sheet 失敗: {exc}")
            sheet_info = []
    for item in sheet_info:
        source_file = item["source_file"]
        sheets = item.get("sheets", [])
        default = sheets[:1]
        selected = st.multiselect(
            f"{source_file} / {item.get('region', 'UNKNOWN')}",
            options=sheets,
            default=default,
            key=f"sheet_select_{source_file}",
        )
        selected_sheets[source_file] = selected
elif sheet_mode == "first":
    st.info("目前設定：每個Excel只統計最左邊第一個Sheet。")
else:
    st.warning("目前設定：會統計每個Excel內所有有效Sheet，請確認不會把舊紀錄一起納入。")

if st.button("Preflight Check / Generate Report"):
    if not zip_file:
        st.error("請先上傳ZIP")
    elif sheet_mode == "manual" and not any(selected_sheets.values()):
        st.error("手動模式下，請至少勾選一個 Sheet")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp) / "production_schedule.zip"
            temp.write_bytes(zip_file.getvalue())
            factory_mapping_path = None
            if factory_mapping_file is not None:
                factory_mapping_path = Path(tmp) / factory_mapping_file.name
                factory_mapping_path.write_bytes(factory_mapping_file.getvalue())
            try:
                result = generate_report(
                    temp,
                    as_of_date=str(as_of_date),
                    include_tbd=include_tbd,
                    sheet_mode=sheet_mode,
                    selected_sheets=selected_sheets if sheet_mode == "manual" else None,
                    exclude_green=exclude_green,
                    factory_mapping_path=factory_mapping_path,
                )
                st.success(f"報表已產出: {result['output']}")
                st.write("Run ID:", result["run_id"])
                for label, key in [
                    ("下載Excel報表", "output"),
                    ("下載Validation Log", "validation_log"),
                    ("下載Runtime Log", "runtime_log"),
                    ("下載Error Log", "error_log"),
                    ("下載Data Quality Log", "data_quality_log"),
                    ("下載Run Summary", "run_summary"),
                ]:
                    path = Path(result[key])
                    if path.exists():
                        st.download_button(label, path.read_bytes(), file_name=path.name)
            except Exception as exc:
                st.error(f"產報失敗: {exc}")
                st.warning("請下載 error log / runtime log 交給程式維護者追查。")
