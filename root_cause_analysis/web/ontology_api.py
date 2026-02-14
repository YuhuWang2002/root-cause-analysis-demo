"""
本体API接口

提供本体的REST API接口，支持：
- 查询本体实体
- 查询本体关系
- 查询本体属性
- 获取本体完整信息
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn

from ontology_manager import OntologyManager, load_ontology_from_file

# 初始化FastAPI应用
app = FastAPI(
    title="本体管理API",
    description="提供本体信息的REST API接口",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化本体管理器
ontology_manager = load_ontology_from_file("ontology.json")


# ============ 数据模型 ============

class EntityResponse(BaseModel):
    """实体响应"""
    id: str
    name: str
    type: str
    description: str
    attributes: Dict[str, Any]


class RelationResponse(BaseModel):
    """关系响应"""
    source: str
    target: str
    relation_type: str
    weight: float
    description: str


class AttributeResponse(BaseModel):
    """属性响应"""
    name: str
    type: str
    description: str
    default_value: Any
    range: Optional[List[float]] = None
    enum_values: Optional[List[Any]] = None


class OntologyInfoResponse(BaseModel):
    """本体信息响应"""
    entities: List[EntityResponse]
    relations: List[RelationResponse]
    attributes: List[AttributeResponse]
    description: str


class CausalGraphRequest(BaseModel):
    """因果图推导请求"""
    scenario_description: str
    outcome_entity: str


class CausalGraphResponse(BaseModel):
    """因果图推导响应"""
    causal_graph: Dict[str, List[str]]
    reasoning: str
    suggested_data_fields: List[str]


# ============ API端点 ============

@app.get("/", tags=["健康检查"])
async def root():
    """根路径"""
    return {
        "message": "本体管理API",
        "version": "1.0.0",
        "endpoints": {
            "GET /entities": "获取所有实体",
            "GET /entities/{entity_type}": "按类型获取实体",
            "GET /entities/{entity_id}": "获取单个实体",
            "GET /relations": "获取所有关系",
            "GET /attributes": "获取所有属性",
            "GET /ontology": "获取完整本体信息",
            "POST /derive-causal-graph": "推导因果图"
        }
    }


@app.get("/entities", response_model=List[EntityResponse], tags=["实体管理"])
async def get_entities():
    """获取所有实体"""
    entities = []
    for entity in ontology_manager.entities.values():
        entities.append(EntityResponse(
            id=entity.id,
            name=entity.name,
            type=entity.type,
            description=entity.description,
            attributes=entity.attributes
        ))
    return entities


@app.get("/entities/{entity_type}", response_model=List[EntityResponse], tags=["实体管理"])
async def get_entities_by_type(entity_type: str):
    """按类型获取实体"""
    entities = []
    for entity in ontology_manager.get_entities_by_type(entity_type):
        entities.append(EntityResponse(
            id=entity.id,
            name=entity.name,
            type=entity.type,
            description=entity.description,
            attributes=entity.attributes
        ))
    return entities


@app.get("/entities/{entity_id}", response_model=EntityResponse, tags=["实体管理"])
async def get_entity(entity_id: str):
    """获取单个实体"""
    entity = ontology_manager.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"实体 {entity_id} 不存在")
    
    return EntityResponse(
        id=entity.id,
        name=entity.name,
        type=entity.type,
        description=entity.description,
        attributes=entity.attributes
    )


@app.get("/relations", response_model=List[RelationResponse], tags=["关系管理"])
async def get_relations():
    """获取所有关系"""
    relations = []
    for relation in ontology_manager.relations:
        relations.append(RelationResponse(
            source=relation.source,
            target=relation.target,
            relation_type=relation.relation_type,
            weight=relation.weight,
            description=relation.description
        ))
    return relations


@app.get("/attributes", response_model=List[AttributeResponse], tags=["属性管理"])
async def get_attributes():
    """获取所有属性"""
    attributes = []
    for attr in ontology_manager.attributes.values():
        attributes.append(AttributeResponse(
            name=attr.name,
            type=attr.type,
            description=attr.description,
            default_value=attr.default_value,
            range=list(attr.range) if attr.range else None,
            enum_values=attr.enum_values
        ))
    return attributes


@app.get("/ontology", response_model=OntologyInfoResponse, tags=["本体管理"])
async def get_ontology_info():
    """获取完整本体信息"""
    entities = []
    for entity in ontology_manager.entities.values():
        entities.append(EntityResponse(
            id=entity.id,
            name=entity.name,
            type=entity.type,
            description=entity.description,
            attributes=entity.attributes
        ))
    
    relations = []
    for relation in ontology_manager.relations:
        relations.append(RelationResponse(
            source=relation.source,
            target=relation.target,
            relation_type=relation.relation_type,
            weight=relation.weight,
            description=relation.description
        ))
    
    attributes = []
    for attr in ontology_manager.attributes.values():
        attributes.append(AttributeResponse(
            name=attr.name,
            type=attr.type,
            description=attr.description,
            default_value=attr.default_value,
            range=list(attr.range) if attr.range else None,
            enum_values=attr.enum_values
        ))
    
    return OntologyInfoResponse(
        entities=entities,
        relations=relations,
        attributes=attributes,
        description=f"当前本体包含 {len(entities)} 个实体，{len(relations)} 个关系，{len(attributes)} 个属性"
    )


@app.post("/derive-causal-graph", response_model=CausalGraphResponse, tags=["因果图推导"])
async def derive_causal_graph(request: CausalGraphRequest):
    """
    推导因果图
    
    这个端点需要LLM来理解场景并推导因果图
    返回推导的因果图和相关推理
    """
    # 这里暂时返回一个示例响应
    # 实际使用时，需要集成LLM来推导
    
    outcome_entity = request.outcome_entity
    
    # 从本体获取与结果相关的实体
    causal_graph = ontology_manager.get_causal_graph()
    
    # 获取结果实体的信息
    outcome_entity_info = ontology_manager.get_entity(outcome_entity)
    
    # 建议的数据字段（从因果图中的实体推导）
    suggested_fields = []
    for entity_id in causal_graph.keys():
        entity = ontology_manager.get_entity(entity_id)
        if entity:
            suggested_fields.append(entity.id)
    
    reasoning = f"""
    根据场景描述"{request.scenario_description}"和结果实体"{outcome_entity}"，
    从本体中推导出以下因果图：
    
    主要因果链：
    """
    
    # 添加因果链描述
    causal_chains = []
    for entity_id in causal_graph.keys():
        if entity_id in causal_graph and len(causal_graph[entity_id]) > 0:
            chain = [entity_id]
            for target in causal_graph[entity_id]:
                if target == outcome_entity:
                    chain.append(target)
                    causal_chains.append(" -> ".join([ontology_manager.get_entity(e).name if ontology_manager.get_entity(e) else e for e in chain]))
                    break
    
    if causal_chains:
        reasoning += "\n".join([f"  - {chain}" for chain in causal_chains])
    else:
        reasoning += "  （未找到直接因果链）"
    
    return CausalGraphResponse(
        causal_graph=causal_graph,
        reasoning=reasoning,
        suggested_data_fields=suggested_fields
    )


if __name__ == "__main__":
    import uvicorn
    
    print("启动本体API服务器...")
    print(f"本体文件: ontology.json")
    print(f"实体数量: {len(ontology_manager.entities)}")
    print(f"关系数量: {len(ontology_manager.relations)}")
    
    uvicorn.run(
        "ontology_api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )