"""
大模型根因解释模块（本体驱动版本）

支持SiliconFlow API（多种开源模型）
"""

import os
import datetime
from typing import Dict, Tuple, Optional
import pandas as pd
from ontology_manager import OntologyManager


class LLMExplainer:
    """大模型解释器（本体驱动版本）"""
    
    def __init__(self, api_type: str = "siliconflow", api_key: str = None, model: str = None, base_url: str = None, ontology_manager: Optional[OntologyManager] = None):
        """
        初始化大模型解释器
        
        Args:
            api_type: API类型 (siliconflow)
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL（用于自定义API端点）
            ontology_manager: 本体管理器，如果为None则不使用本体
        """
        self.api_type = api_type
        self.api_key = api_key
        self.model = model or "Qwen/Qwen2.5-7B-Instruct"
        self.base_url = base_url
        self.ontology = ontology_manager
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
            print(f"[LLM] 创建提示词保存目录: {self.prompt_save_dir}")
    
    def _save_prompt(self, prompt: str):
        """
        保存提示词到文件
        
        Args:
            prompt: 要保存的提示词
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.prompt_save_dir}/prompt_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
                f.write(f"模型: {self.model}\n")
                f.write(f"API类型: {self.api_type}\n")
                f.write(f"Base URL: {self.base_url or '默认'}\n")
                f.write("\n" + "="*80 + "\n\n")
                f.write(prompt)
            
            print(f"[LLM] 提示词已保存到: {filename}")
            
        except Exception as e:
            print(f"[LLM] 保存提示词失败: {str(e)}")
    
    def _init_client(self):
        """初始化API客户端"""
        try:
            # 取消代理设置，避免连接问题
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
            
            print(f"[LLM] 开始初始化客户端...")
            print(f"  - API Key: {self.api_key[:20] if self.api_key else 'None'}...{self.api_key[-10:] if self.api_key else ''}")
            print(f"  - Base URL: {self.base_url or 'https://api.siliconflow.cn/v1'}")
            print(f"  - Model: {self.model}")
            
            import openai
            import httpx
            http_client = httpx.Client(proxy=None,verify=False)
            
            self.client = openai.OpenAI(
                api_key=self.api_key, 
                base_url=self.base_url or "https://api.siliconflow.cn/v1",
                http_client=http_client
            )
            
            print(f"[LLM] 客户端初始化成功")
            
        except ImportError as e:
            self.connection_error = f"未安装 openai SDK，请运行: pip install openai httpx"
            print(f"[LLM] ImportError: {self.connection_error}")
            print(f"  - 详细错误: {str(e)}")
        except Exception as e:
            self.connection_error = f"初始化客户端失败: {str(e)}"
            print(f"[LLM] Exception: {self.connection_error}")
            print(f"  - 错误类型: {type(e).__name__}")
            print(f"  - 详细错误: {str(e)}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        测试API连接是否可用
        
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息或成功消息)
        """
        if not self.client:
            error_msg = "客户端未初始化，请检查API密钥是否正确"
            print(f"[LLM] 连接测试失败: {error_msg}")
            print(f"  - API Key: {self.api_key}")
            print(f"  - Base URL: {self.base_url or 'https://api.siliconflow.cn/v1'}")
            print(f"  - Model: {self.model}")
            return False, error_msg
        
        try:
            print(f"[LLM] 测试连接...")
            print(f"  - API Key: {self.api_key[:20]}...{self.api_key[-10:]}")
            print(f"  - Base URL: {self.base_url or 'https://api.siliconflow.cn/v1'}")
            print(f"  - Model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "测试连接"}
                ],
                max_tokens=10
            )
            
            success_msg = f"连接成功！模型: {self.model}"
            print(f"[LLM] {success_msg}")
            return True, success_msg
            
        except Exception as e:
            error_msg = str(e)
            
            print(f"[LLM] 连接测试失败: {error_msg}")
            print(f"  - API Key: {self.api_key[:20]}...{self.api_key[-10:]}")
            print(f"  - Base URL: {self.base_url or 'https://api.siliconflow.cn/v1'}")
            print(f"  - Model: {self.model}")
            
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower() or "401" in error_msg:
                return False, f"API密钥无效或未授权，请检查密钥是否正确"
            elif "not found" in error_msg.lower() or "404" in error_msg:
                return False, f"API端点未找到，请检查Base URL是否正确: {self.base_url or 'https://api.siliconflow.cn/v1'}"
            elif "model" in error_msg.lower() and "not" in error_msg.lower():
                return False, f"模型 {self.model} 不可用，请检查模型名称是否正确"
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                return False, f"API请求频率超限，请稍后再试"
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return False, f"网络连接失败，请检查网络或Base URL: {self.base_url or 'https://api.siliconflow.cn/v1'}"
            elif "insufficient" in error_msg.lower() or "quota" in error_msg.lower():
                return False, f"API配额不足，请检查账户余额"
            else:
                return False, f"连接测试失败: {error_msg}"
    
    def generate_explanation(self, 
                            analysis_results: Dict,
                            comparison_df: pd.DataFrame,
                            causal_results: pd.DataFrame,
                            counterfactual_results: pd.DataFrame = None,
                            causal_graph: str = None) -> str:
        """
        生成根因分析解释
        
        Args:
            analysis_results: 分析结果字典
            comparison_df: 指标对比数据
            causal_results: 因果分析结果
            counterfactual_results: 反事实分析结果（预期改进效果）
            causal_graph: 因果图（DOT格式字符串）
            
        Returns:
            大模型生成的解释文本
        """
        prompt = self._build_prompt(analysis_results, comparison_df, causal_results, counterfactual_results, causal_graph)
        
        if not self.client:
            print("[LLM] 客户端未初始化，无法生成解释")
            return "错误：大模型客户端未初始化，请检查API配置"
        
        try:
            print(f"[LLM] 生成解释...")
            print(f"  - API Key: {self.api_key[:20]}...{self.api_key[-10:]}")
            print(f"  - Base URL: {self.base_url or 'https://api.siliconflow.cn/v1'}")
            print(f"  - Model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的制造企业生产管理顾问，擅长数据分析和根因分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[LLM] 调用大模型API失败: {str(e)}")
            print(f"  - API Key: {self.api_key[:20]}...{self.api_key[-10:]}")
            print(f"  - Base URL: {self.base_url or 'https://api.siliconflow.cn/v1'}")
            print(f"  - Model: {self.model}")
            return f"错误：调用大模型API失败 - {str(e)}"
    

    def _build_prompt(self, 
                      analysis_results: Dict,
                      comparison_df: pd.DataFrame,
                      causal_results: pd.DataFrame,
                      counterfactual_results: pd.DataFrame = None,
                      causal_graph: str = None) -> str:
        """构建提示词"""
        
        # 检查是否提供了因果图
        if not causal_graph:
            raise ValueError("错误：未提供因果图，无法生成解释")
        
        # 自动检测主要指标
        if 'production_efficiency' in comparison_df['metric'].values:
            main_metric = 'production_efficiency'
            main_metric_name = '生产效率'
            scenario_background = "某制造企业在2024年12月发现生产效率相比前两个月显著下降，需要分析原因并提出改进措施。"
        elif 'inventory_level' in comparison_df['metric'].values:
            main_metric = 'inventory_level'
            main_metric_name = '库存水平'
            scenario_background = "某制造企业在2024年12月发现库存水平相比前两个月显著异常，需要分析原因并提出优化措施。"
        else:
            # 使用第一个指标作为主要指标
            main_metric = comparison_df['metric'].iloc[0]
            main_metric_name = main_metric
            scenario_background = "某制造企业发现关键指标异常，需要分析原因并提出改进措施。"
        
        # 获取主要指标的变化值
        main_metric_change = comparison_df[comparison_df['metric'] == main_metric]['change_percent'].values[0]
        
        # 获取主要下降指标
        top_declines = comparison_df[
            (comparison_df['metric'] != main_metric) & 
            (comparison_df['change_percent'] < 0)
        ].head(3)
        
        valid_causal = causal_results[causal_results['causal_effect'].notna()]
        top_causes = valid_causal.head(3)
        
        # 使用实际的因果图
        causal_graph_description = f"## 因果图结构（实际分析使用的因果图）\n\n```\n{causal_graph}\n```\n\n"
        
        prompt = f"""你是一个专业的制造企业生产管理顾问。请根据以下数据分析结果，给出详细的根因分析和改进建议。

## 场景背景
{scenario_background}

{causal_graph_description}

## 数据分析结果

### 1. {main_metric_name}变化
- {main_metric_name}变化: {main_metric_change:.2f}%

### 2. 主要异常指标
"""
        
        # 动态生成指标名称映射，优先使用本体中的名称，否则使用默认转换
        metric_names = {}
        
        # 如果有本体管理器，从本体中获取指标名称
        if self.ontology:
            try:
                # 从本体中获取所有指标定义
                if hasattr(self.ontology, 'schema') and self.ontology.schema:
                    for entity_type in self.ontology.schema.get('entity_types', []):
                        for metric in entity_type.get('metrics', []):
                            metric_names[metric.get('name')] = metric.get('display_name', metric.get('name'))
            except Exception as e:
                print(f"[LLM] 从本体获取指标名称失败: {e}")
        
        # 添加默认映射作为 fallback
        default_metric_names = {
            'production_efficiency': '生产效率',
            'payment_timeliness': '付款及时性',
            'supplier_efficiency': '供应商效率',
            'parts_availability': '零部件可用性',
            'avg_employee_skill': '员工技能水平',
            'equipment_status': '设备状态',
            'capacity_utilization': '产能利用率',
            'inventory_level': '库存水平',
            'server_2885_sales_quantity': '服务器2885销量',
            'cpu_xeon_6338_utilization_ratio_for_server_5885': 'CPU被服务器5885使用比例',
            'cpu_xeon_6338_utilization_ratio_for_server_2885': 'CPU被服务器2885使用比例'
        }
        
        # 更新默认映射，保留本体中的名称
        metric_names.update(default_metric_names)
        
        for _, row in top_declines.iterrows():
            metric_name = metric_names.get(row['metric'], row['metric'])
            prompt += f"- {metric_name}: 下降 {abs(row['change_percent']):.2f}%\n"
        
        prompt += "\n### 3. 因果效应分析结果\n"
        
        for _, row in top_causes.iterrows():
            cause_name = metric_names.get(row['cause'], row['cause'])
            prompt += f"- {cause_name}: 因果效应值 {row['causal_effect']:.4f}\n"
        
        # 检查是否有根因分析结果
        if analysis_results and 'root_cause_analysis' in analysis_results:
            root_cause_results = analysis_results['root_cause_analysis']
            if root_cause_results:
                prompt += "\n### 4. 根因分析排序结果\n"
                prompt += "以下是按因果效应绝对值排序的根因分析结果：\n"
                for i, item in enumerate(root_cause_results[:5], 1):
                    cause_name = metric_names.get(item['treatment'], item['treatment'])
                    prompt += f"{i}. {cause_name}: 因果效应值 {item['causal_effect']:.4f} (排名: {item['rank']})\n"
        
        if counterfactual_results is not None and len(counterfactual_results) > 0:
            prompt += "\n### 5. DoWhy反事实分析结果（预期改进效果）\n"
            prompt += "以下是通过DoWhy因果推断计算出的真实预期改进效果：\n"
            
            # 检查是否是V2版本的反事实分析结果
            if 'predicted_target_outcome' in counterfactual_results.columns:
                # V2版本的反事实分析结果
                for _, row in counterfactual_results.iterrows():
                    treatment_name = metric_names.get(row['treatment'], row['treatment'])
                    current_value = row.get('current_treatment', 'N/A')
                    target_value = row.get('target_treatment', 'N/A')
                    predicted_outcome = row.get('predicted_target_outcome', 'N/A')
                    feasibility = row.get('feasibility', 'N/A')
                    accuracy = row.get('outcome_accuracy', 'N/A')
                    
                    prompt += f"- {treatment_name}: 当前值 {current_value:.2f}，目标值 {target_value:.2f}，预测结果 {predicted_outcome:.2f}，可行性: {feasibility}，预测准确性: {accuracy}\n"
            else:
                # 原始版本的反事实分析结果
                valid_counterfactual = counterfactual_results[counterfactual_results['expected_efficiency_gain'].notna()]
                for _, row in valid_counterfactual.iterrows():
                    gain_percent = row['expected_efficiency_gain'] * 100
                    prompt += f"- {row['factor']}: 提升{row['improvement_level']*100:.0f}%，预计效率提升{gain_percent:.1f}%\n"
        
        prompt += """
## 请回答以下问题：

1. **根因分析**：根据因果图结构和因果效应分析结果，哪些因素是导致生产效率下降的根本原因？为什么？

2. **因果路径分析**：请结合上面提供的因果图结构，详细解释这些因素是如何通过因果链影响生产效率的。

3. **改进建议**：针对识别出的根本原因，应该采取哪些具体的改进措施？请按优先级排序。

4. **引用分析结果**：在回答中，请引用以下信息：
   - 引用因果图中的因果关系路径
   - 引用因果效应分析结果
   - 引用根因分析排序结果
   - 引用DoWhy反事实分析的预期改进效果数据（不要自己猜测改进效果）

请用专业但易懂的语言回答，适合企业管理层阅读。
"""
        
        self._save_prompt(prompt)
        
        return prompt
    



def create_explainer(api_type: str = "siliconflow", api_key: str = None, model: str = None, base_url: str = None) -> LLMExplainer:
    """
    创建大模型解释器
    
    Args:
        api_type: API类型
        api_key: API密钥
        model: 模型名称
        base_url: API基础URL
        
    Returns:
        LLMExplainer实例
    """
    return LLMExplainer(api_type=api_type, api_key=api_key, model=model, base_url=base_url)
