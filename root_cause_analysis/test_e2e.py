"""
端到端测试脚本

测试完整的Agent驱动的因果分析流程：
1. 读取模型配置
2. 初始化LLM Agent
3. 推导因果图
4. 生成数据
5. 运行因果分析
6. 生成大模型解释
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加web目录到路径
sys.path.insert(0, str(Path(__file__).parent / "web"))

from llm_agent import LLMAgent, CausalGraphDerivationRequest
from data_generator import create_demo_scenario
from root_cause_analysis_pipeline import RootCauseAnalysisPipeline
from llm_explainer import LLMExplainer


def read_model_config(config_file: str = "web/modelkey.cfg"):
    """
    读取模型配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    config = {
        "api_key": None,
        "base_url": None,
        "model": None
    }
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("API Key:"):
                    config["api_key"] = line.split(":", 1)[1].strip()
                elif line.startswith("Base URL:"):
                    config["base_url"] = line.split(":", 1)[1].strip()
                elif line.startswith("Model:"):
                    config["model"] = line.split(":", 1)[1].strip()
        
        print(f"[Config] 成功读取配置文件: {config_file}")
        print(f"[Config] API Key: {config['api_key'][:20]}...")
        print(f"[Config] Base URL: {config['base_url']}")
        print(f"[Config] Model: {config['model']}")
        
    except Exception as e:
        print(f"[Config] 读取配置文件失败: {str(e)}")
        raise
    
    return config


def test_ontology_api():
    """测试本体API"""
    print("\n" + "="*60)
    print("步骤1：测试本体API")
    print("="*60)
    
    try:
        import httpx
        
        # 测试获取实体
        response = httpx.get("http://localhost:8000/entities", timeout=10.0)
        response.raise_for_status()
        entities = response.json()
        
        print(f"✅ 本体API连接成功！")
        print(f"   - 实体数量: {len(entities)}")
        
        # 测试获取关系
        response = httpx.get("http://localhost:8000/relations", timeout=10.0)
        response.raise_for_status()
        relations = response.json()
        
        print(f"   - 关系数量: {len(relations)}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  本体API连接失败: {str(e)}")
        print(f"   提示：本体API未运行，将跳过本体API测试")
        print(f"   启动命令: python web/ontology_api.py")
        return False


