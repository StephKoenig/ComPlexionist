# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\complexionist\\cli.py'],
    pathex=[],
    binaries=[],
    datas=[('d:\\Dev\\ComPlexionist\\.venv\\Lib\\site-packages\\flet/controls', 'flet/controls')],
    hiddenimports=[],
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
    name='complexionist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\Steph\\AppData\\Local\\Temp\\92565f0e-3f6d-426c-9a29-c20da1f2022f',
    icon=['icon.ico'],
)
