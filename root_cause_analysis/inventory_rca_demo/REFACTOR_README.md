# 重构说明文档

## 📋 重构概述

根据 `refactor.md` 的要求，对 `inventory_rca_demo` 进行了全面重构，主要变更如下：

## 🎯 主要变更

### 1. 页面结构简化

**重构前**：
- 场景介绍
- 因果图
- 数据探索
- 因果分析
- 大模型解释

**重构后**：
- 场景介绍
- 根因分析（包含8步流程）

### 2. 新增功能

#### 2.1 本体图API (`ontology_api.py`)

提供本体图的JSON数据，展示产品与部件的关系：

```python
from ontology_api import OntologyAPI

# 获取本体图数据
ontology_data = OntologyAPI.get_ontology_data()

# 获取可视化数据
graph_data = OntologyAPI.get_ontology_graph_data()

# 获取文本描述
text = OntologyAPI.get_ontology_text()
```

**本体关系**：
- 产品A 使用 部件A
- 产品B 使用 部件A1
- 规则：部件A和部件A1是相同型号，可以通用

#### 2.2 LLM解释器增强 (`llm_explainer.py`)

新增两个方法，支持不同的prompt：

1. **`generate_root_cause_explanation()`** - 生成根因解释（6.2步骤）
   - 专注于解释根因是什么
   - 用数据支撑结论
   - 解释因果机制

2. **`generate_solution()`** - 生成解决方案（6.3步骤）
   - 给出具体的改进措施
   - 说明实施步骤
   - 评估预期效果
   - 提出风险提示

### 3. 根因分析页面8步流程

#### 步骤1：What do the users need to do?
- 展示用户需要进行根因分析的目标

#### 步骤2：Where does the needed data come from?
- 展示数据来源（数据库或模拟数据）
- 显示数据样本和统计信息

#### 步骤3：How are users meant to interact with the data?
- 本次不演示
- 说明实际应用中的交互方式

#### 步骤4：What structured data asset needs to be provided to users?
- 展示本体图可视化
- 显示产品与部件的关系
- 展示本体规则

#### 步骤5：What constrain should applied to control the data quality?
- 展示数据质量约束
- 部件通用规则

#### 步骤6：How should the data asset be leveraged?
这是核心步骤，包含3个子步骤：

**6.1 发生了什么？**
- 展示库存趋势图
- 对比实际库存与反事实库存
- 得出结论：库存高位问题

**6.2 为什么会发生？**
- 展示因果图
- 运行因果分析
- 使用LLM生成根因解释

**6.3 如何解决？**
- 使用LLM生成解决方案
- 基于反事实分析结果

#### 步骤7：Describe any automations necessary for users to fulfill their tasks?
- 本次不演示
- 说明实际应用中的自动化措施

#### 步骤8：Define roles and permissions?
- 本次不演示
- 说明实际应用中的角色和权限

## 📁 文件变更

### 新增文件

1. **`ontology_api.py`** - 本体图API
2. **`app_refactored.py`** - 重构后的Web应用
3. **`test_refactored.py`** - 测试脚本

### 修改文件

1. **`llm_explainer.py`** - 新增两个方法：
   - `generate_root_cause_explanation()`
   - `generate_solution()`
   - `_build_root_cause_prompt()`
   - `_build_solution_prompt()`

## 🚀 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置大模型API（可选）

编辑 `modelkey.cfg` 文件：

```
API Key: your_api_key_here
Base URL: https://api.siliconflow.cn/v1
Model: Qwen/Qwen2.5-7B-Instruct
```

### 3. 运行应用

```bash
# 运行重构后的应用
streamlit run app_refactored.py

# 或运行原应用
streamlit run app.py
```

### 4. 访问应用

在浏览器中打开：http://localhost:8501

## ✅ 测试结果

运行 `test_refactored.py` 测试脚本：

```bash
python test_refactored.py
```

**测试结果**：
- ✅ 本体图API正常工作
- ✅ 数据生成正常
- ✅ 因果分析正常
- ✅ LLM解释器支持两种prompt
- ✅ 根因解释prompt构建成功
- ✅ 解决方案prompt构建成功

## 📊 数据说明

### 当前数据满足需求

根据 `refactor.md` 的要求，当前数据已经满足需求：

1. **产品A销量下降**：11月开始下降40%
2. **产品B未使用部件A**：历史全为0
3. **部件A库存高**：持续升高
4. **反事实数据**：产品B使用部件A的场景

### 数据字段

- `date` - 日期
- `product_a_sales` - 产品A销量
- `product_b_sales` - 产品B销量
- `product_b_uses_component_a` - 产品B是否使用部件A
- `component_a_consumption` - 部件A消耗量
- `component_a_inventory` - 部件A库存
- `component_a_procurement` - 部件A采购量
- `is_decline_period` - 是否为销量下降期

## 🎨 页面效果

### 场景介绍页面

- 展示场景背景
- 核心目标
- 因果关系
- 问题描述
- 分析目标

### 根因分析页面

- 8步流程展示
- 每步都有明确的标题和内容
- 步骤6包含3个子步骤
- 使用大模型生成根因解释和解决方案

## 💡 关键特性

1. **流程化展示**：按照8步流程展示完整的根因分析过程
2. **本体图可视化**：展示产品与部件的关系
3. **因果图展示**：展示变量之间的因果关系
4. **库存趋势对比**：对比实际库存与反事实库存
5. **智能解释**：使用大模型生成根因解释和解决方案
6. **交互式操作**：用户可以运行分析、生成解释

## 📝 注意事项

1. **大模型API**：需要配置API密钥才能使用大模型功能
2. **DoWhy依赖**：因果分析需要安装DoWhy库
3. **数据质量**：当前使用模拟数据，实际应用需要真实数据
4. **性能优化**：大数据量时可能需要优化

## 🔄 后续改进

1. 增加步骤3和步骤7、8的具体内容
2. 优化可视化效果
3. 增加更多交互功能
4. 支持更多数据源
5. 增加报告导出功能

## 📚 相关文档

- [README.md](README.md) - 项目说明
- [QUICKSTART.md](QUICKSTART.md) - 快速启动指南
- [设计文档.md](设计文档.md) - 设计文档
- [refactor.md](refactor.md) - 重构需求文档
