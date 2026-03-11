"""
部件PAC900S12-B2-1库存高因果根因分析 - 数据生成模块

场景说明：
- 昆仑2280销量下降，导致PAC900S12-B2-1（服务器白金900W）库存偏高
- 2288HV7未使用PAC900S12-B2-1（历史全为0）
- 需要验证：2288HV7未使用PAC900S12-B2-1是PAC900S12-B2-1库存高的核心因果根因

数据字段：
- 日期
- 昆仑2280销量、2288HV7销量
- 2288HV7是否使用PAC900S12-B2-1（历史全为0）
- PAC900S12-B2-1消耗量、PAC900S12-B2-1期末库存
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple


class InventoryDataGenerator:
    """PAC900S12-B2-1库存数据生成器"""
    
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
                           kunlun_2280_sales_decline_start: str = "2024-11-01",
                           kunlun_2280_decline_rate: float = 0.4) -> pd.DataFrame:
        """
        生成每日库存数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            kunlun_2280_sales_decline_start: 昆仑2280销量开始下降的日期
            kunlun_2280_decline_rate: 昆仑2280销量下降比例
            
        Returns:
            包含库存数据的DataFrame
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        decline_start = datetime.strptime(kunlun_2280_sales_decline_start, "%Y-%m-%d")
        
        records = []
        current_inventory = 100
        
        current_date = start
        while current_date <= end:
            is_decline_period = current_date >= decline_start
            
            kunlun_2280_sales = self._generate_kunlun_2280_sales(is_decline_period, kunlun_2280_decline_rate)
            server_2288hv7_sales = self._generate_server_2288hv7_sales()
            
            server_2288hv7_uses_pac900s12_b2_1 = 0
            
            pac900s12_b2_1_consumption = self._calculate_consumption(
                kunlun_2280_sales, 
                server_2288hv7_sales, 
                server_2288hv7_uses_pac900s12_b2_1
            )
            
            pac900s12_b2_1_procurement = self._calculate_procurement(
                current_inventory,
                pac900s12_b2_1_consumption,
                is_decline_period
            )
            
            current_inventory = current_inventory + pac900s12_b2_1_procurement - pac900s12_b2_1_consumption
            current_inventory = max(0, current_inventory)
            
            record = {
                "date": current_date,
                "kunlun_2280_sales": kunlun_2280_sales,
                "server_2288hv7_sales": server_2288hv7_sales,
                "server_2288hv7_uses_pac900s12_b2_1": server_2288hv7_uses_pac900s12_b2_1,
                "pac900s12_b2_1_consumption": pac900s12_b2_1_consumption,
                "pac900s12_b2_1_inventory": current_inventory,
                "pac900s12_b2_1_procurement": pac900s12_b2_1_procurement,
                "is_decline_period": is_decline_period
            }
            records.append(record)
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def _generate_kunlun_2280_sales(self, is_decline_period: bool, decline_rate: float) -> int:
        """
        生成昆仑2280销量
        
        Args:
            is_decline_period: 是否为销量下降期
            decline_rate: 销量下降比例
            
        Returns:
            昆仑2280销量
        """
        base_sales = np.random.normal(100, 15)
        
        if is_decline_period:
            base_sales *= (1 - decline_rate)
        
        return max(0, int(base_sales))
    
    def _generate_server_2288hv7_sales(self) -> int:
        """
        生成2288HV7销量
        
        Returns:
            2288HV7销量
        """
        base_sales = np.random.normal(80, 12)
        return max(0, int(base_sales))
    
    def _calculate_consumption(self, 
                              kunlun_2280_sales: int,
                              server_2288hv7_sales: int,
                              server_2288hv7_uses_pac900s12_b2_1: int) -> int:
        """
        计算PAC900S12-B2-1消耗量
        
        Args:
            kunlun_2280_sales: 昆仑2280销量
            server_2288hv7_sales: 2288HV7销量
            server_2288hv7_uses_pac900s12_b2_1: 2288HV7是否使用PAC900S12-B2-1
            
        Returns:
            PAC900S12-B2-1消耗量
        """
        consumption_from_kunlun_2280 = kunlun_2280_sales * 1
        
        consumption_from_2288hv7 = server_2288hv7_sales * server_2288hv7_uses_pac900s12_b2_1
        
        total_consumption = consumption_from_kunlun_2280 + consumption_from_2288hv7
        
        return max(0, int(total_consumption))
    
    def _calculate_procurement(self, 
                               current_inventory: int,
                               consumption: int,
                               is_decline_period: bool) -> int:
        """
        计算PAC900S12-B2-1采购量
        
        Args:
            current_inventory: 当前库存
            consumption: 消耗量
            is_decline_period: 是否为销量下降期
            
        Returns:
            PAC900S12-B2-1采购量
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
                                    kunlun_2280_sales_decline_start: str = "2024-11-01",
                                    kunlun_2280_decline_rate: float = 0.4,
                                    server_2288hv7_uses_pac900s12_b2_1: int = 1) -> pd.DataFrame:
        """
        生成反事实数据（如果2288HV7使用PAC900S12-B2-1）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            kunlun_2280_sales_decline_start: 昆仑2280销量开始下降的日期
            kunlun_2280_decline_rate: 昆仑2280销量下降比例
            server_2288hv7_uses_pac900s12_b2_1: 2288HV7是否使用PAC900S12-B2-1（反事实场景中为1）
            
        Returns:
            包含反事实库存数据的DataFrame
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        decline_start = datetime.strptime(kunlun_2280_sales_decline_start, "%Y-%m-%d")
        
        records = []
        current_inventory = 100
        
        current_date = start
        while current_date <= end:
            is_decline_period = current_date >= decline_start
            
            kunlun_2280_sales = self._generate_kunlun_2280_sales(is_decline_period, kunlun_2280_decline_rate)
            server_2288hv7_sales = self._generate_server_2288hv7_sales()
            
            pac900s12_b2_1_consumption = self._calculate_consumption(
                kunlun_2280_sales, 
                server_2288hv7_sales, 
                server_2288hv7_uses_pac900s12_b2_1
            )
            
            pac900s12_b2_1_procurement = self._calculate_procurement(
                current_inventory,
                pac900s12_b2_1_consumption,
                is_decline_period
            )
            
            current_inventory = current_inventory + pac900s12_b2_1_procurement - pac900s12_b2_1_consumption
            current_inventory = max(0, current_inventory)
            
            record = {
                "date": current_date,
                "kunlun_2280_sales": kunlun_2280_sales,
                "server_2288hv7_sales": server_2288hv7_sales,
                "server_2288hv7_uses_pac900s12_b2_1": server_2288hv7_uses_pac900s12_b2_1,
                "pac900s12_b2_1_consumption": pac900s12_b2_1_consumption,
                "pac900s12_b2_1_inventory": current_inventory,
                "pac900s12_b2_1_procurement": pac900s12_b2_1_procurement,
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
        kunlun_2280_sales_decline_start="2024-11-01",
        kunlun_2280_decline_rate=0.4
    )
    
    counterfactual_data = generator.generate_counterfactual_data(
        start_date="2024-06-01",
        end_date="2024-12-31",
        kunlun_2280_sales_decline_start="2024-11-01",
        kunlun_2280_decline_rate=0.4,
        server_2288hv7_uses_pac900s12_b2_1=1
    )
    
    return actual_data, counterfactual_data


if __name__ == "__main__":
    actual_data, counterfactual_data = create_inventory_scenario()
    
    print("实际数据（2288HV7未使用PAC900S12-B2-1）：")
    print(actual_data.head(10))
    print(f"\n总记录数: {len(actual_data)}")
    print(f"日期范围: {actual_data['date'].min()} 至 {actual_data['date'].max()}")
    
    print("\n\n反事实数据（2288HV7使用PAC900S12-B2-1）：")
    print(counterfactual_data.head(10))
    
    actual_data.to_csv("inventory_actual_data.csv", index=False, encoding='utf-8')
    counterfactual_data.to_csv("inventory_counterfactual_data.csv", index=False, encoding='utf-8')
    print("\n数据已保存到CSV文件")
