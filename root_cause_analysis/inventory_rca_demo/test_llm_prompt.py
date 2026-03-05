"""
测试LLM解释器的提示词生成
"""

from data_generator import create_inventory_scenario
from causal_analyzer import InventoryCausalAnalyzer
from llm_explainer import LLMExplainer

def test_prompt_generation():
    """测试提示词生成"""
    print("=== 测试LLM解释器提示词生成 ===\n")
    
    # 生成数据
    print("1. 生成数据...")
    actual_data, counterfactual_data = create_inventory_scenario()
    print(f"   - 实际数据: {len(actual_data)} 条记录")
    print(f"   - 反事实数据: {len(counterfactual_data)} 条记录\n")
    
    # 运行因果分析
    print("2. 运行因果分析...")
    analyzer = InventoryCausalAnalyzer(data=actual_data)
    results = analyzer.run_full_analysis(counterfactual_data)
    print(f"   - 因果效应值: {results.get('causal_effect', 0):.4f}")
    print(f"   - 是否为根因: {results.get('counterfactual_analysis', {}).get('is_root_cause', False)}\n")
    
    # 创建LLM解释器（不初始化客户端，只测试提示词生成）
    print("3. 测试提示词生成...")
    explainer = LLMExplainer(api_key=None)
    
    # 生成提示词
    prompt = explainer._build_prompt(results, actual_data, counterfactual_data)
    
    # 检查因果图是否在提示词中
    if "因果图结构" in prompt:
        print("   ✅ 因果图信息已包含在提示词中")
    else:
        print("   ❌ 因果图信息未包含在提示词中")
    
    if "产品A销量 → 部件A消耗量" in prompt:
        print("   ✅ 因果关系已正确添加")
    else:
        print("   ❌ 因果关系未正确添加")
    
    if "有向无环图" in prompt:
        print("   ✅ DAG说明已添加")
    else:
        print("   ❌ DAG说明未添加")
    
    print("\n4. 提示词预览（前500字符）:")
    print("-" * 80)
    print(prompt[:500])
    print("-" * 80)
    
    print("\n✅ 测试完成！提示词已保存到 prompts/ 目录")

if __name__ == "__main__":
    test_prompt_generation()
