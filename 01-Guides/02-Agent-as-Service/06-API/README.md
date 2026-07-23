# 06 API

## 学习内容

- Agent、Session、Run 等 REST API；
- SSE 事件协议和客户端消费；
- 鉴权、错误码、超时和重试；
- API 版本与请求幂等性。

## 学习重点

客户端重试不能导致工具重复执行。需要为会话、请求和运行分配稳定 ID，并区分网络失败、业务失败和 Agent 执行失败。

## 实践任务

编写一个 Python 客户端：创建或恢复 Session，发送消息，消费 SSE，显示工具事件，并在连接中断后安全恢复。

## 验收标准

- 能从外部进程调用 Agent；
- SSE 增量不会丢失或重复拼接；
- 重试写请求不会重复产生副作用；
- 未认证用户不能访问 Agent、Session 或 Workspace 数据。

[开发版 API 文档入口](https://docs.agentscope.io/api-reference/agent/create-a-new-agent)

