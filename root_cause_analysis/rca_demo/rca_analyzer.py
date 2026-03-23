"""
根因分析核心模块 (Root Cause Analysis Module)

基于DoWhy GCM (Graphical Causal Models) 框架实现的根因分析系统
参考AWS文章: https://aws.amazon.com/cn/blogs/opensource/root-cause-analysis-with-dowhy-an-open-source-python-library-for-causal-machine-learning/

核心功能：
1. 结构因果模型构建
2. 因果机制自动分配与拟合
3. 箭头强度分析 (识别关键因果路径)
4. 反事实分析
5. 干预分析 (What-if分析)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

try:
    from dowhy import gcm
    import networkx as nx
except ImportError:
    raise ImportError("请安装dowhy库: pip install dowhy")


class RootCauseAnalyzer:
    """根因分析器 - 基于DoWhy GCM"""
    
    def __init__(self, data: pd.DataFrame):
        """
        初始化根因分析器
        
        Args:
            data: 分析数据 (DataFrame)
        """
        self.data = data
        self.scm = None
        self.causal_graph = None
        self.fitted = False
        self.causal_mechanisms = {}
        
    def build_causal_graph_from_edges(self, edges: List[Tuple[str, str]]) -> nx.DiGraph:
        """
        从边列表构建因果图
        
        Args:
            edges: 边列表，每个元素是 (source, target) 元组
            
        Returns:
            NetworkX有向图
        """
        causal_graph = nx.DiGraph(edges)
        self.causal_graph = causal_graph
        return causal_graph
    
    def build_causal_graph_from_dot(self, dot_string: str) -> nx.DiGraph:
        """
        从DOT格式字符串构建因果图
        
        Args:
            dot_string: DOT格式的因果图字符串
            
        Returns:
            NetworkX有向图
        """
        import re
        
        edges = []
        lines = dot_string.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if '->' in line:
                parts = line.split('->')
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip().rstrip(';').strip()
                    edges.append((source, target))
        
        causal_graph = nx.DiGraph(edges)
        self.causal_graph = causal_graph
        return causal_graph
    
    def create_structural_causal_model(self, 
                                       causal_graph: Union[nx.DiGraph, str] = None) -> gcm.StructuralCausalModel:
        """
        创建结构因果模型
        
        Args:
            causal_graph: 因果图 (NetworkX图或DOT字符串)
            
        Returns:
            StructuralCausalModel对象
        """
        if causal_graph is not None:
            if isinstance(causal_graph, str):
                self.build_causal_graph_from_dot(causal_graph)
            else:
                self.causal_graph = causal_graph
        
        if self.causal_graph is None:
            raise ValueError("请先设置因果图")
        
        self.scm = gcm.StructuralCausalModel(self.causal_graph)
        self.fitted = False
        
        return self.scm
    
    def auto_assign_causal_mechanisms(self):
        """
        自动分配因果机制
        
        根据数据类型和节点位置自动选择合适的因果机制：
        - 根节点：使用随机模型 (StochasticModel)
        - 连续变量：使用加性噪声模型 (ANM)
        - 离散变量：使用分类模型
        """
        if self.scm is None:
            raise ValueError("请先创建结构因果模型")
        
        for node in self.causal_graph.nodes:
            if node in self.data.columns:
                in_degree = self.causal_graph.in_degree(node)
                
                if in_degree == 0:
                    if self.data[node].dtype in ['int64', 'float64']:
                        if len(self.data[node].unique()) <= 10:
                            self.scm.set_causal_mechanism(node, gcm.EmpiricalDistribution())
                        else:
                            self.scm.set_causal_mechanism(node, gcm.ScipyDistribution())
                    else:
                        self.scm.set_causal_mechanism(node, gcm.EmpiricalDistribution())
                else:
                    if self.data[node].dtype in ['int64', 'float64']:
                        if len(self.data[node].unique()) <= 10:
                            self.scm.set_causal_mechanism(node, gcm.ClassifierFCM())
                        else:
                            self.scm.set_causal_mechanism(node, gcm.AdditiveNoiseModel(gcm.ml.create_linear_regressor()))
                    else:
                        self.scm.set_causal_mechanism(node, gcm.ClassifierFCM())
        
        print("[INFO] 因果机制已自动分配")
    
    def fit_model(self):
        """
        拟合因果模型
        
        使用数据拟合因果机制
        """
        if self.scm is None:
            raise ValueError("请先创建结构因果模型")
        
        gcm.fit(self.scm, self.data)
        self.fitted = True
        print("[INFO] 因果模型拟合完成")
    
    def compute_arrow_strength(self, 
                               target_node: str) -> Dict[Tuple[str, str], float]:
        """
        计算箭头强度 - 识别关键因果路径
        
        箭头强度表示每条边对目标节点变化的贡献程度
        
        Args:
            target_node: 目标节点（结果变量）
            
        Returns:
            箭头强度字典，键为边元组，值为强度值
        """
        if not self.fitted:
            raise ValueError("请先拟合因果模型")
        
        arrow_strengths = gcm.arrow_strength(self.scm, target_node)
        
        strength_dict = {}
        for edge, strength in arrow_strengths.items():
            if isinstance(edge, tuple) and len(edge) == 2:
                strength_dict[edge] = strength
        
        sorted_strengths = sorted(strength_dict.items(), key=lambda x: abs(x[1]), reverse=True)
        
        return dict(sorted_strengths)
    
    def analyze_root_causes(self,
                           outcome: str,
                           top_k: int = 10) -> pd.DataFrame:
        """
        根因分析 - 识别影响结果变量的主要原因
        
        Args:
            outcome: 结果变量
            top_k: 返回前k个最重要的原因
            
        Returns:
            根因分析结果DataFrame
        """
        if not self.fitted:
            raise ValueError("请先拟合因果模型")
        
        arrow_strengths = self.compute_arrow_strength(outcome)
        
        results = []
        for (source, target), strength in arrow_strengths.items():
            if target == outcome:
                results.append({
                    "cause": source,
                    "target": target,
                    "strength": strength,
                    "abs_strength": abs(strength)
                })
        
        results_df = pd.DataFrame(results)
        
        if not results_df.empty:
            results_df = results_df.sort_values('abs_strength', ascending=False)
            results_df['rank'] = range(1, len(results_df) + 1)
            
            if top_k > 0:
                results_df = results_df.head(top_k)
        
        return results_df
    
    def counterfactual_analysis(self,
                               intervention_dict: Dict[str, float],
                               outcome: str) -> pd.DataFrame:
        """
        反事实分析 - 计算干预后的结果变化
        
        Args:
            intervention_dict: 干预字典，键为干预变量，值为干预值
            outcome: 结果变量
            
        Returns:
            反事实分析结果DataFrame
        """
        if not self.fitted:
            raise ValueError("请先拟合因果模型")
        
        counterfactual_samples = gcm.counterfactual_samples(
            self.scm,
            intervention_dict,
            observed_data=self.data
        )
        
        original_outcome = self.data[outcome]
        counterfactual_outcome = counterfactual_samples[outcome]
        
        result_df = pd.DataFrame({
            "original": original_outcome,
            "counterfactual": counterfactual_outcome,
            "difference": counterfactual_outcome - original_outcome
        })
        
        return result_df
    
    def what_if_analysis(self,
                        intervention_dict: Dict[str, float],
                        outcome: str,
                        num_samples: int = 1000) -> pd.DataFrame:
        """
        What-if分析 - 模拟干预后的结果分布
        
        Args:
            intervention_dict: 干预字典
            outcome: 结果变量
            num_samples: 采样数量
            
        Returns:
            What-if分析结果DataFrame
        """
        if not self.fitted:
            raise ValueError("请先拟合因果模型")
        
        what_if_samples = gcm.interventional_samples(
            self.scm,
            intervention_dict,
            observed_data=self.data.sample(min(num_samples, len(self.data)))
        )
        
        return pd.DataFrame({outcome: what_if_samples[outcome]})
    
    def compute_direct_causal_influence(self, 
                                       target_node: str) -> Dict[str, float]:
        """
        计算直接因果影响
        
        评估每个父节点对目标节点的直接因果影响
        
        Args:
            target_node: 目标节点
            
        Returns:
            直接因果影响字典
        """
        if not self.fitted:
            raise ValueError("请先拟合因果模型")
        
        influence = gcm.direct_causal_influence(self.scm, target_node)
        
        sorted_influence = sorted(influence.items(), key=lambda x: abs(x[1]), reverse=True)
        
        return dict(sorted_influence)
    
    def get_distribution_change_attribution(self,
                                           target_node: str,
                                           anomaly_data: pd.DataFrame) -> Dict[str, float]:
        """
        分布变化归因分析
        
        分析异常数据与正常数据之间的分布变化，归因到各个父节点
        
        Args:
            target_node: 目标节点
            anomaly_data: 异常时期数据
            
        Returns:
            归因结果字典
        """
        if not self.fitted:
            raise ValueError("请先拟合因果模型")
        
        attribution = gcm.distribution_change_attribution(
            self.scm, 
            target_node,
            self.data,
            anomaly_data
        )
        
        sorted_attribution = sorted(attribution.items(), key=lambda x: abs(x[1]), reverse=True)
        
        return dict(sorted_attribution)
    
    def intrinsic_causal_influence(self,
                                  target_node: str,
                                  num_samples: int = 1000) -> Dict[str, float]:
        """
        内在因果影响分析
        
        评估每个节点对目标节点的内在因果贡献
        
        Args:
            target_node: 目标节点
            num_samples: 采样数量
            
        Returns:
            内在因果影响字典
        """
        if not self.fitted:
            raise ValueError("请先拟合因果模型")
        
        influence = gcm.intrinsic_causal_influence(
            self.scm, 
            target_node,
            num_samples=num_samples
        )
        
        sorted_influence = sorted(influence.items(), key=lambda x: abs(x[1]), reverse=True)
        
        return dict(sorted_influence)
    
    def get_summary_statistics(self, 
                               variables: List[str] = None) -> pd.DataFrame:
        """
        获取变量的统计摘要
        
        Args:
            variables: 变量列表 (可选)
            
        Returns:
            统计摘要DataFrame
        """
        if variables is None:
            variables = self.data.columns.tolist()
        
        stats = []
        for var in variables:
            if var in self.data.columns:
                if self.data[var].dtype in ['int64', 'float64']:
                    stats.append({
                        'variable': var,
                        'mean': self.data[var].mean(),
                        'std': self.data[var].std(),
                        'min': self.data[var].min(),
                        'max': self.data[var].max(),
                        'median': self.data[var].median()
                    })
        
        return pd.DataFrame(stats)
    
    def compare_periods(self,
                       period_col: str,
                       normal_periods: List,
                       anomaly_periods: List,
                       variables: List[str] = None) -> pd.DataFrame:
        """
        对比正常时期和异常时期的指标
        
        Args:
            period_col: 时期标识列
            normal_periods: 正常时期列表
            anomaly_periods: 异常时期列表
            variables: 要对比的变量列表
            
        Returns:
            对比结果DataFrame
        """
        if variables is None:
            variables = self.data.select_dtypes(include=[np.number]).columns.tolist()
            variables = [v for v in variables if v != period_col]
        
        normal_data = self.data[self.data[period_col].isin(normal_periods)]
        anomaly_data = self.data[self.data[period_col].isin(anomaly_periods)]
        
        comparison = []
        for var in variables:
            if var in self.data.columns:
                normal_mean = normal_data[var].mean()
                anomaly_mean = anomaly_data[var].mean()
                
                if normal_mean != 0:
                    change_percent = (anomaly_mean - normal_mean) / normal_mean * 100
                else:
                    change_percent = 0
                
                comparison.append({
                    'variable': var,
                    'normal_mean': normal_mean,
                    'anomaly_mean': anomaly_mean,
                    'change_percent': change_percent,
                    'abs_change_percent': abs(change_percent)
                })
        
        comparison_df = pd.DataFrame(comparison)
        comparison_df = comparison_df.sort_values('abs_change_percent', ascending=False)
        
        return comparison_df
    
    def visualize_causal_graph(self, 
                               save_path: str = None,
                               highlight_node: str = None) -> Optional[str]:
        """
        可视化因果图
        
        Args:
            save_path: 保存路径 (可选)
            highlight_node: 高亮节点 (可选)
            
        Returns:
            如果指定了保存路径，返回文件路径
        """
        if self.causal_graph is None:
            raise ValueError("请先创建因果图")
        
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.causal_graph, k=2, iterations=50)
        
        node_colors = []
        for node in self.causal_graph.nodes():
            if highlight_node and node == highlight_node:
                node_colors.append('#FF6B6B')
            else:
                node_colors.append('#4ECDC4')
        
        nx.draw(self.causal_graph, pos, 
                with_labels=True,
                node_color=node_colors,
                node_size=3000,
                font_size=10,
                font_weight='bold',
                arrows=True,
                arrowsize=20,
                edge_color='gray',
                linewidths=2)
        
        plt.title("Causal Graph", fontsize=16, fontweight='bold')
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            plt.close()
            return None
