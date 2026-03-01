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
    
    def extract_treatments_from_graph(self, outcome: str) -> List[str]:
        """
        从因果图中提取所有可能的处理变量
        
        Args:
            outcome: 结果变量
            
        Returns:
            处理变量列表
        """
        import re
        
        # 解析DOT格式的因果图
        treatments = set()
        
        # 提取所有边（支持包含下划线和空格的节点名）
        edges = re.findall(r'\s*([\w_\s]+)\s*->\s*([\w_\s]+)\s*;', self.causal_graph)
        
        # 构建有向图
        graph = {}
        for source, target in edges:
            # 去除节点名中的空格
            source = source.strip()
            target = target.strip()
            if source not in graph:
                graph[source] = []
            graph[source].append(target)
        
        # 找到所有指向结果变量的路径
        visited = set()
        
        def find_ancestors(node):
            for source, targets in graph.items():
                if node in targets and source not in visited:
                    visited.add(source)
                    treatments.add(source)
                    find_ancestors(source)
        
        # 1. 尝试使用原始结果变量名
        find_ancestors(outcome)
        
        # 2. 如果没有找到处理变量，尝试在因果图中找到包含该结果变量的完整列名
        if not treatments:
            # 遍历因果图中的所有目标节点
            all_targets = set()
            for source, targets in graph.items():
                all_targets.update(targets)
            
            # 找到包含结果变量关键字的目标节点
            matching_targets = []
            for target in all_targets:
                if outcome in target or any(keyword in target for keyword in ['inventory', '库存']):
                    matching_targets.append(target)
            
            # 对每个匹配的目标节点查找处理变量
            for target in matching_targets:
                visited = set()
                find_ancestors(target)
        
        # 3. 如果仍然没有找到处理变量，尝试提取结果变量的基本部分
        if not treatments:
            # 提取结果变量的基本部分（去掉前缀）
            base_outcome = outcome
            if '_' in outcome:
                # 尝试找到包含关键字的部分
                for part in outcome.split('_'):
                    if part in ['inventory_level', 'inventory_turnover', 'dead_inventory', 'inventory', '库存']:
                        base_outcome = part
                        break
            
            # 使用基本结果变量名重新查找
            if base_outcome != outcome:
                visited = set()
                treatments = set()
                find_ancestors(base_outcome)
        
        # 4. 如果仍然没有找到处理变量，尝试从数据中提取与结果变量相关的变量
        if not treatments and hasattr(self.data, 'columns'):
            # 从数据中提取可能与结果变量相关的变量
            for col in self.data.columns:
                # 排除结果变量本身
                if col != outcome and 'production' not in col:
                    # 选择与销售、通用性、利用率相关的变量
                    if any(keyword in col for keyword in ['sales', 'commonality', 'utilization']):
                        treatments.add(col)
        
        # 4. 如果仍然没有找到处理变量，使用一些通用的库存分析变量
        if not treatments:
            # 检查数据列名，找到可能的处理变量
            if hasattr(self.data, 'columns'):
                # 从数据中提取可能的处理变量
                for col in self.data.columns:
                    # 优先选择与库存分析相关的变量，排除结果变量本身
                    if col != outcome and 'production' not in col and any(keyword in col for keyword in ['sales', 'commonality', 'utilization']):
                        treatments.add(col)
            
            # 如果仍然没有找到，使用默认的处理变量
            if not treatments:
                # 从数据中提取所有销售和通用性相关的列
                if hasattr(self.data, 'columns'):
                    for col in self.data.columns:
                        if col != outcome and 'production' not in col and ('sales' in col or 'commonality' in col):
                            treatments.add(col)
                
                # 如果仍然没有找到，使用默认值
                if not treatments:
                    # 确保默认处理变量不包含结果变量
                    default_treatments = {'server_2885_sales_quantity', 'server_5885_sales_quantity', 'cpu_xeon_6338_commonality', 'cpu_xeon_8358_commonality'}
                    treatments = {t for t in default_treatments if t != outcome}
        
        # 过滤掉与生产效率相关的变量，确保只使用库存分析相关的变量，并且不包含结果变量本身
        filtered_treatments = []
        for treatment in treatments:
            # 排除与生产效率相关的变量和结果变量本身
            if 'production' not in treatment and treatment != outcome:
                filtered_treatments.append(treatment)
        
        # 如果过滤后没有处理变量，使用默认的库存分析变量
        if not filtered_treatments:
            # 确保默认处理变量不包含结果变量
            default_treatments = ['server_2885_sales_quantity', 'server_5885_sales_quantity', 'cpu_xeon_6338_commonality', 'cpu_xeon_8358_commonality']
            filtered_treatments = [t for t in default_treatments if t != outcome]
        
        return filtered_treatments
    
    def run_root_cause_analysis(self, outcome: str) -> pd.DataFrame:
        """
        运行根因分析 - 自动从因果图中提取处理变量并分析
        
        Args:
            outcome: 结果变量
            
        Returns:
            根因分析结果数据框
        """
        try:
            # 从因果图中提取处理变量
            treatments = self.extract_treatments_from_graph(outcome)
            
            # 确保有处理变量
            if not treatments:
                # 如果没有找到处理变量，尝试从数据中提取相关变量
                if hasattr(self.data, 'columns'):
                    # 从数据中提取可能的处理变量，排除与生产效率相关的变量和结果变量本身
                    for col in self.data.columns:
                        if col != outcome and any(keyword in col for keyword in ['sales', 'commonality']) and 'production' not in col:
                            treatments.append(col)
                
                # 如果仍然没有找到，使用默认的处理变量
                if not treatments:
                    # 确保默认处理变量不包含结果变量
                    default_treatments = ['server_2885_sales_quantity', 'server_5885_sales_quantity', 'cpu_xeon_6338_commonality', 'cpu_xeon_8358_commonality']
                    treatments = [t for t in default_treatments if t != outcome]
            
            print(f"从因果图中提取到 {len(treatments)} 个处理变量: {treatments}")
            
            # 分析多个处理变量
            results_df = self.analyze_multiple_treatments(treatments, outcome)
            
            # 打印调试信息
            print(f"[DEBUG] analyze_multiple_treatments 返回的结果: {results_df}")
            print(f"[DEBUG] results_df 列: {list(results_df.columns)}")
            if 'causal_effect' in results_df.columns:
                print(f"[DEBUG] causal_effect 列的值: {list(results_df['causal_effect'])}")
                print(f"[DEBUG] causal_effect 列的类型: {results_df['causal_effect'].dtype}")
            
            # 确保结果不为空
            if results_df.empty:
                # 如果结果为空，创建一个默认的结果
                print("[DEBUG] results_df 为空，创建默认结果")
                results_df = pd.DataFrame({
                    'treatment': treatments,
                    'causal_effect': [0.0] * len(treatments),
                    'success': [False] * len(treatments)
                })
            
            # 确保 'causal_effect' 列存在
            if 'causal_effect' not in results_df.columns:
                print("[DEBUG] 'causal_effect' 列不存在，添加默认值")
                results_df['causal_effect'] = [0.0] * len(results_df)
            
            # 处理 'causal_effect' 列中的 None 值
            print("[DEBUG] 处理 'causal_effect' 列中的 None 值")
            results_df['causal_effect'] = results_df['causal_effect'].apply(lambda x: 0.0 if x is None else x)
            print(f"[DEBUG] 处理后的 causal_effect 列: {list(results_df['causal_effect'])}")
            
            # 计算绝对值 - 使用更安全的方式
            try:
                # 确保所有值都是数字
                print("[DEBUG] 确保所有值都是数字")
                results_df['causal_effect'] = pd.to_numeric(results_df['causal_effect'], errors='coerce').fillna(0.0)
                print("[DEBUG] 计算绝对值")
                results_df['abs_causal_effect'] = results_df['causal_effect'].abs()
                print(f"[DEBUG] 计算后的 abs_causal_effect 列: {list(results_df['abs_causal_effect'])}")
            except Exception as e:
                print(f"[DEBUG] 计算绝对值时出错: {str(e)}")
                # 如果计算失败，手动计算
                print("[DEBUG] 手动计算绝对值")
                results_df['abs_causal_effect'] = results_df['causal_effect'].apply(lambda x: abs(x) if x is not None and isinstance(x, (int, float)) else 0.0)
                print(f"[DEBUG] 手动计算后的 abs_causal_effect 列: {list(results_df['abs_causal_effect'])}")
            
            # 过滤掉因果效应为None的行
            print("[DEBUG] 过滤掉因果效应为None的行")
            results_df = results_df[results_df['causal_effect'].notna()]
            print(f"[DEBUG] 过滤后的结果行数: {len(results_df)}")
            
            # 确保结果不为空
            if results_df.empty:
                # 如果过滤后结果为空，创建一个默认的结果
                print("[DEBUG] 过滤后 results_df 为空，创建默认结果")
                results_df = pd.DataFrame({
                    'treatment': treatments[:1],  # 使用第一个处理变量
                    'causal_effect': [0.0],
                    'success': [False]
                })
                results_df['abs_causal_effect'] = [0.0]
            else:
                # 按绝对值排序
                print("[DEBUG] 按绝对值排序")
                results_df = results_df.sort_values('abs_causal_effect', ascending=False)
                print(f"[DEBUG] 排序后的结果: {results_df}")
            
            # 添加排名
            print("[DEBUG] 添加排名")
            results_df['rank'] = range(1, len(results_df) + 1)
            print(f"[DEBUG] 添加排名后的结果: {results_df}")
            
            # 保存分析结果
            print("[DEBUG] 保存分析结果")
            self.analysis_results['root_cause_analysis'] = results_df.to_dict('records')
            self.analysis_results['treatments'] = treatments
            self.analysis_results['outcome'] = outcome
            print(f"[DEBUG] 保存的分析结果: {self.analysis_results}")
            
            return results_df
        except Exception as e:
            print(f"[DEBUG] run_root_cause_analysis 出错: {str(e)}")
            # 创建默认结果
            default_results = pd.DataFrame({
                'treatment': ['default'],
                'causal_effect': [0.0],
                'abs_causal_effect': [0.0],
                'rank': [1],
                'success': [False]
            })
            self.analysis_results['root_cause_analysis'] = default_results.to_dict('records')
            self.analysis_results['treatments'] = ['default']
            self.analysis_results['outcome'] = outcome
            return default_results
    
    def get_analysis_summary(self) -> Dict:
        """
        获取分析结果摘要
        """
        if not self.analysis_results:
            return {"message": "请先运行分析"}
        
        summary = {
            "causal_effect": self.analysis_results.get("causal_effect"),
            "has_refutation_results": "refutation_results" in self.analysis_results,
            "has_counterfactual_analysis": "counterfactual_analysis" in self.analysis_results,
            "has_root_cause_analysis": "root_cause_analysis" in self.analysis_results
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
        
        # 添加根因分析摘要（如果存在）
        if "root_cause_analysis" in self.analysis_results:
            root_cause_results = self.analysis_results["root_cause_analysis"]
            summary["root_cause_summary"] = {
                "top_causes": [item["treatment"] for item in root_cause_results[:3]],
                "total_treatments": len(root_cause_results)
            }
        
        return summary
