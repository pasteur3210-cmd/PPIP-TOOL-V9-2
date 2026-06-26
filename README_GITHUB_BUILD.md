# GitHub Actions 組譯說明

## 上傳到 GitHub 的內容

請將本資料夾內所有檔案與資料夾上傳到 GitHub Repository 根目錄。

必要檔案：
- app.py
- main.py
- streamlit_launcher.py
- requirements.txt
- PPIP_Reporter.spec
- PPIP_Reporter_CLI.spec
- .github/workflows/build.yml
- collectors/
- core/
- reports/
- utils/
- config/
- logs/
- outputs/
- validation/
- tests/

## GitHub 編譯方式

1. 進入 GitHub Repository
2. 點選 Actions
3. 選擇 Build PPIP Reporter EXE
4. 點選 Run workflow
5. 編譯完成後下載 Artifacts：PPIP_Production_Planning_Reporter_EXE

## 產出檔案

- PPIP_Production_Planning_Reporter.exe  
  Streamlit Web UI 啟動版。執行後會開啟本機 Web UI。

- PPIP_Reporter_CLI.exe  
  CLI 命令列版本。

## CLI 使用範例

```bat
PPIP_Reporter_CLI.exe Production_Schedule.zip --as-of-date 2026-06-24 --output-dir outputs --log-dir logs --validation-dir validation
```

## 注意事項

Streamlit 打包成 EXE 時第一次啟動會較慢，且仍會以瀏覽器方式開啟 UI。
如果要改成真正 Windows GUI，需要另外改寫成 Tkinter / CustomTkinter 版本。

## V9 Build Note
本版已移除 CLI 編譯步驟。GitHub Actions Artifact 只會包含：
- PPIP_Production_Planning_Reporter.exe
- README.md
- README_GITHUB_BUILD.md
