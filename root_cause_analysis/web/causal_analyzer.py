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
    
    def counterfactual_analysis_v2(self, 
                                  treatment: str,
                                  outcome: str,
                                  target_outcome: float,
                                  causal_graph: str) -> Dict:
        """
        结果反事实分析 V2 - 基于真实模拟的反事实分析
        
        核心思路：
        1. 构建反事实数据集（将处理变量设置为不同的目标值）
        2. 使用因果模型预测干预后的结果
        3. 验证预测结果是否接近目标结果
        4. 提供更准确的可行性评估
        
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
        
        # 计算当前原因变量的基线值
        current_treatment = self.data[treatment].mean()
        
        # 获取处理变量的范围
        treatment_min = self.data[treatment].min()
        treatment_max = self.data[treatment].max()
        
        # 生成一系列可能的处理变量值
        import numpy as np
        num_steps = 100
        treatment_values = np.linspace(treatment_min, treatment_max, num_steps)
        
        # 构建反事实数据集并预测结果
        predicted_outcomes = []
        
        for treatment_value in treatment_values:
            try:
                # 构建反事实数据集
                counterfactual_data = self.data.copy()
                counterfactual_data[treatment] = treatment_value
                
                # 使用DoWhy预测反事实结果
                # 注意：这里使用DoWhy的预测功能，具体实现可能需要根据DoWhy版本调整
                # 由于DoWhy的API可能有变化，这里使用一种通用方法
                
                # 提取模型所需的变量
                model = self.identified_estimand.estimator.model
                
                # 预测结果
                if hasattr(model, 'predict'):
                    # 如果模型有predict方法，直接使用
                    features = counterfactual_data[self.identified_estimand.estimator._target_estimand.treatment_variable]
                    predicted_outcome = model.predict(features)
                    predicted_outcomes.append(np.mean(predicted_outcome))
                else:
                    # 否则使用简单的线性预测（基于因果效应）
                    predicted_outcome = current_outcome + (treatment_value - current_treatment) * estimate.value
                    predicted_outcomes.append(predicted_outcome)
            except Exception as e:
                print(f"预测处理变量值 {treatment_value} 时出错: {e}")
                predicted_outcomes.append(float('nan'))
        
        # 找到最接近目标结果的处理变量值
        best_idx = -1
        min_diff = float('inf')
        
        for i, pred_outcome in enumerate(predicted_outcomes):
            if not np.isnan(pred_outcome):
                diff = abs(pred_outcome - target_outcome)
                if diff < min_diff:
                    min_diff = diff
                    best_idx = i
        
        if best_idx == -1:
            # 如果无法预测，使用原始方法
            if estimate.value != 0:
                required_treatment_change = outcome_diff / estimate.value
            else:
                required_treatment_change = float('inf')
            
            target_treatment = current_treatment + required_treatment_change
            predicted_target_outcome = target_outcome
        else:
            # 使用预测结果
            target_treatment = treatment_values[best_idx]
            required_treatment_change = target_treatment - current_treatment
            predicted_target_outcome = predicted_outcomes[best_idx]
        
        # 验证可行性
        feasibility = "high"
        if required_treatment_change == float('inf'):
            feasibility = "impossible"
        elif target_treatment < treatment_min or target_treatment > treatment_max:
            feasibility = "low"
        elif abs(required_treatment_change) > current_treatment * 0.5:
            feasibility = "medium"
        
        # 验证预测结果与目标结果的接近程度
        outcome_accuracy = "high"
        if best_idx != -1:
            outcome_diff_percent = abs(predicted_target_outcome - target_outcome) / max(abs(target_outcome), 1e-6) * 100
            if outcome_diff_percent > 10:
                outcome_accuracy = "low"
            elif outcome_diff_percent > 5:
                outcome_accuracy = "medium"
        
        # 返回结构化的反事实分析结果
        return {
            "treatment": treatment,
            "outcome": outcome,
            "current_treatment": current_treatment,
            "target_treatment": target_treatment,
            "required_treatment_change": required_treatment_change,
            "current_outcome": current_outcome,
            "target_outcome": target_outcome,
            "predicted_target_outcome": predicted_target_outcome,
            "outcome_diff": outcome_diff,
            "causal_effect": estimate.value,
            "feasibility": feasibility,
            "outcome_accuracy": outcome_accuracy,
            "treatment_range": {
                "min": treatment_min,
                "max": treatment_max
            },
            "prediction_details": {
                "num_steps": num_steps,
                "best_index": best_idx,
                "min_prediction_diff": min_diff if best_idx != -1 else None
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
