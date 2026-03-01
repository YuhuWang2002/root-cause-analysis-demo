"""
因果图构建器模块

提供智能构建因果图的功能，支持：
- 从本体构建因果图
- 大模型智能推导因果关系
- 默认因果图模板
- 用户自定义因果图
"""

from typing import Dict, List, Optional, Union
from ontology_manager import OntologyManager


class CausalGraphBuilder:
    """因果图构建器"""
    
    def __init__(self, ontology_manager: Optional[OntologyManager] = None):
        """
        初始化因果图构建器
        
        Args:
            ontology_manager: 本体管理器（可选）
        """
        self.ontology_manager = ontology_manager
    
    def build_from_ontology(self) -> str:
        """
        从本体构建因果图
        
        Returns:
            标准的DoWhy因果图格式字符串
        """
        if not self.ontology_manager:
            raise ValueError("本体管理器未提供")
        
        edges = []
        
        # 从本体关系构建因果边
        for relation in getattr(self.ontology_manager, 'relations', []):
            if hasattr(relation, 'relation_type') and relation.relation_type in ['influences', 'causes', 'related_to']:
                edges.append(f"    {relation.source} -> {relation.target};")
        
        # 如果有schema，从schema构建因果边
        if hasattr(self.ontology_manager, 'schema'):
            schema = self.ontology_manager.schema
            
            # 从关系类型构建因果边
            for relation_type in schema.get('relation_types', []):
                source_types = relation_type.get('source_types', [])
                target_types = relation_type.get('target_types', [])
                
                # 为每种源类型和目标类型的组合创建因果边
                for source_type in source_types:
                    for target_type in target_types:
                        edges.append(f"    {source_type} -> {target_type};")
        
        if edges:
            causal_graph = "digraph {\n" + "\n".join(edges) + "\n}"
            return causal_graph
        
        # 如果没有找到关系，返回默认因果图
        return self.get_default_causal_graph()
    
    def build_with_llm(self, 
                      ontology_schema: Dict, 
                      llm_agent: object,
                      scenario_description: str,
                      outcome_entity: str) -> str:
        """
        使用大模型从本体schema智能推导因果图
        
        Args:
            ontology_schema: 本体schema字典
            llm_agent: LLM代理实例，需要提供推理方法
            scenario_description: 场景描述
            outcome_entity: 结果实体
        
        Returns:
            标准的DoWhy因果图格式字符串
        """
        try:
            # 导入必要的模型
            from llm_agent import CausalGraphDerivationRequest
            
            # 构建因果图推导请求
            request = CausalGraphDerivationRequest(
                scenario_description=scenario_description,
                outcome_entity=outcome_entity,
                ontology_info=ontology_schema
            )
            print(f"[CausalGraphBuilder] 使用场景: {scenario_description}")
            print(f"[CausalGraphBuilder] 结果实体: {outcome_entity}")
            
            # 使用LLM推导因果图
            response = llm_agent.derive_causal_graph(request)
            
            # 从响应构建因果图
            causal_graph_dict = response.causal_graph
            edges = []
            
            for source, targets in causal_graph_dict.items():
                for target in targets:
                    edges.append(f"    {source} -> {target};")
            
            if edges:
                causal_graph = "digraph {\n" + "\n".join(edges) + "\n}"
                return causal_graph
            
        except Exception as e:
            print(f"[CausalGraphBuilder] 使用大模型构建因果图失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 如果LLM推导失败，返回默认因果图
        return self.get_default_causal_graph()
    
    def get_default_causal_graph(self) -> str:
        """
        获取默认因果图模板
        
        Returns:
            标准的DoWhy因果图格式字符串
        """
        default_causal_graph = """digraph {
            treatment -> outcome;
            confounder1 -> treatment;
            confounder1 -> outcome;
            confounder2 -> treatment;
            confounder2 -> outcome;
        }"""
        return default_causal_graph
    
    def build_custom_graph(self, edges: List[Dict[str, str]]) -> str:
        """
        根据用户自定义的边构建因果图
        
        Args:
            edges: 边列表，每个边包含'source'和'target'字段
        
        Returns:
            标准的DoWhy因果图格式字符串
        """
        graph_edges = []
        for edge in edges:
            if 'source' in edge and 'target' in edge:
                graph_edges.append(f"    {edge['source']} -> {edge['target']};")
        
        if graph_edges:
            causal_graph = "digraph {\n" + "\n".join(graph_edges) + "\n}"
            return causal_graph
        
        # 如果没有边，返回默认因果图
        return self.get_default_causal_graph()
    
    def _build_llm_prompt(self, ontology_schema: Dict) -> str:
        """
        构建大模型提示词
        
        Args:
            ontology_schema: 本体schema字典
        
        Returns:
            提示词字符串
        """
        prompt_parts = []
        prompt_parts.append("请根据以下本体schema，推断出合理的因果关系网络：")
        
        # 添加实体类型信息
        entity_types = ontology_schema.get('entity_types', [])
        if entity_types:
            prompt_parts.append("\n实体类型：")
            for entity_type in entity_types:
                entity_name = entity_type.get('name', entity_type.get('id', 'Unknown'))
                entity_id = entity_type.get('id', 'Unknown')
                attributes = entity_type.get('attributes', [])
                attr_names = [attr.get('name') for attr in attributes if attr.get('name')]
                prompt_parts.append(f"- {entity_name} ({entity_id}): {', '.join(attr_names) if attr_names else '无属性'}")
        
        # 添加关系类型信息
        relation_types = ontology_schema.get('relation_types', [])
        if relation_types:
            prompt_parts.append("\n关系类型：")
            for relation_type in relation_types:
                relation_name = relation_type.get('name', relation_type.get('id', 'Unknown'))
                source_types = relation_type.get('source_types', [])
                target_types = relation_type.get('target_types', [])
                prompt_parts.append(f"- {relation_name}: {', '.join(source_types)} -> {', '.join(target_types)}")
        
        # 添加指标定义信息
        metric_definitions = ontology_schema.get('metric_definitions', [])
        if metric_definitions:
            prompt_parts.append("\n指标定义：")
            for metric in metric_definitions:
                metric_name = metric.get('name', metric.get('id', 'Unknown'))
                metric_id = metric.get('id', 'Unknown')
                source_entity = metric.get('source_entity_type', 'Unknown')
                prompt_parts.append(f"- {metric_name} ({metric_id}): 来源实体 = {source_entity}")
        
        # 添加输出格式要求
        prompt_parts.append("\n请以JSON格式输出因果关系列表，每个关系包含'source'和'target'字段，例如：")
        prompt_parts.append('[')
        prompt_parts.append('  {"source": "A", "target": "B"},')
        prompt_parts.append('  {"source": "C", "target": "B"}')
        prompt_parts.append(']')
        
        return '\n'.join(prompt_parts)
    
    def validate_causal_graph(self, causal_graph: str) -> bool:
        """
        验证因果图格式是否正确
        
        Args:
            causal_graph: 因果图字符串
        
        Returns:
            是否有效
        """
        # 简单验证：检查是否包含digraph关键字和至少一个边
        return 'digraph' in causal_graph and '->' in causal_graph
