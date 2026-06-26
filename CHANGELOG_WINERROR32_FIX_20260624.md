# PPIP WinError 32 修正版說明 - 2026/06/24

## 修正問題

執行 `Preflight Check / Generate Report` 時，程式讀完 ZIP 內 Excel 後，可能在清除 Windows Temp 暫存檔時失敗：

```text
PermissionError: [WinError 32] 程序無法存取檔案，因為檔案正由另一個程序使用
```

## 原因

原程式使用 `tempfile.TemporaryDirectory()`，在離開暫存資料夾時會立即刪除解壓後的 Excel 檔案。若 pandas / openpyxl / Windows 防毒或索引服務仍暫時占用檔案，會造成整個報表產生失敗。

## 修改內容

修改檔案：

```text
collectors/backlog_reader.py
```

主要調整：

1. 使用 `with pd.ExcelFile(path) as xls:` 強制關閉 Excel workbook handle。
2. `pd.read_excel()` 改為讀取同一個 `ExcelFile` 物件，避免重複開啟檔案 handle。
3. 移除 `TemporaryDirectory()` 自動清除方式，改用 `mkdtemp()` + 自訂安全清除。
4. 新增 `_safe_rmtree()`：暫存檔刪除失敗時會 retry，不再讓產報流程直接失敗。
5. 加入 `gc.collect()`，協助釋放 pandas / openpyxl 暫存物件。
6. 過濾 `__MACOSX` 與 `~$` 暫存 Excel 檔案。

## 使用方式

將本 ZIP 整包上傳到 GitHub repository 根目錄，重新執行 GitHub Actions build，即可產生新版 EXE。

