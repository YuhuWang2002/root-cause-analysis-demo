"""
制造企业根因分析 - 库存死货问题因果分析模块

因果图结构：
- 需求下降 -> 死库存
- 替代部件意识缺失 -> 死库存
- 库存管理问题 -> 死库存
- 部件成本 -> 资金占用
- 死库存 -> 资金占用
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

import dowhy
from dowhy import CausalModel


class InventoryCausalAnalyzer:
    """库存死货问题因果分析器"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.model = None
        self.identified_estimand = None
        self.estimate = None
        self.refutation_results = {}
        
    def build_causal_graph(self) -> str:
        """
        构建库存死货问题的因果图
        
        因果关系说明：
        1. 需求因素 (demand_factor) 影响死库存
        2. 替代部件意识 (substitute_awareness) 影响死库存
        3. 库存周转率 (stock_turnover) 影响死库存
        4. 死库存 (dead_stock_amount) 影响资金占用
        5. 部件成本 (part_unit_cost) 影响资金占用
        6. 初始库存 (initial_stock) 影响死库存
        7. 最小库存 (min_stock) 影响死库存
        """
        causal_graph = """digraph {
            demand_factor -> dead_stock_amount;
            substitute_awareness -> dead_stock_amount;
            stock_turnover -> dead_stock_amount;
            dead_stock_amount -> capital_tied;
            part_unit_cost -> capital_tied;
            initial_stock -> dead_stock_amount;
            min_stock -> dead_stock_amount;
            has_substitute -> substitute_awareness;
            substitute_awareness -> stock_turnover;
            demand_factor -> stock_turnover;
        }"""
        return causal_graph
    
    def create_causal_model(self, 
                            treatment: str, 
                            outcome: str,
                            confounders: List[str] = None) -> CausalModel:
        """
        创建因果模型
        
        Args:
            treatment: 处理变量
            outcome: 结果变量
            confounders: 混淆变量列表
        """
        causal_graph = self.build_causal_graph()
        
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
        """识别因果效应"""
        if self.model is None:
            raise ValueError("请先创建因果模型")
        
        self.identified_estimand = self.model.identify_effect(proceed_when_unidentifiable=True)
        print("\n=== 因果效应识别结果 ===")
        print(self.identified_estimand)
        
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
        
        print(f"\n=== 因果效应估计结果 ({method_name}) ===")
        print(f"估计值: {self.estimate.value}")
        
        return self.estimate
    
    def refute_estimate(self, 
                        placebo_refutation: bool = True,
                        random_common_cause: bool = True,
                        data_subset_refuter: bool = True) -> Dict:
        """
        驳斥检验 - 验证因果估计的稳健性
        """
        if self.estimate is None:
            raise ValueError("请先估计因果效应")
        
        results = {}
        
        if placebo_refutation:
            print("\n=== 安慰剂驳斥检验 ===")
            placebo_ref = self.model.refute_estimate(
                self.identified_estimand,
                self.estimate,
                method_name="placebo_treatment_refuter"
            )
            print(placebo_ref)
            results["placebo"] = placebo_ref
        
        if random_common_cause:
            print("\n=== 随机共同原因驳斥检验 ===")
            random_ref = self.model.refute_estimate(
                self.identified_estimand,
                self.estimate,
                method_name="random_common_cause"
            )
            print(random_ref)
            results["random_common_cause"] = random_ref
        
        if data_subset_refuter:
            print("\n=== 数据子集驳斥检验 ===")
            subset_ref = self.model.refute_estimate(
                self.identified_estimand,
                self.estimate,
                method_name="data_subset_refuter",
                subset_fraction=0.8
            )
            print(subset_ref)
            results["data_subset"] = subset_ref
        
        self.refutation_results = results
        return results
    
    def analyze_root_cause(self, 
                           target_variable: str = "dead_stock_amount",
                           potential_causes: List[str] = None) -> pd.DataFrame:
        """
        分析根因 - 对多个潜在原因进行因果分析
        
        Args:
            target_variable: 目标变量
            potential_causes: 潜在原因列表
        """
        if potential_causes is None:
            potential_causes = [
                "demand_factor",
                "substitute_awareness",
                "stock_turnover",
                "initial_stock",
                "min_stock"
            ]
        
        results = []
        
        for cause in potential_causes:
            print(f"\n{'='*60}")
            print(f"分析处理变量: {cause} -> {target_variable}")
            print('='*60)
            
            try:
                self.create_causal_model(
                    treatment=cause,
                    outcome=target_variable
                )
                
                self.identify_effect()
                
                estimate = self.estimate_effect()
                
                results.append({
                    "cause": cause,
                    "causal_effect": estimate.value,
                    "interpretation": self._interpret_effect(cause, estimate.value)
                })
                
            except Exception as e:
                print(f"分析 {cause} 时出错: {str(e)}")
                results.append({
                    "cause": cause,
                    "causal_effect": None,
                    "interpretation": f"分析失败: {str(e)}"
                })
        
        return pd.DataFrame(results).sort_values(
            by="causal_effect", 
            key=lambda x: abs(x) if x.notna().all() else x,
            ascending=False
        )
    
    def analyze_capital_impact(self) -> pd.DataFrame:
        """
        分析对资金占用的影响
        """
        results = []
        
        causes = ["dead_stock_amount", "part_unit_cost"]
        
        for cause in causes:
            print(f"\n{'='*60}")
            print(f"分析处理变量: {cause} -> capital_tied")
            print('='*60)
            
            try:
                self.create_causal_model(
                    treatment=cause,
                    outcome="capital_tied"
                )
                
                self.identify_effect()
                
                estimate = self.estimate_effect()
                
                results.append({
                    "cause": cause,
                    "causal_effect": estimate.value,
                    "interpretation": self._interpret_capital_effect(cause, estimate.value)
                })
                
            except Exception as e:
                print(f"分析 {cause} 时出错: {str(e)}")
                results.append({
                    "cause": cause,
                    "causal_effect": None,
                    "interpretation": f"分析失败: {str(e)}"
                })
        
        return pd.DataFrame(results).sort_values(
            by="causal_effect", 
            key=lambda x: abs(x) if x.notna().all() else x,
            ascending=False
        )
    
    def _interpret_effect(self, cause: str, effect: float) -> str:
        """解释因果效应"""
        if effect is None:
            return "无法计算"
        
        abs_effect = abs(effect)
        
        if abs_effect > 10:
            strength = "强"
        elif abs_effect > 5:
            strength = "中等"
        else:
            strength = "弱"
        
        direction = "正向" if effect > 0 else "负向"
        
        cause_names = {
            "demand_factor": "需求因素",
            "substitute_awareness": "替代部件意识",
            "stock_turnover": "库存周转率",
            "initial_stock": "初始库存",
            "min_stock": "最小库存"
        }
        
        cause_name = cause_names.get(cause, cause)
        
        return f"{cause_name}对死库存有{strength}的{direction}影响 (效应值: {effect:.4f})"
    
    def _interpret_capital_effect(self, cause: str, effect: float) -> str:
        """解释资金占用的因果效应"""
        if effect is None:
            return "无法计算"
        
        abs_effect = abs(effect)
        
        if abs_effect > 100:
            strength = "强"
        elif abs_effect > 50:
            strength = "中等"
        else:
            strength = "弱"
        
        direction = "正向" if effect > 0 else "负向"
        
        cause_names = {
            "dead_stock_amount": "死库存数量",
            "part_unit_cost": "部件单位成本"
        }
        
        cause_name = cause_names.get(cause, cause)
        
        return f"{cause_name}对资金占用有{strength}的{direction}影响 (效应值: {effect:.4f})"


