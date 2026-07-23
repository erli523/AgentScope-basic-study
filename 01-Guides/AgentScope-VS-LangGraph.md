# AgentScope VS LangGraph

> 本项目采用「LangGraph + AgentScope」，核心原因不是两个框架叠加后模型更聪明，而是把两类性质完全不同的问题拆开。

| 框架 | 负责什么 |
|------|----------|
| **LangGraph** | 管理「事情应该按照什么顺序发生」——业务流程骨架 |
| **AgentScope** | 管理「每个智能体如何思考、调用什么技能、怎样保存会话并输出事件」——智能体运行平台 |

一句话：**LangGraph 定流程，AgentScope 跑智能体。**

---

## 1. 在这个项目中，两者分别做什么

以设备故障链路为例，LangGraph 定义固定执行顺序：

```
输入校验
  ↓
发现与派单 Agent
  ↓
督办升级 Agent
  ↓
结果复检 Agent
  ↓
结束
```

对应节点（`workflow.py`）：

- `validate_fault_chain_input`
- `discovery_dispatch`
- `supervision_escalation`
- `result_reinspection`

这部分属于**确定性业务规则**：谁先谁后、数据怎么传、在哪里结束，都不该让大模型临时决定。

进入某个 Agent 节点后，需要完成的是：

- 选择并调用 Skill
- 按 system prompt 理解业务语义
- 执行 ReAct 推理
- 调用脚本、数据库等工具
- 保存 Agent、Session 和消息
- 通过 SSE 输出模型 / 工具 / 最终回答事件

这些能力由 **AgentScope** 提供。

三个主要角色（`agent_profiles.py`）：

| Agent Profile | 主要职责 |
|---------------|----------|
| `discovery-dispatch-agent` | 判断人工确认还是直接派单 |
| `supervision-escalation-agent` | 查询超时事件并决定是否督办 |
| `result-reinspection-agent` | 根据复检结果更新处置状态或提交人工确认 |

架构边界：

| 层次 | 回答的问题 |
|------|------------|
| LangGraph | 现在该轮到谁处理？ |
| AgentScope | 这个角色具体如何完成处理？ |
| Skill | 真正执行数据库或业务操作的能力是什么？ |

---

## 2. AgentScope 最大的好处是什么

总体上，价值体现在**智能体工程化**，而不是单纯封装一次大模型 API 调用。

### 2.1 统一管理不同角色

不用 AgentScope 时，通常要自己维护：system prompt、允许的工具、Skill 目录、模型配置、ReAct 循环、Agent/Session 关系、消息历史、流式事件、工具权限。

当前项目把角色配置集中到 `AGENT_PROFILES`，每个 Profile 包含：

- `profile_id`
- `name`
- `system_prompt`
- `skill_paths`

LangGraph 只传一个 `profile_id`，不必知道 Prompt 和 Skill 细节。职责更清晰：

| 改什么 | 改哪里 |
|--------|--------|
| 业务流程 | LangGraph |
| 角色行为 | AgentScope Profile |
| 执行能力 | Skill |
| 模型 / 存储 | AgentScope 服务配置 |

### 2.2 Skill 与 Agent 明确绑定

AgentScope 通过 Workspace 为不同 Agent 注入不同 Skill，例如：

- 派单 Agent：`submit-human-confirmation`、`submit-work-order`
- 复检 Agent：`update-dispatch-after-reinspection`、`submit-reinspection-human-confirmation`

好处：减少选错工具、缩小权限范围、缩短 Prompt、职责更清晰、新增角色不必改所有调用代码。绑定发生在 `bridge_app.py`。

### 2.3 完整的 Agent 运行时

直接调模型 API 还要自己实现：模型调用 → 解析 tool call → 执行工具 → 回填 → 再推理 → 判断结束 → 防无限循环。

AgentScope 已提供 ReAct 执行机制，并设置最大迭代次数（`bridge_app.py`），把「单次模型调用」提升成「可运行的智能体」。

### 2.4 Session、消息和状态持久化

使用 RedisStorage 保存 Agent、Session、Credential、对话消息、运行状态。没有这一层，LangGraph / 业务代码要自己设计会话表、消息表和恢复逻辑。

> 注意：当前虽具备 Session 基础设施，但每次工作流运行仍会重新 bootstrap Agent 和 Session，「跨请求长期记忆」的收益尚未完全发挥。

### 2.5 标准化流式事件

