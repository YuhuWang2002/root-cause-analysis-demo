#!/usr/bin/env python3
"""
测试 LLMExplainer 类的基本功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/web')

from llm_explainer import LLMExplainer
import pandas as pd

# 测试 1: 初始化 LLMExplainer 实例
def test_initialization():
    print("测试 1: 初始化 LLMExplainer 实例")
    try:
        explainer = LLMExplainer()
        print("✓ 成功初始化 LLMExplainer 实例")
        return True
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return False

# 测试 2: 测试 _build_prompt 方法（无因果图）
def test_build_prompt_no_causal_graph():
    print("\n测试 2: 测试 _build_prompt 方法（无因果图）")
    try:
        explainer = LLMExplainer()
        # 创建模拟数据
        analysis_results = {}
        comparison_df = pd.DataFrame({
            'metric': ['production_efficiency', 'payment_timeliness'],
            'change_percent': [-5.0, -10.0]
        })
        causal_results = pd.DataFrame({
            'cause': ['payment_timeliness'],
            'causal_effect': [-0.8]
        })
        # 调用 _build_prompt 方法，不提供因果图
        explainer._build_prompt(analysis_results, comparison_df, causal_results, causal_graph=None)
        print("✗ 应该抛出 ValueError 但没有")
        return False
    except ValueError as e:
        print(f"✓ 正确抛出 ValueError: {e}")
        return True
    except Exception as e:
        print(f"✗ 抛出了意外的异常: {e}")
        return False

# 测试 3: 测试 _build_prompt 方法（有因果图）
def test_build_prompt_with_causal_graph():
    print("\n测试 3: 测试 _build_prompt 方法（有因果图）")
    try:
        explainer = LLMExplainer()
        # 创建模拟数据
        analysis_results = {}
        comparison_df = pd.DataFrame({
            'metric': ['production_efficiency', 'payment_timeliness'],
            'change_percent': [-5.0, -10.0]
        })
        causal_results = pd.DataFrame({
            'cause': ['payment_timeliness'],
            'causal_effect': [-0.8]
        })
        # 提供因果图
        causal_graph = "digraph G { payment_timeliness -> supplier_efficiency -> parts_availability -> production_efficiency }"
        # 调用 _build_prompt 方法
        prompt = explainer._build_prompt(analysis_results, comparison_df, causal_results, causal_graph=causal_graph)
        print("✓ 成功构建提示词")
        print(f"提示词长度: {len(prompt)}")
        return True
    except Exception as e:
        print(f"✗ 构建提示词失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试 LLMExplainer 类...")
    print("=" * 60)
    
    tests = [
        test_initialization,
        test_build_prompt_no_causal_graph,
        test_build_prompt_with_causal_graph
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)
