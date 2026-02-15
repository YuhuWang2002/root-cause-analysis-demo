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
        
        # 从web/modelkey.cfg读取配置
        import os
        modelkey_path = os.path.join(os.path.dirname(__file__), "web", "modelkey.cfg")
        api_key = None
        base_url = None
        model = None
        
        with open(modelkey_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 解析配置
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('API Key:'):
                    api_key = line.split(':', 1)[1].strip()
                elif line.startswith('Base URL:'):
                    base_url = line.split(':', 1)[1].strip()
                elif line.startswith('Model:'):
                    model = line.split(':', 1)[1].strip()
        
        if not api_key:
            raise ValueError("无法从modelkey.cfg文件中读取API密钥")
        if not base_url:
            raise ValueError("无法从modelkey.cfg文件中读取Base URL")
        if not model:
            raise ValueError("无法从modelkey.cfg文件中读取Model")
        
        print(f"   - API Key: {api_key[:20]}...")
        print(f"   - Base URL: {base_url}")
        print(f"   - Model: {model}")
        
        agent = LLMAgentSync(
            ontology_api_url="http://localhost:8000",
            llm_api_key=api_key,
            llm_base_url=base_url,
            llm_model=model
        )
        print("✅ LLM Agent初始化成功！")
        
        print("\n2. 测试查询本体Schema...")
        schema_response = agent.query_schema()
        print(f"✅ 本体查询成功！")
        print(f"   - 实体类型数: {len(schema_response.get('entity_types', []))}")
        print(f"   - 关系类型数: {len(schema_response.get('relation_types', []))}")
        print(f"   - 指标定义数: {len(schema_response.get('metric_definitions', []))}")
        
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