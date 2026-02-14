"""
制造企业根因分析 - 数据生成模块（Web版本）

场景说明：
- 制造企业有很多供应商，提供不同的零部件
- 有不同的工厂，有员工， 员工的熟练度不同生产效率不一样
- 供货商供货效率不一样
- 我们需要下单付款供应商才生产，我们的付款流程也会影响供货效率
- 我们需要根据数据发现生产效率对比上个月降低的原因是什么
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class ManufacturingDataGenerator:
    """制造企业数据生成器"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.suppliers = self._init_suppliers()
        self.factories = self._init_factories()
        self.employees = self._init_employees()
        
    def _init_suppliers(self) -> List[Dict]:
        """初始化供应商信息"""
        suppliers = [
            {"id": "S001", "name": "核心零部件供应商A", "type": "核心", "base_efficiency": 0.85, "parts": ["发动机", "变速箱"]},
            {"id": "S002", "name": "电子元件供应商B", "type": "核心", "base_efficiency": 0.80, "parts": ["控制芯片", "传感器"]},
            {"id": "S003", "name": "结构件供应商C", "type": "普通", "base_efficiency": 0.90, "parts": ["车架", "外壳"]},
            {"id": "S004", "name": "配件供应商D", "type": "普通", "base_efficiency": 0.88, "parts": ["轮胎", "玻璃"]},
            {"id": "S005", "name": "新材料供应商E", "type": "普通", "base_efficiency": 0.75, "parts": ["电池", "电机"]},
        ]
        return suppliers
    
    def _init_factories(self) -> List[Dict]:
        """初始化工厂信息"""
        factories = [
            {"id": "F001", "name": "华东工厂", "capacity": 1000, "equipment_age": 3},
            {"id": "F002", "name": "华南工厂", "capacity": 800, "equipment_age": 5},
            {"id": "F003", "name": "华北工厂", "capacity": 1200, "equipment_age": 2},
        ]
        return factories
    
    def _init_employees(self) -> List[Dict]:
        """初始化员工信息"""
        employees = []
        skill_levels = ["初级", "中级", "高级", "专家"]
        skill_weights = [0.3, 0.4, 0.2, 0.1]
        
        for factory in self.factories:
            num_employees = int(factory["capacity"] * 0.5)
            for i in range(num_employees):
                skill = np.random.choice(skill_levels, p=skill_weights)
                skill_score = {"初级": 0.5, "中级": 0.7, "高级": 0.85, "专家": 0.95}[skill]
                employees.append({
                    "id": f"{factory['id']}_E{i:03d}",
                    "factory_id": factory["id"],
                    "skill_level": skill,
                    "skill_score": skill_score,
                    "experience_years": np.random.exponential(3) + 0.5
                })
        return employees
    
    def generate_monthly_data(self, year: int, month: int, 
                               is_anomaly_month: bool = False,
                               anomaly_factors: Dict = None) -> pd.DataFrame:
        """
        生成月度生产数据
        
        Args:
            year: 年份
            month: 月份
            is_anomaly_month: 是否为异常月份（生产效率下降）
            anomaly_factors: 异常因素配置
        """
        records = []
        days_in_month = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day if month < 12 else 31
        
        default_anomaly = {
            "payment_delay": False,
            "supplier_issue": False,
            "employee_turnover": False,
            "equipment_failure": False
        }
        
        if anomaly_factors is None:
            anomaly_factors = default_anomaly
        else:
            anomaly_factors = {**default_anomaly, **anomaly_factors}
        
        for day in range(1, days_in_month + 1):
            for factory in self.factories:
                factory_employees = [e for e in self.employees if e["factory_id"] == factory["id"]]
                
                for supplier in self.suppliers:
                    payment_delay_days = self._generate_payment_delay(
                        anomaly_factors["payment_delay"]
                    )
                    
                    supplier_efficiency = self._calculate_supplier_efficiency(
                        supplier, payment_delay_days, anomaly_factors["supplier_issue"]
                    )
                    
                    parts_availability = self._calculate_parts_availability(
                        supplier_efficiency, payment_delay_days
                    )
                    
                    avg_employee_skill = np.mean([e["skill_score"] for e in factory_employees])
                    
                    if anomaly_factors["employee_turnover"]:
                        avg_employee_skill *= np.random.uniform(0.7, 0.85)
                    
                    equipment_status = self._calculate_equipment_status(
                        factory, anomaly_factors["equipment_failure"]
                    )
                    
                    capacity_utilization = np.random.uniform(0.7, 0.95)
                    
                    production_efficiency = self._calculate_production_efficiency(
                        parts_availability=parts_availability,
                        employee_skill=avg_employee_skill,
                        equipment_status=equipment_status,
                        capacity_utilization=capacity_utilization,
                        supplier_efficiency=supplier_efficiency,
                        payment_timeliness=1 - min(payment_delay_days / 30, 1)
                    )
                    
                    record = {
                        "date": datetime(year, month, day),
                        "year": year,
                        "month": month,
                        "factory_id": factory["id"],
                        "factory_name": factory["name"],
                        "factory_capacity": factory["capacity"],
                        "equipment_age": factory["equipment_age"],
                        "supplier_id": supplier["id"],
                        "supplier_name": supplier["name"],
                        "supplier_type": supplier["type"],
                        "supplier_base_efficiency": supplier["base_efficiency"],
                        "payment_delay_days": payment_delay_days,
                        "payment_timeliness": 1 - min(payment_delay_days / 30, 1),
                        "supplier_efficiency": supplier_efficiency,
                        "parts_availability": parts_availability,
                        "avg_employee_skill": avg_employee_skill,
                        "equipment_status": equipment_status,
                        "capacity_utilization": capacity_utilization,
                        "production_efficiency": production_efficiency,
                        "production_volume": int(factory["capacity"] * production_efficiency * capacity_utilization)
                    }
                    records.append(record)
        
        return pd.DataFrame(records)
    
    def _generate_payment_delay(self, has_delay: bool) -> float:
        """生成付款延迟天数"""
        if has_delay:
            return np.random.exponential(15) + 5
        return max(0, np.random.exponential(3))
    
    def _calculate_supplier_efficiency(self, supplier: Dict, 
                                        payment_delay: float,
                                        has_issue: bool) -> float:
        """计算供应商效率"""
        base = supplier["base_efficiency"]
        
        payment_penalty = min(payment_delay / 60, 0.3)
        
        if has_issue and supplier["type"] == "核心":
            issue_penalty = np.random.uniform(0.15, 0.25)
        else:
            issue_penalty = 0
        
        efficiency = base * (1 - payment_penalty - issue_penalty)
        noise = np.random.normal(0, 0.02)
        
        return max(0.3, min(1.0, efficiency + noise))
    
    def _calculate_parts_availability(self, supplier_efficiency: float,
                                       payment_delay: float) -> float:
        """计算零部件可用性"""
        base_availability = supplier_efficiency
        
        if payment_delay > 10:
            delay_penalty = (payment_delay - 10) * 0.01
            base_availability -= delay_penalty
        
        noise = np.random.normal(0, 0.03)
        return max(0.2, min(1.0, base_availability + noise))
    
    def _calculate_equipment_status(self, factory: Dict, has_failure: bool) -> float:
        """计算设备状态"""
        base_status = 1 - (factory["equipment_age"] * 0.03)
        
        if has_failure:
            failure_penalty = np.random.uniform(0.1, 0.2)
            base_status -= failure_penalty
        
        noise = np.random.normal(0, 0.02)
        return max(0.5, min(1.0, base_status + noise))
    
    def _calculate_production_efficiency(self,
                                         parts_availability: float,
                                         employee_skill: float,
                                         equipment_status: float,
                                         capacity_utilization: float,
                                         supplier_efficiency: float,
                                         payment_timeliness: float) -> float:
        """
        计算生产效率
        
        因果关系：
        - 零部件可用性 -> 生产效率 (权重: 0.25)
        - 员工技能 -> 生产效率 (权重: 0.20)
        - 设备状态 -> 生产效率 (权重: 0.15)
        - 产能利用率 -> 生产效率 (权重: 0.10)
        - 供应商效率 -> 生产效率 (权重: 0.15)
        - 付款及时性 -> 生产效率 (权重: 0.15)
        """
        efficiency = (
            0.25 * parts_availability +
            0.20 * employee_skill +
            0.15 * equipment_status +
            0.10 * capacity_utilization +
            0.15 * supplier_efficiency +
            0.15 * payment_timeliness
        )
        
        noise = np.random.normal(0, 0.02)
        
        return max(0.3, min(1.0, efficiency + noise))
    
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


def create_demo_scenario():
    """创建演示场景"""
    generator = ManufacturingDataGenerator(seed=42)
    
    anomaly_factors = {
        "payment_delay": True,
        "supplier_issue": True,
        "employee_turnover": False,
        "equipment_failure": False
    }
    
    normal_months = [(2024, 10), (2024, 11)]
    anomaly_month = (2024, 12)
    
    df = generator.generate_comparison_data(
        normal_months=normal_months,
        anomaly_month=anomaly_month,
        anomaly_factors=anomaly_factors
    )
    
    df["is_anomaly_month"] = (df["month"] == 12)
    
    return df, anomaly_factors
