# Checklist

## 后端通用数据查询引擎 (任务1)
- [ ] CSV 文件加载模块
- [ ] 自动字段类型推断（string/number/date）
- [ ] POST /api/data/csv/analyze API
- [ ] POST /api/data/query API
- [ ] 过滤条件支持 (eq/ne/gt/gte/lt/lte/like/in)
- [ ] 聚合支持 (sum/avg/min/max/count)
- [ ] 分组支持 (day/week/month)

## 看板配置后端API (任务2)
- [ ] Dashboard 数据模型
- [ ] POST /api/projects/{project_id}/dashboards
- [ ] GET /api/projects/{project_id}/dashboards
- [ ] GET /api/projects/{project_id}/dashboards/{dashboard_id}
- [ ] PUT /api/projects/{project_id}/dashboards/{dashboard_id}
- [ ] DELETE /api/projects/{project_id}/dashboards/{dashboard_id}

## 前端数据源配置 (任务3)
- [ ] DataAnalysisDashboard.tsx 页面
- [ ] CSV 路径配置输入
- [ ] 调用 analyze API
- [ ] 动态字段选择器
- [ ] 数据预览显示

## 前端查询构建器 (任务4)
- [ ] 字段选择组件
- [ ] 过滤条件构建器
- [ ] 聚合配置组件
- [ ] 分组配置组件
- [ ] 实时查询预览

## 前端看板编辑 (任务5)
- [ ] 看板布局系统
- [ ] 组件添加功能
- [ ] 组件配置面板
- [ ] 看板保存/加载

## 看板可视化组件 (任务6)
- [ ] 统计卡片 (card)
- [ ] 折线图 (line)
- [ ] 柱状图 (bar)
- [ ] 饼图 (pie)
- [ ] 数据表格 (table)

## 集成 (任务7)
- [ ] FlowCanvas 导航
- [ ] 路由配置
- [ ] 端到端测试
