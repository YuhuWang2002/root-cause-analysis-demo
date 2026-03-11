"""
PAC900S12-B2-1库存高因果根因分析 - 本体图API

提供本体图的JSON数据，用于展示产品与部件的关系
"""

from typing import Dict, List
import json
import os


class OntologyAPI:
    """本体图API"""
    
    @staticmethod
    def get_ontology_data() -> Dict:
        """
        获取本体图数据
        
        Returns:
            本体图JSON数据
        """
        # 读取server_inventory_schema.json文件
        schema_path = os.path.join(os.path.dirname(__file__), 'server_inventory_schema.json')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        # 转换为标准本体格式
        entities = []
        relations = []
        rules = []
        
        # 处理实体
        for entity_type in schema_data.get('entity_types', []):
            entity = {
                "id": entity_type.get('id'),
                "name": entity_type.get('name'),
                "type": entity_type.get('type'),
                "description": entity_type.get('description')
            }
            entities.append(entity)
        
        # 处理关系
        for relation_type in schema_data.get('relation_types', []):
            for source_type in relation_type.get('source_types', []):
                for target_type in relation_type.get('target_types', []):
                    relation = {
                        "source": source_type,
                        "target": target_type,
                        "relation_type": relation_type.get('name'),
                        "description": relation_type.get('description')
                    }
                    relations.append(relation)
        
        # 添加规则
        rules.append({
            "id": "rule_1",
            "name": "部件通用规则",
            "description": "相同类型的部件可以通用",
            "type": "constraint"
        })
        
        ontology_data = {
            "entities": entities,
            "relations": relations,
            "rules": rules
        }
        
        return ontology_data
    
    @staticmethod
    def get_ontology_graph_data() -> Dict:
        """
        获取本体图可视化数据（用于Plotly）
        
        Returns:
            本体图可视化数据
        """
        ontology_data = OntologyAPI.get_ontology_data()
        schema_path = os.path.join(os.path.dirname(__file__), 'server_inventory_schema.json')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        entity_attrs = {}
        for entity_type in schema_data.get('entity_types', []):
            entity_attrs[entity_type['id']] = entity_type.get('attributes', [])
        
        nodes = []
        for entity in ontology_data["entities"]:
            attrs = entity_attrs.get(entity["id"], [])
            nodes.append({
                "id": entity["id"],
                "label": entity["name"],
                "type": entity["type"],
                "description": entity["description"],
                "attributes": attrs,
                "color": "#2E86AB" if entity["type"] == "Product" else "#A23B72"
            })
        
        edges = []
        for relation in ontology_data["relations"]:
            edges.append({
                "source": relation["source"],
                "target": relation["target"],
                "label": relation["relation_type"],
                "description": relation["description"]
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "rules": ontology_data["rules"]
        }
    
    @staticmethod
    def get_ontology_text() -> str:
        """
        获取本体图的文本描述
        
        Returns:
            本体图文本描述
        """
        ontology_data = OntologyAPI.get_ontology_data()
        
        text_lines = []
        for relation in ontology_data["relations"]:
            source = next(e["name"] for e in ontology_data["entities"] if e["id"] == relation["source"])
            target = next(e["name"] for e in ontology_data["entities"] if e["id"] == relation["target"])
            text_lines.append(f"{source} {relation['relation_type']} {target}")
        
        return "\n".join(text_lines)
    
    @staticmethod
    def get_metrics_from_ontology() -> List[Dict]:
        """
        从本体中提取所有指标属性
        
        Returns:
            指标列表，每个指标包含fieldName, description, entity等信息
        """
        schema_path = os.path.join(os.path.dirname(__file__), 'server_inventory_schema.json')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        metrics = []
        for entity_type in schema_data.get('entity_types', []):
            entity_name = entity_type.get('name')
            entity_id = entity_type.get('id')
            entity_type_val = entity_type.get('type')
            
            for attr in entity_type.get('attributes', []):
                if attr.get('type') == 'metric':
                    metric = {
                        "fieldName": attr.get('fieldName'),
                        "name": attr.get('name'),
                        "description": attr.get('description'),
                        "unit": attr.get('unit'),
                        "dataType": attr.get('dataType'),
                        "entityName": entity_name,
                        "entityId": entity_id,
                        "entityType": entity_type_val
                    }
                    metrics.append(metric)
        
        return metrics
    
    @staticmethod
    def get_metrics_text() -> str:
        """
        获取指标字段的文本描述
        
        Returns:
            指标字段文本描述
        """
        metrics = OntologyAPI.get_metrics_from_ontology()
        
        text_lines = []
        for metric in metrics:
            text_lines.append(f"- {metric['fieldName']}: {metric['description']}")
        
        return "\n".join(text_lines)
    
    @staticmethod
    def get_ontology_info_for_llm() -> str:
        """
        获取用于LLM推理的本体信息
        
        Returns:
            本体信息文本，包含实体、关系和指标
        """
        schema_path = os.path.join(os.path.dirname(__file__), 'server_inventory_schema.json')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        info_lines = []
        
        info_lines.append("## 实体类型")
        for entity_type in schema_data.get('entity_types', []):
            entity_name = entity_type.get('name')
            entity_id = entity_type.get('id')
            entity_type_val = entity_type.get('type')
            entity_desc = entity_type.get('description')
            info_lines.append(f"- {entity_name}({entity_id}): {entity_desc} [类型: {entity_type_val}]")
            
            metrics = []
            for attr in entity_type.get('attributes', []):
                if attr.get('type') == 'metric':
                    metrics.append(f"  - 指标: {attr.get('fieldName')} - {attr.get('description')}")
            if metrics:
                info_lines.extend(metrics)
        
        info_lines.append("\n## 关系类型")
        for relation_type in schema_data.get('relation_types', []):
            rel_name = relation_type.get('name')
            rel_desc = relation_type.get('description')
            sources = relation_type.get('source_types', [])
            targets = relation_type.get('target_types', [])
            info_lines.append(f"- {rel_name}: {sources} -> {targets} ({rel_desc})")
        
        info_lines.append("\n## 数据字段（从本体中提取）")
        metrics = OntologyAPI.get_metrics_from_ontology()
        for metric in metrics:
            info_lines.append(f"- {metric['fieldName']}: {metric['description']}")
        
        return "\n".join(info_lines)


if __name__ == "__main__":
    api = OntologyAPI()
    
    print("=== 本体图数据 ===")
    data = api.get_ontology_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    print("\n=== 本体图可视化数据 ===")
    graph_data = api.get_ontology_graph_data()
    print(json.dumps(graph_data, ensure_ascii=False, indent=2))
    
    print("\n=== 本体图文本描述 ===")
    print(api.get_ontology_text())
