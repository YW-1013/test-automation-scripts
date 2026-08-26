# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['MegaBook_Server_V2.2_260708.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\py311\\Lib\\site-packages\\uiautomator2\\assets\\u2.jar', 'uiautomator2/assets'),('D:\\py311\\Lib\\site-packages\\uiautomator2\\assets\\app-uiautomator.apk', 'uiautomator2/assets'),('D:\\测试脚本\\audio_test\\megabook\\server\\ffmpeg.exe', '.'),('D:\\测试脚本\\audio_test\\megabook\\server\\refresh.png', '.'),('D:\\测试脚本\\audio_test\\megabook\\server\\test.wav', '.'),('D:\\测试脚本\\audio_test\\megabook\\server\\adb', 'adb')],
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
    name='MegaBook_Server_V2.2_260708',
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
