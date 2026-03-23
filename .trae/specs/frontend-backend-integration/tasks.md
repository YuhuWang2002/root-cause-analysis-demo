# 前端调用后端API - 任务列表

## 任务清单

### Task 1: 创建API服务层
- [ ] 创建 `src/services/api.ts`
  - [ ] 定义API基础URL常量
  - [ ] 实现getProjects()函数
  - [ ] 实现createProject(data)函数
  - [ ] 实现deleteProject(id)函数
  - [ ] 实现getCanvas(projectId)函数
  - [ ] 实现saveCanvas(projectId, data)函数
  - [ ] 实现saveNodeConfig(projectId, nodeId, config)函数
  - [ ] 实现saveAllNodeConfigs(projectId, configs)函数

### Task 2: 修改flowStore集成API
- [ ] 修改 `src/stores/flowStore.ts`
  - [ ] 导入API服务
  - [ ] 修改loadProject函数，从API获取数据
  - [ ] 修改saveCanvas相关逻辑，调用API保存
  - [ ] 修改项目创建/删除逻辑

### Task 3: 后端CORS配置
- [ ] 在后端app.py添加CORS支持

### Task 4: 测试验证
- [ ] 测试项目列表加载
- [ ] 测试创建项目
- [ ] 测试画布数据保存
- [ ] 测试节点配置保存

## 依赖关系
- Task 1 -> Task 2（API服务完成后才能集成到store）
- Task 3可与Task 1并行
- Task 4依赖于Task 1、2、3完成
