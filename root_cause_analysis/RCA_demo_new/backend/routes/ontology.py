from flask import Blueprint, request, jsonify
from models import db, Ontology, OntologyClass, OntologyRelation
import json

bp = Blueprint('ontology', __name__, url_prefix='/api/projects')

@bp.route('/<project_id>/ontologies', methods=['GET'])
def get_ontologies(project_id):
    ontologies = Ontology.query.filter_by(project_id=project_id).all()
    return jsonify([o.to_dict() for o in ontologies])

@bp.route('/<project_id>/ontologies', methods=['POST'])
def create_ontology(project_id):
    data = request.get_json()

    copy_from_id = data.get('copy_from')
    if copy_from_id:
        template_ontology = Ontology.query.get(copy_from_id)
        if template_ontology:
            new_ontology = Ontology(
                project_id=project_id,
                name=data.get('name', template_ontology.name),
                description=data.get('description', template_ontology.description),
                canvas_data=template_ontology.canvas_data
            )
            db.session.add(new_ontology)
            db.session.flush()

            for cls in template_ontology.classes:
                new_cls = OntologyClass(
                    ontology_id=new_ontology.id,
                    name=cls.name,
                    description=cls.description
                )
                db.session.add(new_cls)
                db.session.flush()

                for prop in cls.properties:
                    from models import ClassProperty
                    new_prop = ClassProperty(
                        class_id=new_cls.id,
                        name=prop.name,
                        type=prop.type,
                        description=prop.description
                    )
                    db.session.add(new_prop)

            for rel in template_ontology.relations:
                new_rel = OntologyRelation(
                    ontology_id=new_ontology.id,
                    source_class_id=rel.source_class_id,
                    target_class_id=rel.target_class_id,
                    relation_type=rel.relation_type
                )
                db.session.add(new_rel)

            db.session.commit()
            return jsonify(new_ontology.to_dict()), 201

    ontology = Ontology(
        project_id=project_id,
        name=data.get('name', '新本体库'),
        description=data.get('description', ''),
        canvas_data='[]'
    )

    db.session.add(ontology)
    db.session.commit()

    return jsonify(ontology.to_dict()), 201

@bp.route('/<project_id>/ontologies/<int:ontology_id>', methods=['GET'])
def get_ontology(project_id, ontology_id):
    ontology = Ontology.query.filter_by(id=ontology_id, project_id=project_id).first()
    if not ontology:
        return jsonify({'error': 'Ontology not found'}), 404
    
    return jsonify(ontology.to_dict())

@bp.route('/<project_id>/ontologies/<int:ontology_id>', methods=['PUT'])
def update_ontology(project_id, ontology_id):
    ontology = Ontology.query.filter_by(id=ontology_id, project_id=project_id).first()
    if not ontology:
        return jsonify({'error': 'Ontology not found'}), 404
    
    data = request.get_json()
    if 'name' in data:
        ontology.name = data['name']
    if 'description' in data:
        ontology.description = data['description']
    if 'canvas_data' in data:
        ontology.canvas_data = json.dumps(data['canvas_data'])
    
    db.session.commit()
    
    return jsonify(ontology.to_dict())

@bp.route('/<project_id>/ontologies/<int:ontology_id>', methods=['DELETE'])
def delete_ontology(project_id, ontology_id):
    ontology = Ontology.query.filter_by(id=ontology_id, project_id=project_id).first()
    if not ontology:
        return jsonify({'error': 'Ontology not found'}), 404
    
    db.session.delete(ontology)
    db.session.commit()
    
    return jsonify({'message': 'Ontology deleted successfully'})

@bp.route('/<project_id>/ontologies/<int:ontology_id>/canvas', methods=['PUT'])
def save_ontology_canvas(project_id, ontology_id):
    ontology = Ontology.query.filter_by(id=ontology_id, project_id=project_id).first()
    if not ontology:
        return jsonify({'error': 'Ontology not found'}), 404
    
    data = request.get_json()
    ontology.canvas_data = json.dumps(data.get('canvas_data', []))
    db.session.commit()
    
    return jsonify(ontology.to_dict())

@bp.route('/<project_id>/ontologies/<int:ontology_id>/classes', methods=['GET'])
def get_ontology_classes(project_id, ontology_id):
    ontology = Ontology.query.filter_by(id=ontology_id, project_id=project_id).first()
    if not ontology:
        return jsonify({'error': 'Ontology not found'}), 404
    
    classes = OntologyClass.query.filter_by(ontology_id=ontology_id).all()
    return jsonify([c.to_dict() for c in classes])

@bp.route('/<project_id>/ontologies/<int:ontology_id>/classes', methods=['POST'])
def create_ontology_class(project_id, ontology_id):
    ontology = Ontology.query.filter_by(id=ontology_id, project_id=project_id).first()
    if not ontology:
        return jsonify({'error': 'Ontology not found'}), 404
    
    data = request.get_json()
    
    ontology_class = OntologyClass(
        ontology_id=ontology_id,
        name=data.get('name', '新类'),
        description=data.get('description', ''),
        properties_json='[]'
    )
    
    db.session.add(ontology_class)
    db.session.commit()
    
    return jsonify(ontology_class.to_dict()), 201

