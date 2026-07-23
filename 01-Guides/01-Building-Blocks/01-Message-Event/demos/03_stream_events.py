"""Demo 03：用 reply_stream 观察 Event 流（需要 DASHSCOPE_API_KEY）

学习目标：
1. reply() 返回完整 Msg；reply_stream() 产出增量 Event；
2. 事件大致遵循 start → delta → end；
3. 文本增量应拼接，而不是把每个 delta 当成一条新消息。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.event import EventType
from agentscope.message import UserMsg

from _common import build_agent, event_brief


async def main() -> None:
    agent = build_agent(
        system_prompt="你是简洁的中文助手。回答控制在两句话以内。",
    )
    user_msg = UserMsg(name="user", content="用一句话解释什么是 Agent。")

    print("=== 事件流（观察 type 顺序）===\n")
    text_parts: list[str] = []

    async for event in agent.reply_stream(user_msg):
        print(event_brief(event))

        # 官方推荐：按 event.type 分发处理
        match event.type:
            case EventType.TEXT_BLOCK_DELTA:
                text_parts.append(event.delta)
                # 终端实时打字效果
                print(event.delta, end="", flush=True, file=sys.stderr)
            case EventType.REPLY_END:
                print("\n", file=sys.stderr)
            case _:
                pass

    print("\n=== 拼接后的最终文本 ===")
    print("".join(text_parts) or "(无文本增量)")


if __name__ == "__main__":
    asyncio.run(main())
