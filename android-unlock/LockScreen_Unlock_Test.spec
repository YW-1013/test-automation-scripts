# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# 将 customtkinter 的主题、图标等资源文件一起打进 exe
ctk_datas = collect_data_files('customtkinter')
# 将 uiautomator2 的 assets/u2.jar 等资源文件一起打进 exe
u2_datas  = collect_data_files('uiautomator2')

a = Analysis(
    ['LockScreen_Unlock_Test.py'],
    pathex=[],
    binaries=[],
    datas=ctk_datas + u2_datas,
    hiddenimports=['customtkinter', 'uiautomator2'],
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
    a.binaries,   # 单文件模式：binaries 直接传给 EXE
    a.datas,      # 单文件模式：datas   直接传给 EXE
    exclude_binaries=False,   # False = 单文件（onefile）
    name='LockScreen_Unlock_Test',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,            # False = 无 cmd 黑窗
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
# 单文件模式不需要 COLLECT()，已删除
