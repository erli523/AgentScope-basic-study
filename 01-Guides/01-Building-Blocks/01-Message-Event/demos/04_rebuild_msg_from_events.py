"""Demo 04：从 Event 流用 append_event 重建完整 Msg（需要 DASHSCOPE_API_KEY）

学习目标：
1. Event 是流式传输单元，Msg 是完整会话单元；
2. ReplyStartEvent 时创建空 AssistantMsg；
3. 后续事件通过 msg.append_event(event) 增量还原；
4. 这正是 SSE 前端 / LangGraph 侧订阅事件后重建消息的方式。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.event import ReplyStartEvent, TextBlockDeltaEvent, ReplyEndEvent
from agentscope.message import AssistantMsg, UserMsg

from _common import build_agent


async def main() -> None:
    agent = build_agent(
        system_prompt="你是校园安防助手。回答简洁。",
    )
    user_msg = UserMsg(
        name="user",
        content="如果摄像头离线超过 15 分钟，通常应该怎么处理？一句话回答。",
    )

    msg: AssistantMsg | None = None

    print("=== 实时文本 ===")
    async for event in agent.reply_stream(user_msg):
        if isinstance(event, ReplyStartEvent):
            msg = AssistantMsg(name=event.name, content=[], id=event.reply_id)
            print(f"[ReplyStart] reply_id={event.reply_id[:8]}... name={event.name}")
        elif isinstance(event, TextBlockDeltaEvent):
            print(event.delta, end="", flush=True)
        elif isinstance(event, ReplyEndEvent):
            print("\n[ReplyEnd]")

        # 关键：始终把事件追加进消息，保证最终状态可还原
        if msg is not None:
            msg.append_event(event)

    assert msg is not None, "未收到 ReplyStartEvent，无法重建消息"

    print("\n=== 重建后的完整 Msg ===")
    print(f"id         : {msg.id}")
    print(f"role/name  : {msg.role}/{msg.name}")
    print(f"finished_at: {msg.finished_at}")
    print(f"text       : {msg.get_text_content()!r}")
    print(f"blocks     : {[getattr(b, 'type', type(b).__name__) for b in msg.content]}")


if __name__ == "__main__":
    asyncio.run(main())
