"""Demo 01：从零创建最小 Agent，并用 reply 拿最终回答

学习目标：
1. Agent 至少需要 name、system_prompt、model；
2. reply(UserMsg) 会跑完整轮推理-行动循环，返回完整 AssistantMsg；
3. Agent ≠ 一次模型 API：即使本例无工具，也是由 Agent 统一组织输入与输出。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.message import UserMsg

from _common import build_agent, print_msg_summary


async def main() -> None:
    agent = build_agent(
        name="Tutor",
        system_prompt=(
            "你是 AgentScope 学习助教。只用中文，回答不超过两句话。"
            "如果问题与 AgentScope / Agent / 工具无关，请礼貌拒绝。"
        ),
        max_iters=3,
    )

    user_msg = UserMsg(
        name="user",
        content="一句话说明：AgentScope 里的 Agent 主要负责什么？",
    )
    result = await agent.reply(user_msg)
    print_msg_summary(result, "reply() 返回的最终消息")


if __name__ == "__main__":
    asyncio.run(main())
