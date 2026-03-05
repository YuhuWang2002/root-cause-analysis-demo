"""
实际场景中构造反事实数据的方法

在真实业务中，我们无法同时观察到干预和未干预的情况，
因此需要使用科学的方法来估计反事实结果。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class CounterfactualDataConstructor:
    """反事实数据构造器"""
    
    def __init__(self, historical_data: pd.DataFrame):
        """
        初始化反事实数据构造器
        
        Args:
            historical_data: 历史数据
        """
        self.historical_data = historical_data
        self.models = {}
        
    def method1_causal_model_prediction(self,
                                       intervention: Dict,
                                       outcome_variable: str,
                                       feature_variables: List[str]) -> pd.DataFrame:
        """
        方法1：因果模型预测法
        
        原理：
        1. 基于历史数据训练因果模型
        2. 修改干预变量的值
        3. 使用模型预测反事实结果
        
        优点：
        - 可以量化因果效应
        - 适用于各种干预场景
        - 可以控制混杂变量
        
        缺点：
        - 需要正确的因果图
        - 模型假设可能不成立
        
        Args:
            intervention: 干预条件，如 {'product_b_uses_component_a': 1}
            outcome_variable: 结果变量
            feature_variables: 特征变量列表
            
        Returns:
            反事实数据
        """
        print("=== 方法1：因果模型预测法 ===")
        
        # 训练因果模型
        X = self.historical_data[feature_variables]
        y = self.historical_data[outcome_variable]
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # 构造反事实数据
        counterfactual_data = self.historical_data.copy()
        
        # 应用干预
        for var, value in intervention.items():
            counterfactual_data[var] = value
        
        # 预测反事实结果
        X_cf = counterfactual_data[feature_variables]
        counterfactual_data[outcome_variable] = model.predict(X_cf)
        
        print(f"✅ 已基于因果模型预测反事实结果")
        print(f"   - 干预条件: {intervention}")
        print(f"   - 结果变量: {outcome_variable}")
        print(f"   - 实际{outcome_variable}均值: {self.historical_data[outcome_variable].mean():.2f}")
        print(f"   - 反事实{outcome_variable}均值: {counterfactual_data[outcome_variable].mean():.2f}")
        
        return counterfactual_data
    
    def method2_historical_control(self,
                                  pre_intervention_period: str,
                                  post_intervention_period: str,
                                  intervention_date: str) -> pd.DataFrame:
        """
        方法2：历史对照法
        
        原理：
        1. 使用干预前的数据作为基线
        2. 假设如果没有干预，趋势会延续
        3. 对比实际结果与预测结果
        
        优点：
        - 简单直观
        - 不需要复杂的模型
        - 适用于有明显趋势的数据
        
        缺点：
        - 假设趋势延续
        - 无法控制其他因素变化
        - 需要足够的历史数据
        
        Args:
            pre_intervention_period: 干预前时期
            post_intervention_period: 干预后时期
            intervention_date: 干预日期
            
        Returns:
            反事实数据
        """
        print("\n=== 方法2：历史对照法 ===")
        
        # 分割数据
        pre_data = self.historical_data[
            self.historical_data['date'] < intervention_date
        ]
        post_data = self.historical_data[
            self.historical_data['date'] >= intervention_date
        ]
        
        # 计算干预前的基线
        baseline = pre_data.mean()
        
        # 构造反事实数据（假设趋势延续）
        counterfactual_data = post_data.copy()
        
        # 使用干预前的均值作为反事实
        for col in counterfactual_data.columns:
            if col != 'date' and col in baseline:
                counterfactual_data[col] = baseline[col]
        
        print(f"✅ 已使用历史对照法构造反事实数据")
        print(f"   - 干预日期: {intervention_date}")
        print(f"   - 干预前数据量: {len(pre_data)}")
        print(f"   - 干预后数据量: {len(post_data)}")
        
        return counterfactual_data
    
    def method3_similar_object_control(self,
                                      treatment_group: pd.DataFrame,
                                      control_group: pd.DataFrame,
                                      matching_variables: List[str]) -> pd.DataFrame:
        """
        方法3：相似对象对照法
        
        原理：
        1. 找到与干预组相似但未受干预的对象
        2. 使用对照组的结果作为反事实
        3. 需要匹配关键特征
        
        优点：
        - 可以控制混杂变量
        - 更接近真实情况
        - 适用于有对照组的场景
        
        缺点：
        - 需要找到合适的对照组
        - 匹配可能不完全
        - 可能存在未观察的混杂
        
        Args:
            treatment_group: 干预组数据
            control_group: 对照组数据
            matching_variables: 匹配变量列表
            
        Returns:
            反事实数据
        """
        print("\n=== 方法3：相似对象对照法 ===")
        
        # 计算干预组和对照组的匹配得分
        from sklearn.preprocessing import StandardScaler
        from sklearn.neighbors import NearestNeighbors
        
        # 标准化匹配变量
        scaler = StandardScaler()
        treatment_features = scaler.fit_transform(treatment_group[matching_variables])
        control_features = scaler.transform(control_group[matching_variables])
        
        # 找到最近的对照对象
        nn = NearestNeighbors(n_neighbors=1, metric='euclidean')
        nn.fit(control_features)
        distances, indices = nn.kneighbors(treatment_features)
        
        # 构造反事实数据
        counterfactual_data = control_group.iloc[indices.flatten()].copy()
        counterfactual_data.index = treatment_group.index
        
        print(f"✅ 已使用相似对象对照法构造反事实数据")
        print(f"   - 干预组样本量: {len(treatment_group)}")
        print(f"   - 对照组样本量: {len(control_group)}")
        print(f"   - 匹配变量: {matching_variables}")
        print(f"   - 平均匹配距离: {distances.mean():.4f}")
        
        return counterfactual_data
    
    def method4_difference_in_differences(self,
                                         treatment_group: pd.DataFrame,
                                         control_group: pd.DataFrame,
                                         pre_period: str,
                                         post_period: str) -> Dict:
        """
        方法4：双重差分法（DID）
        
        原理：
        1. 比较干预组和对照组在干预前后的变化
        2. 计算双重差分估计量
        3. 控制时间趋势和组间差异
        
        优点：
        - 可以控制时间不变的混杂
        - 可以控制组间差异
        - 适用于面板数据
        
        缺点：
        - 需要平行趋势假设
        - 需要对照组
        - 对时间点敏感
        
        Args:
            treatment_group: 干预组数据
            control_group: 对照组数据
            pre_period: 干预前时期
            post_period: 干预后时期
            
        Returns:
            双重差分结果
        """
        print("\n=== 方法4：双重差分法（DID） ===")
        
        # 计算干预组的前后差异
        treatment_pre = treatment_group[treatment_group['period'] == pre_period]['outcome'].mean()
        treatment_post = treatment_group[treatment_group['period'] == post_period]['outcome'].mean()
        treatment_diff = treatment_post - treatment_pre
        
        # 计算对照组的前后差异
        control_pre = control_group[control_group['period'] == pre_period]['outcome'].mean()
        control_post = control_group[control_group['period'] == post_period]['outcome'].mean()
        control_diff = control_post - control_pre
        
        # 计算双重差分
        did_estimate = treatment_diff - control_diff
        
        print(f"✅ 已使用双重差分法估计因果效应")
        print(f"   - 干预组变化: {treatment_diff:.4f}")
        print(f"   - 对照组变化: {control_diff:.4f}")
        print(f"   - DID估计量: {did_estimate:.4f}")
        
        return {
            'treatment_diff': treatment_diff,
            'control_diff': control_diff,
            'did_estimate': did_estimate
        }
    
    def method5_regression_discontinuity(self,
                                        running_variable: str,
                                        cutoff: float,
                                        outcome_variable: str) -> Dict:
        """
        方法5：断点回归设计（RDD）
        
        原理：
        1. 利用某个连续变量的临界点
        2. 比较临界点两侧的结果
        3. 估计局部平均处理效应
        
        优点：
        - 可以看作准实验
        - 不需要对照组
        - 可以估计局部因果效应
        
        缺点：
        - 需要明确的临界点
        - 只能估计局部效应
        - 对带宽选择敏感
        
        Args:
            running_variable: 运行变量
            cutoff: 临界点
            outcome_variable: 结果变量
            
        Returns:
            RDD结果
        """
        print("\n=== 方法5：断点回归设计（RDD） ===")
        
        # 分割数据
        left_data = self.historical_data[
            self.historical_data[running_variable] < cutoff
        ]
        right_data = self.historical_data[
            self.historical_data[running_variable] >= cutoff
        ]
        
        # 计算临界点两侧的结果
        left_mean = left_data[outcome_variable].mean()
        right_mean = right_data[outcome_variable].mean()
        
        # 估计处理效应
        treatment_effect = right_mean - left_mean
        
        print(f"✅ 已使用断点回归设计估计因果效应")
        print(f"   - 运行变量: {running_variable}")
        print(f"   - 临界点: {cutoff}")
        print(f"   - 左侧均值: {left_mean:.4f}")
        print(f"   - 右侧均值: {right_mean:.4f}")
        print(f"   - 处理效应: {treatment_effect:.4f}")
        
        return {
            'left_mean': left_mean,
            'right_mean': right_mean,
            'treatment_effect': treatment_effect
        }


def demonstrate_methods():
    """演示各种反事实数据构造方法"""
    
    print("="*80)
    print("实际场景中构造反事实数据的方法演示")
    print("="*80)
    
    # 生成示例数据
    np.random.seed(42)
    n = 1000
    
    historical_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=n, freq='D'),
        'product_a_sales': np.random.normal(100, 15, n),
        'product_b_sales': np.random.normal(80, 12, n),
        'product_b_uses_component_a': np.random.choice([0, 1], n, p=[0.7, 0.3]),
        'component_a_consumption': np.zeros(n),
        'component_a_inventory': np.zeros(n),
        'other_factor': np.random.normal(50, 10, n)
    })
    
    # 计算消耗和库存
    historical_data['component_a_consumption'] = (
        historical_data['product_a_sales'] * 1 + 
        historical_data['product_b_sales'] * historical_data['product_b_uses_component_a']
    )
    historical_data['component_a_inventory'] = np.random.normal(150, 30, n)
    
    # 创建构造器
    constructor = CounterfactualDataConstructor(historical_data)
    
    # 方法1：因果模型预测法
    cf_data1 = constructor.method1_causal_model_prediction(
        intervention={'product_b_uses_component_a': 1},
        outcome_variable='component_a_consumption',
        feature_variables=['product_a_sales', 'product_b_sales', 'product_b_uses_component_a', 'other_factor']
    )
    
    # 方法2：历史对照法
    cf_data2 = constructor.method2_historical_control(
        pre_intervention_period='2024-01-01',
        post_intervention_period='2024-06-01',
        intervention_date='2024-06-01'
    )
    
    print("\n" + "="*80)
    print("总结：实际场景中选择方法的建议")
    print("="*80)
    print("""
1. **因果模型预测法**（推荐）
   - 适用场景：有明确的因果假设，需要量化干预效果
   - 数据要求：历史数据，明确的因果图
   - 实施难度：中等

2. **历史对照法**
   - 适用场景：有明显趋势，干预前后对比
   - 数据要求：足够的历史数据
   - 实施难度：简单

3. **相似对象对照法**
   - 适用场景：有对照组，可以找到相似对象
   - 数据要求：干预组和对照组数据
   - 实施难度：中等

4. **双重差分法**
   - 适用场景：面板数据，有对照组
   - 数据要求：干预前后数据，干预组和对照组
   - 实施难度：中等

5. **断点回归设计**
   - 适用场景：有明确的临界点
   - 数据要求：连续变量，临界点两侧数据
   - 实施难度：较难
    """)


if __name__ == "__main__":
    demonstrate_methods()
