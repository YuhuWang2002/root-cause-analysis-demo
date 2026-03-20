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
    
    print(f"原始节点数量: {len(nodes)}")
    print("原始节点:")
    for node in nodes:
        print(f"  - {node.get('id')} ({node.get('type')})")
    
    # 过滤掉异常节点
    filtered_nodes = [node for node in nodes if node.get('id') != 'root_cause_config']
    
    print(f"\n过滤后节点数量: {len(filtered_nodes)}")
    print("过滤后节点:")
    for node in filtered_nodes:
        print(f"  - {node.get('id')} ({node.get('type')})")
    
    # 更新数据库
    filtered_nodes_json = json.dumps(filtered_nodes)
    cursor.execute('UPDATE canvas_data SET nodes = ? WHERE project_id = ?', (filtered_nodes_json, project_id))
    conn.commit()
    
    print("\n已成功删除异常节点 'root_cause_config'")
else:
    print("未找到该项目的画布数据")

# 关闭连接
conn.close()