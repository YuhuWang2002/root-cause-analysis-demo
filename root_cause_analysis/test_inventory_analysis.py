#!/usr/bin/env python3
"""
测试场景2的库存分析流程
"""

import pandas as pd
import os
import sys
import re
import networkx as nx
from dowhy import CausalModel

# 测试数据路径
data_path = '/Users/yuhuwang/Documents/trae_projects/root_cause_analysis/server_inventory_data.csv'

# 测试因果图（基于场景2的库存分析因果图）
def create_causal_graph():
    """
    创建因果图
    """
    G = nx.DiGraph()
    
    # 添加边
    G.add_edge('server_2885_sales_quantity', 'cpu_xeon_6338_inventory_level')
    G.add_edge('server_5885_sales_quantity', 'cpu_xeon_6338_inventory_level')
    G.add_edge('server_5885_sales_quantity', 'cpu_xeon_8358_inventory_level')
    G.add_edge('server_2885_sales_quantity', 'memory_32gb_inventory_level')
    G.add_edge('server_5885_sales_quantity', 'memory_64gb_inventory_level')
    G.add_edge('server_2885_sales_quantity', 'hdd_2tb_inventory_level')
    G.add_edge('server_5885_sales_quantity', 'ssd_1tb_inventory_level')
    G.add_edge('cpu_xeon_6338_commonality', 'cpu_xeon_6338_inventory_level')
    G.add_edge('cpu_xeon_8358_commonality', 'cpu_xeon_8358_inventory_level')
    G.add_edge('memory_32gb_commonality', 'memory_32gb_inventory_level')
    G.add_edge('memory_64gb_commonality', 'memory_64gb_inventory_level')
    G.add_edge('hdd_2tb_commonality', 'hdd_2tb_inventory_level')
    G.add_edge('ssd_1tb_commonality', 'ssd_1tb_inventory_level')
    G.add_edge('cpu_xeon_6338_utilization_ratio', 'cpu_xeon_6338_inventory_level')
    G.add_edge('cpu_xeon_8358_utilization_ratio', 'cpu_xeon_8358_inventory_level')
    G.add_edge('memory_32gb_utilization_ratio', 'memory_32gb_inventory_level')
    G.add_edge('memory_64gb_utilization_ratio', 'memory_64gb_inventory_level')
    G.add_edge('hdd_2tb_utilization_ratio', 'hdd_2tb_inventory_level')
    G.add_edge('ssd_1tb_utilization_ratio', 'ssd_1tb_inventory_level')
    G.add_edge('cpu_xeon_6338_inventory_turnover_rate', 'cpu_xeon_6338_inventory_level')
    G.add_edge('cpu_xeon_8358_inventory_turnover_rate', 'cpu_xeon_8358_inventory_level')
    G.add_edge('memory_32gb_inventory_turnover_rate', 'memory_32gb_inventory_level')
    G.add_edge('memory_64gb_inventory_turnover_rate', 'memory_64gb_inventory_level')
    G.add_edge('hdd_2tb_inventory_turnover_rate', 'hdd_2tb_inventory_level')
    G.add_edge('ssd_1tb_inventory_turnover_rate', 'ssd_1tb_inventory_level')
    
    return G

# 创建因果图
causal_graph = create_causal_graph()

def extract_treatments_from_graph(causal_graph, outcome, data):
    """
    从因果图中提取所有可能的处理变量
    """
    # 解析networkx DiGraph对象
    treatments = set()
    
    # 构建有向图
    graph = {}
    for source, target in causal_graph.edges():
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
    if not treatments and hasattr(data, 'columns'):
        # 从数据中提取可能与结果变量相关的变量
        for col in data.columns:
            # 排除结果变量本身
            if col != outcome and 'production' not in col:
                # 选择与销售、通用性、利用率相关的变量
                if any(keyword in col for keyword in ['sales', 'commonality', 'utilization']):
                    treatments.add(col)
    
    # 4. 如果仍然没有找到处理变量，使用一些通用的库存分析变量
    if not treatments:
        # 检查数据列名，找到可能的处理变量
        if hasattr(data, 'columns'):
            # 从数据中提取可能的处理变量
            for col in data.columns:
                # 优先选择与库存分析相关的变量，排除结果变量本身
                if col != outcome and 'production' not in col and any(keyword in col for keyword in ['sales', 'commonality', 'utilization']):
                    treatments.add(col)
        
        # 如果仍然没有找到，使用默认的处理变量
        if not treatments:
            # 从数据中提取所有销售和通用性相关的列
            if hasattr(data, 'columns'):
                for col in data.columns:
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

