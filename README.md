# AgentScope-basic-study

基于 [AgentScope](https://github.com/agentscope-ai/agentscope) **2.0** 的入门学习手册与可运行 Demo。

面向初学者，从单 Agent 基础组件一路走到 Agent 服务化、多 Agent 团队、RAG 与隔离 Workspace。每章尽量包含：概念说明、职责边界、可运行示例与验收标准。

## 使用版本

| 项目 | 建议 |
|------|------|
| AgentScope | `agentscope==2.0.4.post1` |
| Python | 3.11+ |
| 文档 | 优先阅读 [2.0.4 中文文档](https://docs.agentscope.io/versions/2.0.4/zh/intro.html) |

> 官方 `latest` 文档可能指向开发版，接口会变。入门阶段请固定在 2.0.4。

## 仓库结构

```text
.
├── README.md
├── .env.example          # 环境变量模板（勿提交真实密钥）
├── requirements.txt
└── 01-Guides/
    ├── 00-Learning-Roadmap.md
    ├── 00-Resources.md
    ├── AgentScope-VS-LangGraph.md
    ├── README.md                     # 章节导航
    ├── 01-Building-Blocks/           # 第一阶段：基础组件
    │   ├── 01-Message-Event/         # ✅ 含 demos + 笔记
    │   ├── 02-Agent/                 # ✅ 含 demos + 笔记
    │   ├── 03-Model/                 # ✅ 含 demos + 笔记
    │   ├── 04-Context/               # ✅ 含 demos
    │   ├── 05-Tool/                  # ✅ 含 demos + 笔记
    │   ├── 06-Plan/                  # ✅ 含 demos + 笔记
    │   ├── 07-Permission-System/     # ✅ 含 demos + 笔记
    │   └── 08-Middleware/ … 11-Workspace/
    └── 02-Agent-as-Service/          # 第二阶段：服务化
```

当前已落地可运行 Demo 的章节：

| 章节 | Demo 目录 | 说明 |
|------|-----------|------|
| [Message 与 Event](01-Guides/01-Building-Blocks/01-Message-Event/README.md) | `demos/` | Msg / Event / Content Block、流式事件、工具事件 |
| [Agent](01-Guides/01-Building-Blocks/02-Agent/README.md) | `demos/` | 创建 Agent、`reply` / `reply_stream`、工具循环、多轮 |
| [Model](01-Guides/01-Building-Blocks/03-Model/README.md) | `demos/` | Credential / 直调 Model、流式 ChatResponse、参数与 usage、结构化输出、切换供应商 |
| [Context](01-Guides/01-Building-Blocks/04-Context/README.md) | `demos/` | 三层上下文、压缩、工具截断、LocalWorkspace offload、与 Session/RAG/LTM 边界 |
| [Tool](01-Guides/01-Building-Blocks/05-Tool/README.md) | `demos/` | ToolBase / Toolkit / ToolGroup、权限、中间件、内置工具与 Agent 调用 |
| [Plan](01-Guides/01-Building-Blocks/06-Plan/README.md) | `demos/` | TaskCreate/Get/List/Update、依赖、预置与序列化、规划 Agent |
| [Permission](01-Guides/01-Building-Blocks/07-Permission-System/README.md) | `demos/` | Mode / Rules / Built-in Checks、确认事件与无人值守策略 |

完整章节列表见 [章节导航](01-Guides/README.md)。

## 快速开始

### 1. 克隆与环境

```bash
git clone https://github.com/erli523/AgentScope-basic-study.git
cd AgentScope-basic-study

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env`，至少填写一种模型提供商的密钥。支持通过 `AI_PROVIDER` 切换：

| 变量 | 含义 |
|------|------|
| `AI_PROVIDER` | `deepseek`（默认）/ `qwen` / `openai` / `dashscope` |
| `DEEPSEEK_*` / `QWEN_*` / `OPENAI_*` | 对应提供商的密钥、Base URL 与模型名 |
| `AI_API_TIMEOUT` | 模型请求超时（秒），默认示例为 `60` |

**切勿把 `.env` 或真实 API Key 提交到 Git。**

### 3. 运行 Demo

**Message / Event（推荐先学）：**

```bash
cd 01-Guides/01-Building-Blocks/01-Message-Event/demos

python 01_create_messages.py          # 无需 API
python 02_access_message_content.py   # 无需 API
python 03_stream_events.py            # 需要 API
python 04_rebuild_msg_from_events.py
python 05_tool_events.py
```

**Agent：**

```bash
cd 01-Guides/01-Building-Blocks/02-Agent/demos

python 01_create_and_reply.py
python 02_reply_vs_stream.py
python 03_react_with_tools.py
python 04_max_iters.py
python 05_observe_and_multiturn.py
python 06_tutor_agent.py
```

**Model：**

```bash
cd 01-Guides/01-Building-Blocks/03-Model/demos

python 01_create_and_inspect_model.py  # 无需 API
python 02_direct_model_call.py
python 03_stream_chat_response.py
python 04_parameters_and_usage.py
python 05_model_tool_call.py
python 06_structured_output.py
python 07_switch_providers.py
```

**Context：**

```bash
cd 01-Guides/01-Building-Blocks/04-Context/demos

python 01_inspect_context_layers.py    # 无需 API
python 02_multiturn_context_growth.py
python 03_manual_compress_context.py
python 04_tool_result_truncation.py
python 05_offload_with_workspace.py
python 06_context_vs_others.py         # 无需 API
```

**Tool：**

```bash
cd 01-Guides/01-Building-Blocks/05-Tool/demos

python 01_builtin_tools_and_schemas.py
python 02_custom_toolbase.py
python 03_function_tool.py
python 04_toolkit_call_and_errors.py
python 05_read_before_write.py
python 06_dynamic_permission.py
python 07_tool_middleware.py
python 08_agent_uses_tool.py           # 需要 API
python 09_tool_groups.py
```

**Plan：**

```bash
cd 01-Guides/01-Building-Blocks/06-Plan/demos

python 01_task_tools_and_schemas.py
python 02_task_lifecycle.py
python 03_dependencies_and_delete.py
python 04_seed_and_auto_id.py
python 05_state_serialization.py
python 06_agent_scope_and_migration.py
python 07_advisory_dependency.py
python 08_planning_agent.py            # 需要 API
```

**Permission：**

```bash
cd 01-Guides/01-Building-Blocks/07-Permission-System/demos

python 01_permission_modes.py
python 02_rule_priority.py
python 03_bash_readonly_and_safety.py
python 04_file_permissions.py
python 05_suggested_rules.py
python 06_custom_permission_tool.py
python 07_dont_ask_vs_bypass.py
python 08_agent_confirmation_event.py  # 需要 API
```

Demo 会从手册**根目录**的 `.env` 加载配置（见各章 `demos/_common.py`）。

## 学习路线

1. [学习路线](01-Guides/00-Learning-Roadmap.md) — 阶段目标与验收问题  
2. [公开学习资料](01-Guides/00-Resources.md)  
3. [章节导航](01-Guides/README.md)  
4. [AgentScope 与 LangGraph 的职责边界](01-Guides/AgentScope-VS-LangGraph.md)

建议顺序：先打通 **Message/Event → Agent → Model → Context → Tool**，再进入权限、中间件、RAG 与服务化。

## 学习目标

完成本手册后，应能独立构建具备以下能力的小型 Agent 系统：

- 流式输出模型、文本与工具事件  
- 多轮上下文管理  
- 自定义工具与错误处理  
- 权限审批、中间件与审计日志  
- RAG 与长期记忆  
- 在隔离 Workspace 中执行工具  
- 多 Agent 团队协作  
- 通过 REST / SSE 对外提供服务  

## 每章建议产出

1. `README.md` 中的概念总结  
2. 一个可独立运行的最小示例  
3. 一个失败 / 边界条件测试  
4. 一段「本组件与相邻组件的职责边界」说明  

## 相关链接

- [AgentScope 官方仓库](https://github.com/agentscope-ai/agentscope)  
- [AgentScope 2.0.4 文档](https://docs.agentscope.io/versions/2.0.4/zh/intro.html)  

## License

本仓库为个人学习笔记与示例代码，仅供学习交流。AgentScope 本身遵循其上游开源协议。
