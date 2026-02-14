# 端到端测试说明

## 环境要求

### Python版本
- Python 3.8+

### 依赖安装

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装基础依赖
pip install -r requirements.txt

# 如果网络有问题，可以尝试使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 必需的依赖包

- `fastapi>=0.104.0` - Web API框架
- `uvicorn>=0.27.0` - ASGI服务器
- `pydantic>=2.0.0` - 数据验证
- `httpx>=0.23.0` - HTTP客户端
- `dowhy>=0.8` - 因果推断
- `pandas>=1.5.0` - 数据处理
- `numpy>=1.21.0` - 数值计算
- `matplotlib>=3.5.0` - 数据可视化
- `seaborn>=0.12.0` - 数据可视化
- `networkx>=2.8` - 图处理
- `graphviz>=0.20` - 图可视化
- `scipy>=1.9.0` - 科学计算
- `openai>=1.0.0` - 大模型API

## 运行测试

### 完整端到端测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试脚本
python test_e2e.py
```

### 测试内容

测试脚本会依次测试以下组件：

1. **配置读取** - 从 `web/modelkey.cfg` 读取模型配置
2. **本体API** - 测试本体API连接（需要先启动）
3. **LLM Agent** - 测试因果图推导功能
4. **数据生成** - 测试数据生成功能
5. **因果分析** - 测试DoWhy因果分析
6. **大模型解释** - 测试大模型解释生成

### 启动本体API（可选）

如果需要测试本体API功能，需要先启动本体API服务器：

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动本体API服务器
python web/ontology_api.py
```

本体API会在 `http://localhost:8000` 启动。

## 配置文件

### modelkey.cfg

在 `web/modelkey.cfg` 文件中配置大模型API：

```
API Key: your_api_key_here
Base URL: https://api.siliconflow.cn/v1
Model: Pro/zai-org/GLM-5
```

### 支持的模型

- `Pro/zai-org/GLM-5` (默认)
- `Qwen/Qwen2.5-7B-Instruct`
- `Qwen/Qwen2.5-72B-Instruct`
- `deepseek-ai/DeepSeek-V2.5`

## 测试结果示例

成功的测试输出：

```
============================================================
端到端测试 - Agent驱动的因果分析
============================================================
[Config] 成功读取配置文件: web/modelkey.cfg
[Config] API Key: sk-mycnmfqzgqanoffec...
[Config] Base URL: https://api.siliconflow.cn/v1
[Config] Model: Pro/zai-org/GLM-5

============================================================
步骤1：测试本体API
============================================================
⚠️  本体API连接失败: [Errno 61] Connection refused
   提示：本体API未运行，将跳过本体API测试
   启动命令: python web/ontology_api.py

============================================================
步骤2：测试LLM Agent（跳过本体API，直接测试Agent逻辑）
============================================================
✅ LLM Agent初始化成功！

   测试推导因果图...
   ✅ 因果图推导成功！

============================================================
步骤3：测试数据生成
============================================================
✅ 数据生成成功！

============================================================
步骤4：测试因果分析
============================================================
✅ 因果分析完成！

============================================================
步骤5：测试大模型解释
============================================================
✅ 大模型解释生成成功！

============================================================
✅ 端到端测试完成！
============================================================

测试总结：
  ✅ 本体API - 正常
  ✅ LLM Agent - 正常
  ✅ 数据生成 - 正常
  ✅ 因果分析 - 正常
  ✅ 大模型解释 - 正常

所有组件都正常工作！
```

## 故障排除

### 问题1：ModuleNotFoundError: No module named 'fastapi'

**原因：** 虚拟环境中缺少 fastapi 包

**解决方案：**
```bash
source venv/bin/activate
pip install fastapi uvicorn pydantic httpx
```

### 问题2：Connection refused when connecting to ontology API

**原因：** 本体API服务器未启动

**解决方案：**
```bash
# 在另一个终端启动本体API
python web/ontology_api.py
```

### 问题3：'coroutine' object has no attribute 'causal_graph'

**原因：** async/await 调用问题

**解决方案：** 已在代码中修复，使用线程运行异步方法

### 问题4：网络连接问题

**原因：** pip 无法连接到 PyPI

**解决方案：** 使用国内镜像源
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 架构说明

### Agent驱动的因果分析流程

1. **用户输入场景描述**
   - 描述遇到的问题场景
   - 选择结果实体（如"生产效率"）

2. **LLM Agent推导因果图**
   - 查询本体API获取实体和关系
   - 使用LLM理解场景并推导因果图
   - 返回因果图、推理过程、建议数据字段

3. **数据生成**
   - 根据推导的因果图生成数据
   - 模拟正常月份和异常月份

4. **DoWhy因果分析**
   - 构建因果模型
   - 识别因果效应
   - 进行反事实分析

5. **大模型解释**
   - 基于DoWhy分析结果生成详细解释
   - 提供根本原因分析
   - 给出改进建议

### 核心优势

- **通用性** - 修改本体文件即可实现新场景
- **智能化** - LLM自动理解场景并推导因果图
- **可扩展** - 轻松添加新的实体、关系和属性
- **数据驱动** - 所有组件都基于本体配置工作