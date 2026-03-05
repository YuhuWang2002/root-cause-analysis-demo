"""
真实场景中的反事实分析 - 与模拟方法的对比

本项目使用模拟方法（直接构造反事实数据）用于演示，
但在真实场景中，我们需要从实际数据推断反事实结果。
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class RealWorldCounterfactualAnalyzer:
    """真实场景的反事实分析器"""
    
    def __init__(self, actual_data: pd.DataFrame):
        """
        初始化分析器
        
        Args:
            actual_data: 实际观察到的数据（只有一种情况）
        """
        self.actual_data = actual_data
        self.causal_model = None
        self.estimate = None
        
    def demonstrate_difference(self):
        """演示模拟方法 vs 真实方法的区别"""
        
        print("="*80)
        print("模拟方法 vs 真实方法的关键区别")
        print("="*80)
        
        print("\n【模拟方法】（本项目使用）")
        print("-" * 80)
        print("✅ 我们可以控制数据生成过程")
        print("✅ 我们可以同时生成实际数据和反事实数据")
        print("✅ 我们知道真实的因果效应")
        print("✅ 适用于：演示、教学、方法验证")
        print("\n代码示例：")
        print("""
# 模拟方法：直接生成两种数据
actual_data = generate_data(product_b_uses_component_a=0)
counterfactual_data = generate_data(product_b_uses_component_a=1)

# 直接对比
effect = actual_data['inventory'].mean() - counterfactual_data['inventory'].mean()
        """)
        
        print("\n【真实方法】（实际业务中使用）")
        print("-" * 80)
        print("❌ 我们无法控制数据生成过程")
        print("❌ 我们只能观察到一种情况（实际发生的）")
        print("❌ 我们不知道真实的因果效应，需要估计")
        print("✅ 适用于：真实业务决策、政策评估")
        print("\n代码示例：")
        print("""
# 真实方法：只有实际数据，需要推断反事实
actual_data = load_historical_data()  # 只有这个

# 建立因果模型
model = CausalModel(data=actual_data, treatment=..., outcome=..., graph=...)

