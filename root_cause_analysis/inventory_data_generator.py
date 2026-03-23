"""
制造企业根因分析 - 库存死货问题数据生成模块

场景说明：
- 制造企业采购部件，有的部件可以被不同产品使用
- 部件需要保证一定的库存水平，有消耗和补充
- 问题：产品可以用同样功能的不同型号/供应商的部件
- 但生产工厂不知道有可代替的部件，导致某些部件成为死库存，占用大量资金
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class InventoryDataGenerator:
    """库存死货问题数据生成器"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.products = self._init_products()
        self.parts = self._init_parts()
        self.factories = self._init_factories()
        self.suppliers = self._init_suppliers()
        self.part_substitutes = self._init_part_substitutes()
        
    def _init_products(self) -> List[Dict]:
        """初始化产品信息"""
        products = [
            {"id": "P001", "name": "产品A", "base_demand": 100, "price": 5000},
            {"id": "P002", "name": "产品B", "base_demand": 80, "price": 4500},
            {"id": "P003", "name": "产品C", "base_demand": 120, "price": 6000},
        ]
        return products
    
    def _init_parts(self) -> List[Dict]:
        """初始化部件信息"""
        parts = [
            {"id": "PT001", "name": "部件A1", "type": "核心", "unit_cost": 100, "min_stock": 50},
            {"id": "PT002", "name": "部件A2", "type": "核心", "unit_cost": 95, "min_stock": 50},
            {"id": "PT003", "name": "部件B1", "type": "普通", "unit_cost": 50, "min_stock": 30},
            {"id": "PT004", "name": "部件B2", "type": "普通", "unit_cost": 48, "min_stock": 30},
            {"id": "PT005", "name": "部件C1", "type": "核心", "unit_cost": 150, "min_stock": 40},
        ]
        return parts
    
    def _init_factories(self) -> List[Dict]:
        """初始化工厂信息"""
        factories = [
            {"id": "F001", "name": "华东工厂", "production_capacity": 200},
            {"id": "F002", "name": "华南工厂", "production_capacity": 180},
        ]
        return factories
    
    def _init_suppliers(self) -> List[Dict]:
        """初始化供应商信息"""
        suppliers = [
            {"id": "S001", "name": "供应商X", "reliability": 0.95, "lead_time": 3},
            {"id": "S002", "name": "供应商Y", "reliability": 0.92, "lead_time": 4},
            {"id": "S003", "name": "供应商Z", "reliability": 0.88, "lead_time": 5},
        ]
        return suppliers
    
    def _init_part_substitutes(self) -> Dict:
        """初始化部件替代关系"""
        substitutes = {
            "PT001": ["PT002"],  # 部件A1可以被部件A2替代
            "PT002": ["PT001"],  # 部件A2可以被部件A1替代
            "PT003": ["PT004"],  # 部件B1可以被部件B2替代
            "PT004": ["PT003"],  # 部件B2可以被部件B1替代
            "PT005": [],  # 部件C1没有替代
        }
        return substitutes
    
    def _get_product_parts(self, product_id: str) -> List[str]:
        """获取产品所需的部件"""
        if product_id == "P001":
            return ["PT001", "PT003"]  # 产品A需要部件A1和B1
        elif product_id == "P002":
            return ["PT002", "PT004"]  # 产品B需要部件A2和B2
        elif product_id == "P003":
            return ["PT001", "PT005"]  # 产品C需要部件A1和C1
        return []
    
    def generate_monthly_data(self, year: int, month: int, 
                               is_anomaly_month: bool = False,
                               anomaly_factors: Dict = None) -> pd.DataFrame:
        """
        生成月度库存数据
        
        Args:
            year: 年份
            month: 月份
            is_anomaly_month: 是否为异常月份（出现死库存）
            anomaly_factors: 异常因素配置
        """
        records = []
        days_in_month = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day if month < 12 else 31
        
        default_anomaly = {
            "demand_decrease": False,  # 需求下降
            "substitute_awareness": False,  # 替代部件意识缺失
            "stock_management_issue": False  # 库存管理问题
        }
        
        if anomaly_factors is None:
            anomaly_factors = default_anomaly
        else:
            anomaly_factors = {**default_anomaly, **anomaly_factors}
        
        # 初始化库存
        initial_stock = {}
        for part in self.parts:
            initial_stock[part["id"]] = part["min_stock"] + np.random.randint(10, 30)
        
        stock_levels = initial_stock.copy()
        
        for day in range(1, days_in_month + 1):
            for factory in self.factories:
                for product in self.products:
                    # 计算产品需求
                    base_demand = product["base_demand"]
                    if anomaly_factors["demand_decrease"] and product["id"] == "P001":
                        demand_factor = np.random.uniform(0.4, 0.6)  # 需求大幅下降
                    else:
                        demand_factor = np.random.uniform(0.8, 1.2)
                    
                    daily_demand = int(base_demand * demand_factor / 30)
                    
                    # 获取产品所需部件
                    required_parts = self._get_product_parts(product["id"])
                    
                    for part_id in required_parts:
                        part = next(p for p in self.parts if p["id"] == part_id)
                        
                        # 检查是否有替代部件可用
                        has_substitute = False
                        substitute_used = None
                        
                        if not anomaly_factors["substitute_awareness"]:
                            substitutes = self.part_substitutes.get(part_id, [])
                            for sub_id in substitutes:
                                if stock_levels.get(sub_id, 0) > part["min_stock"]:
                                    has_substitute = True
                                    substitute_used = sub_id
                                    break
                        
                        # 计算部件消耗
                        if has_substitute and substitute_used:
                            # 使用替代部件
                            stock_levels[substitute_used] = max(0, stock_levels[substitute_used] - daily_demand)
                            actual_part_used = substitute_used
                        else:
                            # 使用原部件
                            stock_levels[part_id] = max(0, stock_levels[part_id] - daily_demand)
                            actual_part_used = part_id
                        
                        # 库存补充（简单的补货逻辑）
                        if stock_levels.get(part_id, 0) < part["min_stock"]:
                            reorder_quantity = part["min_stock"] * 2 - stock_levels[part_id]
                            stock_levels[part_id] += reorder_quantity
                        
                        # 计算死库存指标（超过最小库存的2倍）
                        dead_stock_threshold = part["min_stock"] * 2
                        dead_stock_amount = max(0, stock_levels[part_id] - dead_stock_threshold)
                        is_dead_stock = dead_stock_amount > 0
                        
                        # 计算库存周转率（简化计算）
                        stock_turnover = min(1.0, daily_demand / max(1, stock_levels[part_id]))
                        
                        # 计算资金占用
                        capital_tied = stock_levels[part_id] * part["unit_cost"]
                        
                        # 计算替代部件意识指数
                        substitute_awareness = 1.0 if has_substitute else 0.0
                        if anomaly_factors["substitute_awareness"]:
                            substitute_awareness = 0.0
                        
                        # 增加死库存与替代部件意识的因果关系
                        if anomaly_factors["substitute_awareness"] and part_id == "PT001":
                            # 当替代部件意识缺失时，部件A1容易成为死库存
                            dead_stock_amount = max(dead_stock_amount, part["min_stock"] * 1.5)
                        
                        # 增加需求下降的影响
                        if anomaly_factors["demand_decrease"] and product["id"] == "P001" and part_id == "PT001":
                            # 产品A需求下降导致部件A1库存积压
                            dead_stock_amount = max(dead_stock_amount, part["min_stock"] * 2)
                        
                        record = {
                            "date": datetime(year, month, day),
                            "year": year,
                            "month": month,
                            "factory_id": factory["id"],
                            "factory_name": factory["name"],
                            "product_id": product["id"],
                            "product_name": product["name"],
                            "part_id": part_id,
                            "part_name": part["name"],
                            "part_type": part["type"],
                            "part_unit_cost": part["unit_cost"],
                            "required_part_id": part_id,
                            "actual_part_used": actual_part_used,
                            "daily_demand": daily_demand,
                            "initial_stock": initial_stock[part_id],
                            "current_stock": stock_levels[part_id],
                            "min_stock": part["min_stock"],
                            "dead_stock_amount": dead_stock_amount,
                            "is_dead_stock": is_dead_stock,
                            "stock_turnover": stock_turnover,
                            "capital_tied": capital_tied,
                            "substitute_awareness": substitute_awareness,
                            "has_substitute": has_substitute,
                            "substitute_used": substitute_used,
                            "demand_factor": demand_factor,
                            "is_anomaly_day": is_anomaly_month
                        }
                        records.append(record)
        
        return pd.DataFrame(records)
    
    def generate_comparison_data(self, 
                                  normal_months: List[Tuple[int, int]],
                                  anomaly_month: Tuple[int, int],
                                  anomaly_factors: Dict = None) -> pd.DataFrame:
        """
        生成对比数据（正常月份 vs 异常月份）
        """
        all_data = []
        
        for year, month in normal_months:
            df = self.generate_monthly_data(year, month, is_anomaly_month=False)
            all_data.append(df)
        
        year, month = anomaly_month
        df = self.generate_monthly_data(year, month, is_anomaly_month=True, 
                                        anomaly_factors=anomaly_factors)
        all_data.append(df)
        
        return pd.concat(all_data, ignore_index=True)


def create_inventory_demo_scenario():
    """创建库存死货问题演示场景"""
    generator = InventoryDataGenerator(seed=42)
    
    anomaly_factors = {
        "demand_decrease": True,  # 产品A需求下降
        "substitute_awareness": True,  # 替代部件意识缺失
        "stock_management_issue": True  # 库存管理问题
    }
    
    normal_months = [(2024, 10), (2024, 11)]
    anomaly_month = (2024, 12)
    
    df = generator.generate_comparison_data(
        normal_months=normal_months,
        anomaly_month=anomaly_month,
        anomaly_factors=anomaly_factors
    )
    
    df["is_anomaly_month"] = (df["year"] == anomaly_month[0]) & (df["month"] == anomaly_month[1])
    
    return df, anomaly_factors


if __name__ == "__main__":
    df, factors = create_inventory_demo_scenario()
    print("库存数据概览：")
    print(df.head())
    print("\n各部件死库存情况：")
    dead_stock_summary = df.groupby(["part_id", "part_name", "is_anomaly_month"]).agg({
        "dead_stock_amount": "mean",
        "capital_tied": "mean",
        "stock_turnover": "mean"
    }).round(2)
    print(dead_stock_summary)
    print("\n异常因素：", factors)
