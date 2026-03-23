# 前端调用后端API规范

## 背景
当前前端使用本地Zustand状态管理存储项目数据，需要修改为调用后端API实现数据持久化。

## 目标
修改前端代码，使项目列表、画布数据、节点配置从后端API获取和保存。

## 变更内容
- 新增API服务层，统一管理后端请求
- 修改flowStore，从API获取项目数据
- 修改项目列表页面，从API获取项目列表
- 实现保存功能时调用后端API

## 影响范围
- 受影响的功能：项目管理、画布编辑、节点配置
- 受影响的代码：
  - `src/stores/flowStore.ts`
  - 新增 `src/services/api.ts`
  - `src/pages/ProjectList.tsx` 或类似项目列表页面

## API对接需求
### 1. 项目列表API
- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建新项目
- `DELETE /api/projects/<id>` - 删除项目

### 2. 画布数据API
- `GET /api/projects/<id>/canvas` - 获取画布节点和连接
- `PUT /api/projects/<id>/canvas` - 保存画布节点和连接

### 3. 节点配置API
- `GET /api/projects/<id>/nodes/<node_id>/config` - 获取节点配置
- `PUT /api/projects/<id>/nodes/<node_id>/config` - 保存节点配置
- `PUT /api/projects/<id>/nodes/configs` - 批量保存节点配置

## 前端实现任务

### Task 1: 创建API服务层
创建 `src/services/api.ts`，封装fetch请求：
- `getProjects()` - 获取项目列表
- `createProject(data)` - 创建项目
- `deleteProject(id)` - 删除项目
- `getCanvas(projectId)` - 获取画布数据
- `saveCanvas(projectId, data)` - 保存画布数据
- `saveNodeConfig(projectId, nodeId, config)` - 保存节点配置
- `saveAllNodeConfigs(projectId, configs)` - 批量保存节点配置

### Task 2: 修改flowStore
修改 `src/stores/flowStore.ts`：
- 初始化时从API加载项目数据
- 保存画布时调用API
- 保存节点配置时调用API
- 创建/删除项目时调用API

### Task 3: 处理CORS
后端需要配置CORS支持前端跨域请求

## 验收标准
1. 前端项目列表页面从后端API获取数据
2. 创建新项目时数据保存到后端
3. 画布数据保存到后端
4. 节点配置保存到后端
5. 刷新页面后数据从后端重新加载
