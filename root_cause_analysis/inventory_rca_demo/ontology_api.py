"""
部件A库存高因果根因分析 - 本体图API

提供本体图的JSON数据，用于展示产品与部件的关系
"""

from typing import Dict, List
import json


class OntologyAPI:
    """本体图API"""
    
    @staticmethod
    def get_ontology_data() -> Dict:
        """
        获取本体图数据
        
        Returns:
            本体图JSON数据
        """
        ontology_data = {
            "entities": [
                {
                    "id": "product_a",
                    "name": "产品A",
                    "type": "Product",
                    "description": "产品A，销量下降导致部件A库存高"
                },
                {
                    "id": "product_b",
                    "name": "产品B",
                    "type": "Product",
                    "description": "产品B，未使用部件A"
                },
                {
                    "id": "component_a",
                    "name": "部件A",
                    "type": "Component",
                    "description": "部件A，库存高位问题"
                },
                {
                    "id": "component_a1",
                    "name": "部件A1",
                    "type": "Component",
                    "description": "部件A1，与部件A型号相同，可以通用"
                }
            ],
            "relations": [
                {
                    "source": "product_a",
                    "target": "component_a",
                    "relation_type": "使用",
                    "description": "产品A使用部件A"
                },
                {
                    "source": "product_b",
                    "target": "component_a1",
                    "relation_type": "使用",
                    "description": "产品B使用部件A1"
                }
            ],
            "rules": [
                {
                    "id": "rule_1",
                    "name": "部件通用规则",
                    "description": "部件A和部件A1是相同型号，可以通用",
                    "type": "constraint"
                }
            ]
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
