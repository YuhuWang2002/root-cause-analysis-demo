from flask import Blueprint, request, jsonify
import csv
import os
import re
from datetime import datetime
from collections import defaultdict

bp = Blueprint('data_analysis', __name__, url_prefix='/api/data')

# CSV文件缓存
_csv_cache = {}

def infer_field_type(values):
    """
    自动推断字段类型
    返回: 'string', 'number', 'date'
    """
    non_null_values = [v for v in values if v is not None and str(v).strip() != '']
    if not non_null_values:
        return 'string'

    # 尝试推断为数字
    number_count = 0
    for v in non_null_values[:100]:  # 只检查前100个值
        try:
            float(v)
            number_count += 1
        except (ValueError, TypeError):
            pass

    if number_count / len(non_null_values[:100]) > 0.8:
        return 'number'

    # 尝试推断为日期
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',           # 2024-01-01
        r'^\d{4}/\d{2}/\d{2}$',           # 2024/01/01
        r'^\d{2}-\d{2}-\d{4}$',           # 01-01-2024
        r'^\d{2}/\d{2}/\d{4}$',           # 01/01/2024
    ]

    date_count = 0
    for v in non_null_values[:100]:
        for pattern in date_patterns:
            if re.match(pattern, str(v)):
                date_count += 1
                break

    if date_count / len(non_null_values[:100]) > 0.8:
        return 'date'

    return 'string'

def parse_value(value, field_type):
    """根据字段类型解析值"""
    if value is None or str(value).strip() == '':
        return None

    if field_type == 'number':
        try:
            # 处理整数和浮点数
            if '.' in str(value):
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return None
    elif field_type == 'date':
        return str(value)
    else:
        return str(value)

def get_date_granularity(date_str, granularity):
    """根据粒度截取日期字符串"""
    if granularity == 'day':
        return date_str[:10] if len(date_str) >= 10 else date_str
    elif granularity == 'week':
        try:
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            # 获取该日期所在周的第一天（周一）
            week_start = dt - __import__('datetime').timedelta(days=dt.weekday())
            return week_start.strftime('%Y-%m-%d')
        except:
            return date_str[:10]
    elif granularity == 'month':
        return date_str[:7] if len(date_str) >= 7 else date_str
    return date_str

def load_csv(file_path):
    """加载CSV文件并缓存"""
    if file_path in _csv_cache:
        return _csv_cache[file_path]

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV文件不存在: {file_path}")

    rows = []
    fields = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            rows.append(row)

    # 推断字段类型
    field_types = {}
    for field in fields:
        values = [row.get(field) for row in rows]
        field_types[field] = infer_field_type(values)

    # 转换为指定类型
    typed_rows = []
    for row in rows:
        typed_row = {}
        for field in fields:
            typed_row[field] = parse_value(row.get(field), field_types[field])
        typed_rows.append(typed_row)

    result = {
        'rows': typed_rows,
        'fields': fields,
        'field_types': field_types,
        'total_rows': len(typed_rows)
    }

    _csv_cache[file_path] = result
    return result

def clear_csv_cache():
    """清除CSV缓存"""
    _csv_cache.clear()

@bp.route('/csv/analyze', methods=['POST'])
def analyze_csv():
    """
    分析CSV文件并返回字段信息
    Request: {"file_path": "/path/to/data.csv"}
    Response: {
        "file_path": "/path/to/data.csv",
        "total_rows": 1000,
        "fields": [
            {"name": "date", "type": "date", "sample": "2024-01-01", "null_count": 0},
            {"name": "sales", "type": "number", "sample": 123, "null_count": 2}
        ]
    }
    """
    data = request.get_json()

    if not data or 'file_path' not in data:
        return jsonify({'error': '缺少file_path参数'}), 400

    file_path = data['file_path']

    try:
        csv_data = load_csv(file_path)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'加载CSV文件失败: {str(e)}'}), 500

    # 计算每个字段的null_count和sample
    field_info = []
    for field in csv_data['fields']:
        field_type = csv_data['field_types'][field]
        null_count = sum(1 for row in csv_data['rows'] if row.get(field) is None)

        # 获取一个非null的sample
        sample = None
        for row in csv_data['rows']:
            if row.get(field) is not None:
                sample = row.get(field)
                break

        field_info.append({
            'name': field,
            'type': field_type,
            'sample': sample,
            'null_count': null_count
        })

    return jsonify({
        'file_path': file_path,
        'total_rows': csv_data['total_rows'],
        'fields': field_info
    })

