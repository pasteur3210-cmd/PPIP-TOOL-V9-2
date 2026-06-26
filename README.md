# PPIP 生產排程 DVT 報表產生器 - Integrated Logging Edition

本版本已整合：
- DVT 樣本格式產報流程
- runtime log
- error log（含 traceback）
- data quality log
- run_summary.json
- validation_log.xlsx

## CLI
```bash
pip install -r requirements.txt
python main.py 生產排程.zip --as-of-date 2026-06-24 --output-dir outputs --log-dir logs --validation-dir validation
```

## UI
```bash
streamlit run app.py
```

## 每次執行輸出
```text
outputs/DVT_Production_Schedule_{as_of_date}_{run_id}.xlsx
logs/runtime/ppip_{run_id}.log
logs/error/error_{run_id}.log
logs/data_quality/data_quality_{run_id}.log
logs/run_summary/run_summary_{run_id}.json
validation/validation_log_{run_id}.xlsx
```

## V1 驗收條件
1. runtime log 必須存在。
2. error log 發生錯誤時必須有 traceback。
3. data_quality log 必須記錄 TBD、日期錯、數量轉換問題。
4. validation_log.xlsx 必須驗證 Raw schedule qty = Monthly matrix qty。
5. UI 必須提供報表與 log 下載。

## 2026-06-25 Sheet讀取規則更新

本版本預設只讀取每個 Excel 檔案最左邊第一個 Sheet，避免過往歷史 Sheet 被一起整理進報表。

- GUI 使用方式不變。
- ZIP 內每個 Excel 仍可放多個 Sheet。
- 程式只會讀取每個 Excel 的第一個 Sheet。
- Runtime log 會記錄實際讀取的 Sheet 名稱。

CLI 可使用：

```bash
python main.py production_schedule.zip --as-of-date 2026-06-25 --sheet-mode first
```

如需讀取全部 Sheet，可改用：

```bash
python main.py production_schedule.zip --as-of-date 2026-06-25 --sheet-mode all
```

## 20260625 Update - Green Shipped Row Filter

本版新增綠色列處理規則：

- 仍然只讀取每個 Excel 最左邊第一個 Sheet。
- 若資料列 A~L 欄位中有 6 格以上為綠色底色，程式判定該列為「已出貨」。
- 已出貨綠色列不列入主報表、Monthly/Weekly/Date loading 與 Risk List。
- 已出貨綠色列會另存到輸出報表的 `已出貨_Shipped` sheet。
- 輸出報表增加 `Check_Log` sheet，方便查核各來源 Excel 的讀取筆數、排除筆數與數量。

## 2026-06-25 更新：Sheet 選擇與綠色列保留選項

新增 GUI 功能：

1. 資料統計範圍
   - 使用 First Sheet only（預設）
   - 手動勾選存在的 Sheet
   - 讀取全部 Sheet

2. 綠色已出貨列處理
   - 預設排除綠色列，不列入主報表
   - 可取消勾選，將綠色列保留在主報表
   - 綠色列不論是否保留，都會另外寫入 `已出貨_Shipped`

3. 查核紀錄
   - `Check_Log` 會記錄每個來源檔案、選擇 Sheet、統計筆數、綠色列筆數、主報表納入筆數、綠色列是否排除。

預設行為仍維持舊版：First Sheet only + 排除綠色列。

## 2026-06-25 Update - Model 刪除線排除

本版新增 Excel Model 欄位刪除線判斷：

- Model 欄位有刪除線的列，視為取消/作廢資料。
- 一律不納入主報表、Date_Loading、Risk_List 與統計。
- 排除資料會寫入 `排除資料_Excluded` Sheet。
- `Check_Log` 會留下來源檔案、Sheet、排除筆數與數量，方便查核。

## 2026-06-25 Factory Mapping 功能

本版新增 Factory 對照表功能：

1. GUI 可上傳 `factory_mapping.xlsx` 或 `.csv`。
2. 對照表欄位需包含：`region`, `model_keyword`, `Factory`。
3. 程式依 `region + model_keyword` 對應工廠名稱。
4. 找不到對照時，Factory 顯示 `Unknown`，並在 `Check_Log` 記錄 `factory_mapping_missing_rows`。
5. 以下 Sheet 的 `customer` 欄位改為 `Factory`：
   - Monthly_Loading
   - Weekly_Loading
   - Date_Loading
   - Risk_List
   - 已出貨_Shipped

對照表範本位於：

```text
config/factory_mapping_template_20260625.xlsx
config/factory_mapping_template.csv
```



## 2026-06-26 更新：Factory Mapping 修正 + Loading 總數量

本版修正報表格式與 Factory 對照邏輯，並於 `Monthly_Loading`、`Weekly_Loading`、`Date_Loading` 的 `model_normalized` 後新增 `Loading 總數量` 欄位。

### Factory 對照優先順序
1. `region + model_keyword` 符合。
2. `ALL/*/空白 + model_keyword` 符合。
3. 若 `model_keyword` 在對照表中只對應一個 Factory，允許 model-only fallback。
4. 若同一 model 對應多個 Factory，標記 `CONFLICT` 並顯示 `Unknown`，避免誤判。

### Loading 總數量
`Loading 總數量` = 該列右側所有日期 / 週別 / 月份 loading 數量加總，不包含 `region`、`Factory`、`model_normalized` 等文字欄位。

## 2026-06-26 V9 更新：Current FCD 空白資料納入 Loading
- Current FCD 空白 / TBD / 非日期資料，仍會進 Risk_List。
- 若 shipment_qty > 0，也會納入 Date_Loading / Weekly_Loading / Monthly_Loading。
- 這類資料會統一加總到「未排日期」欄位。
- Loading 總數量已包含「未排日期」數量。
- GitHub Actions 只產出 GUI 版 PPIP_Production_Planning_Reporter.exe，不再產出 PPIP_Reporter_CLI.exe。
