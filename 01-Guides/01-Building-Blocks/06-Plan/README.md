# 06 Plan

## 学习内容

- 复杂任务拆解；
- 计划步骤、状态、更新和重规划；
- 计划如何参与 Agent 的执行循环；
- 计划失败、取消和完成条件。

## 学习重点

Plan 是 Agent 的可观察工作清单，不是强一致的业务状态机。涉及审批、资金、工单状态等规则时，应由确定性代码控制。

## 实践任务

让 Agent 把“阅读一个章节并生成笔记、示例和测试”拆成步骤，执行中实时更新状态，并模拟一步失败后的重规划。

## 验收标准

- 计划步骤具有明确完成条件；
- 能看到 pending、running、completed、failed 等状态；
- 失败后不会虚假标记完成；
- 能解释 Plan 与 LangGraph/工作流引擎的边界。

[开发版官方文档](https://docs.agentscope.io/latest/zh/building-blocks/plan)

