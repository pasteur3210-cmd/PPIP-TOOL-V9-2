# CHANGELOG - Sheet First Mode Fix - 2026-06-25

## 修改目的
避免 Excel 檔案內過往歷史 Sheet 被一起讀入，造成產出報表內容未整理、資料量過多或混入舊紀錄。

## 修改內容
- `collectors/backlog_reader.py`
  - 新增 `sheet_mode` 參數。
  - 預設 `sheet_mode="first"`。
  - 每個 Excel 只讀取最左邊第一個 Sheet。
  - Runtime log 會記錄被選用的 Sheet 名稱。
- `main.py`
  - `generate_report()` 新增 `sheet_mode` 參數。
  - CLI 新增 `--sheet-mode first/all` 選項。
- `app.py`
  - Streamlit GUI 預設使用 `first` 模式。
  - 畫面增加 Sheet 讀取規則提示。

## 使用方式
一般使用方式不變。上傳 ZIP 後產生報表即可。

新版預設規則：
- 每個 Excel 只讀取最左邊第一個 Sheet。
- 不會再自動讀取同一個 Excel 內其他歷史 Sheet。

## 備註
此版本為第一版功能，尚未加入 GUI 手動勾選 Sheet。後續可再增加手動選擇 Sheet 功能。
