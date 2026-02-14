"""
制造企业根因分析系统 - Web界面

使用Streamlit构建交互式Web应用，包含：
1. 场景介绍和教学内容
2. 因果图可视化
3. 数据探索和分析
4. DoWhy因果分析结果
5. 结论和建议展示
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from PIL import Image
import io
import os

from data_generator import create_demo_scenario
from causal_analyzer import CausalAnalyzer, RootCauseAnalysisPipeline

# 设置页面配置
st.set_page_config(
    page_title="制造企业根因分析系统",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #A23B72;
    }
    .section-header {
        background-color: #2E86AB;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .info-box {
        background-color: #e8f4f8;
        border-left: 4px solid #2E86AB;
        padding: 15px;
        margin-bottom: 20px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #FFC107;
        padding: 15px;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28A745;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


class RootCauseAnalysisWebApp:
    """根因分析Web应用"""
    
    def __init__(self):
        self.data = None
        self.anomaly_factors = None
        self.analysis_results = None
        self.pipeline = None
        
    def load_data(self):
        """加载数据"""
        if self.data is None:
            with st.spinner("生成模拟数据..."):
                self.data, self.anomaly_factors = create_demo_scenario()
                self.pipeline = RootCauseAnalysisPipeline(self.data)
        return self.data, self.anomaly_factors
    
    def run_analysis(self):
        """运行分析"""
        if self.analysis_results is None:
            with st.spinner("运行根因分析..."):
                self.analysis_results = self.pipeline.run_full_analysis()
        return self.analysis_results
    
    def plot_causal_graph(self):
        """绘制因果图"""
        analyzer = CausalAnalyzer(self.data)
        causal_graph = analyzer.build_causal_graph()
        
        # 创建NetworkX图
        G = nx.DiGraph()
        
        # 解析因果图
        edges = [
            ("付款及时性", "供应商效率"),
            ("供应商效率", "零部件可用性"),
            ("零部件可用性", "生产效率"),
            ("员工技能水平", "生产效率"),
            ("设备状态", "生产效率"),
            ("产能利用率", "生产效率"),
            ("供应商效率", "生产效率"),
            ("付款及时性", "生产效率"),
            ("供应商基础效率", "供应商效率"),
            ("设备年龄", "设备状态"),
            ("工厂产能", "产能利用率"),
            ("工厂产能", "生产效率")
        ]
        
        for edge in edges:
            G.add_edge(edge[0], edge[1])
        
        # 生成布局
        pos = nx.spring_layout(G, k=0.8, iterations=100)
        
        # 创建Plotly图表
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            if node == "生产效率":
                node_color.append('#A23B72')
            elif node in ["付款及时性", "供应商效率", "零部件可用性"]:
                node_color.append('#2E86AB')
            else:
                node_color.append('#17A2B8')
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                colorscale='YlGnBu',
                reversescale=True,
                color=node_color,
                size=25,
                line_width=2
            ),
            text=node_text,
            textposition="top center"
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=dict(text='生产效率因果图', font=dict(size=16)),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        
        return fig
    
    def plot_efficiency_trend(self):
        """绘制效率趋势图"""
        daily_eff = self.data.groupby(['year', 'month', 'date'])['production_efficiency'].mean().reset_index()
        daily_eff['date_str'] = daily_eff['date'].dt.strftime('%Y-%m-%d')
        
        fig = px.bar(
            daily_eff, 
            x='date_str', 
            y='production_efficiency',
            color=daily_eff['month'].apply(lambda x: '异常月份' if x == 12 else '正常月份'),
            color_discrete_map={'正常月份': '#2E86AB', '异常月份': '#DC3545'},
            title='生产效率趋势分析',
            labels={'production_efficiency': '生产效率', 'date_str': '日期'}
        )
        
        avg_eff = daily_eff['production_efficiency'].mean()
        fig.add_hline(y=avg_eff, line_dash="dash", line_color="#FFC107", line_width=2,
                      annotation_text=f"平均效率: {avg_eff:.3f}",
                      annotation_position="top right")
        
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title="日期",
            yaxis_title="生产效率",
            legend_title="月份类型",
            template="plotly_white"
        )
        
        return fig
    
    def plot_metrics_comparison(self):
        """绘制指标对比图"""
        comparison_df = self.analysis_results['comparison']
        metrics = comparison_df[comparison_df['metric'] != 'production_efficiency']
        
        fig = px.bar(
            metrics,
            x='metric',
            y=['normal_mean', 'anomaly_mean'],
            barmode='group',
            title='正常月份 vs 异常月份指标对比',
            labels={'value': '指标值', 'variable': '月份类型'},
            color_discrete_map={'normal_mean': '#2E86AB', 'anomaly_mean': '#DC3545'}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title="指标",
            yaxis_title="指标值",
            legend_title="月份类型",
            template="plotly_white"
        )
        
        fig.update_traces(
            hovertemplate="%{y:.3f}"
        )
        
        return fig
    
    def plot_causal_effects(self):
        """绘制因果效应图"""
        causal_results = self.analysis_results['causal_analysis']
        valid_results = causal_results[causal_results['causal_effect'].notna()]
        
        fig = px.bar(
            valid_results,
            x='cause',
            y='causal_effect',
            color='causal_effect',
            color_continuous_scale=['#DC3545', '#FFC107', '#28A745'],
            title='各因素对生产效率的因果效应',
            labels={'causal_effect': '因果效应值', 'cause': '影响因素'}
        )
        
        fig.add_hline(y=0, line_dash="solid", line_color="#000000", line_width=1)
        
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title="影响因素",
            yaxis_title="因果效应值",
            template="plotly_white"
        )
        
        fig.update_traces(
            hovertemplate="效应值: %{y:.3f}<br>解释: %{customdata}",
            customdata=valid_results['interpretation']
        )
        
        return fig
    
    def plot_correlation_heatmap(self):
        """绘制相关性热力图"""
        numeric_cols = [
            'production_efficiency',
            'payment_timeliness',
            'supplier_efficiency',
            'parts_availability',
            'avg_employee_skill',
            'equipment_status',
            'capacity_utilization'
        ]
        
        corr_matrix = self.data[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="变量相关性热力图",
            color_continuous_scale="RdBu_r",
            labels={'color': '相关系数'}
        )
        
        fig.update_layout(
            template="plotly_white",
            xaxis_nticks=len(numeric_cols),
            yaxis_nticks=len(numeric_cols)
        )
        
        return fig
    
    def render_sidebar(self):
        """渲染侧边栏"""
        st.sidebar.title("🔍 根因分析系统")
        st.sidebar.markdown("### 分析导航")
        
        page = st.sidebar.radio(
            "选择页面",
            ["场景介绍", "因果图", "数据分析", "因果分析", "结论建议"]
        )
        
        st.sidebar.markdown("### 关于系统")
        st.sidebar.info(
            "这是一个基于DoWhy框架的根因分析系统\n\n"+
            "**用途**：分析制造企业生产效率下降的根本原因\n\n"+
            "**技术栈**：\n"+
            "- Python + Streamlit\n"+
            "- DoWhy 因果推断\n"+
            "- Plotly 数据可视化"
        )
        
        return page
    
    def render_scenario_page(self):
        """渲染场景介绍页面"""
        st.header("场景介绍")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="section-header">
                制造企业生产效率根因分析场景
            </div>
            
            <div class="info-box">
            <h4>场景背景</h4>
            <p>某制造企业在2024年12月发现生产效率相比11月显著下降，需要分析原因并提出改进措施。</p>
            </div>
            
            <div class="info-box">
            <h4>实体构成</h4>
            <ul>
                <li><strong>工厂</strong>：3个工厂（华东、华南、华北）</li>
                <li><strong>供应商</strong>：5个供应商（核心零部件、电子元件、结构件等）</li>
                <li><strong>员工</strong>：约1500名员工（不同熟练度）</li>
                <li><strong>生产流程</strong>：原材料采购 → 生产加工 → 质量检验 → 成品入库</li>
            </ul>
            </div>
            
            <div class="info-box">
            <h4>因果关系</h4>
            <ul>
                <li>付款及时性 → 供应商效率 → 零部件可用性 → 生产效率</li>
                <li>员工技能水平 → 生产效率</li>
                <li>设备状态 → 生产效率</li>
                <li>产能利用率 → 生产效率</li>
            </ul>
            </div>
            
            <div class="warning-box">
            <h4>异常因素</h4>
            <ul>
                <li>付款延迟：付款及时性下降55%</li>
                <li>供应商问题：供应商效率下降28%</li>
            </ul>
            </div>
            
            <div class="success-box">
            <h4>分析目标</h4>
            <p>使用DoWhy因果推断框架，分析生产效率下降的根本原因，并提出针对性的改进建议。</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("数据概览")
            
            data, factors = self.load_data()
            
            st.markdown(f"**数据记录数**: {len(data)}")
            st.markdown(f"**时间范围**: {data['date'].min().strftime('%Y-%m-%d')} 至 {data['date'].max().strftime('%Y-%m-%d')}")
            st.markdown(f"**工厂数量**: {data['factory_id'].nunique()}")
            st.markdown(f"**供应商数量**: {data['supplier_id'].nunique()}")
            
            st.subheader("异常因素配置")
            for factor, enabled in factors.items():
                status = "✅ 启用" if enabled else "❌ 未启用"
                st.markdown(f"**{factor}**: {status}")
            
            if st.button("开始分析", key="start_analysis"):
                self.run_analysis()
                st.success("分析完成！请在其他页面查看结果")
    
    def render_causal_graph_page(self):
        """渲染因果图页面"""
        st.header("因果图分析")
        
        self.load_data()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = self.plot_causal_graph()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="section-header">
                因果图说明
            </div>
            
            <div class="info-box">
            <h4>核心因果链</h4>
            <p><strong>付款及时性 → 供应商效率 → 零部件可用性 → 生产效率</strong></p>
            <p>这是影响生产效率的主要因果路径，付款延迟会直接影响供应商的生产积极性。</p>
            </div>
            
            <div class="info-box">
            <h4>直接影响因素</h4>
            <ul>
                <li><strong>员工技能水平</strong>：员工熟练度直接影响生产效率</li>
                <li><strong>设备状态</strong>：设备运行状况影响生产能力</li>
                <li><strong>产能利用率</strong>：合理的产能分配影响整体效率</li>
            </ul>
            </div>
            
            <div class="info-box">
            <h4>前置因素</h4>
            <ul>
                <li><strong>供应商基础效率</strong>：供应商本身的生产能力</li>
                <li><strong>设备年龄</strong>：设备使用年限影响设备状态</li>
                <li><strong>工厂产能</strong>：工厂规模影响产能利用率</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def render_data_analysis_page(self):
        """渲染数据分析页面"""
        st.header("数据分析")
        
        self.load_data()
        self.run_analysis()
        
        tab1, tab2, tab3 = st.tabs(["效率趋势", "指标对比", "相关性分析"])
        
        with tab1:
            fig = self.plot_efficiency_trend()
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = self.plot_metrics_comparison()
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            fig = self.plot_correlation_heatmap()
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="info-box">
            <h4>相关性分析说明</h4>
            <p>相关性热力图显示了各变量之间的相关程度：</p>
            <ul>
                <li><strong>红色</strong>：负相关（值越小，生产效率越低）</li>
                <li><strong>蓝色</strong>：正相关（值越大，生产效率越高）</li>
                <li><strong>颜色深浅</strong>：相关性强度</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def render_causal_analysis_page(self):
        """渲染因果分析页面"""
        st.header("因果分析")
        
        self.load_data()
        self.run_analysis()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = self.plot_causal_effects()
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("因果效应详细分析")
            causal_results = self.analysis_results['causal_analysis']
            valid_results = causal_results[causal_results['causal_effect'].notna()]
            valid_results = valid_results.sort_values('causal_effect', key=abs, ascending=False)
            
            for _, row in valid_results.iterrows():
                with st.expander(f"{row['cause']} (效应值: {row['causal_effect']:.3f})"):
                    st.write(f"**解释**: {row['interpretation']}")
                    if row['causal_effect'] > 0.3:
                        st.success("强影响因素")
                    elif row['causal_effect'] > 0.1:
                        st.info("中等影响因素")
                    else:
                        st.warning("弱影响因素")
        
        with col2:
            st.markdown("""
            <div class="section-header">
                DoWhy因果推断
            </div>
            
            <div class="info-box">
            <h4>分析方法</h4>
            <p>使用DoWhy框架的线性回归方法估计因果效应，分析各因素对生产效率的影响程度。</p>
            </div>
            
            <div class="info-box">
            <h4>效应解读</h4>
            <ul>
                <li><strong>正值</strong>：因素增加会提高生产效率</li>
                <li><strong>负值</strong>：因素增加会降低生产效率</li>
                <li><strong>绝对值</strong>：影响程度大小</li>
            </ul>
            </div>
            
            <div class="success-box">
            <h4>关键发现</h4>
            <p><strong>员工技能水平</strong>和<strong>零部件可用性</strong>是影响生产效率的最关键因素。</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_conclusion_page(self):
        """渲染结论页面"""
        st.header("结论与建议")
        
        self.load_data()
        self.run_analysis()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(self.analysis_results['summary'])
            
            st.subheader("详细指标变化")
            comparison_df = self.analysis_results['comparison']
            st.dataframe(comparison_df.style.format({
                'normal_mean': '{:.3f}',
                'anomaly_mean': '{:.3f}',
                'change_percent': '{:.2f}%',
                'abs_change': '{:.2f}%'
            }))
        
        with col2:
            st.markdown("""
            <div class="section-header">
                改进建议
            </div>
            
            <div class="info-box">
            <h4>短期措施</h4>
            <ol>
                <li><strong>优化付款流程</strong>：
                    <ul>
                        <li>建立供应商付款预警机制</li>
                        <li>简化审批流程，缩短付款周期</li>
                        <li>对核心供应商实施预付款政策</li>
                    </ul>
                </li>
                <li><strong>加强供应商管理</strong>：
                    <ul>
                        <li>建立供应商绩效评估体系</li>
                        <li>发展备选供应商，降低依赖风险</li>
                        <li>定期与供应商沟通，了解生产状况</li>
                    </ul>
                </li>
            </ol>
            </div>
            
            <div class="info-box">
            <h4>长期措施</h4>
            <ol>
                <li><strong>员工技能提升</strong>：
                    <ul>
                        <li>建立系统化的培训体系</li>
                        <li>实施技能等级认证制度</li>
                        <li>激励高技能员工，减少流失</li>
                    </ul>
                </li>
                <li><strong>设备管理优化</strong>：
                    <ul>
                        <li>建立设备维护保养计划</li>
                        <li>考虑设备更新换代</li>
                        <li>实施预测性维护</li>
                    </ul>
                </li>
                <li><strong>建立监控系统</strong>：
                    <ul>
                        <li>实时监控生产效率指标</li>
                        <li>建立异常预警机制</li>
                        <li>定期进行根因分析</li>
                    </ul>
                </li>
            </ol>
            </div>
            """, unsafe_allow_html=True)
    
    def run(self):
        """运行应用"""
        page = self.render_sidebar()
        
        if page == "场景介绍":
            self.render_scenario_page()
        elif page == "因果图":
            self.render_causal_graph_page()
        elif page == "数据分析":
            self.render_data_analysis_page()
        elif page == "因果分析":
            self.render_causal_analysis_page()
        elif page == "结论建议":
            self.render_conclusion_page()


if __name__ == "__main__":
    app = RootCauseAnalysisWebApp()
    app.run()
