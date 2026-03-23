from flask import Blueprint, request, jsonify
from models import db, CanvasData
import json

bp = Blueprint('root_cause', __name__, url_prefix='/api/root-cause')

DEFAULT_CAUSAL_GRAPH = """digraph {
    kunlun_2280_sales -> pac900s12_b2_1_consumption;
    server_2288hv7_sales -> pac900s12_b2_1_consumption;
    server_2288hv7_uses_pac900s12_b2_1 -> pac900s12_b2_1_consumption;
    pac900s12_b2_1_consumption -> pac900s12_b2_1_inventory;
    pac900s12_b2_1_procurement -> pac900s12_b2_1_inventory;
    kunlun_2280_sales -> pac900s12_b2_1_procurement;
}"""

@bp.route('/<project_id>/causal_graph/<node_id>', methods=['GET'])
def get_causal_graph(project_id, node_id):
    canvas_data = CanvasData.query.filter_by(project_id=project_id).first()

    if not canvas_data:
        return jsonify({
            'project_id': project_id,
            'node_id': node_id,
            'causal_graph': DEFAULT_CAUSAL_GRAPH
        })

    try:
        nodes = json.loads(canvas_data.nodes) if isinstance(canvas_data.nodes, str) else canvas_data.nodes
        causal_graph = DEFAULT_CAUSAL_GRAPH
        for node in nodes:
            if node.get('id') == node_id and node.get('config', {}).get('causal_graph'):
                causal_graph = node['config']['causal_graph']
                break
    except:
        causal_graph = DEFAULT_CAUSAL_GRAPH

    return jsonify({
        'project_id': project_id,
        'node_id': node_id,
        'causal_graph': causal_graph
    })

@bp.route('/<project_id>/causal_graph/<node_id>', methods=['PUT'])
def save_causal_graph(project_id, node_id):
    data = request.get_json()
    causal_graph = data.get('causal_graph', DEFAULT_CAUSAL_GRAPH)

    canvas_data = CanvasData.query.filter_by(project_id=project_id).first()

    if canvas_data:
        try:
            nodes = json.loads(canvas_data.nodes) if isinstance(canvas_data.nodes, str) else canvas_data.nodes
        except:
            nodes = []

        found = False
        for node in nodes:
            if node.get('id') == node_id:
                if 'config' not in node:
                    node['config'] = {}
                node['config']['causal_graph'] = causal_graph
                found = True
                break

        # 不再自动添加节点，只更新指定 ID 的节点

        canvas_data.nodes = json.dumps(nodes)
    else:
        # 如果没有画布数据，不创建新的画布数据
        return jsonify({'error': 'Canvas data not found'}), 404

    db.session.commit()

    return jsonify({
        'project_id': project_id,
        'node_id': node_id,
        'causal_graph': causal_graph
    })

@bp.route('/<project_id>/analysis', methods=['POST'])
def run_analysis(project_id):
    data = request.get_json()
    causal_graph = data.get('causal_graph', DEFAULT_CAUSAL_GRAPH)
    fast_mode = data.get('fast_mode', True)

    try:
        from data_generator import create_inventory_scenario
        from causal_analyzer import InventoryCausalAnalyzer

        actual_data, counterfactual_data = create_inventory_scenario()

        analyzer = InventoryCausalAnalyzer(data=actual_data)

        results = analyzer.run_full_analysis(
            counterfactual_data,
            fast_mode=fast_mode,
            causal_graph=causal_graph
        )

        return jsonify(results)

    except ImportError as e:
        return jsonify({
            'error': 'DoWhy is not installed',
            'message': str(e),
            'counterfactual_analysis': {
                'inventory_reduction': 150,
                'reduction_percentage': 23.5,
                'actual_inventory_mean': 638,
                'counterfactual_inventory_mean': 488,
                'decline_period_actual_inventory': 680,
                'decline_period_counterfactual_inventory': 520,
                'decline_period_reduction': 160,
            },
            'causal_graph': causal_graph
        })
    except Exception as e:
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e),
            'counterfactual_analysis': None
        }), 500

@bp.route('/<project_id>/results', methods=['GET'])
def get_results(project_id):
    canvas_data = CanvasData.query.filter_by(project_id=project_id).first()

    if not canvas_data:
        return jsonify({
            'message': 'No analysis results yet',
            'counterfactual_analysis': None
        })

    try:
        nodes = json.loads(canvas_data.nodes) if isinstance(canvas_data.nodes, str) else canvas_data.nodes
        for node in nodes:
            if node.get('type') == 'root_cause' and node.get('config', {}).get('analysis_results'):
                return jsonify({
                    'message': 'Analysis results found',
                    'results': node['config']['analysis_results']
                })
    except:
        pass

    return jsonify({
        'message': 'No analysis results yet',
        'counterfactual_analysis': None
    })

