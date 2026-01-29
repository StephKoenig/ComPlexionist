# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for ComPlexionist with Flet GUI

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect Flet data files and submodules
flet_datas = collect_data_files('flet')
flet_desktop_datas = collect_data_files('flet_desktop', include_py_files=True)
flet_hidden = collect_submodules('flet')

# Hidden imports for our dependencies
hidden_imports = [
    'plexapi',
    'plexapi.server',
    'plexapi.library',
    'plexapi.video',
    'plexapi.exceptions',
    'httpx',
    'httpx._transports.default',
    'pydantic',
    'pydantic.deprecated.decorator',
    'pydantic_core',
    'click',
    'rich',
    'rich.console',
    'rich.table',
    'rich.progress',
    'rich.panel',
    'rich.text',
    'rich.prompt',
    'dotenv',
    'yaml',
    'configparser',
    # Flet-specific
    'flet',
    'flet_desktop',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
    # asyncio for Flet
    'asyncio',
    'concurrent.futures',
] + flet_hidden

a = Analysis(
    ['src\\complexionist\\cli.py'],
    pathex=['src'],
    binaries=[],
    datas=flet_datas + flet_desktop_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, cipher=block_cipher)

# Single-file executable
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
    console=True,  # Keep console for CLI mode; GUI will still work
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: icon='icon.ico'
)
