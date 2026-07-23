# 05 Workspace Manager

## 学习内容

- Workspace 的创建、分配、复用、暂停和销毁；
- Workspace 与租户、Agent、Session、Run 的绑定；
- 并发容量、资源配额和超时；
- 健康检查、异常回收和泄漏治理。

## 学习重点

Workspace Manager 负责环境生命周期，而 Workspace 负责单个执行环境的操作接口。复用能降低成本，但会增加状态残留和隔离风险。

## 实践任务

设计一个最多允许三个并发 Workspace 的管理器：任务申请、排队、租约续期、超时回收，并记录每个 Workspace 的归属。

## 验收标准

- 不会把同一私有 Workspace 分配给不同租户；
- 超时或进程崩溃后能够回收；
- 配额耗尽时有明确排队或拒绝策略；
- 能观察创建耗时、使用率和失败率。

[开发版官方文档](https://docs.agentscope.io/latest/zh/deploy/workspace-manager)

