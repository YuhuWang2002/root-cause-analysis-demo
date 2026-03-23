"""
制造企业根因分析 - 库存死货问题可视化模块
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


class InventoryVisualizer:
    """库存死货问题可视化器"""
    
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
    
    def plot_dead_stock_trend(self, data: pd.DataFrame, save_path: str = None):
        """绘制死库存趋势图"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        daily_dead_stock = data.groupby(['year', 'month', 'date'])['dead_stock_amount'].mean().reset_index()
        daily_dead_stock['date_str'] = daily_dead_stock['date'].dt.strftime('%Y-%m-%d')
        
        colors = []
        for _, row in daily_dead_stock.iterrows():
            if row['month'] == 12:
                colors.append(self.colors['danger'])
            else:
                colors.append(self.colors['primary'])
        
        bars = ax.bar(range(len(daily_dead_stock)), 
                      daily_dead_stock['dead_stock_amount'],
                      color=colors, alpha=0.7)
        
        ax.axhline(y=daily_dead_stock['dead_stock_amount'].mean(), 
                   color=self.colors['warning'], linestyle='--', 
                   label='平均死库存', linewidth=2)
        
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('死库存数量', fontsize=12)
        ax.set_title('死库存趋势分析', fontsize=14, fontweight='bold')
        
        tick_positions = range(0, len(daily_dead_stock), 7)
        tick_labels = [daily_dead_stock.iloc[i]['date_str'] for i in tick_positions]
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
        
        metrics = comparison_df[~comparison_df['metric'].isin(['dead_stock_amount', 'capital_tied'])].copy()
        
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
        ax.set_title('各因素对死库存的因果效应', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        ax.text(0.02, 0.98, '正值: 正向影响\n负值: 负向影响',
                transform=ax.transAxes, fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_part_analysis(self, data: pd.DataFrame, save_path: str = None):
        """绘制部件分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 各部件死库存情况
        ax1 = axes[0, 0]
        part_dead_stock = data.groupby(['part_name', 'is_anomaly_month'])['dead_stock_amount'].mean().unstack()
        part_dead_stock.columns = ['正常月份', '异常月份']
        
        x = range(len(part_dead_stock))
        width = 0.35
        
        ax1.bar([i - width/2 for i in x], part_dead_stock['正常月份'],
                width, label='正常月份', color=self.colors['primary'], alpha=0.8)
        ax1.bar([i + width/2 for i in x], part_dead_stock['异常月份'],
                width, label='异常月份', color=self.colors['danger'], alpha=0.8)
        
        ax1.set_xlabel('部件', fontsize=11)
        ax1.set_ylabel('死库存数量', fontsize=11)
        ax1.set_title('各部件死库存对比', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(part_dead_stock.index, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 各部件资金占用
        ax2 = axes[0, 1]
        part_capital = data.groupby(['part_name', 'is_anomaly_month'])['capital_tied'].mean().unstack()
        part_capital.columns = ['正常月份', '异常月份']
        
        ax2.bar([i - width/2 for i in x], part_capital['正常月份'],
                width, label='正常月份', color=self.colors['primary'], alpha=0.8)
        ax2.bar([i + width/2 for i in x], part_capital['异常月份'],
                width, label='异常月份', color=self.colors['danger'], alpha=0.8)
        
        ax2.set_xlabel('部件', fontsize=11)
        ax2.set_ylabel('资金占用', fontsize=11)
        ax2.set_title('各部件资金占用对比', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(part_dead_stock.index, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # 替代部件使用情况
        ax3 = axes[1, 0]
        substitute_usage = data.groupby(['is_anomaly_month', 'has_substitute']).size().unstack()
        substitute_usage.columns = ['无替代', '有替代']
        
        labels = ['正常月份', '异常月份']
        x = range(len(substitute_usage))
        
        ax3.bar([i - width/2 for i in x], substitute_usage['无替代'],
                width, label='无替代', color=self.colors['danger'], alpha=0.8)
        ax3.bar([i + width/2 for i in x], substitute_usage['有替代'],
                width, label='有替代', color=self.colors['success'], alpha=0.8)
        
        ax3.set_xlabel('月份类型', fontsize=11)
        ax3.set_ylabel('使用次数', fontsize=11)
        ax3.set_title('替代部件使用情况', fontsize=12, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(labels)
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        # 库存周转率
        ax4 = axes[1, 1]
        turnover_data = data.groupby(['is_anomaly_month'])['stock_turnover'].mean()
        
        labels = ['正常月份', '异常月份']
        colors = [self.colors['primary'], self.colors['danger']]
        
        bars = ax4.bar(labels, turnover_data.values, color=colors, alpha=0.8)
        
        for bar, val in zip(bars, turnover_data.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=11)
        
        ax4.set_ylabel('平均库存周转率', fontsize=11)
        ax4.set_title('库存周转率对比', fontsize=12, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_correlation_heatmap(self, data: pd.DataFrame, save_path: str = None):
        """绘制相关性热力图"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        numeric_cols = [
            'dead_stock_amount',
            'capital_tied',
            'stock_turnover',
            'substitute_awareness',
            'demand_factor',
            'current_stock',
            'part_unit_cost'
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
    
    def create_dashboard(self, 
                        data: pd.DataFrame,
                        comparison_df: pd.DataFrame,
                        causal_results: pd.DataFrame,
                        capital_results: pd.DataFrame,
                        save_path: str = None):
        """创建综合仪表板"""
        fig = plt.figure(figsize=(20, 14))
        
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        ax1 = fig.add_subplot(gs[0, :2])
        daily_dead = data.groupby(['year', 'month', 'date'])['dead_stock_amount'].mean().reset_index()
        colors = [self.colors['danger'] if m == 12 else self.colors['primary'] 
                  for m in daily_dead['month']]
        ax1.bar(range(len(daily_dead)), daily_dead['dead_stock_amount'], color=colors, alpha=0.7)
        ax1.axhline(y=daily_dead['dead_stock_amount'].mean(), 
                   color=self.colors['warning'], linestyle='--', linewidth=2)
        ax1.set_title('死库存趋势', fontsize=12, fontweight='bold')
        ax1.set_xlabel('天数')
        ax1.set_ylabel('死库存数量')
        ax1.grid(axis='y', alpha=0.3)
        
        ax2 = fig.add_subplot(gs[0, 2])
        monthly_dead = data.groupby(['year', 'month'])['dead_stock_amount'].mean()
        monthly_capital = data.groupby(['year', 'month'])['capital_tied'].mean()
        labels = [f"{y}-{m}" for y, m in monthly_dead.index]
        
        ax2.bar(labels, monthly_dead.values, color=self.colors['danger'], alpha=0.8, label='死库存')
        ax2.set_ylabel('死库存数量', fontsize=10)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3)
        
        ax2b = ax2.twinx()
        ax2b.plot(labels, monthly_capital.values, color=self.colors['primary'], marker='o', linewidth=2, label='资金占用')
        ax2b.set_ylabel('资金占用', fontsize=10)
        
        ax2.legend(loc='upper left')
        ax2b.legend(loc='upper right')
        ax2.set_title('月度死库存和资金占用', fontsize=12, fontweight='bold')
        
        ax3 = fig.add_subplot(gs[1, 0])
        metrics = comparison_df[~comparison_df['metric'].isin(['dead_stock_amount', 'capital_tied'])].head(5)
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
        ax4.set_title('死库存因果效应分析', fontsize=12, fontweight='bold')
        ax4.set_xlabel('效应值')
        ax4.grid(axis='x', alpha=0.3)
        
        ax5 = fig.add_subplot(gs[1, 2])
        valid_capital = capital_results[capital_results['causal_effect'].notna()].sort_values(
            'causal_effect', key=abs, ascending=True)
        colors = [self.colors['success'] if e > 0 else self.colors['danger'] 
                  for e in valid_capital['causal_effect']]
        ax5.barh(valid_capital['cause'], valid_capital['causal_effect'], color=colors, alpha=0.8)
        ax5.axvline(x=0, color='black', linewidth=0.5)
        ax5.set_title('资金占用影响分析', fontsize=12, fontweight='bold')
        ax5.set_xlabel('效应值')
        ax5.grid(axis='x', alpha=0.3)
        
        ax6 = fig.add_subplot(gs[2, :])
        ax6.axis('off')
        
        summary_text = "库存死货问题分析结论\n\n"
        summary_text += "="*50 + "\n\n"
        
        dead_stock_change = comparison_df[comparison_df['metric'] == 'dead_stock_amount']['change_percent'].values[0]
        capital_change = comparison_df[comparison_df['metric'] == 'capital_tied']['change_percent'].values[0]
        summary_text += f"• 死库存变化: {dead_stock_change:.2f}%\n"
        summary_text += f"• 资金占用变化: {capital_change:.2f}%\n\n"
        
        top_declines = comparison_df[
            ~comparison_df['metric'].isin(['dead_stock_amount', 'capital_tied'])
        ].head(3)
        
        summary_text += "• 主要影响因素:\n"
        for _, row in top_declines.iterrows():
            summary_text += f"  - {row['metric']}: {row['change_percent']:.2f}%\n"
        
        summary_text += "\n• 建议措施:\n"
        summary_text += "  1. 建立部件替代关系数据库，提高替代部件认知\n"
        summary_text += "  2. 实施智能库存管理系统，自动推荐替代部件\n"
        summary_text += "  3. 加强市场需求预测，优化采购计划\n"
        summary_text += "  4. 定期清理死库存，制定合理的库存周转目标\n"
        
        ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
                fontsize=11, verticalalignment='top',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
        
        fig.suptitle('制造企业库存死货问题根因分析仪表板', fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
