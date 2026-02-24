"""
因果分析器模块

提供通用的DoWhy因果分析功能，支持：
- 因果模型创建
- 因果效应估计
- 驳斥检验
- 结果反事实分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

import dowhy
from dowhy import CausalModel


class CausalAnalyzer:
    """因果分析器（通用版本）"""
    
    def __init__(self, data: pd.DataFrame):
        """
        初始化因果分析器
        
        Args:
            data: 分析数据
        """
        self.data = data
        self.model = None
        self.identified_estimand = None
        self.estimate = None
        self.refutation_results = {}
    
    def create_causal_model(self, 
                            treatment: str, 
                            outcome: str,
                            causal_graph: str,
                            confounders: List[str] = None) -> CausalModel:
        """
        创建因果模型
        
        Args:
            treatment: 处理变量
            outcome: 结果变量
            causal_graph: 因果图（DOT格式字符串）
            confounders: 混淆变量列表
        """
        data_subset = self.data.copy()
        
        if confounders is None:
            confounders = []
        
        self.model = CausalModel(
            data=data_subset,
            treatment=treatment,
            outcome=outcome,
            graph=causal_graph,
            logging_level='INFO'
        )
        
        return self.model
    
    def identify_effect(self) -> object:
        """
        识别因果效应
        """
        if self.model is None:
            raise ValueError("请先创建因果模型")
        
        self.identified_estimand = self.model.identify_effect(proceed_when_unidentifiable=True)
        
        return self.identified_estimand
    
    def estimate_effect(self, method_name: str = "backdoor.linear_regression") -> object:
        """
        估计因果效应
        
        Args:
            method_name: 估计方法名称
        """
        if self.identified_estimand is None:
            raise ValueError("请先识别因果效应")
        
        self.estimate = self.model.estimate_effect(
            self.identified_estimand,
            method_name=method_name
        )
        
        return self.estimate
    
    def refute_estimate(self, 
                        placebo_refutation: bool = True,
                        random_common_cause: bool = True,
                        data_subset_refuter: bool = True) -> Dict:
        """
        驳斥检验 - 验证因果推断的稳健性
        """
        if self.estimate is None:
            raise ValueError("请先估计因果效应")
        
        results = {}
        
        if placebo_refutation:
            placebo_ref = self.model.refute_estimate(
                self.identified_estimand,
                self.estimate,
                method_name="placebo_treatment_refuter"
            )
            results["placebo"] = placebo_ref
        
        if random_common_cause:
            random_ref = self.model.refute_estimate(
                self.identified_estimand,
                self.estimate,
                method_name="random_common_cause"
            )
            results["random_common_cause"] = random_ref
        
        if data_subset_refuter:
            subset_ref = self.model.refute_estimate(
                self.identified_estimand,
                self.estimate,
                method_name="data_subset_refuter",
                subset_fraction=0.8
            )
            results["data_subset"] = subset_ref
        
        self.refutation_results = results
        return results
    
    def counterfactual_analysis(self, 
                                treatment: str,
                                outcome: str,
                                target_outcome: float,
                                causal_graph: str) -> Dict:
        """
        结果反事实分析 - 计算达到目标结果需要的原因变量变化
        
        Args:
            treatment: 处理变量（原因）
            outcome: 结果变量
            target_outcome: 目标结果值
            causal_graph: 因果图（DOT格式字符串）
        """
        # 创建因果模型
        self.create_causal_model(
            treatment=treatment,
            outcome=outcome,
            causal_graph=causal_graph
        )
        
        # 识别因果效应
        self.identify_effect()
        
        # 估计因果效应
        estimate = self.estimate_effect()
        
        # 计算当前结果的基线值
        current_outcome = self.data[outcome].mean()
        
        # 计算目标结果与基线值的差异
        outcome_diff = target_outcome - current_outcome
        
        # 根据因果效应，计算需要的原因变量变化
        if estimate.value != 0:
            required_treatment_change = outcome_diff / estimate.value
        else:
            required_treatment_change = float('inf')  # 无法计算
        
        # 计算当前原因变量的基线值
        current_treatment = self.data[treatment].mean()
        
        # 计算目标原因变量值
        target_treatment = current_treatment + required_treatment_change
        
        # 验证可行性
        treatment_min = self.data[treatment].min()
        treatment_max = self.data[treatment].max()
        
        feasibility = "high"
        if required_treatment_change == float('inf'):
            feasibility = "impossible"
        elif target_treatment < treatment_min or target_treatment > treatment_max:
            feasibility = "low"
        elif abs(required_treatment_change) > current_treatment * 0.5:
            feasibility = "medium"
        
        # 返回结构化的反事实分析结果
        return {
            "treatment": treatment,
            "outcome": outcome,
            "current_treatment": current_treatment,
            "target_treatment": target_treatment,
            "required_treatment_change": required_treatment_change,
            "current_outcome": current_outcome,
            "target_outcome": target_outcome,
            "outcome_diff": outcome_diff,
            "causal_effect": estimate.value,
            "feasibility": feasibility,
            "treatment_range": {
                "min": treatment_min,
                "max": treatment_max
            }
        }
    
    def analyze_causal_effects(self, 
                              causal_graph: str,
                              treatments: List[str],
                              outcome: str) -> pd.DataFrame:
        """
        分析多个处理变量对结果变量的因果效应
        
        Args:
            causal_graph: 因果图（DOT格式字符串）
            treatments: 处理变量列表
            outcome: 结果变量
        """
        results = []
        
        for treatment in treatments:
            try:
                # 创建因果模型
                self.create_causal_model(
                    treatment=treatment,
                    outcome=outcome,
                    causal_graph=causal_graph
                )
                
                # 识别因果效应
                self.identify_effect()
                
                # 估计因果效应
                estimate = self.estimate_effect()
                
                results.append({
                    "treatment": treatment,
                    "causal_effect": estimate.value,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "treatment": treatment,
                    "causal_effect": None,
                    "success": False,
                    "error": str(e)
                })
        
        return pd.DataFrame(results)
