@echo off
chcp 65001 >nul
echo 正在启动衣物识别系统...

REM 检查是否已安装Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到Python，请安装Python后再运行此脚本。
    pause
    exit /b
)

REM 检查是否已安装依赖
echo 正在检查依赖项...
pip install -r requirements.txt

REM 启动应用
echo 正在启动应用，请稍候...
python app.py

pause 