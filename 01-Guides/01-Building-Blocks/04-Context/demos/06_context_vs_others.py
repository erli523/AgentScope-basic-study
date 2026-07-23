"""Demo 06：划清 Context / Session / RAG / 长期记忆（无需 API）。

学习目标：
1. 四者解决的问题不同，不要混用一个词；
2. Context 是「当前窗口内的工作记忆」；
3. 压缩与 offload 仍属于短期/会话内机制，不等于跨会话记忆。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.message import UserMsg

from _common import build_agent, print_context_snapshot


def print_boundary_table() -> None:
    rows = [
        ("Context", "当前模型窗口里的工作记忆", "本会话、近几轮", "压缩 / 截断 / offload"),
        ("Session", "可恢复的会话状态主键与存储", "跨进程，仍属同一会话", "Redis/DB + session_id"),
        ("RAG", "从外部知识库检索相关片段", "按查询动态注入", "向量库 / 文档索引"),
        ("Long-Term Memory", "跨会话、经许可的持久偏好/事实", "跨会话、长期", "记忆中间件 / 存储策略"),
    ]
    print("=== 职责边界 ===")
    print(f"{'概念':<18}{'解决什么':<28}{'生命周期':<22}{'典型手段'}")
    print("-" * 96)
    for concept, what, life, how in rows:
        print(f"{concept:<18}{what:<28}{life:<22}{how}")


async def main() -> None:
    print_boundary_table()

    agent = build_agent(
        system_prompt="你是助教。",
        context_size=128000,
    )
    await agent.observe(UserMsg(name="user", content="这是一条仅存在于当前 Context 的临时备注。"))
    print_context_snapshot(agent, "当前 AgentState 中的短期 Context")

    print("\n=== 易混点 ===")
    print("1. 把 Context 存进 Session：解决的是断线恢复，不是无限窗口。")
    print("2. 把旧对话全塞进 Context：成本高，且可能污染推理。")
    print("3. 用 RAG 替代 Context：RAG 不知道『刚才那轮工具失败了』这类过程态。")
    print("4. 用 Long-Term Memory 替代压缩：长期记忆应受控写入，不是自动 dump 全历史。")

    print("\n=== 一句话 ===")
    print("Context 管『此刻模型看见什么』；Session 管『这份状态存在哪』；")
    print("RAG 管『外部知识怎么取』；长期记忆管『跨会话记住什么』。")


if __name__ == "__main__":
    asyncio.run(main())
