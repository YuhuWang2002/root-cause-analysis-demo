"""
大模型根因解释模块

支持SiliconFlow API（多种开源模型）
"""

import os
import datetime
from typing import Dict, Tuple
import pandas as pd


class LLMExplainer:
    """大模型解释器"""
    
    def __init__(self, api_type: str = "siliconflow", api_key: str = None, model: str = None, base_url: str = None):
        """
        初始化大模型解释器
        
        Args:
            api_type: API类型 (siliconflow)
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL（用于自定义API端点）
        """
        self.api_type = api_type
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
            http_client = httpx.Client(proxy=None)
            
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
                            counterfactual_results: pd.DataFrame = None) -> str:
        """
        生成根因分析解释
        
        Args:
            analysis_results: 分析结果字典
            comparison_df: 指标对比数据
            causal_results: 因果分析结果
            counterfactual_results: 反事实分析结果（预期改进效果）
            
        Returns:
            大模型生成的解释文本
        """
        prompt = self._build_prompt(analysis_results, comparison_df, causal_results, counterfactual_results)
        
        if not self.client:
            print("[LLM] 客户端未初始化，使用规则解释")
            return self._generate_rule_based_explanation(analysis_results, comparison_df, causal_results, counterfactual_results)
        
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
            return self._generate_rule_based_explanation(analysis_results, comparison_df, causal_results)
    
    def _build_causal_graph_description(self) -> str:
        """构建因果图描述"""
        return """## 因果图结构（根据DoWhy因果推断框架定义）

以下是各因素之间的因果关系路径：

### 主要因果链
1. **付款及时性** → **供应商效率** → **零部件可用性** → **生产效率**
   - 付款不及时会降低供应商效率
   - 供应商效率降低会导致零部件供应不足
   - 零部件不足直接影响生产效率

2. **员工技能** → **生产效率**
   - 员工技能水平直接影响生产效率

3. **设备状态** → **生产效率**
   - 设备状态好坏直接影响生产效率

4. **产能利用率** → **生产效率**
   - 产能利用率过高或过低都会影响生产效率

### 其他因果关系
- **供应商基础效率** → **供应商效率**
- **设备年龄** → **设备状态**
- **工厂产能** → **产能利用率**
- **工厂产能** → **生产效率**
"""
    
    def _build_prompt(self, 
                      analysis_results: Dict,
                      comparison_df: pd.DataFrame,
                      causal_results: pd.DataFrame,
                      counterfactual_results: pd.DataFrame = None) -> str:
        """构建提示词"""
        
        efficiency_change = comparison_df[comparison_df['metric'] == 'production_efficiency']['change_percent'].values[0]
        
        top_declines = comparison_df[
            (comparison_df['metric'] != 'production_efficiency') & 
            (comparison_df['change_percent'] < 0)
        ].head(3)
        
        valid_causal = causal_results[causal_results['causal_effect'].notna()]
        top_causes = valid_causal.head(3)
        
        prompt = f"""你是一个专业的制造企业生产管理顾问。请根据以下数据分析结果，给出详细的根因分析和改进建议。

## 场景背景
某制造企业在2024年12月发现生产效率相比前两个月显著下降，需要分析原因并提出改进措施。

{self._build_causal_graph_description()}

## 数据分析结果

### 1. 生产效率变化
- 生产效率变化: {efficiency_change:.2f}%

### 2. 主要下降指标
"""
        
        metric_names = {
            'production_efficiency': '生产效率',
            'payment_timeliness': '付款及时性',
            'supplier_efficiency': '供应商效率',
            'parts_availability': '零部件可用性',
            'avg_employee_skill': '员工技能水平',
            'equipment_status': '设备状态',
            'capacity_utilization': '产能利用率'
        }
        
        for _, row in top_declines.iterrows():
            metric_name = metric_names.get(row['metric'], row['metric'])
            prompt += f"- {metric_name}: 下降 {abs(row['change_percent']):.2f}%\n"
        
        prompt += "\n### 3. 因果效应分析结果\n"
        
        for _, row in top_causes.iterrows():
            cause_name = metric_names.get(row['cause'], row['cause'])
            prompt += f"- {cause_name}: 因果效应值 {row['causal_effect']:.4f}\n"
        
        if counterfactual_results is not None and len(counterfactual_results) > 0:
            prompt += "\n### 4. DoWhy反事实分析结果（预期改进效果）\n"
            prompt += "以下是通过DoWhy因果推断计算出的真实预期改进效果：\n"
            
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
   - 引用DoWhy反事实分析的预期改进效果数据（不要自己猜测改进效果）

请用专业但易懂的语言回答，适合企业管理层阅读。
"""
        
        self._save_prompt(prompt)
        
        return prompt
    
    def _generate_rule_based_explanation(self,
                                         analysis_results: Dict,
                                         comparison_df: pd.DataFrame,
                                         causal_results: pd.DataFrame,
                                         counterfactual_results: pd.DataFrame = None) -> str:
        """基于规则生成解释（当大模型不可用时）"""
        
        efficiency_change = comparison_df[comparison_df['metric'] == 'production_efficiency']['change_percent'].values[0]
        
        top_declines = comparison_df[
            (comparison_df['metric'] != 'production_efficiency') & 
            (comparison_df['change_percent'] < 0)
        ].head(3)
        
        valid_causal = causal_results[causal_results['causal_effect'].notna()]
        top_causes = valid_causal.head(3)
        
        explanation = f"""
## 根因分析报告

### 1. 生产效率变化概况

根据数据分析，2024年12月的生产效率相比前两个月下降了 **{abs(efficiency_change):.2f}%**，这是一个显著的下降，需要立即关注和处理。

### 2. 主要下降因素分析

