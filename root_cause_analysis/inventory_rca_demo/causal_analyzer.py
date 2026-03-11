"""
PAC900S12-B2-1库存高因果根因分析 - 因果分析模块

使用DoWhy进行因果推断分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

import dowhy
from dowhy import CausalModel


class InventoryCausalAnalyzer:
    """PAC900S12-B2-1库存因果分析器"""
    
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
                           treatment: str = "server_2288hv7_uses_pac900s12_b2_1",
                           outcome: str = "pac900s12_b2_1_inventory",
                           causal_graph: str = None) -> CausalModel:
        """
        创建因果模型
        
        Args:
            treatment: 处理变量（2288HV7是否使用PAC900S12-B2-1）
            outcome: 结果变量（PAC900S12-B2-1库存）
            causal_graph: 因果图（DOT格式），如果为None则使用默认因果图
            
        Returns:
            DoWhy因果模型
        """
        if causal_graph is None:
            causal_graph = """digraph {
            kunlun_2280_sales -> pac900s12_b2_1_consumption;
            server_2288hv7_sales -> pac900s12_b2_1_consumption;
            server_2288hv7_uses_pac900s12_b2_1 -> pac900s12_b2_1_consumption;
            pac900s12_b2_1_consumption -> pac900s12_b2_1_inventory;
            pac900s12_b2_1_procurement -> pac900s12_b2_1_inventory;
            kunlun_2280_sales -> pac900s12_b2_1_procurement;
        }"""
        
        self.model = CausalModel(
            data=self.data,
            treatment=treatment,
            outcome=outcome,
            graph=causal_graph,
            logging_level='INFO'
        )
        
        return self.model
    
    def identify_effect(self):
        """
        识别因果效应
        
        Returns:
            识别的因果估计量
        """
        if self.model is None:
            raise ValueError("请先创建因果模型")
        
        self.identified_estimand = self.model.identify_effect(proceed_when_unidentifiable=True)
        
        return self.identified_estimand
    
    def estimate_effect(self, method_name: str = "backdoor.linear_regression"):
        """
        估计因果效应
        
        Args:
            method_name: 估计方法名称
            
        Returns:
            因果效应估计结果
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
        
        Args:
            placebo_refutation: 是否进行安慰剂检验
            random_common_cause: 是否进行随机共同原因检验
            data_subset_refuter: 是否进行数据子集检验
            
        Returns:
            驳斥检验结果字典
        """
        if self.estimate is None:
            raise ValueError("请先估计因果效应")
        
        results = {}
        
        if placebo_refutation:
            try:
                placebo_ref = self.model.refute_estimate(
                    self.identified_estimand,
                    self.estimate,
                    method_name="placebo_treatment_refuter"
                )
                results["placebo"] = {
                    "new_effect": placebo_ref.new_effect,
                    "p_value": placebo_ref.refutation_result['p_value'],
                    "is_statistically_significant": abs(placebo_ref.new_effect) < 0.1
                }
            except Exception as e:
                results["placebo"] = {"error": str(e)}
        
        if random_common_cause:
            try:
                random_ref = self.model.refute_estimate(
                    self.identified_estimand,
                    self.estimate,
                    method_name="random_common_cause"
                )
                results["random_common_cause"] = {
                    "new_effect": random_ref.new_effect,
                    "p_value": random_ref.refutation_result['p_value'],
                    "is_robust": abs(random_ref.new_effect - self.estimate.value) < 0.1
                }
            except Exception as e:
                results["random_common_cause"] = {"error": str(e)}
        
        if data_subset_refuter:
            try:
                subset_ref = self.model.refute_estimate(
                    self.identified_estimand,
                    self.estimate,
                    method_name="data_subset_refuter",
                    subset_fraction=0.8
                )
                results["data_subset"] = {
                    "new_effect": subset_ref.new_effect,
                    "p_value": subset_ref.refutation_result['p_value'],
                    "is_robust": abs(subset_ref.new_effect - self.estimate.value) < 0.1
                }
            except Exception as e:
                results["data_subset"] = {"error": str(e)}
        
        self.refutation_results = results
        return results
    
    def counterfactual_analysis(self,
                               counterfactual_data: pd.DataFrame,
                               treatment: str = "server_2288hv7_uses_pac900s12_b2_1",
                               outcome: str = "pac900s12_b2_1_inventory") -> Dict:
        """
        反事实分析 - 比较实际库存与反事实库存
        
        Args:
            counterfactual_data: 反事实数据（2288HV7使用PAC900S12-B2）
            treatment: 处理变量
            outcome: 结果变量
            
        Returns:
            反事实分析结果
        """
        actual_inventory = self.data[outcome].mean()
        counterfactual_inventory = counterfactual_data[outcome].mean()
        
        inventory_reduction = actual_inventory - counterfactual_inventory
        reduction_percentage = (inventory_reduction / actual_inventory) * 100
        
        decline_period_actual = self.data[self.data['is_decline_period'] == True][outcome].mean()
        decline_period_counterfactual = counterfactual_data[counterfactual_data['is_decline_period'] == True][outcome].mean()
        decline_period_reduction = decline_period_actual - decline_period_counterfactual
        
        return {
            "actual_inventory_mean": actual_inventory,
            "counterfactual_inventory_mean": counterfactual_inventory,
            "inventory_reduction": inventory_reduction,
            "reduction_percentage": reduction_percentage,
            "decline_period_actual_inventory": decline_period_actual,
            "decline_period_counterfactual_inventory": decline_period_counterfactual,
            "decline_period_reduction": decline_period_reduction,
            "is_root_cause": reduction_percentage > 20
        }
    
    def analyze_causal_effects(self,
                              treatments: List[str],
                              outcome: str = "pac900s12_b2_1_inventory") -> pd.DataFrame:
        """
        分析多个处理变量对结果变量的因果效应
        
        Args:
            treatments: 处理变量列表
            outcome: 结果变量
            
        Returns:
            因果效应分析结果DataFrame
        """
        results = []
        
        for treatment in treatments:
            try:
                if treatment not in self.data.columns:
                    print(f"处理变量 {treatment} 不在数据中")
                    continue
                
                if outcome not in self.data.columns:
                    print(f"结果变量 {outcome} 不在数据中")
                    continue
                
                self.create_causal_model(treatment=treatment, outcome=outcome)
                self.identify_effect()
                estimate = self.estimate_effect()
                
                causal_effect = estimate.value if estimate.value is not None else 0.0
                
                results.append({
                    "treatment": treatment,
                    "causal_effect": causal_effect,
                    "abs_causal_effect": abs(causal_effect),
                    "success": True
                })
                
            except Exception as e:
                print(f"分析处理变量 {treatment} 时出错: {str(e)}")
                results.append({
                    "treatment": treatment,
                    "causal_effect": 0.0,
                    "abs_causal_effect": 0.0,
                    "success": False,
                    "error": str(e)
                })
        
        results_df = pd.DataFrame(results)
        
        if not results_df.empty and 'abs_causal_effect' in results_df.columns:
            results_df = results_df.sort_values('abs_causal_effect', ascending=False)
            results_df['rank'] = range(1, len(results_df) + 1)
        
        return results_df
    
    def run_full_analysis(self,
                         counterfactual_data: pd.DataFrame,
                         treatments: List[str] = None,
                         outcome: str = "pac900s12_b2_1_inventory",
                         fast_mode: bool = False,
                         causal_graph: str = None) -> Dict:
        """
        运行完整的因果分析流程
        
        Args:
            counterfactual_data: 反事实数据
            treatments: 处理变量列表
            outcome: 结果变量
            fast_mode: 快速模式（跳过驳斥检验和多变量分析）
            causal_graph: 因果图（DOT格式），如果为None则使用默认因果图
            
        Returns:
            完整分析结果字典
        """
        if treatments is None:
            treatments = ["server_2288hv7_uses_pac900s12_b2_1", "kunlun_2280_sales", "server_2288hv7_sales"]
        
        print("步骤1: 创建因果模型...")
        self.create_causal_model(treatment="server_2288hv7_uses_pac900s12_b2_1", outcome=outcome, causal_graph=causal_graph)
        
        print("步骤2: 识别因果效应...")
        self.identify_effect()
        
        print("步骤3: 估计因果效应...")
        estimate = self.estimate_effect()
        
        if fast_mode:
            print("快速模式：跳过驳斥检验和多变量分析")
            refutation_results = {}
            causal_effects_df = pd.DataFrame([{
                "treatment": "server_2288hv7_uses_pac900s12_b2_1",
                "causal_effect": estimate.value,
                "note": "快速模式"
            }])
        else:
            print("步骤4: 驳斥检验...")
            refutation_results = self.refute_estimate()
            
            print("步骤6: 分析多个处理变量...")
            causal_effects_df = self.analyze_causal_effects(treatments, outcome)
        
        print("步骤5: 反事实分析...")
        counterfactual_results = self.counterfactual_analysis(counterfactual_data)
        
        return {
            "causal_effect": estimate.value,
            "refutation_results": refutation_results,
            "counterfactual_analysis": counterfactual_results,
            "causal_effects": causal_effects_df.to_dict('records'),
            "treatments": treatments,
            "outcome": outcome
        }


if __name__ == "__main__":
    from data_generator import create_inventory_scenario
    
    actual_data, counterfactual_data = create_inventory_scenario()
    
    analyzer = InventoryCausalAnalyzer(data=actual_data)
    
    results = analyzer.run_full_analysis(counterfactual_data)
    
    print("\n=== 因果分析结果 ===")
    print(f"因果效应值: {results['causal_effect']:.4f}")
    
    print("\n=== 驳斥检验结果 ===")
    for test_name, result in results['refutation_results'].items():
        print(f"{test_name}: {result}")
    
    print("\n=== 反事实分析结果 ===")
    cf_results = results['counterfactual_analysis']
    print(f"实际库存均值: {cf_results['actual_inventory_mean']:.2f}")
    print(f"反事实库存均值: {cf_results['counterfactual_inventory_mean']:.2f}")
    print(f"库存降低: {cf_results['inventory_reduction']:.2f} ({cf_results['reduction_percentage']:.2f}%)")
    print(f"是否为根因: {cf_results['is_root_cause']}")
    
    print("\n=== 多变量因果效应分析 ===")
    effects_df = pd.DataFrame(results['causal_effects'])
    print(effects_df)
