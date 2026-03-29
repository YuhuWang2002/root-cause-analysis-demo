import os
from flask import Blueprint, request, jsonify
from cog.torque import Graph

bp = Blueprint('graph_query', __name__, url_prefix='/api/projects')

GRAPH_CACHE = {}

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_graph(ontology_name, cog_home="data", cog_path_prefix=None):
    if cog_path_prefix is None:
        cog_path_prefix = BACKEND_DIR
    
    cache_key = ontology_name
    if cache_key in GRAPH_CACHE:
        return GRAPH_CACHE[cache_key]
    
    g = Graph(ontology_name, cog_home=cog_home, cog_path_prefix=cog_path_prefix)
    GRAPH_CACHE[cache_key] = g
    return g


def _filter_items(g, items, property_name, operator, value):
    op = str(operator).lower()
    result = []
    
    for item in items:
        item_id = item.get('id')
        if not item_id:
            continue
        
        prop_value = ''
        try:
            prop_result = g.v(item_id).out(property_name).all().get('result', [])
            if prop_result and len(prop_result) > 0:
                prop_value = prop_result[0].get('id', '')
        except Exception:
            pass
        
        if op == 'contains':
            if str(value) in str(prop_value):
                result.append(item)
        elif op == 'not_contains':
            if str(value) not in str(prop_value):
                result.append(item)
        elif op in ('equals', 'eq', '='):
            if str(prop_value) == str(value):
                result.append(item)
        elif op in ('not_equals', 'ne', '!='):
            if str(prop_value) != str(value):
                result.append(item)
        elif op in ('gt', '>'):
            try:
                if float(prop_value) > float(value):
                    result.append(item)
            except (ValueError, TypeError):
                if str(prop_value) > str(value):
                    result.append(item)
        elif op in ('gte', '>='):
            try:
                if float(prop_value) >= float(value):
                    result.append(item)
            except (ValueError, TypeError):
                if str(prop_value) >= str(value):
                    result.append(item)
        elif op in ('lt', '<'):
            try:
                if float(prop_value) < float(value):
                    result.append(item)
            except (ValueError, TypeError):
                if str(prop_value) < str(value):
                    result.append(item)
        elif op in ('lte', '<='):
            try:
                if float(prop_value) <= float(value):
                    result.append(item)
            except (ValueError, TypeError):
                if str(prop_value) <= str(value):
                    result.append(item)
        elif op == 'startswith':
            if str(prop_value).startswith(str(value)):
                result.append(item)
        elif op == 'endswith':
            if str(prop_value).endswith(str(value)):
                result.append(item)
        elif op == 'in':
            if isinstance(value, list):
                if str(prop_value) in [str(x) for x in value]:
                    result.append(item)
            else:
                if str(value) in str(prop_value):
                    result.append(item)
        else:
            if str(value) in str(prop_value):
                result.append(item)
    
    return result


def apply_filters(g, items, filters):
    items_filtered = items
    for f in filters:
        if isinstance(f, dict):
            property_name = f.get('property') or f.get('field')
            operator = f.get('operator') or f.get('op', 'contains')
            value = f.get('value')
            if property_name and value is not None:
                items_filtered = _filter_items(g, items_filtered, property_name, operator, value)
        elif isinstance(f, str):
            items_filtered = [item for item in items_filtered if f in str(item.get('id', ''))]
    return items_filtered


def query_branch(g, parent_node_ids, relation, filters):
    all_items = []
    
    for node_id in parent_node_ids:
        query = g.v(node_id).out(relation)
        result = query.all()
        items = result.get('result', [])
        all_items.extend(items)
    
    unique_items = []
    seen_ids = set()
    for item in all_items:
        item_id = item.get('id')
        if item_id and item_id not in seen_ids:
            seen_ids.add(item_id)
            unique_items.append(item)
    
    filtered_items = apply_filters(g, unique_items, filters)
    node_ids = [item.get('id') for item in filtered_items]
    
    return node_ids, filtered_items


