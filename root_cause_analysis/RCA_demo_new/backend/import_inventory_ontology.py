import json
import requests

BASE_URL = "http://localhost:5000/api"

PROJECT_ID = "09778791-9c38-4be2-8559-d30cf635f0b7"

def create_ontology(project_id, name, description=""):
    """创建本体库"""
    url = f"{BASE_URL}/projects/{project_id}/ontologies"
    data = {
        "name": name,
        "description": description
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        ontology = response.json()
        print(f"✓ Created ontology: {ontology['name']} (ID: {ontology['id']})")
        return ontology
    else:
        print(f"✗ Failed to create ontology: {response.text}")
        return None

def create_ontology_class(project_id, ontology_id, class_data):
    """创建本体类"""
    url = f"{BASE_URL}/projects/{project_id}/ontologies/{ontology_id}/classes"
    response = requests.post(url, json=class_data)
    if response.status_code in [200, 201]:
        cls = response.json()
        print(f"  ✓ Created class: {cls['name']} (ID: {cls['id']})")
        return cls
    else:
        print(f"  ✗ Failed to create class: {response.text}")
        return None

def add_class_property(project_id, ontology_id, class_id, property_data):
    """添加类属性"""
    url = f"{BASE_URL}/projects/{project_id}/ontologies/{ontology_id}/classes/{class_id}/properties"
    response = requests.post(url, json=property_data)
    if response.status_code in [200, 201]:
        props = response.json()
        if isinstance(props, list) and len(props) > 0:
            prop = props[0]
            print(f"    ✓ Added property: {prop['name']} ({prop.get('type', 'string')})")
            return prop
        elif isinstance(props, dict):
            print(f"    ✓ Added property: {props['name']} ({props.get('type', 'string')})")
            return props
        return props
    else:
        print(f"    ✗ Failed to add property: {response.text}")
        return None

def create_ontology_relation(project_id, ontology_id, relation_data):
    """创建本体关系"""
    url = f"{BASE_URL}/projects/{project_id}/ontologies/{ontology_id}/relations"
    response = requests.post(url, json=relation_data)
    if response.status_code in [200, 201]:
        rel = response.json()
        print(f"  ✓ Created relation: {rel['relation_type']}")
        return rel
    else:
        print(f"  ✗ Failed to create relation: {response.text}")
        return None

def main():
    schema_path = "/Users/yuhuwang/Documents/trae_projects/root_cause_analysis/inventory_rca_demo/server_inventory_schema.json"

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    print("=" * 60)
    print("Importing Inventory Analysis Ontology")
    print("=" * 60)

    ontology = create_ontology(PROJECT_ID, "库存分析本体库", "基于服务器库存分析的本体库")
    if not ontology:
        print("Failed to create ontology. Exiting.")
        return

    ontology_id = ontology['id']

    class_map = {}

    print("\n--- Creating Entity Classes ---")
    for entity in schema.get('entity_types', []):
        class_data = {
            "name": entity['name'],
            "description": entity.get('description', '')
        }
        cls = create_ontology_class(PROJECT_ID, ontology_id, class_data)
        if cls:
            class_map[entity['id']] = cls['id']

    print("\n--- Adding Properties to Classes ---")
    for entity in schema.get('entity_types', []):
        class_id = class_map.get(entity['id'])
        if not class_id:
            continue

        for attr in entity.get('attributes', []):
            property_data = {
                "name": attr['name'],
                "type": attr.get('type', 'string'),
                "description": attr.get('description', '')
            }

            if 'fieldName' in attr:
                property_data['field_name'] = attr['fieldName']
            if 'unit' in attr:
                property_data['unit'] = attr['unit']
            if 'dataType' in attr:
                property_data['data_type'] = attr['dataType']
            if 'value' in attr:
                property_data['default_value'] = attr['value']

            add_class_property(PROJECT_ID, ontology_id, class_id, property_data)

    print("\n--- Creating Relations ---")
    for relation in schema.get('relation_types', []):
        source_ids = []
        target_ids = []

        for source_type in relation.get('source_types', []):
            if source_type in class_map:
                source_ids.append(class_map[source_type])

        for target_type in relation.get('target_types', []):
            if target_type in class_map:
                target_ids.append(class_map[target_type])

        for source_id in source_ids:
            for target_id in target_ids:
                relation_data = {
                    "source_class_id": source_id,
                    "target_class_id": target_id,
                    "relation_type": f"{relation['name']} ({relation.get('id', '')})"
                }
                create_ontology_relation(PROJECT_ID, ontology_id, relation_data)

    print("\n" + "=" * 60)
    print("Import completed!")
    print("=" * 60)
    print(f"Total classes: {len(class_map)}")
    print(f"Ontology ID: {ontology_id}")

if __name__ == "__main__":
    main()
