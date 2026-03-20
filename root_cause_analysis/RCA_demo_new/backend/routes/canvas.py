from flask import Blueprint, request, jsonify
from models import db, CanvasData
import json

bp = Blueprint('canvas', __name__, url_prefix='/api/projects')

@bp.route('/<project_id>/canvas', methods=['GET'])
def get_canvas(project_id):
    canvas_data = CanvasData.query.filter_by(project_id=project_id).first()
    
    if not canvas_data:
        return jsonify({
            'project_id': project_id,
            'nodes': [],
            'connections': []
        })
    
    return jsonify(canvas_data.to_dict())

@bp.route('/<project_id>/canvas', methods=['PUT'])
def save_canvas(project_id):
    data = request.get_json()
    
    canvas_data = CanvasData.query.filter_by(project_id=project_id).first()
    
    nodes_json = json.dumps(data.get('nodes', []))
    connections_json = json.dumps(data.get('connections', []))
    
    if canvas_data:
        canvas_data.nodes = nodes_json
        canvas_data.connections = connections_json
    else:
        canvas_data = CanvasData(
            project_id=project_id,
            nodes=nodes_json,
            connections=connections_json
        )
        db.session.add(canvas_data)
    
    db.session.commit()
    
    return jsonify(canvas_data.to_dict())
