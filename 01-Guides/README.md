# AgentScope Guides

## 第一阶段：Building Blocks

| 顺序 | 章节 | 核心成果 |
|---|---|---|
| 1 | [Message 与 Event](01-Building-Blocks/01-Message-Event/README.md) | 能消费并展示 Agent 流式事件 |
| 2 | [Agent](01-Building-Blocks/02-Agent/README.md) | 能创建并运行单 Agent |
| 3 | [Model](01-Building-Blocks/03-Model/README.md) | 能安全配置和切换模型 |
| 4 | [Context](01-Building-Blocks/04-Context/README.md) | 能管理多轮上下文与 token |
| 5 | [Tool](01-Building-Blocks/05-Tool/README.md) | 能开发、注册和测试自定义工具 |
| 6 | [Plan](01-Building-Blocks/06-Plan/README.md) | 能规划和跟踪多步骤任务 |
| 7 | [Permission System](01-Building-Blocks/07-Permission-System/README.md) | 能拦截高风险操作并请求确认 |
| 8 | [Middleware](01-Building-Blocks/08-Middleware/README.md) | 能统一加入日志、重试和拦截逻辑 |
| 9 | [RAG](01-Building-Blocks/09-RAG/README.md) | 能构建带来源的文档问答 Agent |
| 10 | [Long-Term Memory](01-Building-Blocks/10-Long-Term-Memory/README.md) | 能实现受控的跨会话记忆 |
| 11 | [Workspace](01-Building-Blocks/11-Workspace/README.md) | 能在隔离环境中执行工具与代码 |

## 第二阶段：Agent as Service

| 顺序 | 章节 | 核心成果 |
|---|---|---|
| 1 | [Architecture](02-Agent-as-Service/01-Architecture/README.md) | 能解释一次服务请求的完整链路 |
| 2 | [Agent Team](02-Agent-as-Service/02-Agent-Team/README.md) | 能实现 Manager–Workers 小团队 |
| 3 | [Resource Sharing](02-Agent-as-Service/03-Resource-Sharing/README.md) | 能设计资源共享与租户隔离 |
| 4 | [RAG Service](02-Agent-as-Service/04-RAG-Service/README.md) | 能服务化知识库的导入与查询 |
| 5 | [Workspace Manager](02-Agent-as-Service/05-Workspace-Manager/README.md) | 能管理 Workspace 生命周期 |
| 6 | [API](02-Agent-as-Service/06-API/README.md) | 能通过 REST/SSE 调用 Agent 服务 |

> 服务化目录中的 Resource Sharing、Workspace Manager 和部分 API 内容来自开发版主线。学习时应记录依赖版本，不要过早绑定尚未稳定的接口。

