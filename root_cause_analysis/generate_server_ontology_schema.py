#!/usr/bin/env python3
"""
生成服务器库存分析的本体Schema

根据用户需求，生成包含服务器、CPU、内存、硬盘等组件的本体Schema
"""

import json
import datetime


def generate_server_ontology_schema():
    """生成服务器库存分析的本体Schema"""
    
    schema = {
        "entity_types": [
            # 服务器类型
            {
                "id": "server_2885",
                "name": "服务器2885",
                "description": "型号为2885的服务器",
                "attributes": [
                    {
                        "name": "price",
                        "type": "float",
                        "description": "服务器价格"
                    },
                    {
                        "name": "stock_level",
                        "type": "integer",
                        "description": "库存水平"
                    },
                    {
                        "name": "lead_time",
                        "type": "integer",
                        "description": "交货周期"
                    }
                ]
            },
            {
                "id": "server_5885",
                "name": "服务器5885",
                "description": "型号为5885的服务器",
                "attributes": [
                    {
                        "name": "price",
                        "type": "float",
                        "description": "服务器价格"
                    },
                    {
                        "name": "stock_level",
                        "type": "integer",
                        "description": "库存水平"
                    },
                    {
                        "name": "lead_time",
                        "type": "integer",
                        "description": "交货周期"
                    }
                ]
            },
            
            # CPU类型
            {
                "id": "cpu_xeon_6338",
                "name": "Xeon 6338 CPU",
                "description": "Intel Xeon 6338 CPU",
                "attributes": [
                    {
                        "name": "price",
                        "type": "float",
                        "description": "CPU价格"
                    },
                    {
                        "name": "stock_level",
                        "type": "integer",
                        "description": "库存水平"
                    },
                    {
                        "name": "performance",
                        "type": "float",
                        "description": "性能评分"
                    }
                ]
            },
            {
                "id": "cpu_xeon_8358",
                "name": "Xeon 8358 CPU",
                "description": "Intel Xeon 8358 CPU",
                "attributes": [
                    {
                        "name": "price",
                        "type": "float",
                        "description": "CPU价格"
                    },
                    {
                        "name": "stock_level",
                        "type": "integer",
                        "description": "库存水平"
                    },
                    {
                        "name": "performance",
                        "type": "float",
                        "description": "性能评分"
                    }
                ]
            },
            
            # 内存类型
            {
                "id": "memory_32gb",
                "name": "32GB内存",
                "description": "32GB DDR4内存",
                "attributes": [
                    {
                        "name": "price",
                        "type": "float",
                        "description": "内存价格"
                    },
                    {
                        "name": "stock_level",
                        "type": "integer",
                        "description": "库存水平"
                    },
                    {
                        "name": "speed",
                        "type": "integer",
                        "description": "内存速度（MHz）"
                    }
                ]
            },
            {
                "id": "memory_64gb",
                "name": "64GB内存",
                "description": "64GB DDR4内存",
                "attributes": [
                    {
                        "name": "price",
                        "type": "float",
                        "description": "内存价格"
                    },
                    {
                        "name": "stock_level",
                        "type": "integer",
                        "description": "库存水平"
                    },
                    {
                        "name": "speed",
                        "type": "integer",
                        "description": "内存速度（MHz）"
                    }
                ]
            },
            
            # 硬盘类型
            {
                "id": "hdd_2tb",
                "name": "2TB HDD",
                "description": "2TB机械硬盘",
                "attributes": [
                    {
                        "name": "price",
                        "type": "float",
                        "description": "硬盘价格"
                    },
                    {
                        "name": "stock_level",
                        "type": "integer",
                        "description": "库存水平"
                    },
                    {
                        "name": "speed",
                        "type": "integer",
                        "description": "硬盘速度（RPM）"
                    }
                ]
            },
            {
                "id": "ssd_1tb",
                "name": "1TB SSD",
                "description": "1TB固态硬盘",
                "attributes": [
                    {
                        "name": "price",
                        "type": "float",
                        "description": "硬盘价格"
                    },
                    {
                        "name": "stock_level",
                        "type": "integer",
                        "description": "库存水平"
                    },
                    {
                        "name": "speed",
                        "type": "integer",
                        "description": "硬盘速度（MB/s）"
                    }
                ]
            }
        ],
        "relation_types": [
            {
                "id": "cpu_used_by_server",
                "name": "CPU被服务器使用",
                "description": "CPU组件被服务器使用",
                "source_types": ["cpu_xeon_6338", "cpu_xeon_8358"],
                "target_types": ["server_2885", "server_5885"]
            },
            {
                "id": "memory_used_by_server",
                "name": "内存被服务器使用",
                "description": "内存组件被服务器使用",
                "source_types": ["memory_32gb", "memory_64gb"],
                "target_types": ["server_2885", "server_5885"]
            },
            {
                "id": "storage_used_by_server",
                "name": "存储被服务器使用",
                "description": "存储组件被服务器使用",
                "source_types": ["hdd_2tb", "ssd_1tb"],
                "target_types": ["server_2885", "server_5885"]
            }
        ],
        "metric_definitions": [
            # CPU指标
            {
                "id": "cpu_xeon_6338_inventory_level",
                "name": "Xeon 6338 CPU库存水平",
                "description": "Xeon 6338 CPU的当前库存水平",
                "source_entity_type": "cpu_xeon_6338"
            },
            {
                "id": "cpu_xeon_6338_inventory_turnover_rate",
                "name": "Xeon 6338 CPU库存周转率",
                "description": "Xeon 6338 CPU的库存周转速度",
                "source_entity_type": "cpu_xeon_6338"
            },
            {
                "id": "cpu_xeon_6338_dead_inventory",
                "name": "Xeon 6338 CPU死库存",
                "description": "Xeon 6338 CPU长期未使用的库存（结果变量）",
                "type": "outcome",
                "source_entity_type": "cpu_xeon_6338"
            },
            {
                "id": "cpu_xeon_6338_commonality",
                "name": "Xeon 6338 CPU通用性",
                "description": "Xeon 6338 CPU在不同服务器型号中的通用程度",
                "source_entity_type": "cpu_xeon_6338"
            },
            {
                "id": "cpu_xeon_6338_utilization_ratio",
                "name": "Xeon 6338 CPU被服务器使用比例",
                "description": "Xeon 6338 CPU被不同服务器型号使用的比例",
                "source_entity_type": "cpu_xeon_6338",
                "source_relation": "cpu_used_by_server",
                "target_entity_type": "server_2885"
            },
            {
                "id": "cpu_xeon_8358_inventory_level",
                "name": "Xeon 8358 CPU库存水平",
                "description": "Xeon 8358 CPU的当前库存水平",
                "source_entity_type": "cpu_xeon_8358"
            },
            {
                "id": "cpu_xeon_8358_inventory_turnover_rate",
                "name": "Xeon 8358 CPU库存周转率",
                "description": "Xeon 8358 CPU的库存周转速度",
                "source_entity_type": "cpu_xeon_8358"
            },
            {
                "id": "cpu_xeon_8358_dead_inventory",
                "name": "Xeon 8358 CPU死库存",
                "description": "Xeon 8358 CPU长期未使用的库存（结果变量）",
                "type": "outcome",
                "source_entity_type": "cpu_xeon_8358"
            },
            {
                "id": "cpu_xeon_8358_commonality",
                "name": "Xeon 8358 CPU通用性",
                "description": "Xeon 8358 CPU在不同服务器型号中的通用程度",
                "source_entity_type": "cpu_xeon_8358"
            },
            {
                "id": "cpu_xeon_8358_utilization_ratio",
                "name": "Xeon 8358 CPU被服务器使用比例",
                "description": "Xeon 8358 CPU被不同服务器型号使用的比例",
                "source_entity_type": "cpu_xeon_8358",
                "source_relation": "cpu_used_by_server",
                "target_entity_type": "server_5885"
            },
            # 内存指标
            {
                "id": "memory_32gb_inventory_level",
                "name": "32GB内存库存水平",
                "description": "32GB内存的当前库存水平",
                "source_entity_type": "memory_32gb"
            },
            {
                "id": "memory_32gb_inventory_turnover_rate",
                "name": "32GB内存库存周转率",
                "description": "32GB内存的库存周转速度",
                "source_entity_type": "memory_32gb"
            },
            {
                "id": "memory_32gb_dead_inventory",
                "name": "32GB内存死库存",
                "description": "32GB内存长期未使用的库存（结果变量）",
                "type": "outcome",
                "source_entity_type": "memory_32gb"
            },
            {
                "id": "memory_32gb_commonality",
                "name": "32GB内存通用性",
                "description": "32GB内存在不同服务器型号中的通用程度",
                "source_entity_type": "memory_32gb"
            },
            {
                "id": "memory_32gb_utilization_ratio",
                "name": "32GB内存被服务器使用比例",
                "description": "32GB内存被不同服务器型号使用的比例",
                "source_entity_type": "memory_32gb",
                "source_relation": "memory_used_by_server",
                "target_entity_type": "server_2885"
            },
            {
                "id": "memory_64gb_inventory_level",
                "name": "64GB内存库存水平",
                "description": "64GB内存的当前库存水平",
                "source_entity_type": "memory_64gb"
            },
            {
                "id": "memory_64gb_inventory_turnover_rate",
                "name": "64GB内存库存周转率",
                "description": "64GB内存的库存周转速度",
                "source_entity_type": "memory_64gb"
            },
            {
                "id": "memory_64gb_dead_inventory",
                "name": "64GB内存死库存",
                "description": "64GB内存长期未使用的库存（结果变量）",
                "type": "outcome",
                "source_entity_type": "memory_64gb"
            },
            {
                "id": "memory_64gb_commonality",
                "name": "64GB内存通用性",
                "description": "64GB内存在不同服务器型号中的通用程度",
                "source_entity_type": "memory_64gb"
            },
            {
                "id": "memory_64gb_utilization_ratio",
                "name": "64GB内存被服务器使用比例",
                "description": "64GB内存被不同服务器型号使用的比例",
                "source_entity_type": "memory_64gb",
                "source_relation": "memory_used_by_server",
                "target_entity_type": "server_5885"
            },
            # 硬盘指标
            {
                "id": "hdd_2tb_inventory_level",
                "name": "2TB HDD库存水平",
                "description": "2TB HDD的当前库存水平",
                "source_entity_type": "hdd_2tb"
            },
            {
                "id": "hdd_2tb_inventory_turnover_rate",
                "name": "2TB HDD库存周转率",
                "description": "2TB HDD的库存周转速度",
                "source_entity_type": "hdd_2tb"
            },
            {
                "id": "hdd_2tb_dead_inventory",
                "name": "2TB HDD死库存",
                "description": "2TB HDD长期未使用的库存（结果变量）",
                "type": "outcome",
                "source_entity_type": "hdd_2tb"
            },
            {
                "id": "hdd_2tb_commonality",
                "name": "2TB HDD通用性",
                "description": "2TB HDD在不同服务器型号中的通用程度",
                "source_entity_type": "hdd_2tb"
            },
            {
                "id": "hdd_2tb_utilization_ratio",
                "name": "2TB HDD被服务器使用比例",
                "description": "2TB HDD被不同服务器型号使用的比例",
                "source_entity_type": "hdd_2tb",
                "source_relation": "storage_used_by_server",
                "target_entity_type": "server_2885"
            },
            {
                "id": "ssd_1tb_inventory_level",
                "name": "1TB SSD库存水平",
                "description": "1TB SSD的当前库存水平",
                "source_entity_type": "ssd_1tb"
            },
            {
                "id": "ssd_1tb_inventory_turnover_rate",
                "name": "1TB SSD库存周转率",
                "description": "1TB SSD的库存周转速度",
                "source_entity_type": "ssd_1tb"
            },
            {
                "id": "ssd_1tb_dead_inventory",
                "name": "1TB SSD死库存",
                "description": "1TB SSD长期未使用的库存（结果变量）",
                "type": "outcome",
                "source_entity_type": "ssd_1tb"
            },
            {
                "id": "ssd_1tb_commonality",
                "name": "1TB SSD通用性",
                "description": "1TB SSD在不同服务器型号中的通用程度",
                "source_entity_type": "ssd_1tb"
            },
            {
                "id": "ssd_1tb_utilization_ratio",
                "name": "1TB SSD被服务器使用比例",
                "description": "1TB SSD被不同服务器型号使用的比例",
                "source_entity_type": "ssd_1tb",
                "source_relation": "storage_used_by_server",
                "target_entity_type": "server_5885"
            },
            # 服务器级指标
            {
                "id": "server_2885_production_efficiency",
                "name": "服务器2885生产效率",
                "description": "服务器2885的生产效率",
                "source_entity_type": "server_2885"
            },
            {
                "id": "server_2885_sales_quantity",
                "name": "服务器2885销售数量",
                "description": "服务器2885的销售数量",
                "source_entity_type": "server_2885"
            },
            {
                "id": "server_5885_production_efficiency",
                "name": "服务器5885生产效率",
                "description": "服务器5885的生产效率",
                "source_entity_type": "server_5885"
            },
            {
                "id": "server_5885_sales_quantity",
                "name": "服务器5885销售数量",
                "description": "服务器5885的销售数量",
                "source_entity_type": "server_5885"
            }
        ],
        "metadata": {
            "created_at": datetime.datetime.now().isoformat(),
            "description": "服务器库存分析本体Schema"
        }
    }
    
    return schema


def save_schema(schema, output_path):
    """保存Schema到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(f"Schema已保存到: {output_path}")


if __name__ == "__main__":
    # 生成Schema
    schema = generate_server_ontology_schema()
    
    # 保存到文件
    output_path = "server_ontology_schema.json"
    save_schema(schema, output_path)
    
    # 打印统计信息
    print(f"\nSchema统计信息:")
    print(f"实体类型数量: {len(schema['entity_types'])}")
    print(f"关系类型数量: {len(schema['relation_types'])}")
    print(f"指标定义数量: {len(schema['metric_definitions'])}")
    
    print("\n生成完成！")
