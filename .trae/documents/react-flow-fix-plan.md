# React Flow 重构修复计划

## 问题
1. 分区（4个区域）不见了 - 需要用框框起来，类似容器
2. 左侧工具栏拖拽到右侧画布添加节点的功能失效

## 解决方案

### 1. 分区容器（使用 React Flow 的 Group 节点或背景标注）
- 方案A：使用 React Flow 的 Group 节点作为容器
- 方案B：在画布背景上绘制分区框
- 推荐使用方案A：用 Group 节点实现可交互的容器

### 2. 拖拽添加节点
- React Flow 支持外部拖拽进入
- 需要使用 onDrop 和 onDragOver 事件
- 从 ToolPalette 拖拽时设置 dataTransfer

## 实施步骤

### 步骤 1：添加分区 Group 节点
- 创建 ZoneGroup 组件作为容器
- 4个区域：数据源、数据Pipeline、数据集、数据分析
- 每个区域用带标题的方框包裹

### 步骤 2：实现拖拽添加节点
- 在 ReactFlow 上添加 onDragOver 和 onDrop
- 从 ToolPalette 拖拽时传递节点类型
- 在 drop 时创建新节点

### 步骤 3：同步节点数据
- 确保 React Flow 的节点与 store 同步
- 节点位置变化时更新 store
