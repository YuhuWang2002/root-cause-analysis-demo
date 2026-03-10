"""
部件A库存高因果根因分析 - Web应用（重构版）

根据refactor.md要求重构：
- 只保留场景介绍和根因分析两个页面
- 根因分析页面展示8步流程
- 每步都有具体的展示内容
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
from ontology_api import OntologyAPI

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
    .step-header {
        background-color: #2E86AB;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 20px 0 10px 0;
    }
    .step-content {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #2E86AB;
        margin-bottom: 20px;
    }
    .info-box {
        background-color: #e8f4f8;
        border-left: 4px solid #2E86AB;
        padding: 15px;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28A745;
        padding: 15px;
        margin-bottom: 20px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #FFC107;
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
        if 'root_cause_explanation' not in st.session_state:
            st.session_state.root_cause_explanation = None
        if 'solution' not in st.session_state:
            st.session_state.solution = None
        
        self.actual_data = st.session_state.actual_data
        self.counterfactual_data = st.session_state.counterfactual_data
        self.analysis_results = st.session_state.analysis_results
        self.llm_explainer = st.session_state.llm_explainer
        self.root_cause_explanation = st.session_state.root_cause_explanation
        self.solution = st.session_state.solution
    
    def load_data(self):
        """加载数据"""
        if self.actual_data is None:
            with st.spinner("生成数据..."):
                self.actual_data, self.counterfactual_data = create_inventory_scenario()
                st.session_state.actual_data = self.actual_data
                st.session_state.counterfactual_data = self.counterfactual_data
                st.success(f"✅ 已生成 {len(self.actual_data)} 条数据记录")
        
        return self.actual_data, self.counterfactual_data
    
    def run_analysis(self, fast_mode: bool = False):
        """运行因果分析
        
        Args:
            fast_mode: 快速模式（跳过驳斥检验和多变量分析）
        """
        if self.analysis_results is None:
            with st.spinner("运行因果分析..." + ("（快速模式）" if fast_mode else "")):
                analyzer = InventoryCausalAnalyzer(data=self.actual_data)
                self.analysis_results = analyzer.run_full_analysis(
                    self.counterfactual_data,
                    fast_mode=fast_mode
                )
                st.session_state.analysis_results = self.analysis_results
                st.success("✅ 因果分析完成！" + ("（快速模式）" if fast_mode else ""))
        
        return self.analysis_results
    
    def init_llm_explainer(self, api_key: str, model: str = None, base_url: str = None):
        """初始化大模型解释器"""
        self.llm_explainer = LLMExplainer(api_key=api_key, model=model, base_url=base_url)
        self.root_cause_explanation = None
        self.solution = None
        st.session_state.llm_explainer = self.llm_explainer
        st.session_state.root_cause_explanation = None
        st.session_state.solution = None
    
    def generate_root_cause_explanation(self):
        """生成根因解释（6.2步骤）"""
        if self.root_cause_explanation is None and self.llm_explainer is not None:
            if self.analysis_results is None:
                st.warning("请先运行因果分析")
                return None
            
            with st.spinner("大模型正在生成根因解释..."):
                self.root_cause_explanation = self.llm_explainer.generate_root_cause_explanation(
                    self.analysis_results,
                    self.actual_data,
                    self.counterfactual_data
                )
                st.session_state.root_cause_explanation = self.root_cause_explanation
        
        return self.root_cause_explanation
    
    def generate_solution(self):
        """生成解决方案（6.3步骤）"""
        if self.solution is None and self.llm_explainer is not None:
            if self.analysis_results is None:
                st.warning("请先运行因果分析")
                return None
            
            with st.spinner("大模型正在生成解决方案..."):
                self.solution = self.llm_explainer.generate_solution(
                    self.analysis_results,
                    self.actual_data,
                    self.counterfactual_data
                )
                st.session_state.solution = self.solution
        
        return self.solution
    
    def render_sidebar(self):
        """渲染侧边栏"""
        st.sidebar.title("🔍 库存根因分析")
        st.sidebar.markdown("### 分析导航")
        
        page = st.sidebar.radio(
            "选择页面",
            ["场景介绍", "根因分析"]
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
        
        return page
    
    def render_scenario_page(self):
        """渲染场景介绍页面"""
        st.header("场景介绍")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="step-header">
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
            st.markdown(f"- 昆仑2280平均销量: {actual_data['kunlun_2280_sales'].mean():.0f}")
            st.markdown(f"- 2288HV7平均销量: {actual_data['server_2288hv7_sales'].mean():.0f}")
            st.markdown(f"- PAC900S12-B2平均库存: {actual_data['pac900s12_b2_inventory'].mean():.0f}")
            
            if st.button("开始分析", key="start_analysis"):
                self.run_analysis()
                st.success("分析完成！请在根因分析页面查看结果")
    
    def render_analysis_page(self):
        """渲染根因分析页面"""
        st.header("根因分析")
        
        st.markdown("""
        <div class="info-box">
        <h4>📊 数据分析流程</h4>
        <p>本页面展示完整的根因分析流程，包括数据获取、本体展示、因果分析和解决方案。</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📋 完整数据分析流程")
        
        st.markdown("""
        <div class="step-content">
        <table style="width: 100%; border-collapse: collapse;">
        <tr style="background-color: #2E86AB; color: white;">
            <th style="padding: 10px; text-align: left; width: 5%;">步骤</th>
            <th style="padding: 10px; text-align: left; width: 45%;">英文问题</th>
            <th style="padding: 10px; text-align: left; width: 50%;">中文问题</th>
        </tr>
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px;"><strong>1</strong></td>
            <td style="padding: 10px;">What do the users need to do?</td>
            <td style="padding: 10px;">用户需要做什么</td>
        </tr>
        <tr>
            <td style="padding: 10px;"><strong>2</strong></td>
            <td style="padding: 10px;">Where does the needed data come from?</td>
            <td style="padding: 10px;">需要的数据来自哪里</td>
        </tr>
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px;"><strong>3</strong></td>
            <td style="padding: 10px;">How are users meant to interact with the data?</td>
            <td style="padding: 10px;">用户如何与数据信息交互</td>
        </tr>
        <tr>
            <td style="padding: 10px;"><strong>4</strong></td>
            <td style="padding: 10px;">What structured data asset needs to be provided to users?</td>
            <td style="padding: 10px;">需要向用户提供什么样的结构化数据资产</td>
        </tr>
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px;"><strong>5</strong></td>
            <td style="padding: 10px;">What constrain should applied to control the data quality?</td>
            <td style="padding: 10px;">应对施加哪些约束来控制数据质量</td>
        </tr>
        <tr>
            <td style="padding: 10px;"><strong>6</strong></td>
            <td style="padding: 10px;">How should the data asset be leveraged?</td>
            <td style="padding: 10px;">数据资产应该如何被利用</td>
        </tr>
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px;"><strong>7</strong></td>
            <td style="padding: 10px;">Describe any automations necessary for users to fulfill their tasks?</td>
            <td style="padding: 10px;">用户完成其任务所需的自动化措施</td>
        </tr>
        <tr>
            <td style="padding: 10px;"><strong>8</strong></td>
            <td style="padding: 10px;">Define roles and permissions?</td>
            <td style="padding: 10px;">定义角色和权限</td>
        </tr>
        </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        self.load_data()
        
        st.markdown("---")
        
        self._render_step1()
        self._render_step2()
        self._render_step3()
        self._render_step4()
        self._render_step5()
        self._render_step6()
        self._render_step7()
        self._render_step8()
    
    def _render_step1(self):
        """步骤1：What do the users need to do?"""
        st.markdown("""
        <div class="step-header">
            步骤1：What do the users need to do? / 用户需要做什么
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-content">
        <p><strong>用户需要了解当前各库存的情况，在库存出现异常的情况下，找到根本原因。</strong></p>
        <ul>
            <li>监控和了解当前各库存的实时情况</li>
            <li>识别库存异常（如库存过高或过低）</li>
            <li>分析库存异常的根本原因</li>
            <li>提供决策支持和改进建议</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_step2(self):
        """步骤2：Where does the needed data come from?"""
        st.markdown("""
        <div class="step-header">
            步骤2：Where does the needed data come from? / 需要的数据来自哪里
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-content">
        <p><strong>用户需要从数据库中获取库存数据和相关指标数据。本次演示使用的是模拟数据。</strong></p>
        <ul>
            <li>数据来源：企业ERP系统、库存管理系统</li>
            <li>数据类型：产品销量、部件消耗、库存水平</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if 'step2_data_loaded' not in st.session_state:
            st.session_state.step2_data_loaded = False
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📖 读取数据", key="load_data_step2"):
                self.load_data()
                st.session_state.step2_data_loaded = True
                st.success("✅ 数据读取成功！")
        
        if st.session_state.step2_data_loaded and self.actual_data is not None:
            st.markdown("---")
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"📊 **时间范围**: {self.actual_data['date'].min().strftime('%Y-%m-%d')} 至 {self.actual_data['date'].max().strftime('%Y-%m-%d')}")
            with col_info2:
                st.info(f"📈 **数据量**: {len(self.actual_data)} 条记录")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**数据样本（前5行）**:")
                st.dataframe(self.actual_data.head())
            with col2:
                st.markdown("**数据统计**:")
                st.dataframe(self.actual_data.describe())
    
    def _render_step3(self):
        """步骤3：How are users meant to interact with the data?"""
        st.markdown("""
        <div class="step-header">
            步骤3：How are users meant to interact with the data? / 用户如何与数据信息交互
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-content">
        <p><strong>本次不演示</strong></p>
        <p>在实际应用中，用户可以通过以下方式与数据交互：</p>
        <ul>
            <li>数据筛选：按时间、产品类型筛选数据</li>
            <li>数据可视化：查看趋势图、对比图</li>
            <li>参数调整：调整分析参数</li>
            <li>结果导出：导出分析报告</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_step4(self):
        """步骤4：What structured data asset needs to be provided to users?"""
        st.markdown("""
        <div class="step-header">
            步骤4：What structured data asset needs to be provided to users? / 需要向用户提供什么样的结构化数据资产
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-content">
        <p><strong>向用户展示本体图，展示产品与部件的关系。</strong></p>
        <p>本体信息包含：实体（产品、部件）、关系（使用关系）、规则（约束条件）</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 初始化会话状态
        if 'step4_ontology_loaded' not in st.session_state:
            st.session_state.step4_ontology_loaded = False
        if 'ontology_data' not in st.session_state:
            st.session_state.ontology_data = None
        if 'selected_nodes' not in st.session_state:
            st.session_state.selected_nodes = []
        if 'selected_edges' not in st.session_state:
            st.session_state.selected_edges = []
        if 'selected_source' not in st.session_state:
            st.session_state.selected_source = None
        if 'node_click_processed' not in st.session_state:
            st.session_state.node_click_processed = False
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔗 读取本体信息", key="load_ontology_step4"):
                st.session_state.ontology_data = OntologyAPI.get_ontology_graph_data()
                st.session_state.step4_ontology_loaded = True
                st.success("✅ 本体信息读取成功！")
        
        if st.session_state.step4_ontology_loaded and st.session_state.ontology_data:
            st.markdown("---")
            
            ontology_data = st.session_state.ontology_data
            
            st.markdown("#### 📊 本体信息概览")
            col_info1, col_info2, col_info3 = st.columns(3)
            
            # 实体数量，点击展开详情
            with col_info1:
                with st.expander(f"🏢 **实体数量**: {len(ontology_data['nodes'])} 个"):
                    st.markdown("**实体详情**:")
                    entities_df = pd.DataFrame([
                        {"ID": node['id'], "名称": node['label'], "类型": node['type'], "描述": node['description']}
                        for node in ontology_data['nodes']
                    ])
                    st.dataframe(entities_df, use_container_width=True)
            
            # 关系数量，点击展开详情
            with col_info2:
                with st.expander(f"🔗 **关系数量**: {len(ontology_data['edges'])} 个"):
                    st.markdown("**关系详情**:")
                    relations_df = pd.DataFrame([
                        {"源节点": edge['source'], "目标节点": edge['target'], "关系类型": edge['label']}
                        for edge in ontology_data['edges']
                    ])
                    st.dataframe(relations_df, use_container_width=True)
            
            # 规则数量，点击展开详情
            with col_info3:
                with st.expander(f"📋 **规则数量**: {len(ontology_data['rules'])} 个"):
                    st.markdown("**规则详情**:")
                    for rule in ontology_data['rules']:
                        st.info(f"📋 {rule['name']}: {rule['description']}")
            
            st.markdown("---")
            
            # 节点选择和添加功能
            st.markdown("#### 🎯 节点选择与添加")
            
            # 处理节点点击事件
            pass
            
            # 源节点选择，默认值为session_state中的selected_source
            node_options = [node['id'] for node in ontology_data['nodes']]
            print(f"节点选项: {node_options}")
            print(f"当前 selected_source: {st.session_state.selected_source}")
            default_index = 0
            if 'selected_source' in st.session_state and st.session_state.selected_source in node_options:
                default_index = node_options.index(st.session_state.selected_source)
                print(f"计算的 default_index: {default_index}")
            selected_source = st.selectbox("选择源节点", node_options, index=default_index)
            # 更新session_state
            st.session_state.selected_source = selected_source
            
            # 目标节点选择，添加空选项
            target_options = [""]  # 空选项，代表只添加源节点
            if selected_source:
                # 找到与源节点相关的目标节点
                for edge in ontology_data['edges']:
                    if edge['source'] == selected_source:
                        target_options.append(edge['target'])
                # 去重
                target_options = list(set(target_options))
            
            selected_target = st.selectbox("选择目标节点（为空则只添加源节点）", target_options, key="target_node")
            
            if st.button("添加到画布", key="add_to_canvas"):
                # 添加源节点（如果不存在）
                if selected_source:
                    if selected_source not in [n['id'] for n in st.session_state.selected_nodes]:
                        node = next(n for n in ontology_data['nodes'] if n['id'] == selected_source)
                        st.session_state.selected_nodes.append(node)
                    
                    # 如果选择了目标节点，添加目标节点和边
                    if selected_target:
                        if selected_target not in [n['id'] for n in st.session_state.selected_nodes]:
                            node = next(n for n in ontology_data['nodes'] if n['id'] == selected_target)
                            st.session_state.selected_nodes.append(node)
                        
                        # 添加边（如果不存在）
                        edge_exists = any(
                            e['source'] == selected_source and e['target'] == selected_target 
                            for e in st.session_state.selected_edges
                        )
                        if not edge_exists:
                            edge = next(e for e in ontology_data['edges'] if e['source'] == selected_source and e['target'] == selected_target)
                            st.session_state.selected_edges.append(edge)
                            st.success(f"已添加关系: {selected_source} → {selected_target}")
                    else:
                        st.success(f"已添加节点: {selected_source}")
            
            # 绘制选中的内容（无论是否点击了添加按钮）
            if st.session_state.selected_nodes or st.session_state.selected_edges:
                st.markdown("**关系图**:")
                selected_graph_data = {
                    "nodes": st.session_state.selected_nodes,
                    "edges": st.session_state.selected_edges,
                    "rules": []
                }
                fig = self._plot_ontology_graph(selected_graph_data)
                
                # 使用 st.plotly_chart 的 on_select 参数来处理点击事件
                selected_points = st.plotly_chart(fig, on_select="rerun", use_container_width=True)
                
                print(f"selected_points: {selected_points}")
                
                # 处理点击事件
                if selected_points and 'selection' in selected_points:
                    selection = selected_points['selection']
                    print(f"selection: {selection}")
                    if 'point_indices' in selection and len(selection['point_indices']) > 0:
                        point_index = selection['point_indices'][0]
                        # 获取节点 ID
                        node_ids = [node['id'] for node in st.session_state.selected_nodes]
                        if point_index < len(node_ids):
                            clicked_node_id = node_ids[point_index]
                            print(f"点击了节点: {clicked_node_id}")
                            print(f"点击前 selected_source: {st.session_state.selected_source}")
                            # 自动设置为源节点
                            st.session_state.selected_source = clicked_node_id
                            print(f"点击后 selected_source: {st.session_state.selected_source}")
                            # 扩展图形，添加与该节点相关的所有节点和边
                            for edge in ontology_data['edges']:
                                if edge['source'] == clicked_node_id:
                                    # 添加目标节点
                                    if edge['target'] not in [n['id'] for n in st.session_state.selected_nodes]:
                                        node = next(n for n in ontology_data['nodes'] if n['id'] == edge['target'])
                                        st.session_state.selected_nodes.append(node)
                                    # 添加边
                                    if edge not in st.session_state.selected_edges:
                                        st.session_state.selected_edges.append(edge)
                            print(f"节点点击处理完成")
                            # 强制重新渲染
                            st.rerun()
            
            # 清空选中列表
            if st.button("清空画布", key="clear_canvas"):
                st.session_state.selected_nodes = []
                st.session_state.selected_edges = []
                st.success("已清空画布")
    
    def _render_step5(self):
        """步骤5：What constrain should applied to control the data quality?"""
        st.markdown("""
        <div class="step-header">
            步骤5：What constrain should applied to control the data quality? / 应对施加哪些约束来控制数据质量
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-content">
        <p><strong>规则：部件A和部件A1是相同型号，可以通用</strong></p>
        <ul>
            <li>数据完整性：无缺失值</li>
            <li>数据准确性：数值范围合理</li>
            <li>数据一致性：时间连续</li>
            <li>业务约束：部件可以通用</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_step6(self):
        """步骤6：How should the data asset be leveraged?"""
        st.markdown("""
        <div class="step-header">
            步骤6：How should the data asset be leveraged? / 数据资产应该如何被利用
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-content">
        <p><strong>用户需要利用数据资产进行根因分析，发现库存高位问题的根本原因。</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        self._render_step6_1()
        self._render_step6_2()
        self._render_step6_3()
    
    def _render_step6_1(self):
        """步骤6.1：发生了什么？"""
        st.markdown("#### 6.1 发生了什么？")
        
        st.markdown("""
        <div class="info-box">
        <p><strong>展示当前的库存数据和指标数据，用户可以查看库存数据和指标数据。</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        if self.actual_data is not None:
            fig = self._plot_inventory_trend()
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="success-box">
            <h4>结论</h4>
            <p>当前库存数据显示，有一些商品的库存数量异常高，导致库存高位问题。</p>
            <ul>
                <li>产品A销量在11月开始下降</li>
                <li>部件A库存持续升高</li>
                <li>库存占用资金增加</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_step6_2(self):
        """步骤6.2：为什么会发生？"""
        st.markdown("#### 6.2 为什么会发生？")
        
        st.markdown("""
        <div class="info-box">
        <p><strong>定义因果因素，展示因果图，进行根因分析。</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # 初始化session_state
        if 'causal_graph' not in st.session_state:
            st.session_state.causal_graph = """digraph {
    kunlun_2280_sales -> pac900s12_b2_consumption;
    server_2288hv7_sales -> pac900s12_b2_consumption;
    server_2288hv7_uses_pac900s12_b2 -> pac900s12_b2_consumption;
    pac900s12_b2_consumption -> pac900s12_b2_inventory;
    pac900s12_b2_procurement -> pac900s12_b2_inventory;
    kunlun_2280_sales -> pac900s12_b2_procurement;
}"""
        
        if 'edited_causal_graph' not in st.session_state:
            st.session_state.edited_causal_graph = st.session_state.causal_graph
        
        # 第一部分：因果图展示和构建
        st.markdown("##### 📊 因果图展示")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 直接展示因果图可视化
            st.markdown("**因果图可视化**:")
            fig = self._plot_causal_graph_from_string(st.session_state.causal_graph)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**因果图定义**:")
            st.code(st.session_state.causal_graph, language="python")
            
            # 使用大模型构建因果图按钮
            if st.button("🤖 使用大模型构建因果图", type="primary"):
                if self.llm_explainer is None:
                    st.warning("请先在侧边栏配置大模型API密钥并初始化解释器")
                else:
                    with st.spinner("大模型正在构建因果图..."):
                        try:
                            # 调用大模型构建因果图
                            new_graph = self._build_causal_graph_with_llm()
                            if new_graph:
                                st.session_state.causal_graph = new_graph
                                st.session_state.edited_causal_graph = new_graph
                                st.success("✅ 因果图构建成功！")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ 构建失败: {str(e)}")
        
        st.markdown("---")
        
        # 第二部分：人工修正因果图
        st.markdown("##### ✏️ 人工修正因果图")
        
        edited_graph = st.text_area(
            "编辑因果图（DOT格式）",
            value=st.session_state.edited_causal_graph,
            height=200,
            help="可以直接编辑因果图，格式为DOT语言"
        )
        
        col_btn1, col_btn2 = st.columns([1, 1])
        
        with col_btn1:
            if st.button("✅ 应用修改"):
                st.session_state.causal_graph = edited_graph
                st.session_state.edited_causal_graph = edited_graph
                st.success("✅ 因果图已更新！")
                st.rerun()
        
        with col_btn2:
            if st.button("🔄 重置为默认"):
                default_graph = """digraph {
    kunlun_2280_sales -> pac900s12_b2_consumption;
    server_2288hv7_sales -> pac900s12_b2_consumption;
    server_2288hv7_uses_pac900s12_b2 -> pac900s12_b2_consumption;
    pac900s12_b2_consumption -> pac900s12_b2_inventory;
    pac900s12_b2_procurement -> pac900s12_b2_inventory;
    kunlun_2280_sales -> pac900s12_b2_procurement;
}"""
                st.session_state.causal_graph = default_graph
                st.session_state.edited_causal_graph = default_graph
                st.success("✅ 已重置为默认因果图！")
                st.rerun()
        
        st.markdown("---")
        
        # 第三部分：运行因果分析
        st.markdown("##### 🔬 因果分析")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fast_mode = st.checkbox(
                "🚀 快速模式",
                value=True,
                help="快速模式跳过驳斥检验和多变量分析，大幅提升分析速度"
            )
        
        with col2:
            if st.button("运行因果分析", type="primary", use_container_width=True):
                self.run_analysis(fast_mode=fast_mode)
        
        if self.analysis_results:
            st.markdown("**分析结果**:")
            
            cf_results = self.analysis_results.get('counterfactual_analysis', {})
            
            # 第一部分：反事实分析结果
            st.markdown("##### 📊 反事实分析结果")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "库存降低量",
                    f"{cf_results.get('inventory_reduction', 0):.0f} 单位",
                    f"{cf_results.get('reduction_percentage', 0):.1f}%"
                )
            
            with col2:
                st.metric(
                    "实际库存均值",
                    f"{cf_results.get('actual_inventory_mean', 0):.0f}",
                    "当前状态"
                )
            
            with col3:
                st.metric(
                    "反事实库存均值",
                    f"{cf_results.get('counterfactual_inventory_mean', 0):.0f}",
                    "如果产品B使用部件A"
                )
            
            st.markdown("---")
            
            # 第二部分：销量下降期分析
            st.markdown("##### 📉 销量下降期分析")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "下降期实际库存",
                    f"{cf_results.get('decline_period_actual_inventory', 0):.0f}",
                    "销量下降期间"
                )
            
            with col2:
                st.metric(
                    "下降期反事实库存",
                    f"{cf_results.get('decline_period_counterfactual_inventory', 0):.0f}",
                    "如果产品B使用部件A"
                )
            
            with col3:
                decline_reduction = cf_results.get('decline_period_reduction', 0)
                decline_actual = cf_results.get('decline_period_actual_inventory', 1)
                decline_pct = (decline_reduction / decline_actual * 100) if decline_actual > 0 else 0
                st.metric(
                    "下降期库存降低",
                    f"{decline_reduction:.0f}",
                    f"{decline_pct:.1f}%"
                )
            
            st.markdown("---")
            
            # 第三部分：根因判定
            st.markdown("##### 🎯 根因判定")
            
            col1, col2 = st.columns(2)
            
            with col1:
                is_root_cause = cf_results.get('is_root_cause', False)
                st.metric(
                    "是否为核心根因",
                    "是" if is_root_cause else "否",
                    "库存降低超过20%即为根因"
                )
            
            with col2:
                st.metric(
                    "根因强度",
                    f"{cf_results.get('reduction_percentage', 0):.1f}%",
                    "影响程度"
                )
            
            st.markdown("---")
            
            # 第四部分：因果效应值
            st.markdown("##### 📈 因果效应估计")
            
            causal_effect = self.analysis_results.get('causal_effect', 0)
            st.metric(
                "因果效应值",
                f"{causal_effect:.4f}",
                "处理变量对结果变量的平均影响"
            )
            
            st.markdown("---")
            
            # 第五部分：驳斥检验结果
            st.markdown("##### ✅ 驳斥检验结果")
            
            refutation_results = self.analysis_results.get('refutation_results', {})
            
            if not refutation_results:
                st.info("💡 快速模式下跳过了驳斥检验。如需完整分析，请取消勾选'快速模式'后重新运行。")
            elif refutation_results:
                for test_name, result in refutation_results.items():
                    if isinstance(result, dict) and 'error' not in result:
                        with st.expander(f"**{test_name}** 检验", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(
                                    "新效应值",
                                    f"{result.get('new_effect', 0):.4f}"
                                )
                            with col2:
                                p_value = result.get('p_value', 0)
                                st.metric(
                                    "P值",
                                    f"{p_value:.4f}",
                                    "P < 0.05 表示显著"
                                )
                            
                            # 判断检验是否通过
                            if test_name == "placebo":
                                is_significant = result.get('is_statistically_significant', False)
                                if is_significant:
                                    st.success("✅ 安慰剂检验通过：新效应值接近0，说明结果稳健")
                                else:
                                    st.warning("⚠️ 安慰剂检验未通过：新效应值不接近0")
                            elif test_name in ["random_common_cause", "data_subset"]:
                                is_robust = result.get('is_robust', False)
                                if is_robust:
                                    st.success(f"✅ {test_name}检验通过：结果稳健")
                                else:
                                    st.warning(f"⚠️ {test_name}检验未通过：结果可能不稳健")
                    elif isinstance(result, dict) and 'error' in result:
                        st.error(f"❌ {test_name} 检验失败: {result['error']}")
            
            st.markdown("---")
            
            # 第六部分：多变量因果效应分析
            st.markdown("##### 📋 多变量因果效应分析")
            
            causal_effects = self.analysis_results.get('causal_effects', [])
            
            if causal_effects and len(causal_effects) > 0:
                # 检查是否是快速模式的结果
                first_effect = causal_effects[0] if isinstance(causal_effects[0], dict) else {}
                if first_effect.get('note') == '快速模式':
                    st.info("💡 快速模式下跳过了多变量分析。如需完整分析，请取消勾选'快速模式'后重新运行。")
                else:
                    effects_df = pd.DataFrame(causal_effects)
                    st.dataframe(effects_df, use_container_width=True)
            else:
                st.info("💡 快速模式下跳过了多变量分析。如需完整分析，请取消勾选'快速模式'后重新运行。")
            
            st.markdown("---")
            
            st.markdown("##### 🤖 智能解释（根因是什么）")
            
            if self.llm_explainer is None:
                st.warning("请先在侧边栏配置大模型API密钥并初始化解释器")
            else:
                if st.button("生成根因解释", key="gen_root_cause"):
                    explanation = self.generate_root_cause_explanation()
                    if explanation:
                        st.markdown(explanation)
                        
                        st.download_button(
                            label="下载根因解释",
                            data=explanation,
                            file_name="根因解释.md",
                            mime="text/markdown"
                        )
    
    def _render_step6_3(self):
        """步骤6.3：如何解决？"""
        st.markdown("#### 6.3 如何解决？")
        
        st.markdown("""
        <div class="info-box">
        <p><strong>调用LLM生成解决方案，根据反事实分析给出的解决方案。</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        if self.analysis_results is None:
            st.warning("请先运行因果分析")
        elif self.llm_explainer is None:
            st.warning("请先在侧边栏配置大模型API密钥并初始化解释器")
        else:
            if st.button("生成解决方案", key="gen_solution"):
                solution = self.generate_solution()
                if solution:
                    st.markdown(solution)
                    
                    st.download_button(
                        label="下载解决方案",
                        data=solution,
                        file_name="解决方案.md",
                        mime="text/markdown"
                    )
    
    def _render_step7(self):
        """步骤7：Describe any automations necessary for users to fulfill their tasks?"""
        st.markdown("""
        <div class="step-header">
            步骤7：Describe any automations necessary for users to fulfill their tasks? / 用户完成其任务所需的自动化措施
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-content">
        <p><strong>本次演示不展示</strong></p>
        <p>在实际应用中，可以包括：</p>
        <ul>
            <li>自动数据采集和清洗</li>
            <li>自动因果分析</li>
            <li>自动报告生成</li>
            <li>自动预警通知</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_step8(self):
        """步骤8：Define roles and permissions?"""
        st.markdown("""
        <div class="step-header">
            步骤8：Define roles and permissions? / 定义角色和权限
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-content">
        <p><strong>本次演示不展示</strong></p>
        <p>在实际应用中，可以包括：</p>
        <ul>
            <li>数据分析师：查看和分析数据</li>
            <li>业务经理：查看报告和决策</li>
            <li>系统管理员：配置和管理系统</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def _plot_ontology_graph(self, ontology_data):
        """绘制本体图"""
        G = nx.DiGraph()
        
        for node in ontology_data['nodes']:
            G.add_node(node['id'], label=node['label'], type=node['type'])
        
        for edge in ontology_data['edges']:
            G.add_edge(edge['source'], edge['target'], label=edge['label'])
        
        pos = nx.spring_layout(G, k=0.8, iterations=100)
        
        arrows = []
        edge_labels = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            dx = x1 - x0
            dy = y1 - y0
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
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
                
                # 添加边的标签
                edge_label = G.edges[edge]['label']
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2
                
                edge_labels.append(
                    dict(
                        x=mid_x,
                        y=mid_y,
                        xref='x',
                        yref='y',
                        text=edge_label,
                        showarrow=False,
                        font=dict(size=10, color='#666'),
                        bgcolor='rgba(255, 255, 255, 0.8)',
                        bordercolor='#ccc',
                        borderwidth=1,
                        borderpad=2
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
            node_label = G.nodes[node]['label']
            node_type = G.nodes[node]['type']
            node_text.append(node_label)
            if node_type in ['Product', 'Server']:
                node_color.append('#2E86AB')  # 蓝色 - 服务器
            elif node_type == 'PartType':
                node_color.append('#28A745')  # 绿色 - 部件类型
            else:
                node_color.append('#A23B72')  # 紫色 - 具体部件
        
        # 准备节点数据
        node_ids = [node for node in G.nodes()]
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color=node_color,
                size=30,
                line_width=2
            ),
            text=node_text,
            textposition="top center",
            textfont=dict(size=12),
            customdata=node_ids
        )
        
        fig = go.Figure(data=[node_trace],
                       layout=go.Layout(
                           title=dict(text='本体图（产品与部件关系）', font=dict(size=16)),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=arrows + edge_labels,
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           clickmode='event+select',
                           dragmode='select'
                       ))
        
        return fig
    
    def _plot_causal_graph(self):
        """绘制因果图"""
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
        
        arrows = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            dx = x1 - x0
            dy = y1 - y0
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
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
                           title=dict(text='因果图（有向无环图）', font=dict(size=16)),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=arrows,
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        
        return fig
    
    def _plot_causal_graph_from_string(self, graph_string: str):
        """
        从DOT格式字符串绘制因果图
        
        Args:
            graph_string: DOT格式的因果图字符串
            
        Returns:
            Plotly图表对象
        """
        G = nx.DiGraph()
        
        # 英文变量名到中文的映射
        variable_name_mapping = {
            'kunlun_2280_sales': '昆仑2280销量',
            'server_2288hv7_sales': '2288HV7销量',
            'server_2288hv7_uses_pac900s12_b2': '2288HV7使用PAC900S12-B2',
            'pac900s12_b2_consumption': 'PAC900S12-B2消耗量',
            'pac900s12_b2_inventory': 'PAC900S12-B2库存',
            'pac900s12_b2_procurement': 'PAC900S12-B2采购量'
        }
        
        # 解析DOT格式字符串
        lines = graph_string.strip().split('\n')
        for line in lines:
            line = line.strip()
            if '->' in line:
                # 提取边信息
                parts = line.replace(';', '').split('->')
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip()
                    G.add_edge(source, target)
        
        if G.number_of_nodes() == 0:
            # 如果没有解析到节点，使用默认因果图
            return self._plot_causal_graph()
        
        pos = nx.spring_layout(G, k=0.8, iterations=100)
        
        arrows = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            dx = x1 - x0
            dy = y1 - y0
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
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
            # 将英文变量名转换为中文显示
            display_text = variable_name_mapping.get(node, node)
            node_text.append(display_text)
            # 根据节点名称设置颜色
            if '库存' in display_text or 'inventory' in node.lower():
                node_color.append('#A23B72')
            elif '使用' in display_text or '销量' in display_text or 'uses' in node.lower() or 'sales' in node.lower():
                node_color.append('#2E86AB')
            else:
                node_color.append('#17A2B8')
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=False,
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
                           title=dict(text='因果图（有向无环图）', font=dict(size=16)),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=arrows,
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        
        return fig
    
    def _build_causal_graph_with_llm(self):
        """
        使用大模型构建因果图
        
        Returns:
            构建的因果图字符串（DOT格式）
        """
        if self.llm_explainer is None or self.llm_explainer.client is None:
            raise ValueError("大模型客户端未初始化")
        
        # 构建提示词
        prompt = """你是一个专业的因果分析专家。请根据以下信息构建因果图。

## 问题描述
某制造企业发现部件A库存持续升高，占用大量资金，需要找出根本原因。

## 本体信息
以下是产品与部件的关系：
- 产品A 使用 部件A
- 产品B 使用 部件A1

## 业务规则
- 部件A和部件A1是相同型号，可以通用
- 产品A销量在近期出现下降
- 产品B销量保持稳定

## 数据字段
- kunlun_2280_sales: 昆仑2280销量
- server_2288hv7_sales: 2288HV7销量
- server_2288hv7_uses_pac900s12_b2: 2288HV7是否使用PAC900S12-B2（0或1）
- pac900s12_b2_consumption: PAC900S12-B2消耗量
- pac900s12_b2_inventory: PAC900S12-B2库存
- pac900s12_b2_procurement: PAC900S12-B2采购量

## 分析任务
请分析以下问题：
1. 根据本体信息和业务规则，发现可能存在的问题
2. 构建因果图，展示变量之间的因果关系
3. 特别关注：产品B是否应该使用部件A？这对库存有什么影响？

## 输出要求
请构建一个因果图，使用DOT格式输出。格式如下：
```
digraph {
    变量1 -> 变量2;
    变量2 -> 变量3;
    ...
}
```

注意事项：
1. 只输出DOT格式的因果图，不要有其他解释
2. 节点名称必须与数据字段名称一致
3. 箭头方向表示因果关系（原因 -> 结果）
4. 确保因果图是有向无环图（DAG）
5. 特别注意：如果发现本体信息中缺少某些关系，请在因果图中体现出来
"""
        
        # 保存提示词到文件
        self._save_causal_graph_prompt(prompt)
        
        try:
            # 调用大模型API
            response = self.llm_explainer.client.chat.completions.create(
                model=self.llm_explainer.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的因果分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            
            # 提取DOT格式代码
            if '```' in result:
                # 提取代码块中的内容
                parts = result.split('```')
                if len(parts) >= 2:
                    # 找到包含digraph的代码块
                    for part in parts:
                        if 'digraph' in part:
                            # 去除语言标记（如python、dot等）
                            lines = part.strip().split('\n')
                            # 跳过第一行（语言标记）
                            dot_content = '\n'.join(lines[1:] if lines[0].strip() in ['python', 'dot', ''] else lines)
                            return dot_content.strip()
            
            # 如果没有代码块，直接返回结果
            return result.strip()
            
        except Exception as e:
            raise Exception(f"大模型构建因果图失败: {str(e)}")
    
    def _save_causal_graph_prompt(self, prompt: str):
        """
        保存构建因果图的提示词到文件
        
        Args:
            prompt: 提示词内容
        """
        import os
        import datetime
        
        # 确保prompts目录存在
        prompt_dir = "prompts"
        if not os.path.exists(prompt_dir):
            os.makedirs(prompt_dir)
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(prompt_dir, f"causal_graph_prompt_{timestamp}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
                f.write(f"模型: {self.llm_explainer.model if self.llm_explainer else 'Unknown'}\n")
                f.write("\n" + "="*80 + "\n\n")
                f.write("【构建因果图提示词】\n\n")
                f.write(prompt)
                f.write("\n\n" + "="*80 + "\n")
                f.write("说明：此提示词用于让大模型根据场景描述和本体信息构建因果图\n")
        except Exception as e:
            print(f"保存因果图提示词失败: {str(e)}")
    
    def _plot_inventory_trend(self):
        """绘制库存趋势图和月度指标柱状图"""
        from plotly.subplots import make_subplots
        
        # 创建子图：上面是趋势图，下面是月度柱状图
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('部件A库存趋势', '部件A库存月度指标'),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4]
        )
        
        # 趋势图：只显示实际库存
        fig.add_trace(
            go.Scatter(
                x=self.actual_data['date'],
                y=self.actual_data['pac900s12_b2_inventory'],
                mode='lines',
                name='实际库存',
                line=dict(color='#DC3545', width=2),
                hovertemplate='日期: %{x}<br>库存: %{y}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 计算月度统计数据
        monthly_data = self.actual_data.copy()
        monthly_data['month'] = pd.to_datetime(monthly_data['date']).dt.to_period('M')
        monthly_stats = monthly_data.groupby('month').agg({
            'pac900s12_b2_inventory': ['mean', 'max', 'min'],
            'kunlun_2280_sales': 'sum',
            'server_2288hv7_sales': 'sum'
        }).reset_index()
        
        monthly_stats.columns = ['month', 'avg_inventory', 'max_inventory', 'min_inventory', 'kunlun_2280_sales', 'server_2288hv7_sales']
        monthly_stats['month_str'] = monthly_stats['month'].astype(str)
        
        # 月度柱状图：平均库存
        fig.add_trace(
            go.Bar(
                x=monthly_stats['month_str'],
                y=monthly_stats['avg_inventory'],
                name='月平均库存',
                marker_color='#2E86AB',
                text=monthly_stats['avg_inventory'].round(0),
                textposition='outside',
                hovertemplate='月份: %{x}<br>平均库存: %{y:.0f}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 添加最大最小库存的误差线
        fig.add_trace(
            go.Bar(
                x=monthly_stats['month_str'],
                y=monthly_stats['max_inventory'],
                name='月最大库存',
                marker_color='#A23B72',
                opacity=0.6,
                hovertemplate='月份: %{x}<br>最大库存: %{y:.0f}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 标记销量下降期
        decline_start = self.actual_data[self.actual_data['is_decline_period'] == True]['date'].min()
        
        # 更新布局
        fig.update_xaxes(title_text="日期", row=1, col=1)
        fig.update_yaxes(title_text="库存水平", row=1, col=1)
        fig.update_xaxes(title_text="月份", row=2, col=1)
        fig.update_yaxes(title_text="库存数量", row=2, col=1)
        
        fig.update_layout(
            height=800,
            showlegend=True,
            template='plotly_white',
            hovermode='x unified',
            title_text="部件A库存分析",
            title_x=0.5,
            title_font_size=16,
            # 在第一个子图添加垂直线标记
            shapes=[
                dict(
                    type='line',
                    xref='x',
                    yref='paper',
                    x0=decline_start,
                    y0=0,
                    x1=decline_start,
                    y1=1,
                    line=dict(color='orange', width=2, dash='dash'),
                    xanchor='x',
                    yanchor='paper',
                    layer='above'
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
                    yanchor='bottom',
                    xanchor='left'
                )
            ]
        )
        
        return fig


if __name__ == "__main__":
    app = InventoryAnalysisWebApp()
    page = app.render_sidebar()
    
    if page == "场景介绍":
        app.render_scenario_page()
    elif page == "根因分析":
        app.render_analysis_page()
