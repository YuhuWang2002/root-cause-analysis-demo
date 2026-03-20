#!/usr/bin/env python3
"""
测试提示词保存功能
"""

import os
import sys
import pandas as pd
from llm_explainer import LLMExplainer

# 创建测试数据
def create_test_data():
    # 创建测试数据
    dates = pd.date_range('2024-01-01', '2024-12-31', freq='ME')
    actual_data = pd.DataFrame({
        'date': dates,
        'kunlun_2280_sales': [100, 105, 110, 108, 105, 100, 95, 90, 85, 80, 60, 55],
        'server_2288hv7_sales': [80, 82, 85, 83, 80, 81, 82, 80, 79, 80, 81, 82],
        'pac900s12_b2_1_inventory': [100, 105, 110, 115, 120, 130, 140, 150, 160, 170, 180, 200]
    })
    
    counterfactual_data = pd.DataFrame({
        'date': dates,
        'kunlun_2280_sales': [100, 105, 110, 108, 105, 100, 95, 90, 85, 80, 60, 55],
        'server_2288hv7_sales': [80, 82, 85, 83, 80, 81, 82, 80, 79, 80, 81, 82],
        'pac900s12_b2_1_inventory': [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155]
    })
    
    return actual_data, counterfactual_data

# 测试提示词保存
def test_prompt_saving():
    print("测试提示词保存功能...")
    
    # 创建测试数据
    actual_data, counterfactual_data = create_test_data()
    
    # 测试分析结果
    analysis_results = {
        'counterfactual_analysis': {
            'actual_inventory_mean': 145.83,
            'counterfactual_inventory_mean': 127.5,
            'inventory_reduction': 18.33,
            'reduction_percentage': 12.57,
            'decline_period_actual_inventory': 190.0,
            'decline_period_counterfactual_inventory': 155.0,
            'decline_period_reduction': 35.0,
            'is_root_cause': False
        },
        'causal_effect': -0.35
    }
    
    # 创建LLM解释器
    explainer = LLMExplainer()
    
    # 测试根因分析提示词
    print("\n1. 测试根因分析提示词保存...")
    try:
        # 这里不会实际调用API，因为没有配置API密钥
        result = explainer.generate_root_cause_explanation(
            analysis_results, 
            actual_data, 
            counterfactual_data
        )
        print("根因分析提示词保存测试完成")
    except Exception as e:
        print(f"根因分析测试错误: {e}")
    
    # 测试解决方案提示词
    print("\n2. 测试解决方案提示词保存...")
    try:
        # 这里不会实际调用API，因为没有配置API密钥
        result = explainer.generate_solution(
            analysis_results, 
            actual_data, 
            counterfactual_data
        )
        print("解决方案提示词保存测试完成")
    except Exception as e:
        print(f"解决方案测试错误: {e}")
    
    # 检查提示词文件是否生成
    print("\n3. 检查提示词文件...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(current_dir, "prompts")
    
    if os.path.exists(prompts_dir):
        files = os.listdir(prompts_dir)
        prompt_files = [f for f in files if f.endswith('.txt')]
        print(f"在 {prompts_dir} 中找到 {len(prompt_files)} 个提示词文件:")
        for file in prompt_files:
            print(f"  - {file}")
        
        # 检查是否有带时间戳的文件
        timestamp_files = [f for f in prompt_files if 'root_cause_prompt_' in f or 'solution_prompt_' in f]
        if timestamp_files:
            print(f"\n找到 {len(timestamp_files)} 个带时间戳的提示词文件:")
            for file in timestamp_files:
                print(f"  - {file}")
        else:
            print("\n未找到带时间戳的提示词文件")
    else:
        print(f"提示词目录 {prompts_dir} 不存在")

if __name__ == "__main__":
    test_prompt_saving()
