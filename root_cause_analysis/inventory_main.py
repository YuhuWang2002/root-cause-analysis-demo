"""
制造企业根因分析系统 - 库存死货问题主程序

使用DoWhy进行因果推断，分析库存死货问题的根因

场景说明：
- 制造企业采购部件，有的部件可以被不同产品使用
- 部件需要保证一定的库存水平，有消耗和补充
- 问题：产品可以用同样功能的不同型号/供应商的部件
- 但生产工厂不知道有可代替的部件，导致某些部件成为死库存，占用大量资金
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

from inventory_data_generator import create_inventory_demo_scenario, InventoryDataGenerator
from inventory_causal_analyzer import InventoryCausalAnalyzer, InventoryRootCauseAnalysisPipeline
from inventory_visualizer import InventoryVisualizer


def main():
    """主程序入口"""
    print("="*70)
    print("制造企业库存死货问题根因分析系统")
    print("基于DoWhy因果推断框架")
    print("="*70)
    
    output_dir = "output_inventory"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n[步骤1] 生成模拟数据...")
    print("-"*70)
    
    df, anomaly_factors = create_inventory_demo_scenario()
    
    print(f"数据生成完成！")
    print(f"  - 总记录数: {len(df)}")
    print(f"  - 时间范围: {df['date'].min().strftime('%Y-%m-%d')} 至 {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"  - 工厂数量: {df['factory_id'].nunique()}")
    print(f"  - 产品数量: {df['product_id'].nunique()}")
    print(f"  - 部件数量: {df['part_id'].nunique()}")
    print(f"\n异常因素配置:")
    for factor, enabled in anomaly_factors.items():
        status = "✓ 启用" if enabled else "✗ 未启用"
        print(f"  - {factor}: {status}")
    
    print("\n[步骤2] 数据探索性分析...")
    print("-"*70)
    
    print("\n各月份死库存统计:")
    monthly_stats = df.groupby(['year', 'month']).agg({
        'dead_stock_amount': ['mean', 'sum'],
        'capital_tied': ['mean', 'sum'],
        'stock_turnover': 'mean'
    }).round(4)
    print(monthly_stats)
    
    print("\n正常月份 vs 异常月份对比:")
    normal_data = df[~df['is_anomaly_month']]
    anomaly_data = df[df['is_anomaly_month']]
    
    print(f"  正常月份平均死库存: {normal_data['dead_stock_amount'].mean():.4f}")
    print(f"  异常月份平均死库存: {anomaly_data['dead_stock_amount'].mean():.4f}")
    dead_stock_increase = (anomaly_data['dead_stock_amount'].mean() - normal_data['dead_stock_amount'].mean()) / normal_data['dead_stock_amount'].mean() * 100
    print(f"  死库存增长幅度: {dead_stock_increase:.2f}%")
    
    print(f"\n  正常月份平均资金占用: {normal_data['capital_tied'].mean():.2f}")
    print(f"  异常月份平均资金占用: {anomaly_data['capital_tied'].mean():.2f}")
    capital_increase = (anomaly_data['capital_tied'].mean() - normal_data['capital_tied'].mean()) / normal_data['capital_tied'].mean() * 100
    print(f"  资金占用增长幅度: {capital_increase:.2f}%")
    
    print("\n[步骤3] 运行根因分析流水线...")
    print("-"*70)
    
    pipeline = InventoryRootCauseAnalysisPipeline(df)
    results = pipeline.run_full_analysis()
    
    print("\n[步骤4] 因果效应详细分析...")
    print("-"*70)
    
    analyzer = InventoryCausalAnalyzer(df)
    
    print("\n分析: 替代部件意识 -> 死库存")
    print("-"*40)
    analyzer.create_causal_model(
        treatment="substitute_awareness",
        outcome="dead_stock_amount"
    )
    analyzer.identify_effect()
    estimate1 = analyzer.estimate_effect()
    
    print("\n分析: 需求因素 -> 死库存")
    print("-"*40)
    analyzer.create_causal_model(
        treatment="demand_factor",
        outcome="dead_stock_amount"
    )
    analyzer.identify_effect()
    estimate2 = analyzer.estimate_effect()
    
    print("\n分析: 死库存 -> 资金占用")
    print("-"*40)
    analyzer.create_causal_model(
        treatment="dead_stock_amount",
        outcome="capital_tied"
    )
    analyzer.identify_effect()
    estimate3 = analyzer.estimate_effect()
    
    print("\n[步骤5] 驳斥检验（验证因果推断稳健性）...")
    print("-"*70)
    
    analyzer.create_causal_model(
        treatment="substitute_awareness",
        outcome="dead_stock_amount"
    )
    analyzer.identify_effect()
    analyzer.estimate_effect()
    
    refutation_results = analyzer.refute_estimate(
        placebo_refutation=True,
        random_common_cause=True,
        data_subset_refuter=True
    )
    
    print("\n[步骤6] 生成可视化报告...")
    print("-"*70)
    
    visualizer = InventoryVisualizer(figsize=(12, 8))
    
    print("  生成死库存趋势图...")
    fig1 = visualizer.plot_dead_stock_trend(df, f"{output_dir}/dead_stock_trend.png")
    
    print("  生成指标对比图...")
    fig2 = visualizer.plot_metrics_comparison(results['comparison'], f"{output_dir}/metrics_comparison.png")
    
    print("  生成因果效应图...")
    fig3 = visualizer.plot_causal_effects(results['causal_analysis'], f"{output_dir}/causal_effects.png")
    
    print("  生成部件分析图...")
    fig4 = visualizer.plot_part_analysis(df, f"{output_dir}/part_analysis.png")
    
    print("  生成相关性热力图...")
    fig5 = visualizer.plot_correlation_heatmap(df, f"{output_dir}/correlation_heatmap.png")
    
    print("  生成综合仪表板...")
    fig6 = visualizer.create_dashboard(
        df, 
        results['comparison'], 
        results['causal_analysis'],
        results['capital_analysis'],
        f"{output_dir}/dashboard.png"
    )
    
    print("\n[步骤7] 保存分析结果...")
    print("-"*70)
    
    df.to_csv(f"{output_dir}/inventory_data.csv", index=False, encoding='utf-8-sig')
    results['comparison'].to_csv(f"{output_dir}/metrics_comparison.csv", index=False, encoding='utf-8-sig')
    results['causal_analysis'].to_csv(f"{output_dir}/causal_analysis_results.csv", index=False, encoding='utf-8-sig')
    results['capital_analysis'].to_csv(f"{output_dir}/capital_analysis_results.csv", index=False, encoding='utf-8-sig')
    
    print("分析结果已保存到 output_inventory/ 目录")
    
    print("\n" + "="*70)
    print("分析完成！")
    print("="*70)
    
    print(results['summary'])
    
    print("\n生成的文件:")
    for file in os.listdir(output_dir):
        print(f"  - {output_dir}/{file}")
    
    return results


def demo_single_cause_analysis():
    """演示单一因果分析"""
    print("\n" + "="*70)
    print("单一因果分析演示 - 库存死货问题")
    print("="*70)
    
    df, _ = create_inventory_demo_scenario()
    
    analyzer = InventoryCausalAnalyzer(df)
    
    print("\n因果图结构:")
    print(analyzer.build_causal_graph())
    
    print("\n创建因果模型: substitute_awareness -> dead_stock_amount")
    model = analyzer.create_causal_model(
        treatment="substitute_awareness",
        outcome="dead_stock_amount"
    )
    
    print("\n因果图可视化:")
    model.view_model()
    
    print("\n识别因果效应...")
    identified_estimand = analyzer.identify_effect()
    
    print("\n估计因果效应...")
    estimate = analyzer.estimate_effect()
    
    print("\n驳斥检验...")
    refutation = analyzer.refute_estimate()
    
    return analyzer


if __name__ == "__main__":
    results = main()
    
    print("\n" + "="*70)
    print("提示: 运行 demo_single_cause_analysis() 可查看单一因果分析详细演示")
    print("="*70)
