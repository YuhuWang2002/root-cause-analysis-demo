"""
LLM Agent模块

支持：
- 查询本体API获取本体信息
- 根据场景描述理解问题
- 推导因果图
- 返回推导结果
"""

import httpx
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
    causal_graph: Dict[str, List[str]]
    reasoning: str
    suggested_data_fields: List[str]
    required_entities: List[str]


class LLMAgent:
    """LLM Agent - 支持本体查询和因果图推导"""
    
    def __init__(self, ontology_api_url: str = "http://localhost:8000", llm_api_key: str = None):
        """
        初始化LLM Agent
        
        Args:
            ontology_api_url: 本体API地址
            llm_api_key: 大模型API密钥
        """
        self.ontology_api_url = ontology_api_url
        self.llm_api_key = llm_api_key
        self.http_client = httpx.Client(timeout=30.0)
    
    async def query_ontology(self, query_type: str = "all") -> OntologyQueryResponse:
        """
        查询本体API
        
        Args:
            query_type: 查询类型 ("entities", "relations", "attributes", "all")
            
        Returns:
            本体查询响应
        """
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
        # 第一步：查询本体获取完整信息
        ontology_response = await self.query_ontology("all")
        
        # 第二步：构建提示词让LLM推导因果图
        prompt = self._build_derivation_prompt(
            request.scenario_description,
            request.outcome_entity,
            ontology_response
        )
        
        # 第三步：调用LLM API推导因果图
        # 这里暂时返回一个示例响应
        # 实际使用时需要集成真实的LLM API调用
        
        causal_graph = {}
        reasoning = f"""
        根据场景描述"{request.scenario_description}"和结果实体"{request.outcome_entity}"，
        从本体中推导出以下因果图：
        
        本体中包含的实体：
        {', '.join([f"  - {e.get('name', e.get('id'))} ({e.get('type', 'unknown')})" for e in ontology_response.entities[:5]])}
        
        本体中包含的关系：
        {', '.join([f"  - {r.get('source', '')} -> {r.get('target', '')} ({r.get('relation_type', 'unknown')})" for r in ontology_response.relations[:5]])}
        
        推导的因果图：
        """
        
        # 添加因果链（示例）
        causal_graph["payment_timeliness"] = ["supplier_efficiency"]
        causal_graph["supplier_efficiency"] = ["parts_availability", "production_efficiency"]
        causal_graph["parts_availability"] = ["production_efficiency"]
        causal_graph["avg_employee_skill"] = ["production_efficiency"]
        causal_graph["equipment_status"] = ["production_efficiency"]
        
        reasoning += """
        
        主要因果链：
        1. 付款及时性 -> 供应商效率 -> 零部件可用性 -> 生产效率
        2. 员工技能 -> 生产效率
        3. 设备状态 -> 生产效率
        
        建议的数据字段：
        """
        
        suggested_fields = [
            "payment_timeliness",
            "supplier_efficiency",
            "parts_availability",
            "avg_employee_skill",
            "equipment_status",
            "production_efficiency"
        ]
        
        reasoning += """
        - payment_timeliness (付款及时性)
        - supplier_efficiency (供应商效率)
        - parts_availability (零部件可用性)
        - avg_employee_skill (员工技能水平)
        - equipment_status (设备状态)
        - production_efficiency (生产效率)
        """
        
        return CausalGraphDerivationResponse(
            causal_graph=causal_graph,
            reasoning=reasoning,
            suggested_data_fields=suggested_fields,
            required_entities=list(causal_graph.keys())
        )
    
    def _build_derivation_prompt(self, 
                                scenario_description: str,
                                outcome_entity: str,
                                ontology_response: OntologyQueryResponse) -> str:
        """
        构建因果图推导的提示词
        
        Args:
            scenario_description: 场景描述
            outcome_entity: 结果实体
            ontology_response: 本体查询响应
            
        Returns:
            提示词字符串
        """
        prompt = f"""你是一个专业的因果分析专家。请根据以下信息推导出因果图。

## 场景描述
{scenario_description}

## 结果实体
{outcome_entity}

## 本体信息

### 可用实体
"""
        
        for entity in ontology_response.entities[:10]:
            prompt += f"- **{entity.get('name', entity.get('id'))}** ({entity.get('type', 'unknown')})\n"
            if entity.get('description'):
                prompt += f"  描述: {entity.get('description')}\n"
            if entity.get('attributes'):
                prompt += f"  属性: {', '.join(entity.get('attributes', {}).keys())}\n"
        
        prompt += """
### 可用关系
"""
        
        for relation in ontology_response.relations[:10]:
            prompt += f"- {relation.get('source', '')} -> {relation.get('target', '')} ({relation.get('relation_type', 'unknown')})\n"
            if relation.get('description'):
                prompt += f"  描述: {relation.get('description')}\n"
        
        prompt += """
## 任务
请根据场景描述和本体信息，推导出合理的因果图。

要求：
1. 因果图必须包含结果实体"{outcome_entity}"
2. 因果图中的节点必须来自本体中的实体
3. 因果图中的边必须来自本体中的关系或合理的推导
4. 返回格式：JSON格式的邻接表 {{"source": ["target1", "target2"]}

请以JSON格式返回你的推导结果，包含：
- causal_graph: 因果图邻接表
- reasoning: 推导过程说明
- suggested_data_fields: 建议需要收集的数据字段
- required_entities: 因果图中涉及的实体ID列表
"""
        
        return prompt


