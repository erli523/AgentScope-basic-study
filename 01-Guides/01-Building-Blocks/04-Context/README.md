# 04 Context

> 官方文档：[Context](https://docs.agentscope.io/versions/2.0.4/zh/building-blocks/context)

## 本章要回答的问题

前几章里，`Agent` 会把多轮消息放进 `state.context`。本章专门拆开「工作记忆」：

1. 一次模型调用实际看到哪三层内容？
2. 上下文增长后，如何自动/手动压缩？
3. 过大的工具结果如何截断？
4. 被移出窗口的内容如何 offload，之后怎么回查？
5. Context 与 Session、RAG、长期记忆有何边界？

## 核心结构

每次模型调用前，Agent 会拼出大致如下输入：

```text
Model API Input
├─ System Prompt   # 基础角色 + skill 指令 + on_system_prompt 中间件
├─ Summary         # 压缩后的历史摘要（若已发生压缩）
└─ Context         # 最近尚未压缩的 Msg（含 tool_call / tool_result）
```

AgentScope 用三种机制撑住长任务：

| 机制 | 做什么 |
|------|--------|
| 上下文压缩 | token 逼近阈值时，把较早消息汇总成 summary |
| 工具结果截断 | 过大工具输出先截断，再（可选）offload |
| Context offload | 把移出窗口的内容落到外部存储，便于回查 |

## 实践 Demo

目录：[`demos/`](./demos/)

| 序号 | 文件 | 是否需要 API | 学什么 |
|------|------|:------------:|--------|
| 01 | `01_inspect_context_layers.py` | 否 | 三层结构与 ContextConfig |
| 02 | `02_multiturn_context_growth.py` | 是 | 多轮下 context / token 增长 |
| 03 | `03_manual_compress_context.py` | 是 | `compress_context` 与 summary |
| 04 | `04_tool_result_truncation.py` | 是 | `tool_result_limit` 与 `<<<TRUNCATED>>>` |
| 05 | `05_offload_with_workspace.py` | 是 | `LocalWorkspace` offload 落盘 |
| 06 | `06_context_vs_others.py` | 否 | Context / Session / RAG / LTM 边界 |

### 环境准备

```bash
conda activate Scope-School
# 或使用手册根目录 .venv

# 根目录 .env
AI_PROVIDER=deepseek   # 也可 qwen / openai
```

推荐运行顺序：

```bash
cd 01-Guides/01-Building-Blocks/04-Context/demos

python 01_inspect_context_layers.py
python 02_multiturn_context_growth.py
python 03_manual_compress_context.py
python 04_tool_result_truncation.py
python 05_offload_with_workspace.py
python 06_context_vs_others.py
```

> **供应商提示：** 压缩内部会调用 `generate_structured_output`。  
> 若 DeepSeek thinking 模式拒绝 forced `tool_choice`，可改 `AI_PROVIDER=qwen` 或 `openai` 再跑 03/05。

Demo 运行时会把 workspace 写到 `demos/.workspace/`（已在 `.gitignore` 中忽略）。

## ContextConfig 常用字段

创建 Agent 时传入：

```python
from agentscope.agent import Agent, ContextConfig

agent = Agent(
    ...,
    context_config=ContextConfig(
        trigger_ratio=0.8,      # 超过 context_size 的该比例则压缩（上限 0.9）
        reserve_ratio=0.1,      # 压缩后保留的最近上下文比例
        tool_result_limit=3000, # 单条工具结果 token 上限
    ),
)
```

也可手动：

```python
await agent.compress_context()
await agent.compress_context(
    context_config=ContextConfig(trigger_ratio=0.5, reserve_ratio=0.1),
)
```

低于阈值时为空操作。

## 学习重点

- Context 是工作记忆，不是「越长越好」；
- System / Summary / Context 三层拼成单次模型输入；
- 压缩会尽量保持 tool_call / tool_result 成对；
- 截断会插入 `<<<TRUNCATED>>>`；挂了 offloader 时还能指向落盘路径；
- 无 offloader 时，移出窗口的内容会丢；
- Session 解决持久化与恢复，RAG 解决外部知识，长期记忆解决跨会话偏好——都不是 Context 的替代品。

## 职责边界

| 组件 | 负责 | 不负责 |
|------|------|--------|
| Context | 当前窗口内可见的消息与摘要 | 无限历史、跨会话偏好 |
| Session 存储 | 按 session_id 恢复 AgentState | 自动做知识检索 |
| RAG | 按查询注入外部文档片段 | 工具执行过程态 |
| Long-Term Memory | 受控的跨会话记忆 | 替代上下文压缩策略 |

## 验收标准

- 能说明一次模型调用看到的三层内容；
- 能配置 `ContextConfig` 并解释阈值；
- 能观察压缩前后 `summary` / `context` 变化；
- 能解释工具截断标记的含义；
- 能区分 Context、Session、RAG、长期记忆。

## 实践任务（可选加练）

1. 把 `03` 的 `trigger_ratio` 调高到几乎不触发，确认 `compress_context` 为空操作；
2. 给 `05` 的 Toolkit 加上内置 `Read` 工具，让 Agent 读回 `tool_result-*.txt`；
3. 对照实习项目：断线恢复靠 Session，长对话靠 Context 压缩，知识库靠 RAG——各画一行职责。
