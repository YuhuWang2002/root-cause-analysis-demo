# 电商利润根因分析系统

基于DoWhy GCM (Graphical Causal Models) 框架实现的根因分析系统，参考AWS文章中的电商利润分析场景。

## 📋 场景说明

**问题背景**：
- 在线商店销售智能手机，零售价$999
- 2021年利润保持稳定
- 2022年初利润突然下降
- 需要找出利润下降的根本原因

**因果因素**：
- `shopping_event`: 购物活动标识（黑色星期五、网络星期一等）
- `ad_spend`: 广告支出
- `page_views`: 页面浏览量
- `unit_price`: 单价（可能有折扣）
- `sold_units`: 销售数量
- `revenue`: 收入
- `operational_cost`: 运营成本
- `profit`: 利润

## 🚀 快速开始

### 安装依赖

```bash
pip install dowhy pandas numpy plotly streamlit networkx matplotlib openai httpx
```

### 运行Web应用

```bash
cd rca_demo
streamlit run rca_app.py
```

### 使用Python API

```python
from rca_analyzer import RootCauseAnalyzer
from rca_data_generator import create_demo_scenario
import pandas as pd

# 生成演示数据
data, anomaly_factors, causal_graph = create_demo_scenario()

# 创建根因分析器
analyzer = RootCauseAnalyzer(data)

# 构建因果图
analyzer.build_causal_graph_from_dot(causal_graph)

# 创建结构因果模型
analyzer.create_structural_causal_model()

# 自动分配因果机制
analyzer.auto_assign_causal_mechanisms()

# 拟合模型
analyzer.fit_model()

# 分析根本原因
results = analyzer.analyze_root_causes('profit', top_k=10)
print(results)

# 反事实分析
what_if_results = analyzer.what_if_analysis(
    intervention_dict={'ad_spend': lambda x: x * 1.5},  # 增加50%广告支出
    outcome='profit',
    num_samples=1000
)
print(what_if_results.mean())
```

## 📊 功能特性

### 1. 结构因果模型 (SCM)
- 基于DoWhy GCM构建结构因果模型
- 支持从DOT格式或边列表构建因果图
- 自动分配因果机制（连续变量使用ANM，离散变量使用分类模型）

### 2. 根因分析
- **箭头强度分析**：识别关键因果路径
- **直接因果影响**：评估每个父节点对目标节点的直接影响
- **内在因果影响**：评估每个节点对目标节点的内在贡献

### 3. 反事实分析
- **What-if分析**：模拟干预后的结果分布
- **反事实样本**：计算干预后的具体结果变化

### 4. 分布变化归因
- 分析异常数据与正常数据之间的分布变化
- 归因到各个父节点

### 5. 大模型智能解释 🤖
- **自动解释根因分析结果**：使用LLM生成易于理解的业务洞察
- **改进建议生成**：基于分析结果提出具体的改进措施
- **自定义问答**：支持用户提问，获得专业解答
- **支持多种开源模型**：通过SiliconFlow API访问Qwen、Llama等模型

## 📁 文件结构

```
rca_demo/
├── rca_analyzer.py          # 核心根因分析模块
├── rca_data_generator.py    # 演示数据生成器
├── rca_llm_explainer.py     # 大模型解释模块
├── rca_app.py               # Web演示界面
├── test_rca.py              # 根因分析测试脚本
├── test_llm.py              # LLM功能测试脚本
├── check_code.py            # 代码质量检查脚本
├── run_demo.py              # 快速启动脚本
├── README.md                # 使用说明
├── QUICKSTART.md            # 快速上手指南
└── prompts/                 # 提示词保存目录
```

## 🔬 核心API

### RootCauseAnalyzer

#### 初始化
```python
analyzer = RootCauseAnalyzer(data: pd.DataFrame)
```

#### 构建因果图
```python
# 从边列表构建
analyzer.build_causal_graph_from_edges(edges: List[Tuple[str, str]])

# 从DOT字符串构建
analyzer.build_causal_graph_from_dot(dot_string: str)
```

#### 创建和拟合模型
```python
# 创建结构因果模型
analyzer.create_structural_causal_model()

# 自动分配因果机制
analyzer.auto_assign_causal_mechanisms()

# 拟合模型
analyzer.fit_model()
```

#### 分析方法
```python
# 根因分析
results = analyzer.analyze_root_causes(outcome: str, top_k: int = 10)

# 计算箭头强度
strengths = analyzer.compute_arrow_strength(target_node: str)

# What-if分析
what_if = analyzer.what_if_analysis(
    intervention_dict: Dict[str, float],
    outcome: str,
    num_samples: int = 1000
)

# 反事实分析
counterfactual = analyzer.counterfactual_analysis(
    intervention_dict: Dict[str, float],
    outcome: str
)

# 分布变化归因
attribution = analyzer.get_distribution_change_attribution(
    target_node: str,
    anomaly_data: pd.DataFrame
)
```

### LLMExplainer

#### 初始化
```python
from rca_llm_explainer import LLMExplainer

# 创建解释器（需要API密钥）
explainer = LLMExplainer(
    api_key="your-siliconflow-api-key",
    model="Qwen/Qwen2.5-7B-Instruct",
    base_url="https://api.siliconflow.cn/v1"
)
```

#### 解释方法
```python
# 生成根因分析解释
explanation = explainer.generate_explanation(
    analysis_results=results_df,
    comparison_df=comparison_df,
    causal_graph=causal_graph,
    scenario_background="场景描述"
)

# 生成改进建议
suggestions = explainer.generate_improvement_suggestions(
    analysis_results=results_df,
    causal_graph=causal_graph,
    scenario_description="场景描述",
    problem_description="问题描述"
)
```

## 📈 分析结果示例

### 根因分析结果

| 排名 | 原因变量 | 目标变量 | 影响强度 | 绝对强度 |
|------|----------|----------|----------|----------|
| 1 | ad_spend | profit | -0.45 | 0.45 |
| 2 | unit_price | profit | -0.38 | 0.38 |
| 3 | page_views | profit | 0.32 | 0.32 |

### 反事实分析结果

**干预措施**：广告支出增加50%

**结果**：
- 当前平均利润：$12,345
- 干预后平均利润：$15,678
- 利润变化：+27.0%

## 🎯 应用场景

1. **电商利润分析**：识别影响利润的关键因素
2. **营销效果评估**：分析广告支出对销售的影响
3. **价格策略优化**：评估价格变化对利润的影响
4. **异常诊断**：识别业务指标异常的根本原因

## 📚 参考资料

- [AWS Blog: Root Cause Analysis with DoWhy](https://aws.amazon.com/cn/blogs/opensource/root-cause-analysis-with-dowhy-an-open-source-python-library-for-causal-machine-learning/)
- [DoWhy Documentation](https://py-why.github.io/dowhy/)
- [DoWhy GCM Tutorial](https://py-why.github.io/dowhy/example_notebooks/dowhy-gcm.html)

## ⚠️ 注意事项

1. **数据质量**：确保数据质量良好，缺失值已处理
2. **因果图**：因果图应该基于领域知识构建，错误的因果图会导致错误的分析结果
3. **模型拟合**：需要足够的数据量来拟合因果机制
4. **解释结果**：结合业务背景解释分析结果
5. **LLM配置**：
   - 需要配置SiliconFlow API密钥才能使用AI解释功能
   - 建议使用Qwen2.5-7B-Instruct或更强大的模型
   - API调用会产生费用，请注意控制成本
   - 提示词会自动保存到prompts目录，便于调试和优化

## 📝 License

MIT License
