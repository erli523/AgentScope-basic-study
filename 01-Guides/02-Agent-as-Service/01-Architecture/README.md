# 01 Agent Service Architecture

## 学习内容

- Agent Service 的客户端、API、Agent、Session、存储和事件通道；
- 一次请求从接收到模型、工具、存储和 SSE 返回的链路；
- 单进程、分布式和多租户部署的差异；
- 状态持久化、恢复和可观测性。

## 学习重点

先建立组件边界和数据流，再学习部署命令。尤其要明确 Agent 定义、Agent 实例、Session 和一次 Run 不是同一个概念。

## 实践任务

画出请求时序图，并标明每一步的 ID、输入输出、失败方式和可重试性。

## 验收标准

- 能追踪一次请求的完整生命周期；
- 能说明哪些状态在内存、数据库或对象存储中；
- 能识别服务重启后的恢复点；
- 能列出至少三类需要监控的指标。

[官方文档](https://docs.agentscope.io/versions/2.0.4/zh/deploy/agent-service)

