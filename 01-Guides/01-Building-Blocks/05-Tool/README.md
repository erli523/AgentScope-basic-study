# 05 Tool

> 主要依据：用户提供的 AgentScope 2.0.4 官方《工具》教程  
> 在线文档：[Tool](https://docs.agentscope.io/versions/2.0.4/zh/building-blocks/tool)

## 本章目标

理解工具如何把 Agent 与 Python 函数、文件系统、命令、API、MCP 和外部系统连接起来，并掌握工具定义、Schema、Toolkit 调度、权限、状态注入、中间件和 Tool Group。

配套材料：[个人学习记录](./学习.md) · [整理后的完整笔记](./笔记.md)

## 三个核心概念

| 概念 | 作用 |
|---|---|
| `ToolBase` | 单项能力的统一接口，定义名称、描述、输入 Schema、权限和执行逻辑 |
| `Toolkit` | 注册、暴露、查找和调用工具，同时管理 MCP、Skill 与工具组 |
| `ToolGroup` | 按场景激活/停用一组工具，减少无关 Schema 占用模型上下文 |

## Demo

目录：[`demos/`](./demos/)

| 序号 | 文件 | 是否需要模型 API | 学习内容 |
|---|---|---:|---|
| 01 | `01_builtin_tools_and_schemas.py` | 否 | 内置工具、Toolkit 和 JSON Schema |
| 02 | `02_custom_toolbase.py` | 否 | 继承 `ToolBase` 编写只读工具 |
| 03 | `03_function_tool.py` | 否 | 用 `FunctionTool` 包装普通函数 |
| 04 | `04_toolkit_call_and_errors.py` | 否 | 用 `ToolCallBlock` 调度工具及观察错误 |
| 05 | `05_read_before_write.py` | 否 | `Read/Write/Edit` 的先读后写规则 |
| 06 | `06_dynamic_permission.py` | 否 | 动态只读判断与 ALLOW/ASK/DENY |
| 07 | `07_tool_middleware.py` | 否 | 日志、参数加工、重试及洋葱顺序 |
| 08 | `08_agent_uses_tool.py` | 是 | Agent ReAct 中的工具事件与最终消息 |
| 09 | `09_tool_groups.py` | 否 | `reset_tools` 动态激活 Tool Group |

## 推荐运行顺序

```bash
conda activate Scope-School
cd 01-Guides/01-Building-Blocks/05-Tool/demos

python 01_builtin_tools_and_schemas.py
python 02_custom_toolbase.py
python 03_function_tool.py
python 04_toolkit_call_and_errors.py
python 05_read_before_write.py
python 06_dynamic_permission.py
python 07_tool_middleware.py
python 08_agent_uses_tool.py
python 09_tool_groups.py
```

只有 `08_agent_uses_tool.py` 会读取根目录 `.env` 并调用模型。

## 学习重点

- `description` 和 `input_schema` 是给模型看的能力契约；
- `check_permissions()` 是每个 `ToolBase` 子类必须实现的接口；
- 正常执行代码写在 `call()`，不要覆盖框架调度入口 `__call__()`；
- `ToolChunk` 表示增量结果，`ToolResponse` 表示 Toolkit 聚合后的最终结果；
- `is_read_only` 是静态声明，输入相关的只读性使用 `check_read_only()`；
- 直接调用 `tool.call()` 只适合单元测试，会绕过 Agent 的权限与事件链；
- Model 生成 `ToolCallBlock` 不代表工具已经执行；
- `FunctionTool` 默认权限行为是 ASK，需要自定义权限时应继承 `ToolBase`；
- 文件写入和命令执行必须结合 Permission 与 Workspace，而不能只靠 Prompt；
- MCP、Skill 和 Tool Group 都由 Toolkit 管理，但 Skill 本身不是可直接调用的工具。

## 本章不直接连接的外部能力

MCP Demo 需要一个真实 MCP 服务，Skill Demo 需要准备符合规范的 `SKILL.md` 目录。为了让本章基础 Demo 无额外依赖，这两部分先在 [笔记.md](./笔记.md) 中总结，之后可以分别加入独立实践。

## 验收标准

- 能从零实现并单独测试一个 `ToolBase`；
- 能解释 JSON Schema 如何影响模型生成的参数；
- 能通过 Toolkit 调用工具并处理 ToolResponse；
- 能区分工具生成调用、权限检查、真实执行和结果回填；
- 能处理参数错误、业务异常、拒绝和流式结果；
- 能说明内置文件工具为什么要求先读后写；
- 能通过中间件添加日志或重试而不修改工具逻辑；
- 能按任务激活工具组，避免把全部工具长期暴露给模型。
