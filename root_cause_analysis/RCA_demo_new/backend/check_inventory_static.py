import sys
from cog.torque import Graph

DB_NAME = "server_inventory_graph"
COG_HOME = "data"
COG_PATH_PREFIX = "."

print("=" * 50)
print(f"Checking specific static nodes in: {DB_NAME}")
print("=" * 50)

g = Graph(DB_NAME, cog_home=COG_HOME, cog_path_prefix=COG_PATH_PREFIX)

static_nodes_to_check = [
    "Supplier A",
    "Power Supply 02313XSF",
    "KunLun 2280",
    "2288HV7",
    "KunLun 2280 Order",
    "2288HV7 Order"
]

for node_name in static_nodes_to_check:
    try:
        result = g.v(node_name).all()
        if result.get('result') and len(result.get('result')) > 0:
            print(f"\n✅ Found: {node_name}")
            
            # 检查 type 属性
            type_result = g.v(node_name).out("type").all().get('result', [])
            if type_result:
                print(f"   type: {type_result[0].get('id')}")
            
            # 检查其他属性
            all_outs = g.v(node_name).out().all().get('result', [])
            print(f"   Other properties/edges: {len(all_outs)}")
            for out in all_outs[:5]:
                print(f"     - {out.get('id')}")
        else:
            print(f"\n❌ NOT found: {node_name}")
    except Exception as e:
        print(f"\n❌ Error checking {node_name}: {e}")

print("\n" + "=" * 50)
print("All Order nodes (first 10):")
print("=" * 50)
all_orders = g.v().has("type", "Order").all().get('result', [])
print(f"Total Orders: {len(all_orders)}")
for order in all_orders[:10]:
    print(f"  - {order.get('id')}")
