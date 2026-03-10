"""
PAC900S12-B2库存高因果根因分析 - 本体图API

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
        
        nodes = []
        for entity in ontology_data["entities"]:
            nodes.append({
                "id": entity["id"],
                "label": entity["name"],
                "type": entity["type"],
                "description": entity["description"],
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
