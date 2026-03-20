from flask import Blueprint, request, jsonify
from models import db, NodeConfig
import json

bp = Blueprint('nodes', __name__, url_prefix='/api/projects')

@bp.route('/<project_id>/nodes/<node_id>/config', methods=['GET'])
def get_node_config(project_id, node_id):
    node_config = NodeConfig.query.filter_by(project_id=project_id, node_id=node_id).first()
    
    if not node_config:
        return jsonify({
            'project_id': project_id,
            'node_id': node_id,
            'config': {}
        })
    
    return jsonify(node_config.to_dict())

@bp.route('/<project_id>/nodes/<node_id>/config', methods=['PUT'])
def save_node_config(project_id, node_id):
    data = request.get_json()
    
    node_config = NodeConfig.query.filter_by(project_id=project_id, node_id=node_id).first()
    
    config_json = json.dumps(data.get('config', {}))
    
    if node_config:
        node_config.config_json = config_json
    else:
        node_config = NodeConfig(
            project_id=project_id,
            node_id=node_id,
            config_json=config_json
        )
        db.session.add(node_config)
    
    db.session.commit()
    
    return jsonify(node_config.to_dict())

@bp.route('/<project_id>/nodes/configs', methods=['GET'])
def get_all_node_configs(project_id):
    configs = NodeConfig.query.filter_by(project_id=project_id).all()
    return jsonify([c.to_dict() for c in configs])

@bp.route('/<project_id>/nodes/configs', methods=['PUT'])
def save_all_node_configs(project_id):
    data = request.get_json()
    configs = data.get('configs', [])
    
    for config_data in configs:
        node_id = config_data.get('node_id')
        if not node_id:
            continue
            
        node_config = NodeConfig.query.filter_by(project_id=project_id, node_id=node_id).first()
        
        config_json = json.dumps(config_data.get('config', {}))
        
        if node_config:
            node_config.config_json = config_json
        else:
            node_config = NodeConfig(
                project_id=project_id,
                node_id=node_id,
                config_json=config_json
            )
            db.session.add(node_config)
    
    db.session.commit()
    
    return jsonify({'message': 'Configs saved successfully'})
