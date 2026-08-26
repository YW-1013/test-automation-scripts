@echo off

set "script_name=main.py"
set "output_file=output.txt"
set "script_dir=%~dp0"

REM 切换到脚本所在的目录
cd /d "%script_dir%"

REM 以管理员权限运行Python脚本并将输出保存到txt文件中
powershell -Command "Start-Process python -ArgumentList '%script_name% > %output_file%' -WorkingDirectory '%script_dir%' -Verb RunAs; exit $LASTEXITCODE"

REM 检查执行结果并显示相应的消息
if %ERRORLEVEL% equ 0 (
    echo Success: Output written to %output_file%
) else (
    echo Error: Failed to run script %script_name%
)