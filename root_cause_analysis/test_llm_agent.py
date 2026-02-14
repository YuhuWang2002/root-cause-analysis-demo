"""
测试脚本 - 专门测试LLM Agent部分
"""

import sys
from pathlib import Path

# 添加web目录到路径
sys.path.insert(0, str(Path(__file__).parent / "web"))

from llm_agent import LLMAgentSync, CausalGraphDerivationRequest


def test_llm_agent():
    """测试LLM Agent"""
    print("\n" + "="*60)
    print("测试LLM Agent")
    print("="*60)
    
    try:
        print("\n1. 初始化LLM Agent...")
        agent = LLMAgentSync(
            ontology_api_url="http://localhost:8000",
            llm_api_key="test_key"
        )
        print("✅ LLM Agent初始化成功！")
        
        print("\n2. 测试查询本体...")
        ontology_response = agent.query_ontology("all")
        print(f"✅ 本体查询成功！")
        print(f"   - 实体数量: {len(ontology_response.entities)}")
        print(f"   - 关系数量: {len(ontology_response.relations)}")
        
        print("\n3. 测试推导因果图...")
        request = CausalGraphDerivationRequest(
            scenario_description="某制造企业在2024年12月发现生产效率相比11月显著下降，需要分析原因并提出改进措施。",
            outcome_entity="production_efficiency"
        )
        
        result = agent.derive_causal_graph(request)
        
        print(f"✅ 因果图推导成功！")
        print(f"   - 因果图节点数: {len(result.causal_graph)}")
        print(f"   - 建议数据字段数: {len(result.suggested_data_fields)}")
        print(f"   - 推理过程长度: {len(result.reasoning)} 字符")
        
        print("\n" + "="*60)
        print("✅ LLM Agent测试通过！")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ LLM Agent测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("❌ LLM Agent测试失败！")
        print("="*60)
        return False


if __name__ == "__main__":
    success = test_llm_agent()
    sys.exit(0 if success else 1)