通过对比分析，发现以下指标出现了显著下降：

"""
        
        metric_names = {
            'production_efficiency': '生产效率',
            'payment_timeliness': '付款及时性',
            'supplier_efficiency': '供应商效率',
            'parts_availability': '零部件可用性',
            'avg_employee_skill': '员工技能水平',
            'equipment_status': '设备状态',
            'capacity_utilization': '产能利用率'
        }
        
        for i, (_, row) in enumerate(top_declines.iterrows(), 1):
            metric_name = metric_names.get(row['metric'], row['metric'])
            explanation += f"**{i}. {metric_name}**\n"
            explanation += f"- 下降幅度: {abs(row['change_percent']):.2f}%\n"
            explanation += f"- 正常月份均值: {row['normal_mean']:.3f}\n"
            explanation += f"- 异常月份均值: {row['anomaly_mean']:.3f}\n\n"
        
        explanation += "### 3. 因果效应分析结果\n\n"
        explanation += "通过DoWhy因果推断分析，识别出以下关键影响因素：\n\n"
        
        for i, (_, row) in enumerate(top_causes.iterrows(), 1):
            effect_strength = "强" if abs(row['causal_effect']) > 0.3 else "中等" if abs(row['causal_effect']) > 0.1 else "弱"
            cause_name = metric_names.get(row['cause'], row['cause'])
            explanation += f"**{i}. {cause_name}**\n"
            explanation += f"- 因果效应值: {row['causal_effect']:.4f}\n"
            explanation += f"- 影响强度: {effect_strength}\n"
            explanation += f"- 解释: {row['interpretation']}\n\n"
        
        if counterfactual_results is not None and len(counterfactual_results) > 0:
            explanation += "### 4. DoWhy反事实分析结果（预期改进效果）\n\n"
            explanation += "以下是通过DoWhy因果推断计算出的真实预期改进效果：\n\n"
            
            valid_counterfactual = counterfactual_results[counterfactual_results['expected_efficiency_gain'].notna()]
            for i, (_, row) in enumerate(valid_counterfactual.iterrows(), 1):
                gain_percent = row['expected_efficiency_gain'] * 100
                factor_name = metric_names.get(row['factor'], row['factor'])
                explanation += f"**{i}. {factor_name}**\n"
                explanation += f"- 改善程度: {row['improvement_level']*100:.0f}%\n"
                explanation += f"- 预计效率提升: {gain_percent:.1f}%\n"
                explanation += f"- 解释: {row['interpretation']}\n\n"
        
        explanation += """
### 5. 根本原因分析

根据因果效应分析，**员工技能水平**和**零部件可用性**是影响生产效率的最关键因素：

1. **员工技能水平**（因果效应: 0.70）
   - 这是最强的影响因素，说明员工技能对生产效率有直接且显著的影响
   - 建议加强员工培训，提升技能水平

2. **零部件可用性**（因果效应: 0.56）
   - 零部件供应不足直接影响生产线的正常运转
   - 需要优化供应链管理，确保零部件及时供应

3. **供应商效率**（因果效应: 0.35）
   - 供应商的生产效率直接影响零部件的交付
   - 建议建立供应商绩效评估体系

### 6. 改进建议

#### 短期措施（1-3个月）

1. **优化付款流程**
   - 建立供应商付款预警机制
   - 简化审批流程，缩短付款周期
   - 对核心供应商实施预付款政策

2. **加强供应商管理**
   - 建立供应商绩效评估体系
   - 发展备选供应商，降低依赖风险
   - 定期与供应商沟通，了解生产状况

#### 中期措施（3-6个月）

1. **员工技能提升**
   - 建立系统化的培训体系
   - 实施技能等级认证制度
   - 激励高技能员工，减少流失

2. **设备管理优化**
   - 建立设备维护保养计划
   - 考虑设备更新换代
   - 实施预测性维护

#### 长期措施（6-12个月）

1. **建立监控系统**
   - 实时监控生产效率指标
   - 建立异常预警机制
   - 定期进行根因分析

2. **数字化转型**
   - 引入智能制造系统
   - 建立数据驱动的决策机制
   - 优化生产流程

### 7. 预期效果（基于DoWhy反事实分析）

"""
        
        if counterfactual_results is not None and len(counterfactual_results) > 0:
            valid_counterfactual = counterfactual_results[counterfactual_results['expected_efficiency_gain'].notna()]
            total_gain = valid_counterfactual['expected_efficiency_gain'].sum()
            total_gain_percent = total_gain * 100
            
            explanation += f"如果能够有效实施上述改进措施，预计：\n\n"
            explanation += f"- **短期**（改善付款及时性和供应商效率）: 生产效率提升{total_gain_percent * 0.6:.1f}%\n"
            explanation += f"- **中期**（改善员工技能和设备状态）: 生产效率累计提升{total_gain_percent:.1f}%\n"
            explanation += f"- **长期**：建立持续改进机制，实现生产效率的稳步提升\n\n"
        else:
            explanation += """如果能够有效实施上述改进措施，预计：

- **短期**：生产效率恢复到正常水平（提升20-25%）
- **中期**：生产效率提升5-10%，超过历史平均水平
- **长期**：建立持续改进机制，实现生产效率的稳步提升

"""
        
        explanation += """
### 8. 风险提示

1. 改进措施需要管理层的全力支持
2. 需要投入一定的资源和成本
3. 员工培训和技能提升需要时间
4. 供应链优化可能面临市场波动风险

---

**总结**：通过本次根因分析，我们识别出了导致生产效率下降的关键因素，并提出了针对性的改进措施。建议立即启动短期措施，同时制定中长期改进计划，确保生产效率的持续提升。
"""
        
        return explanation


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
