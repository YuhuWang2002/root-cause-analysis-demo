"""
制造企业根因分析系统 - Web界面

使用Streamlit构建交互式Web应用，包含：
1. 场景介绍和教学内容
2. 因果图可视化
3. 数据探索和分析
4. DoWhy因果分析结果
5. 大模型智能解释
6. 结论和建议展示
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
from llm_explainer import LLMExplainer
from llm_agent import LLMAgent

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
    .llm-box {
        background-color: #f0f8ff;
        border-left: 4px solid #4169E1;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


class RootCauseAnalysisWebApp:
    """根因分析Web应用"""
    
    def __init__(self):
        # CSV文件路径
        self.data_csv_path = "production_data.csv"
        self.anomaly_factors_json_path = "anomaly_factors.json"
        
        # 使用 st.session_state 持久化状态
        if 'data' not in st.session_state:
            st.session_state.data = None
        if 'anomaly_factors' not in st.session_state:
            st.session_state.anomaly_factors = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'pipeline' not in st.session_state:
            st.session_state.pipeline = None
        if 'llm_explainer' not in st.session_state:
            st.session_state.llm_explainer = None
        if 'llm_explanation' not in st.session_state:
            st.session_state.llm_explanation = None
        if 'llm_agent' not in st.session_state:
            st.session_state.llm_agent = None
        if 'causal_graph_derived' not in st.session_state:
            st.session_state.causal_graph_derived = None
        if 'agent_outcome_entity' not in st.session_state:
            st.session_state.agent_outcome_entity = None
        if 'causal_graph_result' not in st.session_state:
            st.session_state.causal_graph_result = None
        
        self.data = st.session_state.data
        self.anomaly_factors = st.session_state.anomaly_factors
        self.analysis_results = st.session_state.analysis_results
        self.pipeline = st.session_state.pipeline
        self.llm_explainer = st.session_state.llm_explainer
        self.llm_explanation = st.session_state.llm_explanation
        self.llm_agent = st.session_state.llm_agent
        self.causal_graph_derived = st.session_state.causal_graph_derived
        self.agent_outcome_entity = st.session_state.agent_outcome_entity
        
    def _save_state(self):
        """保存状态到 session_state"""
        st.session_state.data = self.data
        st.session_state.anomaly_factors = self.anomaly_factors
        st.session_state.analysis_results = self.analysis_results
        st.session_state.pipeline = self.pipeline
        st.session_state.llm_explainer = self.llm_explainer
        st.session_state.llm_explanation = self.llm_explanation
        st.session_state.llm_agent = self.llm_agent
        st.session_state.causal_graph_derived = self.causal_graph_derived
        # 注意：agent_outcome_entity由Streamlit自动管理，不需要手动保存
        
    def load_data(self):
        """加载数据"""
        if self.data is None:
            with st.spinner("加载数据..."):
                # 尝试从CSV文件读取
                if os.path.exists(self.data_csv_path):
                    try:
                        import json
                        self.data = pd.read_csv(self.data_csv_path, parse_dates=['date'])
                        
                        # 读取异常因素配置
                        if os.path.exists(self.anomaly_factors_json_path):
                            with open(self.anomaly_factors_json_path, 'r', encoding='utf-8') as f:
                                self.anomaly_factors = json.load(f)
                        else:
                            self.anomaly_factors = {
                                "payment_delay": True,
                                "supplier_issue": True,
                                "employee_turnover": False,
                                "equipment_failure": False
                            }
                        
                        self.pipeline = RootCauseAnalysisPipeline(self.data)
                        st.success(f"✅ 从CSV文件加载了 {len(self.data)} 条数据记录")
                    except Exception as e:
                        st.warning(f"⚠️ 读取CSV文件失败: {str(e)}，将重新生成数据")
                        self._generate_new_data()
                else:
                    # CSV文件不存在，生成新数据
                    self._generate_new_data()
            self._save_state()
        return self.data, self.anomaly_factors
    
    def _generate_new_data(self):
        """生成新数据并保存到CSV"""
        with st.spinner("生成模拟数据..."):
            self.data, self.anomaly_factors = create_demo_scenario()
            self.pipeline = RootCauseAnalysisPipeline(self.data)
            
            # 保存到CSV文件
            try:
                self.data.to_csv(self.data_csv_path, index=False, encoding='utf-8')
                
                # 保存异常因素配置
                import json
                with open(self.anomaly_factors_json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.anomaly_factors, f, ensure_ascii=False, indent=2)
                
                st.success(f"✅ 已生成并保存 {len(self.data)} 条数据记录到 {self.data_csv_path}")
            
            except Exception as e:
                st.warning(f"⚠️ 保存数据到CSV失败: {str(e)}")
    
    def init_llm_agent(self, ontology_api_url: str = "http://localhost:8000", llm_api_key: str = None, llm_base_url: str = None, llm_model: str = None):
        """
        初始化LLM Agent
        
        Args:
            ontology_api_url: 本体API地址
            llm_api_key: 大模型API密钥
            llm_base_url: 大模型API基础URL
            llm_model: 大模型名称
        """
        if not llm_api_key:
            st.warning("⚠️ 请输入LLM API密钥")
            return False
        
        try:
            from llm_agent import LLMAgentSync
            self.llm_agent = LLMAgentSync(
                ontology_api_url=ontology_api_url, 
                llm_api_key=llm_api_key,
                llm_base_url=llm_base_url,
                llm_model=llm_model
            )
            # 保存状态到会话
            self._save_state()
            st.success(f"✅ LLM Agent已初始化，连接到本体API: {ontology_api_url}")
            if llm_model:
                st.info(f"📝 使用模型: {llm_model}")
            return True
        except Exception as e:
            st.error(f"❌ 初始化LLM Agent失败: {str(e)}")
            return False
    
    async def derive_causal_graph_with_agent(self, scenario_description: str, outcome_entity: str = "production_efficiency"):
        """
        使用Agent推导因果图
        
        Args:
            scenario_description: 场景描述
            outcome_entity: 结果实体
            
        Returns:
            因果图推导响应
        """
        if not self.llm_agent:
            st.error("❌ 请先初始化LLM Agent")
            return None
        
        try:
            with st.spinner("LLM正在推导因果图..."):
                from llm_agent import CausalGraphDerivationRequest
                
                request = CausalGraphDerivationRequest(
                    scenario_description=scenario_description,
                    outcome_entity=outcome_entity
                )
                
                response = self.llm_agent.derive_causal_graph(request)
                
                # 保存推导结果
                self.causal_graph_derived = {
                    "causal_graph": response.causal_graph,
                    "reasoning": response.reasoning,
                    "suggested_data_fields": response.suggested_data_fields,
                    "required_entities": response.required_entities
                }
                
                st.success(f"✅ 因果图推导完成！")
                st.info(f"推理过程：\n{response.reasoning}")
                
                return response
        except Exception as e:
            st.error(f"❌ 推导因果图失败: {str(e)}")
            return None
    
    def run_analysis(self):
        """运行分析"""
        if self.analysis_results is None:
            with st.spinner("运行根因分析..."):
                self.analysis_results = self.pipeline.run_full_analysis()
            self._save_state()
        return self.analysis_results
    
    def init_llm_explainer(self, api_type: str, api_key: str, model: str = None, base_url: str = None):
        """初始化大模型解释器"""
        self.llm_explainer = LLMExplainer(api_type=api_type, api_key=api_key, model=model, base_url=base_url)
        self.llm_explanation = None
        self._save_state()
    
    def generate_llm_explanation(self):
        """生成大模型解释"""
        print("[APP] generate_llm_explanation 被调用")
        print(f"  - llm_explainer: {self.llm_explainer is not None}")
        print(f"  - analysis_results: {self.analysis_results is not None}")
        print(f"  - llm_explanation: {self.llm_explanation is not None}")
        
        if self.llm_explanation is None and self.llm_explainer is not None:
            print("[APP] 开始生成解释...")
            
            if self.analysis_results is None:
                print("[APP] analysis_results 为空，先运行分析...")
                self.run_analysis()
            
            print(f"[APP] analysis_results 状态: {self.analysis_results is not None}")
            print(f"[APP] comparison 数据: {self.analysis_results['comparison'] is not None if self.analysis_results else 'N/A'}")
            print(f"[APP] causal_analysis 数据: {self.analysis_results['causal_analysis'] is not None if self.analysis_results else 'N/A'}")
            
            with st.spinner("大模型正在生成解释..."):
                print("[APP] 调用 llm_explainer.generate_explanation...")
                
                counterfactual_results = None
                if 'counterfactual_analysis' in self.analysis_results:
                    counterfactual_results = self.analysis_results['counterfactual_analysis']
                
                self.llm_explanation = self.llm_explainer.generate_explanation(
                    self.analysis_results,
                    self.analysis_results['comparison'],
                    self.analysis_results['causal_analysis'],
                    counterfactual_results
                )
                self._save_state()
                print(f"[APP] 解释生成完成，长度: {len(self.llm_explanation) if self.llm_explanation else 0}")
        
        return self.llm_explanation
    
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
            ["场景介绍", "因果图", "数据分析", "因果分析", "AI智能解释", "Agent分析"]
        )
        
        st.sidebar.markdown("### 大模型配置")
        with st.sidebar.expander("配置大模型API"):
            st.info("从 modelkey.cfg 文件读取默认配置，可以手动修改")
            
            # 读取modelkey.cfg文件获取默认值
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
                
                if default_api_key:
                    st.info(f"✅ 默认API Key: {default_api_key[:20]}...")
                else:
                    st.warning("⚠️ 未找到默认API Key")
                
                if default_base_url:
                    st.info(f"📡 默认Base URL: {default_base_url}")
                else:
                    st.warning("⚠️ 未找到默认Base URL")
                
                if default_model:
                    st.info(f"📝 默认Model: {default_model}")
                else:
                    st.warning("⚠️ 未找到默认Model")
            else:
                st.error("❌ modelkey.cfg 文件不存在")
            
            # 用户可以手动输入配置
            api_key = st.text_input(
                "API密钥",
                value=default_api_key,
                type="password",
                help="输入您的API密钥（留空使用默认值）"
            )
            
            base_url = st.text_input(
                "API Base URL",
                value=default_base_url,
                placeholder="默认: https://api.siliconflow.cn/v1",
                help="自定义API端点（留空使用默认值）"
            )
            
            model = st.text_input(
                "模型名称",
                value=default_model,
                placeholder="默认: Qwen/Qwen2.5-7B-Instruct",
                help="输入模型名称（留空使用默认值）"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("测试大模型连接"):
                    print(f"[APP] 用户点击了'测试大模型连接'按钮")
                    if api_key:
                        with st.spinner("正在测试大模型连接..."):
                            try:
                                print(f"[APP] 开始初始化LLM Agent...")
                                success = self.init_llm_agent(
                                    "http://localhost:8000",
                                    api_key,
                                    base_url,
                                    model
                                )
                                
                                print(f"[APP] init_llm_agent返回: {success}")
                                
                                if success:
                                    st.success("✅ 大模型连接测试成功！")
                                    st.session_state.llm_agent_initialized = True
                                else:
                                    st.error("❌ 大模型连接测试失败！")
                            except Exception as e:
                                print(f"[APP] 初始化LLM Agent时发生异常: {str(e)}")
                                st.error(f"❌ 大模型连接测试失败: {str(e)}")
                    else:
                        st.warning("请输入API密钥")
            with col2:
                if st.button("初始化大模型解释器"):
                    print(f"[APP] 用户点击了'初始化大模型解释器'按钮")
                    if api_key:
                        with st.spinner("正在初始化大模型解释器..."):
                            try:
                                print(f"[APP] 开始初始化LLM Explainer...")
                                self.init_llm_explainer(
                                    "siliconflow",
                                    api_key,
                                    model,
                                    base_url
                                )
                                st.success("✅ 大模型解释器初始化成功！")
                                st.session_state.llm_explainer_initialized = True
                            except Exception as e:
                                print(f"[APP] 初始化LLM Explainer时发生异常: {str(e)}")
                                st.error(f"❌ 大模型解释器初始化失败: {str(e)}")
                    else:
                        st.warning("请输入API密钥")
        
        st.sidebar.markdown("### 关于系统")
        st.sidebar.info(
            "这是一个基于DoWhy框架的根因分析系统\n\n"+
            "**用途**：分析制造企业生产效率下降的根本原因\n\n"+
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
    
    def render_agent_analysis_page(self):
        """渲染Agent分析页面"""
        st.header("🤖 Agent智能分析")
        
        st.markdown("""
        <div class="llm-box">
        <h4>Agent驱动的因果分析</h4>
        <p>通过LLM理解本体并推导因果图，实现智能的根因分析流程。</p>
        <p><strong>操作步骤：</strong></p>
        <ol>
            <li>查看本体关系</li>
            <li>输入场景描述</li>
            <li>选择结果实体</li>
            <li>点击"推导因果图"按钮</li>
            <li>查看推导结果</li>
            <li>系统自动生成数据并分析</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # 步骤0：查看本体关系
        st.markdown("---")
        st.markdown("### 步骤0：查看本体关系")
        st.info("查看当前业务本体的实体和关系定义，了解系统的知识结构。")
        
        # 初始化会话状态
        if 'ontology_schema' not in st.session_state:
            st.session_state.ontology_schema = None
        if 'ontology_graph_image' not in st.session_state:
            st.session_state.ontology_graph_image = None
        
        # 查看本体关系按钮
        if st.button("查看本体关系", type="primary"):
            with st.spinner("正在读取本体Schema..."):
                try:
                    import requests
                    
                    # 从本体API读取schema
                    response = requests.get("http://localhost:8000/schema")
                    response.raise_for_status()
                    schema = response.json()
                    
                    # 保存schema到会话状态
                    st.session_state.ontology_schema = schema
                    
                    # 创建NetworkX图
                    import networkx as nx
                    import matplotlib.pyplot as plt
                    import io
                    import base64
                    
                    # 设置中文字体
                    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']  # 用来正常显示中文标签
                    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
                    
                    G = nx.DiGraph()
                    
                    # 添加实体节点
                    entity_map = {}
                    for entity_type in schema.get('entity_types', []):
                        entity_id = entity_type.get('id')
                        entity_name = entity_type.get('name', entity_id)
                        entity_map[entity_id] = entity_name
                        G.add_node(entity_id, type='entity', name=entity_name)
                    
                    # 添加指标节点
                    metric_map = {}
                    for metric in schema.get('metric_definitions', []):
                        metric_id = metric.get('id')
                        metric_name = metric.get('name', metric_id)
                        metric_map[metric_id] = metric_name
                        # 添加指标节点，类型为'metric'
                        G.add_node(metric_id, type='metric', name=metric_name)
                    
                    # 添加关系边
                    for relation_type in schema.get('relation_types', []):
                        relation_id = relation_type.get('id')
                        relation_name = relation_type.get('name', relation_id)
                        source_types = relation_type.get('source_types', [])
                        target_types = relation_type.get('target_types', [])
                        
                        # 为每个源类型和目标类型创建边
                        for source_type in source_types:
                            for target_type in target_types:
                                if source_type in entity_map and target_type in entity_map:
                                    G.add_edge(source_type, target_type, label=relation_name)
                    
                    # 添加指标与实体之间的边
                    for metric in schema.get('metric_definitions', []):
                        metric_id = metric.get('id')
                        source_entity_type = metric.get('source_entity_type')
                        
                        # 将指标连接到其源实体类型
                        if metric_id in metric_map and source_entity_type in entity_map:
                            G.add_edge(source_entity_type, metric_id, label="has_metric")
                    
                    # 设置图形大小
                    plt.figure(figsize=(12, 8))
                    
                    # 使用spring布局
                    pos = nx.spring_layout(G, k=0.3, iterations=50)
                    
                    # 分离实体节点和指标节点
                    entity_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') == 'entity']
                    metric_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') == 'metric']
                    
                    # 绘制实体节点（蓝色）
                    nx.draw_networkx_nodes(G, pos, nodelist=entity_nodes, node_size=1000, node_color='#6495ED', alpha=0.8, node_shape='o')
                    
                    # 绘制指标节点（红色，使用不同形状）
                    nx.draw_networkx_nodes(G, pos, nodelist=metric_nodes, node_size=800, node_color='#DC143C', alpha=0.8, node_shape='s')  # s表示正方形
                    
                    # 绘制边
                    nx.draw_networkx_edges(G, pos, edge_color='#888888', arrowsize=20, width=1.5)
                    
                    # 绘制边标签
                    edge_labels = nx.get_edge_attributes(G, 'label')
                    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_family='Arial Unicode MS')
                    
                    # 准备所有节点的标签
                    node_labels = {}
                    # 添加实体标签
                    for entity_id, entity_name in entity_map.items():
                        node_labels[entity_id] = entity_name
                    # 添加指标标签
                    for metric_id, metric_name in metric_map.items():
                        node_labels[metric_id] = metric_name
                    
                    # 绘制节点标签
                    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_weight='bold', font_family='Arial Unicode MS')
                    
                    # 添加图例
                    plt.legend(
                        handles=[
                            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#6495ED', markersize=10, label='实体'),
                            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#DC143C', markersize=10, label='指标')
                        ],
                        loc='best',
                        prop={'family': 'Arial Unicode MS'}
                    )
                    
                    # 美化图形
                    plt.title('本体关系与指标图', fontsize=16, fontweight='bold')
                    plt.axis('off')
                    plt.tight_layout()
                    
                    # 保存到内存
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                    buf.seek(0)
                    
                    # 转换为base64
                    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    plt.close()
                    
                    # 保存图像到会话状态
                    st.session_state.ontology_graph_image = image_base64
                    
                    st.success("✅ 本体Schema读取成功！")
                except Exception as e:
                    st.error(f"❌ 读取本体Schema失败: {str(e)}")
                    # 清除失败的结果
                    st.session_state.ontology_schema = None
                    st.session_state.ontology_graph_image = None
        
        # 基于会话状态显示本体关系图和详细信息（持久化显示）
        if st.session_state.ontology_schema and st.session_state.ontology_graph_image:
            schema = st.session_state.ontology_schema
            image_base64 = st.session_state.ontology_graph_image
            
            # 展示本体关系图形
            st.markdown("#### � 本体关系图")
            st.image(f"data:image/png;base64,{image_base64}")
            
            # 展示本体详细信息
            st.markdown("#### 📋 本体详细信息")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**实体类型**")
                for entity_type in schema.get('entity_types', []):
                    entity_id = entity_type.get('id')
                    entity_name = entity_type.get('name', entity_id)
                    with st.expander(f"{entity_name} ({entity_id})"):
                        st.write(f"**描述**：{entity_type.get('description', '无')}")
                        attributes = entity_type.get('attributes', [])
                        if attributes:
                            # 处理属性，确保每个属性都是字符串
                            attr_strings = []
                            for attr in attributes:
                                if isinstance(attr, dict):
                                    # 如果是字典，使用id或name字段
                                    attr_name = attr.get('name', attr.get('id', str(attr)))
                                    attr_strings.append(attr_name)
                                else:
                                    # 如果是字符串，直接使用
                                    attr_strings.append(str(attr))
                            st.write(f"**属性**：{', '.join(attr_strings)}")
                        else:
                            st.write("**属性**：无")
            
            with col2:
                st.markdown("**关系类型**")
                for relation_type in schema.get('relation_types', []):
                    relation_id = relation_type.get('id')
                    relation_name = relation_type.get('name', relation_id)
                    with st.expander(f"{relation_name} ({relation_id})"):
                        st.write(f"**描述**：{relation_type.get('description', '无')}")
                        source_types = relation_type.get('source_types', [])
                        target_types = relation_type.get('target_types', [])
                        
                        # 处理源实体类型
                        if source_types:
                            # 确保每个源类型都是字符串
                            source_strings = []
                            for source in source_types:
                                if isinstance(source, dict):
                                    source_name = source.get('name', source.get('id', str(source)))
                                    source_strings.append(source_name)
                                else:
                                    source_strings.append(str(source))
                            st.write(f"**源实体类型**：{', '.join(source_strings)}")
                        else:
                            st.write("**源实体类型**：无")
                        
                        # 处理目标实体类型
                        if target_types:
                            # 确保每个目标类型都是字符串
                            target_strings = []
                            for target in target_types:
                                if isinstance(target, dict):
                                    target_name = target.get('name', target.get('id', str(target)))
                                    target_strings.append(target_name)
                                else:
                                    target_strings.append(str(target))
                            st.write(f"**目标实体类型**：{', '.join(target_strings)}")
                        else:
                            st.write("**目标实体类型**：无")
        
        # 步骤1：输入场景描述
        st.markdown("---")
        st.markdown("### 步骤1：输入场景描述")
        
        scenario_description = st.text_area(
            "场景描述",
            placeholder="例如：某制造企业在2024年12月发现生产效率相比11月显著下降，需要分析原因并提出改进措施。",
            height=100,
            help="描述您遇到的问题场景，LLM将根据描述和本体信息推导因果图"
        )
        
        # 步骤2：选择结果实体
        st.markdown("### 步骤2：选择结果实体")
        
        # 从session_state恢复outcome_entity
        if st.session_state.agent_outcome_entity is not None:
            outcome_entity = st.session_state.agent_outcome_entity
            print(f"[APP] 从session_state恢复outcome_entity: {outcome_entity}")
        else:
            outcome_entity = None
        
        if self.llm_agent:
            outcome_entity = st.selectbox(
                "选择结果实体（要分析的目标）",
                index=["production_efficiency", "supplier_efficiency", "parts_availability", "avg_employee_skill", "equipment_status"].index(outcome_entity) if outcome_entity else 0,
                options=["production_efficiency", "supplier_efficiency", "parts_availability", "avg_employee_skill", "equipment_status"],
                format_func=lambda x: {
                    "production_efficiency": "生产效率",
                    "supplier_efficiency": "供应商效率",
                    "parts_availability": "零部件可用性",
                    "avg_employee_skill": "员工技能水平",
                    "equipment_status": "设备状态"
                }[x],
                help="选择要分析的结果实体",
                key="agent_outcome_entity"
            )
        else:
            st.warning("⚠️ 请先初始化LLM Agent")
            outcome_entity = None
        
        # 步骤3：推导因果图
        st.markdown("### 步骤3：推导因果图")
        
        # 从会话状态获取最新的outcome_entity
        current_outcome_entity = st.session_state.agent_outcome_entity
        
        if current_outcome_entity and self.llm_agent:
            # 推导因果图按钮
            if st.button("推导因果图", type="primary"):
                with st.spinner("LLM正在推导因果图，请稍候..."):
                    from llm_agent import CausalGraphDerivationRequest
                    
                    request = CausalGraphDerivationRequest(
                        scenario_description=scenario_description,
                        outcome_entity=current_outcome_entity
                    )
                    
                    result = self.llm_agent.derive_causal_graph(request)
                    
                    if result:
                        # 保存结果到会话状态
                        st.session_state.causal_graph_result = result
                        st.success("✅ 因果图推导完成！")
                    else:
                        st.error("❌ 推导因果图失败")
                        # 清除失败的结果
                        st.session_state.causal_graph_result = None
            
            # 基于会话状态显示因果图结果（持久化显示）
            if st.session_state.causal_graph_result:
                result = st.session_state.causal_graph_result
                
                # 展示推导结果
                st.markdown("#### 📊 推导结果")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**因果图结构**")
                    
                    # 显示因果图
                    causal_graph = result.causal_graph
                    
                    # 文本格式展示
                    st.subheader("文本格式")
                    for source, targets in causal_graph.items():
                        if len(targets) > 0:
                            st.markdown(f"- {source} → {', '.join(targets)}")
                    
                    # 图形化展示
                    st.subheader("图形化展示")
                    try:
                        import networkx as nx
                        import matplotlib.pyplot as plt
                        import io
                        import base64
                        
                        # 创建有向图
                        G = nx.DiGraph()
                        
                        # 添加节点和边
                        for source, targets in causal_graph.items():
                            for target in targets:
                                G.add_edge(source, target)
                        
                        # 设置图形大小
                        plt.figure(figsize=(12, 8))
                        
                        # 使用spring布局
                        pos = nx.spring_layout(G, k=0.3, iterations=50)
                        
                        # 绘制节点
                        nx.draw_networkx_nodes(G, pos, node_size=800, node_color='#6495ED', alpha=0.8)
                        
                        # 绘制边
                        nx.draw_networkx_edges(G, pos, edge_color='#888888', arrowsize=20, width=1.5)
                        
                        # 绘制节点标签
                        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_family='SimHei')
                        
                        # 美化图形
                        plt.title('因果关系图', fontsize=16, fontweight='bold')
                        plt.axis('off')
                        plt.tight_layout()
                        
                        # 保存到内存
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                        buf.seek(0)
                        
                        # 转换为base64
                        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                        plt.close()
                        
                        # 在Streamlit中显示
                        st.image(f"data:image/png;base64,{image_base64}")
                    except Exception as e:
                        st.warning(f"图形化展示失败: {str(e)}")
                        st.info("将使用文本格式展示因果图")
                    
                    # 显示推理过程
                    st.markdown("**推理过程**")
                    st.markdown(result.reasoning)
                    
                    # 显示建议的数据字段
                    st.markdown("**建议的数据字段**")
                    for field in result.suggested_data_fields:
                        st.markdown(f"- {field}")
                    
                    # 显示需要的实体
                    st.markdown("**需要的实体**")
                    for entity_id in result.required_entities:
                        st.markdown(f"- {entity_id}")
                
                with col2:
                    st.markdown("**下一步操作**")
                    st.info("""
                    1. 系统将根据推导的因果图生成数据
                    2. 自动运行DoWhy因果分析
                    3. 生成智能分析报告
                    """)
        else:
            st.info("👆 请先完成步骤1和步骤2")
            # 清除因果图结果
            st.session_state.causal_graph_result = None
        
        # 4.1 根因分析
        st.markdown("---")
        st.markdown("### 4.1 根因分析")
        
        if st.session_state.causal_graph_result:
            st.info("基于因果图推导结果，系统将生成数据并运行完整的分析流程。")
            
            if st.button("根因分析", type="primary"):
                self._generate_data_from_agent(st.session_state.causal_graph_result)
            
            # 基于会话状态显示DoWhy分析结果（持久化显示）
            if self.analysis_results is not None:
                st.markdown("#### 📊 DoWhy分析结果")
                
                with st.expander("查看指标对比分析", expanded=True):
                    comparison_df = self.analysis_results['comparison']
                    st.dataframe(comparison_df.style.format({
                        'normal_mean': '{:.3f}',
                        'anomaly_mean': '{:.3f}',
                        'change_percent': '{:.2f}%',
                        'abs_change': '{:.2f}%'
                    }))
                
                with st.expander("查看因果效应分析"):
                    causal_df = self.analysis_results['causal_analysis']
                    valid_causal = causal_df[causal_df['causal_effect'].notna()]
                    st.dataframe(valid_causal.style.format({
                        'causal_effect': '{:.4f}'
                    }))
                

            
            # 4.2 智能解释
            st.markdown("---")
            st.markdown("### 4.2 智能解释")
            
            if self.llm_explainer is None:
                st.warning("⚠️ 请先在侧边栏配置SiliconFlow API密钥并初始化大模型解释器")
                st.info("""
                **配置步骤：**
                
                1. 在侧边栏输入您的SiliconFlow API密钥
                2. （可选）输入自定义的Base URL
                3. （可选）输入模型名称
                4. 点击"初始化大模型解释器"按钮
                
                **支持的模型：**
                - Qwen/Qwen2.5-7B-Instruct（默认）
                - Qwen/Qwen2.5-72B-Instruct
                - deepseek-ai/DeepSeek-V2.5
                
                **注意：** 如果未配置API，可以点击下方按钮使用规则解释。
                """)
                
                if st.button("使用规则解释（无需API）"):
                    self.llm_explainer = LLMExplainer()
                    self._save_state()
                    st.success("✅ 规则解释器已初始化！")
                    st.rerun()
            
            # 生成大模型解释
            if self.llm_explainer is not None:
                st.info(f"当前使用: **{self.llm_explainer.model}** 模型")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("生成大模型解释", type="primary"):
                        print("[APP] 用户点击了'生成大模型解释'按钮")
                        
                        with st.spinner("大模型正在生成解释，请稍候..."):
                            explanation = self.generate_llm_explanation()
                        
                        print(f"[APP] 获取到的解释: {explanation is not None}")
                        
                        if explanation:
                            st.markdown("#### 📊 AI生成的根因分析报告")
                            st.markdown(explanation)
                            
                            st.download_button(
                                label="下载报告",
                                data=explanation,
                                file_name="根因分析报告.md",
                                mime="text/markdown"
                            )
                        else:
                            st.error("生成解释失败，请检查API配置或查看终端日志")
                with col2:
                    if st.button("重新生成解释"):
                        self.llm_explanation = None
                        self._save_state()
                        st.success("✅ 已清除旧解释，请点击'生成大模型解释'")
                        st.rerun()
        else:
            st.info("👆 请先完成步骤3，推导因果图")
    
    def _generate_data_from_agent(self, causal_graph_result):
        """根据Agent推导的因果图生成数据并分析"""
        try:
            # 步骤1：生成数据并运行DoWhy分析
            with st.spinner("正在生成数据并运行DoWhy分析..."):
                self.data, self.anomaly_factors = create_demo_scenario()
                self.pipeline = RootCauseAnalysisPipeline(self.data)
                self.analysis_results = self.pipeline.run_full_analysis()
                self._save_state()
            
            st.success("✅ 数据生成和DoWhy分析完成！")
            
        except Exception as e:
            st.error(f"❌ 生成数据和分析失败: {str(e)}")
    

    
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
            <li>改进建议</li>
            <li>预期效果评估</li>
        </ul>
        <p><strong>操作步骤：</strong></p>
        <ol>
            <li>点击"运行DoWhy分析"按钮，获取因果分析结果</li>
            <li>查看分析结果</li>
            <li>点击"生成大模型解释"按钮，获取AI解释</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # 步骤1：运行DoWhy分析
        st.markdown("---")
        st.markdown("### 步骤1：运行DoWhy因果分析")
        
        if st.button("运行DoWhy分析", type="primary"):
            with st.spinner("正在生成数据并运行DoWhy分析..."):
                self.load_data()
                self.run_analysis()
            st.success("✅ DoWhy分析完成！")
        
        # 展示DoWhy分析结果
        if self.analysis_results is not None:
            st.markdown("#### 📊 DoWhy分析结果")
            
            with st.expander("查看指标对比分析", expanded=True):
                comparison_df = self.analysis_results['comparison']
                st.dataframe(comparison_df.style.format({
                    'normal_mean': '{:.3f}',
                    'anomaly_mean': '{:.3f}',
                    'change_percent': '{:.2f}%',
                    'abs_change': '{:.2f}%'
                }))
            
            with st.expander("查看因果效应分析"):
                causal_df = self.analysis_results['causal_analysis']
                valid_causal = causal_df[causal_df['causal_effect'].notna()]
                st.dataframe(valid_causal.style.format({
                    'causal_effect': '{:.4f}'
                }))
            
            with st.expander("查看分析总结"):
                st.markdown(self.analysis_results['summary'])
            
            with st.expander("查看反事实分析结果（预期改进效果）", expanded=True):
                if 'counterfactual_analysis' in self.analysis_results and self.analysis_results['counterfactual_analysis'] is not None:
                    cf_df = self.analysis_results['counterfactual_analysis']
                    valid_cf = cf_df[cf_df['expected_efficiency_gain'].notna()]
                    
                    st.markdown("**预期改进效果（基于DoWhy因果推断）：**")
                    
                    st.dataframe(valid_cf.style.format({
                        'causal_effect': '{:.4f}',
                        'improvement_level': '{:.0%}',
                        'expected_efficiency_gain': '{:.2%}'
                    }))
                    
                    st.markdown("**改进效果说明：**")
                    for _, row in valid_cf.iterrows():
                        st.info(row['interpretation'])
                else:
                    st.info("暂无反事实分析结果")
            
            # 步骤2：配置大模型
            st.markdown("---")
            st.markdown("### 步骤2：配置大模型")
            
            if self.llm_explainer is None:
                st.warning("⚠️ 请先在侧边栏配置SiliconFlow API密钥并初始化大模型解释器")
                st.info("""
                **配置步骤：**
                
                1. 在侧边栏输入您的SiliconFlow API密钥
                2. （可选）输入自定义的Base URL
                3. （可选）输入模型名称
                4. 点击"初始化大模型解释器"按钮
                
                **支持的模型：**
                - Qwen/Qwen2.5-7B-Instruct（默认）
                - Qwen/Qwen2.5-72B-Instruct
                - deepseek-ai/DeepSeek-V2.5
                
                **注意：** 如果未配置API，可以点击下方按钮使用规则解释。
                """)
                
                if st.button("使用规则解释（无需API）"):
                    self.llm_explainer = LLMExplainer()
                    self._save_state()
                    st.success("✅ 规则解释器已初始化！")
                    st.rerun()
            
            # 步骤3：生成大模型解释
            if self.llm_explainer is not None:
                st.markdown("---")
                st.markdown("### 步骤3：生成大模型解释")
                
                st.info(f"当前使用: **{self.llm_explainer.model}** 模型")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("生成大模型解释", type="primary"):
                        print("[APP] 用户点击了'生成大模型解释'按钮")
                        
                        with st.spinner("大模型正在生成解释，请稍候..."):
                            explanation = self.generate_llm_explanation()
                        
                        print(f"[APP] 获取到的解释: {explanation is not None}")
                        
                        if explanation:
                            st.markdown("#### 📊 AI生成的根因分析报告")
                            st.markdown(explanation)
                            
                            st.download_button(
                                label="下载报告",
                                data=explanation,
                                file_name="根因分析报告.md",
                                mime="text/markdown"
                            )
                        else:
                            st.error("生成解释失败，请检查API配置或查看终端日志")
                with col2:
                    if st.button("重新生成解释"):
                        self.llm_explanation = None
                        self._save_state()
                        st.success("✅ 已清除旧解释，请点击'生成大模型解释'")
                        st.rerun()
        else:
            st.info("👆 请先运行DoWhy分析获取分析结果")
    

    
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
        elif page == "AI智能解释":
            self.render_llm_explanation_page()
        elif page == "Agent分析":
            self.render_agent_analysis_page()


if __name__ == "__main__":
    app = RootCauseAnalysisWebApp()
    app.run()
