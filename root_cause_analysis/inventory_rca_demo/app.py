"""
部件A库存高因果根因分析 - Web应用

使用Streamlit构建交互式Web应用，展示：
1. 场景介绍
2. 因果图可视化
3. 数据探索
4. 因果分析结果
5. 大模型智能解释
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import os

from data_generator import InventoryDataGenerator, create_inventory_scenario
from causal_analyzer import InventoryCausalAnalyzer
from llm_explainer import LLMExplainer

st.set_page_config(
    page_title="部件A库存高因果根因分析",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .llm-box {
        background-color: #f0f8ff;
        border-left: 4px solid #4169E1;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


class InventoryAnalysisWebApp:
    """库存分析Web应用"""
    
    def __init__(self):
        if 'actual_data' not in st.session_state:
            st.session_state.actual_data = None
        if 'counterfactual_data' not in st.session_state:
            st.session_state.counterfactual_data = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'llm_explainer' not in st.session_state:
            st.session_state.llm_explainer = None
        if 'llm_explanation' not in st.session_state:
            st.session_state.llm_explanation = None
        
        self.actual_data = st.session_state.actual_data
        self.counterfactual_data = st.session_state.counterfactual_data
        self.analysis_results = st.session_state.analysis_results
        self.llm_explainer = st.session_state.llm_explainer
        self.llm_explanation = st.session_state.llm_explanation
    
    def load_data(self):
        """加载数据"""
        if self.actual_data is None:
            with st.spinner("生成数据..."):
                self.actual_data, self.counterfactual_data = create_inventory_scenario()
                st.session_state.actual_data = self.actual_data
                st.session_state.counterfactual_data = self.counterfactual_data
                st.success(f"✅ 已生成 {len(self.actual_data)} 条数据记录")
        
        return self.actual_data, self.counterfactual_data
    
    def run_analysis(self):
        """运行因果分析"""
        if self.analysis_results is None:
            with st.spinner("运行因果分析..."):
                analyzer = InventoryCausalAnalyzer(data=self.actual_data)
                self.analysis_results = analyzer.run_full_analysis(self.counterfactual_data)
                st.session_state.analysis_results = self.analysis_results
                st.success("✅ 因果分析完成！")
        
        return self.analysis_results
    
    def init_llm_explainer(self, api_key: str, model: str = None, base_url: str = None):
        """初始化大模型解释器"""
        self.llm_explainer = LLMExplainer(api_key=api_key, model=model, base_url=base_url)
        self.llm_explanation = None
        st.session_state.llm_explainer = self.llm_explainer
        st.session_state.llm_explanation = None
    
    def generate_llm_explanation(self):
        """生成大模型解释"""
        if self.llm_explanation is None and self.llm_explainer is not None:
            if self.analysis_results is None:
                st.warning("请先运行因果分析")
                return None
            
            with st.spinner("大模型正在生成解释..."):
                self.llm_explanation = self.llm_explainer.generate_explanation(
                    self.analysis_results,
                    self.actual_data,
                    self.counterfactual_data
                )
                st.session_state.llm_explanation = self.llm_explanation
        
        return self.llm_explanation
    
    def plot_causal_graph(self):
        """绘制因果图（有向无环图）"""
        G = nx.DiGraph()
        
        edges = [
            ("产品A销量", "部件A消耗量"),
            ("产品B销量", "部件A消耗量"),
            ("产品B使用部件A", "部件A消耗量"),
            ("部件A消耗量", "部件A库存"),
            ("部件A采购量", "部件A库存"),
            ("产品A销量", "部件A采购量"),
        ]
        
        for edge in edges:
            G.add_edge(edge[0], edge[1])
        
        pos = nx.spring_layout(G, k=0.8, iterations=100)
        
        # 创建箭头注释来表示有向边
        arrows = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            # 计算箭头的偏移，使其从节点边缘开始
            dx = x1 - x0
            dy = y1 - y0
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
                # 节点半径约为0.05（根据节点大小调整）
                node_radius = 0.05
                offset_x = dx / length * node_radius
                offset_y = dy / length * node_radius
                
                arrows.append(
                    dict(
                        ax=x0 + offset_x,
                        ay=y0 + offset_y,
                        x=x1 - offset_x,
                        y=y1 - offset_y,
                        xref='x',
                        yref='y',
                        axref='x',
                        ayref='y',
                        arrowhead=2,
                        arrowwidth=2,
                        arrowcolor='#666',
                        showarrow=True,
                        arrowside='end'
                    )
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
            if node == "部件A库存":
                node_color.append('#A23B72')
            elif node in ["产品B使用部件A", "产品A销量"]:
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
                size=30,
                line_width=2
            ),
            text=node_text,
            textposition="top center",
            textfont=dict(size=12)
        )
        
        fig = go.Figure(data=[node_trace],
                       layout=go.Layout(
                           title=dict(text='部件A库存因果图（有向无环图）', font=dict(size=16)),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=arrows,
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        
        return fig
    
    def plot_inventory_trend(self):
        """绘制库存趋势图"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.actual_data['date'],
            y=self.actual_data['component_a_inventory'],
            mode='lines',
            name='实际库存',
            line=dict(color='#DC3545', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=self.counterfactual_data['date'],
            y=self.counterfactual_data['component_a_inventory'],
            mode='lines',
            name='反事实库存（产品B使用部件A）',
            line=dict(color='#28A745', width=2, dash='dash')
        ))
        
        decline_start = self.actual_data[self.actual_data['is_decline_period'] == True]['date'].min()
        
        fig.update_layout(
            title='部件A库存趋势对比',
            xaxis_title='日期',
            yaxis_title='库存水平',
            template='plotly_white',
            hovermode='x unified',
            shapes=[
                dict(
                    type='line',
                    xref='x',
                    yref='paper',
                    x0=decline_start,
                    y0=0,
                    x1=decline_start,
                    y1=1,
                    line=dict(color='orange', width=2, dash='dash')
                )
            ],
            annotations=[
                dict(
                    x=decline_start,
                    y=1,
                    yref='paper',
                    text='产品A销量下降开始',
                    showarrow=False,
                    font=dict(color='orange', size=12),
                    yanchor='bottom'
                )
            ]
        )
        
        return fig
    
    def plot_sales_trend(self):
        """绘制销量趋势图"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.actual_data['date'],
            y=self.actual_data['product_a_sales'],
            mode='lines',
            name='产品A销量',
            line=dict(color='#2E86AB', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=self.actual_data['date'],
            y=self.actual_data['product_b_sales'],
            mode='lines',
            name='产品B销量',
            line=dict(color='#A23B72', width=2)
        ))
        
        decline_start = self.actual_data[self.actual_data['is_decline_period'] == True]['date'].min()
        
        fig.update_layout(
            title='产品销量趋势',
            xaxis_title='日期',
            yaxis_title='销量',
            template='plotly_white',
            hovermode='x unified',
            shapes=[
                dict(
                    type='line',
                    xref='x',
                    yref='paper',
                    x0=decline_start,
                    y0=0,
                    x1=decline_start,
                    y1=1,
                    line=dict(color='orange', width=2, dash='dash')
                )
            ],
            annotations=[
                dict(
                    x=decline_start,
                    y=1,
                    yref='paper',
                    text='产品A销量下降开始',
                    showarrow=False,
                    font=dict(color='orange', size=12),
                    yanchor='bottom'
                )
            ]
        )
        
        return fig
    
    def plot_metrics_comparison(self):
        """绘制指标对比图"""
        if self.analysis_results is None:
            return None
        
        cf_results = self.analysis_results.get('counterfactual_analysis', {})
        
        metrics = ['实际库存均值', '反事实库存均值', '销量下降期实际库存', '销量下降期反事实库存']
        values = [
            cf_results.get('actual_inventory_mean', 0),
            cf_results.get('counterfactual_inventory_mean', 0),
            cf_results.get('decline_period_actual_inventory', 0),
            cf_results.get('decline_period_counterfactual_inventory', 0)
        ]
        
        fig = go.Figure(data=[
            go.Bar(name='库存水平', x=metrics, y=values, marker_color=['#DC3545', '#28A745', '#DC3545', '#28A745'])
        ])
        
        fig.update_layout(
            title='库存对比分析',
            xaxis_title='指标',
            yaxis_title='库存水平',
            template='plotly_white'
        )
        
        return fig
    
    def render_sidebar(self):
        """渲染侧边栏"""
        st.sidebar.title("🔍 库存根因分析")
        st.sidebar.markdown("### 分析导航")
        
        page = st.sidebar.radio(
            "选择页面",
            ["场景介绍", "因果图", "数据探索", "因果分析", "大模型解释"]
        )
        
        st.sidebar.markdown("### 大模型配置")
        with st.sidebar.expander("配置大模型API"):
            st.info("配置API密钥以启用大模型解释功能")
            
            modelkey_path = os.path.join(os.path.dirname(__file__), "modelkey.cfg")
            default_api_key = None
            default_base_url = None
            default_model = None
            
            if os.path.exists(modelkey_path):
                with open(modelkey_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('API Key:'):
                            default_api_key = line.split(':', 1)[1].strip()
                        elif line.startswith('Base URL:'):
                            default_base_url = line.split(':', 1)[1].strip()
                        elif line.startswith('Model:'):
                            default_model = line.split(':', 1)[1].strip()
            
            api_key = st.text_input(
                "API密钥",
                value=default_api_key,
                type="password",
                help="输入您的API密钥"
            )
            
            base_url = st.text_input(
                "API Base URL",
                value=default_base_url,
                placeholder="默认: https://api.siliconflow.cn/v1"
            )
            
            model = st.text_input(
                "模型名称",
                value=default_model,
                placeholder="默认: Qwen/Qwen2.5-7B-Instruct"
            )
            
            if st.button("初始化大模型解释器"):
                if api_key:
                    self.init_llm_explainer(api_key, model, base_url)
                    st.success("✅ 大模型解释器初始化成功！")
                else:
                    st.warning("请输入API密钥")
        
        st.sidebar.markdown("### 关于系统")
        st.sidebar.info(
            "这是一个基于DoWhy框架的库存根因分析系统\n\n"+
            "**用途**：分析部件A库存高的根本原因\n\n"+
            "**技术栈**：\n"+
            "- Python + Streamlit\n"+
            "- DoWhy 因果推断\n"+
            "- Plotly 数据可视化\n"+
            "- 大模型智能解释"
        )
        
        return page
    
    def render_scenario_page(self):
        """渲染场景介绍页面"""
        st.header("场景介绍")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="section-header">
                部件A库存高因果根因分析场景
            </div>
            
            <div class="info-box">
            <h4>场景背景</h4>
            <p>产品A销量下降，导致部件A库存偏高。需要验证：<strong>产品B未使用部件A</strong> 是部件A库存高的<strong>核心因果根因</strong>，而非仅由产品A销量下降导致。</p>
            </div>
            
            <div class="info-box">
            <h4>核心目标</h4>
            <ul>
                <li>用因果分析量化：若产品B使用部件A，库存可下降多少</li>
                <li>通过反事实与稳健检验证明因果结论可靠</li>
                <li>输出Web可视化页面 + 大模型业务解释</li>
            </ul>
            </div>
            
            <div class="info-box">
            <h4>因果关系</h4>
            <ul>
                <li>产品A销量 → 部件A消耗量 → 部件A库存</li>
                <li>产品B销量 → 部件A消耗量（如果产品B使用部件A）</li>
                <li>产品B使用部件A → 部件A消耗量</li>
            </ul>
            </div>
            
            <div class="warning-box">
            <h4>问题描述</h4>
            <ul>
                <li>产品A销量在11月开始下降40%</li>
                <li>产品B未使用部件A（历史全为0）</li>
                <li>部件A库存持续升高，占用资金</li>
            </ul>
            </div>
            
            <div class="success-box">
            <h4>分析目标</h4>
            <p>使用DoWhy因果推断框架，量化产品B未使用部件A对库存的影响，验证其是否为核心根因。</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("数据概览")
            
            actual_data, counterfactual_data = self.load_data()
            
            st.markdown(f"**数据记录数**: {len(actual_data)}")
            st.markdown(f"**时间范围**: {actual_data['date'].min().strftime('%Y-%m-%d')} 至 {actual_data['date'].max().strftime('%Y-%m-%d')}")
            
            st.markdown("**关键指标**:")
            st.markdown(f"- 产品A平均销量: {actual_data['product_a_sales'].mean():.0f}")
            st.markdown(f"- 产品B平均销量: {actual_data['product_b_sales'].mean():.0f}")
            st.markdown(f"- 部件A平均库存: {actual_data['component_a_inventory'].mean():.0f}")
            
            if st.button("开始分析", key="start_analysis"):
                self.run_analysis()
                st.success("分析完成！请在其他页面查看结果")
    
    def render_causal_graph_page(self):
        """渲染因果图页面"""
        st.header("因果图分析")
        
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
            <p><strong>产品B使用部件A → 部件A消耗量 → 部件A库存</strong></p>
            <p>这是影响库存水平的主要因果路径，产品B是否使用部件A直接影响部件A的消耗速度。</p>
            </div>
            
            <div class="info-box">
            <h4>直接影响因素</h4>
            <ul>
                <li><strong>产品A销量</strong>：直接影响部件A消耗量</li>
                <li><strong>产品B销量</strong>：如果产品B使用部件A，则影响消耗量</li>
                <li><strong>部件A采购量</strong>：直接影响库存水平</li>
            </ul>
            </div>
            
            <div class="info-box">
            <h4>干预变量</h4>
            <p><strong>产品B使用部件A</strong>：这是我们可以干预的变量，通过改变产品B的BOM配置，可以让产品B也使用部件A。</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_data_exploration_page(self):
        """渲染数据探索页面"""
        st.header("数据探索")
        
        self.load_data()
        
        tab1, tab2, tab3 = st.tabs(["库存趋势", "销量趋势", "数据概览"])
        
        with tab1:
            fig = self.plot_inventory_trend()
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="info-box">
            <h4>库存趋势分析</h4>
            <p>图中显示了实际库存与反事实库存的对比：</p>
            <ul>
                <li><strong>红色实线</strong>：实际库存（产品B未使用部件A）</li>
                <li><strong>绿色虚线</strong>：反事实库存（产品B使用部件A）</li>
                <li><strong>橙色虚线</strong>：产品A销量下降开始时间</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with tab2:
            fig = self.plot_sales_trend()
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="info-box">
            <h4>销量趋势分析</h4>
            <p>图中显示了产品A和产品B的销量趋势：</p>
            <ul>
                <li><strong>蓝色线</strong>：产品A销量（11月开始下降）</li>
                <li><strong>紫色线</strong>：产品B销量（保持稳定）</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with tab3:
            st.subheader("数据统计")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**正常期统计**")
                normal_data = self.actual_data[self.actual_data['is_decline_period'] == False]
                st.dataframe(normal_data.describe())
            
            with col2:
                st.markdown("**销量下降期统计**")
                decline_data = self.actual_data[self.actual_data['is_decline_period'] == True]
                st.dataframe(decline_data.describe())
    
    def render_causal_analysis_page(self):
        """渲染因果分析页面"""
        st.header("因果分析")
        
        self.load_data()
        
        if st.button("运行因果分析", type="primary"):
            self.run_analysis()
        
        if self.analysis_results:
            st.markdown("### 分析结果")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cf_results = self.analysis_results.get('counterfactual_analysis', {})
                st.metric(
                    "库存降低",
                    f"{cf_results.get('inventory_reduction', 0):.0f}",
                    f"{cf_results.get('reduction_percentage', 0):.1f}%"
                )
            
            with col2:
                st.metric(
                    "因果效应值",
                    f"{self.analysis_results.get('causal_effect', 0):.4f}"
                )
            
            with col3:
                cf_results = self.analysis_results.get('counterfactual_analysis', {})
                is_root_cause = cf_results.get('is_root_cause', False)
                st.metric(
                    "是否为根因",
                    "是" if is_root_cause else "否",
                    delta="核心根因" if is_root_cause else "非核心根因"
                )
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 库存对比图")
                fig = self.plot_metrics_comparison()
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 驳斥检验结果")
                refutation_results = self.analysis_results.get('refutation_results', {})
                for test_name, result in refutation_results.items():
                    if isinstance(result, dict) and 'error' not in result:
                        st.markdown(f"**{test_name}**:")
                        st.markdown(f"- 新效应值: {result.get('new_effect', 0):.4f}")
                        if 'is_statistically_significant' in result:
                            st.markdown(f"- 统计显著性: {'✅ 通过' if result['is_statistically_significant'] else '❌ 未通过'}")
                        if 'is_robust' in result:
                            st.markdown(f"- 稳健性: {'✅ 稳健' if result['is_robust'] else '❌ 不稳健'}")
            
            st.markdown("---")
            
            st.markdown("#### 多变量因果效应分析")
            effects_df = pd.DataFrame(self.analysis_results.get('causal_effects', []))
            if not effects_df.empty:
                st.dataframe(effects_df)
            
            st.markdown("---")
            
            st.markdown("#### 反事实分析详情")
            cf_results = self.analysis_results.get('counterfactual_analysis', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**整体库存对比**")
                st.markdown(f"- 实际库存均值: {cf_results.get('actual_inventory_mean', 0):.2f}")
                st.markdown(f"- 反事实库存均值: {cf_results.get('counterfactual_inventory_mean', 0):.2f}")
                st.markdown(f"- 库存降低: {cf_results.get('inventory_reduction', 0):.2f} ({cf_results.get('reduction_percentage', 0):.2f}%)")
            
            with col2:
                st.markdown("**销量下降期库存对比**")
                st.markdown(f"- 实际库存: {cf_results.get('decline_period_actual_inventory', 0):.2f}")
                st.markdown(f"- 反事实库存: {cf_results.get('decline_period_counterfactual_inventory', 0):.2f}")
                st.markdown(f"- 库存降低: {cf_results.get('decline_period_reduction', 0):.2f}")
    
    def render_llm_explanation_page(self):
        """渲染大模型解释页面"""
        st.header("AI智能解释")
        
        st.markdown("""
        <div class="llm-box">
        <h4>🤖 大模型智能解释</h4>
        <p>基于DoWhy因果分析结果，大模型将生成详细的根因分析报告，包括：</p>
        <ul>
            <li>根本原因分析</li>
            <li>影响机制解释</li>
            <li>量化影响评估</li>
            <li>改进建议</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if self.llm_explainer is None:
            st.warning("请先在侧边栏配置大模型API密钥并初始化解释器")
            return
        
        if self.analysis_results is None:
            st.warning("请先运行因果分析")
            return
        
        if st.button("生成大模型解释", type="primary"):
            explanation = self.generate_llm_explanation()
            if explanation:
                st.markdown("#### 📊 AI生成的根因分析报告")
                st.markdown(explanation)
                
                st.download_button(
                    label="下载报告",
                    data=explanation,
                    file_name="库存根因分析报告.md",
                    mime="text/markdown"
                )


if __name__ == "__main__":
    app = InventoryAnalysisWebApp()
    page = app.render_sidebar()
    
    if page == "场景介绍":
        app.render_scenario_page()
    elif page == "因果图":
        app.render_causal_graph_page()
    elif page == "数据探索":
        app.render_data_exploration_page()
    elif page == "因果分析":
        app.render_causal_analysis_page()
    elif page == "大模型解释":
        app.render_llm_explanation_page()
