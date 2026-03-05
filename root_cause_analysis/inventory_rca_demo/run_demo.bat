@echo off
REM 部件A库存高因果根因分析 - Windows启动脚本

echo =========================================
echo 部件A库存高因果根因分析系统
echo =========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo Python版本:
python --version
echo.

REM 检查依赖包
echo 检查依赖包...
pip install -r requirements.txt
echo.

REM 创建必要的目录
if not exist "prompts" (
    mkdir prompts
    echo 创建prompts目录
)

REM 启动Web应用
echo 启动Web应用...
echo 请在浏览器中访问: http://localhost:8501
echo.
echo 按Ctrl+C停止应用
echo.

streamlit run app.py

pause
