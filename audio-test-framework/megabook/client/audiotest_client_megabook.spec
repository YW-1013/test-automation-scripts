# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['MegaBook_Client_V2.2_260708.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\测试脚本\\audio_test\\megabook\\client\\test.wav', '.'),('D:\\测试脚本\\audio_test\\megabook\\client\\PowerTool.exe', '.')],
    hiddenimports=['websocket'],
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
    name='MegaBook_Client_V2.2_260708',
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
)
