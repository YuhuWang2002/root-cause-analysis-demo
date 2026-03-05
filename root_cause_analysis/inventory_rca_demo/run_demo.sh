#!/bin/bash

# 部件A库存高因果根因分析 - 启动脚本

echo "========================================="
echo "部件A库存高因果根因分析系统"
echo "========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null
then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

echo "Python版本:"
python3 --version
echo ""

# 检查依赖包
echo "检查依赖包..."
pip3 install -r requirements.txt
echo ""

# 创建必要的目录
if [ ! -d "prompts" ]; then
    mkdir prompts
    echo "创建prompts目录"
fi

# 启动Web应用
echo "启动Web应用..."
echo "请在浏览器中访问: http://localhost:8501"
echo ""
echo "按Ctrl+C停止应用"
echo ""

streamlit run app.py
