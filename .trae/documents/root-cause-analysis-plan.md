# 实现根因分析功能计划

## 任务目标
1. 在前端创建"根因分析"页面，实现app_refactored.py中6.2步骤的"为什么会发生"功能
2. 在项目画布的"根因分析"节点配置中添加按钮，跳转到根因分析页面

## 实现步骤

### 1. 创建根因分析后端API
- 在 `backend/routes/` 下创建 `root_cause.py` 路由文件
- 实现因果图构建API（调用LLM）
- 实现因果分析API（使用DoWhy）
- 实现反事实分析API

### 2. 创建根因分析前端页面
- 在 `src/pages/` 下创建 `RootCauseAnalysis.tsx` 页面
- 页面包含：
  - 因果图展示（使用vis-network或react-flow）
  - 因果图编辑（DOT格式）
  - 因果分析运行按钮
  - 分析结果展示（反事实分析、库存降低量等）

### 3. 添加前端路由
- 在 `App.tsx` 中添加根因分析路由 `/root-cause/:projectId`

### 4. 修改节点配置
- 在 `ConfigPanel.tsx` 的 `AnalysisConfig` 中：
  - 判断 `analysisType === 'root_cause'` 时显示"打开根因分析"按钮
  - 创建或获取根因分析配置并保存到节点配置
  - 跳转到根因分析页面

### 5. 实现细节

#### 5.1 后端API设计
```
POST /api/root-cause/build-graph
- 根据数据构建因果图（调用LLM）

POST /api/root-cause/run-analysis
- 运行因果分析（使用DoWhy）

GET /api/root-cause/results/:projectId
- 获取分析结果
```

#### 5.2 前端页面设计
- 左侧：因果图编辑区域（DOT格式）
- 右侧：因果图可视化（网络图）
- 底部：分析结果展示

## 预期文件修改
1. 新增: `backend/routes/root_cause.py`
2. 新增: `src/pages/RootCauseAnalysis.tsx`
3. 修改: `src/App.tsx` (添加路由)
4. 修改: `src/components/flow/ConfigPanel.tsx` (添加按钮)
5. 修改: `src/services/api.ts` (添加API调用)
