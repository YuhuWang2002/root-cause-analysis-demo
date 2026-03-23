# 前端调用后端API - 验收清单

## 验收检查点

### API服务层
- [x] api.ts文件创建成功，包含所有API函数
- [x] API基础URL正确配置（http://127.0.0.1:5000）
- [x] 所有fetch请求正确处理错误

### flowStore集成
- [x] 项目列表从API加载
- [x] 创建项目调用POST /api/projects
- [x] 删除项目调用DELETE /api/projects/<id>
- [x] 画布数据调用PUT /api/projects/<id>/canvas保存
- [x] 节点配置调用对应API保存

### CORS配置
- [x] 后端CORS配置添加成功
- [x] 前端可以跨域访问后端API

### 功能测试
- [x] 页面加载时项目列表从后端获取
- [x] 创建新项目后列表更新
- [x] 画布修改后保存成功
- [x] 节点配置修改后保存成功
- [x] 刷新页面数据从后端重新加载
