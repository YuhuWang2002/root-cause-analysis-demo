# Tasks

## 任务 1: 后端通用数据查询引擎
- [ ] CSV 文件加载模块
- [ ] 自动字段类型推断（string/number/date）
- [ ] 实现 POST /api/data/csv/analyze - 分析CSV字段
- [ ] 实现 POST /api/data/query - 通用数据查询API
- [ ] 支持过滤条件 (eq/ne/gt/gte/lt/lte/like/in)
- [ ] 支持聚合 (sum/avg/min/max/count)
- [ ] 支持分组 (day/week/month)
- [ ] 测试不同CSV文件的适配性

## 任务 2: 看板配置后端API
- [ ] 创建 Dashboard 数据模型
- [ ] POST /api/projects/{project_id}/dashboards - 创建看板
- [ ] GET /api/projects/{project_id}/dashboards - 获取看板列表
- [ ] GET /api/projects/{project_id}/dashboards/{dashboard_id} - 获取看板详情
- [ ] PUT /api/projects/{project_id}/dashboards/{dashboard_id} - 更新看板
- [ ] DELETE /api/projects/{project_id}/dashboards/{dashboard_id} - 删除看板

## 任务 3: 前端通用数据源配置
- [ ] 创建 DataAnalysisDashboard.tsx 页面
- [ ] CSV 文件路径配置输入框
- [ ] 调用 analyze API 获取字段信息
- [ ] 动态渲染字段选择器
- [ ] 显示数据预览

## 任务 4: 前端查询构建器
- [ ] 字段选择组件
- [ ] 过滤条件构建器（添加/删除条件）
- [ ] 聚合配置组件
- [ ] 分组配置组件
- [ ] 实时查询预览

## 任务 5: 前端看板编辑功能
- [ ] 看板布局系统（拖拽网格）
- [ ] 添加组件按钮
- [ ] 组件配置面板（根据组件类型动态）
- [ ] 看板保存/加载功能

## 任务 6: 看板可视化组件
- [ ] 统计卡片组件 (card)
- [ ] 折线图组件 (line) - 使用 Recharts
- [ ] 柱状图组件 (bar)
- [ ] 饼图组件 (pie)
- [ ] 数据表格组件 (table)

## 任务 7: 与项目画布集成
- [ ] 修改 FlowCanvas 支持数据分析节点点击
- [ ] 配置路由 /dashboard/{project_id}
- [ ] 端到端测试
- [ ] 测试不同CSV文件的兼容性

# Task Dependencies
- 任务 2 与任务 1 可并行开发
- 任务 3 依赖任务 1 的 API
- 任务 4 依赖任务 3
- 任务 5 依赖任务 2、3
- 任务 6 依赖任务 5
- 任务 7 依赖任务 6
