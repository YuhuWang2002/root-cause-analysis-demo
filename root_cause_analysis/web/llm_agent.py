"""
LLM Agent模块

支持：
- 查询本体API获取本体信息
- 根据场景描述理解问题
- 推导因果图
- 返回推导结果

MVP架构简化：
- 因果图节点直接对应数据字段
- 保持与 data_generator.py 生成的字段一致
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel


# ============ 数据模型 ============

class OntologyQueryRequest(BaseModel):
    """本体查询请求"""
    query_type: str  # "entities", "relations", "attributes", "all"


class OntologyQueryResponse(BaseModel):
    """本体查询响应"""
    entities: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]
    attributes: List[Dict[str, Any]]


class CausalGraphDerivationRequest(BaseModel):
    """因果图推导请求"""
    scenario_description: str
    outcome_entity: str
    ontology_info: Optional[Dict[str, Any]] = None


class CausalGraphDerivationResponse(BaseModel):
    """因果图推导响应"""
    causal_graph: Dict[str, List[str]]  # 节点直接对应数据字段
    reasoning: str
    suggested_data_fields: List[str]
    required_entities: List[str]


class AnalysisResultsExplanationRequest(BaseModel):
    """分析结果解释请求"""
    analysis_results: Dict[str, Any]
    scenario_description: Optional[str] = None


class AnalysisResultsExplanationResponse(BaseModel):
    """分析结果解释响应"""
    root_cause_analysis: str
    impact_mechanism: str
    improvement_suggestions: str
    expected_effect: str
    reasoning: str


class LLMAgent:
    """LLM Agent - 支持本体查询和因果图推导"""
    
    def __init__(self, ontology_api_url: str = "http://localhost:8000", llm_api_key: str = None, llm_base_url: str = None, llm_model: str = None):
        """
        初始化LLM Agent
        
        Args:
            ontology_api_url: 本体API地址
            llm_api_key: 大模型API密钥
            llm_base_url: 大模型API基础URL
            llm_model: 大模型名称
        """
        self.ontology_api_url = ontology_api_url
        self.llm_api_key = llm_api_key
        self.llm_base_url = llm_base_url
        self.llm_model = llm_model
        self.http_client = None
    
    async def query_ontology(self, query_type: str = "all") -> OntologyQueryResponse:
        """
        查询本体API
        
        Args:
            query_type: 查询类型 ("entities", "relations", "attributes", "all")
            
        Returns:
            本体查询响应
        """
        import httpx
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        
        try:
            response = await self.http_client.get(
                f"{self.ontology_api_url}/entities" if query_type in ["all", "entities"] else 
                f"{self.ontology_api_url}/relations" if query_type == "relations" else
                f"{self.ontology_api_url}/attributes" if query_type == "attributes" else
                f"{self.ontology_api_url}/ontology"
            )
            response.raise_for_status()
            data = response.json()
            
            # 根据查询类型返回数据
            if query_type in ["all", "entities"]:
                return OntologyQueryResponse(
                    entities=data.get("entities", []),
                    relations=[],
                    attributes=[]
                )
            elif query_type == "relations":
                return OntologyQueryResponse(
                    entities=[],
                    relations=data.get("relations", []),
                    attributes=[]
                )
            elif query_type == "attributes":
                return OntologyQueryResponse(
                    entities=[],
                    relations=[],
                    attributes=data.get("attributes", [])
                )
            else:  # ontology
                return OntologyQueryResponse(
                    entities=data.get("entities", []),
                    relations=data.get("relations", []),
                    attributes=data.get("attributes", [])
                )
                
        except Exception as e:
            print(f"[LLM Agent] 查询本体API失败: {str(e)}")
            raise
    
    async def query_schema(self) -> dict:
        """
        查询本体Schema（元数据）
        
        Returns:
            Schema响应字典
        """
        import httpx
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        
        try:
            response = await self.http_client.get(
                f"{self.ontology_api_url}/schema"
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"[LLM Agent] Schema查询成功")
            return data
            
        except Exception as e:
            print(f"[LLM Agent] 查询Schema失败: {str(e)}")
            raise
    
    async def derive_causal_graph(self, request: CausalGraphDerivationRequest) -> CausalGraphDerivationResponse:
        """
        推导因果图
        
        这个方法需要：
        1. 查询本体获取实体和关系
        2. 使用LLM理解场景并推导因果图
        3. 返回推导结果
        
        Args:
            request: 因果图推导请求
            
        Returns:
            因果图推导响应
        """
        # 第一步：查询本体Schema获取元数据
        schema_response = await self.query_schema()
        
        # 第二步：构建提示词让LLM推导因果图
        prompt = self._build_derivation_prompt(
            request.scenario_description,
            request.outcome_entity,
            schema_response
        )
        
        # 第三步：调用LLM API推导因果图
        print("[LLM Agent] 调用大模型API推导因果图...")
        
        import openai
        
        if not self.llm_api_key:
            raise ValueError("LLM API密钥未配置")
        if not self.llm_base_url:
            raise ValueError("LLM Base URL未配置")
        if not self.llm_model:
            raise ValueError("LLM Model未配置")
        
        try:
            client = openai.OpenAI(
                api_key=self.llm_api_key,
                base_url=self.llm_base_url
            )
            
            print(f"[LLM Agent] 调用大模型API...")
            completion = client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            print(f"[LLM Agent] 大模型API调用成功")
            
            response_text = completion.choices[0].message.content
            print(f"[LLM Agent] 响应长度: {len(response_text)} 字符")
            
            import json
            llm_result = json.loads(response_text)
            
            causal_graph = llm_result.get("causal_graph", {})
            reasoning = llm_result.get("reasoning", "")
            suggested_fields = llm_result.get("suggested_data_fields", [])
            required_entities = llm_result.get("required_entities", [])
            
            print(f"[LLM Agent] 因果图节点数: {len(causal_graph)}")
            print(f"[LLM Agent] 建议数据字段数: {len(suggested_fields)}")
            
            return CausalGraphDerivationResponse(
                causal_graph=causal_graph,
                reasoning=reasoning,
                suggested_data_fields=suggested_fields,
                required_entities=required_entities
            )
            
        except Exception as e:
            print(f"[LLM Agent] 调用大模型API失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            raise
    
    def _build_derivation_prompt(self, 
                                scenario_description: str,
                                outcome_entity: str,
                                schema_response: dict) -> str:
        """
        构建因果图推导的提示词

        Args:
            scenario_description: 场景描述
            outcome_entity: 结果实体
            schema_response: Schema响应（包含entity_types, relation_types, metric_definitions）

        Returns:
            提示词字符串
        """
        prompt = f"""你是一个专业的因果分析专家。请根据以下本体Schema信息和业务场景，推导出合理的因果图。

