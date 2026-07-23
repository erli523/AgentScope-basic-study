# 10 Long-Term Memory

## 学习内容

- 记忆写入、检索、更新、合并和遗忘；
- 用户偏好、事实记忆与任务经验；
- AgentScope 长期记忆接口及 ReMe/Mem0 等集成；
- 记忆的隐私、来源和置信度。

## 学习重点

只保存未来确实有用且允许保存的信息。模型推测不能直接当成用户事实；敏感信息需要明确授权、保留期限和删除能力。

## 实践任务

让 Agent 记住用户选择的学习语言和当前进度，重启会话后恢复；随后实现查看、更正和删除记忆。

## 验收标准

- 能区分 Context、RAG 和长期记忆；
- 每条记忆具有来源和更新时间；
- 用户能检查、修改和删除自己的记忆；
- 错误记忆不会无限传播。

[开发版官方文档](https://docs.agentscope.io/latest/zh/building-blocks/long-term-memory) · [ReMe](https://github.com/agentscope-ai/ReMe)

