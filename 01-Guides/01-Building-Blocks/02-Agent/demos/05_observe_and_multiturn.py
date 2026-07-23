"""Demo 05：observe 注入上下文 + 多轮 reply 复用同一 Agent

学习目标：
1. observe(msgs)：把消息写入上下文，但不触发推理；
2. 同一个 Agent 实例连续 reply，会保留会话上下文；
3. 这与「每次新建 Agent / 每次 bootstrap」是不同策略（实习项目目前偏后者）。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.message import AssistantMsg, UserMsg

from _common import build_agent, print_msg_summary


async def main() -> None:
    agent = build_agent(
        name="Tutor",
        system_prompt=(
            "你是 AgentScope 助教。回答简短。"
            "如果上下文里已有背景资料，请优先依据背景回答。"
        ),
        max_iters=4,
    )

    # 1) 只观察，不回答
    # 注意：observe 只接受 role=user/assistant，且不能含 tool/thinking 块
    await agent.observe(
        [
            UserMsg(
                name="curriculum",
                content="背景：本课程固定学习版本为 agentscope 2.0.x。",
            ),
            AssistantMsg(
                name="peer-agent",
                content="补充：Message 负责持久化，Event 负责流式传输。",
            ),
        ],
    )
    print("已 observe 两条背景消息（未触发模型推理）")

    # 2) 第一轮：问背景相关问题
    r1 = await agent.reply(
        UserMsg(name="user", content="我们这门课学的是哪个大版本？只答版本号。"),
    )
    print_msg_summary(r1, "第 1 轮 reply")

    # 3) 第二轮：依赖上一轮上下文
    r2 = await agent.reply(
        UserMsg(
            name="user",
            content="那 Message 和 Event 各自负责什么？各用半句话。",
        ),
    )
    print_msg_summary(r2, "第 2 轮 reply（应能利用上下文）")

    # 4) 看一下状态里大概有多少上下文（字段因版本可能略有差异）
    ctx = getattr(agent.state, "context", None)
    print("\n=== agent.state 一瞥 ===")
    print(f"session_id : {getattr(agent.state, 'session_id', None)}")
    print(f"cur_iter   : {getattr(agent.state, 'cur_iter', None)}")
    if ctx is None:
        print("context    : None")
    else:
        # context 可能是列表或带 messages 的对象
        if isinstance(ctx, list):
            print(f"context_len: {len(ctx)}")
        else:
            msgs = getattr(ctx, "messages", None) or getattr(ctx, "msgs", None)
            print(f"context_type: {type(ctx).__name__}")
            if msgs is not None:
                print(f"context_msgs: {len(msgs)}")


if __name__ == "__main__":
    asyncio.run(main())
