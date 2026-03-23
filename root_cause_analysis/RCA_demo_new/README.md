# 根因分析系统 (Root Cause Analysis System)

本项目是一个基于前后端分离架构的根因分析系统，用于分析和诊断系统异常的根本原因。

## 技术栈

### 前端

- React 18 + TypeScript
- Vite
- Tailwind CSS
- ReactFlow (流程图可视化)
- Framer Motion (动画效果)
- Zustand (状态管理)
- React Router (路由管理)

### 后端

- Flask
- SQLAlchemy (ORM)
- SQLite (数据库)
- DoWhy (因果分析)
- OpenAI API (LLM 集成)

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/YuhuWang2002/root-cause-analysis-demo.git
cd root-cause-analysis-demo
```

### 2. 前端安装

```bash
# 进入前端目录
cd RCA_demo_new

# 安装依赖
npm install
```

### 3. 后端安装

```bash
# 进入后端目录
cd backend

# 创建虚拟环境 (可选)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 运行步骤

### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 启动服务
python app.py
```

后端服务将运行在 `http://127.0.0.1:5000`

### 2. 启动前端开发服务器

```bash
# 进入前端目录
cd RCA_demo_new

# 启动开发服务器
npm run dev
```

前端开发服务器将运行在 `http://127.0.0.1:5173`

### 3. 访问系统

打开浏览器，访问 `http://127.0.0.1:5173` 即可进入系统。

## 项目结构

### 前端结构

- `src/`
  - `components/` - 组件目录
    - `common/` - 通用组件
    - `flow/` - 流程图相关组件
    - `layout/` - 布局组件
  - `pages/` - 页面目录
    - `AnalysisFlow.tsx` - 分析流程图页面
    - `RootCauseAnalysis.tsx` - 根因分析页面
    - `OntologyEditor.tsx` - 本体编辑器页面
    - `DataAnalysisDashboard.tsx` - 数据分析看板页面
  - `services/` - API 服务
  - `stores/` - 状态管理
  - `types/` - TypeScript 类型定义

### 后端结构

- `backend/`
  - `routes/` - API 路由
    - `root_cause.py` - 根因分析相关 API
    - `canvas.py` - 画布数据相关 API
    - `projects.py` - 项目相关 API
  - `app.py` - 应用主文件
  - `causal_analyzer.py` - 因果分析器
  - `llm_explainer.py` - LLM 解释器
  - `data_generator.py` - 数据生成器
  - `models.py` - 数据库模型

## 核心功能

1. **项目管理** - 创建、编辑、删除项目
2. **分析流程图** - 可视化构建分析流程，包括数据源、数据处理、本体构建、根因分析等节点
3. **本体库管理** - 创建和管理本体库，定义实体和关系
4. **根因分析** - 使用 DoWhy 进行因果分析，结合 LLM 生成根因解释和解决方案
5. **数据分析看板** - 可视化展示分析结果

## 注意事项

1. **数据库** - 系统使用 SQLite 数据库，默认存储在 `backend/rca.db`
2. **LLM 配置** - 需要在根因分析页面配置 OpenAI API 密钥才能使用 LLM 功能
3. **Playwright 浏览器** - 如需使用 Playwright 进行测试，请不要运行 `npx playwright install chromium`，系统需要特定版本的浏览器
4. **端口占用** - 确保 5000 端口（后端）和 5173 端口（前端）未被占用

## 开发命令

### 前端

- `npm run dev` - 启动开发服务器
- `npm run build` - 构建生产版本
- `npm run lint` - 运行代码检查

### 后端

- `python app.py` - 启动后端服务
- `python test_prompt_saving.py` - 测试提示词保存功能
- `python fix_canvas.py` - 修复画布数据

## 许可证

MIT License
