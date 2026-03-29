import sys
sys.path.insert(0, '.')

from app import create_app
from models import db, Ontology, OntologyClass

app = create_app()

with app.app_context():
    print("=" * 50)
    print("Ontology ID 1 (server_manufacturing_cog_graph) classes:")
    print("=" * 50)
    
    ontology = Ontology.query.get(1)
    if ontology:
        print(f"Ontology name: {ontology.name}")
        print(f"\nClasses count: {len(ontology.ontology_classes)}")
        
        for cls in ontology.ontology_classes[:5]:
            print(f"\n  Class ID: {cls.id}")
            print(f"  class_id: {cls.class_id}")
            print(f"  name: {cls.name}")
