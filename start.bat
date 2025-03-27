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
if exist venv (
    echo 删除旧的虚拟环境...
    rmdir /s /q venv
)

echo 创建新的虚拟环境...
python -m venv venv
call venv\Scripts\activate

echo 升级基础包...
python -m pip install --upgrade pip setuptools wheel

echo 安装依赖...
pip install numpy==1.24.3
pip install tensorflow
pip install pillow
pip install Flask==2.0.1
pip install werkzeug==2.0.2
pip install SQLAlchemy==1.4.46
pip install Flask-SQLAlchemy==2.5.1

REM 创建上传目录
if not exist static\uploads (
    mkdir static\uploads
)

REM 启动应用
echo 启动应用，请稍候...
echo 系统启动成功！请在浏览器中访问 http://localhost:5000
python app.py

pause 