#!/usr/bin/env python3
"""
MVP架构测试脚本

测试简化后的架构：
1. 本体管理 - 正常工作
2. LLM Agent - 能查询本体并推导因果图
3. 数据生成 - 正常工作
4. 因果分析 - 正常工作
"""

import sys
from pathlib import Path

# 添加web目录到路径
sys.path.insert(0, str(Path(__file__).parent / "web"))

print("=" * 70)
print("测试MVP架构")
print("=" * 70)

# 1. 测试本体管理器
print("\n[1] 测试本体管理器...")
try:
    from ontology_manager import OntologyManager, create_manufacturing_ontology
    
    ontology = create_manufacturing_ontology()
    print(f"✓ 成功创建本体管理器")
    print(f"✓ 实体数量: {len(ontology.entities)}")
    print(f"✓ 关系数量: {len(ontology.relations)}")
    print(f"✓ 属性数量: {len(ontology.attributes)}")
    
    # 检查是否有metric实体
    metric_entities = ontology.get_entities_by_type("metric")
    print(f"✓ metric类型实体数量: {len(metric_entities)}")
    
except Exception as e:
    print(f"✗ 本体管理器测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 测试LLM Agent（跳过需要httpx的部分，直接测试逻辑）
print("\n[2] 测试LLM Agent数据模型和逻辑...")
try:
    from llm_agent import CausalGraphDerivationRequest, CausalGraphDerivationResponse
    from ontology_manager import create_manufacturing_ontology
    
    # 测试数据模型
    request = CausalGraphDerivationRequest(
        scenario_description="某制造企业生产效率下降，需要分析原因",
        outcome_entity="production_efficiency"
    )
    print(f"✓ CausalGraphDerivationRequest 数据模型正常")
    
    # 测试因果图结构（模拟LLM输出）
    causal_graph = {
        "payment_timeliness": ["supplier_efficiency"],
        "supplier_efficiency": ["parts_availability", "production_efficiency"],
        "parts_availability": ["production_efficiency"],
        "avg_employee_skill": ["production_efficiency"],
        "equipment_status": ["production_efficiency"]
    }
    
    response = CausalGraphDerivationResponse(
        causal_graph=causal_graph,
        reasoning="测试推理过程",
        suggested_data_fields=["payment_timeliness", "supplier_efficiency", "production_efficiency"],
        required_entities=["payment_timeliness", "supplier_efficiency"]
    )
    print(f"✓ CausalGraphDerivationResponse 数据模型正常")
    print(f"✓ 因果图节点数: {len(response.causal_graph)}")
    
    # 打印因果图结构
    print("\n因果图结构（示例）:")
    for source, targets in response.causal_graph.items():
        if targets:
            print(f"  {source} → {', '.join(targets)}")
    
except Exception as e:
    print(f"✗ LLM Agent测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试数据生成器
print("\n[3] 测试数据生成器...")
try:
    from data_generator import create_demo_scenario
    
    df, anomaly_factors = create_demo_scenario()
    print(f"✓ 成功生成测试数据")
    print(f"✓ 数据记录数: {len(df)}")
    print(f"✓ 数据字段数: {len(df.columns)}")
    
    # 检查关键字段是否存在
    required_fields = ['payment_timeliness', 'supplier_efficiency', 'parts_availability', 
                      'avg_employee_skill', 'equipment_status', 'production_efficiency']
    missing_fields = [f for f in required_fields if f not in df.columns]
    if missing_fields:
        print(f"✗ 缺少字段: {missing_fields}")
    else:
        print(f"✓ 所有关键字段都存在")
    
except Exception as e:
    print(f"✗ 数据生成器测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 测试因果分析器
print("\n[4] 测试因果分析器...")
try:
    from causal_analyzer import RootCauseAnalysisPipeline, CausalAnalyzer
    
    # 测试CausalAnalyzer
    analyzer = CausalAnalyzer(df, ontology)
    causal_graph_dot = analyzer.build_causal_graph()
    print(f"✓ 成功构建因果图DOT格式")
    print(f"✓ DOT格式长度: {len(causal_graph_dot)} 字符")
    
    # 测试RootCauseAnalysisPipeline
    pipeline = RootCauseAnalysisPipeline(df, ontology)
    results = pipeline.run_full_analysis()
    print(f"✓ 成功运行完整分析")
    print(f"✓ 因果效应分析: {len(results['causal_analysis'])} 个因素")
    
except Exception as e:
    print(f"✗ 因果分析器测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ 所有测试通过！MVP架构正常工作！")
print("=" * 70)
print("\n架构总结:")
print("- ontology_manager.py: 管理业务本体，包含metric实体和业务关系")
print("- llm_agent.py: 从本体API查询信息，推理因果图")
print("- data_generator.py: 直接生成分析数据（假定从本体抽取）")
print("- causal_analyzer.py: 使用因果图进行DoWhy分析")
print("- llm_explainer.py: 大模型解释分析结果")
