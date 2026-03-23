"""
电商利润分析数据生成器

基于AWS文章中的在线商店智能手机销售场景生成模拟数据。

场景描述：
- 在线商店销售智能手机，零售价$999
- 2021年利润稳定，2022年初突然下降
- 需要分析利润下降的根本原因

因果因素：
- Shopping Event: 是否有购物活动（黑色星期五、网络星期一等）
- Ad Spend: 广告支出
- Page Views: 页面浏览量
- Unit Price: 单价（可能有折扣）
- Sold Units: 销售数量
- Revenue: 收入
- Operational Cost: 运营成本
- Profit: 利润
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class EcommerceDataGenerator:
    """电商数据生成器"""
    
    def __init__(self, seed: int = 42):
        """
        初始化数据生成器
        
        Args:
            seed: 随机种子
        """
        np.random.seed(seed)
        self.retail_price = 999
        
    def generate_daily_data(self, 
                           start_date: str,
                           end_date: str,
                           anomaly_start: str = None,
                           anomaly_factors: Dict = None) -> pd.DataFrame:
        """
        生成每日销售数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            anomaly_start: 异常开始日期 (可选)
            anomaly_factors: 异常因素配置
            
        Returns:
            包含每日销售数据的DataFrame
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if anomaly_start:
            anomaly_start_dt = datetime.strptime(anomaly_start, "%Y-%m-%d")
        else:
            anomaly_start_dt = end + timedelta(days=1)
        
        default_anomaly = {
            "ad_spend_reduction": False,
            "price_increase": False,
            "shopping_event_absence": False
        }
        
        if anomaly_factors is None:
            anomaly_factors = default_anomaly
        else:
            anomaly_factors = {**default_anomaly, **anomaly_factors}
        
        records = []
        current_date = start
        
        while current_date <= end:
            is_anomaly = current_date >= anomaly_start_dt
            
            shopping_event = self._generate_shopping_event(current_date, is_anomaly, anomaly_factors)
            
            ad_spend = self._generate_ad_spend(current_date, shopping_event, is_anomaly, anomaly_factors)
            
            page_views = self._generate_page_views(ad_spend, shopping_event, is_anomaly)
            
            unit_price = self._generate_unit_price(current_date, shopping_event, is_anomaly, anomaly_factors)
            
            sold_units = self._calculate_sold_units(page_views, unit_price, shopping_event, is_anomaly)
            
            revenue = sold_units * unit_price
            
            operational_cost = self._calculate_operational_cost(ad_spend, sold_units, unit_price)
            
            profit = revenue - operational_cost
            
            record = {
                "date": current_date,
                "year": current_date.year,
                "month": current_date.month,
                "day": current_date.day,
                "day_of_week": current_date.weekday(),
                "is_weekend": current_date.weekday() >= 5,
                "shopping_event": shopping_event,
                "ad_spend": ad_spend,
                "page_views": page_views,
                "unit_price": unit_price,
                "sold_units": sold_units,
                "revenue": revenue,
                "operational_cost": operational_cost,
                "profit": profit,
                "is_anomaly_period": is_anomaly
            }
            
            records.append(record)
            current_date += timedelta(days=1)
        
        return pd.DataFrame(records)
    
    def _generate_shopping_event(self, 
                                 date: datetime, 
                                 is_anomaly: bool,
                                 anomaly_factors: Dict) -> int:
        """
        生成购物活动标识
        
        Returns:
            1表示有购物活动，0表示没有
        """
        month = date.month
        day = date.day
        
        shopping_events = [
            (11, range(24, 31)),
            (12, range(1, 32)),
            (1, range(1, 15)),
            (7, range(1, 31)),
        ]
        
        for event_month, event_days in shopping_events:
            if month == event_month and day in event_days:
                if is_anomaly and anomaly_factors.get("shopping_event_absence", False):
                    if np.random.random() > 0.3:
                        return 0
                return 1
        
        return 0
    
    def _generate_ad_spend(self,
                          date: datetime,
                          shopping_event: int,
                          is_anomaly: bool,
                          anomaly_factors: Dict) -> float:
        """
        生成广告支出
        
        Returns:
            广告支出金额
        """
        base_spend = 5000
        
        if shopping_event:
            base_spend = 15000
        
        if is_anomaly and anomaly_factors.get("ad_spend_reduction", False):
            base_spend *= 0.5
        
        noise = np.random.normal(0, 500)
        
        return max(1000, base_spend + noise)
    
    def _generate_page_views(self,
                            ad_spend: float,
                            shopping_event: int,
                            is_anomaly: bool) -> int:
        """
        生成页面浏览量
        
        Returns:
            页面浏览量
        """
        base_views = 5000
        
        ad_effect = ad_spend / 100
        
        if shopping_event:
            base_views = 20000
        
        views = base_views + ad_effect * 10
        
        noise = np.random.normal(0, 500)
        
        return int(max(1000, views + noise))
    
    def _generate_unit_price(self,
                            date: datetime,
                            shopping_event: int,
                            is_anomaly: bool,
                            anomaly_factors: Dict) -> float:
        """
        生成单价
        
        Returns:
            单价
        """
        price = self.retail_price
        
        if shopping_event:
            discount = np.random.uniform(0.1, 0.2)
            price = self.retail_price * (1 - discount)
        
        if is_anomaly and anomaly_factors.get("price_increase", False):
            price *= 1.1
        
        noise = np.random.normal(0, 10)
        
        return max(500, price + noise)
    
    def _calculate_sold_units(self,
                             page_views: int,
                             unit_price: float,
                             shopping_event: int,
                             is_anomaly: bool) -> int:
        """
        计算销售数量
        
        Returns:
            销售数量
        """
        base_conversion = 0.02
        
        price_effect = (self.retail_price / unit_price) * 0.01
        
        if shopping_event:
            base_conversion = 0.05
        
        conversion_rate = base_conversion + price_effect
        
        noise = np.random.normal(0, 0.005)
        conversion_rate = max(0.005, conversion_rate + noise)
        
        sold_units = int(page_views * conversion_rate)
        
        return max(10, sold_units)
    
    def _calculate_operational_cost(self,
                                   ad_spend: float,
                                   sold_units: int,
                                   unit_price: float) -> float:
        """
        计算运营成本
        
        Returns:
            运营成本
        """
        production_cost = sold_units * (unit_price * 0.6)
        
        shipping_cost = sold_units * 15
        
        admin_cost = 2000
        
        total_cost = ad_spend + production_cost + shipping_cost + admin_cost
        
        noise = np.random.normal(0, 500)
        
        return max(0, total_cost + noise)
    
    def get_causal_graph(self) -> str:
        """
        获取因果图定义
        
        Returns:
            因果图字符串 (DOT格式)
        """
        causal_graph = """digraph {
            shopping_event -> ad_spend;
            shopping_event -> page_views;
            shopping_event -> unit_price;
            shopping_event -> sold_units;
            ad_spend -> page_views;
            ad_spend -> operational_cost;
            page_views -> sold_units;
            unit_price -> sold_units;
            unit_price -> revenue;
            sold_units -> revenue;
            revenue -> profit;
            operational_cost -> profit;
        }"""
        
        return causal_graph
    
    def get_variable_descriptions(self) -> Dict[str, str]:
        """
        获取变量描述
        
        Returns:
            变量描述字典
        """
        return {
            "shopping_event": "购物活动标识 (1=有活动, 0=无活动)",
            "ad_spend": "广告支出 (美元)",
            "page_views": "页面浏览量",
            "unit_price": "单价 (美元)",
            "sold_units": "销售数量",
            "revenue": "收入 (美元)",
            "operational_cost": "运营成本 (美元)",
            "profit": "利润 (美元)"
        }