## 场景描述
{scenario_description}

## 结果实体
{outcome_entity}

## 本体Schema信息

### 实体类型及其属性
"""
        
        for entity_type in schema_response.get("entity_types", []):
            prompt += f"""
**{entity_type['name']}** ({entity_type['id']})
- 描述: {entity_type['description']}
- 属性:
"""
            for attr in entity_type.get("attributes", []):
                prompt += f"  - {attr['name']} ({attr['type']}): {attr['description']}\n"
        
        prompt += """
### 关系类型
"""
        
        for relation_type in schema_response.get("relation_types", []):
            source_types = ", ".join(relation_type.get("source_types", []))
            target_types = ", ".join(relation_type.get("target_types", []))
            prompt += f"""
**{relation_type['name']}** ({relation_type['id']})
- 描述: {relation_type['description']}
- 源类型: {source_types}
- 目标类型: {target_types}
"""
        
        prompt += """
### 指标定义（从实体属性派生）
"""
        
        for metric in schema_response.get("metric_definitions", []):
            prompt += f"""
**{metric['name']}** ({metric['id']})
- 描述: {metric['description']}
- 源实体类型: {metric.get('source_entity_type', 'N/A')}
- 目标实体类型: {metric.get('target_entity_type', 'N/A')}
- 源关系类型: {metric.get('source_relation', 'N/A')}
- 指标类型: {metric.get('type', 'N/A')}
"""
        
        prompt += """
## 任务
请根据场景描述和本体Schema信息，推导出合理的因果图。

