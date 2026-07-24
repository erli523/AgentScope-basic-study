# 06 Plan（计划模式）

> 主要依据：用户提供的 AgentScope 2.0.4 官方《计划模式》教程  
> 在线文档：[Plan](https://docs.agentscope.io/versions/2.0.4/zh/building-blocks/plan)

## 本章目标

掌握 AgentScope 如何通过四个内置任务工具维护显式、结构化、可追踪的任务清单，并理解 Plan 与 Agent 推理、Tool、AgentState 及确定性工作流之间的边界。

## 四个内置计划工具

| 工具 | 作用 | 只读 |
|---|---|---:|
| `TaskCreate` | 在任务清单末尾创建任务 | 否 |
| `TaskGet` | 获取单个任务的完整信息 | 是 |
| `TaskList` | 获取任务清单摘要 | 是 |
| `TaskUpdate` | 更新字段、状态、依赖或删除任务 | 否 |

四个工具都是状态注入式工具：Toolkit 调用时自动传入 `_agent_state`，数据保存在 `agent.state.tasks_context`。

> 版本提示：官方 2.0.4 文档把 `TaskGet/TaskList` 标为只读；本机 AgentScope 2.0.3 实测两者的 `is_read_only` 仍为 `False`，但 `check_permissions()` 依然返回 ALLOW。Demo 会打印当前环境的真实属性。

## Demo

目录：[`demos/`](./demos/)

| 序号 | 文件 | 是否需要模型 API | 学习内容 |
|---|---|---:|---|
| 01 | `01_task_tools_and_schemas.py` | 否 | 四个工具的 Schema、权限和状态注入 |
| 02 | `02_task_lifecycle.py` | 否 | 创建、查看、开始和完成任务 |
| 03 | `03_dependencies_and_delete.py` | 否 | 双向依赖边及删除清理 |
| 04 | `04_seed_and_auto_id.py` | 否 | 预置计划与自动 ID 分配 |
| 05 | `05_state_serialization.py` | 否 | AgentState 序列化与计划恢复 |
| 06 | `06_agent_scope_and_migration.py` | 否 | 计划以 Agent 为作用域及状态迁移 |
| 07 | `07_advisory_dependency.py` | 否 | 依赖仅是建议，不是执行锁 |
| 08 | `08_planning_agent.py` | 是 | Agent 通过工具自主创建计划 |

## 推荐运行顺序

```bash
conda activate Scope-School
cd 01-Guides/01-Building-Blocks/06-Plan/demos

python 01_task_tools_and_schemas.py
python 02_task_lifecycle.py
python 03_dependencies_and_delete.py
python 04_seed_and_auto_id.py
python 05_state_serialization.py
python 06_agent_scope_and_migration.py
python 07_advisory_dependency.py
python 08_planning_agent.py
```

只有 `08_planning_agent.py` 会读取根目录 `.env` 并调用模型。

## 正确的任务状态

```text
pending → in_progress → completed
```

- Task 对象中存储字段名为 `state`；
- `TaskUpdate` 接收的更新参数名为 `status`；
- 没有内置 `failed` 状态，失败原因可放进 `metadata`，并将任务保持 pending 或重新规划；
- `deleted` 是 `TaskUpdate` 的删除操作，不会作为 Task.state 保存。

## 学习重点

- Plan 是任务清单，不是自由形式思考文本；
- 每个离散步骤单独创建 Task，subject 应简短且使用命令式表达；
- 任务 ID 是稳定、单调递增的数字字符串；
- `blocks` 与 `blocked_by` 是对称边，优先通过 `TaskUpdate` 修改；
- 完成依赖任务不会删除依赖边，但它不再属于“未解决阻塞”；
- 删除任务会从其他任务的依赖边中移除该 ID；
- 依赖不会强制阻止模型执行被阻塞任务；
- Plan 随 AgentState 持久化，并默认以单个 Agent 为作用域；
- 多 Agent 共享计划、外部工单同步和业务状态机需要应用层自行设计。

## 与确定性工作流的边界

AgentScope Plan 适合记录「要做哪些步骤、做到哪了、谁阻塞谁」。  
但强业务规则（必须审批、状态只能按固定流转、超时阈值等）仍应由工作流引擎、数据库事务或业务服务强制执行——Plan 是可观察清单，不是硬锁状态机。

## 验收标准

- 能通过四个任务工具完成任务生命周期；
- 能解释 `state` 与 `status`、`deleted` 与持久状态的差异；
- 能创建并验证双向依赖；
- 能预置、序列化、恢复和清空计划；
- 能证明两个 AgentState 默认不共享任务；
- 能解释为什么 blocked_by 不能替代工作流执行锁；
- 能让 Agent 使用任务工具规划复杂请求，并从 state 中读取最终计划。

完整概念总结见：[笔记.md](./笔记.md)
