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

from ontology_manager import OntologyManager, load_ontology_schema

# 初始化FastAPI应用
app = FastAPI(
    title="本体管理API",
    description="提供本体Schema的REST API接口",
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

# 初始化本体管理器（加载Schema）
import os
schema_path = os.path.join(os.path.dirname(__file__), "../ontology_schema.json")
schema_data = load_ontology_schema(schema_path)
ontology_manager = OntologyManager()
ontology_manager.schema = schema_data


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


class SchemaResponse(BaseModel):
    """Schema响应"""
    entity_types: List[Dict[str, Any]]
    relation_types: List[Dict[str, Any]]
    metric_definitions: List[Dict[str, Any]]
    metadata: Dict[str, Any]


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
            "GET /": "API根路径",
            "GET /schema": "获取本体Schema（元数据）",
            "GET /entities": "获取所有实体（当前为空，只有Schema）",
            "GET /entities/{entity_type}": "按类型获取实体（当前为空）",
            "GET /entities/{entity_id}": "获取单个实体（当前为空）",
            "GET /relations": "获取所有关系（当前为空）",
            "GET /attributes": "获取所有属性（当前为空）",
            "GET /ontology": "获取完整本体信息（当前为空）"
        }
    }


@app.get("/schema", response_model=SchemaResponse, tags=["Schema管理"])
async def get_schema():
    """获取本体Schema（元数据）"""
    schema_data = ontology_manager.schema
    
    entity_types = [
        {
            "id": et["id"],
            "name": et["name"],
            "description": et["description"],
            "attributes": et["attributes"]
        }
        for et in schema_data.get("entity_types", [])
    ]
    
    relation_types = [
        {
            "id": rt["id"],
            "name": rt["name"],
            "description": rt["description"],
            "source_types": rt.get("source_types", []),
            "target_types": rt.get("target_types", [])
        }
        for rt in schema_data.get("relation_types", [])
    ]
    
    metric_definitions = [
        {
            "id": md["id"],
            "name": md["name"],
            "description": md["description"],
            "source_entity_type": md.get("source_entity_type"),
            "target_entity_type": md.get("target_entity_type"),
            "source_relation": md.get("source_relation"),
            "type": md.get("type")
        }
        for md in schema_data.get("metric_definitions", [])
    ]
    
    metadata = schema_data.get("metadata", {})
    
    return SchemaResponse(
        entity_types=entity_types,
        relation_types=relation_types,
        metric_definitions=metric_definitions,
        metadata=metadata
    )


@app.get("/entities", response_model=List[EntityResponse], tags=["实体管理"])
async def get_entities():
    """获取所有实体（当前为空，只有Schema）"""
    return []


@app.get("/entities/{entity_type}", response_model=List[EntityResponse], tags=["实体管理"])
async def get_entities_by_type(entity_type: str):
    """按类型获取实体（当前为空，只有Schema）"""
    return []


@app.get("/entities/{entity_id}", response_model=EntityResponse, tags=["实体管理"])
async def get_entity(entity_id: str):
    """获取单个实体（当前为空，只有Schema）"""
    raise HTTPException(status_code=404, detail=f"当前只有Schema，没有实体实例。实体 {entity_id} 不存在")


@app.get("/relations", response_model=List[RelationResponse], tags=["关系管理"])
async def get_relations():
    """获取所有关系（当前为空，只有Schema）"""
    return []


@app.get("/attributes", response_model=List[AttributeResponse], tags=["属性管理"])
async def get_attributes():
    """获取所有属性（当前为空，只有Schema）"""
    return []


@app.get("/ontology", response_model=OntologyInfoResponse, tags=["本体管理"])
async def get_ontology_info():
    """获取完整本体信息（当前为空，只有Schema）"""
    return OntologyInfoResponse(
        entities=[],
        relations=[],
        attributes=[],
        description="当前只有Schema元数据，没有实体实例。请使用 GET /schema 获取Schema"
    )


@app.get("/schema/server", response_model=SchemaResponse, tags=["Schema管理"])
async def get_server_schema():
    """获取服务器库存分析本体Schema（元数据）"""
    server_schema_path = os.path.join(os.path.dirname(__file__), "../server_ontology_schema.json")
    server_schema_data = load_ontology_schema(server_schema_path)
    
    entity_types = [
        {
            "id": et["id"],
            "name": et["name"],
            "description": et["description"],
            "attributes": et["attributes"]
        }
        for et in server_schema_data.get("entity_types", [])
    ]
    
    relation_types = [
        {
            "id": rt["id"],
            "name": rt["name"],
            "description": rt["description"],
            "source_types": rt.get("source_types", []),
            "target_types": rt.get("target_types", [])
        }
        for rt in server_schema_data.get("relation_types", [])
    ]
    
    metric_definitions = [
        {
            "id": md["id"],
            "name": md["name"],
            "description": md["description"],
            "source_entity_type": md.get("source_entity_type"),
            "target_entity_type": md.get("target_entity_type"),
            "source_relation": md.get("source_relation"),
            "type": md.get("type")
        }
        for md in server_schema_data.get("metric_definitions", [])
    ]
    
    metadata = server_schema_data.get("metadata", {})
    
    return SchemaResponse(
        entity_types=entity_types,
        relation_types=relation_types,
        metric_definitions=metric_definitions,
        metadata=metadata
    )


if __name__ == "__main__":
    import uvicorn
    
    print("启动本体API服务器...")
    print(f"本体文件: ontology_schema.json")
    print(f"实体数量: {len(ontology_manager.entities)}")
    print(f"关系数量: {len(ontology_manager.relations)}")
    
    uvicorn.run(
        "ontology_api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )