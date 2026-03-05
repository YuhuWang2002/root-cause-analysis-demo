"""
部件A库存高因果根因分析 - 数据生成模块

场景说明：
- 产品A销量下降，导致部件A库存偏高
- 产品B未使用部件A（历史全为0）
- 需要验证：产品B未使用部件A是部件A库存高的核心因果根因

数据字段：
- 日期
- 产品A销量、产品B销量
- 产品B是否使用部件A（历史全为0）
- 部件A消耗量、部件A期末库存
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple


class InventoryDataGenerator:
    """部件A库存数据生成器"""
    
    def __init__(self, seed: int = 42):
        """
        初始化数据生成器
        
        Args:
            seed: 随机种子
        """
        np.random.seed(seed)
        
    def generate_daily_data(self, 
                           start_date: str = "2024-06-01",
                           end_date: str = "2024-12-31",
                           product_a_sales_decline_start: str = "2024-11-01",
                           product_a_decline_rate: float = 0.4) -> pd.DataFrame:
        """
        生成每日库存数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            product_a_sales_decline_start: 产品A销量开始下降的日期
            product_a_decline_rate: 产品A销量下降比例
            
        Returns:
            包含库存数据的DataFrame
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        decline_start = datetime.strptime(product_a_sales_decline_start, "%Y-%m-%d")
        
        records = []
        current_inventory = 100
        
        current_date = start
        while current_date <= end:
            is_decline_period = current_date >= decline_start
            
            product_a_sales = self._generate_product_a_sales(is_decline_period, product_a_decline_rate)
            product_b_sales = self._generate_product_b_sales()
            
            product_b_uses_component_a = 0
            
            component_a_consumption = self._calculate_consumption(
                product_a_sales, 
                product_b_sales, 
                product_b_uses_component_a
            )
            
            component_a_procurement = self._calculate_procurement(
                current_inventory,
                component_a_consumption,
                is_decline_period
            )
            
            current_inventory = current_inventory + component_a_procurement - component_a_consumption
            current_inventory = max(0, current_inventory)
            
            record = {
                "date": current_date,
                "product_a_sales": product_a_sales,
                "product_b_sales": product_b_sales,
                "product_b_uses_component_a": product_b_uses_component_a,
                "component_a_consumption": component_a_consumption,
                "component_a_inventory": current_inventory,
                "component_a_procurement": component_a_procurement,
                "is_decline_period": is_decline_period
            }
            records.append(record)
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def _generate_product_a_sales(self, is_decline_period: bool, decline_rate: float) -> int:
        """
        生成产品A销量
        
        Args:
            is_decline_period: 是否为销量下降期
            decline_rate: 销量下降比例
            
        Returns:
            产品A销量
        """
        base_sales = np.random.normal(100, 15)
        
        if is_decline_period:
            base_sales *= (1 - decline_rate)
        
        return max(0, int(base_sales))
    
    def _generate_product_b_sales(self) -> int:
        """
        生成产品B销量
        
        Returns:
            产品B销量
        """
        base_sales = np.random.normal(80, 12)
        return max(0, int(base_sales))
    
    def _calculate_consumption(self, 
                              product_a_sales: int,
                              product_b_sales: int,
                              product_b_uses_component_a: int) -> int:
        """
        计算部件A消耗量
        
        Args:
            product_a_sales: 产品A销量
            product_b_sales: 产品B销量
            product_b_uses_component_a: 产品B是否使用部件A
            
        Returns:
            部件A消耗量
        """
        consumption_from_a = product_a_sales * 1
        
        consumption_from_b = product_b_sales * product_b_uses_component_a
        
        total_consumption = consumption_from_a + consumption_from_b
        
        return max(0, int(total_consumption))
    
    def _calculate_procurement(self, 
                               current_inventory: int,
                               consumption: int,
                               is_decline_period: bool) -> int:
        """
        计算部件A采购量
        
        Args:
            current_inventory: 当前库存
            consumption: 消耗量
            is_decline_period: 是否为销量下降期
            
        Returns:
            部件A采购量
        """
        target_inventory = 150
        
        if is_decline_period:
            target_inventory = 120
        
        if current_inventory < target_inventory * 0.8:
            procurement = int(np.random.normal(120, 20))
        elif current_inventory > target_inventory * 1.2:
            procurement = int(np.random.normal(60, 15))
        else:
            procurement = int(np.random.normal(90, 15))
        
        return max(0, procurement)
    
    def generate_counterfactual_data(self,
                                    start_date: str = "2024-06-01",
                                    end_date: str = "2024-12-31",
                                    product_a_sales_decline_start: str = "2024-11-01",
                                    product_a_decline_rate: float = 0.4,
                                    product_b_uses_component_a: int = 1) -> pd.DataFrame:
        """
        生成反事实数据（如果产品B使用部件A）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            product_a_sales_decline_start: 产品A销量开始下降的日期
            product_a_decline_rate: 产品A销量下降比例
            product_b_uses_component_a: 产品B是否使用部件A（反事实场景中为1）
            
        Returns:
            包含反事实库存数据的DataFrame
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        decline_start = datetime.strptime(product_a_sales_decline_start, "%Y-%m-%d")
        
        records = []
        current_inventory = 100
        
        current_date = start
        while current_date <= end:
            is_decline_period = current_date >= decline_start
            
            product_a_sales = self._generate_product_a_sales(is_decline_period, product_a_decline_rate)
            product_b_sales = self._generate_product_b_sales()
            
            component_a_consumption = self._calculate_consumption(
                product_a_sales, 
                product_b_sales, 
                product_b_uses_component_a
            )
            
            component_a_procurement = self._calculate_procurement(
                current_inventory,
                component_a_consumption,
                is_decline_period
            )
            
            current_inventory = current_inventory + component_a_procurement - component_a_consumption
            current_inventory = max(0, current_inventory)
            
            record = {
                "date": current_date,
                "product_a_sales": product_a_sales,
                "product_b_sales": product_b_sales,
                "product_b_uses_component_a": product_b_uses_component_a,
                "component_a_consumption": component_a_consumption,
                "component_a_inventory": current_inventory,
                "component_a_procurement": component_a_procurement,
                "is_decline_period": is_decline_period
            }
            records.append(record)
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        
        return df


def create_inventory_scenario():
    """
    创建库存分析场景
    
    Returns:
        实际数据和反事实数据
    """
    generator = InventoryDataGenerator(seed=42)
    
    actual_data = generator.generate_daily_data(
        start_date="2024-06-01",
        end_date="2024-12-31",
        product_a_sales_decline_start="2024-11-01",
        product_a_decline_rate=0.4
    )
    
    counterfactual_data = generator.generate_counterfactual_data(
        start_date="2024-06-01",
        end_date="2024-12-31",
        product_a_sales_decline_start="2024-11-01",
        product_a_decline_rate=0.4,
        product_b_uses_component_a=1
    )
    
    return actual_data, counterfactual_data


if __name__ == "__main__":
    actual_data, counterfactual_data = create_inventory_scenario()
    
    print("实际数据（产品B未使用部件A）：")
    print(actual_data.head(10))
    print(f"\n总记录数: {len(actual_data)}")
    print(f"日期范围: {actual_data['date'].min()} 至 {actual_data['date'].max()}")
    
    print("\n\n反事实数据（产品B使用部件A）：")
    print(counterfactual_data.head(10))
    
    actual_data.to_csv("inventory_actual_data.csv", index=False, encoding='utf-8')
    counterfactual_data.to_csv("inventory_counterfactual_data.csv", index=False, encoding='utf-8')
    print("\n数据已保存到CSV文件")