@bp.route('/query', methods=['POST'])
def query_data():
    """
    通用数据查询接口
    Request: {
        "dataSource": {"type": "csv", "file_path": "/path/to/data.csv"},
        "query": {
            "fields": ["date", "sales"],
            "filters": [{"field": "date", "operator": "gte", "value": "2024-01-01"}],
            "groupBy": {"field": "date", "granularity": "day"},
            "aggregations": [{"field": "sales", "function": "sum", "alias": "total_sales"}]
        }
    }
    Response: {
        "fields": [{"name": "date", "type": "date"}, {"name": "total_sales", "type": "number"}],
        "data": [{"date": "2024-01-01", "total_sales": 1234}]
    }
    """
    data = request.get_json()

    if not data or 'dataSource' not in data or 'query' not in data:
        return jsonify({'error': '缺少dataSource或query参数'}), 400

    data_source = data['dataSource']
    query = data['query']

    if data_source.get('type') != 'csv':
        return jsonify({'error': '暂不支持的数据源类型'}), 400

    file_path = data_source.get('file_path')
    if not file_path:
        return jsonify({'error': '缺少file_path参数'}), 400

    try:
        csv_data = load_csv(file_path)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'加载CSV文件失败: {str(e)}'}), 500

    # 应用过滤条件
    filtered_rows = csv_data['rows']
    filters = query.get('filters', [])
    for f in filters:
        field = f.get('field')
        operator = f.get('operator')
        value = f.get('value')

        if not field or not operator:
            continue

        field_type = csv_data['field_types'].get(field, 'string')
        filtered_rows = apply_filter(filtered_rows, field, operator, value, field_type)

    # 分组处理
    group_by = query.get('groupBy')
    aggregations = query.get('aggregations', [])

    if group_by and aggregations:
        # 有分组和聚合
        result = apply_group_by_and_aggregations(
            filtered_rows,
            group_by,
            aggregations,
            csv_data['field_types']
        )
    elif aggregations:
        # 只有聚合，无分组
        result = apply_aggregations_only(filtered_rows, aggregations, csv_data['field_types'])
    else:
        # 只返回字段
        result = apply_fields_only(filtered_rows, query.get('fields', []), csv_data['field_types'])

    # 构建返回的字段信息
    result_fields = []
    if group_by:
        result_fields.append({
            'name': group_by.get('field'),
            'type': csv_data['field_types'].get(group_by.get('field'), 'string')
        })
    for agg in aggregations:
        result_fields.append({
            'name': agg.get('alias', f"{agg.get('function')}_{agg.get('field')}"),
            'type': 'number'
        })

    if not aggregations and not group_by:
        for f in query.get('fields', []):
            result_fields.append({
                'name': f,
                'type': csv_data['field_types'].get(f, 'string')
            })

    return jsonify({
        'fields': result_fields,
        'data': result
    })

def apply_filter(rows, field, operator, value, field_type):
    """应用过滤条件"""
    filtered = []

    # 转换value为适当类型
    if field_type == 'number':
        try:
            value = float(value) if '.' in str(value) else int(value)
        except:
            pass

    for row in rows:
        row_value = row.get(field)

        if row_value is None:
            continue

        # 转换行值为适当类型
        if field_type == 'number' and row_value is not None:
            try:
                row_value = float(row_value) if isinstance(row_value, float) or (isinstance(row_value, str) and '.' in row_value) else int(float(row_value))
            except:
                pass

        # 根据操作符进行过滤
        if operator == 'eq':
            if row_value == value:
                filtered.append(row)
        elif operator == 'ne':
            if row_value != value:
                filtered.append(row)
        elif operator == 'gt':
            if row_value > value:
                filtered.append(row)
        elif operator == 'gte':
            if row_value >= value:
                filtered.append(row)
        elif operator == 'lt':
            if row_value < value:
                filtered.append(row)
        elif operator == 'lte':
            if row_value <= value:
                filtered.append(row)
        elif operator == 'like':
            if value in str(row_value):
                filtered.append(row)
        elif operator == 'in':
            if row_value in (value if isinstance(value, list) else [value]):
                filtered.append(row)

    return filtered

def apply_group_by_and_aggregations(rows, group_by, aggregations, field_types):
    """应用分组和聚合"""
    group_field = group_by.get('field')
    granularity = group_by.get('granularity', 'day')

    # 按分组键分组
    groups = defaultdict(list)
    for row in rows:
        key_value = row.get(group_field)
        if key_value is not None:
            # 根据粒度处理日期
            if field_types.get(group_field) == 'date':
                key_value = get_date_granularity(str(key_value), granularity)
            groups[key_value].append(row)

    # 计算聚合
    result = []
    for key, group_rows in sorted(groups.items()):
        result_row = {}

        # 添加分组字段
        if field_types.get(group_field) == 'date':
            result_row[group_field] = key
        else:
            result_row[group_field] = key

        # 计算每个聚合
        for agg in aggregations:
            agg_field = agg.get('field')
            agg_func = agg.get('function')
            agg_alias = agg.get('alias', f"{agg_func}_{agg_field}")

            values = [row.get(agg_field) for row in group_rows if row.get(agg_field) is not None]

            if agg_func == 'sum':
                result_row[agg_alias] = sum(values) if values else 0
            elif agg_func == 'avg':
                result_row[agg_alias] = sum(values) / len(values) if values else None
            elif agg_func == 'min':
                result_row[agg_alias] = min(values) if values else None
            elif agg_func == 'max':
                result_row[agg_alias] = max(values) if values else None
            elif agg_func == 'count':
                result_row[agg_alias] = len(values)

        result.append(result_row)

    return result

def apply_aggregations_only(rows, aggregations, field_types):
    """只应用聚合，无分组"""
    result_row = {}

    for agg in aggregations:
        agg_field = agg.get('field')
        agg_func = agg.get('function')
        agg_alias = agg.get('alias', f"{agg_func}_{agg_field}")

        values = [row.get(agg_field) for row in rows if row.get(agg_field) is not None]

        if agg_func == 'sum':
            result_row[agg_alias] = sum(values) if values else 0
        elif agg_func == 'avg':
            result_row[agg_alias] = sum(values) / len(values) if values else None
        elif agg_func == 'min':
            result_row[agg_alias] = min(values) if values else None
        elif agg_func == 'max':
            result_row[agg_alias] = max(values) if values else None
        elif agg_func == 'count':
            result_row[agg_alias] = len(values)

    return [result_row] if result_row else []

def apply_fields_only(rows, fields, field_types):
    """只返回指定字段"""
    if not fields:
        return rows

    result = []
    for row in rows:
        filtered_row = {f: row.get(f) for f in fields if f in row}
        result.append(filtered_row)

    return result

# 清除缓存端点（用于测试）
@bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """清除CSV缓存"""
    clear_csv_cache()
    return jsonify({'message': '缓存已清除'})
