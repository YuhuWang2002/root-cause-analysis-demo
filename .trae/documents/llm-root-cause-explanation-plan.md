# 用大模型生成根因解释功能实现计划

## 目标
参照 `/Users/yuhuwang/Documents/trae_projects/root_cause_analysis/inventory_rca_demo/llm_explainer.py` 实现用大模型生成根因解释的功能。

## 实现步骤

### 1. 创建后端LLM解释器模块
- 文件位置: `backend/llm_explainer.py`
- 实现功能:
  - `LLMExplainer` 类
  - 初始化大模型客户端（支持OpenAI兼容API）
  - 测试连接功能
  - 生成根因解释方法 `generate_root_cause_explanation()`
  - 生成解决方案方法 `generate_solution()`
  - 构建提示词方法

### 2. 添加后端API端点
- 文件位置: `backend/routes/root_cause.py`
- 新增端点:
  - `POST /api/root-cause/llm/config` - 配置LLM（API密钥、模型、base URL）
  - `POST /api/root-cause/llm/test` - 测试LLM连接
  - `POST /api/root-cause/<project_id>/explain` - 生成根因解释
  - `POST /api/root-cause/<project_id>/solution` - 生成解决方案

### 3. 添加大模型配置存储
- 使用Flask session或数据库存储LLM配置
- 支持从配置文件读取默认配置

### 4. 更新前端API调用
- 文件位置: `src/services/api.ts`
- 新增API函数:
  - `configureLLM(config)` - 配置LLM
  - `testLLMConnection()` - 测试连接
  - `generateRootCauseExplanation(projectId, data)` - 生成根因解释
  - `generateSolution(projectId, data)` - 生成解决方案

### 5. 更新前端根因分析页面
- 文件位置: `src/pages/RootCauseAnalysis.tsx`
- 添加功能:
  - LLM配置区域（API密钥、模型选择）
  - "生成根因解释"按钮
  - "生成解决方案"按钮
  - 显示解释结果的区域

## 技术细节

### LLM配置
- 支持OpenAI兼容API（如SiliconFlow）
- 默认模型: Qwen/Qwen2.5-7B-Instruct
- 默认Base URL: https://api.siliconflow.cn/v1

### 提示词构建
参考原始实现，构建包含以下信息的提示词:
- 场景背景
- 本体信息
- 因果图结构
- 数据分析结果
- 具体问题

## 验收标准
1. 后端能够配置LLM并测试连接
2. 能够生成根因解释文本
3. 能够生成解决方案文本
4. 前端能够调用API并显示结果
