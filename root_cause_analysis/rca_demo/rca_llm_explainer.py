"""
大模型根因解释模块

支持SiliconFlow API（多种开源模型）
用于解释根因分析结果
"""

import os
import datetime
from typing import Dict, Optional
import pandas as pd


class LLMExplainer:
    """大模型解释器"""
    
    def __init__(self, 
                 api_key: str = None, 
                 model: str = None, 
                 base_url: str = None):
        """
        初始化大模型解释器
        
        Args:
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL（用于自定义API端点）
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
                f.write(f"Base URL: {self.base_url or '默认'}\n")
                f.write("\n" + "="*80 + "\n\n")
                f.write(prompt)
            
            print(f"[LLM] 提示词已保存到: {filename}")
            
        except Exception as e:
            print(f"[LLM] 保存提示词失败: {str(e)}")
    
    def _init_client(self):
        """初始化API客户端"""
        try:
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
            http_client = httpx.Client(proxy=None, verify=False)
            
            self.client = openai.OpenAI(
                api_key=self.api_key, 
                base_url=self.base_url or "https://api.siliconflow.cn/v1",
                http_client=http_client
            )
            
            print(f"[LLM] 客户端初始化成功")
            
        except ImportError as e:
            self.connection_error = f"未安装 openai SDK，请运行: pip install openai httpx"
            print(f"[LLM] ImportError: {self.connection_error}")
        except Exception as e:
            self.connection_error = f"初始化客户端失败: {str(e)}"
            print(f"[LLM] Exception: {self.connection_error}")
    
    def test_connection(self) -> tuple:
        """
        测试API连接是否可用
        
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息或成功消息)
        """
        if not self.client:
            error_msg = "客户端未初始化，请检查API密钥是否正确"
            print(f"[LLM] 连接测试失败: {error_msg}")
            return False, error_msg
        
        try:
            print(f"[LLM] 测试连接...")
            
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
            
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower() or "401" in error_msg:
                return False, f"API密钥无效或未授权，请检查密钥是否正确"
            elif "not found" in error_msg.lower() or "404" in error_msg:
                return False, f"API端点未找到，请检查Base URL是否正确"
            elif "model" in error_msg.lower() and "not" in error_msg.lower():
                return False, f"模型 {self.model} 不可用，请检查模型名称"
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                return False, f"API请求频率超限，请稍后再试"
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return False, f"网络连接失败，请检查网络"
            elif "insufficient" in error_msg.lower() or "quota" in error_msg.lower():
                return False, f"API配额不足，请检查账户余额"
            else:
                return False, f"连接测试失败: {error_msg}"
    
    def generate_explanation(self, 
                            analysis_results: pd.DataFrame,
                            comparison_df: pd.DataFrame,
                            causal_graph: str,
                            scenario_background: str = None) -> str:
        """
        生成根因分析解释
        
        Args:
            analysis_results: 根因分析结果DataFrame
            comparison_df: 指标对比数据
            causal_graph: 因果图（DOT格式字符串）
            scenario_background: 场景背景描述
            
        Returns:
            大模型生成的解释文本
        """
        prompt = self._build_prompt(analysis_results, comparison_df, causal_graph, scenario_background)
        
        if not self.client:
            print("[LLM] 客户端未初始化，无法生成解释")
            return "错误：大模型客户端未初始化，请检查API配置"
        
        try:
            print(f"[LLM] 生成解释...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的电商数据分析顾问，擅长利润分析和根因分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[LLM] 调用大模型API失败: {str(e)}")
            return f"错误：调用大模型API失败 - {str(e)}"
    
    def _build_prompt(self, 
                      analysis_results: pd.DataFrame,
                      comparison_df: pd.DataFrame,
                      causal_graph: str,
                      scenario_background: str = None) -> str:
        """构建提示词"""
        
        if not scenario_background:
            scenario_background = "某在线商店销售智能手机，零售价$999。2021年利润保持稳定，但在2022年初突然下降。需要分析利润下降的根本原因。"
        
        causal_graph_description = f"## 因果图结构\n\n```\n{causal_graph}\n```\n\n"
        
        prompt = f"""你是一个专业的电商数据分析顾问。请根据以下数据分析结果，给出详细的根因分析和改进建议。

## 场景背景
{scenario_background}