def test_llm_agent(config: dict):
    """测试LLM Agent"""
    print("\n" + "="*60)
    print("步骤2：测试LLM Agent")
    print("="*60)
    
    try:
        # 初始化LLM Agent
        agent = LLMAgent(
            ontology_api_url="http://localhost:8000",
            llm_api_key=config["api_key"]
        )
        
        print(f"✅ LLM Agent初始化成功！")
        
        # 测试查询本体
        print("\n   测试查询本体...")
        ontology_response = agent.query_ontology("all")
        print(f"   - 查询到 {len(ontology_response.entities)} 个实体")
        print(f"   - 查询到 {len(ontology_response.relations)} 个关系")
        
        # 测试推导因果图
        print("\n   测试推导因果图...")
        request = CausalGraphDerivationRequest(
            scenario_description="某制造企业在2024年12月发现生产效率相比11月显著下降，需要分析原因并提出改进措施。",
            outcome_entity="production_efficiency"
        )
        
        result = agent.derive_causal_graph(request)
        
        print(f"   ✅ 因果图推导成功！")
        print(f"   - 因果图节点数: {len(result.causal_graph)}")
        print(f"   - 建议数据字段数: {len(result.suggested_data_fields)}")
        print(f"   - 推理过程长度: {len(result.reasoning)} 字符")
        
        return result
        
    except Exception as e:
        print(f"❌ LLM Agent测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_data_generation():
    """测试数据生成"""
    print("\n" + "="*60)
    print("步骤3：测试数据生成")
    print("="*60)
    
    try:
        # 生成数据
        data, anomaly_factors = create_demo_scenario()
        
        print(f"✅ 数据生成成功！")
        print(f"   - 数据记录数: {len(data)}")
        print(f"   - 数据列数: {len(data.columns)}")
        print(f"   - 异常因素: {anomaly_factors}")
        
        return data, anomaly_factors
        
    except Exception as e:
        print(f"❌ 数据生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def test_causal_analysis(data):
    """
    测试因果分析
    """
    print("\n" + "="*60)
    print("步骤4：测试因果分析")
    print("="*60)
    
    try:
        # 创建默认因果图
        default_causal_graph = """digraph {
            payment_timeliness -> supplier_efficiency;
            supplier_efficiency -> parts_availability;
            parts_availability -> production_efficiency;
            avg_employee_skill -> production_efficiency;
            equipment_status -> production_efficiency;
            capacity_utilization -> production_efficiency;
            supplier_efficiency -> production_efficiency;
            payment_timeliness -> production_efficiency;
        }"""
        
        # 运行因果分析
        pipeline = RootCauseAnalysisPipeline(
            data=data,
            causal_graph=default_causal_graph
        )
        results = pipeline.run_full_analysis(
            treatment="payment_timeliness",
            outcome="production_efficiency"
        )
        
        print(f"✅ 因果分析完成！")
        print(f"   - 分析结果包含: {list(results.keys())}")
        
        # 打印因果效应
        if 'causal_effect' in results:
            print(f"   - 因果效应值: {results['causal_effect']:.4f}")
        
        # 打印驳斥检验结果
        if 'refutation_results' in results:
            refutation_results = results['refutation_results']
            print(f"   - 驳斥检验结果: {len(refutation_results)} 个测试")
            for test_name, result in refutation_results.items():
                print(f"     * {test_name}: {result}")
        
        # 打印反事实分析结果
        if 'counterfactual_analysis' in results:
            print(f"   - 反事实分析: 已执行")
        
        return results
        
    except Exception as e:
        print(f"❌ 因果分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_llm_explanation(config: dict, analysis_results: dict, data):
    """
    测试大模型解释
    """
    print("\n" + "="*60)
    print("步骤5：测试大模型解释")
    print("="*60)
    
    try:
        # 初始化大模型解释器
        explainer = LLMExplainer(
            api_type="siliconflow",
            api_key=config["api_key"],
            model=config["model"],
            base_url=config["base_url"]
        )
        
        print(f"✅ 大模型解释器初始化成功！")
        
        # 生成解释
        print("\n   正在生成大模型解释...")
        
        # 创建mock的comparison_df和causal_results数据帧
        import pandas as pd
        
        # 创建mock的comparison_df
        comparison_df = pd.DataFrame({
            'metric': ['production_efficiency', 'payment_timeliness', 'supplier_efficiency', 'parts_availability'],
            'normal_mean': [0.85, 0.9, 0.88, 0.92],
            'anomaly_mean': [0.65, 0.45, 0.68, 0.75],
            'change_percent': [-0.235, -0.5, -0.227, -0.185],
            'abs_change': [0.235, 0.5, 0.227, 0.185]
        })
        
        # 创建mock的causal_results
        causal_results = pd.DataFrame({
            'cause': ['avg_employee_skill', 'parts_availability', 'supplier_efficiency'],
            'causal_effect': [0.70, 0.56, 0.35],
            'interpretation': ['员工技能对生产效率有直接且显著的影响', '零部件供应不足直接影响生产线的正常运转', '供应商的生产效率直接影响零部件的交付']
        })
        
        # 生成解释
        explanation = explainer.generate_explanation(
            analysis_results=analysis_results,
            comparison_df=comparison_df,
            causal_results=causal_results
        )
        
        print(f"   ✅ 大模型解释生成成功！")
        print(f"   - 解释长度: {len(explanation)} 字符")
        
        # 显示解释的前500个字符
        print(f"\n   解释预览（前500字符）:")
        print("   " + "-"*50)
        print("   " + explanation[:500])
        print("   " + "-"*50)
        
        return explanation
        
    except Exception as e:
        print(f"❌ 大模型解释失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("\n" + "="*60)
    print("端到端测试 - Agent驱动的因果分析")
    print("="*60)
    
    # 读取配置
    config = read_model_config()
    
    if not config["api_key"]:
        print("\n❌ 错误：未找到API Key")
        print("   请在 modelkey.cfg 文件中配置 API Key")
        return
    
    # 测试状态
    test_status = {
        "ontology_api": False,
        "llm_agent": False,
        "data_generation": False,
        "causal_analysis": False,
        "llm_explanation": False
    }
    
    # 测试本体API
    test_status["ontology_api"] = test_ontology_api()
    
    # 测试LLM Agent（跳过本体API，直接测试Agent逻辑）
    print("\n" + "="*60)
    print("步骤2：测试LLM Agent（跳过本体API，直接测试Agent逻辑）")
    print("="*60)
    
    causal_graph_result = None
    try:
        # 初始化LLM Agent（使用同步版本）
        from llm_agent import LLMAgentSync
        
        agent = LLMAgentSync(
            ontology_api_url="http://localhost:8000",
            llm_api_key=config["api_key"],
            llm_base_url=config["base_url"],
            llm_model=config["model"]
        )
        
        print(f"✅ LLM Agent初始化成功！")
        
        # 测试推导因果图（使用内部逻辑，不调用本体API）
        print("\n   测试推导因果图...")
        from llm_agent import CausalGraphDerivationRequest
        
        request = CausalGraphDerivationRequest(
            scenario_description="某制造企业在2024年12月发现生产效率相比11月显著下降，需要分析原因并提出改进措施。",
            outcome_entity="production_efficiency"
        )
        
        result = agent.derive_causal_graph(request)
        
        print(f"   ✅ 因果图推导成功！")
        print(f"   - 因果图节点数: {len(result.causal_graph)}")
        print(f"   - 建议数据字段数: {len(result.suggested_data_fields)}")
        print(f"   - 推理过程长度: {len(result.reasoning)} 字符")
        
        # 打印因果图
        print(f"\n   📊 因果图结构:")
        for source, targets in result.causal_graph.items():
            if len(targets) > 0:
                print(f"      {source} → {', '.join(targets)}")
        
        # 打印建议的数据字段
        print(f"\n   📝 建议的数据字段:")
        for field in result.suggested_data_fields:
            print(f"      - {field}")
        
        causal_graph_result = result
        test_status["llm_agent"] = True
        
    except Exception as e:
        print(f"❌ LLM Agent测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        causal_graph_result = None
        test_status["llm_agent"] = False
    
    # 测试数据生成
    data, anomaly_factors = test_data_generation()
    if data is not None:
        test_status["data_generation"] = True
    else:
        print("\n❌ 数据生成失败，跳过后续测试")
        test_status["data_generation"] = False
        # 继续总结，不return
    
    # 测试因果分析
    analysis_results = test_causal_analysis(data) if (data is not None) else None
    if analysis_results:
        test_status["causal_analysis"] = True
    else:
        print("\n❌ 因果分析失败，跳过后续测试")
        test_status["causal_analysis"] = False
        # 继续总结，不return
    
    # 测试大模型解释
    explanation = None
    if (analysis_results is not None) and (data is not None):
        explanation = test_llm_explanation(config, analysis_results, data)
    
    if explanation:
        test_status["llm_explanation"] = True
    else:
        test_status["llm_explanation"] = False
    
    # 总结
    print("\n" + "="*60)
    print("端到端测试完成！")
    print("="*60)
    print("\n测试总结：")
    print(f"  {'✅' if test_status['ontology_api'] else '❌'} 本体API - {'正常' if test_status['ontology_api'] else '失败'}")
    print(f"  {'✅' if test_status['llm_agent'] else '❌'} LLM Agent - {'正常' if test_status['llm_agent'] else '失败'}")
    print(f"  {'✅' if test_status['data_generation'] else '❌'} 数据生成 - {'正常' if test_status['data_generation'] else '失败'}")
    print(f"  {'✅' if test_status['causal_analysis'] else '❌'} 因果分析 - {'正常' if test_status['causal_analysis'] else '失败'}")
    print(f"  {'✅' if test_status['llm_explanation'] else '❌'} 大模型解释 - {'正常' if test_status['llm_explanation'] else '失败'}")
    
    # 检查是否所有测试都通过
    all_passed = all(test_status.values())
    if all_passed:
        print("\n✅ 所有组件都正常工作！")
    else:
        print("\n⚠️  部分组件测试失败！")


if __name__ == "__main__":
    main()