# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

datas = [
    ('app.py', '.'),
    ('main.py', '.'),
    ('config', 'config'),
    ('collectors', 'collectors'),
    ('core', 'core'),
    ('reports', 'reports'),
    ('utils', 'utils'),
]

hiddenimports = []
for package_name in ['streamlit', 'pandas', 'openpyxl', 'yaml', 'dateutil']:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package_name)
        datas += pkg_datas
        hiddenimports += pkg_hiddenimports
    except Exception:
        pass

try:
    hiddenimports += collect_submodules('streamlit')
except Exception:
    pass

for package_name in ['streamlit', 'pandas', 'openpyxl', 'pyarrow', 'altair', 'numpy']:
    try:
        datas += copy_metadata(package_name)
    except Exception:
        pass

a = Analysis(
    ['streamlit_launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PPIP_Production_Planning_Reporter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
