from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    canvas_data = db.relationship('CanvasData', backref='project', uselist=False, cascade='all, delete-orphan')
    node_configs = db.relationship('NodeConfig', backref='project', cascade='all, delete-orphan')
    ontologies = db.relationship('Ontology', backref='project', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class CanvasData(db.Model):
    __tablename__ = 'canvas_data'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), unique=True, nullable=False)
    nodes = db.Column(db.Text, default='[]')
    connections = db.Column(db.Text, default='[]')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'nodes': json.loads(self.nodes) if self.nodes else [],
            'connections': json.loads(self.connections) if self.connections else [],
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class NodeConfig(db.Model):
    __tablename__ = 'node_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    node_id = db.Column(db.String(100), nullable=False)
    config_json = db.Column(db.Text, default='{}')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'node_id', name='unique_project_node'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'node_id': self.node_id,
            'config': json.loads(self.config_json) if self.config_json else {},
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Ontology(db.Model):
    __tablename__ = 'ontologies'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    canvas_data = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ontology_classes = db.relationship('OntologyClass', backref='ontology', cascade='all, delete-orphan')
    relations = db.relationship('OntologyRelation', backref='ontology', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'canvas_data': json.loads(self.canvas_data) if self.canvas_data else [],
            'classes': [c.to_dict() for c in self.ontology_classes],
            'relations': [r.to_dict() for r in self.relations],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class OntologyClass(db.Model):
    __tablename__ = 'ontology_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    ontology_id = db.Column(db.Integer, db.ForeignKey('ontologies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    properties_json = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ontology_id': self.ontology_id,
            'name': self.name,
            'description': self.description,
            'properties': json.loads(self.properties_json) if self.properties_json else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class OntologyRelation(db.Model):
    __tablename__ = 'ontology_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    ontology_id = db.Column(db.Integer, db.ForeignKey('ontologies.id'), nullable=False)
    source_class_id = db.Column(db.Integer, db.ForeignKey('ontology_classes.id'), nullable=False)
    target_class_id = db.Column(db.Integer, db.ForeignKey('ontology_classes.id'), nullable=False)
    relation_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    source_class = db.relationship('OntologyClass', foreign_keys=[source_class_id])
    target_class = db.relationship('OntologyClass', foreign_keys=[target_class_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'ontology_id': self.ontology_id,
            'source_class_id': self.source_class_id,
            'target_class_id': self.target_class_id,
            'relation_type': self.relation_type,
            'description': self.description,
            'source_class_name': self.source_class.name if self.source_class else None,
            'target_class_name': self.target_class.name if self.target_class else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
