# 快速启动指南

## 1. 环境准备

### 安装依赖
```bash
cd /Users/yuhuwang/Documents/trae_projects/root_cause_analysis/inventory_rca_demo
pip install -r requirements.txt
```

### 配置大模型API（可选）
编辑 `modelkey.cfg` 文件，填入您的API密钥：
```
API Key: your_actual_api_key_here
Base URL: https://api.siliconflow.cn/v1
Model: Qwen/Qwen2.5-7B-Instruct
```

## 2. 启动应用

### 方式1：使用启动脚本
```bash
# Linux/Mac
chmod +x run_demo.sh
./run_demo.sh

# Windows
run_demo.bat
```

### 方式2：直接运行
```bash
streamlit run app.py
```

## 3. 访问应用

在浏览器中打开：**http://localhost:8501**

## 4. 使用流程

1. **场景介绍** → 点击"开始分析"生成数据
2. **因果图** → 查看变量关系
3. **数据探索** → 分析库存和销量趋势
4. **因果分析** → 点击"运行因果分析"查看结果
5. **大模型解释** → 生成智能报告（需配置API）

## 5. 预期结果

### 因果分析结果
- **因果效应值**: 约0.0000（产品B使用部件A对库存的影响）
- **库存降低**: 约151.56（98.59%）
- **是否为根因**: ✅ 是

### 驳斥检验
- **安慰剂检验**: 通过（新效应值接近0）
- **随机共同原因检验**: 稳健
- **数据子集检验**: 稳健

### 反事实分析
- **实际库存均值**: 约153.73
- **反事实库存均值**: 约2.17
- **销量下降期库存降低**: 显著

## 6. 常见问题

### Q1: 如何修改数据参数？
A: 编辑 `data_generator.py` 中的参数：
- `product_a_decline_rate`: 产品A销量下降比例
- `product_a_sales_decline_start`: 销量下降开始日期

### Q2: 如何更换大模型？
A: 修改 `modelkey.cfg` 中的 `Model` 参数，支持任何OpenAI兼容的API

### Q3: 如何导出分析结果？
A: 在"大模型解释"页面点击"下载报告"按钮

## 7. 项目文件说明

```
inventory_rca_demo/
├── data_generator.py      # 数据生成（可修改参数）
├── causal_analyzer.py     # 因果分析（核心算法）
├── llm_explainer.py       # 大模型解释
├── app.py                 # Web应用主程序
├── requirements.txt       # 依赖包
├── run_demo.sh/.bat       # 启动脚本
├── modelkey.cfg           # API配置
└── README.md              # 详细文档
```

## 8. 技术支持

如遇问题，请检查：
1. Python版本 >= 3.8
2. 依赖包是否正确安装
3. API密钥是否有效（如使用大模型功能）

---

**祝您使用愉快！** 🎉
