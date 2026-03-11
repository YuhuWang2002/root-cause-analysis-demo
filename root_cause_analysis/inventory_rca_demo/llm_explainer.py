"""
PAC900S12-B2-1库存高因果根因分析 - LLM解释模块

使用大模型生成业务化的根因分析解释
"""

import os
import datetime
from typing import Dict, Optional
import pandas as pd


class LLMExplainer:
    """大模型解释器"""
    
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        """
        初始化大模型解释器
        
        Args:
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL
        """
        self.api_key = api_key
        self.model = model or "Qwen/Qwen2.5-7B-Instruct"
        self.base_url = base_url
        self.client = None
        self.connection_error = None
        self.prompt_save_dir = "prompts"
        self._ensure_prompt_dir()
        
        if self.api_key:
            self._init_client()
    
    def _ensure_prompt_dir(self):
        """确保保存提示词的目录存在"""
        if not os.path.exists(self.prompt_save_dir):
            os.makedirs(self.prompt_save_dir)
    
    def _save_prompt(self, prompt: str):
        """保存提示词到文件"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.prompt_save_dir}/prompt_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
                f.write(f"模型: {self.model}\n")
                f.write("\n" + "="*80 + "\n\n")
                f.write(prompt)
        except Exception as e:
            print(f"保存提示词失败: {str(e)}")
    
    def _init_client(self):
        """初始化API客户端"""
        try:
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
            
            import openai
            import httpx
            http_client = httpx.Client(proxy=None, verify=False)
            
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.siliconflow.cn/v1",
                http_client=http_client
            )
            
        except ImportError:
            self.connection_error = "未安装 openai SDK，请运行: pip install openai httpx"
        except Exception as e:
            self.connection_error = f"初始化客户端失败: {str(e)}"
    
    def test_connection(self) -> tuple:
        """测试API连接是否可用"""
        if not self.client:
            return False, "客户端未初始化，请检查API密钥是否正确"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "测试连接"}],
                max_tokens=10
            )
            return True, f"连接成功！模型: {self.model}"
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return False, "API密钥无效或未授权"
            elif "not found" in error_msg.lower():
                return False, f"API端点未找到"
            elif "model" in error_msg.lower():
                return False, f"模型 {self.model} 不可用"
            else:
                return False, f"连接测试失败: {error_msg}"
    
    def generate_explanation(self,
                            analysis_results: Dict,
                            actual_data: pd.DataFrame,
                            counterfactual_data: pd.DataFrame) -> str:
        """
        生成根因分析解释（旧方法，保留兼容性）
        
        Args:
            analysis_results: 分析结果字典
            actual_data: 实际数据
            counterfactual_data: 反事实数据
            
        Returns:
            大模型生成的解释文本
        """
        prompt = self._build_prompt(analysis_results, actual_data, counterfactual_data)
        
        if not self.client:
            return "错误：大模型客户端未初始化，请检查API配置"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的供应链管理顾问，擅长库存优化和根因分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"错误：调用大模型API失败 - {str(e)}"
    
    def generate_root_cause_explanation(self,
                                       analysis_results: Dict,
                                       actual_data: pd.DataFrame,
                                       counterfactual_data: pd.DataFrame,
                                       ontology_info: str = None,
                                       causal_graph: str = None) -> str:
        """
        生成根因解释（6.2步骤）
        
        Args:
            analysis_results: 分析结果字典
            actual_data: 实际数据
            counterfactual_data: 反事实数据
            ontology_info: 本体信息，如果为None则使用默认信息
            causal_graph: 因果图，如果为None则使用默认因果图
            
        Returns:
            根因解释文本
        """
        prompt = self._build_root_cause_prompt(analysis_results, actual_data, counterfactual_data, ontology_info, causal_graph)
        
        if not self.client:
            return "错误：大模型客户端未初始化，请检查API配置"
        
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
                         root_cause_text: str = None) -> str:
        """
        生成解决方案（6.3步骤）
        
        Args:
            analysis_results: 分析结果字典
            actual_data: 实际数据
            counterfactual_data: 反事实数据
            ontology_info: 本体信息JSON
            causal_graph: 因果图DOT字符串
            root_cause_text: 根因分析文本
            
        Returns:
            解决方案文本
        """
        prompt = self._build_solution_prompt(
            analysis_results, 
            actual_data, 
            counterfactual_data,
            ontology_info,
            causal_graph,
            root_cause_text
        )
        
        if not self.client:
            return "错误：大模型客户端未初始化，请检查API配置"
        
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
    
    def _build_prompt(self,
                     analysis_results: Dict,
                     actual_data: pd.DataFrame,
                     counterfactual_data: pd.DataFrame) -> str:
        """构建提示词"""
        
        cf_results = analysis_results.get('counterfactual_analysis', {})
        
        decline_period_actual = actual_data[actual_data['is_decline_period'] == True]
        decline_period_counterfactual = counterfactual_data[counterfactual_data['is_decline_period'] == True]
        
        prompt = f"""你是一个专业的供应链管理顾问。请根据以下数据分析结果，给出详细的根因分析和改进建议。

