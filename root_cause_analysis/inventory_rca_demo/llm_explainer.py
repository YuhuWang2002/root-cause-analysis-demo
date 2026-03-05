"""
部件A库存高因果根因分析 - LLM解释模块

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
        生成根因分析解释
        
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
某制造企业发现产品A销量下降后，部件A库存处于高位。需要验证：产品B未使用部件A是部件A库存高的核心因果根因。

## 因果图结构（有向无环图）

以下是本次分析使用的因果图，表示变量之间的因果关系：

```
产品A销量 → 部件A消耗量
产品B销量 → 部件A消耗量
产品B使用部件A → 部件A消耗量
部件A消耗量 → 部件A库存
部件A采购量 → 部件A库存
产品A销量 → 部件A采购量
```

**因果图说明**：
- 箭头（→）表示因果关系方向，从原因指向结果
- **产品B使用部件A** 是我们要干预的处理变量
- **部件A库存** 是我们要分析的结果变量
- 其他变量是影响库存的中间变量或混杂变量

## 数据分析结果

### 1. 库存对比分析
- 实际库存均值: {cf_results.get('actual_inventory_mean', 0):.2f}
- 反事实库存均值（如果产品B使用部件A）: {cf_results.get('counterfactual_inventory_mean', 0):.2f}
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

3. **量化影响**：如果产品B使用部件A，库存可以降低多少？这个影响有多大？

4. **改进建议**：针对这个根因，应该采取哪些改进措施？请给出具体的建议。

请用专业但易懂的语言回答，适合企业管理层阅读。
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
