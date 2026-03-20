from flask import Blueprint, request, jsonify
from models import db, Dashboard
import json

bp = Blueprint('dashboards', __name__, url_prefix='/api/projects')

@bp.route('/<project_id>/dashboards', methods=['GET'])
def get_dashboards(project_id):
    """获取项目的所有看板"""
    dashboards = Dashboard.query.filter_by(project_id=project_id).all()
    return jsonify([d.to_dict() for d in dashboards])

@bp.route('/<project_id>/dashboards/<int:dashboard_id>', methods=['GET'])
def get_dashboard(project_id, dashboard_id):
    """获取指定看板详情"""
    dashboard = Dashboard.query.filter_by(id=dashboard_id, project_id=project_id).first()
    if not dashboard:
        return jsonify({'error': 'Dashboard not found'}), 404

    return jsonify(dashboard.to_dict())

@bp.route('/<project_id>/dashboards', methods=['POST'])
def create_dashboard(project_id):
    """创建新看板"""
    data = request.get_json()

    dashboard = Dashboard(
        project_id=project_id,
        name=data.get('name', '新看板'),
        data_source=json.dumps(data.get('data_source', {})),
        components=json.dumps(data.get('components', [])),
        layout=json.dumps(data.get('layout', {'columns': 12, 'rows': 8}))
    )

    db.session.add(dashboard)
    db.session.commit()

    return jsonify(dashboard.to_dict()), 201

@bp.route('/<project_id>/dashboards/<int:dashboard_id>', methods=['PUT'])
def update_dashboard(project_id, dashboard_id):
    """更新看板配置"""
    dashboard = Dashboard.query.filter_by(id=dashboard_id, project_id=project_id).first()
    if not dashboard:
        return jsonify({'error': 'Dashboard not found'}), 404

    data = request.get_json()

    if 'name' in data:
        dashboard.name = data['name']
    if 'data_source' in data:
        dashboard.data_source = json.dumps(data['data_source'])
    if 'components' in data:
        dashboard.components = json.dumps(data['components'])
    if 'layout' in data:
        dashboard.layout = json.dumps(data['layout'])

    db.session.commit()

    return jsonify(dashboard.to_dict())

@bp.route('/<project_id>/dashboards/<int:dashboard_id>', methods=['DELETE'])
def delete_dashboard(project_id, dashboard_id):
    """删除看板"""
    dashboard = Dashboard.query.filter_by(id=dashboard_id, project_id=project_id).first()
    if not dashboard:
        return jsonify({'error': 'Dashboard not found'}), 404

    db.session.delete(dashboard)
    db.session.commit()

    return jsonify({'message': 'Dashboard deleted successfully'})