{causal_graph_description}

## 数据分析结果

### 1. 利润变化
"""
        
        if not comparison_df.empty:
            profit_row = comparison_df[comparison_df['variable'] == 'profit']
            if not profit_row.empty:
                change_percent = profit_row['change_percent'].values[0]
                prompt += f"- 利润变化: {change_percent:.2f}%\n"
        
        prompt += "\n### 2. 主要异常指标\n"
        
        if not comparison_df.empty:
            top_changes = comparison_df.head(5)
            for _, row in top_changes.iterrows():
                variable = row['variable'].replace('_', ' ').title()
                change = row['change_percent']
                prompt += f"- {variable}: 变化 {change:.2f}%\n"
        
        prompt += "\n### 3. 根因分析结果\n"
        
        if not analysis_results.empty:
            for _, row in analysis_results.iterrows():
                cause = row['cause'].replace('_', ' ').title()
                strength = row['abs_strength']
                prompt += f"- {cause}: 影响强度 {strength:.2e}\n"
        
        prompt += """

## 请回答以下问题：

1. **根因分析**：根据因果图结构和根因分析结果，哪些因素是导致利润下降的根本原因？为什么？

2. **因果路径分析**：请结合因果图结构，详细解释这些因素是如何通过因果链影响利润的。

3. **改进建议**：针对识别出的根本原因，应该采取哪些具体的改进措施？

请用专业但易懂的语言回答，适合企业管理层阅读。
"""
        
        self._save_prompt(prompt)
        
        return prompt
    
    def generate_improvement_suggestions(self,
                                         analysis_results: pd.DataFrame,
                                         causal_graph: str,
                                         scenario_description: str,
                                         problem_description: str) -> str:
        """
        生成改进建议
        
        Args:
            analysis_results: 根因分析结果DataFrame
            causal_graph: 因果图（DOT格式字符串）
            scenario_description: 场景描述
            problem_description: 问题描述
            
        Returns:
            大模型生成的改进建议文本
        """
        prompt = self._build_improvement_prompt(analysis_results, causal_graph, scenario_description, problem_description)
        
        if not self.client:
            print("[LLM] 客户端未初始化，无法生成改进建议")
            return "错误：大模型客户端未初始化，请检查API配置"
        
        try:
            print(f"[LLM] 生成改进建议...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的电商运营顾问，擅长根据数据分析结果提出改进建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[LLM] 调用大模型API失败: {str(e)}")
            return f"错误：调用大模型API失败 - {str(e)}"
    
    def _build_improvement_prompt(self,
                                  analysis_results: pd.DataFrame,
                                  causal_graph: str,
                                  scenario_description: str,
                                  problem_description: str) -> str:
        """构建改进建议提示词"""
        
        causal_graph_description = f"## 因果图结构\n\n```\n{causal_graph}\n```\n\n"
        
        prompt = f"""你是一个专业的电商运营顾问。请根据以下根因分析结果，给出具体的改进建议。

## 场景背景
{scenario_description}

## 问题描述
{problem_description}

{causal_graph_description}

## 根因分析结果

"""
        
        if not analysis_results.empty:
            for i, row in analysis_results.iterrows():
                cause = row['cause'].replace('_', ' ').title()
                strength = row['abs_strength']
                prompt += f"{i+1}. {cause}: 影响强度 {strength:.2e}\n"
        
        prompt += """

## 请回答以下问题：

1. **改进建议**：针对识别出的根本原因，应该采取哪些具体的改进措施？请按优先级排序，并说明每项措施的预期效果。

2. **实施路径**：请给出改进措施的实施路径，包括短期、中期和长期措施。

3. **风险评估**：实施这些改进措施可能面临哪些风险？如何规避？

4. **效果评估**：如何评估改进措施的效果？建议设置哪些监控指标？

请用专业但易懂的语言回答，适合企业管理层阅读。
"""
        
        self._save_prompt(prompt)
        
        return prompt


def create_explainer(api_key: str = None, model: str = None, base_url: str = None) -> LLMExplainer:
    """
    创建大模型解释器
    
    Args:
        api_key: API密钥
        model: 模型名称
        base_url: API基础URL
        
    Returns:
        LLMExplainer实例
    """
    return LLMExplainer(api_key=api_key, model=model, base_url=base_url)
