"""Demo 02：对比 reply() 与 reply_stream()

学习目标：
1. 两者驱动同一套 reasoning-acting 循环；
2. reply：适合自动化脚本，只要最终结果；
3. reply_stream：适合 UI / 审计，边跑边拿 Event。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.event import EventType, ReplyStartEvent
from agentscope.message import AssistantMsg, UserMsg

from _common import build_agent, event_brief, print_msg_summary


async def run_reply(agent) -> None:
    print("\n### A) await agent.reply(...)")
    msg = await agent.reply(
        UserMsg(name="user", content="用一句话解释什么是 ReAct 循环。"),
    )
    print_msg_summary(msg, "reply 结果")


async def run_stream(agent) -> None:
    print("\n### B) async for event in agent.reply_stream(...)")
    rebuilt: AssistantMsg | None = None
    text_parts: list[str] = []

    async for event in agent.reply_stream(
        UserMsg(name="user", content="用一句话解释什么是 Toolkit。"),
    ):
        print(event_brief(event))
        if isinstance(event, ReplyStartEvent):
            rebuilt = AssistantMsg(name=event.name, content=[], id=event.reply_id)
        if event.type == EventType.TEXT_BLOCK_DELTA:
            text_parts.append(event.delta)
        if rebuilt is not None:
            rebuilt.append_event(event)

    print("\n拼接文本:", "".join(text_parts))
    if rebuilt is not None:
        print_msg_summary(rebuilt, "从事件流重建的 Msg")


async def main() -> None:
    agent = build_agent(
        system_prompt="你是简洁的中文技术助教，每题只回答一句话。",
        max_iters=3,
    )
    await run_reply(agent)
    await run_stream(agent)


if __name__ == "__main__":
    asyncio.run(main())
