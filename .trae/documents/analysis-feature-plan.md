# 数据分析功能实施计划

## 阶段目标
在数据分析阶段添加三种分析类型卡片，并实现本体探索的画布选择功能。

## 功能分析

1. **数据分析阶段添加卡片**
   - 本体探索 - 可视化探索本体关系
   - 数据分析 - 数据统计和分析
   - 根因分析 - 根因识别和分析

2. **箭头连接**
   - 添加的分析卡片自动指向对应的本体库

3. **本体探索画布**
   - 点击本体探索节点打开配置面板
   - 显示已定义的本体实体（从 ontology 节点配置中读取）
   - 用户可以选择实体
   - 根据已定义的关系自动连线展示

## 实施步骤

### 步骤 1：在 flowStore 中添加 addAnalysis 方法
- 支持三种分析类型：ontology_explore, data_analysis, root_cause
- 参数：name, type, ontologyId（关联的本体库ID）
- 位置计算：Y = START_Y + ROW_HEIGHT * (index * 1.5)
- 自动建立从本体库到分析卡的连接

### 步骤 2：更新 FlowCanvas 添加分析卡片按钮
- 在数据分析列（第7列）添加"添加分析"按钮
- 按钮点击后弹出选择分析类型

### 步骤 3：创建 AnalysisConfig 组件
- 本体探索配置：
  - 读取关联的本体库节点配置中的 entities 和 relationships
  - 显示实体选择画布（小画布）
  - 用户勾选要展示的实体
  - 根据 relationships 自动绘制实体之间的连线
- 数据分析配置：统计参数设置
- 根因分析配置：分析参数设置

### 步骤 4：更新 ConfigPanel
- 添加 AnalysisConfig 组件引用
- 在 switch 中添加 'analysis' case 处理

### 步骤 5：更新 AddNodeModal
- 支持选择分析类型（本体探索、数据分析、根因分析）
- 选择后调用 addAnalysis 方法

### 步骤 6：更新 flowStore 节点类型
- 分析节点类型需要支持：ontology_explore, data_analysis, root_cause
- 状态管理支持配置数据
