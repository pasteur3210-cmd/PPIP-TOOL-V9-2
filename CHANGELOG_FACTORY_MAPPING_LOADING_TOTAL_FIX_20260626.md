# CHANGELOG - Factory Mapping Fix + Loading 總數量 - 2026-06-26

## 修改目的
修正 V7 報表格式與 Factory 對照問題，並新增 Loading 總數量欄位。

## 修改內容
1. `reports/dvt_report_writer.py`
   - 修正報表標題格式錯位。
   - 第 1 列保留 Sheet 名稱。
   - 第 2 列為欄位標題並套用藍底白字。
   - 第 3 列開始為資料內容。
   - `Check_Log` 新增 Factory conflict / model-only fallback 統計欄位。

2. `core/factory_mapping.py`
   - Factory 對照邏輯改為四層優先順序：
     1. region + model_keyword
     2. ALL / * / 空白 + model_keyword
     3. model_keyword 唯一 Factory fallback
     4. 多 Factory 衝突時標記 CONFLICT，不自動亂填。

3. `core/loading_matrix.py`
   - `Monthly_Loading` / `Weekly_Loading` / `Date_Loading` 新增 `Loading 總數量` 欄位。
   - 欄位位置固定在 `model_normalized` 後面。
   - 加總範圍只包含日期、週別、月份 loading 數值欄位。

## 查核項目
- [x] Python 語法檢查通過。
- [x] Loading 總數量欄位插入位置正確。
- [x] Validation 加總排除 Loading 總數量，避免重複加總。
- [x] 報表欄位標題固定在第 2 列。
- [x] Factory mapping 支援 model-only unique fallback。
- [x] Factory mapping conflict 不會自動亂填。

## 驗證方式
- 執行 `python -m py_compile` 檢查主要程式。
- 使用測試資料產生報表，檢查輸出 Excel 的 `Monthly_Loading`、`Weekly_Loading`、`Date_Loading`。
- 檢查 `Check_Log` 是否記錄 Factory mapping missing / conflict / model-only fallback。

## 版本
`PPIP_GitHub_Build_Ready_FactoryMapping_LoadingTotalFix_20260626`
