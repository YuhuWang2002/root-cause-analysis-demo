#!/usr/bin/env python3
"""
生成服务器库存分析的模拟数据

根据用户需求，生成11月份和12月份的服务器库存数据，其中12月份数据要反映server_2885销售下降和server_5885停止使用cpu_xeon_6338导致cpu_xeon_6338库存增加的情况
"""

import pandas as pd
import numpy as np
import datetime


def generate_server_inventory_data():
    """生成服务器库存分析的模拟数据"""
    
    # 生成日期数据
    dates = pd.date_range(start='2026-11-01', end='2026-12-31', freq='D')
    
    # 初始化数据
    data = []
    
    for date in dates:
        month = date.month
        day = date.day
        
        # 服务器2885销售数量 - 12月下降
        if month == 11:
            server_2885_sales = np.random.randint(15, 25)
        else:  # 12月
            server_2885_sales = np.random.randint(5, 10)  # 销售下降
        
        # 服务器5885销售数量 - 保持稳定
        server_5885_sales = np.random.randint(10, 20)
        
        # 服务器2885生产效率
        server_2885_efficiency = np.random.uniform(0.8, 0.95)
        
        # 服务器5885生产效率
        server_5885_efficiency = np.random.uniform(0.85, 0.98)
        
        # CPU Xeon 6338 - 12月库存增加
        if month == 11:
            # 11月：server_2885销售正常，server_5885使用cpu_xeon_6338
            cpu_6338_inventory = np.random.randint(50, 80)
            # 11月库存较低，周转率较高
            cpu_6338_turnover = np.random.uniform(0.4, 0.6)
            # 11月：server_2885使用比例较高
            cpu_6338_utilization_server_2885 = np.random.uniform(0.6, 0.8)
            # 11月：server_5885使用比例较高
            cpu_6338_utilization_server_5885 = np.random.uniform(0.5, 0.7)
        else:  # 12月
            # 12月：server_2885销售下降，server_5885停止使用cpu_xeon_6338
            cpu_6338_inventory = np.random.randint(100, 150)  # 库存增加
            # 12月库存较高，周转率较低
            cpu_6338_turnover = np.random.uniform(0.2, 0.4)
            # 12月：server_2885使用比例下降
            cpu_6338_utilization_server_2885 = np.random.uniform(0.3, 0.5)
            # 12月：server_5885停止使用
            cpu_6338_utilization_server_5885 = 0.0  # 完全不使用
        
        cpu_6338_commonality = 2  # 被两款服务器使用
        
        # CPU Xeon 8358
        if month == 11:
            cpu_8358_inventory = np.random.randint(30, 60)
            cpu_8358_turnover = np.random.uniform(0.4, 0.7)
            # 11月：server_2885使用比例
            cpu_8358_utilization_server_2885 = np.random.uniform(0.1, 0.3)
            # 11月：server_5885使用比例较高
            cpu_8358_utilization_server_5885 = np.random.uniform(0.6, 0.8)
        else:  # 12月
            cpu_8358_inventory = np.random.randint(35, 65)
            cpu_8358_turnover = np.random.uniform(0.45, 0.75)
            # 12月：server_2885使用比例
            cpu_8358_utilization_server_2885 = np.random.uniform(0.1, 0.3)
            # 12月：server_5885使用比例保持较高
            cpu_8358_utilization_server_5885 = np.random.uniform(0.6, 0.8)
        cpu_8358_commonality = 1  # 主要被一款服务器使用
        
        # 32GB内存
        if month == 11:
            memory_32gb_inventory = np.random.randint(100, 150)
            memory_32gb_turnover = np.random.uniform(0.5, 0.8)
            # 11月：server_2885使用比例较高
            memory_32gb_utilization_server_2885 = np.random.uniform(0.6, 0.8)
            # 11月：server_5885使用比例较低
            memory_32gb_utilization_server_5885 = np.random.uniform(0.1, 0.3)
        else:  # 12月
            memory_32gb_inventory = np.random.randint(110, 160)
            memory_32gb_turnover = np.random.uniform(0.4, 0.7)
            # 12月：server_2885使用比例下降
            memory_32gb_utilization_server_2885 = np.random.uniform(0.3, 0.5)
            # 12月：server_5885使用比例保持较低
            memory_32gb_utilization_server_5885 = np.random.uniform(0.1, 0.3)
        memory_32gb_commonality = 1  # 主要被一款服务器使用
        
        # 64GB内存
        if month == 11:
            memory_64gb_inventory = np.random.randint(80, 120)
            memory_64gb_turnover = np.random.uniform(0.4, 0.7)
            # 11月：server_2885使用比例较低
            memory_64gb_utilization_server_2885 = np.random.uniform(0.1, 0.3)
            # 11月：server_5885使用比例较高
            memory_64gb_utilization_server_5885 = np.random.uniform(0.6, 0.8)
        else:  # 12月
            memory_64gb_inventory = np.random.randint(85, 125)
            memory_64gb_turnover = np.random.uniform(0.45, 0.75)
            # 12月：server_2885使用比例较低
            memory_64gb_utilization_server_2885 = np.random.uniform(0.1, 0.3)
            # 12月：server_5885使用比例保持较高
            memory_64gb_utilization_server_5885 = np.random.uniform(0.6, 0.8)
        memory_64gb_commonality = 1  # 主要被一款服务器使用
        
        # 2TB HDD
        if month == 11:
            hdd_2tb_inventory = np.random.randint(60, 100)
            hdd_2tb_turnover = np.random.uniform(0.3, 0.6)
            # 11月：server_2885使用比例较高
            hdd_2tb_utilization_server_2885 = np.random.uniform(0.6, 0.8)
            # 11月：server_5885使用比例较低
            hdd_2tb_utilization_server_5885 = np.random.uniform(0.1, 0.3)
        else:  # 12月
            hdd_2tb_inventory = np.random.randint(70, 110)
            hdd_2tb_turnover = np.random.uniform(0.2, 0.5)
            # 12月：server_2885使用比例下降
            hdd_2tb_utilization_server_2885 = np.random.uniform(0.3, 0.5)
            # 12月：server_5885使用比例保持较低
            hdd_2tb_utilization_server_5885 = np.random.uniform(0.1, 0.3)
        hdd_2tb_commonality = 1  # 主要被一款服务器使用
        
        # 1TB SSD
        if month == 11:
            ssd_1tb_inventory = np.random.randint(40, 80)
            ssd_1tb_turnover = np.random.uniform(0.6, 0.9)
            # 11月：server_2885使用比例较低
            ssd_1tb_utilization_server_2885 = np.random.uniform(0.1, 0.3)
            # 11月：server_5885使用比例较高
            ssd_1tb_utilization_server_5885 = np.random.uniform(0.6, 0.8)
        else:  # 12月
            ssd_1tb_inventory = np.random.randint(45, 85)
            ssd_1tb_turnover = np.random.uniform(0.65, 0.95)
            # 12月：server_2885使用比例较低
            ssd_1tb_utilization_server_2885 = np.random.uniform(0.1, 0.3)
            # 12月：server_5885使用比例保持较高
            ssd_1tb_utilization_server_5885 = np.random.uniform(0.6, 0.8)
        ssd_1tb_commonality = 1  # 主要被一款服务器使用
        
        # 添加数据行
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'month': month,
            'day': day,
            'server_2885_sales_quantity': server_2885_sales,
            'server_2885_production_efficiency': server_2885_efficiency,
            'server_5885_sales_quantity': server_5885_sales,
            'server_5885_production_efficiency': server_5885_efficiency,
            'cpu_xeon_6338_inventory_level': cpu_6338_inventory,
            'cpu_xeon_6338_inventory_turnover_rate': cpu_6338_turnover,
            'cpu_xeon_6338_commonality': cpu_6338_commonality,
            'cpu_xeon_6338_utilization_ratio_for_server_2885': cpu_6338_utilization_server_2885,
            'cpu_xeon_6338_utilization_ratio_for_server_5885': cpu_6338_utilization_server_5885,
            'cpu_xeon_8358_inventory_level': cpu_8358_inventory,
            'cpu_xeon_8358_inventory_turnover_rate': cpu_8358_turnover,
            'cpu_xeon_8358_commonality': cpu_8358_commonality,
            'cpu_xeon_8358_utilization_ratio_for_server_2885': cpu_8358_utilization_server_2885,
            'cpu_xeon_8358_utilization_ratio_for_server_5885': cpu_8358_utilization_server_5885,
            'memory_32gb_inventory_level': memory_32gb_inventory,
            'memory_32gb_inventory_turnover_rate': memory_32gb_turnover,
            'memory_32gb_commonality': memory_32gb_commonality,
            'memory_32gb_utilization_ratio_for_server_2885': memory_32gb_utilization_server_2885,
            'memory_32gb_utilization_ratio_for_server_5885': memory_32gb_utilization_server_5885,
            'memory_64gb_inventory_level': memory_64gb_inventory,
            'memory_64gb_inventory_turnover_rate': memory_64gb_turnover,
            'memory_64gb_commonality': memory_64gb_commonality,
            'memory_64gb_utilization_ratio_for_server_2885': memory_64gb_utilization_server_2885,
            'memory_64gb_utilization_ratio_for_server_5885': memory_64gb_utilization_server_5885,
            'hdd_2tb_inventory_level': hdd_2tb_inventory,
            'hdd_2tb_inventory_turnover_rate': hdd_2tb_turnover,
            'hdd_2tb_commonality': hdd_2tb_commonality,
            'hdd_2tb_utilization_ratio_for_server_2885': hdd_2tb_utilization_server_2885,
            'hdd_2tb_utilization_ratio_for_server_5885': hdd_2tb_utilization_server_5885,
            'ssd_1tb_inventory_level': ssd_1tb_inventory,
            'ssd_1tb_inventory_turnover_rate': ssd_1tb_turnover,
            'ssd_1tb_commonality': ssd_1tb_commonality,
            'ssd_1tb_utilization_ratio_for_server_2885': ssd_1tb_utilization_server_2885,
            'ssd_1tb_utilization_ratio_for_server_5885': ssd_1tb_utilization_server_5885
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
    
    # 打印11月和12月的server_2885销售数量
    print("\n服务器2885销售数量:")
    print(f"11月平均: {df[df['month'] == 11]['server_2885_sales_quantity'].mean():.2f}")
    print(f"12月平均: {df[df['month'] == 12]['server_2885_sales_quantity'].mean():.2f}")
    
    # 打印11月和12月的cpu_xeon_6338库存水平
    print("\nCPU Xeon 6338库存水平:")
    print(f"11月平均: {df[df['month'] == 11]['cpu_xeon_6338_inventory_level'].mean():.2f}")
    print(f"12月平均: {df[df['month'] == 12]['cpu_xeon_6338_inventory_level'].mean():.2f}")


if __name__ == "__main__":
    # 生成数据
    df = generate_server_inventory_data()
    
    # 保存到文件
    output_path = "server_inventory_data.csv"
    save_data(df, output_path)
    
    # 打印Schema
    print_schema(df)
    
    # 打印样例数据
    print_sample_data(df)
    
    # 打印统计信息
    print_statistics(df)
    
    print("\n数据生成完成！")
