# AgentScope 学习路线

## 准备阶段

需要具备以下基础：

- Python 3.11+、虚拟环境和依赖管理；
- `async`、`await`、异步生成器和 `async for`；
- 类型提示、异常处理、环境变量；
- HTTP、JSON、REST 和 SSE 的基本概念；
- 大模型消息、tool call、token 和上下文窗口的基本概念。

建议固定环境：

```bash
python -m venv .venv
pip install "agentscope==2.0.4.post1"
```

API Key 只能通过环境变量或密钥系统提供，不应写入示例代码或提交到 Git。

## 阶段一：最小可运行 Agent

学习 Message/Event、Agent、Model、Context、Tool。

阶段作品：命令行 Agent，至少具有两个自定义工具，能够流式显示文本和工具调用事件，并支持多轮对话。

## 阶段二：安全与工程化

学习 Plan、Permission System、Middleware、Workspace。

阶段作品：为第一阶段 Agent 加入多步骤计划、危险操作审批、统一日志和隔离执行环境。

## 阶段三：知识与记忆

学习 RAG 和 Long-Term Memory。

阶段作品：基于本地文档回答问题、给出来源，并且只保存用户明确允许的跨会话偏好。

## 阶段四：服务化与多 Agent

学习 Architecture、API、Agent Team、Resource Sharing、RAG Service 和 Workspace Manager。

阶段作品：Manager 调度检索 Agent 与执行 Agent，通过 REST/SSE 对外服务，具备会话、权限、资源隔离和审计记录。

## 每章统一学习方法

每章至少提交四类成果：

1. `README.md` 中的概念总结；
2. 一个可以独立运行的最小示例；
3. 一个失败或边界条件测试；
4. 一段“本组件与相邻组件的职责边界”说明。

## 最终验收问题

- Message 与 Event 有什么区别？
- Context、RAG、Long-Term Memory 分别解决什么问题？
- Plan 为什么不能代替确定性的业务工作流？
- 为什么权限控制不能只写在 Prompt 中？
- Tool、Middleware、Workspace 的安全边界分别在哪里？
- Agent、Session、Tenant、Workspace 和 RAG Knowledge Base 如何关联？
- SSE 中断后如何恢复，写操作如何避免重复执行？

