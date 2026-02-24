"""
根因分析管道模块

提供通用的DoWhy分析管道，支持完整的因果分析流程：
- 模型创建
- 效应估计
- 驳斥检验
- 反事实分析
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from causal_analyzer import CausalAnalyzer


class RootCauseAnalysisPipeline:
    """根因分析管道（通用版本）"""
    
    def __init__(self, 
                 data: pd.DataFrame,
                 causal_graph: str,
                 analysis_config: Optional[Dict] = None):
        """
        初始化根因分析管道
        
        Args:
            data: 分析数据
            causal_graph: 因果图（DOT格式字符串）
            analysis_config: 分析配置参数
        """
        self.data = data
        self.causal_graph = causal_graph
        self.config = analysis_config or {}
        self.analyzer = CausalAnalyzer(data)
        self.analysis_results = {}
    
    def run_full_analysis(self, 
                          treatment: str,
                          outcome: str,
                          target_outcome: Optional[float] = None) -> Dict:
        """
        运行完整的因果分析流程
        
        Args:
            treatment: 处理变量
            outcome: 结果变量
            target_outcome: 目标结果值（用于反事实分析）
        """
        results = {}
        
        # 1. 模型创建
        print("步骤1：创建因果模型")
        self.analyzer.create_causal_model(
            treatment=treatment,
            outcome=outcome,
            causal_graph=self.causal_graph
        )
        
        # 2. 效应估计
        print("步骤2：估计因果效应")
        self.analyzer.identify_effect()
        estimate = self.analyzer.estimate_effect()
        results["causal_effect"] = estimate.value
        
        # 3. 驳斥检验
        print("步骤3：执行驳斥检验")
        refutation_results = self.analyzer.refute_estimate()
        results["refutation_results"] = refutation_results
        
        # 4. 反事实分析
        if target_outcome is not None:
            print("步骤4：执行反事实分析")
            counterfactual_result = self.analyzer.counterfactual_analysis(
                treatment=treatment,
                outcome=outcome,
                target_outcome=target_outcome,
                causal_graph=self.causal_graph
            )
            results["counterfactual_analysis"] = counterfactual_result
        
        # 保存分析结果
        self.analysis_results = results
        
        return results
    
    def analyze_multiple_treatments(self, 
                                   treatments: List[str],
                                   outcome: str) -> pd.DataFrame:
        """
        分析多个处理变量对结果变量的因果效应
        
        Args:
            treatments: 处理变量列表
            outcome: 结果变量
        """
        print(f"分析多个处理变量对{outcome}的因果效应")
        
        # 使用CausalAnalyzer的analyze_causal_effects方法
        results_df = self.analyzer.analyze_causal_effects(
            causal_graph=self.causal_graph,
            treatments=treatments,
            outcome=outcome
        )
        
        return results_df
    
    def get_analysis_summary(self) -> Dict:
        """
        获取分析结果摘要
        """
        if not self.analysis_results:
            return {"message": "请先运行分析"}
        
        summary = {
            "causal_effect": self.analysis_results.get("causal_effect"),
            "has_refutation_results": "refutation_results" in self.analysis_results,
            "has_counterfactual_analysis": "counterfactual_analysis" in self.analysis_results
        }
        
        # 添加反事实分析摘要（如果存在）
        if "counterfactual_analysis" in self.analysis_results:
            cf_result = self.analysis_results["counterfactual_analysis"]
            summary["counterfactual_summary"] = {
                "treatment": cf_result["treatment"],
                "outcome": cf_result["outcome"],
                "current_outcome": cf_result["current_outcome"],
                "target_outcome": cf_result["target_outcome"],
                "required_treatment_change": cf_result["required_treatment_change"],
                "feasibility": cf_result["feasibility"]
            }
        
        return summary
