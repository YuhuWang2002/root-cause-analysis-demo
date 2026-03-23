# LLM解释功能使用指南

## 🤖 功能介绍

大模型解释功能使用SiliconFlow API，通过开源大语言模型（如Qwen、Llama等）对根因分析结果进行智能解释，生成易于理解的业务洞察和改进建议。

## 📋 前置要求

### 1. 获取API密钥

访问 [SiliconFlow](https://cloud.siliconflow.cn/) 注册账号并获取API密钥。

### 2. 安装依赖

```bash
pip install openai httpx
```

## 🚀 快速开始

### 方法1: Web界面使用

1. **启动Web应用**
   ```bash
   cd rca_demo
   streamlit run rca_app.py
   ```

2. **配置LLM API**
   - 在侧边栏找到"大模型配置"
   - 输入您的SiliconFlow API密钥
   - 点击"初始化LLM解释器"

3. **使用AI解释**
   - 完成"根因分析"页面的分析
   - 进入"AI解释"页面
   - 选择解释类型并生成解释

### 方法2: Python代码使用

```python
from rca_analyzer import RootCauseAnalyzer
from rca_data_generator import create_demo_scenario
from rca_llm_explainer import LLMExplainer
import pandas as pd

# 1. 准备数据和分析
data, anomaly_factors, causal_graph = create_demo_scenario()

analyzer = RootCauseAnalyzer(data)
analyzer.build_causal_graph_from_dot(causal_graph)
analyzer.create_structural_causal_model()
analyzer.auto_assign_causal_mechanisms()
analyzer.fit_model()

results = analyzer.analyze_root_causes('profit')

# 2. 创建LLM解释器
explainer = LLMExplainer(
    api_key="your-api-key",
    model="Qwen/Qwen2.5-7B-Instruct"
)

# 3. 生成解释
comparison_df = pd.DataFrame({
    'variable': ['profit', 'revenue'],
    'normal_mean': [10000, 50000],
    'anomaly_mean': [8000, 45000],
    'change_percent': [-20, -10]
})

explanation = explainer.generate_explanation(
    analysis_results=results,
    comparison_df=comparison_df,
    causal_graph=causal_graph
)

print(explanation)
```

## 📊 功能详解

### 1. 根因分析解释

自动解释根因分析结果，包括：
- 利润变化分析
- 主要异常指标识别
- 根本原因分析
- 因果路径解释
- 改进建议

**示例输出**：
```
## 根因分析

根据因果图结构和根因分析结果，导致利润下降的根本原因主要包括：

1. **广告支出减少**（影响强度：1.6e+11）
   - 广告支出减少导致页面浏览量下降
   - 页面浏览量下降直接影响销售数量
   - 销售数量减少导致收入下降
   - 最终影响利润

2. **单价上涨**（影响强度：6.2e+10）
   - 单价上涨直接降低消费者购买意愿
   - 转化率下降导致销售数量减少
   - 进而影响收入和利润

## 改进建议

1. **恢复广告投放**：将广告支出恢复到正常水平
2. **优化定价策略**：考虑促销活动或折扣
3. **提升转化率**：优化产品页面和用户体验
```

### 2. 改进建议生成

基于根因分析结果，生成具体的改进措施：
- 按优先级排序的改进建议
- 实施路径（短期、中期、长期）
- 风险评估和规避策略
- 效果评估指标

### 3. 自定义问答

支持用户提问，获得专业解答：
- "为什么广告支出减少会导致利润下降？"
- "如何优化定价策略？"
- "改进措施的预期效果如何？"

## 🔧 高级配置

### 支持的模型

通过SiliconFlow API，支持多种开源模型：

```python
# Qwen系列
model="Qwen/Qwen2.5-7B-Instruct"      # 推荐
model="Qwen/Qwen2.5-14B-Instruct"     # 更强大
model="Qwen/Qwen2.5-72B-Instruct"     # 最强大

# Llama系列
model="meta-llama/Llama-3.1-8B-Instruct"
model="meta-llama/Llama-3.1-70B-Instruct"

# 其他模型
model="THUDM/glm-4-9b-chat"
model="01-ai/Yi-1.5-9B-Chat"
```

### 自定义API端点

```python
explainer = LLMExplainer(
    api_key="your-api-key",
    model="your-model",
    base_url="https://your-api-endpoint"
)
```

### 调整生成参数

在`rca_llm_explainer.py`中修改：

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=messages,
    temperature=0.7,      # 创造性 (0-1)
    max_tokens=2000       # 最大生成长度
)
```

## 📁 提示词管理

所有提示词会自动保存到`prompts/`目录：

```
prompts/
├── prompt_20260304_013148.txt
├── prompt_20260304_013205.txt
└── ...
```

提示词文件包含：
- 生成时间
- 使用的模型
- 完整的提示词内容

这有助于：
- 调试和优化提示词
- 理解LLM的输入
- 改进生成效果

## 💡 最佳实践

### 1. 提示词优化

- 提供清晰的场景背景
- 包含完整的分析结果
- 明确要求输出格式
- 指定目标受众

### 2. 模型选择

- **Qwen2.5-7B**：性价比高，适合一般场景
- **Qwen2.5-14B**：更强大，适合复杂分析
- **Qwen2.5-72B**：最强大，适合专业场景

### 3. 成本控制

- 合理设置`max_tokens`
- 避免重复生成相同内容
- 使用缓存机制
- 选择合适的模型

### 4. 结果验证

- 结合业务知识验证解释
- 检查逻辑合理性
- 必要时进行人工审核

## 🐛 常见问题

### Q: API密钥无效怎么办？
A: 
1. 检查密钥是否正确复制
2. 确认账户余额充足
3. 验证API端点URL是否正确

### Q: 生成速度慢怎么办？
A: 
1. 使用较小的模型（如Qwen2.5-7B）
2. 减少`max_tokens`
3. 检查网络连接

### Q: 生成质量不满意怎么办？
A: 
1. 使用更强大的模型
2. 优化提示词
3. 调整`temperature`参数
4. 提供更多上下文信息

### Q: 如何查看提示词？
A: 查看`prompts/`目录下的文件，了解LLM的输入内容。

## 📚 参考资料

- [SiliconFlow文档](https://docs.siliconflow.cn/)
- [OpenAI API文档](https://platform.openai.com/docs)
- [Qwen模型介绍](https://github.com/QwenLM/Qwen)

## 📝 更新日志

### v1.0.0 (2026-03-04)
- ✅ 实现基础LLM解释功能
- ✅ 支持根因分析解释
- ✅ 支持改进建议生成
- ✅ 支持自定义问答
- ✅ 自动保存提示词
- ✅ Web界面集成

## 📧 反馈与支持

如有问题或建议，请提交Issue或Pull Request。