def create_demo_scenario():
    """
    创建演示场景
    
    Returns:
        数据DataFrame和异常因素配置
    """
    generator = EcommerceDataGenerator(seed=42)
    
    anomaly_factors = {
        "ad_spend_reduction": True,
        "price_increase": True,
        "shopping_event_absence": False
    }
    
    df = generator.generate_daily_data(
        start_date="2021-01-01",
        end_date="2022-03-31",
        anomaly_start="2022-01-01",
        anomaly_factors=anomaly_factors
    )
    
    return df, anomaly_factors, generator.get_causal_graph()


if __name__ == "__main__":
    df, anomaly_factors, causal_graph = create_demo_scenario()
    
    print("=" * 60)
    print("电商利润分析演示数据")
    print("=" * 60)
    print(f"\n数据概览:")
    print(f"  总记录数: {len(df)}")
    print(f"  时间范围: {df['date'].min()} 至 {df['date'].max()}")
    print(f"  正常时期: {len(df[~df['is_anomaly_period']])} 天")
    print(f"  异常时期: {len(df[df['is_anomaly_period']])} 天")
    
    print(f"\n异常因素配置:")
    for factor, enabled in anomaly_factors.items():
        print(f"  {factor}: {'启用' if enabled else '未启用'}")
    
    print(f"\n因果图:")
    print(causal_graph)
    
    print(f"\n数据样本 (前5行):")
    print(df.head())
    
    print(f"\n统计摘要:")
    print(df.describe())
    
    normal_data = df[~df['is_anomaly_period']]
    anomaly_data = df[df['is_anomaly_period']]
    
    print(f"\n利润对比:")
    print(f"  正常时期平均利润: ${normal_data['profit'].mean():,.2f}")
    print(f"  异常时期平均利润: ${anomaly_data['profit'].mean():,.2f}")
    print(f"  利润变化: {(anomaly_data['profit'].mean() - normal_data['profit'].mean()) / normal_data['profit'].mean() * 100:.2f}%")
