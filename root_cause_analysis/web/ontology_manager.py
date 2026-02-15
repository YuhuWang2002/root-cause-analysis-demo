"""
本体管理模块

提供本体信息的读取和管理接口，支持：
- 业务实体管理
- 业务关系管理
- 实体属性管理（包含指标属性）
- 数据生成配置
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class OntologyEntity:
    """本体实体类 - 代表现实世界中的业务对象"""
    id: str
    name: str
    type: str  # "factory", "supplier", "metric" 等
    description: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)  # 实体的属性，包括指标属性
    relationships: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class OntologyRelation:
    """本体关系类 - 代表业务实体之间的业务关系"""
    source: str
    target: str
    relation_type: str  # "influences", "causes", "related_to" 等
    weight: float = 1.0
    description: str = ""


@dataclass
class OntologyAttribute:
    """本体属性类 - 定义属性的元信息"""
    name: str
    type: str
    description: str = ""
    default_value: Any = None
    range: Optional[tuple] = None
    enum_values: Optional[List[Any]] = None


class OntologyManager:
    """本体管理器"""
    
    def __init__(self, ontology_file: str = None):
        """
        初始化本体管理器
        
        Args:
            ontology_file: 本体数据文件路径（JSON格式）
        """
        self.ontology_file = ontology_file
        self.entities: Dict[str, OntologyEntity] = {}
        self.relations: List[OntologyRelation] = []
        self.attributes: Dict[str, OntologyAttribute] = {}
        
        if ontology_file:
            self.load_ontology(ontology_file)
    
    def load_ontology(self, ontology_file: str):
        """
        从JSON文件加载本体数据
        
        Args:
            ontology_file: 本体数据文件路径
        """
        try:
            with open(ontology_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载实体
            if 'entities' in data:
                for entity_data in data['entities']:
                    entity = OntologyEntity(
                        id=entity_data['id'],
                        name=entity_data['name'],
                        type=entity_data.get('type', 'default'),
                        description=entity_data.get('description', ''),
                        attributes=entity_data.get('attributes', {}),
                        relationships=entity_data.get('relationships', [])
                    )
                    self.entities[entity.id] = entity
            
            # 加载关系
            if 'relations' in data:
                for rel_data in data['relations']:
                    relation = OntologyRelation(
                        source=rel_data['source'],
                        target=rel_data['target'],
                        relation_type=rel_data.get('type', rel_data.get('relation_type', 'related_to')),
                        weight=rel_data.get('weight', 1.0),
                        description=rel_data.get('description', '')
                    )
                    self.relations.append(relation)
            
            # 加载属性定义
            if 'attributes' in data:
                for attr_data in data['attributes']:
                    attribute = OntologyAttribute(
                        name=attr_data['name'],
                        type=attr_data.get('type', 'string'),
                        description=attr_data.get('description', ''),
                        default_value=attr_data.get('default_value'),
                        range=tuple(attr_data['range']) if 'range' in attr_data else None,
                        enum_values=attr_data.get('enum_values')
                    )
                    self.attributes[attr_data['name']] = attribute
            
            print(f"[Ontology] 成功加载本体: {len(self.entities)} 个实体, {len(self.relations)} 个关系")
            
        except Exception as e:
            print(f"[Ontology] 加载本体失败: {str(e)}")
            raise
    
    def get_entity(self, entity_id: str) -> Optional[OntologyEntity]:
        """
        获取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            实体对象，如果不存在返回None
        """
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: str) -> List[OntologyEntity]:
        """
        按类型获取实体列表
        
        Args:
            entity_type: 实体类型
            
        Returns:
            实体列表
        """
        return [e for e in self.entities.values() if e.type == entity_type]
    
    def get_relations_by_type(self, relation_type: str) -> List[OntologyRelation]:
        """
        按类型获取关系列表
        
        Args:
            relation_type: 关系类型
            
        Returns:
            关系列表
        """
        return [r for r in self.relations if r.relation_type == relation_type]
    
    def get_data_generation_config(self) -> Dict[str, Any]:
        """
        获取数据生成配置
        
        Returns:
            数据生成配置字典
        """
        config = {
            'entities': [],
            'relations': [],
            'attributes': {}
        }
        
        for entity in self.entities.values():
            config['entities'].append({
                'id': entity.id,
                'name': entity.name,
                'type': entity.type,
                'attributes': entity.attributes
            })
        
        for relation in self.relations:
            config['relations'].append({
                'source': relation.source,
                'target': relation.target,
                'type': relation.relation_type,
                'weight': relation.weight
            })
        
        config['attributes'] = {
            name: {
                'type': attr.type,
                'default_value': attr.default_value,
                'range': attr.range,
                'enum_values': attr.enum_values
            }
            for name, attr in self.attributes.items()
        }
        
        return config
    
    def get_ontology_description(self) -> str:
        """
        获取本体描述（用于大模型提示词）
        
        Returns:
            本体描述文本
        """
        description_lines = []
        
        description_lines.append("## 业务本体结构\n")
        description_lines.append("### 实体列表\n")
        
        for entity in self.entities.values():
            description_lines.append(f"- **{entity.name}** ({entity.id}, 类型: {entity.type})")
            if entity.description:
                description_lines.append(f"  - 描述: {entity.description}")
            if entity.attributes:
                description_lines.append(f"  - 属性:")
                for attr_name, attr_value in entity.attributes.items():
                    description_lines.append(f"    - {attr_name}: {attr_value}")
        
        description_lines.append("\n### 业务关系\n")
        
        for relation in self.relations:
            source_entity = self.get_entity(relation.source)
            target_entity = self.get_entity(relation.target)
            
            if source_entity and target_entity:
                description_lines.append(
                    f"- {source_entity.name} → {relation.relation_type} → {target_entity.name}"
                )
                if relation.description:
                    description_lines.append(f"  - 描述: {relation.description}")
        
        return "\n".join(description_lines)
    
    def save_ontology(self, output_file: str):
        """
        保存本体到JSON文件
        
        Args:
            output_file: 输出文件路径
        """
        data = {
            'entities': [
                {
                    'id': e.id,
                    'name': e.name,
                    'type': e.type,
                    'description': e.description,
                    'attributes': e.attributes,
                    'relationships': e.relationships
                }
                for e in self.entities.values()
            ],
            'relations': [
                {
                    'source': r.source,
                    'target': r.target,
                    'type': r.relation_type,
                    'weight': r.weight,
                    'description': r.description
                }
                for r in self.relations
            ],
            'attributes': [
                {
                    'name': a.name,
                    'type': a.type,
                    'description': a.description,
                    'default_value': a.default_value,
                    'range': a.range,
                    'enum_values': a.enum_values
                }
                for a in self.attributes.values()
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[Ontology] 本体已保存到: {output_file}")


def create_manufacturing_ontology() -> OntologyManager:
    """
    创建制造企业场景的本体Schema（元数据）
    只定义实体类型、关系类型、属性类型，不包含具体实体实例
    
    Agent读取这个schema后，可以根据业务场景推断因果关系
    
    Returns:
        本体管理器实例
    """
    ontology_data = {
        "entity_types": [
            {
                "id": "factory",
                "name": "工厂",
                "description": "制造企业中的生产工厂",
                "attributes": [
                    {
                        "name": "capacity",
                        "type": "integer",
                        "description": "工厂产能"
                    },
                    {
                        "name": "equipment_age",
                        "type": "integer",
                        "description": "设备使用年限"
                    },
                    {
                        "name": "location",
                        "type": "string",
                        "description": "工厂位置"
                    }
                ]
            },
            {
                "id": "supplier",
                "name": "供应商",
                "description": "提供零部件的供应商",
                "attributes": [
                    {
                        "name": "base_efficiency",
                        "type": "float",
                        "description": "基础效率"
                    },
                    {
                        "name": "location",
                        "type": "string",
                        "description": "供应商位置"
                    }
                ]
            },
            {
                "id": "employee",
                "name": "员工",
                "description": "工厂员工",
                "attributes": [
                    {
                        "name": "skill_level",
                        "type": "float",
                        "description": "技能水平"
                    },
                    {
                        "name": "experience_years",
                        "type": "integer",
                        "description": "工作年限"
                    },
                    {
                        "name": "team_size",
                        "type": "integer",
                        "description": "团队规模"
                    }
                ]
            },
            {
                "id": "product",
                "name": "产品",
                "description": "工厂生产的产品",
                "attributes": [
                    {
                        "name": "complexity",
                        "type": "string",
                        "description": "产品复杂度"
                    },
                    {
                        "name": "target_efficiency",
                        "type": "float",
                        "description": "目标效率"
                    }
                ]
            },
            {
                "id": "part",
                "name": "零部件",
                "description": "产品所需的零部件",
                "attributes": [
                    {
                        "name": "criticality",
                        "type": "string",
                        "description": "关键程度"
                    },
                    {
                        "name": "lead_time",
                        "type": "integer",
                        "description": "交货周期"
                    }
                ]
            }
        ],
        "relation_types": [
            {
                "id": "contains",
                "name": "包含",
                "description": "实体包含关系（工厂包含员工、产品包含零部件）",
                "source_types": ["factory", "product"],
                "target_types": ["employee", "part"]
            },
            {
                "id": "supplies",
                "name": "供货",
                "description": "供应商向工厂供货",
                "source_types": ["supplier"],
                "target_types": ["factory"]
            },
            {
                "id": "provides",
                "name": "提供",
                "description": "供应商提供零部件",
                "source_types": ["supplier"],
                "target_types": ["part"]
            },
            {
                "id": "produces",
                "name": "生产",
                "description": "工厂生产产品",
                "source_types": ["factory"],
                "target_types": ["product"]
            }
        ],
        "metric_definitions": [
            {
                "id": "payment_timeliness",
                "name": "付款及时性",
                "description": "企业向供应商付款的及时程度",
                "source_relation": "supplies",
                "source_entity_type": "factory",
                "target_entity_type": "supplier"
            },
            {
                "id": "supplier_efficiency",
                "name": "供应商效率",
                "description": "供应商的生产和交付效率",
                "source_entity_type": "supplier"
            },
            {
                "id": "parts_availability",
                "name": "零部件可用性",
                "description": "零部件的供应及时性和充足性",
                "source_relation": "provides",
                "source_entity_type": "supplier",
                "target_entity_type": "part"
            },
            {
                "id": "avg_employee_skill",
                "name": "员工技能水平",
                "description": "员工的平均技能熟练度",
                "source_entity_type": "employee"
            },
            {
                "id": "equipment_status",
                "name": "设备状态",
                "description": "生产设备的运行状态",
                "source_entity_type": "factory"
            },
            {
                "id": "capacity_utilization",
                "name": "产能利用率",
                "description": "工厂产能的利用程度",
                "source_entity_type": "factory"
            },
            {
                "id": "production_efficiency",
                "name": "生产效率",
                "description": "企业的整体生产效率",
                "type": "outcome",
                "source_entity_type": "factory"
            }
        ]
    }
    
    manager = OntologyManager()
    manager.schema = ontology_data
    
    return manager


def save_ontology_schema(manager: OntologyManager, output_file: str = "web/ontology_schema.json"):
    """
    保存本体Schema到JSON文件
    
    Args:
        manager: 本体管理器实例
        output_file: 输出文件路径
    """
    import json
    from datetime import datetime
    
    schema_data = {
        "entity_types": manager.schema.get("entity_types", []),
        "relation_types": manager.schema.get("relation_types", []),
        "metric_definitions": manager.schema.get("metric_definitions", []),
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "description": "制造企业业务本体Schema"
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(schema_data, f, ensure_ascii=False, indent=2)
    
    print(f"[Ontology] Schema已保存到: {output_file}")


def load_ontology_schema(schema_file: str) -> dict:
    """
    从文件加载本体Schema
    
    Args:
        schema_file: Schema文件路径
        
    Returns:
        Schema字典
    """
    import json
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    print(f"[Ontology] Schema已从 {schema_file} 加载")
    return schema


def load_ontology_from_file(ontology_file: str) -> OntologyManager:
    """
    从文件加载本体
    
    Args:
        ontology_file: 本体文件路径
        
    Returns:
        本体管理器实例
    """
    return OntologyManager(ontology_file)