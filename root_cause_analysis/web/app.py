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
from causal_analyzer import CausalAnalyzer
from root_cause_analysis_pipeline import RootCauseAnalysisPipeline
from causal_graph_builder import CausalGraphBuilder
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
        if 'causal_graph' not in st.session_state:
            st.session_state.causal_graph = None
        if 'ontology_manager' not in st.session_state:
            st.session_state.ontology_manager = None
        if 'causal_graph_builder' not in st.session_state:
            st.session_state.causal_graph_builder = None
        
        self.data = st.session_state.data
        self.anomaly_factors = st.session_state.anomaly_factors
        self.analysis_results = st.session_state.analysis_results
        self.pipeline = st.session_state.pipeline
        self.llm_explainer = st.session_state.llm_explainer
        self.llm_explanation = st.session_state.llm_explanation
        self.llm_agent = st.session_state.llm_agent
        self.causal_graph_derived = st.session_state.causal_graph_derived
        self.agent_outcome_entity = st.session_state.agent_outcome_entity
        self.causal_graph = st.session_state.causal_graph
        self.ontology_manager = st.session_state.ontology_manager
        self.causal_graph_builder = st.session_state.causal_graph_builder
        
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
        st.session_state.causal_graph = self.causal_graph
        st.session_state.ontology_manager = self.ontology_manager
        st.session_state.causal_graph_builder = self.causal_graph_builder
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
    
    def init_ontology_manager(self):
        """
        初始化本体管理器 - 从ontology_api读取schema信息
        """
        if not self.ontology_manager:
            try:
                import httpx
                
                # 从ontology_api读取schema信息
                st.info("正在从ontology_api读取schema信息...")
                
                # 只读取schema端点，因为其他端点返回空数据
                schema_response = httpx.get("http://localhost:8000/schema", timeout=10.0)
                schema_response.raise_for_status()
                schema_data = schema_response.json()
                
                # 创建本体管理器实例
                from ontology_manager import OntologyManager
                self.ontology_manager = OntologyManager()
                
                # 设置schema数据
                self.ontology_manager.schema = schema_data
                
                # 创建因果图构建器
                self.causal_graph_builder = CausalGraphBuilder(self.ontology_manager)
                
                # 统计schema中的元素数量
                entity_types_count = len(schema_data.get('entity_types', []))
                relation_types_count = len(schema_data.get('relation_types', []))
                metric_definitions_count = len(schema_data.get('metric_definitions', []))
                
                st.success("✅ 本体管理器初始化成功！")
                st.success(f"📊 读取到 {entity_types_count} 个实体类型, {relation_types_count} 个关系类型, {metric_definitions_count} 个指标定义")
                
                # 保存状态
                self._save_state()
                
            except Exception as e:
                st.error(f"❌ 初始化本体管理器失败: {str(e)}")
                st.info("请确保ontology_api服务正在运行: python web/ontology_api.py")
        return self.ontology_manager
    
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
    
    def build_causal_graph(self, method: str = "llm") -> str:
        """
        构建因果图
        
        Args:
            method: 构建方法 (ontology, llm, default)
        """
        if method == "ontology" and self.causal_graph_builder:
            # 从本体构建因果图
            try:
                self.causal_graph = self.causal_graph_builder.build_from_ontology()
                st.success("✅ 从本体构建因果图成功！")
            except Exception as e:
                st.error(f"❌ 从本体构建因果图失败: {str(e)}")
                self.causal_graph = self.causal_graph_builder.get_default_causal_graph()
        elif method == "llm" and self.llm_agent and self.ontology_manager:
            # 使用大模型构建因果图
            try:
                ontology_schema = self.ontology_manager.schema
                self.causal_graph = self.causal_graph_builder.build_with_llm(ontology_schema, self.llm_agent)
                st.success("✅ 使用大模型构建因果图成功！")
            except Exception as e:
                st.error(f"❌ 使用大模型构建因果图失败: {str(e)}")
                self.causal_graph = self.causal_graph_builder.get_default_causal_graph()
        else:
            # 使用默认因果图
            if self.causal_graph_builder:
                self.causal_graph = self.causal_graph_builder.get_default_causal_graph()
            else:
                # 如果没有因果图构建器，使用硬编码的默认因果图
                self.causal_graph = """digraph {
                    payment_timeliness -> supplier_efficiency;
                    supplier_efficiency -> parts_availability;
                    parts_availability -> production_efficiency;
                    avg_employee_skill -> production_efficiency;
                    equipment_status -> production_efficiency;
                    capacity_utilization -> production_efficiency;
                    supplier_efficiency -> production_efficiency;
                    payment_timeliness -> production_efficiency;
                }"""
        
        self._save_state()
        return self.causal_graph
    
    def run_analysis(self, treatment: str = "payment_timeliness", outcome: str = "production_efficiency"):
        """运行分析"""
        if self.analysis_results is None:
            with st.spinner("运行根因分析..."):
                # 确保有因果图
                if not self.causal_graph:
                    self.build_causal_graph()
                
                # 初始化分析管道
                self.pipeline = RootCauseAnalysisPipeline(
                    data=self.data,
                    causal_graph=self.causal_graph
                )
                
                # 运行完整分析
                self.analysis_results = self.pipeline.run_full_analysis(
                    treatment=treatment,
                    outcome=outcome
                )
                
                # 在控制台打印分析结果
                print("[APP] 分析结果:")
                print(f"[APP] 因果效应: {self.analysis_results.get('causal_effect')}")
                print(f"[APP] 驳斥检验结果: {self.analysis_results.get('refutation_results')}")
                print(f"[APP] 反事实分析: {self.analysis_results.get('counterfactual_analysis')}")
                
                # 在web上展示分析结果
                st.success("✅ 分析完成！")
                
                # 显示因果效应
                causal_effect = self.analysis_results.get("causal_effect")
                if causal_effect is not None:
                    st.markdown(f"**因果效应值**: {causal_effect:.4f}")
                    
                    if causal_effect > 0:
                        st.success("正向因果效应：处理变量增加会提高结果变量")
                    else:
                        st.warning("负向因果效应：处理变量增加会降低结果变量")
                
                # 显示驳斥检验结果
                refutation_results = self.analysis_results.get("refutation_results")
                if refutation_results:
                    with st.expander("查看驳斥检验结果"):
                        for test_name, result in refutation_results.items():
                            st.markdown(f"**{test_name}**: {result}")
                
                # 显示反事实分析结果
                counterfactual_analysis = self.analysis_results.get("counterfactual_analysis")
                if counterfactual_analysis:
                    with st.expander("查看反事实分析结果"):
                        st.json(counterfactual_analysis)
            self._save_state()
        return self.analysis_results
    
    def init_llm_explainer(self, api_type: str, api_key: str, model: str = None, base_url: str = None):
        """初始化大模型解释器"""
        self.llm_explainer = LLMExplainer(api_type=api_type, api_key=api_key, model=model, base_url=base_url)
        self.llm_explanation = None
        self._save_state()
    
    def generate_llm_explanation(self):
        """
        生成大模型解释
        """
        print("[APP] generate_llm_explanation 被调用")
        print(f"  - llm_explainer: {self.llm_explainer is not None}")
        print(f"  - analysis_results: {self.analysis_results is not None}")
        print(f"  - llm_explanation: {self.llm_explanation is not None}")
        
        if self.llm_explanation is None and self.llm_explainer is not None:
            print("[APP] 开始生成解释...")
            
            if self.analysis_results is None:
                print("[APP] analysis_results 为空，先运行分析...")
                # 默认分析生产效率
                if not self.causal_graph:
                    st.warning("请先构建因果图并运行根因分析")
                    return None
                
                # 初始化分析管道
                self.pipeline = RootCauseAnalysisPipeline(
                    data=self.data,
                    causal_graph=self.causal_graph
                )
                
                # 运行根因分析
                try:
                    results_df = self.pipeline.run_root_cause_analysis("production_efficiency")
                    self.analysis_results = self.pipeline.analysis_results
                    self._save_state()
                except Exception as e:
                    st.error(f"❌ 运行分析失败: {str(e)}")
                    return None
            
            print(f"[APP] analysis_results 状态: {self.analysis_results is not None}")
            
            with st.spinner("大模型正在生成解释..."):
                print("[APP] 调用 llm_explainer.generate_explanation...")
                
                # 准备数据
                import pandas as pd
                
                # 创建comparison_df
                if "root_cause_analysis" in self.analysis_results:
                    # 从根因分析结果创建causal_results
                    root_cause_results = self.analysis_results["root_cause_analysis"]
                    causal_results = pd.DataFrame(root_cause_results)
                    
                    # 重命名列以匹配预期格式
                    if 'treatment' in causal_results.columns and 'cause' not in causal_results.columns:
                        causal_results = causal_results.rename(columns={'treatment': 'cause'})
                    
                    # 添加interpretation列（如果不存在）
                    if 'interpretation' not in causal_results.columns:
                        causal_results['interpretation'] = causal_results['cause'].apply(lambda x: f"{x}对生产效率有影响")
                    
                    # 按因果效应排序
                    causal_results = causal_results.sort_values('abs_causal_effect', ascending=False)
                else:
                    # 创建默认的causal_results
                    causal_results = pd.DataFrame({
                        'cause': ['avg_employee_skill', 'parts_availability', 'supplier_efficiency'],
                        'causal_effect': [0.70, 0.56, 0.35],
                        'interpretation': ['员工技能对生产效率有直接且显著的影响', '零部件供应不足直接影响生产线的正常运转', '供应商的生产效率直接影响零部件的交付']
                    })
                
                # 创建comparison_df
                comparison_df = pd.DataFrame({
                    'metric': ['production_efficiency', 'payment_timeliness', 'supplier_efficiency', 'parts_availability'],
                    'normal_mean': [0.85, 0.9, 0.88, 0.92],
                    'anomaly_mean': [0.65, 0.45, 0.68, 0.75],
                    'change_percent': [-0.235, -0.5, -0.227, -0.185],
                    'abs_change': [0.235, 0.5, 0.227, 0.185]
                })
                
                # 生成解释，传递完整的因果图和分析结果
                self.llm_explanation = self.llm_explainer.generate_explanation(
                    self.analysis_results,
                    comparison_df,
                    causal_results,
                    causal_graph=self.causal_graph  # 传递完整的因果图
                )
                self._save_state()
                print(f"[APP] 解释生成完成，长度: {len(self.llm_explanation) if self.llm_explanation else 0}")
        
        return self.llm_explanation
    
    def plot_causal_graph(self):
        """绘制因果图"""
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
        # 生成指标对比数据
        normal_data = self.data[self.data['month'] != 12]
        anomaly_data = self.data[self.data['month'] == 12]
        
        metrics = ['production_efficiency', 'payment_timeliness', 'supplier_efficiency', 
                   'parts_availability', 'avg_employee_skill', 'equipment_status', 'capacity_utilization']
        
        comparison_data = []
        for metric in metrics:
            normal_mean = normal_data[metric].mean()
            anomaly_mean = anomaly_data[metric].mean()
            change = (anomaly_mean - normal_mean) / normal_mean * 100
            
            comparison_data.append({
                'metric': metric,
                'normal_mean': normal_mean,
                'anomaly_mean': anomaly_mean,
                'change_percent': change,
                'abs_change': abs(change)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        metrics_df = comparison_df[comparison_df['metric'] != 'production_efficiency']
        
        fig = px.bar(
            metrics_df,
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
        
        return fig, comparison_df
    
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
            ["场景介绍", "因果图", "数据分析", "Agent分析"]
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
                if st.button("初始化因果解释器"):
                    print(f"[APP] 用户点击了'初始化因果解释器'按钮")
                    if api_key:
                        with st.spinner("正在初始化因果解释器..."):
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
                                    st.success("✅ 因果解释器初始化成功！")
                                    st.session_state.llm_agent_initialized = True
                                else:
                                    st.error("❌ 因果解释器初始化失败！")
                            except Exception as e:
                                print(f"[APP] 初始化LLM Agent时发生异常: {str(e)}")
                                st.error(f"❌ 因果解释器初始化失败: {str(e)}")
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
        
        st.sidebar.markdown("### 本体配置")
        with st.sidebar.expander("本体管理器"):
            if st.button("初始化本体管理器"):
                self.init_ontology_manager()
            
            if st.button("构建因果图"):
                if not self.causal_graph_builder:
                    self.init_ontology_manager()
                self.build_causal_graph()
        
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
        
        tab1, tab2, tab3 = st.tabs(["效率趋势", "指标对比", "相关性分析"])
        
        with tab1:
            fig = self.plot_efficiency_trend()
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig, comparison_df = self.plot_metrics_comparison()
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
        
        # 构建因果图
        if not self.causal_graph:
            self.build_causal_graph()
        
        # 运行分析
        if not self.analysis_results:
            self.run_analysis()
        
        st.markdown("### 分析结果")
        
        # 显示因果效应
        causal_effect = self.analysis_results.get("causal_effect")
        if causal_effect is not None:
            st.markdown(f"**因果效应值**: {causal_effect:.4f}")
            
            if causal_effect > 0:
                st.success("正向因果效应：处理变量增加会提高结果变量")
            else:
                st.warning("负向因果效应：处理变量增加会降低结果变量")
        
        # 显示驳斥检验结果
        refutation_results = self.analysis_results.get("refutation_results")
        if refutation_results:
            with st.expander("查看驳斥检验结果"):
                for test_name, result in refutation_results.items():
                    st.markdown(f"**{test_name}**: {result}")
        
        # 显示反事实分析结果
        counterfactual_analysis = self.analysis_results.get("counterfactual_analysis")
        if counterfactual_analysis:
            with st.expander("查看反事实分析结果"):
                st.json(counterfactual_analysis)
    
    def render_agent_analysis_page(self):
        """
        渲染Agent分析页面
        """
        st.header("🤖 Agent智能分析")
        
        st.markdown("""
        <div class="llm-box">
        <h4>Agent驱动的因果分析</h4>
        <p>通过LLM理解本体并推导因果图，实现智能的根因分析流程。</p>
        <p><strong>操作步骤：</strong></p>
        <ol>
            <li>初始化本体管理器（读取并展示本体信息）</li>
            <li>构建因果图（基于本体信息）</li>
            <li>配置分析参数</li>
            <li>运行完整分析</li>
            <li>查看分析结果</li>
            <li>生成智能解释</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # 步骤1：初始化本体管理器
        st.markdown("---")
        st.markdown("### 步骤1：初始化本体管理器")
        
        if st.button("初始化本体管理器", type="primary"):
            self.init_ontology_manager()
        
        # 显示本体信息图形化展示
        if self.ontology_manager:
            st.markdown("#### 📊 本体信息展示")
            
            # 显示Schema信息
            if hasattr(self.ontology_manager, 'schema') and self.ontology_manager.schema:
                schema = self.ontology_manager.schema
                
                # 绘制本体图
                st.markdown("##### 🎯 本体图形化展示")
                
                try:
                    import networkx as nx
                    import plotly.graph_objects as go
                    
                    # 创建有向图
                    G = nx.DiGraph()
                    
                    # 从schema添加实体类型节点
                    entity_types = schema.get('entity_types', [])
                    relation_types = schema.get('relation_types', [])
                    metric_definitions = schema.get('metric_definitions', [])
                    
                    # 添加节点
                    entity_map = {}
                    for i, entity_type in enumerate(entity_types):
                        entity_id = entity_type.get('id', entity_type.get('name', f'entity_{i}'))
                        entity_name = entity_type.get('name', entity_id)
                        entity_map[entity_id] = entity_name
                        G.add_node(entity_id, type='entity', name=entity_name)
                    
                    # 添加指标定义节点
                    metric_map = {}
                    for i, metric in enumerate(metric_definitions):
                        metric_id = metric.get('id', metric.get('name', f'metric_{i}'))
                        metric_name = metric.get('name', metric_id)
                        metric_map[metric_id] = metric_name
                        G.add_node(metric_id, type='metric', name=metric_name)
                    
                    # 添加关系类型边
                    for i, relation_type in enumerate(relation_types):
                        relation_name = relation_type.get('name', f'relation_{i}')
                        source_types = relation_type.get('source_types', [])
                        target_types = relation_type.get('target_types', [])
                        
                        # 为每种源类型和目标类型的组合添加边
                        for source_type in source_types:
                            for target_type in target_types:
                                if source_type in G.nodes and target_type in G.nodes:
                                    G.add_edge(source_type, target_type, label=relation_name)
                    
                    # 添加指标与实体的关系边
                    for metric in metric_definitions:
                        metric_id = metric.get('id', metric.get('name'))
                        source_entity = metric.get('source_entity_type')
                        
                        # 连接指标与相关实体
                        if metric_id in G.nodes and source_entity and source_entity in G.nodes:
                            G.add_edge(source_entity, metric_id, label="has_metric")
                    
                    # 分离实体和指标节点
                    entity_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') == 'entity']
                    metric_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') == 'metric']
                    other_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') not in ['entity', 'metric']]
                    
                    # 使用更智能的布局算法
                    if len(G.nodes) > 0:
                        print(f"[DEBUG] 节点数量: {len(G.nodes)}")
                        print(f"[DEBUG] 实体节点: {len(entity_nodes)}")
                        print(f"[DEBUG] 指标节点: {len(metric_nodes)}")
                        print(f"[DEBUG] 其他节点: {len(other_nodes)}")
                        # 直接使用spring_layout，调整参数避免节点重叠
                        print("[DEBUG] 使用 spring_layout")
                        # 增加k值以增大节点间距，增加迭代次数以提高布局质量
                        pos = nx.spring_layout(G, k=1.0, iterations=300, seed=42)
                        # 打印布局结果
                        print(f"[DEBUG] 布局完成，节点位置数量: {len(pos)}")
                    else:
                        pos = {}
                    
                    # 创建边轨迹
                    edge_x = []
                    edge_y = []
                    edge_hover_text = []
                    
                    # 添加边标签
                    edge_annotations = []
                    
                    for edge in G.edges(data=True):
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                        
                        label = edge[2].get('label', 'relation')
                        edge_hover_text.append(label)
                        
                        # 添加边标签，确保它们正确显示
                        x_mid = (x0 + x1) / 2
                        y_mid = (y0 + y1) / 2
                        
                        # 计算标签位置的偏移，避免与边重叠
                        dx = x1 - x0
                        dy = y1 - y0
                        length = (dx**2 + dy**2)**0.5
                        if length > 0:
                            # 垂直于边的方向偏移
                            offset_x = -dy / length * 0.05
                            offset_y = dx / length * 0.05
                        else:
                            offset_x = offset_y = 0
                        
                        edge_annotations.append(dict(
                            x=x_mid + offset_x,
                            y=y_mid + offset_y,
                            xref="x",
                            yref="y",
                            text=label,
                            showarrow=False,
                            font=dict(size=10, color="#333", weight="bold"),
                            bgcolor="rgba(255, 255, 255, 0.9)",
                            bordercolor="rgba(0, 0, 0, 0.3)",
                            borderwidth=1,
                            borderpad=5
                        ))
                    
                    # 创建边轨迹
                    edge_trace = go.Scatter(
                        x=edge_x, y=edge_y,
                        line=dict(width=1.5, color='#888888'),
                        hoverinfo='text',
                        mode='lines'
                    )
                    edge_trace.text = edge_hover_text
                    
                    # 创建箭头标记
                    arrow_x = []
                    arrow_y = []
                    arrow_angles = []
                    
                    import math
                    
                    for edge in G.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        
                        # 计算箭头位置（在边的末端）
                        arrow_x.append(x1)
                        arrow_y.append(y1)
                        
                        # 计算箭头角度
                        angle = 180 + (180 / math.pi) * math.atan2(y1 - y0, x1 - x0)
                        arrow_angles.append(angle)
                    
                    # 创建箭头轨迹
                    arrow_trace = go.Scatter(
                        x=arrow_x,
                        y=arrow_y,
                        mode='markers',
                        marker=dict(
                            symbol='arrow',
                            size=10,
                            color='#666',
                            angleref='previous',
                            angle=[angle for angle in arrow_angles]
                        ),
                        hoverinfo='none'
                    )
                    
                    # 创建实体节点轨迹
                    entity_x = []
                    entity_y = []
                    entity_texts = []
                    for node in entity_nodes:
                        x, y = pos[node]
                        entity_x.append(x)
                        entity_y.append(y)
                        entity_texts.append(G.nodes[node].get('name', node))
                    
                    entity_trace = go.Scatter(
                        x=entity_x,
                        y=entity_y,
                        mode='markers+text',
                        text=entity_texts,
                        textposition="middle center",
                        textfont=dict(color="#000000"),  # 文本颜色为黑色
                        marker=dict(
                            showscale=False,
                            color='#6495ED',  # 实体类型用蓝色
                            size=35,  # 实体类型节点大小
                            line_width=2,
                            symbol='circle'  # 实体类型用圆形
                        ),
                        hoverinfo='text',
                        name='实体类型 (蓝色圆形)'
                    )
                    
                    # 创建指标节点轨迹
                    metric_x = []
                    metric_y = []
                    metric_texts = []
                    for node in metric_nodes:
                        x, y = pos[node]
                        metric_x.append(x)
                        metric_y.append(y)
                        metric_texts.append(G.nodes[node].get('name', node))
                    
                    metric_trace = go.Scatter(
                        x=metric_x,
                        y=metric_y,
                        mode='markers+text',
                        text=metric_texts,
                        textposition="middle center",
                        textfont=dict(color="#000000"),  # 文本颜色为黑色
                        marker=dict(
                            showscale=False,
                            color='#DC143C',  # 指标定义用红色
                            size=30,  # 指标定义节点大小
                            line_width=2,
                            symbol='square'  # 指标定义用正方形
                        ),
                        hoverinfo='text',
                        name='指标定义 (红色正方形)'
                    )
                    
                    # 创建其他节点轨迹
                    other_x = []
                    other_y = []
                    other_texts = []
                    for node in other_nodes:
                        x, y = pos[node]
                        other_x.append(x)
                        other_y.append(y)
                        other_texts.append(G.nodes[node].get('name', node))
                    
                    other_trace = go.Scatter(
                        x=other_x,
                        y=other_y,
                        mode='markers+text',
                        text=other_texts,
                        textposition="middle center",
                        textfont=dict(color="#000000"),  # 文本颜色为黑色
                        marker=dict(
                            showscale=False,
                            color='#666666',
                            size=25,
                            line_width=2,
                            symbol='circle'
                        ),
                        hoverinfo='text',
                        name='其他节点'
                    )
                    
                    # 创建图表
                    data = [edge_trace, arrow_trace]
                    if entity_nodes:
                        data.append(entity_trace)
                    if metric_nodes:
                        data.append(metric_trace)
                    if other_nodes:
                        data.append(other_trace)
                    
                    fig = go.Figure(data=data,
                                   layout=go.Layout(
                                       title=dict(text='本体关系与指标图', font=dict(size=16, weight='bold')),
                                       showlegend=True,
                                       hovermode='closest',
                                       margin=dict(b=40, l=40, r=40, t=80),
                                       height=800,  # 增加画布高度
                                       annotations=edge_annotations,
                                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                       legend=dict(
                                           x=0.01,
                                           y=0.99,
                                           bgcolor="rgba(255, 255, 255, 0.8)",
                                           bordercolor="rgba(0, 0, 0, 0.5)",
                                           borderwidth=1,
                                           traceorder="normal",
                                           font=dict(
                                               family="sans-serif",
                                               size=12,
                                               color="#000"
                                           )
                                       )
                                   ))
                    
                    # 显示图表
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ 绘制本体图失败: {str(e)}")
                    
                # 显示详细信息
                st.markdown("##### 📋 Schema详细信息")
                
                # 实体类型详情
                if entity_types:
                    st.info(f"共 {len(entity_types)} 个实体类型")
                    
                    with st.expander("查看实体类型详情"):
                        for entity_type in entity_types:
                            st.markdown(f"**{entity_type.get('name', 'Unknown')}** ({entity_type.get('id', 'Unknown')})")
                            st.markdown(f"- 描述: {entity_type.get('description', '无')}")
                            attributes = entity_type.get('attributes', [])
                            if attributes:
                                st.markdown("- 属性:")
                                for attr in attributes:
                                    st.markdown(f"  - {attr.get('name')} ({attr.get('type')}): {attr.get('description')}")
                            st.markdown("")
                
                # 关系类型详情
                if relation_types:
                    st.info(f"共 {len(relation_types)} 个关系类型")
                    
                    with st.expander("查看关系类型详情"):
                        for relation_type in relation_types:
                            st.markdown(f"**{relation_type.get('name', 'Unknown')}** ({relation_type.get('id', 'Unknown')})")
                            st.markdown(f"- 描述: {relation_type.get('description', '无')}")
                            source_types = relation_type.get('source_types', [])
                            target_types = relation_type.get('target_types', [])
                            st.markdown(f"- 源类型: {', '.join(source_types)}")
                            st.markdown(f"- 目标类型: {', '.join(target_types)}")
                            st.markdown("")
                
                # 指标定义详情
                if metric_definitions:
                    st.info(f"共 {len(metric_definitions)} 个指标定义")
                    
                    with st.expander("查看指标定义详情"):
                        for metric in metric_definitions:
                            st.markdown(f"**{metric.get('name', 'Unknown')}** ({metric.get('id', 'Unknown')})")
                            st.markdown(f"- 描述: {metric.get('description', '无')}")
                            st.markdown(f"- 源实体类型: {metric.get('source_entity_type', '无')}")
                            st.markdown(f"- 目标实体类型: {metric.get('target_entity_type', '无')}")
                            st.markdown(f"- 源关系: {metric.get('source_relation', '无')}")
                            st.markdown(f"- 类型: {metric.get('type', '无')}")
                            st.markdown("")
            
            # 显示因果图构建提示
            st.success("✅ 本体信息已缓存，可用于下一步构建因果图")
            st.info("这些本体信息将作为因果图构建的输入，帮助系统理解领域知识结构")
        
        # 步骤2：构建因果图
        st.markdown("---")
        st.markdown("### 步骤2：构建因果图")
        
        if self.causal_graph_builder:
            col1, col2 = st.columns([2, 1])
            with col1:
                if st.button("使用大模型构建因果图", type="primary"):
                    if self.llm_agent:
                        self.build_causal_graph(method="llm")
                    else:
                        st.warning("⚠️ 请先初始化LLM Agent")
            
            # 显示因果图可视化
            if self.causal_graph:
                st.markdown("#### 🎯 因果图可视化")
                
                try:
                    import networkx as nx
                    import plotly.graph_objects as go
                    
                    # 解析因果图字符串
                    def parse_causal_graph(graph_str):
                        G = nx.DiGraph()
                        # 简单解析digraph格式
                        lines = graph_str.strip().split('\n')
                        for line in lines:
                            line = line.strip()
                            if '->' in line:
                                parts = line.split('->')
                                if len(parts) == 2:
                                    source = parts[0].strip()
                                    target = parts[1].strip().rstrip(';').strip()
                                    G.add_edge(source, target)
                        return G
                    
                    # 解析因果图
                    G = parse_causal_graph(self.causal_graph)
                    
                    # 生成布局
                    if len(G.nodes) > 0:
                        try:
                            pos = nx.kamada_kawai_layout(G)
                        except:
                            pos = nx.spring_layout(G, k=0.8, iterations=200)
                    else:
                        pos = {}
                    
                    # 创建边轨迹
                    edge_x = []
                    edge_y = []
                    
                    for edge in G.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                    
                    edge_trace = go.Scatter(
                        x=edge_x, y=edge_y,
                        line=dict(width=1.5, color='#666'),
                        hoverinfo='none',
                        mode='lines'
                    )
                    
                    # 创建箭头标记
                    arrow_x = []
                    arrow_y = []
                    arrow_angles = []
                    
                    import math
                    
                    for edge in G.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        arrow_x.append(x1)
                        arrow_y.append(y1)
                        angle = 180 + (180 / math.pi) * math.atan2(y1 - y0, x1 - x0)
                        arrow_angles.append(angle)
                    
                    arrow_trace = go.Scatter(
                        x=arrow_x,
                        y=arrow_y,
                        mode='markers',
                        marker=dict(
                            symbol='arrow',
                            size=8,
                            color='#666',
                            angleref='previous',
                            angle=[angle for angle in arrow_angles]
                        ),
                        hoverinfo='none'
                    )
                    
                    # 创建节点轨迹
                    node_x = []
                    node_y = []
                    node_texts = []
                    
                    for node in G.nodes():
                        x, y = pos[node]
                        node_x.append(x)
                        node_y.append(y)
                        node_texts.append(node)
                    
                    node_trace = go.Scatter(
                        x=node_x,
                        y=node_y,
                        mode='markers+text',
                        text=node_texts,
                        textposition="top center",
                        marker=dict(
                            showscale=False,
                            color='#2E86AB',
                            size=25,
                            line_width=2
                        ),
                        hoverinfo='text'
                    )
                    
                    # 创建图表
                    fig = go.Figure(data=[edge_trace, arrow_trace, node_trace],
                                   layout=go.Layout(
                                       title=dict(text='因果图可视化', font=dict(size=16)),
                                       showlegend=False,
                                       hovermode='closest',
                                       margin=dict(b=20, l=5, r=5, t=40),
                                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                                   ))
                    
                    # 显示图表
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ 绘制因果图失败: {str(e)}")
            
            if self.causal_graph:
                st.markdown("#### 因果图结果")
                st.code(self.causal_graph, language="python")
                
                # 人工修正因果图
                st.markdown("#### 人工修正因果图")
                edited_causal_graph = st.text_area(
                    "编辑因果图（DOT格式）",
                    value=self.causal_graph,
                    height=200,
                    help="可以直接编辑因果图，格式为DOT语言，例如：digraph G { A -> B; B -> C; }"
                )
                
                if st.button("应用修改"):
                    if edited_causal_graph != self.causal_graph:
                        self.causal_graph = edited_causal_graph
                        self._save_state()
                        st.success("✅ 因果图已更新")
                        # 重新渲染页面以显示更新后的因果图
                        st.experimental_rerun()
        else:
            st.warning("请先初始化本体管理器")
        
        # 步骤3：配置分析参数
        st.markdown("---")
        st.markdown("### 步骤3：配置分析参数")
        
        outcome = st.selectbox(
            "选择结果变量",
            options=["production_efficiency", "supplier_efficiency", "parts_availability"],
            format_func=lambda x: {
                "production_efficiency": "生产效率",
                "supplier_efficiency": "供应商效率",
                "parts_availability": "零部件可用性"
            }[x]
        )
        
        # 步骤4：运行根因分析
        st.markdown("---")
        st.markdown("### 步骤4：运行根因分析")
        
        if st.button("自动分析所有根因", type="primary"):
            if not self.causal_graph:
                st.warning("请先构建因果图")
            else:
                with st.spinner("正在分析根因..."):
                    try:
                        # 初始化分析管道
                        self.pipeline = RootCauseAnalysisPipeline(
                            data=self.data,
                            causal_graph=self.causal_graph
                        )
                        
                        # 运行根因分析
                        results_df = self.pipeline.run_root_cause_analysis(outcome)
                        
                        # 保存分析结果
                        self.analysis_results = self.pipeline.analysis_results
                        self._save_state()
                        
                        st.success("✅ 根因分析完成！")
                    except Exception as e:
                        st.error(f"❌ 根因分析失败: {str(e)}")
        
        # 步骤5：查看分析结果
        st.markdown("---")
        st.markdown("### 步骤5：查看分析结果")
        
        if self.analysis_results:
            # 检查是否有根因分析结果
            if "root_cause_analysis" in self.analysis_results:
                st.markdown("#### 根因分析结果")
                
                # 显示根因分析表格
                root_cause_results = self.analysis_results["root_cause_analysis"]
                results_df = pd.DataFrame(root_cause_results)
                
                # 格式化显示
                display_df = results_df[["rank", "treatment", "causal_effect", "abs_causal_effect"]].copy()
                display_df.columns = ["排名", "处理变量", "因果效应", "绝对效应值"]
                display_df["因果效应"] = display_df["因果效应"].map(lambda x: f"{x:.4f}" if x is not None else "N/A")
                display_df["绝对效应值"] = display_df["绝对效应值"].map(lambda x: f"{x:.4f}" if x is not None else "N/A")
                
                st.dataframe(display_df, use_container_width=True)
                
                # 显示处理变量和结果变量信息
                st.markdown(f"**分析变量**: {', '.join(self.analysis_results.get('treatments', []))}")
                st.markdown(f"**结果变量**: {self.analysis_results.get('outcome', 'N/A')}")
            
            # 显示传统分析结果（如果存在）
            if "causal_effect" in self.analysis_results:
                st.markdown("#### 传统分析结果")
                
                # 显示因果效应
                causal_effect = self.analysis_results.get("causal_effect")
                if causal_effect is not None:
                    st.markdown(f"**因果效应值**: {causal_effect:.4f}")
                    
                    if causal_effect > 0:
                        st.success("正向因果效应：处理变量增加会提高结果变量")
                    else:
                        st.warning("负向因果效应：处理变量增加会降低结果变量")
            
            # 显示驳斥检验结果
            refutation_results = self.analysis_results.get("refutation_results")
            if refutation_results:
                with st.expander("查看驳斥检验结果"):
                    for test_name, result in refutation_results.items():
                        st.markdown(f"**{test_name}**: {result}")
        else:
            st.info("请先运行分析")
        
        # 步骤6：生成智能解释
        st.markdown("---")
        st.markdown("### 步骤6：生成智能解释")
        
        if self.llm_explainer:
            if st.button("生成智能解释", type="primary"):
                explanation = self.generate_llm_explanation()
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
            st.warning("请先初始化大模型解释器")
    
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
            <li>加载数据</li>
            <li>运行DoWhy分析</li>
            <li>生成大模型解释</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # 步骤1：加载数据
        st.markdown("---")
        st.markdown("### 步骤1：加载数据")
        
        if st.button("加载数据"):
            self.load_data()
            st.success("✅ 数据加载完成！")
        
        # 步骤2：运行DoWhy分析
        st.markdown("---")
        st.markdown("### 步骤2：运行DoWhy分析")
        
        if st.button("运行DoWhy分析", type="primary"):
            with st.spinner("正在运行DoWhy分析..."):
                self.run_analysis()
            st.success("✅ DoWhy分析完成！")
        
        # 展示DoWhy分析结果
        if self.analysis_results:
            st.markdown("#### 📊 DoWhy分析结果")
            
            # 显示因果效应
            causal_effect = self.analysis_results.get("causal_effect")
            if causal_effect is not None:
                st.markdown(f"**因果效应值**: {causal_effect:.4f}")
                
                if causal_effect > 0:
                    st.success("正向因果效应：处理变量增加会提高结果变量")
                else:
                    st.warning("负向因果效应：处理变量增加会降低结果变量")
            
            # 显示驳斥检验结果
            refutation_results = self.analysis_results.get("refutation_results")
            if refutation_results:
                with st.expander("查看驳斥检验结果"):
                    for test_name, result in refutation_results.items():
                        st.markdown(f"**{test_name}**: {result}")
        
        # 步骤3：生成大模型解释
        st.markdown("---")
        st.markdown("### 步骤3：生成大模型解释")
        
        if self.llm_explainer:
            if st.button("生成大模型解释", type="primary"):
                explanation = self.generate_llm_explanation()
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
            st.warning("请先在侧边栏配置SiliconFlow API密钥并初始化大模型解释器")
            st.info("""
            **配置步骤：**
            
            1. 在侧边栏输入您的SiliconFlow API密钥
            2. （可选）输入自定义的Base URL
            3. （可选）输入模型名称
            4. 点击"初始化大模型解释器"按钮
            """)


if __name__ == "__main__":
    app = RootCauseAnalysisWebApp()
    page = app.render_sidebar()
    
    if page == "场景介绍":
        app.render_scenario_page()
    elif page == "因果图":
        app.render_causal_graph_page()
    elif page == "数据分析":
        app.render_data_analysis_page()
    elif page == "Agent分析":
        app.render_agent_analysis_page()
