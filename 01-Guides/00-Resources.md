# AgentScope 初学者公开资料

更新日期：2026-07-23。

## 官方文档

1. [AgentScope 2.0.4 中文文档](https://docs.agentscope.io/versions/2.0.4/zh)：本手册的主要依据。
2. [2.0.4 中文快速开始](https://docs.agentscope.io/versions/2.0.4/zh/quickstart)：第一个应运行的示例。
3. [开发版中文文档](https://docs.agentscope.io/latest/zh)：仅用于查看稳定版尚未包含的新章节。
4. [PyPI](https://pypi.org/project/agentscope/)：核对稳定版本和 Python 版本要求。

## 官方 GitHub 项目

| 项目 | 建议用途 |
|---|---|
| [agentscope-ai/agentscope](https://github.com/agentscope-ai/agentscope) | 框架源码、README、2.0 示例和测试 |
| [中文 README](https://github.com/agentscope-ai/agentscope/blob/main/README_zh.md) | 快速了解 2.0 的定位和最小代码 |
| [agentscope-samples](https://github.com/agentscope-ai/agentscope-samples) | Chatbot、浏览器 Agent、Deep Research、多 Agent 示例 |
| [agentscope-runtime](https://github.com/agentscope-ai/agentscope-runtime) | 服务化与运行时参考 |
| [agentscope-studio](https://github.com/agentscope-ai/agentscope-studio) | 可视化与运行过程观察 |
| [ReMe](https://github.com/agentscope-ai/ReMe) | 长期记忆专题 |
| [AgentTeams](https://github.com/agentscope-ai/AgentTeams) | 企业级多 Agent 协作，高级阶段阅读 |

运行任何示例前，先检查它自己的 `README`、`pyproject.toml` 或依赖文件。不同仓库和示例可能对应不同 AgentScope 版本。

## 论文

- [AgentScope: A Flexible yet Robust Multi-Agent Platform](https://arxiv.org/abs/2402.14034)

论文用于学习设计思想。论文早于 AgentScope 2.0，不应直接照搬其中的旧 API。

## 第三方技术文章

- [阿里开源 Agent 框架大升级：AgentScope 2.0](https://blog.csdn.net/Guo_Python/article/details/161509613)
- [AgentScope 从入门到精通](https://blog.csdn.net/weixin_58753619/article/details/153646966)
- [AgentScope：生产级 AI Agent 框架完全指南](https://txtmix.com/posts/tech/ai-agent/agentscope-ai-agent-framework/)

第三方文章适合辅助理解，不作为 API 的最终依据。若代码中大量使用 `DialogAgent`、`UserAgent` 等接口，应先判断它是否基于 AgentScope 1.x。

## 推荐的资料优先级

1. 稳定版官方 Quickstart；
2. 官方 Building Blocks 文档；
3. 官方仓库 `examples/`；
4. 自己修改并运行最小示例；
5. 第三方博客；
6. 源码和论文。

