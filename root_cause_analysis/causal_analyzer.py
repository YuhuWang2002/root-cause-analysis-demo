"""
制造企业根因分析 - DoWhy因果分析模块

因果图结构：
- 付款及时性 -> 供应商效率 -> 零部件可用性 -> 生产效率
- 供应商类型 -> 供应商效率
- 员工技能 -> 生产效率
- 设备状态 -> 生产效率
- 产能利用率 -> 生产效率
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

import dowhy
from dowhy import CausalModel


class CausalAnalyzer:
    """因果分析器"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.model = None
        self.identified_estimand = None
        self.estimate = None
        self.refutation_results = {}
        
    def build_causal_graph(self) -> str:
        """
        构建因果图的DOT格式定义
        
        因果关系说明：
        1. 付款及时性 (payment_timeliness) 影响供应商效率
        2. 供应商效率 (supplier_efficiency) 影响零部件可用性
        3. 零部件可用性 (parts_availability) 影响生产效率
        4. 员工技能 (avg_employee_skill) 影响生产效率
        5. 设备状态 (equipment_status) 影响生产效率
        6. 产能利用率 (capacity_utilization) 影响生产效率
        7. 供应商基础效率 (supplier_base_efficiency) 影响供应商效率
        8. 设备年龄 (equipment_age) 影响设备状态
        """
        causal_graph = """digraph {
            payment_timeliness -> supplier_efficiency;
            supplier_efficiency -> parts_availability;
            parts_availability -> production_efficiency;
            avg_employee_skill -> production_efficiency;
            equipment_status -> production_efficiency;
            capacity_utilization -> production_efficiency;
            supplier_efficiency -> production_efficiency;
            payment_timeliness -> production_efficiency;
            supplier_base_efficiency -> supplier_efficiency;
            equipment_age -> equipment_status;
            factory_capacity -> capacity_utilization;
            factory_capacity -> production_efficiency;
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
                           target_variable: str = "production_efficiency",
                           potential_causes: List[str] = None) -> pd.DataFrame:
        """
        分析根因 - 对多个潜在原因进行因果分析
        
        Args:
            target_variable: 目标变量
            potential_causes: 潜在原因列表
        """
        if potential_causes is None:
            potential_causes = [
                "payment_timeliness",
                "supplier_efficiency",
                "parts_availability",
                "avg_employee_skill",
                "equipment_status",
                "capacity_utilization"
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
    
    def _interpret_effect(self, cause: str, effect: float) -> str:
        """解释因果效应"""
        if effect is None:
            return "无法计算"
        
        abs_effect = abs(effect)
        
        if abs_effect > 0.3:
            strength = "强"
        elif abs_effect > 0.15:
            strength = "中等"
        else:
            strength = "弱"
        
        direction = "正向" if effect > 0 else "负向"
        
        cause_names = {
            "payment_timeliness": "付款及时性",
            "supplier_efficiency": "供应商效率",
            "parts_availability": "零部件可用性",
            "avg_employee_skill": "员工技能水平",
            "equipment_status": "设备状态",
            "capacity_utilization": "产能利用率"
        }
        
        cause_name = cause_names.get(cause, cause)
        
        return f"{cause_name}对生产效率有{strength}的{direction}影响 (效应值: {effect:.4f})"


class RootCauseAnalysisPipeline:
    """根因分析流水线"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.analyzer = CausalAnalyzer(data)
        self.analysis_results = None
        
    def run_full_analysis(self) -> Dict:
        """运行完整的根因分析"""
        print("="*70)
        print("制造企业生产效率根因分析")
        print("="*70)
        
        print("\n第一步：数据概览")
        self._print_data_overview()
        
        print("\n第二步：对比分析（正常月份 vs 异常月份）")
        comparison = self._compare_periods()
        
        print("\n第三步：因果分析")
        self.analysis_results = self.analyzer.analyze_root_cause()
        
        print("\n第四步：根因总结")
        summary = self._generate_summary(comparison)
        
        return {
            "comparison": comparison,
            "causal_analysis": self.analysis_results,
            "summary": summary
        }
    
    def _print_data_overview(self):
        """打印数据概览"""
        print(f"数据记录数: {len(self.data)}")
        print(f"时间范围: {self.data['date'].min()} 到 {self.data['date'].max()}")
        print(f"工厂数量: {self.data['factory_id'].nunique()}")
        print(f"供应商数量: {self.data['supplier_id'].nunique()}")
        
        print("\n各月份生产效率统计：")
        monthly_stats = self.data.groupby(['year', 'month'])['production_efficiency'].agg(['mean', 'std', 'min', 'max'])
        print(monthly_stats)
    
    def _compare_periods(self) -> pd.DataFrame:
        """对比正常月份和异常月份"""
        normal_data = self.data[~self.data['is_anomaly_month']]
        anomaly_data = self.data[self.data['is_anomaly_month']]
        
        metrics = [
            'production_efficiency',
            'payment_timeliness',
            'supplier_efficiency',
            'parts_availability',
            'avg_employee_skill',
            'equipment_status',
            'capacity_utilization'
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
        summary_lines.append("根因分析总结")
        summary_lines.append("="*70)
        
        efficiency_change = comparison[comparison['metric'] == 'production_efficiency']['change_percent'].values[0]
        summary_lines.append(f"\n生产效率变化: {efficiency_change:.2f}%")
        
        if efficiency_change < 0:
            summary_lines.append("\n主要下降原因（按影响程度排序）：")
            
            top_causes = comparison[
                (comparison['metric'] != 'production_efficiency') & 
                (comparison['change_percent'] < 0)
            ].head(3)
            
            for idx, row in top_causes.iterrows():
                summary_lines.append(f"  - {row['metric']}: 下降 {abs(row['change_percent']):.2f}%")
        
        if self.analysis_results is not None and len(self.analysis_results) > 0:
            summary_lines.append("\n因果效应分析结果：")
            for _, row in self.analysis_results.head(3).iterrows():
                if row['causal_effect'] is not None:
                    summary_lines.append(f"  - {row['interpretation']}")
        
        summary_lines.append("\n建议措施：")
        if len(comparison[comparison['metric'] == 'payment_timeliness']) > 0:
            payment_change = comparison[comparison['metric'] == 'payment_timeliness']['change_percent'].values[0]
            if payment_change < -5:
                summary_lines.append("  1. 优化付款流程，缩短付款周期，提高供应商合作积极性")
        
        if len(comparison[comparison['metric'] == 'supplier_efficiency']) > 0:
            supplier_change = comparison[comparison['metric'] == 'supplier_efficiency']['change_percent'].values[0]
            if supplier_change < -5:
                summary_lines.append("  2. 加强供应商管理，建立备选供应商机制")
        
        summary_lines.append("  3. 建立实时监控预警系统，及时发现效率异常")
        
        return "\n".join(summary_lines)
