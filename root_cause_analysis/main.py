"""
制造企业根因分析系统 - 主程序

使用DoWhy进行因果推断，分析生产效率下降的根因

场景说明：
- 制造企业有多个供应商提供不同零部件
- 有多个工厂，员工熟练度不同
- 付款流程影响供应商供货效率
- 目标：分析生产效率对比上个月降低的原因
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

from data_generator import create_demo_scenario, ManufacturingDataGenerator
from causal_analyzer import CausalAnalyzer, RootCauseAnalysisPipeline
from visualizer import CausalVisualizer


def main():
    """主程序入口"""
    print("="*70)
    print("制造企业生产效率根因分析系统")
    print("基于DoWhy因果推断框架")
    print("="*70)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n[步骤1] 生成模拟数据...")
    print("-"*70)
    
    df, anomaly_factors = create_demo_scenario()
    
    print(f"数据生成完成！")
    print(f"  - 总记录数: {len(df)}")
    print(f"  - 时间范围: {df['date'].min().strftime('%Y-%m-%d')} 至 {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"  - 工厂数量: {df['factory_id'].nunique()}")
    print(f"  - 供应商数量: {df['supplier_id'].nunique()}")
    print(f"\n异常因素配置:")
    for factor, enabled in anomaly_factors.items():
        status = "✓ 启用" if enabled else "✗ 未启用"
        print(f"  - {factor}: {status}")
    
    print("\n[步骤2] 数据探索性分析...")
    print("-"*70)
    
    print("\n各月份生产效率统计:")
    monthly_stats = df.groupby(['year', 'month']).agg({
        'production_efficiency': ['mean', 'std', 'min', 'max'],
        'production_volume': 'sum'
    }).round(4)
    print(monthly_stats)
    
    print("\n正常月份 vs 异常月份对比:")
    normal_data = df[~df['is_anomaly_month']]
    anomaly_data = df[df['is_anomaly_month']]
    
    print(f"  正常月份平均生产效率: {normal_data['production_efficiency'].mean():.4f}")
    print(f"  异常月份平均生产效率: {anomaly_data['production_efficiency'].mean():.4f}")
    efficiency_drop = (normal_data['production_efficiency'].mean() - anomaly_data['production_efficiency'].mean()) / normal_data['production_efficiency'].mean() * 100
    print(f"  效率下降幅度: {efficiency_drop:.2f}%")
    
    print("\n[步骤3] 运行根因分析流水线...")
    print("-"*70)
    
    pipeline = RootCauseAnalysisPipeline(df)
    results = pipeline.run_full_analysis()
    
    print("\n[步骤4] 因果效应详细分析...")
    print("-"*70)
    
    analyzer = CausalAnalyzer(df)
    
    print("\n分析: 付款及时性 -> 生产效率")
    print("-"*40)
    analyzer.create_causal_model(
        treatment="payment_timeliness",
        outcome="production_efficiency"
    )
    analyzer.identify_effect()
    estimate1 = analyzer.estimate_effect()
    
    print("\n分析: 供应商效率 -> 生产效率")
    print("-"*40)
    analyzer.create_causal_model(
        treatment="supplier_efficiency",
        outcome="production_efficiency"
    )
    analyzer.identify_effect()
    estimate2 = analyzer.estimate_effect()
    
    print("\n分析: 零部件可用性 -> 生产效率")
    print("-"*40)
    analyzer.create_causal_model(
        treatment="parts_availability",
        outcome="production_efficiency"
    )
    analyzer.identify_effect()
    estimate3 = analyzer.estimate_effect()
    
    print("\n[步骤5] 驳斥检验（验证因果推断稳健性）...")
    print("-"*70)
    
    analyzer.create_causal_model(
        treatment="supplier_efficiency",
        outcome="production_efficiency"
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
    
    visualizer = CausalVisualizer(figsize=(12, 8))
    
    print("  生成效率趋势图...")
    fig1 = visualizer.plot_efficiency_trend(df, f"{output_dir}/efficiency_trend.png")
    
    print("  生成指标对比图...")
    fig2 = visualizer.plot_metrics_comparison(results['comparison'], f"{output_dir}/metrics_comparison.png")
    
    print("  生成因果效应图...")
    fig3 = visualizer.plot_causal_effects(results['causal_analysis'], f"{output_dir}/causal_effects.png")
    
    print("  生成供应商分析图...")
    fig4 = visualizer.plot_supplier_analysis(df, f"{output_dir}/supplier_analysis.png")
    
    print("  生成相关性热力图...")
    fig5 = visualizer.plot_correlation_heatmap(df, f"{output_dir}/correlation_heatmap.png")
    
    print("  生成工厂对比图...")
    fig6 = visualizer.plot_factory_comparison(df, f"{output_dir}/factory_comparison.png")
    
    print("  生成综合仪表板...")
    fig7 = visualizer.create_dashboard(
        df, 
        results['comparison'], 
        results['causal_analysis'],
        f"{output_dir}/dashboard.png"
    )
    
    print("\n[步骤7] 保存分析结果...")
    print("-"*70)
    
    df.to_csv(f"{output_dir}/production_data.csv", index=False, encoding='utf-8-sig')
    results['comparison'].to_csv(f"{output_dir}/metrics_comparison.csv", index=False, encoding='utf-8-sig')
    results['causal_analysis'].to_csv(f"{output_dir}/causal_analysis_results.csv", index=False, encoding='utf-8-sig')
    
    print("分析结果已保存到 output/ 目录")
    
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
    print("单一因果分析演示")
    print("="*70)
    
    df, _ = create_demo_scenario()
    
    analyzer = CausalAnalyzer(df)
    
    print("\n因果图结构:")
    print(analyzer.build_causal_graph())
    
    print("\n创建因果模型: payment_timeliness -> production_efficiency")
    model = analyzer.create_causal_model(
        treatment="payment_timeliness",
        outcome="production_efficiency"
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
