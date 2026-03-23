# 创建库存分析本体库计划

## 任务目标
根据 `/Users/yuhuwang/Documents/trae_projects/root_cause_analysis/inventory_rca_demo/server_inventory_schema.json` 文件，创建一个 Python 脚本，通过后端 API 创建"库存分析本体库"，包含所有实体类型和关系类型。

## 实现步骤

### 1. 分析 Schema 文件结构
Schema 文件包含：
- **entity_types**: 实体类型列表（类）
  - id: 唯一标识符
  - name: 显示名称
  - description: 描述
  - type: 类型（Supplier, Product, Order, Server, PartType, Part 等）
  - attributes: 属性列表
    - name: 属性名
    - type: 属性类型（string, metric, array）
    - description: 描述
    - fieldName: 字段名（仅 metric 类型）

- **relation_types**: 关系类型列表
  - id: 唯一标识符
  - name: 关系名称（生成、被使用、采购入库等）
  - description: 描述
  - source_types: 源实体类型列表
  - target_types: 目标实体类型列表

### 2. 创建 Python 脚本 `import_inventory_ontology.py`

#### 2.1 导入必要的库
- json: 读取 schema 文件
- requests: 调用后端 API

#### 2.2 定义 API 辅助函数
```python
def create_ontology(base_url, project_id, name, description):
    """创建本体库"""

def create_ontology_class(base_url, project_id, ontology_id, class_data):
    """创建本体类"""

def create_ontology_relation(base_url, project_id, ontology_id, relation_data):
    """创建本体关系"""

def add_class_property(base_url, project_id, ontology_id, class_id, property_data):
    """添加类属性"""
```

#### 2.3 实现主逻辑
```python
# 1. 读取并解析 schema 文件
with open('server_inventory_schema.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# 2. 创建本体库 "库存分析本体库"
ontology = create_ontology(project_id, "库存分析本体库", "基于库存分析的本体库")

# 3. 创建所有实体类型（类）
for entity in schema['entity_types']:
    class_data = {
        'name': entity['name'],
        'description': entity.get('description', ''),
        'type': entity.get('type', '')
    }
    # 调用 API 创建类

# 4. 为每个类添加属性
for entity in schema['entity_types']:
    for attr in entity.get('attributes', []):
        property_data = {
            'name': attr['name'],
            'type': attr.get('type', 'string'),
            'description': attr.get('description', '')
        }
        # 调用 API 添加属性

# 5. 创建所有关系
for relation in schema['relation_types']:
    relation_data = {
        'source_class_id': source_class_id,
        'target_class_id': target_class_id,
        'relation_type': f"{relation['name']} ({relation['id']})"
    }
    # 调用 API 创建关系
```

### 3. 注意事项
- 需要已知项目 ID（project_id）
- 类和关系的创建需要先创建本体库获取 ontology_id
- 关系创建需要知道源类和目标类的 ID
- 需要处理 API 错误和异常

### 4. 预期输出
脚本运行后将创建：
- 1 个本体库：库存分析本体库
- 约 30+ 个类（实体类型）
- 约 50+ 个属性
- 约 30+ 个关系
