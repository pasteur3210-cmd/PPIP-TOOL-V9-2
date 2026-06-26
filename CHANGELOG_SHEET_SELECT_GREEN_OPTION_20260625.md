# CHANGELOG - Sheet 選擇與綠色列保留選項

版本日期：2026-06-25

## 修改目的

在既有可用版本基礎上，新增資料統計範圍設定，讓使用者可以決定：

1. 維持 First Sheet only。
2. 手動勾選 ZIP 內各 Excel 需要統計的 Sheet。
3. 讀取全部有效 Sheet。
4. 自行選擇綠色已出貨列是否保留在主報表。

## 修改內容

### app.py

- 新增「資料統計範圍」GUI 區塊。
- 新增 Sheet 讀取模式：
  - 使用 First Sheet only（預設）
  - 手動勾選存在的 Sheet
  - 讀取全部 Sheet
- 新增「綠色已出貨列處理」GUI 選項：
  - 排除綠色列，不列入主報表（預設勾選）
- 手動模式會先掃描 ZIP 內 Excel 的 Sheet 清單，並用 multiselect 讓使用者勾選。

### collectors/backlog_reader.py

- 新增 `inspect_backlog_zip_sheets()`，提供 GUI 掃描 ZIP 內 Excel Sheet 清單。
- 新增 `sheet_mode="manual"`。
- 新增 `selected_sheets` 參數，只讀取使用者勾選的 Sheet。
- 保留既有：
  - WinError 32 暫存檔清除容錯
  - First Sheet only 預設邏輯
  - 綠色列偵測邏輯：A~L 欄至少 6 格為綠色即視為已出貨

### main.py

- 新增 `selected_sheets` 參數。
- 新增 `exclude_green` 參數。
- `exclude_green=True`：綠色列排除於主報表，但仍寫入 `已出貨_Shipped`。
- `exclude_green=False`：綠色列保留在主報表，同時也寫入 `已出貨_Shipped` 供追蹤。

### reports/dvt_report_writer.py

- Dashboard 改為顯示 `Main Report Rows / Main Report Qty`。
- `Check_Log` 新增：
  - sheet_mode
  - exclude_green_from_main_report
  - main_report_rows
  - main_report_shipment_qty
  - rule 說明

## 預設行為

為了不影響目前已驗證可用流程，預設仍然是：

- 每個 Excel 只讀取最左邊第一個 Sheet。
- 綠色列不列入主報表。
- 綠色列另外寫入 `已出貨_Shipped`。

## 查核與驗證

已執行以下檢查：

1. Python syntax check：PASS
   - app.py
   - main.py
   - collectors/backlog_reader.py
   - reports/dvt_report_writer.py
2. ZIP Sheet 掃描功能：PASS
3. First Sheet 模式讀取：PASS
4. Manual Sheet 模式讀取：PASS
5. 綠色列保留在主報表模式：PASS
6. 報表輸出：PASS
7. Check_Log 輸出：PASS

## 風險與注意事項

- 手動模式下，如果完全沒有勾選 Sheet，程式會提示錯誤，不會產出報表。
- 「讀取全部 Sheet」可能會把歷史 Sheet 納入統計，僅建議特殊需求使用。
- 綠色列判斷仍以 A~L 欄位底色為依據。