class InventoryRootCauseAnalysisPipeline:
    """库存死货问题根因分析流水线"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.analyzer = InventoryCausalAnalyzer(data)
        self.analysis_results = None
        self.capital_analysis_results = None
        
    def run_full_analysis(self) -> Dict:
        """运行完整的根因分析"""
        print("="*70)
        print("制造企业库存死货问题根因分析")
        print("="*70)
        
        print("\n第一步：数据概览")
        self._print_data_overview()
        
        print("\n第二步：对比分析（正常月份 vs 异常月份）")
        comparison = self._compare_periods()
        
        print("\n第三步：死库存根因分析")
        self.analysis_results = self.analyzer.analyze_root_cause()
        
        print("\n第四步：资金占用影响分析")
        self.capital_analysis_results = self.analyzer.analyze_capital_impact()
        
        print("\n第五步：根因总结")
        summary = self._generate_summary(comparison)
        
        return {
            "comparison": comparison,
            "causal_analysis": self.analysis_results,
            "capital_analysis": self.capital_analysis_results,
            "summary": summary
        }
    
    def _print_data_overview(self):
        """打印数据概览"""
        print(f"数据记录数: {len(self.data)}")
        print(f"时间范围: {self.data['date'].min()} 到 {self.data['date'].max()}")
        print(f"工厂数量: {self.data['factory_id'].nunique()}")
        print(f"产品数量: {self.data['product_id'].nunique()}")
        print(f"部件数量: {self.data['part_id'].nunique()}")
        
        print("\n各月份死库存统计：")
        monthly_stats = self.data.groupby(['year', 'month']).agg({
            'dead_stock_amount': ['mean', 'sum'],
            'capital_tied': ['mean', 'sum'],
            'stock_turnover': 'mean'
        }).round(2)
        print(monthly_stats)
    
    def _compare_periods(self) -> pd.DataFrame:
        """对比正常月份和异常月份"""
        normal_data = self.data[~self.data['is_anomaly_month']]
        anomaly_data = self.data[self.data['is_anomaly_month']]
        
        metrics = [
            'dead_stock_amount',
            'capital_tied',
            'stock_turnover',
            'substitute_awareness',
            'demand_factor',
            'current_stock'
        ]
        
        comparison = []
        for metric in metrics:
            normal_mean = normal_data[metric].mean()
            anomaly_mean = anomaly_data[metric].mean()
            change = (anomaly_mean - normal_mean) / normal_mean * 100
            
            comparison.append({
                'metric': metric,
                'normal_mean': normal_mean,
                'anomaly_mean': anomaly_mean,
                'change_percent': change,
                'abs_change': abs(change)
            })
        
        comparison_df = pd.DataFrame(comparison).sort_values('abs_change', ascending=False)
        
        print("\n指标对比：")
        print(comparison_df.to_string(index=False))
        
        return comparison_df
    
    def _generate_summary(self, comparison: pd.DataFrame) -> str:
        """生成根因分析总结"""
        summary_lines = []
        summary_lines.append("\n" + "="*70)
        summary_lines.append("库存死货问题根因分析总结")
        summary_lines.append("="*70)
        
        dead_stock_change = comparison[comparison['metric'] == 'dead_stock_amount']['change_percent'].values[0]
        capital_change = comparison[comparison['metric'] == 'capital_tied']['change_percent'].values[0]
        
        summary_lines.append(f"\n死库存变化: {dead_stock_change:.2f}%")
        summary_lines.append(f"资金占用变化: {capital_change:.2f}%")
        
        if dead_stock_change > 0:
            summary_lines.append("\n主要问题原因（按影响程度排序）：")
            
            # 构建条件：对于替代部件意识和库存周转率，看下降；其他看上升
            condition = (comparison['metric'] != 'dead_stock_amount') & (comparison['metric'] != 'capital_tied') & (((comparison['metric'].isin(['substitute_awareness', 'stock_turnover'])) & (comparison['change_percent'] < 0)) | ((~comparison['metric'].isin(['substitute_awareness', 'stock_turnover'])) & (comparison['change_percent'] > 0)))
            top_causes = comparison[condition].head(3)
            
            for idx, row in top_causes.iterrows():
                summary_lines.append(f"  - {row['metric']}: {'下降' if row['change_percent'] < 0 else '上升'} {abs(row['change_percent']):.2f}%")
        
        if self.analysis_results is not None and len(self.analysis_results) > 0:
            summary_lines.append("\n死库存因果效应分析结果：")
            for _, row in self.analysis_results.head(3).iterrows():
                if row['causal_effect'] is not None:
                    summary_lines.append(f"  - {row['interpretation']}")
        
        if self.capital_analysis_results is not None and len(self.capital_analysis_results) > 0:
            summary_lines.append("\n资金占用影响分析结果：")
            for _, row in self.capital_analysis_results.head(2).iterrows():
                if row['causal_effect'] is not None:
                    summary_lines.append(f"  - {row['interpretation']}")
        
        summary_lines.append("\n建议措施：")
        if len(comparison[comparison['metric'] == 'substitute_awareness']) > 0:
            awareness_change = comparison[comparison['metric'] == 'substitute_awareness']['change_percent'].values[0]
            if awareness_change < -50:
                summary_lines.append("  1. 建立部件替代关系数据库，提高生产工厂对替代部件的认知")
                summary_lines.append("  2. 实施智能库存管理系统，自动推荐替代部件")
        
        if len(comparison[comparison['metric'] == 'demand_factor']) > 0:
            demand_change = comparison[comparison['metric'] == 'demand_factor']['change_percent'].values[0]
            if demand_change < -20:
                summary_lines.append("  3. 加强市场需求预测，优化采购计划")
                summary_lines.append("  4. 建立灵活的生产计划调整机制")
        
        summary_lines.append("  5. 定期清理死库存，制定合理的库存周转目标")
        summary_lines.append("  6. 建立跨部门协作机制，共享库存和生产信息")
        
        return "\n".join(summary_lines)