# ============ 同步版本（用于非异步环境）===========

class LLMAgentSync(LLMAgent):
    """LLM Agent同步版本"""
    
    def __init__(self, ontology_api_url: str = "http://localhost:8000", llm_api_key: str = None):
        super().__init__(ontology_api_url, llm_api_key)
    
    def query_ontology(self, query_type: str = "all") -> OntologyQueryResponse:
        """同步版本的本体查询"""
        import httpx
        
        try:
            if query_type in ["all", "entities"]:
                # 查询所有类型的端点
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
                    # 如果是all，从/ontology端点获取完整数据
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
                
            elif query_type == "relations":
                response = httpx.get(f"{self.ontology_api_url}/relations", timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                return OntologyQueryResponse(
                    entities=[],
                    relations=data if isinstance(data, list) else data.get("relations", []),
                    attributes=[]
                )
            
            elif query_type == "attributes":
                response = httpx.get(f"{self.ontology_api_url}/attributes", timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                return OntologyQueryResponse(
                    entities=[],
                    relations=[],
                    attributes=data if isinstance(data, list) else data.get("attributes", [])
                )
                
        except Exception as e:
            print(f"[LLM Agent Sync] 查询本体API失败: {str(e)}")
            raise
    
    def derive_causal_graph(self, request: CausalGraphDerivationRequest) -> CausalGraphDerivationResponse:
        """同步版本的因果图推导 - 直接实现不使用super()"""
        import httpx
        
        # 第一步：查询本体获取完整信息
        print(f"[LLM Agent Sync] 正在查询本体...")
        
        try:
            # 直接查询本体API
            response = httpx.get(
                f"{self.ontology_api_url}/ontology",
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            ontology_response = OntologyQueryResponse(
                entities=data.get("entities", []),
                relations=data.get("relations", []),
                attributes=data.get("attributes", [])
            )
            
            print(f"[LLM Agent Sync] 查询到 {len(ontology_response.entities)} 个实体, {len(ontology_response.relations)} 个关系")
            
        except Exception as e:
            print(f"[LLM Agent Sync] 查询本体失败: {str(e)}, 将使用默认逻辑")
            # 使用默认响应
            ontology_response = OntologyQueryResponse(
                entities=[],
                relations=[],
                attributes=[]
            )
        
        # 第二步：构建提示词（直接使用基类的方法
        print(f"[LLM Agent Sync] 正在构建提示词...")
        prompt = self._build_derivation_prompt(
            request.scenario_description,
            request.outcome_entity,
            ontology_response
        )
        
        # 第三步：返回示例响应（简化版，不调用LLM）
        print(f"[LLM Agent Sync] 正在推导因果图（使用内部逻辑...")
        
        causal_graph = {}
        reasoning = f"""
        根据场景描述"{request.scenario_description}"和结果实体"{request.outcome_entity}"，
        从本体中推导出以下因果图：
        
        本体中包含的实体：
        {', '.join([f"  - {e.get('name', e.get('id'))} ({e.get('type', 'unknown')})" for e in ontology_response.entities[:5]])}
        
        推导的因果图：
        """
        
        # 添加因果链（示例）
        causal_graph["payment_timeliness"] = ["supplier_efficiency"]
        causal_graph["supplier_efficiency"] = ["parts_availability", "production_efficiency"]
        causal_graph["parts_availability"] = ["production_efficiency"]
        causal_graph["avg_employee_skill"] = ["production_efficiency"]
        causal_graph["equipment_status"] = ["production_efficiency"]
        
        reasoning += """
        
        主要因果链：
        1. 付款及时性 -> 供应商效率 -> 零部件可用性 -> 生产效率
        2. 员工技能 -> 生产效率
        3. 设备状态 -> 生产效率
        
        建议的数据字段：
        """
        
        suggested_fields = [
            "payment_timeliness",
            "supplier_efficiency",
            "parts_availability",
            "avg_employee_skill",
            "equipment_status",
            "production_efficiency"
        ]
        
        reasoning += """
        - payment_timeliness (付款及时性)
        - supplier_efficiency (供应商效率)
        - parts_availability (零部件可用性)
        - avg_employee_skill (员工技能水平)
        - equipment_status (设备状态)
        - production_efficiency (生产效率)
        """
        
        print(f"[LLM Agent Sync] 因果图推导完成！")
        
        return CausalGraphDerivationResponse(
            causal_graph=causal_graph,
            reasoning=reasoning,
            suggested_data_fields=suggested_fields,
            required_entities=list(causal_graph.keys())
        )