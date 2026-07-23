# 02 Agent Team

## 学习内容

- 多 Agent 角色、职责和通信；
- Manager–Workers、委派、交接和汇总；
- 团队共享上下文与私有上下文；
- 终止条件、失败处理和人工介入。

## 学习重点

多 Agent 的价值来自角色分工和能力隔离，不来自增加聊天轮数。每个角色都要有明确输入、输出、工具和完成条件。

## 实践任务

实现一个学习团队：Manager 分配任务给“资料检索 Agent”和“代码示例 Agent”，最后由 Manager 汇总并检查结果。

## 验收标准

- Manager 不亲自执行 Worker 的所有工作；
- Worker 只拥有职责所需工具；
- 团队不会无限对话；
- Worker 失败时具有清晰的重试、替代或上报策略。

[官方文档](https://docs.agentscope.io/versions/2.0.4/zh/deploy/agent-team)

