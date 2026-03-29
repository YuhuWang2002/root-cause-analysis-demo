import json
import os
from datetime import datetime, timedelta
from cog.torque import Graph

DB_NAME = "server_manufacturing_cog_graph"
COG_HOME = "data"
COG_PATH_PREFIX = os.path.dirname(__file__)

def load_ontology():
    ontology_path = os.path.join(os.path.dirname(__file__), "..", "server_manufacturing_ontology.json")
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
    
    suppliers_data = [
        ("Intel Corporation", {"supplierCode": "SUP-INTEL", "category": "芯片"}),
        ("Samsung Electronics", {"supplierCode": "SUP-SAMSUNG", "category": "内存/存储"}),
        ("Seagate Technology", {"supplierCode": "SUP-SEAGATE", "category": "硬盘"}),
        ("Delta Electronics", {"supplierCode": "SUP-DELTA", "category": "电源"}),
        ("ASUS", {"supplierCode": "SUP-ASUS", "category": "主板"}),
        ("Micron Technology", {"supplierCode": "SUP-MICRON", "category": "内存"}),
    ]
    for name, attrs in suppliers_data:
        triples.append((name, "type", "Supplier"))
        for k, v in attrs.items():
            triples.append((name, k, str(v)))
    print(f"  Added {len(suppliers_data)} suppliers")
    
    customers_data = [
        ("中国银行", {"customerCode": "CUST-BOC", "industry": "金融"}),
        ("中国电信", {"customerCode": "CUST-CT", "industry": "电信"}),
        ("阿里云", {"customerCode": "CUST-ALI", "industry": "云计算"}),
        ("腾讯云", {"customerCode": "CUST-TENCENT", "industry": "云计算"}),
        ("华为云", {"customerCode": "CUST-HUAWEI", "industry": "云计算"}),
    ]
    for name, attrs in customers_data:
        triples.append((name, "type", "Customer"))
        for k, v in attrs.items():
            triples.append((name, k, str(v)))
    print(f"  Added {len(customers_data)} customers")
    
    logistics_data = [
        ("顺丰速运", {"logisticsCode": "LOG-SF"}),
        ("京东物流", {"logisticsCode": "LOG-JD"}),
        ("德邦物流", {"logisticsCode": "LOG-DB"}),
    ]
    for name, attrs in logistics_data:
        triples.append((name, "type", "Logistics"))
        for k, v in attrs.items():
            triples.append((name, k, str(v)))
    print(f"  Added {len(logistics_data)} logistics")
    
    manufacturers_data = [
        ("富士康", {"manufacturerCode": "MFG-FOXCONN", "location": "深圳", "capacity": "1000"}),
        ("纬创", {"manufacturerCode": "MFG-WISTRON", "location": "昆山", "capacity": "800"}),
        ("浪潮", {"manufacturerCode": "MFG-INSPIRON", "location": "济南", "capacity": "600"}),
    ]
    for name, attrs in manufacturers_data:
        triples.append((name, "type", "Manufacturer"))
        for k, v in attrs.items():
            triples.append((name, k, str(v)))
    print(f"  Added {len(manufacturers_data)} manufacturers")
    
    warehouses_data = [
        ("原材料仓库A", {"warehouseCode": "WH-RAW-A", "warehouseType": "原材料仓", "capacity": "10000"}),
        ("原材料仓库B", {"warehouseCode": "WH-RAW-B", "warehouseType": "原材料仓", "capacity": "8000"}),
        ("成品仓库", {"warehouseCode": "WH-FG", "warehouseType": "成品仓", "capacity": "5000"}),
    ]
    for name, attrs in warehouses_data:
        triples.append((name, "type", "Warehouse"))
        for k, v in attrs.items():
            triples.append((name, k, str(v)))
    print(f"  Added {len(warehouses_data)} warehouses")
    
    production_lines_data = [
        ("x86服务器生产线", {"lineCode": "LINE-X86", "capacity": "500", "utilization": "85.5"}),
        ("ARM服务器生产线", {"lineCode": "LINE-ARM", "capacity": "300", "utilization": "72.0"}),
        ("AI服务器生产线", {"lineCode": "LINE-AI", "capacity": "200", "utilization": "95.0"}),
    ]
    for name, attrs in production_lines_data:
        triples.append((name, "type", "ProductionLine"))
        for k, v in attrs.items():
            triples.append((name, k, str(v)))
    print(f"  Added {len(production_lines_data)} production lines")
    
    equipments_data = [
        ("老化测试仪", {"equipmentCode": "EQ-TEST-001", "status": "运行中"}),
        ("贴片机", {"equipmentCode": "EQ-SMT-001", "status": "运行中"}),
        ("AOI检测仪", {"equipmentCode": "EQ-AOI-001", "status": "运行中"}),
    ]
    for name, attrs in equipments_data:
        triples.append((name, "type", "Equipment"))
        for k, v in attrs.items():
            triples.append((name, k, str(v)))
    print(f"  Added {len(equipments_data)} equipments")
    
    print("\n  Generating 30-day dynamic data...")
    
    raw_materials_base = [
        ("Intel Xeon Gold 6544Y", "芯片", "Intel Corporation"),
        ("Intel Xeon Platinum 8480+", "芯片", "Intel Corporation"),
        ("DDR5 32GB", "内存", "Samsung Electronics"),
        ("DDR5 64GB", "内存", "Samsung Electronics"),
        ("480GB SATA SSD", "存储", "Samsung Electronics"),
        ("4TB SATA HDD", "存储", "Seagate Technology"),
        ("900W电源", "电源", "Delta Electronics"),
        ("1500W电源", "电源", "Delta Electronics"),
        ("X670主板", "主板", "ASUS"),
        ("Z790主板", "主板", "ASUS"),
    ]
    
    production_lines = ["x86服务器生产线", "ARM服务器生产线", "AI服务器生产线"]
    warehouses = {"原材料": ["原材料仓库A", "原材料仓库B"], "成品": ["成品仓库"]}
    customers_list = ["中国银行", "中国电信", "阿里云", "腾讯云", "华为云"]
    logistics_list = ["顺丰速运", "京东物流", "德邦物流"]
    
    raw_material_count = 0
    po_count = 0
    receipt_count = 0
    wo_count = 0
    fp_count = 0
    so_count = 0
    qr_count = 0
    
    for day_idx, date in enumerate(dates):
        batch_id = f"BATCH-{date.replace('-', '')}"
        
        for mat_name, category, supplier in raw_materials_base:
            rm_name = f"{mat_name}-{batch_id}"
            rm_code = f"RAW-{mat_name.replace(' ', '-')}-{batch_id}"
            
            triples.append((rm_name, "type", "RawMaterial"))
            triples.append((rm_name, "name", rm_name))
            triples.append((rm_name, "materialCode", rm_code))
            triples.append((rm_name, "category", category))
            triples.append((rm_name, "supplier", supplier))
            triples.append((rm_name, "batch", batch_id))
            triples.append((rm_name, "productionDate", date))
            triples.append((rm_name, "inventory", str(100 + day_idx * 10)))
            
            triples.append((supplier, "provided_by_supplier", rm_name))
            
            warehouse = warehouses["原材料"][0] if category in ["芯片", "内存"] else warehouses["原材料"][1]
            triples.append((rm_name, "stored_in_warehouse", warehouse))
            
            po_name = f"采购订单-{mat_name}-{batch_id}"
            po_num = f"PO-{mat_name.replace(' ', '-')[:5].upper()}-{date.replace('-', '')}"
            triples.append((po_name, "type", "PurchaseOrder"))
            triples.append((po_name, "name", po_name))
            triples.append((po_name, "poNumber", po_num))
            triples.append((po_name, "orderDate", date))
            triples.append((po_name, "quantity", str(100 + day_idx * 5)))
            triples.append((po_name, "status", "已完成" if day_idx > 0 else "待入库"))
            
            triples.append((po_name, "po_from_supplier", supplier))
            
            receipt_name = f"入库单-{mat_name}-{batch_id}"
            receipt_num = f"RCV-{mat_name.replace(' ', '-')[:5].upper()}-{date.replace('-', '')}"
            triples.append((receipt_name, "type", "Receipt"))
            triples.append((receipt_name, "name", receipt_name))
            triples.append((receipt_name, "receiptNumber", receipt_num))
            triples.append((receipt_name, "receiptDate", date))
            triples.append((receipt_name, "quantity", str(100 + day_idx * 5)))
            triples.append((receipt_name, "qualityStatus", "合格"))
            
            triples.append((receipt_name, "receipt_for_purchase_order", po_name))
            triples.append((receipt_name, "receipt_records_material", rm_name))
            
            if category == "芯片":
                prod_line = production_lines[0]
            elif category == "内存":
                prod_line = production_lines[1]
            else:
                prod_line = production_lines[2]
            
            triples.append((rm_name, "consumed_by_production", prod_line))
            
            raw_material_count += 1
            po_count += 1
            receipt_count += 1
        
        for idx, prod_line in enumerate(production_lines):
            if idx == 0:
                server_type = "x86服务器"
            elif idx == 1:
                server_type = "ARM服务器"
            else:
                server_type = "AI服务器"
            
            fp_name = f"{server_type}-{batch_id}"
            fp_code = f"SRV-{server_type.replace('服务器', '').upper()}-{date.replace('-', '')}"
            
            triples.append((fp_name, "type", "FinishedProduct"))
            triples.append((fp_name, "name", fp_name))
            triples.append((fp_name, "productCode", fp_code))
            triples.append((fp_name, "productionDate", date))
            triples.append((fp_name, "inventory", str(50 + idx * 10 + day_idx * 2)))
            triples.append((fp_name, "production", str(50 + idx * 10)))
            triples.append((fp_name, "sales", str(40 + idx * 8)))
            
            triples.append((prod_line, "produced_by_line", fp_name))
            triples.append((fp_name, "stored_in_warehouse", "成品仓库"))
            
            wo_name = f"生产工单-{server_type}-{batch_id}"
            wo_num = f"WO-{server_type.replace('服务器', '').upper()}-{date.replace('-', '')}"
            triples.append((wo_name, "type", "WorkOrder"))
            triples.append((wo_name, "name", wo_name))
            triples.append((wo_name, "woNumber", wo_num))
            triples.append((wo_name, "createDate", date))
            triples.append((wo_name, "plannedQuantity", str(50 + idx * 10)))
            triples.append((wo_name, "completedQuantity", str(45 + idx * 9)))
            triples.append((wo_name, "status", "已完成" if day_idx > 0 else "进行中"))
            
            triples.append((prod_line, "production_for_work_order", wo_name))
            triples.append((wo_name, "product_fulfills_work_order", fp_name))
            
            qr_name = f"质检报告-{server_type}-{batch_id}"
            qr_num = f"QC-{server_type.replace('服务器', '').upper()}-{date.replace('-', '')}"
            triples.append((qr_name, "type", "QualityReport"))
            triples.append((qr_name, "name", qr_name))
            triples.append((qr_name, "reportNumber", qr_num))
            triples.append((qr_name, "inspectionDate", date))
            triples.append((qr_name, "sampleSize", str(20 + idx * 5)))
            triples.append((qr_name, "passRate", "98.5"))
            triples.append((qr_name, "result", "通过"))
            
            triples.append((fp_name, "qc_inspects_product", qr_name))
            
            fp_count += 1
            wo_count += 1
            qr_count += 1
        
        for idx, customer in enumerate(customers_list[:3]):
            if idx == 0:
                server_type = "AI服务器"
            elif idx == 1:
                server_type = "ARM服务器"
            else:
                server_type = "x86服务器"
            
            so_name = f"销售订单-{customer}-{server_type}-{batch_id}"
            so_num = f"SO-{customer[:2].upper()}-{server_type.replace('服务器', '').upper()}-{date.replace('-', '')}"
            triples.append((so_name, "type", "SalesOrder"))
            triples.append((so_name, "name", so_name))
            triples.append((so_name, "orderNumber", so_num))
            triples.append((so_name, "orderDate", date))
            triples.append((so_name, "quantity", str(10 + idx * 5)))
            triples.append((so_name, "fulfillmentRate", "100.0"))
            triples.append((so_name, "status", "待发货"))
            
            triples.append((customer, "order_placed_by_customer", so_name))
            
            fp_name = f"{server_type}-{batch_id}"
            triples.append((fp_name, "order_requires_product", so_name))
            triples.append((so_name, "warehouse_fulfills_order", "成品仓库"))
            
            triples.append((customer, "sold_to_customer", manufacturers_data[idx % 3][0]))
            triples.append((customer, "delivered_by_logistics", logistics_list[idx % 3]))
            
            so_count += 1
    
    print(f"  Added {raw_material_count} raw materials (30 days x {len(raw_materials_base)})")
    print(f"  Added {po_count} purchase orders")
    print(f"  Added {receipt_count} receipts")
    print(f"  Added {wo_count} work orders")
    print(f"  Added {fp_count} finished products")
    print(f"  Added {qr_count} quality reports")
    print(f"  Added {so_count} sales orders")
    
    for prod_line in production_lines:
        for eq in equipments_data[:2]:
            triples.append((prod_line, "equipment_used_in_line", eq[0]))
    
    return triples