def process_query_tree(g, query_tree, parent_node_ids=None, step=0):
    node_type = query_tree.get('node_type')
    filters = query_tree.get('filters', [])
    children = query_tree.get('children', [])
    
    if parent_node_ids is None:
        query = g.v().has("type", node_type)
        result = query.all()
        items = result.get('result', [])
        filtered_items = apply_filters(g, items, filters)
        node_ids = [item.get('id') for item in filtered_items]
    else:
        relation = query_tree.get('relation')
        if not relation:
            return None
        
        node_ids, filtered_items = query_branch(g, parent_node_ids, relation, filters)
    
    result = {
        'step': step,
        'node_type': node_type,
        'count': len(node_ids),
        'results': node_ids[:100],
        'filters': filters,
        'children': []
    }
    
    for child in children:
        child_result = process_query_tree(g, child, node_ids, step + 1)
        if child_result:
            if 'relation' in child:
                child_result['relation'] = child['relation']
            result['children'].append(child_result)
    
    return result


@bp.route('/<project_id>/ontologies/<ontology_id>/graph/query', methods=['POST'])
def graph_query(project_id, ontology_id):
    data = request.get_json()
    
    print('=== graph_query debug ===')
    print('Received data:', data)
    print('Has queries key?', 'queries' in data)
    print('Has query key?', 'query' in data)
    
    ontology = data.get('ontology', 'server_manufacturing_cog_graph')
    
    if 'queries' in data:
        queries = data.get('queries', [])
        print('Processing multi-root queries:', queries)
        if not isinstance(queries, list):
            return jsonify({'error': 'Queries must be an array'}), 400
        
        try:
            g = get_graph(ontology, cog_home="data", cog_path_prefix=BACKEND_DIR)
        except Exception as e:
            return jsonify({'error': f'Failed to connect to graph: {str(e)}'}), 500
        
        results = []
        for query_tree in queries:
            if not query_tree or 'node_type' not in query_tree:
                return jsonify({'error': 'Invalid query tree format in queries array'}), 400
            result = process_query_tree(g, query_tree)
            if result:
                results.append(result)
        
        return jsonify({
            'query_results': results
        })
    
    elif 'query' in data:
        query_tree = data.get('query')
        print('Processing tree query:', query_tree)
        if not query_tree or 'node_type' not in query_tree:
            return jsonify({'error': 'Invalid query tree format'}), 400
        
        try:
            g = get_graph(ontology, cog_home="data", cog_path_prefix=BACKEND_DIR)
        except Exception as e:
            return jsonify({'error': f'Failed to connect to graph: {str(e)}'}), 500
        
        result = process_query_tree(g, query_tree)
        
        return jsonify({
            'query_result': result
        })
    
    else:
        return jsonify({'error': 'Invalid request format. Must provide either "queries" (array) or "query" (object)'}), 400


@bp.route('/<project_id>/ontologies/<ontology_id>/graph/nodes', methods=['GET'])
def get_graph_nodes(project_id, ontology_id):
    ontology = request.args.get('ontology', 'server_manufacturing_cog_graph')
    entity_type = request.args.get('type')
    
    try:
        g = get_graph(ontology, cog_home="data", cog_path_prefix=BACKEND_DIR)
    except Exception as e:
        return jsonify({'error': f'Failed to connect to graph: {str(e)}'}), 500
    
    if entity_type:
        query = g.v().has("type", entity_type)
    else:
        query = g.v()
    
    result = query.all()
    items = result.get('result', [])
    
    nodes = []
    for item in items:
        nodes.append({
            'id': item.get('id'),
            'properties': item
        })
    
    return jsonify({
        'nodes': nodes
    })


@bp.route('/<project_id>/ontologies/<ontology_id>/graph/relations', methods=['GET'])
def get_graph_relations(project_id, ontology_id):
    ontology = request.args.get('ontology', 'server_manufacturing_cog_graph')
    node_id = request.args.get('node_id')
    
    if not node_id:
        return jsonify({'error': 'node_id is required'}), 400
    
    try:
        g = get_graph(ontology, cog_home="data", cog_path_prefix=BACKEND_DIR)
    except Exception as e:
        return jsonify({'error': f'Failed to connect to graph: {str(e)}'}), 500
    
    outgoing_query = g.v(node_id).outE()
    outgoing_result = outgoing_query.all()
    outgoing_edges = outgoing_result.get('result', [])
    
    incoming_query = g.v(node_id).inE()
    incoming_result = incoming_query.all()
    incoming_edges = incoming_result.get('result', [])
    
    return jsonify({
        'outgoing': outgoing_edges,
        'incoming': incoming_edges
    })
