#!/usr/bin/env python
"""
根因分析演示启动脚本

快速启动Web演示界面
"""

import os
import sys

def main():
    """启动Web应用"""
    print("=" * 60)
    print("电商利润根因分析系统")
    print("=" * 60)
    print("\n正在启动Web演示界面...")
    print("\n访问地址: http://localhost:8501")
    print("\n按 Ctrl+C 停止服务\n")
    print("=" * 60)
    
    os.system("streamlit run rca_app.py")

if __name__ == "__main__":
    main()