## 场景背景
某制造企业发现昆仑2280销量下降后，PAC900S12-B2-1（服务器白金900W电源）库存处于高位。需要验证：2288HV7未使用PAC900S12-B2-1是PAC900S12-B2-1库存高的核心因果根因。

## 因果图结构（有向无环图）

以下是本次分析使用的因果图，表示变量之间的因果关系：

```
昆仑2280销量 → PAC900S12-B2-1消耗量
2288HV7销量 → PAC900S12-B2-1消耗量
2288HV7使用PAC900S12-B2-1 → PAC900S12-B2-1消耗量
PAC900S12-B2-1消耗量 → PAC900S12-B2-1库存
PAC900S12-B2-1采购量 → PAC900S12-B2-1库存
昆仑2280销量 → PAC900S12-B2-1采购量
```

**因果图说明**：
- 箭头（→）表示因果关系方向，从原因指向结果
- **2288HV7使用PAC900S12-B2-1** 是我们要干预的处理变量
- **PAC900S12-B2-1库存** 是我们要分析的结果变量
- 其他变量是影响库存的中间变量或混杂变量

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

### 4. 驳斥检验结果
"""
        
        refutation_results = analysis_results.get('refutation_results', {})
        for test_name, result in refutation_results.items():
            if isinstance(result, dict) and 'error' not in result:
                prompt += f"- {test_name}: 新效应值 {result.get('new_effect', 0):.4f}\n"
        
        prompt += f"""
### 5. 根因判定
- 是否为根因: {'是' if cf_results.get('is_root_cause', False) else '否'}
- 判定依据: 库存降低超过20%即认为是核心根因

## 请回答以下问题：

1. **根因分析**：产品B未使用部件A是否是导致库存高的核心根因？请结合数据分析结果进行解释。

2. **影响机制**：产品B未使用部件A是如何导致库存积压的？请解释因果路径。

3. **量化影响**：如果2288HV7使用PAC900S12-B2-1，库存可以降低多少？这个影响有多大？

4. **改进建议**：针对这个根因，应该采取哪些改进措施？请给出具体的建议。

请用专业但易懂的语言回答，适合企业管理层阅读。
"""
        
        self._save_prompt(prompt)
        
        return prompt
    
    def _build_root_cause_prompt(self,
                                analysis_results: Dict,
                                actual_data: pd.DataFrame,
                                counterfactual_data: pd.DataFrame,
                                ontology_info: str = None,
                                causal_graph: str = None) -> str:
        """构建根因解释prompt（6.2步骤）"""
        
        cf_results = analysis_results.get('counterfactual_analysis', {})
        
        decline_start = "2024-11-01"
        
        actual_data_decline = actual_data[pd.to_datetime(actual_data['date']) >= decline_start]
        
        what_happened = f"""- 昆仑2280销量在{decline_start}开始下降，平均月销量从约{actual_data[pd.to_datetime(actual_data['date']) < decline_start]['kunlun_2280_sales'].mean():.0f}台下降到约{actual_data_decline['kunlun_2280_sales'].mean():.0f}台
- PAC900S12-B2-1库存从约{actual_data[pd.to_datetime(actual_data['date']) < decline_start]['pac900s12_b2_1_inventory'].mean():.0f}个上升到约{actual_data_decline['pac900s12_b2_1_inventory'].mean():.0f}个
- 2288HV7销量保持稳定，平均月销量约{actual_data['server_2288hv7_sales'].mean():.0f}台
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

## 发生了什么（6.1数据分析结果）
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
- 因果效应值含义: {analysis_results.get('causal_effect', 0):.4f}，表示如果2288HV7使用PAC900S12-B2-1，每台2288HV7服务器会导致PAC900S12-B2-1库存增加多少个

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

        self._save_prompt(prompt)
        
        return prompt
    
    def _build_solution_prompt(self,
                               analysis_results: Dict,
                               actual_data: pd.DataFrame,
                               counterfactual_data: pd.DataFrame,
                               ontology_info: str = None,
                               causal_graph: str = None,
                               root_cause_text: str = None) -> str:
        """构建解决方案prompt（6.3步骤）"""
        
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
        
        prompt = f"""你是一个专业的供应链管理顾问。请根据以下分析结果，给出具体的解决方案。

## 问题描述
某制造企业发现PAC900S12-B2-1库存持续升高，占用大量资金，需要找出根本原因并制定解决方案。

## 本体信息
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
        
        self._save_prompt(prompt)
        
        return prompt


if __name__ == "__main__":
    from data_generator import create_inventory_scenario
    from causal_analyzer import InventoryCausalAnalyzer
    
    actual_data, counterfactual_data = create_inventory_scenario()
    
    analyzer = InventoryCausalAnalyzer(data=actual_data)
    results = analyzer.run_full_analysis(counterfactual_data)
    
    print("\n请配置API密钥以使用LLM解释器")
    print("示例: explainer = LLMExplainer(api_key='your_api_key')")
