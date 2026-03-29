import sys
import json
sys.path.insert(0, '.')

from app import create_app
from models import db, Ontology, OntologyClass

app = create_app()

schema_path = '../../inventory_rca_demo/server_inventory_schema.json'

with open(schema_path, 'r', encoding='utf-8') as f:
    schema = json.load(f)

entity_type_map = {}
for entity in schema['entity_types']:
    # entity['id'] 是具体节点名（如 "Supplier A"）
    # entity['type'] 才是真正的类型（如 "Supplier"）
    entity_type_map[entity['id']] = entity.get('type', entity['id'])

print("=" * 50)
print("Fixing Ontology ID 5 (server_inventory_graph) classes")
print("=" * 50)
print("\nEntity type mapping from schema:")
for old_id, new_id in entity_type_map.items():
    print(f"  {old_id} -> {new_id}")

with app.app_context():
    ontology = Ontology.query.get(5)
    if not ontology:
        print("\nOntology not found!")
        sys.exit(1)
    
    print(f"\nOntology name: {ontology.name}")
    print(f"Current classes count: {len(ontology.ontology_classes)}")
    
    updated_count = 0
    for cls in ontology.ontology_classes:
        old_class_id = cls.class_id
        if old_class_id in entity_type_map:
            new_class_id = entity_type_map[old_class_id]
            if old_class_id != new_class_id:
                print(f"\n  Updating class {cls.id}:")
                print(f"    Old class_id: {old_class_id}")
                print(f"    New class_id: {new_class_id}")
                cls.class_id = new_class_id
                updated_count += 1
    
    if updated_count > 0:
        db.session.commit()
        print(f"\n✅ Updated {updated_count} classes!")
    else:
        print("\n✅ No updates needed!")
    
    print("\n" + "=" * 50)
    print("Final classes:")
    print("=" * 50)
    for cls in ontology.ontology_classes:
        print(f"  {cls.id}: class_id={cls.class_id}, name={cls.name}")
