# 数据分析看板规范

## Why
用户需要一个通用的数据分析看板，能够读取任意 CSV 文件并进行分析，而不是局限于特定的数据结构。用户可以更换 CSV 数据源，看板系统应该能自动适应。

## What Changes
- 通用 CSV 数据加载器，自动推断字段类型
- 动态生成字段选择界面
- 支持多种图表类型的可视化框架
- 灵活的看板配置系统

## Impact
- Affected specs: 项目配置画布
- Affected code: 后端 routes/data_analysis.py, 前端 pages/AnalysisDashboard.tsx

## 设计原则

### 1. 通用性
- 系统不依赖特定的数据结构
- 读取任意 CSV 文件，自动识别字段
- 字段类型推断：string/number/date

### 2. 动态性
- 前端界面根据 CSV 字段动态生成
- 不需要硬编码字段
- 更换 CSV 后自动更新界面

### 3. 灵活性
- 支持任意数量的字段
- 支持多种聚合方式
- 支持多种图表类型

## 数据模型设计

### CSV 数据源配置
看板组件引用数据源配置：
```json
{
  "dataSource": {
    "type": "csv",
    "file_path": "/path/to/data.csv"
  }
}
```

### 字段元数据
系统自动从 CSV 推断字段信息：
```json
{
  "fields": [
    {"name": "field_1", "type": "string", "label": "字段1"},
    {"name": "field_2", "type": "number", "label": "字段2"},
    {"name": "field_3", "type": "date", "label": "字段3", "format": "YYYY-MM-DD"}
  ]
}
```

## API 设计

### 1. 通用数据查询 API
#### POST /api/data/query
通用的数据查询接口，适用于任何 CSV 数据源

**Request:**
```json
{
  "dataSource": {
    "type": "csv",
    "file_path": "/path/to/data.csv"
  },
  "query": {
    "fields": ["date", "sales", "inventory"],
    "filters": [
      {"field": "date", "operator": "gte", "value": "2024-01-01"},
      {"field": "sales", "operator": "gt", "value": 100}
    ],
    "groupBy": {"field": "date", "granularity": "day"},
    "aggregations": [
      {"field": "sales", "function": "sum", "alias": "total_sales"},
      {"field": "inventory", "function": "avg", "alias": "avg_inventory"}
    ]
  }
}
```

**Response:**
```json
{
  "fields": [
    {"name": "date", "type": "date"},
    {"name": "total_sales", "type": "number"},
    {"name": "avg_inventory", "type": "number"}
  ],
  "data": [
    {"date": "2024-01-01", "total_sales": 1234, "avg_inventory": 456}
  ]
}
```

### 2. CSV 字段识别 API
#### POST /api/data/csv/analyze
分析 CSV 文件并返回字段信息

**Request:**
```json
{
  "file_path": "/path/to/data.csv"
}
```

**Response:**
```json
{
  "file_path": "/path/to/data.csv",
  "total_rows": 1000,
  "fields": [
    {"name": "date", "type": "date", "sample": "2024-01-01", "null_count": 0},
    {"name": "sales", "type": "number", "sample": 123, "null_count": 2},
    {"name": "product_name", "type": "string", "sample": "Product A", "null_count": 0}
  ]
}
```

### 3. 看板配置 API
#### POST /api/projects/{project_id}/dashboards
创建看板

**Request:**
```json
{
  "name": "销售分析看板",
  "data_source": {
    "type": "csv",
    "file_path": "/data/sales.csv"
  },
  "components": [
    {
      "id": "chart-1",
      "type": "line",
      "title": "销售趋势",
      "position": {"x": 0, "y": 0, "w": 6, "h": 4},
      "config": {
        "xField": "date",
        "yFields": ["sales"],
        "dataSource": {"ref": "parent"}
      }
    }
  ]
}
```

## 前端功能设计

### 1. 数据源配置
- 支持配置 CSV 文件路径
- 或上传 CSV 文件
- 自动分析并显示字段信息

### 2. 组件配置面板
- **字段选择器**：多选字段列表
- **过滤条件**：动态添加过滤规则
- **聚合配置**：选择字段和聚合函数
- **图表类型**：选择可视化方式

### 3. 支持的组件类型

| 组件类型 | 适用场景 | 必需配置 |
|---------|---------|---------|
| 统计卡片 | 单指标展示 | 字段 + 聚合函数 |
| 折线图 | 趋势分析 | X轴字段 + Y轴字段(数值) |
| 柱状图 | 分类对比 | X轴字段 + Y轴字段(数值) |
| 饼图 | 占比分布 | 分类字段 + 数值字段 |
| 数据表格 | 明细查看 | 字段列表 |

### 4. 聚合函数
根据字段类型自动适配：
- **数值字段**: sum, avg, min, max, count
- **字符串字段**: count, distinct
- **日期字段**: count, min, max

## 架构设计

```
┌─────────────────────────────────────────────┐
│                  前端                        │
│  ┌─────────────┐  ┌─────────────────────┐   │
│  │ 看板编辑界面 │  │  组件配置面板        │   │
│  └─────────────┘  └─────────────────────┘   │
│           │                │                 │
│           └────────┬───────┘                 │
│                    ▼                         │
│         ┌──────────────────┐                 │
│         │  Query Builder  │                 │
│         └──────────────────┘                 │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│                  后端                        │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │ CSV Loader  │  │   Query Engine       │  │
│  └─────────────┘  └─────────────────────┘  │
│         │                   │                │
│         └─────────┬─────────┘                │
│                   ▼                          │
│         ┌──────────────────┐                 │
│         │  Aggregation    │                 │
│         └──────────────────┘                 │
└─────────────────────────────────────────────┘
```

## 核心特性

### 动态适应
- 更换 CSV 文件后，自动重新分析字段
- 前端界面自动更新字段选择器
- 现有组件配置自动校验有效性

### 查询构建
- 可视化查询构建器
- 支持复杂过滤条件
- 实时预览查询结果

### 可视化
- 多种图表类型
- 图表联动（点击某数据点过滤其他图表）
- 导出图表为图片
