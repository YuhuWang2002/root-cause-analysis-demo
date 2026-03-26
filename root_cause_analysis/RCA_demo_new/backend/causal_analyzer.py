"""
因果分析模块 - 使用DoWhy进行因果推断分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    import dowhy
    from dowhy import CausalModel
    DOWHY_AVAILABLE = True
except ImportError:
    DOWHY_AVAILABLE = False


class InventoryCausalAnalyzer:
    """库存因果分析器"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.model = None
        self.identified_estimand = None
        self.estimate = None
        self.refutation_results = {}

    def create_causal_model(self,
                           treatment: str = "server_2288hv7_uses_pac900s12_b2_1",
                           outcome: str = "pac900s12_b2_1_inventory",
                           causal_graph: str = None) -> 'CausalModel':
        if causal_graph is None:
            causal_graph = """digraph {
            kunlun_2280_sales -> pac900s12_b2_1_consumption;
            server_2288hv7_sales -> pac900s12_b2_1_consumption;
            server_2288hv7_uses_pac900s12_b2_1 -> pac900s12_b2_1_consumption;
            pac900s12_b2_1_consumption -> pac900s12_b2_1_inventory;
            pac900s12_b2_1_procurement -> pac900s12_b2_1_inventory;
            kunlun_2280_sales -> pac900s12_b2_1_procurement;
        }"""

        if not DOWHY_AVAILABLE:
            raise ImportError("DoWhy is not installed. Please install it with: pip install dowhy")

        self.model = CausalModel(
            data=self.data,
            treatment=treatment,
            outcome=outcome,
            graph=causal_graph,
            logging_level='WARNING'
        )

        return self.model

    def identify_effect(self):
        if self.model is None:
            raise ValueError("请先创建因果模型")

        self.identified_estimand = self.model.identify_effect(proceed_when_unidentifiable=True)
        return self.identified_estimand

    def estimate_effect(self, method_name: str = "backdoor.linear_regression"):
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
                    "new_effect": float(placebo_ref.new_effect),
                    "p_value": float(placebo_ref.refutation_result['p_value']),
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
                    "new_effect": float(random_ref.new_effect),
                    "p_value": float(random_ref.refutation_result['p_value']),
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
                    "new_effect": float(subset_ref.new_effect),
                    "p_value": float(subset_ref.refutation_result['p_value']),
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
        actual_inventory = self.data[outcome].mean()
        counterfactual_inventory = counterfactual_data[outcome].mean()

        inventory_reduction = actual_inventory - counterfactual_inventory
        reduction_percentage = (inventory_reduction / actual_inventory) * 100

        decline_period_actual = self.data[self.data['is_decline_period'] == True][outcome].mean()
        decline_period_counterfactual = counterfactual_data[counterfactual_data['is_decline_period'] == True][outcome].mean()
        decline_period_reduction = decline_period_actual - decline_period_counterfactual

        return {
            "actual_inventory_mean": float(actual_inventory),
            "counterfactual_inventory_mean": float(counterfactual_inventory),
            "inventory_reduction": float(inventory_reduction),
            "reduction_percentage": float(reduction_percentage),
            "decline_period_actual_inventory": float(decline_period_actual),
            "decline_period_counterfactual_inventory": float(decline_period_counterfactual),
            "decline_period_reduction": float(decline_period_reduction),
            "is_root_cause": bool(reduction_percentage > 20)
        }

    def analyze_causal_effects(self,
                              treatments: List[str],
                              outcome: str = "pac900s12_b2_1_inventory") -> pd.DataFrame:
        results = []

        for treatment in treatments:
            try:
                if treatment not in self.data.columns:
                    continue

                if outcome not in self.data.columns:
                    continue

                self.create_causal_model(treatment=treatment, outcome=outcome)
                self.identify_effect()
                estimate = self.estimate_effect()

                causal_effect = estimate.value if estimate.value is not None else 0.0

                results.append({
                    "treatment": treatment,
                    "causal_effect": float(causal_effect),
                    "abs_causal_effect": abs(float(causal_effect)),
                    "success": True
                })

            except Exception as e:
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
        if treatments is None:
            treatments = ["server_2288hv7_uses_pac900s12_b2_1", "kunlun_2280_sales", "server_2288hv7_sales"]

        self.create_causal_model(treatment="server_2288hv7_uses_pac900s12_b2_1", outcome=outcome, causal_graph=causal_graph)

        self.identify_effect()

        estimate = self.estimate_effect()

        if fast_mode:
            refutation_results = {}
            # causal_effects_df = pd.DataFrame([{
            #     "treatment": "server_2288hv7_uses_pac900s12_b2_1",
            #     "causal_effect": float(estimate.value),
            #     "note": "快速模式"
            # }])
            causal_effects_df = self.analyze_causal_effects(treatments, outcome)
        else:
            refutation_results = self.refute_estimate()
            causal_effects_df = self.analyze_causal_effects(treatments, outcome)

        counterfactual_results = self.counterfactual_analysis(counterfactual_data)

        return {
            "causal_effect": float(estimate.value) if estimate.value is not None else 0.0,
            "refutation_results": refutation_results,
            "counterfactual_analysis": counterfactual_results,
            "causal_effects": causal_effects_df.to_dict('records') if not causal_effects_df.empty else [],
            "treatments": treatments,
            "outcome": outcome
        }
