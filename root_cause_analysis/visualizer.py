"""
制造企业根因分析 - 可视化模块
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CausalVisualizer:
    """因果分析可视化器"""
    
    def __init__(self, figsize: tuple = (12, 8)):
        self.figsize = figsize
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545',
            'info': '#17A2B8'
        }
    
    def plot_efficiency_trend(self, data: pd.DataFrame, save_path: str = None):
        """绘制生产效率趋势图"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        daily_efficiency = data.groupby(['year', 'month', 'date'])['production_efficiency'].mean().reset_index()
        daily_efficiency['date_str'] = daily_efficiency['date'].dt.strftime('%Y-%m-%d')
        
        colors = []
        for _, row in daily_efficiency.iterrows():
            if row['month'] == 12:
                colors.append(self.colors['danger'])
            else:
                colors.append(self.colors['primary'])
        
        bars = ax.bar(range(len(daily_efficiency)), 
                      daily_efficiency['production_efficiency'],
                      color=colors, alpha=0.7)
        
        ax.axhline(y=daily_efficiency['production_efficiency'].mean(), 
                   color=self.colors['warning'], linestyle='--', 
                   label='平均效率', linewidth=2)
        
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('生产效率', fontsize=12)
        ax.set_title('生产效率趋势分析', fontsize=14, fontweight='bold')
        
        tick_positions = range(0, len(daily_efficiency), 7)
        tick_labels = [daily_efficiency.iloc[i]['date_str'] for i in tick_positions]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')
        
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_metrics_comparison(self, comparison_df: pd.DataFrame, save_path: str = None):
        """绘制指标对比图"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        metrics = comparison_df[comparison_df['metric'] != 'production_efficiency'].copy()
        
        ax1 = axes[0]
        x = range(len(metrics))
        width = 0.35
        
        bars1 = ax1.bar([i - width/2 for i in x], metrics['normal_mean'], 
                        width, label='正常月份', color=self.colors['primary'], alpha=0.8)
        bars2 = ax1.bar([i + width/2 for i in x], metrics['anomaly_mean'], 
                        width, label='异常月份', color=self.colors['danger'], alpha=0.8)
        
        ax1.set_xlabel('指标', fontsize=11)
        ax1.set_ylabel('平均值', fontsize=11)
        ax1.set_title('正常月份 vs 异常月份指标对比', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(metrics['metric'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        ax2 = axes[1]
        colors = [self.colors['danger'] if c < 0 else self.colors['success'] 
                  for c in metrics['change_percent']]
        
        bars = ax2.barh(metrics['metric'], metrics['change_percent'], color=colors, alpha=0.8)
        
        ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_xlabel('变化百分比 (%)', fontsize=11)
        ax2.set_title('指标变化幅度', fontsize=12, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        for i, (idx, row) in enumerate(metrics.iterrows()):
            ax2.text(row['change_percent'] + 0.5 if row['change_percent'] > 0 else row['change_percent'] - 0.5,
                     i, f"{row['change_percent']:.1f}%",
                     va='center', ha='left' if row['change_percent'] > 0 else 'right',
                     fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_causal_effects(self, causal_results: pd.DataFrame, save_path: str = None):
        """绘制因果效应分析结果"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        valid_results = causal_results[causal_results['causal_effect'].notna()].copy()
        valid_results = valid_results.sort_values('causal_effect', key=abs, ascending=True)
        
        colors = [self.colors['success'] if e > 0 else self.colors['danger'] 
                  for e in valid_results['causal_effect']]
        
        y_pos = range(len(valid_results))
        
        ax.barh(y_pos, valid_results['causal_effect'], 
                color=colors, alpha=0.8, height=0.6)
        
        ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(valid_results['cause'])
        ax.set_xlabel('因果效应值', fontsize=11)
        ax.set_title('各因素对生产效率的因果效应', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        ax.text(0.02, 0.98, '正值: 正向影响\n负值: 负向影响',
                transform=ax.transAxes, fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_supplier_analysis(self, data: pd.DataFrame, save_path: str = None):
        """绘制供应商分析图"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        ax1 = axes[0]
        supplier_eff = data.groupby(['supplier_name', 'is_anomaly_month'])['supplier_efficiency'].mean().unstack()
        supplier_eff.columns = ['正常月份', '异常月份']
        
        x = range(len(supplier_eff))
        width = 0.35
        
        bars1 = ax1.bar([i - width/2 for i in x], supplier_eff['正常月份'],
                        width, label='正常月份', color=self.colors['primary'], alpha=0.8)
        bars2 = ax1.bar([i + width/2 for i in x], supplier_eff['异常月份'],
                        width, label='异常月份', color=self.colors['danger'], alpha=0.8)
        
        ax1.set_xlabel('供应商', fontsize=11)
        ax1.set_ylabel('供应商效率', fontsize=11)
        ax1.set_title('各供应商效率对比', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels([s[:10] + '...' if len(s) > 10 else s for s in supplier_eff.index], 
                           rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        ax2 = axes[1]
        payment_data = data.groupby('is_anomaly_month')['payment_delay_days'].mean()
        
        labels = ['正常月份', '异常月份']
        colors = [self.colors['primary'], self.colors['danger']]
        
        bars = ax2.bar(labels, payment_data.values, color=colors, alpha=0.8)
        
        for bar, val in zip(bars, payment_data.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'{val:.1f}天', ha='center', va='bottom', fontsize=11)
        
        ax2.set_ylabel('平均付款延迟天数', fontsize=11)
        ax2.set_title('付款延迟对比', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_correlation_heatmap(self, data: pd.DataFrame, save_path: str = None):
        """绘制相关性热力图"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        numeric_cols = [
            'production_efficiency',
            'payment_timeliness',
            'supplier_efficiency',
            'parts_availability',
            'avg_employee_skill',
            'equipment_status',
            'capacity_utilization'
        ]
        
        corr_matrix = data[numeric_cols].corr()
        
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
                   cmap='RdBu_r', center=0, square=True,
                   linewidths=0.5, ax=ax,
                   cbar_kws={'shrink': 0.8})
        
        ax.set_title('变量相关性热力图', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_factory_comparison(self, data: pd.DataFrame, save_path: str = None):
        """绘制工厂对比图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        factory_eff = data.groupby(['factory_name', 'is_anomaly_month'])['production_efficiency'].mean().unstack()
        factory_eff.columns = ['正常月份', '异常月份']
        
        ax1 = axes[0, 0]
        x = range(len(factory_eff))
        width = 0.35
        
        ax1.bar([i - width/2 for i in x], factory_eff['正常月份'],
               width, label='正常月份', color=self.colors['primary'], alpha=0.8)
        ax1.bar([i + width/2 for i in x], factory_eff['异常月份'],
               width, label='异常月份', color=self.colors['danger'], alpha=0.8)
        
        ax1.set_xlabel('工厂', fontsize=11)
        ax1.set_ylabel('生产效率', fontsize=11)
        ax1.set_title('各工厂生产效率对比', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(factory_eff.index, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        ax2 = axes[0, 1]
        equipment_eff = data.groupby(['factory_name', 'equipment_age'])['production_efficiency'].mean().reset_index()
        
        scatter = ax2.scatter(equipment_eff['equipment_age'], 
                             equipment_eff['production_efficiency'],
                             s=100, c=self.colors['info'], alpha=0.7)
        
        for i, row in equipment_eff.iterrows():
            ax2.annotate(row['factory_name'], 
                        (row['equipment_age'], row['production_efficiency']),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        ax2.set_xlabel('设备年龄（年）', fontsize=11)
        ax2.set_ylabel('生产效率', fontsize=11)
        ax2.set_title('设备年龄与生产效率关系', fontsize=12, fontweight='bold')
        ax2.grid(alpha=0.3)
        
        ax3 = axes[1, 0]
        skill_eff = data.groupby('factory_name')['avg_employee_skill'].mean()
        
        ax3.barh(skill_eff.index, skill_eff.values, color=self.colors['success'], alpha=0.8)
        ax3.set_xlabel('平均员工技能水平', fontsize=11)
        ax3.set_title('各工厂员工技能水平', fontsize=12, fontweight='bold')
        ax3.grid(axis='x', alpha=0.3)
        
        ax4 = axes[1, 1]
        capacity_eff = data.groupby(['factory_name', 'is_anomaly_month'])['capacity_utilization'].mean().unstack()
        capacity_eff.columns = ['正常月份', '异常月份']
        
        ax4.bar([i - width/2 for i in x], capacity_eff['正常月份'],
               width, label='正常月份', color=self.colors['primary'], alpha=0.8)
        ax4.bar([i + width/2 for i in x], capacity_eff['异常月份'],
               width, label='异常月份', color=self.colors['danger'], alpha=0.8)
        
        ax4.set_xlabel('工厂', fontsize=11)
        ax4.set_ylabel('产能利用率', fontsize=11)
        ax4.set_title('各工厂产能利用率对比', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(capacity_eff.index, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_dashboard(self, 
                        data: pd.DataFrame,
                        comparison_df: pd.DataFrame,
                        causal_results: pd.DataFrame,
                        save_path: str = None):
        """创建综合仪表板"""
        fig = plt.figure(figsize=(20, 14))
        
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        ax1 = fig.add_subplot(gs[0, :2])
        daily_eff = data.groupby(['year', 'month', 'date'])['production_efficiency'].mean().reset_index()
        colors = [self.colors['danger'] if m == 12 else self.colors['primary'] 
                  for m in daily_eff['month']]
        ax1.bar(range(len(daily_eff)), daily_eff['production_efficiency'], color=colors, alpha=0.7)
        ax1.axhline(y=daily_eff['production_efficiency'].mean(), 
                   color=self.colors['warning'], linestyle='--', linewidth=2)
        ax1.set_title('生产效率趋势', fontsize=12, fontweight='bold')
        ax1.set_xlabel('天数')
        ax1.set_ylabel('效率')
        ax1.grid(axis='y', alpha=0.3)
        
        ax2 = fig.add_subplot(gs[0, 2])
        monthly_eff = data.groupby(['year', 'month'])['production_efficiency'].mean()
        labels = [f"{y}-{m}" for y, m in monthly_eff.index]
        colors = [self.colors['danger'] if m == 12 else self.colors['primary'] 
                  for y, m in monthly_eff.index]
        ax2.bar(labels, monthly_eff.values, color=colors, alpha=0.8)
        ax2.set_title('月度平均效率', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3)
        
        ax3 = fig.add_subplot(gs[1, 0])
        metrics = comparison_df[comparison_df['metric'] != 'production_efficiency'].head(5)
        colors = [self.colors['danger'] if c < 0 else self.colors['success'] 
                  for c in metrics['change_percent']]
        ax3.barh(metrics['metric'], metrics['change_percent'], color=colors, alpha=0.8)
        ax3.axvline(x=0, color='black', linewidth=0.5)
        ax3.set_title('指标变化幅度', fontsize=12, fontweight='bold')
        ax3.set_xlabel('变化%')
        ax3.grid(axis='x', alpha=0.3)
        
        ax4 = fig.add_subplot(gs[1, 1])
        valid_causal = causal_results[causal_results['causal_effect'].notna()].sort_values(
            'causal_effect', key=abs, ascending=True)
        colors = [self.colors['success'] if e > 0 else self.colors['danger'] 
                  for e in valid_causal['causal_effect']]
        ax4.barh(valid_causal['cause'], valid_causal['causal_effect'], color=colors, alpha=0.8)
        ax4.axvline(x=0, color='black', linewidth=0.5)
        ax4.set_title('因果效应分析', fontsize=12, fontweight='bold')
        ax4.set_xlabel('效应值')
        ax4.grid(axis='x', alpha=0.3)
        
        ax5 = fig.add_subplot(gs[1, 2])
        supplier_eff = data.groupby(['supplier_type', 'is_anomaly_month'])['supplier_efficiency'].mean().unstack()
        supplier_eff.columns = ['正常', '异常']
        x = range(len(supplier_eff))
        ax5.bar([i - 0.2 for i in x], supplier_eff['正常'], 0.4, 
               label='正常', color=self.colors['primary'], alpha=0.8)
        ax5.bar([i + 0.2 for i in x], supplier_eff['异常'], 0.4,
               label='异常', color=self.colors['danger'], alpha=0.8)
        ax5.set_xticks(x)
        ax5.set_xticklabels(supplier_eff.index)
        ax5.set_title('供应商类型效率', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(axis='y', alpha=0.3)
        
        ax6 = fig.add_subplot(gs[2, :])
        ax6.axis('off')
        
        summary_text = "根因分析结论\n\n"
        summary_text += "="*50 + "\n\n"
        
        eff_change = comparison_df[comparison_df['metric'] == 'production_efficiency']['change_percent'].values[0]
        summary_text += f"• 生产效率变化: {eff_change:.2f}%\n\n"
        
        top_declines = comparison_df[
            (comparison_df['metric'] != 'production_efficiency') & 
            (comparison_df['change_percent'] < 0)
        ].head(3)
        
        summary_text += "• 主要下降因素:\n"
        for _, row in top_declines.iterrows():
            summary_text += f"  - {row['metric']}: {row['change_percent']:.2f}%\n"
        
        summary_text += "\n• 建议措施:\n"
        summary_text += "  1. 优化付款流程，缩短付款周期\n"
        summary_text += "  2. 加强核心供应商管理\n"
        summary_text += "  3. 建立实时监控预警系统\n"
        
        ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
                fontsize=11, verticalalignment='top',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
        
        fig.suptitle('制造企业生产效率根因分析仪表板', fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