def analyze_causal_effect(data, causal_graph, treatment, outcome):
    """
    分析单个处理变量对结果变量的因果效应
    """
    try:
        # 检查变量是否在数据中
        if treatment not in data.columns:
            print(f"处理变量 {treatment} 不在数据中")
            return 0.0, False, f"处理变量不在数据中: {treatment}"
        
        if outcome not in data.columns:
            print(f"结果变量 {outcome} 不在数据中")
            return 0.0, False, f"结果变量不在数据中: {outcome}"
        
        # 创建因果模型
        model = CausalModel(
            data=data,
            treatment=treatment,
            outcome=outcome,
            graph=causal_graph,
            logging_level='INFO'
        )
        
        # 识别因果效应
        identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
        
        # 估计因果效应
        estimate = model.estimate_effect(
            identified_estimand,
            method_name="backdoor.linear_regression"
        )
        
        # 确保estimate.value不为None
        causal_effect = estimate.value if estimate.value is not None else 0.0
        print(f"处理变量 {treatment} 的因果效应: {causal_effect}")
        
        return causal_effect, True, None
    except Exception as e:
        print(f"分析处理变量 {treatment} 时出错: {str(e)}")
        return 0.0, False, str(e)

def run_root_cause_analysis(data, causal_graph, outcome):
    """
    运行根因分析 - 自动从因果图中提取处理变量并分析
    """
    try:
        # 从因果图中提取处理变量
        treatments = extract_treatments_from_graph(causal_graph, outcome, data)
        
        # 确保有处理变量
        if not treatments:
            # 如果没有找到处理变量，尝试从数据中提取相关变量
            if hasattr(data, 'columns'):
                # 从数据中提取可能的处理变量，排除与生产效率相关的变量和结果变量本身
                for col in data.columns:
                    if col != outcome and any(keyword in col for keyword in ['sales', 'commonality']) and 'production' not in col:
                        treatments.append(col)
            
            # 如果仍然没有找到，使用默认的处理变量
            if not treatments:
                # 确保默认处理变量不包含结果变量
                default_treatments = ['server_2885_sales_quantity', 'server_5885_sales_quantity', 'cpu_xeon_6338_commonality', 'cpu_xeon_8358_commonality']
                treatments = [t for t in default_treatments if t != outcome]
        
        print(f"从因果图中提取到 {len(treatments)} 个处理变量: {treatments}")
        
        # 分析多个处理变量
        results = []
        for treatment in treatments:
            causal_effect, success, error = analyze_causal_effect(data, causal_graph, treatment, outcome)
            results.append({
                "treatment": treatment,
                "causal_effect": causal_effect,
                "success": success,
                "error": error
            })
        
        # 创建DataFrame
        results_df = pd.DataFrame(results)
        print(f"analyze_causal_effects 返回的结果: {results_df}")
        if 'causal_effect' in results_df.columns:
            print(f"causal_effect 列的值: {list(results_df['causal_effect'])}")
            print(f"causal_effect 列的类型: {results_df['causal_effect'].dtype}")
        
        # 确保结果不为空
        if results_df.empty:
            # 如果结果为空，创建一个默认的结果
            print("results_df 为空，创建默认结果")
            results_df = pd.DataFrame({
                'treatment': treatments,
                'causal_effect': [0.0] * len(treatments),
                'success': [False] * len(treatments)
            })
        
        # 确保 'causal_effect' 列存在
        if 'causal_effect' not in results_df.columns:
            print("'causal_effect' 列不存在，添加默认值")
            results_df['causal_effect'] = [0.0] * len(results_df)
        
        # 处理 'causal_effect' 列中的 None 值
        print("处理 'causal_effect' 列中的 None 值")
        results_df['causal_effect'] = results_df['causal_effect'].apply(lambda x: 0.0 if x is None else x)
        print(f"处理后的 causal_effect 列: {list(results_df['causal_effect'])}")
        
        # 计算绝对值 - 使用更安全的方式
        try:
            # 确保所有值都是数字
            print("确保所有值都是数字")
            results_df['causal_effect'] = pd.to_numeric(results_df['causal_effect'], errors='coerce').fillna(0.0)
            print("计算绝对值")
            results_df['abs_causal_effect'] = results_df['causal_effect'].abs()
            print(f"计算后的 abs_causal_effect 列: {list(results_df['abs_causal_effect'])}")
        except Exception as e:
            print(f"计算绝对值时出错: {str(e)}")
            # 如果计算失败，手动计算
            print("手动计算绝对值")
            results_df['abs_causal_effect'] = results_df['causal_effect'].apply(lambda x: abs(x) if x is not None and isinstance(x, (int, float)) else 0.0)
            print(f"手动计算后的 abs_causal_effect 列: {list(results_df['abs_causal_effect'])}")
        
        # 过滤掉因果效应为None的行
        print("过滤掉因果效应为None的行")
        results_df = results_df[results_df['causal_effect'].notna()]
        print(f"过滤后的结果行数: {len(results_df)}")
        
        # 确保结果不为空
        if results_df.empty:
            # 如果过滤后结果为空，创建一个默认的结果
            print("过滤后 results_df 为空，创建默认结果")
            results_df = pd.DataFrame({
                'treatment': treatments[:1],  # 使用第一个处理变量
                'causal_effect': [0.0],
                'success': [False]
            })
            results_df['abs_causal_effect'] = [0.0]
        else:
            # 按绝对值排序
            print("按绝对值排序")
            results_df = results_df.sort_values('abs_causal_effect', ascending=False)
            print(f"排序后的结果: {results_df}")
        
        # 添加排名
        print("添加排名")
        results_df['rank'] = range(1, len(results_df) + 1)
        print(f"添加排名后的结果: {results_df}")
        
        # 保存分析结果
        analysis_results = {}
        analysis_results['root_cause_analysis'] = results_df.to_dict('records')
        analysis_results['treatments'] = treatments
        analysis_results['outcome'] = outcome
        print(f"保存的分析结果: {analysis_results}")
        
        return results_df, analysis_results
    except Exception as e:
        print(f"run_root_cause_analysis 出错: {str(e)}")
        # 创建默认结果
        default_results = pd.DataFrame({
            'treatment': ['default'],
            'causal_effect': [0.0],
            'abs_causal_effect': [0.0],
            'rank': [1],
            'success': [False]
        })
        analysis_results = {}
        analysis_results['root_cause_analysis'] = default_results.to_dict('records')
        analysis_results['treatments'] = ['default']
        analysis_results['outcome'] = outcome
        return default_results, analysis_results

