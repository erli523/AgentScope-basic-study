# 01 Message 与 Event

> 官方文档：[Message & Event](https://docs.agentscope.io/versions/2.0.4/zh/building-blocks/message-and-event)

## 一句话区分

| 概念 | 是什么 | 典型用途 |
|------|--------|----------|
| **Message (`Msg`)** | 一次完整的用户输入或助手回复 | 写入上下文、持久化会话、渲染消息气泡 |
| **Event (`AgentEvent`)** | 一次 `reply_stream` 过程中的增量状态变化 | SSE 推送、终端打字效果、审计日志、人工介入 |
| **Content Block** | Message 内部的有序内容块 | 文本、思考、工具调用、工具结果、多媒体 |

**不要把所有 Event 都塞进下一轮模型上下文；也不要只保存最终文本而丢掉必要的工具执行记录。**

事件与消息是同一数据的两种视图：一串 Event 可通过 `msg.append_event(event)` 还原成完整 `Msg`。

## 学习内容

- 用户、助手、系统消息与各类 Content Block；
- Message 在上下文中的作用；
- `reply()` 与 `reply_stream()`；
- 模型调用、工具调用、文本增量及回复结束事件；
- 事件如何驱动终端输出、前端 UI、日志和人工介入。

## 实践 Demo

目录：[`demos/`](./demos/)

| 序号 | 文件 | 是否需要 API Key | 学什么 |
|------|------|------------------|--------|
| 01 | `01_create_messages.py` | 否 | 创建 User/Assistant/System 消息与内容块 |
| 02 | `02_access_message_content.py` | 否 | `get_text_content` / `get_content_blocks` |
| 03 | `03_stream_events.py` | 是 | `reply_stream` 观察事件类型与文本增量 |
| 04 | `04_rebuild_msg_from_events.py` | 是 | `append_event` 从事件流重建完整 Msg |
| 05 | `05_tool_events.py` | 是 | 工具调用 / 工具结果事件的先后顺序 |

### 环境准备

本手册示例默认使用 conda 环境 `Scope-School`，并从手册根目录读取 `.env`。

```bash
conda activate Scope-School

# 若尚未创建 .env：复制模板后填入密钥
# cp .env.example .env

# AI_PROVIDER=deepseek | qwen | openai | dashscope
# 当前默认 deepseek；切换 Qwen 时改 AI_PROVIDER=qwen 即可
```

需要的包（`Scope-School` 中通常已具备）：

```bash
pip install "agentscope>=2.0.3" python-dotenv
```

### 运行顺序（推荐）

```bash
conda activate Scope-School
cd 01-Guides/01-Building-Blocks/01-Message-Event/demos

python 01_create_messages.py          # 无需调用模型
python 02_access_message_content.py   # 无需调用模型
python 03_stream_events.py            # 读 .env，调用 LLM
python 04_rebuild_msg_from_events.py
python 05_tool_events.py
```

## 事件生命周期（简化）

```
ReplyStart
  └─ ModelCallStart
       ├─ TextBlockStart → TextBlockDelta(×N) → TextBlockEnd
       └─ ToolCallStart → ToolCallDelta(×N) → ToolCallEnd
  └─ ModelCallEnd
  └─ ToolResultStart → ToolResultTextDelta(×N) → ToolResultEnd
  └─ （可能再次 ModelCall...）
ReplyEnd
```

同一次 `reply_stream` 共享 `reply_id`；文本/思考用 `block_id` 关联，工具调用与结果用 `tool_call_id` 关联。

## 与实习项目的对应关系

校园安防项目中，LangGraph 侧通过 HTTP/SSE 订阅 AgentScope 事件，并用 `append_event` 重建助手消息（见 `workflow_graph.py` 的 `agent_reply`）。  
学完本目录后，应能读懂那条链路：

1. AgentScope 产出 Event；
2. 编排层转发 / 记录 Event；
3. 前端或日志层还原 Msg，展示文本与工具过程。

## 职责边界

| 组件 | 负责 | 不负责 |
|------|------|--------|
| Message | 会话数据的结构化表达与持久化 | 业务流程节点顺序 |
| Event | 运行时增量可观测与流式交互 | 替代完整业务状态机 |
| Context（下一章） | 哪些 Message 进入模型窗口 | 定义 Event 协议本身 |

## 验收标准

- 能解释 Message、Content Block 和 Event 的差异；
- 能正确拼接流式文本，而不是把每个 delta 当成新消息；
- 能记录工具开始、结束、失败和最终回答；
- 不会把中间事件重复展示或重复写入上下文。

## 实践任务（可选加练）

1. 修改 `05_tool_events.py`，让工具故意抛错，观察 `ToolResultEndEvent.state`；
2. 把 `03_stream_events.py` 的输出改成「只打印事件类型，不打印 delta」，再对比最终拼接文本；
3. 对照 `AgentScope-VS-LangGraph.md`，用自己的话写 5 行：为什么 SSE 事件对审计很重要。
