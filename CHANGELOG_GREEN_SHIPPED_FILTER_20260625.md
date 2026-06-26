# CHANGELOG - Green Shipped Row Filter 20260625

## 修改目的
針對 Forecast backlog Excel 最左邊 First Sheet 增加「綠色底色列」處理規則。

## 修改內容
1. `collectors/backlog_reader.py`
   - 改用 openpyxl 讀取 xlsx/xlsm，保留 cell fill color 資訊。
   - 新增綠色列判斷：A~L 欄位中綠色底色 >= 6 格，即判定為已出貨列。
   - 每筆資料增加追蹤欄位：`__excel_row`、`__is_shipped`、`__green_cells`、`__green_checked_cells`。

2. `core/normalizer.py`
   - 保留綠色列判斷結果到標準化資料：`is_shipped_green`、`excel_row`、`green_cells`。

3. `main.py`
   - 產報前將資料分流為：
     - Active Backlog：非綠色列，列入主報表與 loading 計算。
     - Shipped Green Rows：綠色列，不列入主報表與 loading 計算。

4. `reports/dvt_report_writer.py`
   - Dashboard 增加 Active / Shipped rows 與 Qty 統計。
   - 新增 `已出貨_Shipped` sheet。
   - 新增 `Check_Log` sheet，記錄各來源檔案、選取 sheet、讀取筆數、排除綠色筆數與數量。

## 查核項目
- [x] Python syntax check passed。
- [x] 使用測試 Excel ZIP 驗證：綠色列不進入 Back log 明細。
- [x] 使用測試 Excel ZIP 驗證：綠色列會進入 `已出貨_Shipped` sheet。
- [x] Validation qty 以 Active Backlog rows 為準，驗證 PASS。
- [x] 保留上一版 WinError 32 暫存檔清除修正。
- [x] 保留上一版 First Sheet only 規則。

## 版本說明
此版為第一版 Shipped green row filter。若後續綠色不是標準 RGB / indexed green，可能需要依實際 Excel 色碼再擴充判斷條件。