# 推断反事实结果（不是真实观察到的）
estimate = model.estimate_effect()
counterfactual = model.predict_counterfactual(intervention=...)
        """)
        
        print("\n" + "="*80)
        print("关键问题：在真实场景中，我们如何推断反事实？")
        print("="*80)
        
    def method_real_world_causal_inference(self):
        """
        真实场景方法：因果推断
        
        在真实场景中，我们：
        1. 只有实际数据（product_b_uses_component_a = 0）
        2. 无法观察到反事实（product_b_uses_component_a = 1）
        3. 需要通过因果模型推断反事实结果
        """
        print("\n" + "="*80)
        print("真实场景方法：因果推断（DoWhy）")
        print("="*80)
        
        print("\n步骤1：我们只有实际数据")
        print("-" * 80)
        print(f"实际数据样本量: {len(self.actual_data)}")
        print(f"product_b_uses_component_a 的值: {self.actual_data['product_b_uses_component_a'].unique()}")
        print("⚠️ 注意：历史数据中 product_b_uses_component_a 全为 0")
        
        print("\n步骤2：建立因果模型")
        print("-" * 80)
        print("from dowhy import CausalModel")
        print()
        print('causal_graph = """')
        print("digraph {")
        print("    product_a_sales -> component_a_consumption;")
        print("    product_b_sales -> component_a_consumption;")
        print("    product_b_uses_component_a -> component_a_consumption;")
        print("    component_a_consumption -> component_a_inventory;")
        print("}")
        print('"""')
        print()
        print("model = CausalModel(")
        print("    data=self.actual_data,  # 只有实际数据")
        print("    treatment='product_b_uses_component_a',")
        print("    outcome='component_a_inventory',")
        print("    graph=causal_graph")
        print(")")
        
        print("\n步骤3：识别因果效应")
        print("-" * 80)
        print("""
identified_estimand = model.identify_effect()
print("识别方法:", identified_estimand.estimand_type)
        """)
        
        print("\n步骤4：估计因果效应")
        print("-" * 80)
        print("""
estimate = model.estimate_effect(
    identified_estimand,
    method_name="backdoor.linear_regression"
)
print("因果效应估计值:", estimate.value)
        """)
        
        print("\n步骤5：推断反事实结果（关键步骤）")
        print("-" * 80)
        print("""
# 这不是真实观察到的，而是模型推断的
counterfactual_data = self.actual_data.copy()
counterfactual_data['product_b_uses_component_a'] = 1

# 使用因果模型预测反事实结果
counterfactual_inventory = predict_with_causal_model(
    model, 
    counterfactual_data
)

print("实际库存:", self.actual_data['component_a_inventory'].mean())
print("反事实库存（推断）:", counterfactual_inventory.mean())
print("⚠️ 注意：反事实库存是推断出来的，不是真实观察到的")
        """)
        
        print("\n步骤6：驳斥检验（验证推断的可靠性）")
        print("-" * 80)
        print("""
refutation = model.refute_estimate(
    identified_estimand,
    estimate,
    method_name="placebo_treatment_refuter"
)
print("安慰剂检验结果:", refutation)
        """)
        
    def method_comparison_table(self):
        """方法对比表"""
        print("\n" + "="*80)
        print("方法对比总结")
        print("="*80)
        
        comparison = """
┌─────────────────────┬──────────────────────┬──────────────────────┐
│       方面          │   模拟方法（本项目）  │   真实方法（业务）    │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ 数据来源            │ 直接生成              │ 历史观察              │
│ 反事实数据          │ 真实模拟              │ 模型推断              │
│ 因果效应            │ 已知真值              │ 需要估计              │
│ 可靠性              │ 100%准确              │ 依赖模型假设          │
│ 适用场景            │ 演示、教学、验证      │ 真实业务决策          │
│ 数据要求            │ 可以控制              │ 只能观察              │
│ 实施难度            │ 简单                  │ 较难                  │
│ 结果可信度          │ 绝对可信              │ 需要验证              │
└─────────────────────┴──────────────────────┴──────────────────────┘
        """
        
        print(comparison)
        
        print("\n关键要点：")
        print("1. 本项目使用模拟方法是为了教学和演示")
        print("2. 在真实场景中，我们只能观察到一种情况")
        print("3. 需要通过因果推断方法来估计反事实结果")
        print("4. 结果的可靠性依赖于模型假设的正确性")
        
    def practical_example(self):
        """实际案例"""
        print("\n" + "="*80)
        print("实际案例：产品B是否应该使用部件A？")
        print("="*80)
        
        print("\n【问题背景】")
        print("-" * 80)
        print("• 现状：产品B未使用部件A（历史全为0）")
        print("• 问题：部件A库存高")
        print("• 问题：如果产品B使用部件A，库存会降低多少？")
        
        print("\n【数据情况】")
        print("-" * 80)
        print("• 我们只有历史数据（product_b_uses_component_a = 0）")
        print("• 我们无法真正让产品B使用部件A（这是假设）")
        print("• 我们需要推断：如果产品B使用部件A，库存会是多少？")
        
        print("\n【解决方案】")
        print("-" * 80)
        print("""
# 真实场景中的做法：

# 1. 收集历史数据
actual_data = pd.read_csv('inventory_history.csv')

# 2. 建立因果模型
model = CausalModel(
    data=actual_data,
    treatment='product_b_uses_component_a',
    outcome='component_a_inventory',
    graph=causal_graph
)

# 3. 估计因果效应
estimate = model.estimate_effect()

# 4. 推断反事实结果（关键）
counterfactual_inventory = predict_counterfactual(
    model, 
    intervention={'product_b_uses_component_a': 1}
)

# 5. 量化影响
reduction = (actual_inventory - counterfactual_inventory) / actual_inventory * 100

# 6. 支持决策
if reduction > 20:
    print("建议：修改产品B的BOM，让产品B使用部件A")
    print(f"预期效果：库存降低 {reduction:.1f}%")
        """)
        
        print("\n【注意事项】")
        print("-" * 80)
        print("⚠️ 反事实结果是推断出来的，不是真实观察到的")
        print("⚠️ 推断的可靠性依赖于模型假设的正确性")
        print("⚠️ 需要进行敏感性分析和稳健性检验")
        print("⚠️ 需要结合业务知识验证结果的合理性")


def main():
    """主演示函数"""
    
    # 加载实际数据
    actual_data = pd.read_csv('inventory_actual_data.csv')
    
    # 创建分析器
    analyzer = RealWorldCounterfactualAnalyzer(actual_data)
    
    # 演示区别
    analyzer.demonstrate_difference()
    
    # 展示真实方法
    analyzer.method_real_world_causal_inference()
    
    # 方法对比
    analyzer.method_comparison_table()
    
    # 实际案例
    analyzer.practical_example()
    
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    print("""
本项目使用模拟方法的原因：
1. 教学目的：让学生直观理解反事实的概念
2. 方法验证：验证因果推断方法的有效性
3. 完整展示：展示完整的因果推断流程

在真实场景中：
1. 我们只有实际数据，无法观察到反事实
2. 需要通过因果模型推断反事实结果
3. 结果的可靠性依赖于模型假设
4. 需要进行敏感性分析和稳健性检验

关键要点：
✅ 反事实分析是因果推断的核心
✅ 我们只能观察到一种情况，需要推断另一种情况
✅ 因果推断方法帮助我们科学地估计反事实结果
✅ 结果需要结合业务知识验证合理性
    """)


if __name__ == "__main__":
    main()
