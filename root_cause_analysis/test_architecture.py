#!/usr/bin/env python3
"""
测试架构重构是否成功
验证因果图功能是否从本体管理器中正确分离
"""

import sys
sys.path.insert(0, 'web')

from ontology_manager import OntologyManager, create_manufacturing_ontology
from causal_graph_builder import build_causal_graph_from_relations, get_causal_chain

print("=" * 70)
print("测试架构重构")
print("=" * 70)

# 1. 测试本体管理器是否正常工作
print("\n[1] 测试本体管理器...")
try:
    ontology = create_manufacturing_ontology()
    print(f"✓ 成功创建本体管理器")
    print(f"✓ 实体数量: {len(ontology.entities)}")
    print(f"✓ 关系数量: {len(ontology.relations)}")
    print(f"✓ 属性数量: {len(ontology.attributes)}")
    
    # 检查是否有因果图相关的属性
    if hasattr(ontology, 'causal_graph'):
        print(f"✗ 错误: ontology_manager 中仍有 causal_graph 属性")
        sys.exit(1)
    else:
        print(f"✓ ontology_manager 中已移除 causal_graph 属性")
    
    if hasattr(ontology, '_build_causal_graph'):
        print(f"✗ 错误: ontology_manager 中仍有 _build_causal_graph 方法")
        sys.exit(1)
    else:
        print(f"✓ ontology_manager 中已移除 _build_causal_graph 方法")
    
    if hasattr(ontology, 'get_causal_graph'):
        print(f"✗ 错误: ontology_manager 中仍有 get_causal_graph 方法")
        sys.exit(1)
    else:
        print(f"✓ ontology_manager 中已移除 get_causal_graph 方法")
    
    if hasattr(ontology, 'get_causal_chain'):
        print(f"✗ 错误: ontology_manager 中仍有 get_causal_chain 方法")
        sys.exit(1)
    else:
        print(f"✓ ontology_manager 中已移除 get_causal_chain 方法")
        
except Exception as e:
    print(f"✗ 本体管理器测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 测试因果图构建模块
print("\n[2] 测试因果图构建模块...")
try:
    # 将本体关系转换为字典格式
    relations_dict = []
    for relation in ontology.relations:
        relations_dict.append({
            'source': relation.source,
            'target': relation.target,
            'relation_type': relation.relation_type
        })
    
    # 使用 causal_graph_builder 构建因果图
    causal_graph = build_causal_graph_from_relations(relations_dict)
    print(f"✓ 成功使用 causal_graph_builder 构建因果图")
    print(f"✓ 因果图节点数: {len(causal_graph)}")
    print(f"✓ 因果图边数: {sum(len(targets) for targets in causal_graph.values())}")
    
    # 测试获取因果链
    chain = get_causal_chain(causal_graph, "payment_timeliness", "production_efficiency")
    print(f"✓ 成功获取因果链: {' → '.join(chain)}")
    
except Exception as e:
    print(f"✗ 因果图构建模块测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试因果分析器是否能使用新架构
print("\n[3] 测试因果分析器...")
try:
    from causal_analyzer import CausalAnalyzer
    from data_generator import create_demo_scenario
    
    # 生成测试数据
    data, _ = create_demo_scenario()
    
    # 创建分析器并测试
    analyzer = CausalAnalyzer(data, ontology)
    causal_graph_dot = analyzer.build_causal_graph()
    print(f"✓ 成功使用因果分析器构建因果图")
    print(f"✓ 因果图DOT格式长度: {len(causal_graph_dot)} 字符")
    
except Exception as e:
    print(f"✗ 因果分析器测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ 所有测试通过！架构重构成功！")
print("=" * 70)
print("\n架构说明:")
print("- ontology_manager.py: 只负责本体管理（实体、关系、属性）")
print("- causal_graph_builder.py: 独立模块，负责因果图构建")
print("- causal_analyzer.py: 使用 causal_graph_builder 模块")
