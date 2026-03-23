"""
电商利润根因分析 - Web演示界面

基于Streamlit构建的交互式Web应用，演示DoWhy GCM根因分析功能。

场景：在线商店智能手机销售利润分析
问题：2022年初利润突然下降，需要找出根本原因
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rca_analyzer import RootCauseAnalyzer
from rca_data_generator import EcommerceDataGenerator, create_demo_scenario
from rca_llm_explainer import LLMExplainer

st.set_page_config(
    page_title="电商利润根因分析系统",
    page_icon="📊",
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
</style>
""", unsafe_allow_html=True)


class RCADemoApp:
    """根因分析演示应用"""
    
    def __init__(self):
        if 'data' not in st.session_state:
            st.session_state.data = None
        if 'analyzer' not in st.session_state:
            st.session_state.analyzer = None
        if 'causal_graph' not in st.session_state:
            st.session_state.causal_graph = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'llm_explainer' not in st.session_state:
            st.session_state.llm_explainer = None
        if 'llm_explanation' not in st.session_state:
            st.session_state.llm_explanation = None
        
        self.data = st.session_state.data
        self.analyzer = st.session_state.analyzer
        self.causal_graph = st.session_state.causal_graph
        self.analysis_results = st.session_state.analysis_results
        self.llm_explainer = st.session_state.llm_explainer
        self.llm_explanation = st.session_state.llm_explanation
        
    def save_state(self):
        """保存状态到session_state"""
        st.session_state.data = self.data
        st.session_state.analyzer = self.analyzer
        st.session_state.causal_graph = self.causal_graph
        st.session_state.analysis_results = self.analysis_results
        st.session_state.llm_explainer = self.llm_explainer
        st.session_state.llm_explanation = self.llm_explanation
    
    def load_or_generate_data(self):
        """加载或生成数据"""
        if self.data is None:
            with st.spinner("生成演示数据..."):
                self.data, anomaly_factors, self.causal_graph = create_demo_scenario()
                st.session_state.anomaly_factors = anomaly_factors
                self.save_state()
                st.success(f"✅ 已生成 {len(self.data)} 条数据记录")
        
        return self.data
    
    def render_sidebar(self):
        """渲染侧边栏"""
        st.sidebar.title("📊 根因分析系统")
        st.sidebar.markdown("### 分析导航")
        
        page = st.sidebar.radio(
            "选择页面",
            ["场景介绍", "数据探索", "因果图", "根因分析", "反事实分析", "AI解释"]
        )
        
        st.sidebar.markdown("### 大模型配置")
        with st.sidebar.expander("配置LLM API"):
            st.info("配置大模型API以启用AI解释功能")
            
            api_key = st.text_input(
                "API密钥",
                type="password",
                help="输入您的SiliconFlow API密钥"
            )
            
            base_url = st.text_input(
                "API Base URL",
                value="https://api.siliconflow.cn/v1",
                help="API端点URL"
            )
            
            model = st.text_input(
                "模型名称",
                value="Qwen/Qwen2.5-7B-Instruct",
                help="模型名称"
            )
            
            if st.button("初始化LLM解释器"):
                if api_key:
                    with st.spinner("正在初始化..."):
                        try:
                            from rca_llm_explainer import LLMExplainer
                            self.llm_explainer = LLMExplainer(
                                api_key=api_key,
                                model=model,
                                base_url=base_url
                            )
                            
                            success, message = self.llm_explainer.test_connection()
                            
                            if success:
                                st.success(f"✅ {message}")
                                self.save_state()
                            else:
                                st.error(f"❌ {message}")
                                self.llm_explainer = None
                        except Exception as e:
                            st.error(f"❌ 初始化失败: {str(e)}")
                            self.llm_explainer = None
                else:
                    st.warning("⚠️ 请输入API密钥")
        
        st.sidebar.markdown("### 关于系统")
        st.sidebar.info(
            "这是一个基于DoWhy GCM框架的根因分析系统\n\n"
            "**场景**：电商利润分析\n\n"
            "**问题**：2022年初利润突然下降\n\n"
            "**技术栈**：\n"
            "- DoWhy GCM\n"
            "- Streamlit\n"
            "- Plotly\n"
            "- LLM (可选)"
        )
        
        return page
    
    def render_scenario_page(self):
        """渲染场景介绍页面"""
        st.header("📋 场景介绍")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="section-header">
                在线商店智能手机销售利润分析场景
            </div>
            
            <div class="info-box">
            <h4>场景背景</h4>
            <p>某在线商店销售智能手机，零售价为$999。2021年利润保持稳定，但在2022年初突然出现显著下降。需要分析利润下降的根本原因。</p>
            </div>
            
            <div class="info-box">
            <h4>因果因素</h4>
            <ul>
                <li><strong>Shopping Event</strong>：购物活动标识（黑色星期五、网络星期一等）</li>
                <li><strong>Ad Spend</strong>：广告支出</li>
                <li><strong>Page Views</strong>：页面浏览量</li>
                <li><strong>Unit Price</strong>：单价（可能有折扣）</li>
                <li><strong>Sold Units</strong>：销售数量</li>
                <li><strong>Revenue</strong>：收入</li>
                <li><strong>Operational Cost</strong>：运营成本</li>
                <li><strong>Profit</strong>：利润</li>
            </ul>
            </div>
            
            <div class="warning-box">
            <h4>异常因素</h4>
            <ul>
                <li>广告支出减少50%</li>
                <li>单价上涨10%</li>
            </ul>
            </div>
            
            <div class="success-box">
            <h4>分析目标</h4>
            <p>使用DoWhy GCM框架，识别利润下降的根本原因，并提出改进建议。</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("数据概览")
            
            data = self.load_or_generate_data()
            
            st.markdown(f"**数据记录数**: {len(data)}")
            st.markdown(f"**时间范围**: {data['date'].min().strftime('%Y-%m-%d')} 至 {data['date'].max().strftime('%Y-%m-%d')}")
            st.markdown(f"**正常时期**: {len(data[~data['is_anomaly_period']])} 天")
            st.markdown(f"**异常时期**: {len(data[data['is_anomaly_period']])} 天")
            
            normal_data = data[~data['is_anomaly_period']]
            anomaly_data = data[data['is_anomaly_period']]
            
            st.markdown("### 利润对比")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("正常时期平均利润", f"${normal_data['profit'].mean():,.2f}")
            with col_b:
                st.metric("异常时期平均利润", f"${anomaly_data['profit'].mean():,.2f}")
            
            profit_change = (anomaly_data['profit'].mean() - normal_data['profit'].mean()) / normal_data['profit'].mean() * 100
            st.metric("利润变化", f"{profit_change:.2f}%", delta_color="inverse")
    
    def render_data_exploration_page(self):
        """渲染数据探索页面"""
        st.header("📊 数据探索")
        
        data = self.load_or_generate_data()
        
        tab1, tab2, tab3 = st.tabs(["趋势分析", "指标对比", "统计摘要"])
        
        with tab1:
            st.subheader("利润趋势分析")
            
            daily_profit = data.groupby('date').agg({
                'profit': 'mean',
                'is_anomaly_period': 'first'
            }).reset_index()
            
            fig = px.line(
                daily_profit, 
                x='date', 
                y='profit',
                title='每日利润趋势',
                labels={'profit': '利润 ($)', 'date': '日期'}
            )
            
            fig.add_vrect(
                x0=data[data['is_anomaly_period']]['date'].min(),
                x1=data[data['is_anomaly_period']]['date'].max(),
                fillcolor="red",
                opacity=0.1,
                annotation_text="异常时期",
                annotation_position="top left"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("正常时期 vs 异常时期指标对比")
            
            normal_data = data[~data['is_anomaly_period']]
            anomaly_data = data[data['is_anomaly_period']]
            
            metrics = ['profit', 'revenue', 'sold_units', 'page_views', 'ad_spend', 'unit_price', 'operational_cost']
            
            comparison_data = []
            for metric in metrics:
                normal_mean = normal_data[metric].mean()
                anomaly_mean = anomaly_data[metric].mean()
                change = (anomaly_mean - normal_mean) / normal_mean * 100 if normal_mean != 0 else 0
                
                comparison_data.append({
                    '指标': metric.replace('_', ' ').title(),
                    '正常时期': normal_mean,
                    '异常时期': anomaly_mean,
                    '变化率 (%)': change
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            fig = px.bar(
                comparison_df,
                x='指标',
                y=['正常时期', '异常时期'],
                barmode='group',
                title='指标对比',
                labels={'value': '值', 'variable': '时期'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(comparison_df, use_container_width=True)
        
        with tab3:
            st.subheader("统计摘要")
            
            stats_df = data.describe()
            st.dataframe(stats_df, use_container_width=True)
    
    def render_causal_graph_page(self):
        """渲染因果图页面"""
        st.header("🔗 因果图分析")
        
        data = self.load_or_generate_data()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("因果图可视化")
            
            if self.causal_graph is None:
                generator = EcommerceDataGenerator()
                self.causal_graph = generator.get_causal_graph()
                self.save_state()
            
            edges = []
            lines = self.causal_graph.strip().split('\n')
            for line in lines:
                line = line.strip()
                if '->' in line:
                    parts = line.split('->')
                    if len(parts) == 2:
                        source = parts[0].strip()
                        target = parts[1].strip().rstrip(';').strip()
                        edges.append((source, target))
            
            G = nx.DiGraph(edges)
            
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
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
                if node == 'profit':
                    node_color.append('#FF6B6B')
                elif node in ['shopping_event', 'ad_spend', 'unit_price']:
                    node_color.append('#4ECDC4')
                else:
                    node_color.append('#95E1D3')
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=node_text,
                textposition="top center",
                marker=dict(
                    color=node_color,
                    size=30,
                    line_width=2
                ),
                hoverinfo='text'
            )
            
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title='电商利润因果图',
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                           ))
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
            <h4>因果图说明</h4>
            <p><strong>核心因果链</strong>：</p>
            <ul>
                <li>Shopping Event → Ad Spend → Page Views → Sold Units → Revenue → Profit</li>
                <li>Unit Price → Sold Units → Revenue → Profit</li>
                <li>Ad Spend → Operational Cost → Profit</li>
            </ul>
            </div>
            
            <div class="info-box">
            <h4>节点颜色说明</h4>
            <ul>
                <li><span style="color:#FF6B6B">● 红色</span>：结果变量 (Profit)</li>
                <li><span style="color:#4ECDC4">● 青色</span>：关键原因变量</li>
                <li><span style="color:#95E1D3">● 浅绿</span>：中间变量</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("因果图定义")
            st.code(self.causal_graph, language='python')
    
    def render_analysis_page(self):
        """渲染根因分析页面"""
        st.header("🔍 根因分析")
        
        data = self.load_or_generate_data()
        
        st.markdown("""
        <div class="info-box">
        <h4>分析步骤</h4>
        <ol>
            <li>创建结构因果模型 (SCM)</li>
            <li>自动分配因果机制</li>
            <li>拟合模型</li>
            <li>计算箭头强度</li>
            <li>识别根本原因</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("开始根因分析", type="primary"):
            with st.spinner("正在进行根因分析..."):
                try:
                    if self.analyzer is None:
                        self.analyzer = RootCauseAnalyzer(data)
                    
                    if self.analyzer.causal_graph is None:
                        self.analyzer.build_causal_graph_from_dot(self.causal_graph)
                    
                    if self.analyzer.scm is None:
                        self.analyzer.create_structural_causal_model()
                    
                    self.analyzer.auto_assign_causal_mechanisms()
                    
                    self.analyzer.fit_model()
                    
                    self.analysis_results = self.analyzer.analyze_root_causes('profit', top_k=10)
                    
                    self.save_state()
                    
                    st.success("✅ 根因分析完成！")
                    
                except Exception as e:
                    st.error(f"❌ 分析失败: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        if self.analysis_results is not None and not self.analysis_results.empty:
            st.subheader("根因分析结果")
            
            st.dataframe(self.analysis_results, use_container_width=True)
            
            fig = px.bar(
                self.analysis_results,
                x='cause',
                y='abs_strength',
                title='根本原因影响强度',
                labels={'cause': '原因变量', 'abs_strength': '影响强度'},
                color='abs_strength',
                color_continuous_scale='Viridis'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="success-box">
            <h4>分析结论</h4>
            <p>根据箭头强度分析，影响利润下降的主要原因是：</p>
            <ul>
                <li><strong>广告支出减少</strong>：导致页面浏览量下降，进而影响销售数量和收入</li>
                <li><strong>单价上涨</strong>：直接影响销售数量，降低转化率</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def render_counterfactual_page(self):
        """渲染反事实分析页面"""
        st.header("🎯 反事实分析")
        
        data = self.load_or_generate_data()
        
        st.markdown("""
        <div class="info-box">
        <h4>What-if分析</h4>
        <p>通过反事实分析，我们可以模拟不同干预措施对利润的影响。</p>
        <p>例如：如果我们将广告支出增加到某个值，利润会如何变化？</p>
        </div>
        """, unsafe_allow_html=True)
        
        if self.analyzer is None or not self.analyzer.fitted:
            st.warning("⚠️ 请先在'根因分析'页面完成模型训练")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("干预设置")
            
            ad_spend_change = st.slider(
                "广告支出变化 (%)",
                min_value=-50,
                max_value=100,
                value=50,
                step=10
            )
            
            unit_price_change = st.slider(
                "单价变化 (%)",
                min_value=-20,
                max_value=20,
                value=-10,
                step=5
            )
            
            if st.button("运行反事实分析", type="primary"):
                with st.spinner("正在进行反事实分析..."):
                    try:
                        current_ad_spend = data['ad_spend'].mean()
                        current_price = data['unit_price'].mean()
                        
                        intervention_dict = {
                            'ad_spend': lambda x: current_ad_spend * (1 + ad_spend_change / 100),
                            'unit_price': lambda x: current_price * (1 + unit_price_change / 100)
                        }
                        
                        what_if_samples = self.analyzer.what_if_analysis(
                            intervention_dict,
                            'profit',
                            num_samples=1000
                        )
                        
                        original_profit = data['profit'].mean()
                        what_if_profit = what_if_samples['profit'].mean()
                        
                        st.session_state.what_if_results = {
                            'original_profit': original_profit,
                            'what_if_profit': what_if_profit,
                            'samples': what_if_samples
                        }
                        
                        st.success("✅ 反事实分析完成！")
                        
                    except Exception as e:
                        st.error(f"❌ 分析失败: {str(e)}")
        
        with col2:
            if 'what_if_results' in st.session_state:
                results = st.session_state.what_if_results
                
                st.subheader("分析结果")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("当前平均利润", f"${results['original_profit']:,.2f}")
                with col_b:
                    st.metric("干预后平均利润", f"${results['what_if_profit']:,.2f}")
                
                profit_change = (results['what_if_profit'] - results['original_profit']) / results['original_profit'] * 100
                st.metric("利润变化", f"{profit_change:.2f}%")
                
                fig = px.histogram(
                    results['samples'],
                    x='profit',
                    title='干预后利润分布',
                    labels={'profit': '利润 ($)'},
                    nbins=50
                )
                
                fig.add_vline(
                    x=results['original_profit'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text="当前利润"
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    def render_llm_explanation_page(self):
        """渲染AI解释页面"""
        st.header("🤖 AI智能解释")
        
        st.markdown("""
        <div class="info-box">
        <h4>AI解释功能</h4>
        <p>使用大语言模型（LLM）对根因分析结果进行智能解释，生成易于理解的业务洞察。</p>
        <p><strong>功能特点：</strong></p>
        <ul>
            <li>自动解释根因分析结果</li>
            <li>生成业务洞察和建议</li>
            <li>支持多轮对话式问答</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if self.llm_explainer is None:
            st.warning("⚠️ 请先在侧边栏配置并初始化LLM解释器")
            st.info("💡 提示：您需要配置SiliconFlow API密钥才能使用AI解释功能")
            return
        
        if self.analysis_results is None:
            st.warning("⚠️ 请先在'根因分析'页面完成分析")
            return
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("生成解释")
            
            explanation_type = st.radio(
                "选择解释类型",
                ["根因分析解释", "改进建议", "自定义问题"]
            )
            
            if explanation_type == "根因分析解释":
                if st.button("生成根因分析解释", type="primary"):
                    with st.spinner("AI正在生成解释..."):
                        try:
                            data = self.load_or_generate_data()
                            
                            normal_data = data[~data['is_anomaly_period']]
                            anomaly_data = data[data['is_anomaly_period']]
                            
                            comparison_data = []
                            metrics = ['profit', 'revenue', 'sold_units', 'page_views', 'ad_spend', 'unit_price', 'operational_cost']
                            
                            for metric in metrics:
                                normal_mean = normal_data[metric].mean()
                                anomaly_mean = anomaly_data[metric].mean()
                                change = (anomaly_mean - normal_mean) / normal_mean * 100 if normal_mean != 0 else 0
                                
                                comparison_data.append({
                                    'variable': metric,
                                    'normal_mean': normal_mean,
                                    'anomaly_mean': anomaly_mean,
                                    'change_percent': change
                                })
                            
                            comparison_df = pd.DataFrame(comparison_data)
                            
                            explanation = self.llm_explainer.generate_explanation(
                                analysis_results=self.analysis_results,
                                comparison_df=comparison_df,
                                causal_graph=self.causal_graph,
                                scenario_background="某在线商店销售智能手机，零售价$999。2021年利润保持稳定，但在2022年初突然出现显著下降。"
                            )
                            
                            self.llm_explanation = explanation
                            self.save_state()
                            
                            st.success("✅ 解释生成成功！")
                            
                        except Exception as e:
                            st.error(f"❌ 生成失败: {str(e)}")
            
            elif explanation_type == "改进建议":
                if st.button("生成改进建议", type="primary"):
                    with st.spinner("AI正在生成建议..."):
                        try:
                            suggestions = self.llm_explainer.generate_improvement_suggestions(
                                analysis_results=self.analysis_results,
                                causal_graph=self.causal_graph,
                                scenario_description="某在线商店销售智能手机，2022年初利润突然下降。",
                                problem_description="利润相比2021年显著下降，需要找出根本原因并提出改进措施。"
                            )
                            
                            self.llm_explanation = suggestions
                            self.save_state()
                            
                            st.success("✅ 建议生成成功！")
                            
                        except Exception as e:
                            st.error(f"❌ 生成失败: {str(e)}")
            
            else:
                user_question = st.text_area(
                    "输入您的问题",
                    placeholder="例如：为什么广告支出减少会导致利润下降？",
                    height=100
                )
                
                if st.button("提问", type="primary"):
                    if user_question:
                        with st.spinner("AI正在思考..."):
                            try:
                                data = self.load_or_generate_data()
                                
                                context = f"""
                                场景：在线商店智能手机销售利润分析
                                问题：2022年初利润突然下降
                                
                                根因分析结果：
                                {self.analysis_results.to_string() if self.analysis_results is not None else '无'}
                                
                                因果图：
                                {self.causal_graph if self.causal_graph else '无'}
                                
                                用户问题：{user_question}
                                """
                                
                                prompt = f"""你是一个专业的电商数据分析顾问。请根据以下信息回答用户的问题。

{context}

请用专业但易懂的语言回答，适合企业管理层阅读。
"""
                                
                                self.llm_explainer._save_prompt(prompt)
                                
                                import openai
                                response = self.llm_explainer.client.chat.completions.create(
                                    model=self.llm_explainer.model,
                                    messages=[
                                        {"role": "system", "content": "你是一个专业的电商数据分析顾问。"},
                                        {"role": "user", "content": prompt}
                                    ],
                                    temperature=0.7,
                                    max_tokens=2000
                                )
                                
                                self.llm_explanation = response.choices[0].message.content
                                self.save_state()
                                
                                st.success("✅ 回答生成成功！")
                                
                            except Exception as e:
                                st.error(f"❌ 生成失败: {str(e)}")
                    else:
                        st.warning("⚠️ 请输入问题")
        
        with col2:
            st.subheader("AI解释结果")
            
            if self.llm_explanation:
                st.markdown(self.llm_explanation)
                
                st.download_button(
                    label="下载解释",
                    data=self.llm_explanation,
                    file_name="ai_explanation.md",
                    mime="text/markdown"
                )
            else:
                st.info("👆 请先生成AI解释")
    
    def run(self):
        """运行应用"""
        page = self.render_sidebar()
        
        if page == "场景介绍":
            self.render_scenario_page()
        elif page == "数据探索":
            self.render_data_exploration_page()
        elif page == "因果图":
            self.render_causal_graph_page()
        elif page == "根因分析":
            self.render_analysis_page()
        elif page == "反事实分析":
            self.render_counterfactual_page()
        elif page == "AI解释":
            self.render_llm_explanation_page()


if __name__ == "__main__":
    app = RCADemoApp()
    app.run()