def import_data():
    print("=" * 50)
    print("Creating graph data with CogDB")
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
    for item in result.get('result', [])[:3]:
        print(f"   - {item.get('id')}")
    
    print("\n2. Query all Customers:")
    result = g.v().has("type", "Customer").all()
    print(f"   Found {len(result.get('result', []))} customers")
    
    print("\n3. Query Raw Materials (last 5 days):")
    result = g.v().has("type", "RawMaterial").all()
    total_rm = len(result.get('result', []))
    print(f"   Total raw materials: {total_rm}")
    
    print("\n4. Query Finished Products:")
    result = g.v().has("type", "FinishedProduct").all()
    total_fp = len(result.get('result', []))
    print(f"   Total finished products: {total_fp}")
    
    print("\n5. Query Sales Orders:")
    result = g.v().has("type", "SalesOrder").all()
    total_so = len(result.get('result', []))
    print(f"   Total sales orders: {total_so}")
    
    print("\n6. Query Production Lines:")
    result = g.v().has("type", "ProductionLine").all()
    print(f"   Found {len(result.get('result', []))} production lines")
    for item in result.get('result', []):
        print(f"   - {item.get('id')}")
    
    print("\n7. Query relationships from Intel Corporation:")
    result = g.v("Intel Corporation").out("provided_by_supplier").limit(3).all()
    print(f"   Intel provides {len(result.get('result', []))} types of materials")
    
    print("\n8. Count all nodes by type:")
    for entity_type in ["Supplier", "Customer", "Logistics", "Manufacturer", "Warehouse", 
                        "ProductionLine", "Equipment", "RawMaterial", "FinishedProduct", 
                        "PurchaseOrder", "Receipt", "WorkOrder", "QualityReport", "SalesOrder"]:
        result = g.v().has("type", entity_type).count()
        print(f"   {entity_type}: {result}")

def main():
    g = import_data()
    verify_graph(g)
    print("\n" + "=" * 50)
    print(f"Done! Graph saved as: {DB_NAME}")
    print("=" * 50)

if __name__ == "__main__":
    main()
