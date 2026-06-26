@echo off
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m compileall .
pyinstaller --clean --noconfirm PPIP_Reporter.spec
pyinstaller --clean --noconfirm PPIP_Reporter_CLI.spec
pause
