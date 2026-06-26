# 20260624 Integrated Update Changelog

## 整合來源
- PPIP_Production_Planning_Reporter_Code_Skeleton_20260624.zip
- PPIP_Logging_Code_Skeleton_20260624.zip

## 本次整合重點
1. 新增 `utils/logger.py`：建立 runtime/error/data_quality/run_summary log。
2. 更新 `main.py`：全流程加入 run_id、RUN_START、RUN_END、try/except、CRITICAL traceback、run_summary。
3. 更新 `collectors/backlog_reader.py`：讀 ZIP/Excel 時記錄 UNZIP_SOURCE、LOAD_WORKBOOK、LOAD_SOURCE、錯誤 traceback。
4. 更新 `core/normalizer.py`：記錄數量轉換錯誤、TBD日期、Invalid Date、NORMALIZE_DONE。
5. 更新 `core/schedule_rules.py`：記錄 schedule rows 與 risk rows。
6. 更新 `core/loading_matrix.py`：記錄 BUILD_MATRIX 與 qty 總量。
7. 更新 `core/validator.py`：新增 validation_log_{run_id}.xlsx，驗證 Raw schedule qty = Monthly matrix qty。
8. 更新 `reports/dvt_report_writer.py`：記錄 EXPORT_START 與 EXPORT_SUCCESS。
9. 更新 `app.py`：UI 產報後可下載 Excel、validation log、runtime log、error log、data quality log、run summary。
10. 新增 `tests/smoke_test.py`：可驗證報表與全部 log 檔是否產出。

## V1 驗收結論
此整合版已將程式執行 log 與 error log 併入主產報流程，非獨立骨架。
