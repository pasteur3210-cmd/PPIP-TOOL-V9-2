# CHANGELOG - Blank Current FCD Loading Fix

Version: V9 / 2026-06-26

## 修改目的
修正 Current FCD 空白 / TBD / 非日期資料只進 Risk_List、未進 Loading 統計的問題。

## 修改內容
1. Date_Loading / Weekly_Loading / Monthly_Loading 增加「未排日期」欄位。
2. Current FCD 空白 / TBD / 非日期，但 shipment_qty > 0 的資料，仍納入 Loading List 統計並加總到「未排日期」。
3. Risk_List 邏輯保留；空白 Current FCD 資料仍會進 Risk_List。
4. Loading 總數量會包含「未排日期」數量。
5. Validation_Log 改為比對「有 shipment_qty 的主報表資料」與 Monthly_Loading 矩陣總數。
6. Check_Log 增加 blank_current_fcd_rows_in_loading / blank_current_fcd_qty_in_loading / blank_current_fcd_included_in_loading。
7. Dashboard 增加 Blank Current FCD Loading Qty 與 Total Loading Qty incl Blank FCD。
8. GitHub Actions 移除 PPIP_Reporter_CLI.exe 編譯，只保留 GUI EXE。

## 影響檔案
- core/loading_matrix.py
- core/validator.py
- reports/dvt_report_writer.py
- .github/workflows/build.yml
- README.md
- README_GITHUB_BUILD.md

## 查核項目
- DPU-4672xs-DZSG-P1 (756016-023) Current FCD 空白資料 1584 + 16 = 1600 應出現在 Date_Loading / Weekly_Loading / Monthly_Loading 的「未排日期」欄位。
- 同筆資料仍應保留在 Risk_List。
- 綠色已出貨列仍依使用者勾選規則處理；預設不進主 Loading。
- Model 欄位刪除線資料仍一律排除。
- Monthly_Loading / Weekly_Loading / Date_Loading 的 Loading 總數量需包含未排日期。
- Validation_Log 需 PASS。
- GitHub Artifact 不再包含 PPIP_Reporter_CLI.exe。

## 驗證結果
已用使用者提供的 Forecast_Backlog_20260618.zip 進行測試。
- 程式語法檢查：PASS
- 報表產生：PASS
- DPU-4672xs-DZSG-P1 (756016-023) 未排日期數量：1600
- Validation_Log：PASS