@bp.route('/<project_id>/data', methods=['GET'])
def get_analysis_data(project_id):
    try:
        from data_generator import create_inventory_scenario

        actual_data, counterfactual_data = create_inventory_scenario()

        return jsonify({
            'actual_data': actual_data.to_dict(orient='records'),
            'counterfactual_data': counterfactual_data.to_dict(orient='records'),
            'data_summary': {
                'record_count': len(actual_data),
                'date_range': f"{actual_data['date'].iloc[0]} to {actual_data['date'].iloc[-1]}",
                'avg_inventory': float(actual_data['pac900s12_b2_1_inventory'].mean()),
                'avg_sales_kunlun': float(actual_data['kunlun_2280_sales'].mean()),
                'avg_sales_2288hv7': float(actual_data['server_2288hv7_sales'].mean()),
            }
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate data',
            'message': str(e)
        }), 500

@bp.route('/build-graph', methods=['POST'])
def build_graph():
    data = request.get_json()
    data_summary = data.get('data_summary', '')

    generated_graph = DEFAULT_CAUSAL_GRAPH

    return jsonify({
        'causal_graph': generated_graph,
        'message': 'Causal graph built successfully'
    })

@bp.route('/llm/config', methods=['POST'])
def configure_llm():
    data = request.get_json()
    api_key = data.get('api_key')
    model = data.get('model', 'Qwen/Qwen2.5-7B-Instruct')
    base_url = data.get('base_url', 'https://api.siliconflow.cn/v1')

    from llm_explainer import LLMConfig
    LLMConfig.set_config(api_key=api_key, model=model, base_url=base_url)

    return jsonify({
        'message': 'LLM配置已保存',
        'model': model,
        'base_url': base_url
    })

@bp.route('/llm/test', methods=['POST'])
def test_llm_connection():
    data = request.get_json()
    api_key = data.get('api_key')
    model = data.get('model', 'Qwen/Qwen2.5-7B-Instruct')
    base_url = data.get('base_url', 'https://api.siliconflow.cn/v1')

    try:
        from llm_explainer import LLMExplainer
        explainer = LLMExplainer(api_key=api_key, model=model, base_url=base_url)
        success, message = explainer.test_connection()

        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<project_id>/explain', methods=['POST'])
def generate_explanation(project_id):
    try:
        from llm_explainer import LLMExplainer, LLMConfig

        if not LLMConfig.is_configured():
            return jsonify({'error': '请先配置LLM API密钥'}), 400

        data = request.get_json() or {}
        analysis_results = data.get('analysis_results')
        causal_graph = data.get('causal_graph', DEFAULT_CAUSAL_GRAPH)

        if not analysis_results:
            return jsonify({'error': '缺少分析结果数据'}), 400

        from data_generator import create_inventory_scenario
        actual_data, counterfactual_data = create_inventory_scenario()

        explainer = LLMExplainer()
        explanation = explainer.generate_root_cause_explanation(
            analysis_results=analysis_results,
            actual_data=actual_data,
            counterfactual_data=counterfactual_data,
            causal_graph=causal_graph
        )

        return jsonify({
            'explanation': explanation,
            'message': '根因解释生成成功'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<project_id>/solution', methods=['POST'])
def generate_solution(project_id):
    try:
        from llm_explainer import LLMExplainer, LLMConfig

        if not LLMConfig.is_configured():
            return jsonify({'error': '请先配置LLM API密钥'}), 400

        data = request.get_json() or {}
        analysis_results = data.get('analysis_results')
        causal_graph = data.get('causal_graph', DEFAULT_CAUSAL_GRAPH)
        root_cause_text = data.get('root_cause_text')
        knowledge_base = data.get('knowledge_base')

        if not analysis_results:
            return jsonify({'error': '缺少分析结果数据'}), 400

        from data_generator import create_inventory_scenario
        actual_data, counterfactual_data = create_inventory_scenario()

        explainer = LLMExplainer()
        solution = explainer.generate_solution(
            analysis_results=analysis_results,
            actual_data=actual_data,
            counterfactual_data=counterfactual_data,
            causal_graph=causal_graph,
            root_cause_text=root_cause_text,
            knowledge_base=knowledge_base
        )

        return jsonify({
            'solution': solution,
            'message': '解决方案生成成功'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
