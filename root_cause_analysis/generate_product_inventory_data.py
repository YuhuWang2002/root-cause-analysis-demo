#!/usr/bin/env python3
"""
生成产品部件库存分析的模拟数据

场景描述：
- 有两个产品：产品A和产品B
- 部件A本来可以同时被产品A和B使用
- 但由于BOM单或其他原因，一直以来都是产品A用部件A，产品B用的是A1
- 实际上A=A1（技术规格相同）
- 当产品A销售下降后，导致看到部件A库存处于高位
- 根因：部件A没有被产品B使用，导致部件A库存降不下来
"""

import pandas as pd
import numpy as np
import datetime


def generate_product_inventory_data():
    """生成产品部件库存分析的模拟数据"""
    
    # 生成日期数据
    dates = pd.date_range(start='2026-11-01', end='2026-12-31', freq='D')
    
    # 初始化数据
    data = []
    
    for date in dates:
        month = date.month
        day = date.day
        
        # 产品A销售数量 - 12月下降
        if month == 11:
            product_a_sales = np.random.randint(80, 120)
        else:  # 12月
            product_a_sales = np.random.randint(30, 50)  # 销售下降
        
        # 产品B销售数量 - 保持稳定
        product_b_sales = np.random.randint(60, 100)
        
        # 产品A生产数量
        product_a_production = product_a_sales + np.random.randint(-5, 10)
        
        # 产品B生产数量
        product_b_production = product_b_sales + np.random.randint(-5, 10)
        
        # 部件A - 12月库存增加
        if month == 11:
            # 11月：产品A销售正常，部件A库存较低
            component_a_inventory = np.random.randint(200, 300)
            # 11月库存周转率较高
            component_a_turnover = np.random.uniform(0.6, 0.8)
            # 11月：产品A使用部件A的比例较高
            component_a_utilization_product_a = np.random.uniform(0.7, 0.9)
        else:  # 12月
            # 12月：产品A销售下降，部件A库存增加
            component_a_inventory = np.random.randint(400, 600)  # 库存增加
            # 12月库存周转率较低
            component_a_turnover = np.random.uniform(0.3, 0.5)
            # 12月：产品A使用部件A的比例下降
            component_a_utilization_product_a = np.random.uniform(0.4, 0.6)
        
        # 关键：部件A被产品B使用比例 - 始终为0（这是问题的根因）
        # 但为了因果分析能够计算，我们给一个很小的随机值（接近0）
        component_a_utilization_product_b = np.random.uniform(0.0, 0.01)  # 几乎为0，但有一点变化
        
        # 部件A的通用性 - 可被2个产品使用
        component_a_commonality = 2
        
        # 部件A1 - 产品B使用的部件（实际与A相同）
        if month == 11:
            component_a1_inventory = np.random.randint(150, 250)
            component_a1_turnover = np.random.uniform(0.5, 0.7)
        else:  # 12月
            component_a1_inventory = np.random.randint(160, 260)
            component_a1_turnover = np.random.uniform(0.55, 0.75)
        
        # 部件A1被产品B使用比例 - 较高
        component_a1_utilization_product_b = np.random.uniform(0.6, 0.8)
        
        # 部件A1的通用性 - 只被1个产品使用
        component_a1_commonality = 1
        
        # 添加数据行
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'month': month,
            'day': day,
            'product_a_sales_quantity': product_a_sales,
            'product_a_production_quantity': product_a_production,
            'product_b_sales_quantity': product_b_sales,
            'product_b_production_quantity': product_b_production,
            'component_a_inventory_level': component_a_inventory,
            'component_a_inventory_turnover_rate': component_a_turnover,
            'component_a_commonality': component_a_commonality,
            'component_a_utilization_ratio_for_product_a': component_a_utilization_product_a,
            'component_a_utilization_ratio_for_product_b': component_a_utilization_product_b,
            'component_a1_inventory_level': component_a1_inventory,
            'component_a1_inventory_turnover_rate': component_a1_turnover,
            'component_a1_commonality': component_a1_commonality,
            'component_a1_utilization_ratio_for_product_b': component_a1_utilization_product_b
        })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    return df


def save_data(df, output_path):
    """保存数据到文件"""
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"数据已保存到: {output_path}")


def print_schema(df):
    """打印数据Schema"""
    print("\n数据Schema:")
    print("字段名称,数据类型")
    for col in df.columns:
        print(f"{col},{df[col].dtype}")


def print_sample_data(df):
    """打印样例数据"""
    print("\n样例数据:")
    print(df.head())


def print_statistics(df):
    """打印数据统计信息"""
    print("\n数据统计信息:")
    print(f"总记录数: {len(df)}")
    print(f"日期范围: {df['date'].min()} 到 {df['date'].max()}")
    
    # 打印11月和12月的产品A销售数量
    print("\n产品A销售数量:")
    print(f"11月平均: {df[df['month'] == 11]['product_a_sales_quantity'].mean():.2f}")
    print(f"12月平均: {df[df['month'] == 12]['product_a_sales_quantity'].mean():.2f}")
    
    # 打印11月和12月的部件A库存水平
    print("\n部件A库存水平:")
    print(f"11月平均: {df[df['month'] == 11]['component_a_inventory_level'].mean():.2f}")
    print(f"12月平均: {df[df['month'] == 12]['component_a_inventory_level'].mean():.2f}")
    
    # 打印关键指标
    print("\n关键指标:")
    print(f"部件A被产品B使用比例: {df['component_a_utilization_ratio_for_product_b'].mean():.2f}")
    print(f"部件A1被产品B使用比例: {df['component_a1_utilization_ratio_for_product_b'].mean():.2f}")


if __name__ == "__main__":
    # 生成数据
    df = generate_product_inventory_data()
    
    # 保存到文件
    output_path = "product_inventory_data.csv"
    save_data(df, output_path)
    
    # 打印Schema
    print_schema(df)
    
    # 打印样例数据
    print_sample_data(df)
    
    # 打印统计信息
    print_statistics(df)
    
    print("\n数据生成完成！")
