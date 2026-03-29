import json
import os
from datetime import datetime, timedelta
from cog.torque import Graph

DB_NAME = "server_inventory_graph"
COG_HOME = "data"
COG_PATH_PREFIX = os.path.dirname(__file__)

def load_ontology():
    ontology_path = os.path.join(os.path.dirname(__file__), "server_inventory_schema.json")
    with open(ontology_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_date_range(days=30):
    dates = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates

def create_triples():
    ontology = load_ontology()
    triples = []
    
    entity_attrs = {}
    for entity in ontology["entity_types"]:
        entity_attrs[entity["id"]] = entity.get("attributes", [])
    
    print("Building triples list...")
    
    dates = generate_date_range(30)
    
    # 1. 添加静态实体
    print("\n  Adding static entities...")
    
    # Supplier A
    triples.append(("Supplier A", "type", "Supplier"))
    triples.append(("Supplier A", "supplierCode", "SUP-A"))
    
    # Power Supply 02313XSF
    triples.append(("Power Supply 02313XSF", "type", "Product"))
    triples.append(("Power Supply 02313XSF", "productCode", "02313XSF"))
    triples.append(("Power Supply 02313XSF", "producedBy", "Supplier A"))
    
    # Servers
    servers = [
        ("KunLun 2280", "EW073063", "CN"),
        ("2288HV7", "EW072949", "CN")
    ]
    for name, code, country in servers:
        triples.append((name, "type", "Server"))
        triples.append((name, "productCode", code))
        triples.append((name, "countryCode", country))
    
    # Orders
    orders = [
        ("KunLun 2280 Order", "ORD-KL2280"),
        ("2288HV7 Order", "ORD-2288HV7")
    ]
    for name, order_id in orders:
        triples.append((name, "type", "Order"))
        triples.append((name, "orderId", order_id))
    
    # PartTypes
    part_types = [
        "KunLun 2280 Power",
        "KunLun 2280 CPU",
        "KunLun 2280 Disk",
        "KunLun 2280 Memory",
        "2288HV7 Power",
        "2288HV7 CPU",
        "2288HV7 Disk",
        "2288HV7 Memory"
    ]
    for pt in part_types:
        triples.append((pt, "type", "PartType"))
    
    # Parts
    parts = [
        ("PAC900S12-B2-1", "02313XSF"),
        ("PAC2000S12-B1", "0231Y019"),
        ("S920S00", "03050SNB"),
        ("S920X00", "03050SND"),
        ("PM893-480GB", "0255Y819"),
        ("ST-4000GB-SATA", "0254Y524"),
        ("BC82M32G46-32GB", "2510318"),
        ("PAC900S12-B2", "02313XSF"),
        ("PAC1500S12-B1", "0231Y033"),
        ("BC1CPU6544Y", "0253Y909"),
        ("BC7MX001CPU", "0253Y163"),
        ("BC7MX093CPU", "0253Y322"),
        ("SAS-600GB-10K", "0254Y057"),
        ("UH631a-1600GB", "0255YCDN"),
        ("DDR5-32GB-5600", "0620Y029"),
        ("DDR5-64GB-5600", "0620Y031")
    ]
    for name, code in parts:
        triples.append((name, "type", "Part"))
        triples.append((name, "productCode", code))
    
    print(f"  Added {len(servers) + len(orders) + len(part_types) + len(parts) + 2} static entities")
    
    # 2. 添加关系
    print("\n  Adding relationships...")
    
    # Supplier produces product
    triples.append(("Supplier A", "supplier_produces", "Power Supply 02313XSF"))
    
    # Product procures to parts
    triples.append(("Power Supply 02313XSF", "power_procure_kunlun", "PAC900S12-B2-1"))
    triples.append(("Power Supply 02313XSF", "power_procure_hv7", "PAC900S12-B2"))
    
    # Parts used by servers
    triples.append(("PAC900S12-B2-1", "part_used_by_kunlun2280", "KunLun 2280"))
    triples.append(("PAC900S12-B2", "part_used_by_hv7", "2288HV7"))
    triples.append(("S920S00", "kunlun2280_cpu_used_by", "KunLun 2280"))
    triples.append(("S920X00", "kunlun2280_cpu_used_by", "KunLun 2280"))
    triples.append(("PM893-480GB", "kunlun2280_disk_used_by", "KunLun 2280"))
    triples.append(("ST-4000GB-SATA", "kunlun2280_disk_used_by", "KunLun 2280"))
    triples.append(("BC82M32G46-32GB", "kunlun2280_memory_used_by", "KunLun 2280"))
    triples.append(("BC1CPU6544Y", "hv7_cpu_used_by", "2288HV7"))
    triples.append(("BC7MX001CPU", "hv7_cpu_used_by", "2288HV7"))
    triples.append(("BC7MX093CPU", "hv7_cpu_used_by", "2288HV7"))
    triples.append(("SAS-600GB-10K", "hv7_disk_used_by", "2288HV7"))
    triples.append(("UH631a-1600GB", "hv7_disk_used_by", "2288HV7"))
    triples.append(("DDR5-32GB-5600", "hv7_memory_used_by", "2288HV7"))
    triples.append(("DDR5-64GB-5600", "hv7_memory_used_by", "2288HV7"))
    
    # Servers generate orders
    triples.append(("KunLun 2280", "kunlun2280_generates_order", "KunLun 2280 Order"))
    triples.append(("2288HV7", "hv7_generates_order", "2288HV7 Order"))
    
    print("  Added static relationships")
    
    # 3. 生成30天的动态数据
    print("\n  Generating 30-day dynamic data...")
    
    daily_part_count = 0
    daily_server_count = 0
    daily_order_count = 0
    
    for day_idx, date in enumerate(dates):
        batch_id = f"BATCH-{date.replace('-', '')}"
        
        # 每日动态零件数据
        for part_name, part_code in parts:
            daily_name = f"{part_name}-{batch_id}"
            
            triples.append((daily_name, "type", "Part"))
            triples.append((daily_name, "name", daily_name))
            triples.append((daily_name, "productCode", part_code))
            triples.append((daily_name, "batch", batch_id))
            triples.append((daily_name, "date", date))
            triples.append((daily_name, "consumption", str(100 + day_idx * 10)))
            triples.append((daily_name, "inventory", str(200 + day_idx * 15)))
            triples.append((daily_name, "procurement", str(150 + day_idx * 8)))
            
            # 链接到原始零件类型
            triples.append((part_name, "has_daily_data", daily_name))
            
            daily_part_count += 1
        
        # 每日动态服务器数据
        for server_name, server_code, country in servers:
            daily_server_name = f"{server_name}-{batch_id}"
            
            triples.append((daily_server_name, "type", "Server"))
            triples.append((daily_server_name, "name", daily_server_name))
            triples.append((daily_server_name, "productCode", server_code))
            triples.append((daily_server_name, "countryCode", country))
            triples.append((daily_server_name, "batch", batch_id))
            triples.append((daily_server_name, "date", date))
            triples.append((daily_server_name, "sales", str(50 + day_idx * 5)))
            
            triples.append((server_name, "has_daily_data", daily_server_name))
            
            daily_server_count += 1
        
        # 每日动态订单数据
        for order_name, order_id in orders:
            daily_order_name = f"{order_name}-{batch_id}"
            
            triples.append((daily_order_name, "type", "Order"))
            triples.append((daily_order_name, "name", daily_order_name))
            triples.append((daily_order_name, "orderId", order_id))
            triples.append((daily_order_name, "batch", batch_id))
            triples.append((daily_order_name, "date", date))
            triples.append((daily_order_name, "sales", str(30 + day_idx * 3)))
            
            triples.append((order_name, "has_daily_data", daily_order_name))
            
            daily_order_count += 1
    
    print(f"  Added {daily_part_count} daily part records (30 days x {len(parts)})")
    print(f"  Added {daily_server_count} daily server records (30 days x {len(servers)})")
    print(f"  Added {daily_order_count} daily order records (30 days x {len(orders)})")
    
    return triples

def import_data():
    print("=" * 50)
    print("Creating inventory graph data with CogDB")
    print("=" * 50)
    
    triples = create_triples()
    
    print(f"\nTotal triples to import: {len(triples)}")
    
    print("\nImporting to CogDB (using put_batch)...")
    g = Graph(DB_NAME, cog_home=COG_HOME, cog_path_prefix=COG_PATH_PREFIX, flush_interval=1000)
    
    g.put_batch(triples)
    g.sync()
    
    print("Import complete!")
    return g

def verify_graph(g):
    print("\n" + "=" * 50)
    print("Verifying graph data")
    print("=" * 50)
    
    print("\n1. Query all Suppliers:")
    result = g.v().has("type", "Supplier").all()
    print(f"   Found {len(result.get('result', []))} suppliers")
    
    print("\n2. Query all Servers:")
    result = g.v().has("type", "Server").all()
    print(f"   Found {len(result.get('result', []))} servers (including daily data)")
    
    print("\n3. Query all Parts:")
    result = g.v().has("type", "Part").all()
    print(f"   Found {len(result.get('result', []))} parts (including daily data)")
    
    print("\n4. Query static Servers only:")
    static_servers = ["KunLun 2280", "2288HV7"]
    for server in static_servers:
        result = g.v(server).all()
        if result.get('result'):
            print(f"   - {server} exists")
    
    print("\n5. Query daily data for KunLun 2280 (sample):")
    all_servers = g.v().has("type", "Server").all().get('result', [])
    daily_servers = [s for s in all_servers if s.get('id', '').startswith('KunLun 2280-')][:3]
    print(f"   Found {len(daily_servers)} sample daily records")
    
    print("\n6. Count all nodes by type:")
    for entity_type in ["Supplier", "Product", "Order", "Server", "PartType", "Part"]:
        result = g.v().has("type", entity_type).count()
        print(f"   {entity_type}: {result}")
    
    print("\n7. Check relationships from PAC900S12-B2-1:")
    result = g.v("PAC900S12-B2-1").out("part_used_by_kunlun2280").all()
    print(f"   Used by {len(result.get('result', []))} servers")

def main():
    g = import_data()
    verify_graph(g)
    print("\n" + "=" * 50)
    print(f"Done! Graph saved as: {DB_NAME}")
    print("=" * 50)

if __name__ == "__main__":
    main()
