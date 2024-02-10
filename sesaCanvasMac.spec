# -*- mode: python ; coding: utf-8 -*-
import os 
from PyInstaller.utils.hooks import collect_data_files
# Get a list of all files in the thermosteam directory
# thermosteam_dir = "/opt/homebrew/lib/python3.10/site-packages/thermosteam"
# Get a list of all files in the thermosteam directory
# thermosteam_files = []
# for dirpath, dirnames, filenames in os.walk(thermosteam_dir):
#     for f in filenames:
#         thermosteam_files.append((os.path.join(dirpath, f), os.path.relpath(dirpath, thermosteam_dir)))

a = Analysis(
    ['src/__main__.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('thermosteam')+collect_data_files('thermo')+collect_data_files('chemicals'),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='sesaCanvas',
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
    icon=['logo.ico'],
)
app = BUNDLE(
    exe,
    name='sesaCanvas.app',
    icon='logo.ico',
    bundle_identifier=None,
)