def test_inventory_analysis():
    """
    测试库存分析流程
    """
    print("开始测试场景2的库存分析流程...")
    
    # 1. 读取数据
    print(f"读取数据文件: {data_path}")
    if not os.path.exists(data_path):
        print(f"错误: 数据文件不存在: {data_path}")
        return
    
    data = pd.read_csv(data_path)
    print(f"数据读取成功，共 {len(data)} 行，{len(data.columns)} 列")
    print(f"数据列名: {list(data.columns)}")
    
    # 2. 测试不同的结果变量
    outcome_variables = [
        "cpu_xeon_6338_inventory_level",
        "cpu_xeon_6338_inventory_turnover_rate",
        "cpu_xeon_6338_dead_inventory",
        "cpu_xeon_8358_inventory_level",
        "memory_32gb_inventory_level",
        "memory_64gb_inventory_level",
        "hdd_2tb_inventory_level",
        "ssd_1tb_inventory_level"
    ]
    
    for outcome in outcome_variables:
        print(f"\n测试结果变量: {outcome}")
        
        # 3. 提取处理变量
        treatments = extract_treatments_from_graph(causal_graph, outcome, data)
        print(f"从因果图中提取到 {len(treatments)} 个处理变量: {treatments}")
        
        # 4. 运行根因分析
        print("运行根因分析...")
        try:
            results_df, analysis_results = run_root_cause_analysis(data, causal_graph, outcome)
            print(f"分析完成，结果行数: {len(results_df)}")
            
            # 5. 输出分析结果
            print("根因分析结果:")
            print(results_df[['rank', 'treatment', 'causal_effect', 'abs_causal_effect']])
            
            # 6. 输出分析变量和结果变量
            if analysis_results:
                print(f"分析变量: {', '.join(analysis_results.get('treatments', []))}")
                print(f"结果变量: {analysis_results.get('outcome', 'N/A')}")
                
                # 7. 检查是否有非零的因果效应
                if 'root_cause_analysis' in analysis_results:
                    root_cause_results = analysis_results['root_cause_analysis']
                    non_zero_effects = [item for item in root_cause_results if item['causal_effect'] != 0]
                    print(f"非零因果效应的处理变量数量: {len(non_zero_effects)}")
                    if non_zero_effects:
                        print("非零因果效应的处理变量:")
                        for item in non_zero_effects:
                            print(f"  - {item['treatment']}: {item['causal_effect']:.4f}")
        except Exception as e:
            print(f"分析失败: {str(e)}")

if __name__ == "__main__":
    test_inventory_analysis()

