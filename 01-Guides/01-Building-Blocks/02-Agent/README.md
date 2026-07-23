# 02 Agent

> 官方文档：
> - [Agent Overview](https://docs.agentscope.io/versions/2.0.5dev/en/building-blocks/agent/overview.md)
> - [Configure Agent](https://docs.agentscope.io/versions/2.0.5dev/en/building-blocks/agent/configure-agent.md)
> - [Run Agent](https://docs.agentscope.io/versions/2.0.5dev/en/building-blocks/agent/run-agent.md)
> - 中文入口：[Building Blocks / Agent](https://docs.agentscope.io/versions/2.0.4/zh/building-blocks/agent)

当前 conda 环境 `Scope-School` 实测版本：`agentscope 2.0.3`（接口以本机安装为准；开发版文档可能更超前）。

## 学习信息（先读这段）

### Agent 是什么

AgentScope 2.0 里的 `Agent` 不是「包一层大模型 API」，而是一个**无状态的推理-行动（ReAct）循环引擎**。它把模型、工具、权限、上下文、中间件、状态和事件，收成统一接口。

一句话：

| 层次 | 问题 |
|------|------|
| LangGraph（业务编排） | 现在该轮到谁处理？ |
| **Agent（本课）** | 这个角色如何思考、调工具、产出消息/事件？ |
| Skill / Tool | 真正能执行什么动作？ |

### 构造时要准备什么

| 参数 | 作用 |
|------|------|
| `name` | 智能体标识，会出现在消息与日志里 |
| `system_prompt` | 角色与行为约束 |
| `model` | 聊天模型（DeepSeek / Qwen / OpenAI…） |
| `toolkit` | 工具 / MCP / Skill 集合 |
| `react_config` | 如 `max_iters`、`stop_on_reject` |
| `state` | 上下文、权限、会话状态（可持久化） |
| `context_config` / `middlewares` / `offloader` | 上下文压缩、钩子、卸载（后续章节） |

### 核心接口

| 方法 | 做什么 |
|------|--------|
| `reply(inputs)` | 跑完整循环，返回最终 `Msg` |
| `reply_stream(inputs)` | 同一循环，边跑边 yield `AgentEvent` |
| `observe(msgs)` | 只写入上下文，**不**触发推理 |
| `compress_context(...)` | 上下文过长时压缩（Context 章展开） |

`inputs` 可以是：单条/多条 `Msg`、人工确认/外部执行结果事件，或 `None`（从当前暂停处继续）。

### 主循环（简化）

```
输入 Msg / Event
  → 写入上下文
  → 决策：reasoning / acting / exit
       ├─ reasoning：必要时压缩上下文 → 调 LLM
       ├─ acting：权限检查 → 执行工具 → 结果回填
       └─ exit：得到最终回答，或暂停等人确认/外部执行
```

触达 `max_iters` 仍未结束时，会发出 `ExceedMaxItersEvent`（流式可直接观察到）。

### 与上一章的关系

- **Message**：Agent 一次完整回复的「结果对象」
- **Event**：Agent 运行过程中的「过程对象」
- 本课重点：谁在驱动循环、如何配置、如何停止、如何多轮复用

### 版本注意

开发版文档提到的 `structured_schema` / `finished_reason` 等，在 **2.0.3** 的 `reply()` 签名中可能尚未暴露。本目录 demo 按你当前环境可运行的 API 编写；结构化输出等能力留待升级版本后再补。

---

## 实践 Demo

目录：[`demos/`](./demos/)

| 序号 | 文件 | 学什么 |
|------|------|--------|
| 01 | `01_create_and_reply.py` | 最小 Agent + `reply` |
| 02 | `02_reply_vs_stream.py` | `reply` vs `reply_stream` |
| 03 | `03_react_with_tools.py` | 带工具的 ReAct 时间线 |
| 04 | `04_max_iters.py` | 超出最大迭代次数 |
| 05 | `05_observe_and_multiturn.py` | `observe` + 多轮上下文 |
| 06 | `06_tutor_agent.py` | 章节实践：学习助教 |

### 运行

```bash
conda activate Scope-School
cd 01-Guides/01-Building-Blocks/02-Agent/demos

python 01_create_and_reply.py
python 02_reply_vs_stream.py
python 03_react_with_tools.py
python 04_max_iters.py
python 05_observe_and_multiturn.py
python 06_tutor_agent.py
```

配置仍使用手册根目录 `.env`（默认 `AI_PROVIDER=deepseek`）。

---

## 职责边界

| 组件 | 负责 | 不负责 |
|------|------|--------|
| Agent | 单角色内的推理、工具、事件、本会话上下文 | 跨业务节点的固定状态机 |
| Message/Event | 数据与流式可观测 | 决定「下一步该哪个角色」 |
| LangGraph | 节点顺序、分支、重试、人工恢复 | 替代 Agent 运行时 |

## 验收标准

- 能从零创建并运行 Agent；
- 能解释一次工具调用型回答的步骤；
- 能处理超出迭代次数（观察 `ExceedMaxItersEvent`）；
- 能区分 Agent 职责与业务工作流职责。

## 建议笔记

学完后可在本章自建 `笔记.md`，至少写清：

1. `reply` / `reply_stream` / `observe` 三者差异；
2. `max_iters` 为什么必要；
3. 实习项目里「每次 bootstrap Agent」与本 demo「同一实例多轮 reply」的取舍。
