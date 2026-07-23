"""Demo 02：多轮对话中 Context 如何增长（需要 API）。

学习目标：
1. 同一 Agent 实例连续 reply，消息会累积进 state.context；
2. 可用 count_tokens 估算即将送入模型的体积；
3. 上下文不是越长越好：成本上升，且可能带入无关旧信息。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.message import UserMsg

from _common import build_agent, estimate_tokens, print_context_snapshot, print_msg_summary


async def main() -> None:
    agent = build_agent(
        system_prompt="你是简洁的中文助教。每题只回答一句话，并尽量复述已知约束。",
        max_iters=3,
    )

    turns = [
        "请记住约束：回答必须包含标记 [CTX]。",
        "AgentScope 里 Context 主要解决什么问题？",
        "刚才的标记约束还在吗？请在回答里带上 [CTX]。",
    ]

    for i, text in enumerate(turns, start=1):
        msg = await agent.reply(UserMsg(name="user", content=text))
        tokens = await estimate_tokens(agent)
        print_msg_summary(msg, f"第 {i} 轮 reply")
        print(f"estimated_tokens ≈ {tokens}")
        print_context_snapshot(agent, f"第 {i} 轮后 Context")

    print("\n=== 结论 ===")
    print("- 轮次增加 → context_msgs / estimated_tokens 通常一起上升。")
    print("- 这就是后续需要压缩 / 截断 / offload 的原因。")


if __name__ == "__main__":
    asyncio.run(main())
