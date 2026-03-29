import sys
from cog.torque import Graph

DB_NAME = "server_inventory_graph"
COG_HOME = "data"
COG_PATH_PREFIX = "."

print("=" * 50)
print(f"Checking graph: {DB_NAME}")
print("=" * 50)

try:
    g = Graph(DB_NAME, cog_home=COG_HOME, cog_path_prefix=COG_PATH_PREFIX)
    
    print("\n1. Query all Suppliers:")
    result = g.v().has("type", "Supplier").all()
    suppliers = result.get('result', [])
    print(f"   Found {len(suppliers)} suppliers")
    for s in suppliers:
        print(f"   - {s.get('id')}")
    
    print("\n2. Query all Orders:")
    result = g.v().has("type", "Order").all()
    orders = result.get('result', [])
    print(f"   Found {len(orders)} orders")
    for o in orders[:5]:
        print(f"   - {o.get('id')}")
    
    print("\n3. Query all Servers:")
    result = g.v().has("type", "Server").all()
    servers = result.get('result', [])
    print(f"   Found {len(servers)} servers")
    for s in servers[:5]:
        print(f"   - {s.get('id')}")
    
    print("\n4. Query all Parts:")
    result = g.v().has("type", "Part").all()
    parts = result.get('result', [])
    print(f"   Found {len(parts)} parts")
    for p in parts[:5]:
        print(f"   - {p.get('id')}")
    
    print("\n5. All node types in graph:")
    all_nodes = g.v().all().get('result', [])
    type_counts = {}
    for node in all_nodes:
        node_id = node.get('id', '')
        try:
            types = g.v(node_id).out("type").all().get('result', [])
            for t in types:
                type_name = t.get('id', '')
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
        except:
            pass
    
    for type_name, count in sorted(type_counts.items()):
        print(f"   {type_name}: {count}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
