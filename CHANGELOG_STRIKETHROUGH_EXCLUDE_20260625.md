# CHANGELOG_STRIKETHROUGH_EXCLUDE_20260625

## 修改目的
針對 Forecast Backlog Excel 來源資料中，Model 欄位被設定刪除線的列，視為取消/作廢資料，避免被納入主報表、Date_Loading、Risk_List 及各項統計。

## 修改內容
1. `collectors/backlog_reader.py`
   - 新增 Model 欄位定位邏輯。
   - 新增 Excel 字型刪除線偵測。
   - 每筆資料增加 `__is_strikethrough`、`__strikethrough_checked_column` 追蹤欄位。
   - Runtime Log 增加 `model_strikethrough_rows`。

2. `core/normalizer.py`
   - 標準化資料增加 `is_model_strikethrough`。
   - 增加 `excluded_reason = Model strikethrough`。

3. `main.py`
   - Model 欄位刪除線資料一律從主統計資料排除。
   - 排除邏輯優先於綠色列處理。
   - Run Summary 增加 `model_strikethrough_excluded_rows`。

4. `reports/dvt_report_writer.py`
   - 新增 `排除資料_Excluded` Sheet。
   - Dashboard 增加 Model Strikethrough Excluded Rows / Qty。
   - Check_Log 增加刪除線排除筆數與數量。

## 統計規則
- First Sheet / 手動 Sheet / 全部 Sheet 模式仍保留。
- 綠色列是否保留仍由 GUI 勾選控制。
- Model 欄位有刪除線者，一律不進主報表。
- Model 欄位刪除線資料會寫入 `排除資料_Excluded` 供查核。

## 查核項目
- Python syntax check：PASS。
- GUI 參數相容性：PASS。
- GitHub Actions 檔案結構保留：PASS。
- `requirements.txt` 保留於根目錄：PASS。

## 驗證重點
- `STB-7078-DIG (301153-001)` 這類 Model 欄位有刪除線資料，不應出現在 Date_Loading / Risk_List / Back log 明細。
- 該資料應出現在 `排除資料_Excluded`，且 `excluded_reason` 應為 `Model strikethrough`。
