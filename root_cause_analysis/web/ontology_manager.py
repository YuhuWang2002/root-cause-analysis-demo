"""
本体管理模块

提供本体信息的读取和管理接口，支持：
- 本体对象（实体）管理
- 本体属性管理
- 本体关系管理
- 因果图构建
- 数据生成配置
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class OntologyEntity:
    """本体实体类"""
    id: str
    name: str
    type: str
    description: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class OntologyRelation:
    """本体关系类"""
    source: str
    target: str
    relation_type: str
    weight: float = 1.0
    description: str = ""


@dataclass
class OntologyAttribute:
    """本体属性类"""
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
        self.causal_graph: Dict[str, List[str]] = {}
        
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
                        relation_type=rel_data.get('type', 'causes'),
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
            
            # 构建因果图
            self._build_causal_graph()
            
            print(f"[Ontology] 成功加载本体: {len(self.entities)} 个实体, {len(self.relations)} 个关系")
            
        except Exception as e:
            print(f"[Ontology] 加载本体失败: {str(e)}")
            raise
    
    def _build_causal_graph(self):
        """构建因果图（邻接表）"""
        self.causal_graph = {}
        
        for relation in self.relations:
            if relation.relation_type == 'causes':
                if relation.source not in self.causal_graph:
                    self.causal_graph[relation.source] = []
                self.causal_graph[relation.source].append(relation.target)
    
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
    
    def get_causal_graph(self) -> Dict[str, List[str]]:
        """
        获取因果图
        
        Returns:
            因果图邻接表 {source: [targets]}
        """
        return self.causal_graph
    
    def get_causal_chain(self, start_entity: str, end_entity: str) -> List[str]:
        """
        获取两个实体之间的因果链
        
        Args:
            start_entity: 起始实体
            end_entity: 结束实体
            
        Returns:
            因果链路径（实体ID列表）
        """
        # 使用BFS查找最短路径
        from collections import deque
        
        queue = deque([(start_entity, [start_entity])])
        visited = {start_entity}
        
        while queue:
            current, path = queue.popleft()
            
            if current == end_entity:
                return path
            
            if current in self.causal_graph:
                for neighbor in self.causal_graph[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
        
        return []
    
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
        
        description_lines.append("## 本体结构\n")
        description_lines.append("### 实体列表\n")
        
        for entity in self.entities.values():
            description_lines.append(f"- **{entity.name}** ({entity.id})")
            description_lines.append(f"  - 类型: {entity.type}")
            if entity.description:
                description_lines.append(f"  - 描述: {entity.description}")
            if entity.attributes:
                description_lines.append(f"  - 属性: {', '.join(entity.attributes.keys())}")
        
        description_lines.append("\n### 因果关系\n")
        
        for relation in self.relations:
            source_entity = self.get_entity(relation.source)
            target_entity = self.get_entity(relation.target)
            
            if source_entity and target_entity:
                description_lines.append(
                    f"- {source_entity.name} → {target_entity.name}"
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
    创建制造企业场景的本体
    
    Returns:
        本体管理器实例
    """
    ontology_data = {
        "entities": [
            {
                "id": "payment_timeliness",
                "name": "付款及时性",
                "type": "metric",
                "description": "企业向供应商付款的及时程度",
                "attributes": {
                    "base_value": 0.85,
                    "variance": 0.1
                }
            },
            {
                "id": "supplier_efficiency",
                "name": "供应商效率",
                "type": "metric",
                "description": "供应商的生产和交付效率",
                "attributes": {
                    "base_value": 0.80,
                    "variance": 0.15
                }
            },
            {
                "id": "parts_availability",
                "name": "零部件可用性",
                "type": "metric",
                "description": "零部件的供应及时性和充足性",
                "attributes": {
                    "base_value": 0.85,
                    "variance": 0.1
                }
            },
            {
                "id": "production_efficiency",
                "name": "生产效率",
                "type": "outcome",
                "description": "企业的整体生产效率",
                "attributes": {
                    "target_value": 0.85,
                    "acceptable_range": [0.75, 0.95]
                }
            },
            {
                "id": "avg_employee_skill",
                "name": "员工技能水平",
                "type": "metric",
                "description": "员工的平均技能熟练度",
                "attributes": {
                    "base_value": 0.70,
                    "variance": 0.15
                }
            },
            {
                "id": "equipment_status",
                "name": "设备状态",
                "type": "metric",
                "description": "生产设备的运行状态",
                "attributes": {
                    "base_value": 0.85,
                    "variance": 0.1
                }
            },
            {
                "id": "capacity_utilization",
                "name": "产能利用率",
                "type": "metric",
                "description": "工厂产能的利用程度",
                "attributes": {
                    "base_value": 0.80,
                    "variance": 0.15
                }
            },
            {
                "id": "supplier_base_efficiency",
                "name": "供应商基础效率",
                "type": "factor",
                "description": "供应商的基础生产能力",
                "attributes": {
                    "base_value": 0.85,
                    "variance": 0.1
                }
            },
            {
                "id": "equipment_age",
                "name": "设备年龄",
                "type": "factor",
                "description": "设备的使用年限",
                "attributes": {
                    "base_value": 3.0,
                    "variance": 2.0
                }
            },
            {
                "id": "factory_capacity",
                "name": "工厂产能",
                "type": "factor",
                "description": "工厂的设计产能",
                "attributes": {
                    "base_value": 1000,
                    "variance": 200
                }
            }
        ],
        "relations": [
            {
                "source": "payment_timeliness",
                "target": "supplier_efficiency",
                "type": "causes",
                "weight": 1.0,
                "description": "付款不及时会降低供应商的生产积极性"
            },
            {
                "source": "supplier_efficiency",
                "target": "parts_availability",
                "type": "causes",
                "weight": 1.0,
                "description": "供应商效率低会导致零部件供应不足"
            },
            {
                "source": "parts_availability",
                "target": "production_efficiency",
                "type": "causes",
                "weight": 1.0,
                "description": "零部件不足直接影响生产效率"
            },
            {
                "source": "avg_employee_skill",
                "target": "production_efficiency",
                "type": "causes",
                "weight": 1.0,
                "description": "员工技能水平直接影响生产效率"
            },
            {
                "source": "equipment_status",
                "target": "production_efficiency",
                "type": "causes",
                "weight": 1.0,
                "description": "设备状态影响生产能力"
            },
            {
                "source": "capacity_utilization",
                "target": "production_efficiency",
                "type": "causes",
                "weight": 1.0,
                "description": "产能利用率影响整体效率"
            },
            {
                "source": "supplier_efficiency",
                "target": "production_efficiency",
                "type": "causes",
                "weight": 0.5,
                "description": "供应商效率也直接影响生产效率"
            },
            {
                "source": "payment_timeliness",
                "target": "production_efficiency",
                "type": "causes",
                "weight": 0.3,
                "description": "付款及时性对生产效率有间接影响"
            },
            {
                "source": "supplier_base_efficiency",
                "target": "supplier_efficiency",
                "type": "causes",
                "weight": 1.0,
                "description": "供应商基础效率决定其整体效率"
            },
            {
                "source": "equipment_age",
                "target": "equipment_status",
                "type": "causes",
                "weight": 1.0,
                "description": "设备年龄影响设备状态"
            },
            {
                "source": "factory_capacity",
                "target": "capacity_utilization",
                "type": "causes",
                "weight": 1.0,
                "description": "工厂产能影响产能利用率"
            },
            {
                "source": "factory_capacity",
                "target": "production_efficiency",
                "type": "causes",
                "weight": 0.5,
                "description": "工厂产能也直接影响生产效率"
            }
        ],
        "attributes": [
            {
                "name": "payment_delay_days",
                "type": "float",
                "description": "付款延迟天数",
                "default_value": 0.0,
                "range": [0.0, 30.0]
            },
            {
                "name": "skill_level",
                "type": "string",
                "description": "员工技能等级",
                "default_value": "中级",
                "enum_values": ["初级", "中级", "高级", "专家"]
            },
            {
                "name": "equipment_failure",
                "type": "boolean",
                "description": "设备是否故障",
                "default_value": False
            },
            {
                "name": "is_anomaly_month",
                "type": "boolean",
                "description": "是否为异常月份",
                "default_value": False
            }
        ]
    }
    
    manager = OntologyManager()
    
    # 从字典加载
    manager.entities = {}
    manager.relations = []
    manager.attributes = {}
    
    for entity_data in ontology_data['entities']:
        entity = OntologyEntity(
            id=entity_data['id'],
            name=entity_data['name'],
            type=entity_data.get('type', 'default'),
            description=entity_data.get('description', ''),
            attributes=entity_data.get('attributes', {}),
            relationships=entity_data.get('relationships', [])
        )
        manager.entities[entity.id] = entity
    
    for rel_data in ontology_data['relations']:
        relation = OntologyRelation(
            source=rel_data['source'],
            target=rel_data['target'],
            relation_type=rel_data.get('type', 'causes'),
            weight=rel_data.get('weight', 1.0),
            description=rel_data.get('description', '')
        )
        manager.relations.append(relation)
    
    for attr_data in ontology_data['attributes']:
        attribute = OntologyAttribute(
            name=attr_data['name'],
            type=attr_data.get('type', 'string'),
            description=attr_data.get('description', ''),
            default_value=attr_data.get('default_value'),
            range=tuple(attr_data['range']) if 'range' in attr_data else None,
            enum_values=attr_data.get('enum_values')
        )
        manager.attributes[attr_data['name']] = attribute
    
    manager._build_causal_graph()
    
    return manager


def load_ontology_from_file(ontology_file: str) -> OntologyManager:
    """
    从文件加载本体
    
    Args:
        ontology_file: 本体文件路径
        
    Returns:
        本体管理器实例
    """
    return OntologyManager(ontology_file)