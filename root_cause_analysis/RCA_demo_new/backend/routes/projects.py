from flask import Blueprint, request, jsonify
from models import db, Project, Ontology
import uuid
from datetime import datetime

bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@bp.route('', methods=['GET'])
def get_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify([p.to_dict() for p in projects])

@bp.route('', methods=['POST'])
def create_project():
    data = request.get_json()

    project = Project(
        id=str(uuid.uuid4()),
        name=data.get('name', '新项目'),
        description=data.get('description', ''),
        status=data.get('status', 'draft'),
        progress=data.get('progress', 0)
    )

    db.session.add(project)
    db.session.flush()

    default_ontology = Ontology(
        project_id=project.id,
        name='默认本体库',
        description='项目默认本体库',
        canvas_data='[]'
    )
    db.session.add(default_ontology)
    db.session.flush()

    template_ontology_id = 18
    template_ontology = Ontology.query.get(template_ontology_id)
    if template_ontology:
        inventory_ontology = Ontology(
            project_id=project.id,
            name='库存分析本体库',
            description=template_ontology.description,
            canvas_data=template_ontology.canvas_data
        )
        db.session.add(inventory_ontology)
        db.session.flush()

        class_id_mapping = {}
        for cls in template_ontology.ontology_classes:
            from models import OntologyClass
            new_cls = OntologyClass(
                ontology_id=inventory_ontology.id,
                name=cls.name,
                description=cls.description,
                properties_json=cls.properties_json
            )
            db.session.add(new_cls)
            db.session.flush()
            class_id_mapping[cls.id] = new_cls.id

        for rel in template_ontology.relations:
            from models import OntologyRelation as Rel
            new_rel = Rel(
                ontology_id=inventory_ontology.id,
                source_class_id=class_id_mapping.get(rel.source_class_id, rel.source_class_id),
                target_class_id=class_id_mapping.get(rel.target_class_id, rel.target_class_id),
                relation_type=rel.relation_type
            )
            db.session.add(new_rel)

    db.session.commit()

    return jsonify(project.to_dict()), 201

@bp.route('/<project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify(project.to_dict())

@bp.route('/<project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']
    if 'progress' in data:
        project.progress = data['progress']
    
    project.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(project.to_dict())

@bp.route('/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'})
