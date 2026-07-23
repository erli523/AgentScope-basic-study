# 03 Model

> 官方文档：[Model](https://docs.agentscope.io/versions/2.0.4/zh/building-blocks/model)

## 本章要回答的问题

前两章中，`Agent` 通过 `model=build_chat_model()` 使用模型，但模型层本身被 `_common.py` 隐藏了。本章把这一层拆开：

1. Credential、模型客户端和 Agent 分别负责什么？
2. 不经过 Agent，怎样直接调用 Model？
3. `stream=True` 时为什么返回 `ChatResponse` 流，而不是 Agent Event？
4. 模型参数、token usage、工具调用和结构化输出如何工作？
5. 如何切换供应商而不修改上层 Agent 代码？

## 核心调用链

```text
Credential
    └─ 保存访问模型服务所需的认证与 base_url
Model
    └─ 把 AgentScope Msg 转换为供应商请求，再转换为 ChatResponse
Agent
    └─ 组织 Context、Model、Toolkit 和 ReAct 循环，最终产生 Msg/Event
```

Model 的一次调用只负责“给定消息和工具 Schema，生成一次模型响应”。工具的真实执行、工具结果回填和多轮 ReAct 由 Agent 负责。

## 实践 Demo

目录：[`demos/`](./demos/)

| 序号 | 文件 | 是否调用 API | 学习内容 |
|---|---|---:|---|
| 01 | `01_create_and_inspect_model.py` | 否 | Credential、Model、Parameters 和安全配置 |
| 02 | `02_direct_model_call.py` | 是 | 不经过 Agent，直接调用 Model |
| 03 | `03_stream_chat_response.py` | 是 | Model 流与 Agent Event 流的区别 |
| 04 | `04_parameters_and_usage.py` | 是 | temperature、max_tokens、context_size 和 usage |
| 05 | `05_model_tool_call.py` | 是 | Model 只生成 ToolCallBlock，不执行工具 |
| 06 | `06_structured_output.py` | 是 | 使用 Pydantic 获取结构化结果 |
| 07 | `07_switch_providers.py` | 是 | 相同调用代码切换 DeepSeek/Qwen/OpenAI |

## 环境准备

本机 `Scope-School` 环境当前检测到 AgentScope 2.0.3；这些 Demo 按 2.0.3/2.0.4 公共接口编写。

```bash
conda activate Scope-School

# 根目录 .env 中选择供应商
AI_PROVIDER=deepseek

# 对应供应商至少配置一个 API Key
DEEPSEEK_API_KEY=...
# 或 QWEN_API_KEY / DASHSCOPE_API_KEY / OPENAI_API_KEY
```

推荐运行顺序：

```bash
cd 01-Guides/01-Building-Blocks/03-Model/demos

python 01_create_and_inspect_model.py
python 02_direct_model_call.py
python 03_stream_chat_response.py
python 04_parameters_and_usage.py --temperature 0.2 --max-tokens 120
python 05_model_tool_call.py
python 06_structured_output.py
python 07_switch_providers.py
```

只有在 `.env` 同时配置多个供应商密钥时，才运行跨供应商比较：

```bash
python 07_switch_providers.py --providers deepseek qwen
```

## 学习重点

- Credential 只负责认证配置，绝不能打印或提交真实 Key；
- `Model(messages)` 返回 `ChatResponse`，`Agent.reply_stream()` 返回 Agent Event；
- 流式 Model 的最后一个 `is_last=True` chunk 保存聚合后的完整内容；
- `context_size` 是模型窗口配置，不是当前请求实际消耗；
- `usage` 应用于成本和容量观测；
- 模型生成工具调用不等于工具已经执行；
- 结构化输出仍需 Pydantic/业务代码再次校验。

## 验收标准

- 能安全构建模型并说明 Credential/Model/Agent 的边界；
- 能直接处理非流式和流式 `ChatResponse`；
- 能读取 Text/Thinking/ToolCall 内容块和 token usage；
- 能通过环境变量切换模型而不修改 Agent 逻辑；
- 能识别模型不支持工具、结构化输出或某参数时的失败；
- 不会把 API Key、完整敏感请求或思考内容写入普通日志。

更完整的概念总结见：[笔记.md](./笔记.md)