要求：
1. 因果图必须包含结果实体"{outcome_entity}"
2. 因果图中的节点必须来自指标定义中的metric_id
3. 因果图中的边必须反映合理的因果关系（如：A影响B，B影响C）
4. 考虑实体类型和关系类型来推导因果关系
5. 返回格式：JSON格式的邻接表 {{"source": ["target1", "target2"]}

请以JSON格式返回你的推导结果，包含：
- causal_graph: 因果图邻接表
- reasoning: 推导过程说明
- suggested_data_fields: 建议需要收集的数据字段列表
- required_entities: 因果图中涉及的实体ID列表
"""
        
        return prompt
    
    async def explain_analysis_results(self, request: AnalysisResultsExplanationRequest) -> AnalysisResultsExplanationResponse:
        """
        解释分析结果

        Args:
            request: 分析结果解释请求

        Returns:
            分析结果解释响应
        """
        # 构建提示词让LLM解释分析结果
        prompt = self._build_explanation_prompt(
            request.analysis_results,
            request.scenario_description
        )
        
        # 调用LLM API解释分析结果
        print("[LLM Agent] 调用大模型API解释分析结果...")
        
        import openai
        
        if not self.llm_api_key:
            raise ValueError("LLM API密钥未配置")
        if not self.llm_base_url:
            raise ValueError("LLM Base URL未配置")
        if not self.llm_model:
            raise ValueError("LLM Model未配置")
        
        try:
            client = openai.OpenAI(
                api_key=self.llm_api_key,
                base_url=self.llm_base_url
            )
            
            print(f"[LLM Agent] 调用大模型API...")
            completion = client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            print(f"[LLM Agent] 大模型API调用成功")
            
            response_text = completion.choices[0].message.content
            print(f"[LLM Agent] 响应长度: {len(response_text)} 字符")
            
            import json
            llm_result = json.loads(response_text)
            
            root_cause_analysis = llm_result.get("root_cause_analysis", "")
            impact_mechanism = llm_result.get("impact_mechanism", "")
            improvement_suggestions = llm_result.get("improvement_suggestions", "")
            expected_effect = llm_result.get("expected_effect", "")
            reasoning = llm_result.get("reasoning", "")
            
            return AnalysisResultsExplanationResponse(
                root_cause_analysis=root_cause_analysis,
                impact_mechanism=impact_mechanism,
                improvement_suggestions=improvement_suggestions,
                expected_effect=expected_effect,
                reasoning=reasoning
            )
            
        except Exception as e:
            print(f"[LLM Agent] 调用大模型API失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            raise
    
    def _build_explanation_prompt(self, 
                                analysis_results: Dict[str, Any],
                                scenario_description: Optional[str] = None) -> str:
        """
        构建分析结果解释的提示词

        Args:
            analysis_results: 分析结果字典
            scenario_description: 场景描述（可选）

        Returns:
            提示词字符串
        """
        prompt = f"""你是一个专业的因果分析专家。请根据以下DoWhy因果分析结果，生成详细的根因分析报告。

## 场景描述
{scenario_description or "通用因果分析场景"}

## DoWhy分析结果

### 因果效应
"""
        
        causal_effect = analysis_results.get("causal_effect")
        prompt += f"因果效应值: {causal_effect:.4f}\n" if causal_effect is not None else "因果效应值: 未计算\n"
        
        prompt += """

### 驳斥检验结果
"""
        
        refutation_results = analysis_results.get("refutation_results", {})
        for test_name, result in refutation_results.items():
            prompt += f"{test_name}: {result}\n"
        
        prompt += """

### 反事实分析结果
"""
        
        counterfactual_analysis = analysis_results.get("counterfactual_analysis", {})
        if counterfactual_analysis:
            prompt += f"反事实分析: {counterfactual_analysis}\n"
        else:
            prompt += "反事实分析: 未计算\n"
        
        prompt += """

## 任务
请基于以上DoWhy分析结果，生成详细的根因分析报告，包括：

1. **根本原因分析**：基于因果效应值和驳斥检验结果，分析影响结果变量的主要因素
2. **影响机制**：解释这些因素如何影响结果变量的机制
3. **改进建议**：基于分析结果，提出具体的改进措施
4. **预期效果**：评估改进措施实施后的预期效果

要求：
- 分析要基于实际的DoWhy计算结果，不要凭空猜测
- 语言要专业、客观、准确
- 建议要具体、可操作
- 预期效果要合理、可衡量

请以JSON格式返回你的分析结果，包含：
- root_cause_analysis: 根本原因分析
- impact_mechanism: 影响机制
- improvement_suggestions: 改进建议
- expected_effect: 预期效果
- reasoning: 分析过程说明
"""
        
        return prompt


# ============ 同步版本（用于非异步环境）===========

class LLMAgentSync(LLMAgent):
    """LLM Agent同步版本"""
    
    def __init__(self, ontology_api_url: str = "http://localhost:8000", llm_api_key: str = None, llm_base_url: str = None, llm_model: str = None):
        super().__init__(ontology_api_url, llm_api_key, llm_base_url, llm_model)
    
    def query_ontology(self, query_type: str = "all") -> OntologyQueryResponse:
        """同步版本的本体查询"""
        import httpx
        
        try:
            entities = []
            relations = []
            attributes = []
            
            if query_type in ["all", "entities"]:
                response = httpx.get(f"{self.ontology_api_url}/entities", timeout=30.0)
                response.raise_for_status()
                entities = response.json()
            
            if query_type in ["all", "relations"]:
                response = httpx.get(f"{self.ontology_api_url}/relations", timeout=30.0)
                response.raise_for_status()
                relations = response.json()
            
            if query_type in ["all", "attributes"]:
                response = httpx.get(f"{self.ontology_api_url}/attributes", timeout=30.0)
                response.raise_for_status()
                attributes = response.json()
            
            if query_type == "all":
                try:
                    response = httpx.get(f"{self.ontology_api_url}/ontology", timeout=30.0)
                    response.raise_for_status()
                    data = response.json()
                    entities = data.get("entities", [])
                    relations = data.get("relations", [])
                    attributes = data.get("attributes", [])
                except Exception:
                    pass
            
            return OntologyQueryResponse(
                entities=entities,
                relations=relations,
                attributes=attributes
            )
                
        except Exception as e:
            print(f"[LLM Agent Sync] 查询本体API失败: {str(e)}")
            raise
    
    def query_schema(self) -> dict:
        """同步版本的Schema查询"""
        import httpx
        
        try:
            response = httpx.get(
                f"{self.ontology_api_url}/schema",
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"[LLM Agent Sync] Schema查询成功")
            return data
            
        except Exception as e:
            print(f"[LLM Agent Sync] 查询Schema失败: {str(e)}")
            raise
    
    def derive_causal_graph(self, request: CausalGraphDerivationRequest) -> CausalGraphDerivationResponse:
        """同步版本的因果图推导 - 直接实现不使用super()"""
        import httpx
        
        # 第一步：查询本体Schema获取元数据
        print(f"[LLM Agent Sync] 正在查询本体Schema...")
        
        try:
            schema_response = self.query_schema()
            print(f"[LLM Agent Sync] 查询到 {len(schema_response.get('entity_types', []))} 个实体类型, {len(schema_response.get('relation_types', []))} 个关系类型")
            
        except Exception as e:
            print(f"[LLM Agent Sync] 查询Schema失败: {str(e)}, 将使用默认逻辑")
            # 使用默认响应
            schema_response = {
                "entity_types": [],
                "relation_types": [],
                "metric_definitions": []
            }
        
        # 第二步：构建提示词（直接使用基类的方法）
        print(f"[LLM Agent Sync] 正在构建提示词...")
        prompt = self._build_derivation_prompt(
            request.scenario_description,
            request.outcome_entity,
            schema_response
        )
        
        # 保存提示词
        import os
        from datetime import datetime
        
        prompt_dir = "prompts"
        if not os.path.exists(prompt_dir):
            os.makedirs(prompt_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_file = os.path.join(prompt_dir, f"agent_prompt_{timestamp}.txt")
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        print(f"[LLM Agent Sync] 提示词已保存到: {prompt_file}")
        
        # 第三步：调用LLM API推导因果图
        print(f"[LLM Agent Sync] 正在调用大模型API推导因果图...")
        
        import openai
        
        if not self.llm_api_key:
            raise ValueError("LLM API密钥未配置")
        if not self.llm_base_url:
            raise ValueError("LLM Base URL未配置")
        if not self.llm_model:
            raise ValueError("LLM Model未配置")
        
        try:
            client = openai.OpenAI(
                api_key=self.llm_api_key,
                base_url=self.llm_base_url
            )
            
            print(f"[LLM Agent Sync] 调用大模型API...")
            completion = client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            print(f"[LLM Agent Sync] 大模型API调用成功")
            
            response_text = completion.choices[0].message.content
            print(f"[LLM Agent Sync] 响应长度: {len(response_text)} 字符")
            print(f"[LLM Agent Sync] 响应内容前500字符: {response_text[:500]}")
            
            import json
            
            # 去除可能的代码块标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            llm_result = json.loads(response_text)
            
            causal_graph = llm_result.get("causal_graph", {})
            reasoning = llm_result.get("reasoning", "")
            suggested_fields_raw = llm_result.get("suggested_data_fields", [])
            required_entities = llm_result.get("required_entities", [])
            
            # 处理suggested_data_fields：可能是字符串列表或字典列表
            suggested_fields = []
            for field in suggested_fields_raw:
                if isinstance(field, str):
                    suggested_fields.append(field)
                elif isinstance(field, dict):
                    # 如果是字典，提取metric_id或field_name
                    metric_id = field.get("metric_id", field.get("field_name", ""))
                    if metric_id:
                        suggested_fields.append(metric_id)
            
            print(f"[LLM Agent Sync] 因果图节点数: {len(causal_graph)}")
            print(f"[LLM Agent Sync] 建议数据字段数: {len(suggested_fields)}")
            
            return CausalGraphDerivationResponse(
                causal_graph=causal_graph,
                reasoning=reasoning,
                suggested_data_fields=suggested_fields,
                required_entities=required_entities
            )
            
        except Exception as e:
            print(f"[LLM Agent Sync] 调用大模型API失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            raise
        
        print(f"[LLM Agent Sync] 因果图推导完成！")
        
        return CausalGraphDerivationResponse(
            causal_graph=causal_graph,
            reasoning=reasoning,
            suggested_data_fields=suggested_fields,
            required_entities=list(causal_graph.keys())
        )
    
    def explain_analysis_results(self, request: AnalysisResultsExplanationRequest) -> AnalysisResultsExplanationResponse:
        """
        同步版本的分析结果解释

        Args:
            request: 分析结果解释请求

        Returns:
            分析结果解释响应
        """
        print(f"[LLM Agent Sync] 正在解释分析结果...")
        
        # 构建提示词
        print(f"[LLM Agent Sync] 正在构建提示词...")
        prompt = self._build_explanation_prompt(
            request.analysis_results,
            request.scenario_description
        )
        
        # 保存提示词
        import os
        from datetime import datetime
        
        prompt_dir = "prompts"
        if not os.path.exists(prompt_dir):
            os.makedirs(prompt_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_file = os.path.join(prompt_dir, f"explanation_prompt_{timestamp}.txt")
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        print(f"[LLM Agent Sync] 提示词已保存到: {prompt_file}")
        
        # 调用LLM API解释分析结果
        print(f"[LLM Agent Sync] 正在调用大模型API解释分析结果...")
        
        import openai
        
        if not self.llm_api_key:
            raise ValueError("LLM API密钥未配置")
        if not self.llm_base_url:
            raise ValueError("LLM Base URL未配置")
        if not self.llm_model:
            raise ValueError("LLM Model未配置")
        
        try:
            client = openai.OpenAI(
                api_key=self.llm_api_key,
                base_url=self.llm_base_url
            )
            
            print(f"[LLM Agent Sync] 调用大模型API...")
            completion = client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            print(f"[LLM Agent Sync] 大模型API调用成功")
            
            response_text = completion.choices[0].message.content
            print(f"[LLM Agent Sync] 响应长度: {len(response_text)} 字符")
            print(f"[LLM Agent Sync] 响应内容前500字符: {response_text[:500]}")
            
            import json
            
            # 去除可能的代码块标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            llm_result = json.loads(response_text)
            
            root_cause_analysis = llm_result.get("root_cause_analysis", "")
            impact_mechanism = llm_result.get("impact_mechanism", "")
            improvement_suggestions = llm_result.get("improvement_suggestions", "")
            expected_effect = llm_result.get("expected_effect", "")
            reasoning = llm_result.get("reasoning", "")
            
            print(f"[LLM Agent Sync] 分析结果解释完成！")
            
            return AnalysisResultsExplanationResponse(
                root_cause_analysis=root_cause_analysis,
                impact_mechanism=impact_mechanism,
                improvement_suggestions=improvement_suggestions,
                expected_effect=expected_effect,
                reasoning=reasoning
            )
            
        except Exception as e:
            print(f"[LLM Agent Sync] 调用大模型API失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            raise
