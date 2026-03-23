import sqlite3
import json

# 连接到数据库
db_path = 'rca.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询画布数据
project_id = 'e37ef71c-79ae-491d-879b-cc32b6bc3513'
cursor.execute('SELECT nodes FROM canvas_data WHERE project_id = ?', (project_id,))
result = cursor.fetchone()

if result:
    nodes_json = result[0]
    nodes = json.loads(nodes_json)
    
    print(f"项目 {project_id} 的节点数量: {len(nodes)}")
    print("节点详情:")
    for i, node in enumerate(nodes, 1):
        print(f"\n{i}. ID: {node.get('id')}")
        print(f"   类型: {node.get('type')}")
        print(f"   名称: {node.get('name')}")
        print(f"   状态: {node.get('status')}")
        print(f"   位置: x={node.get('x')}, y={node.get('y')}")
        print(f"   配置: {json.dumps(node.get('config', {}), indent=4)}")
else:
    print(f"未找到项目 {project_id} 的画布数据")

# 关闭连接
conn.close()
