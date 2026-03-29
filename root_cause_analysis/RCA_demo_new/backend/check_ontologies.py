import sys
import os
sys.path.insert(0, '.')

from app import create_app
from models import db, Ontology

app = create_app()

with app.app_context():
    print("=" * 50)
    print("Current ontologies in database:")
    print("=" * 50)
    
    ontologies = Ontology.query.all()
    
    for o in ontologies:
        print(f"\nID: {o.id}")
        print(f"Name: {o.name}")
        print(f"Description: {o.description}")
        print(f"Project ID: {o.project_id}")
        print(f"Classes count: {len(o.ontology_classes)}")
        print(f"Relations count: {len(o.relations)}")
