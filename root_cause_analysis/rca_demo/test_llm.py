"""
测试大模型解释功能

验证LLM解释器是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rca_analyzer import RootCauseAnalyzer
from rca_data_generator import create_demo_scenario
from rca_llm_explainer import LLMExplainer
import pandas as pd

def test_llm_explainer():
    """测试大模型解释器"""
    print("=" * 60)
    print("测试大模型解释功能")
    print("=" * 60)
    
    print("\n1. 生成演示数据...")
    data, anomaly_factors, causal_graph = create_demo_scenario()
    print(f"   ✓ 数据生成成功: {len(data)} 条记录")
    
    print("\n2. 创建根因分析器...")
    analyzer = RootCauseAnalyzer(data)
    print("   ✓ 分析器创建成功")
    
    print("\n3. 构建因果图...")
    analyzer.build_causal_graph_from_dot(causal_graph)
    print(f"   ✓ 因果图构建成功")
    
    print("\n4. 创建结构因果模型...")
    analyzer.create_structural_causal_model()
    analyzer.auto_assign_causal_mechanisms()
    analyzer.fit_model()
    print("   ✓ 模型拟合成功")
    
    print("\n5. 分析根本原因...")
    analysis_results = analyzer.analyze_root_causes('profit', top_k=10)
    print("   ✓ 根因分析完成")
    print("\n根因分析结果:")
    print(analysis_results.to_string(index=False))
    
    print("\n6. 创建指标对比数据...")
    normal_data = data[~data['is_anomaly_period']]
    anomaly_data = data[data['is_anomaly_period']]
    
    comparison_data = []
    metrics = ['profit', 'revenue', 'sold_units', 'page_views', 'ad_spend', 'unit_price', 'operational_cost']
    
    for metric in metrics:
        normal_mean = normal_data[metric].mean()
        anomaly_mean = anomaly_data[metric].mean()
        change = (anomaly_mean - normal_mean) / normal_mean * 100 if normal_mean != 0 else 0
        
        comparison_data.append({
            'variable': metric,
            'normal_mean': normal_mean,
            'anomaly_mean': anomaly_mean,
            'change_percent': change
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    print("   ✓ 指标对比数据创建成功")
    
    print("\n7. 测试LLM解释器（无API密钥模式）...")
    explainer = LLMExplainer()
    print("   ✓ LLM解释器创建成功（未配置API）")
    
    print("\n8. 测试提示词生成...")
    prompt = explainer._build_prompt(
        analysis_results=analysis_results,
        comparison_df=comparison_df,
        causal_graph=causal_graph,
        scenario_background="某在线商店销售智能手机，零售价$999。2021年利润保持稳定，但在2022年初突然出现显著下降。"
    )
    print("   ✓ 提示词生成成功")
    print(f"   提示词长度: {len(prompt)} 字符")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    
    print("\n提示：要使用完整的LLM功能，请配置SiliconFlow API密钥")
    print("使用方法：")
    print("  1. 在Web界面侧边栏输入API密钥")
    print("  2. 或在代码中创建LLMExplainer(api_key='your-api-key')")

if __name__ == "__main__":
    try:
        test_llm_explainer()
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