@bp.route('/<project_id>/ontologies/<int:ontology_id>/classes/<int:class_id>', methods=['PUT'])
def update_ontology_class(project_id, ontology_id, class_id):
    ontology_class = OntologyClass.query.filter_by(id=class_id, ontology_id=ontology_id).first()
    if not ontology_class:
        return jsonify({'error': 'Class not found'}), 404
    
    data = request.get_json()
    if 'name' in data:
        ontology_class.name = data['name']
    if 'description' in data:
        ontology_class.description = data['description']
    if 'properties' in data:
        ontology_class.properties_json = json.dumps(data['properties'])
    
    db.session.commit()
    
    return jsonify(ontology_class.to_dict())

@bp.route('/<project_id>/ontologies/<int:ontology_id>/classes/<int:class_id>', methods=['DELETE'])
def delete_ontology_class(project_id, ontology_id, class_id):
    ontology_class = OntologyClass.query.filter_by(id=class_id, ontology_id=ontology_id).first()
    if not ontology_class:
        return jsonify({'error': 'Class not found'}), 404
    
    OntologyRelation.query.filter(
        (OntologyRelation.source_class_id == class_id) | 
        (OntologyRelation.target_class_id == class_id)
    ).delete()
    
    db.session.delete(ontology_class)
    db.session.commit()
    
    return jsonify({'message': 'Class deleted successfully'})

@bp.route('/<project_id>/ontologies/<int:ontology_id>/classes/<int:class_id>/properties', methods=['GET'])
def get_class_properties(project_id, ontology_id, class_id):
    ontology_class = OntologyClass.query.filter_by(id=class_id, ontology_id=ontology_id).first()
    if not ontology_class:
        return jsonify({'error': 'Class not found'}), 404
    
    return jsonify(ontology_class.properties)

@bp.route('/<project_id>/ontologies/<int:ontology_id>/classes/<int:class_id>/properties', methods=['POST'])
def add_class_property(project_id, ontology_id, class_id):
    ontology_class = OntologyClass.query.filter_by(id=class_id, ontology_id=ontology_id).first()
    if not ontology_class:
        return jsonify({'error': 'Class not found'}), 404
    
    data = request.get_json()
    properties = json.loads(ontology_class.properties_json) if ontology_class.properties_json else []
    
    new_property = {
        'id': len(properties) + 1,
        'name': data.get('name', '新属性'),
        'type': data.get('type', 'string'),
        'description': data.get('description', '')
    }
    properties.append(new_property)
    ontology_class.properties_json = json.dumps(properties)
    db.session.commit()
    
    return jsonify(properties)

@bp.route('/<project_id>/ontologies/<int:ontology_id>/classes/<int:class_id>/properties/<int:prop_id>', methods=['PUT'])
def update_class_property(project_id, ontology_id, class_id, prop_id):
    ontology_class = OntologyClass.query.filter_by(id=class_id, ontology_id=ontology_id).first()
    if not ontology_class:
        return jsonify({'error': 'Class not found'}), 404
    
    data = request.get_json()
    properties = json.loads(ontology_class.properties_json) if ontology_class.properties_json else []
    
    for prop in properties:
        if prop.get('id') == prop_id:
            if 'name' in data:
                prop['name'] = data['name']
            if 'type' in data:
                prop['type'] = data['type']
            if 'description' in data:
                prop['description'] = data['description']
            break
    
    ontology_class.properties_json = json.dumps(properties)
    db.session.commit()
    
    return jsonify(properties)

@bp.route('/<project_id>/ontologies/<int:ontology_id>/classes/<int:class_id>/properties/<int:prop_id>', methods=['DELETE'])
def delete_class_property(project_id, ontology_id, class_id, prop_id):
    ontology_class = OntologyClass.query.filter_by(id=class_id, ontology_id=ontology_id).first()
    if not ontology_class:
        return jsonify({'error': 'Class not found'}), 404
    
    properties = json.loads(ontology_class.properties_json) if ontology_class.properties_json else []
    properties = [p for p in properties if p.get('id') != prop_id]
    
    ontology_class.properties_json = json.dumps(properties)
    db.session.commit()
    
    return jsonify(properties)

@bp.route('/<project_id>/ontologies/<int:ontology_id>/relations', methods=['GET'])
def get_ontology_relations(project_id, ontology_id):
    ontology = Ontology.query.filter_by(id=ontology_id, project_id=project_id).first()
    if not ontology:
        return jsonify({'error': 'Ontology not found'}), 404
    
    relations = OntologyRelation.query.filter_by(ontology_id=ontology_id).all()
    return jsonify([r.to_dict() for r in relations])

@bp.route('/<project_id>/ontologies/<int:ontology_id>/relations', methods=['POST'])
def create_ontology_relation(project_id, ontology_id):
    ontology = Ontology.query.filter_by(id=ontology_id, project_id=project_id).first()
    if not ontology:
        return jsonify({'error': 'Ontology not found'}), 404
    
    data = request.get_json()
    
    relation = OntologyRelation(
        ontology_id=ontology_id,
        source_class_id=data.get('source_class_id'),
        target_class_id=data.get('target_class_id'),
        relation_type=data.get('relation_type', 'has_relation'),
        description=data.get('description', '')
    )
    
    db.session.add(relation)
    db.session.commit()
    
    return jsonify(relation.to_dict()), 201

@bp.route('/<project_id>/ontologies/<int:ontology_id>/relations/<int:relation_id>', methods=['DELETE'])
def delete_ontology_relation(project_id, ontology_id, relation_id):
    relation = OntologyRelation.query.filter_by(id=relation_id, ontology_id=ontology_id).first()
    if not relation:
        return jsonify({'error': 'Relation not found'}), 404
    
    db.session.delete(relation)
    db.session.commit()
    
    return jsonify({'message': 'Relation deleted successfully'})
