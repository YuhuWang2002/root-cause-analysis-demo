"""
测试根因分析模块

验证DoWhy GCM根因分析功能是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rca_analyzer import RootCauseAnalyzer
from rca_data_generator import create_demo_scenario
import pandas as pd

def test_basic_analysis():
    """测试基本分析流程"""
    print("=" * 60)
    print("测试根因分析模块")
    print("=" * 60)
    
    print("\n1. 生成演示数据...")
    data, anomaly_factors, causal_graph = create_demo_scenario()
    print(f"   ✓ 数据生成成功: {len(data)} 条记录")
    
    print("\n2. 创建根因分析器...")
    analyzer = RootCauseAnalyzer(data)
    print("   ✓ 分析器创建成功")
    
    print("\n3. 构建因果图...")
    analyzer.build_causal_graph_from_dot(causal_graph)
    print(f"   ✓ 因果图构建成功: {len(analyzer.causal_graph.nodes)} 个节点, {len(analyzer.causal_graph.edges)} 条边")
    
    print("\n4. 创建结构因果模型...")
    analyzer.create_structural_causal_model()
    print("   ✓ 结构因果模型创建成功")
    
    print("\n5. 自动分配因果机制...")
    analyzer.auto_assign_causal_mechanisms()
    print("   ✓ 因果机制分配成功")
    
    print("\n6. 拟合模型...")
    analyzer.fit_model()
    print("   ✓ 模型拟合成功")
    
    print("\n7. 分析根本原因...")
    results = analyzer.analyze_root_causes('profit', top_k=10)
    print("   ✓ 根因分析完成")
    print("\n根因分析结果:")
    print(results.to_string(index=False))
    
    print("\n8. 计算箭头强度...")
    strengths = analyzer.compute_arrow_strength('profit')
    print("   ✓ 箭头强度计算完成")
    print("\n箭头强度 (Top 5):")
    for i, (edge, strength) in enumerate(list(strengths.items())[:5], 1):
        print(f"   {i}. {edge[0]} -> {edge[1]}: {strength:.4f}")
    
    print("\n9. What-if分析...")
    current_ad_spend = data['ad_spend'].mean()
    what_if_results = analyzer.what_if_analysis(
        intervention_dict={'ad_spend': lambda x: current_ad_spend * 1.5},
        outcome='profit',
        num_samples=100
    )
    print("   ✓ What-if分析完成")
    print(f"\n   当前平均利润: ${data['profit'].mean():,.2f}")
    print(f"   干预后平均利润: ${what_if_results['profit'].mean():,.2f}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_basic_analysis()
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
