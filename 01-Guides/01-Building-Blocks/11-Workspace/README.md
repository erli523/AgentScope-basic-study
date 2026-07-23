# 11 Workspace

## 学习内容

- 本地、Docker、E2B、OpenSandbox、Daytona 等 Workspace 后端；
- 文件与命令工具如何绑定 Workspace；
- 隔离、资源配额、超时、网络和凭证；
- Workspace 创建、复用和销毁。

## 学习重点

Workspace 是执行边界，不等于完整权限系统。即使在容器中，也要限制挂载目录、网络、凭证和资源消耗。

## 实践任务

让 Agent 在临时 Workspace 中生成并运行一个 Python 文件，验证它无法读取宿主机未授权目录，并在任务结束后清理环境。

## 验收标准

- Agent 代码不会直接在重要宿主目录执行；
- CPU、内存、时间和文件范围受到限制；
- 每个会话或租户的文件互相隔离；
- 异常退出后 Workspace 仍能被回收。

[官方文档](https://docs.agentscope.io/versions/2.0.4/zh/building-blocks/workspace)

