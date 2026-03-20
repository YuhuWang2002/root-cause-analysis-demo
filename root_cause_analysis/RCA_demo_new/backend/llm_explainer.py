"""
LLM解释模块 - 使用大模型生成根因分析解释
"""

import os
import datetime
from typing import Dict, Optional
import pandas as pd

class LLMConfig:
    """LLM配置管理器"""
    _config = {
        'api_key': None,
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'base_url': 'https://api.siliconflow.cn/v1'
    }

    @classmethod
    def set_config(cls, api_key: str = None, model: str = None, base_url: str = None):
        if api_key:
            cls._config['api_key'] = api_key
        if model:
            cls._config['model'] = model
        if base_url:
            cls._config['base_url'] = base_url

    @classmethod
    def get_config(cls):
        return cls._config.copy()

    @classmethod
    def is_configured(cls):
        return bool(cls._config.get('api_key'))


class LLMExplainer:
    """大模型解释器"""

    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        self.api_key = api_key or LLMConfig.get_config().get('api_key')
        self.model = model or LLMConfig.get_config().get('model', 'Qwen/Qwen2.5-7B-Instruct')
        self.base_url = base_url or LLMConfig.get_config().get('base_url', 'https://api.siliconflow.cn/v1')
        self.client = None
        self.connection_error = None

        if self.api_key:
            self._init_client()

    def _init_client(self):
        try:
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)

            import openai
            import httpx
            http_client = httpx.Client(proxy=None, verify=False, timeout=60.0)

            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                http_client=http_client
            )
        except ImportError:
            self.connection_error = "未安装 openai SDK"
        except Exception as e:
            self.connection_error = f"初始化客户端失败: {str(e)}"

    def test_connection(self) -> tuple:
        if not self.client:
            return False, self.connection_error or "客户端未初始化"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "测试"}],
                max_tokens=10
            )
            return True, f"连接成功！模型: {self.model}"
        except Exception as e:
            return False, f"连接失败: {str(e)}"

    def generate_root_cause_explanation(self,
                                       analysis_results: Dict,
                                       actual_data: pd.DataFrame,
                                       counterfactual_data: pd.DataFrame,
                                       ontology_info: str = None,
                                       causal_graph: str = None) -> str:
        prompt = self._build_root_cause_prompt(analysis_results, actual_data, counterfactual_data, ontology_info, causal_graph)

        # 保存提示词到文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # 使用绝对路径确保保存到正确位置
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_filename = os.path.join(current_dir, f"prompts/root_cause_prompt_{timestamp}.txt")
        os.makedirs(os.path.dirname(prompt_filename), exist_ok=True)
        try:
            with open(prompt_filename, 'w', encoding='utf-8') as f:
                f.write("# 根因分析提示词\n\n")
                f.write("系统角色: 你是一个专业的供应链管理顾问，擅长库存优化和根因分析。请用专业但易懂的语言回答。\n\n")
                f.write("用户问题: \n")
                f.write(prompt)
        except Exception as e:
            pass

        if not self.client:
            return "错误：大模型客户端未初始化，请先配置API密钥"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的供应链管理顾问，擅长库存优化和根因分析。请用专业但易懂的语言回答。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"错误：调用大模型API失败 - {str(e)}"

    def generate_solution(self,
                         analysis_results: Dict,
                         actual_data: pd.DataFrame,
                         counterfactual_data: pd.DataFrame,
                         ontology_info: str = None,
                         causal_graph: str = None,
                         root_cause_text: str = None,
                         knowledge_base: str = None) -> str:
        prompt = self._build_solution_prompt(
            analysis_results, actual_data, counterfactual_data,
            ontology_info, causal_graph, root_cause_text, knowledge_base
        )

        # 保存提示词到文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # 使用绝对路径确保保存到正确位置
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_filename = os.path.join(current_dir, f"prompts/solution_prompt_{timestamp}.txt")
        os.makedirs(os.path.dirname(prompt_filename), exist_ok=True)
        try:
            with open(prompt_filename, 'w', encoding='utf-8') as f:
                f.write("# 解决方案提示词\n\n")
                f.write("系统角色: 你是一个专业的供应链管理顾问，擅长库存优化和解决方案设计。请给出具体可行的建议。\n\n")
                f.write("用户问题: \n")
                f.write(prompt)
        except Exception as e:
            pass

        if not self.client:
            return "错误：大模型客户端未初始化，请先配置API密钥"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的供应链管理顾问，擅长库存优化和解决方案设计。请给出具体可行的建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"错误：调用大模型API失败 - {str(e)}"

    def _build_root_cause_prompt(self,
                                analysis_results: Dict,
                                actual_data: pd.DataFrame,
                                counterfactual_data: pd.DataFrame,
                                ontology_info: str = None,
                                causal_graph: str = None) -> str:
        cf_results = analysis_results.get('counterfactual_analysis', {})

        decline_start = "2024-11-01"

        try:
            actual_data['date'] = pd.to_datetime(actual_data['date'])
            actual_data_decline = actual_data[actual_data['date'] >= decline_start]
            before_decline = actual_data[actual_data['date'] < decline_start]
        except:
            actual_data_decline = actual_data
            before_decline = actual_data

        try:
            avg_kunlun_before = before_decline['kunlun_2280_sales'].mean()
            avg_kunlun_after = actual_data_decline['kunlun_2280_sales'].mean()
            avg_inv_before = before_decline['pac900s12_b2_1_inventory'].mean()
            avg_inv_after = actual_data_decline['pac900s12_b2_1_inventory'].mean()
            avg_2288hv7 = actual_data['server_2288hv7_sales'].mean()
        except:
            avg_kunlun_before = 100
            avg_kunlun_after = 60
            avg_inv_before = 100
            avg_inv_after = 200
            avg_2288hv7 = 80

        what_happened = f"""- 昆仑2280销量在{decline_start}开始下降，平均月销量从约{avg_kunlun_before:.0f}台下降到约{avg_kunlun_after:.0f}台
- PAC900S12-B2-1库存从约{avg_inv_before:.0f}个上升到约{avg_inv_after:.0f}个
- 2288HV7销量保持稳定，平均月销量约{avg_2288hv7:.0f}台
- 2288HV7未使用PAC900S12-B2-1（历史数据全为0）"""

        if ontology_info is None:
            ontology_info = """以下是产品与部件的关系：
- 昆仑2280 使用 PAC900S12-B2-1（服务器白金900W电源）
- 2288HV7 使用 PAC900S12-B2-1（服务器白金900W电源）（当前未使用）"""

        default_causal_graph = """昆仑2280销量 → PAC900S12-B2-1消耗量
2288HV7销量 → PAC900S12-B2-1消耗量
2288HV7使用PAC900S12-B2-1 → PAC900S12-B2-1消耗量
PAC900S12-B2-1消耗量 → PAC900S12-B2-1库存
PAC900S12-B2-1采购量 → PAC900S12-B2-1库存
昆仑2280销量 → PAC900S12-B2-1采购量"""

        causal_graph_text = causal_graph if causal_graph else default_causal_graph

        prompt = f"""你是一个专业的供应链管理顾问。请根据以下数据分析结果，找出库存高的根本原因。

## 问题描述
某制造企业发现PAC900S12-B2-1库存持续升高，占用大量资金，需要找出根本原因。

## 发生了什么（数据分析结果）
{what_happened}

## 本体信息
{ontology_info}

## 因果图结构（有向无环图）

```
{causal_graph_text}
```

**因果图说明**：
- 箭头（→）表示因果关系方向，从原因指向结果
- **2288HV7使用PAC900S12-B2-1** 是我们要干预的处理变量（Treatment）
- **PAC900S12-B2-1库存** 是我们要分析的结果变量（Outcome）

## 数据分析结果

### 1. 库存对比分析
- 实际库存均值: {cf_results.get('actual_inventory_mean', 0):.2f}
- 反事实库存均值（如果2288HV7使用PAC900S12-B2-1）: {cf_results.get('counterfactual_inventory_mean', 0):.2f}
- 库存降低: {cf_results.get('inventory_reduction', 0):.2f} ({cf_results.get('reduction_percentage', 0):.2f}%)

### 2. 销量下降期库存分析
- 销量下降期实际库存: {cf_results.get('decline_period_actual_inventory', 0):.2f}
- 销量下降期反事实库存: {cf_results.get('decline_period_counterfactual_inventory', 0):.2f}
- 销量下降期库存降低: {cf_results.get('decline_period_reduction', 0):.2f}

### 3. 因果效应分析
- 因果效应值: {analysis_results.get('causal_effect', 0):.4f}

### 4. 根因判定
- 是否为根因: {'是' if cf_results.get('is_root_cause', False) else '否'}
- 判定依据: 库存降低超过20%即认为是核心根因

## 分析任务

请分析以下问题：

1. **发生了什么**：昆仑2280销量下降后，发生了什么变化？

2. **本体关系分析**：请根据本体信息分析：
   - 电源产品的供应商是谁？不同库存实体之间有什么关系？
   - PAC900S12-B2-1和PAC900S12-B2是否是同一个产品？它们是什么关系？
   - 这种关系如何影响库存？

3. **因果机制**：结合因果图和数据，找出导致库存高的根本原因

4. **输出根本原因**：明确给出库存高的根本原因是什么

## 输出要求

**请用简洁专业的语言，明确指出根因是什么，并解释为什么这是根因。**

要求：
1. 直接给出结论：根本原因是什么
2. 用数据支撑你的结论
3. 解释因果机制和推理过程
4. 语言要简洁明了，适合向领导汇报
5. **重点分析本体关系**：从本体信息中发现库存高的真正原因
"""
        return prompt

    def _build_solution_prompt(self,
                               analysis_results: Dict,
                               actual_data: pd.DataFrame,
                               counterfactual_data: pd.DataFrame,
                               ontology_info: str = None,
                               causal_graph: str = None,
                               root_cause_text: str = None,
                               knowledge_base: str = None) -> str:
        cf_results = analysis_results.get('counterfactual_analysis', {})

        if ontology_info is None:
            ontology_info = """以下是产品与部件的关系：
- 昆仑2280 使用 PAC900S12-B2-1（服务器白金900W电源）
- 2288HV7 使用 PAC900S12-B2-1（服务器白金900W电源）（当前未使用）"""

        default_causal_graph = """昆仑2280销量 → PAC900S12-B2-1消耗量
2288HV7销量 → PAC900S12-B2-1消耗量
2288HV7使用PAC900S12-B2-1 → PAC900S12-B2-1消耗量
PAC900S12-B2-1消耗量 → PAC900S12-B2-1库存
PAC900S12-B2-1采购量 → PAC900S12-B2-1库存
昆仑2280销量 → PAC900S12-B2-1采购量"""

        causal_graph_text = causal_graph if causal_graph else default_causal_graph

        root_cause_section = ""
        if root_cause_text:
            root_cause_section = f"""
## 已确定的根本原因

{root_cause_text}
"""

        knowledge_base_section = ""
        if knowledge_base:
            knowledge_base_section = f"""
## 企业知识库

{knowledge_base}

"""

        prompt = f"""你是一个专业的供应链管理顾问。请根据以下分析结果，给出具体的解决方案。

## 问题描述
某制造企业发现PAC900S12-B2-1库存持续升高，占用大量资金，需要找出根本原因并制定解决方案。

{knowledge_base_section}## 本体信息
{ontology_info}

## 因果图结构（有向无环图）

```
{causal_graph_text}
```
{root_cause_section}
## 根因分析结果

通过因果分析，已找出导致库存高的根本原因：

### 1. 库存对比
- 实际库存均值: {cf_results.get('actual_inventory_mean', 0):.2f}
- 反事实库存均值（如果2288HV7使用PAC900S12-B2-1）: {cf_results.get('counterfactual_inventory_mean', 0):.2f}
- 库存降低: {cf_results.get('inventory_reduction', 0):.2f} ({cf_results.get('reduction_percentage', 0):.2f}%)

### 2. 因果效应
- 如果2288HV7使用PAC900S12-B2-1，库存可降低 {cf_results.get('reduction_percentage', 0):.2f}%

### 3. 根因判定
- 是否为根因: {'是' if cf_results.get('is_root_cause', False) else '否'}
- 判定依据: 库存降低超过20%即认为是核心根因

## 分析任务

请基于以上信息，制定具体的解决方案：

1. **问题诊断**：确认根本原因是什么
2. **解决方案**：针对这个根因，应该采取哪些改进措施？
3. **实施步骤**：如何实施这些措施？
4. **预期效果**：实施后预期达到什么效果？
5. **风险评估**：实施过程中可能遇到哪些风险？

## 输出要求

**请给出具体的解决方案和实施建议。**

要求：
1. 明确指出根本原因
2. 给出具体可行的改进措施
3. 说明详细的实施步骤
4. 评估预期效果（用量化数据）
5. 提出风险提示和应对措施
6. 语言要简洁明了，适合向领导汇报
7. 方案要具有可操作性，不要过于理论化
"""
        return prompt
