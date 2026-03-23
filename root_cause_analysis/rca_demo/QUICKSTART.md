# 快速开始指南

## 🚀 5分钟快速上手

### 1. 安装依赖

```bash
pip install dowhy pandas numpy plotly streamlit networkx matplotlib
```

### 2. 运行测试

```bash
cd rca_demo
python test_rca.py
```

### 3. 启动Web演示

```bash
streamlit run rca_app.py
```

或者使用启动脚本：

```bash
python run_demo.py
```

## 📊 使用流程

### 方法1: 使用Web界面

1. **场景介绍** - 了解电商利润分析场景
2. **数据探索** - 查看数据趋势和统计信息
3. **因果图** - 可视化因果关系
4. **根因分析** - 运行DoWhy GCM分析
5. **反事实分析** - 模拟干预措施

### 方法2: 使用Python API

```python
from rca_analyzer import RootCauseAnalyzer
from rca_data_generator import create_demo_scenario

# 1. 准备数据
data, anomaly_factors, causal_graph = create_demo_scenario()

# 2. 创建分析器
analyzer = RootCauseAnalyzer(data)

# 3. 构建因果图
analyzer.build_causal_graph_from_dot(causal_graph)

# 4. 创建结构因果模型
analyzer.create_structural_causal_model()

# 5. 自动分配因果机制
analyzer.auto_assign_causal_mechanisms()

# 6. 拟合模型
analyzer.fit_model()

# 7. 分析根本原因
results = analyzer.analyze_root_causes('profit')
print(results)

# 8. 反事实分析
what_if = analyzer.what_if_analysis(
    intervention_dict={'ad_spend': lambda x: x * 1.5},
    outcome='profit'
)
print(f"干预后平均利润: ${what_if['profit'].mean():,.2f}")
```

## 🎯 核心功能

### 1. 根因分析
- **箭头强度分析**: 识别关键因果路径
- **直接因果影响**: 评估父节点对目标节点的直接影响
- **内在因果影响**: 评估节点的内在因果贡献

### 2. 反事实分析
- **What-if分析**: 模拟干预后的结果分布
- **反事实样本**: 计算干预后的具体结果变化

### 3. 分布变化归因
- 分析异常数据与正常数据的分布差异
- 归因到各个父节点

## 📈 分析结果示例

### 根因分析结果

```
           cause target     strength  abs_strength  rank
         revenue profit 1.605269e+11  1.605269e+11     1
operational_cost profit 6.158206e+10  6.158206e+10     2
```

### 箭头强度

```
revenue -> profit: 158,246,333,922.60
operational_cost -> profit: 64,700,029,505.39
```

## 🔧 高级用法

### 自定义因果图

```python
# 从边列表构建
edges = [
    ('shopping_event', 'ad_spend'),
    ('ad_spend', 'page_views'),
    ('page_views', 'sold_units'),
    ('sold_units', 'revenue'),
    ('revenue', 'profit')
]

analyzer.build_causal_graph_from_edges(edges)
```

### 分布变化归因

```python
# 对比正常时期和异常时期
normal_data = data[~data['is_anomaly_period']]
anomaly_data = data[data['is_anomaly_period']]

# 重新拟合模型（使用正常数据）
analyzer = RootCauseAnalyzer(normal_data)
# ... 拟合模型 ...

# 分析分布变化
attribution = analyzer.get_distribution_change_attribution(
    target_node='profit',
    anomaly_data=anomaly_data
)
print(attribution)
```

## ⚠️ 注意事项

1. **数据质量**: 确保数据质量良好，处理缺失值
2. **因果图**: 因果图应基于领域知识构建
3. **样本量**: 需要足够的数据量拟合模型
4. **解释结果**: 结合业务背景解释分析结果

## 📚 参考资料

- [AWS Blog: Root Cause Analysis with DoWhy](https://aws.amazon.com/cn/blogs/opensource/root-cause-analysis-with-dowhy-an-open-source-python-library-for-causal-machine-learning/)
- [DoWhy Documentation](https://py-why.github.io/dowhy/)
- [DoWhy GCM Tutorial](https://py-why.github.io/dowhy/example_notebooks/dowhy-gcm.html)

## 🐛 常见问题

### Q: 为什么根节点需要特殊处理？
A: 根节点没有父节点，需要使用随机模型（如EmpiricalDistribution）而不是条件模型。

### Q: 如何选择因果机制？
A: 系统会自动选择：
- 根节点：EmpiricalDistribution 或 ScipyDistribution
- 连续变量：AdditiveNoiseModel (ANM)
- 离散变量：ClassifierFCM

### Q: 分析结果如何解释？
A: 箭头强度表示该因果边对目标变量变化的贡献程度。强度越大，影响越显著。

## 📧 反馈与支持

如有问题或建议，请提交Issue或Pull Request。