通过 SSE 输出结构化事件（模型起止、工具调用、文本增量、回复结束、超迭代等）。LangGraph 侧在 `agentscope_http_client.py` 订阅。

前端和编排层因此能知道：Agent 是否还在跑、调了什么工具、是否成功、跑了几轮、回答是否完整——对需要审计追踪的校园安防系统更可靠。

### 2.6 能力可独立部署与扩缩容

```
LangGraph Orchestrator :8094
            ↓ HTTP + SSE
AgentScope Bridge       :8000
```

| 压力 / 变更 | 主要扩容或发布谁 |
|-------------|------------------|
| 工作流请求多 | LangGraph |
| 模型与工具调用压力大 | AgentScope |
| 更新 Skill | AgentScope |
| 调整流程节点 | LangGraph |

也可绕过完整工作流，直接用 `agent_smoke_test.py` 单测某个 Agent。

---

## 3. 为什么不只用 LangGraph

只用 LangGraph 也能做，但节点内部要自己完成：Agent 创建、prompt 管理、Skill 加载、ReAct、Session、Redis 持久化、SSE、Workspace 隔离、工具权限。

LangGraph 能编排节点，**不会自动替你建设完整的 Agent 服务平台**。角色和 Skill 一多，节点里就会混入大量智能体运行细节。

---

## 4. 为什么不只用 AgentScope

只用 AgentScope 也能让多 Agent 互调，但校园安防流程有强业务约束：

- 发现后才能派单
- 超时才能督办
- 处置后才能复检
- 低置信度必须人工确认
- 每步留痕；失败要明确停止或重试

这些规则不适合全部交给大模型自由规划。AgentScope 解决「Agent 如何完成任务」；跨 Agent 的固定业务状态机，**LangGraph 更清楚、稳定、易测**。

---

## 5. 组合使用的真正收益

1. **确定性与智能性分离** — 流程顺序由代码控制，语义判断与工具选择由 Agent 完成  
2. **流程与能力解耦** — LangGraph 只依赖 `profile_id`，不直接绑 Prompt / Skill 文件  
3. **可观测、可审计** — LangGraph 记节点状态，AgentScope 记模型、消息和工具事件  
4. **支持持续扩展** — 后续加消防、门禁、巡检等 Agent 时可复用同一套运行时  

因此 AgentScope 的价值不是「帮忙画工作流」，而是把 Prompt、Skill、工具调用、ReAct、Session、存储、事件流和权限，整合成统一的 Agent 运行环境。

---

## 6. 当前项目是否必须同时用两个框架

**判断：目标架构合理；以当前代码规模看，有一部分设计偏重。**

不少 LangGraph 图仍是简单线性流程（例如结果复检：`device_check_review → device_check_agent`）。若永远只有「一次校验 + 调用一个 Agent」，普通 Python 函数或任务队列就够，LangGraph 价值有限。

LangGraph 真正有优势的场景：

- 条件分支、自动重试
- 人工确认后恢复、节点失败补偿
- 并行检测、循环复检
- 工作流断点恢复
- 多 Agent 按状态动态路由

当前设备故障链路已有多阶段结构，但仍是固定直线，条件边、暂停恢复等能力尚未充分使用。

拆成两个 HTTP 服务也增加了：部署排障、HTTP/SSE 超时、两套 Redis 命名空间、Agent 与工作流 ID 关联、服务间故障处理、每次运行重新创建 Agent/Session 的成本。文档也承认每次运行都重新 bootstrap，旧 Profile 绑定只在 Bridge 内存中保存——这些是后续优化点。

---

## 7. 最终结论

若项目要成为真正的校园安防智能体平台（多业务链路、多角色、人工介入、失败恢复、完整审计），「LangGraph + AgentScope」有意义：

| 组件 | 保证什么 |
|------|----------|
| LangGraph | 业务不乱 |
| AgentScope | Agent 易建设、易治理 |
| Skill | 真实业务动作可复用 |

若只是小型演示、始终只有两三个线性节点，这套架构偏重，直接在 LangGraph 节点里调模型和工具会更简单。

**最准确的评价不是「必须用两个框架」，而是：**

> 它是在为后续复杂工作流和多智能体扩展提前建设分层架构；当前已体现角色、Skill、Session、事件流和流程日志方面的收益，但 LangGraph 的分支、恢复、循环等核心价值还没有完全发挥出来。
