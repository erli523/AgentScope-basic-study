"""Demo 01：从零创建最小 Agent，并用 reply 拿最终回答

学习目标：
1. Agent 至少需要 name、system_prompt、model；
2. reply(UserMsg) 会跑完整轮推理-行动循环，返回完整 AssistantMsg；
3. Agent ≠ 一次模型 API：即使本例无工具，也是由 Agent 统一组织输入与输出。
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.message import UserMsg

from _common import build_agent, print_msg_summary


def _block_to_dict(block: Any) -> dict[str, Any]:
    """把 Content Block 转成可打印的 dict。"""
    if hasattr(block, "model_dump"):
        return block.model_dump(mode="python")
    if isinstance(block, dict):
        return block
    return {"repr": repr(block)}


def print_blocks_detail(msg: Any, title: str = "content blocks 详情") -> None:
    """逐块打印 Msg.content 里每个 block 的字段。"""
    content = getattr(msg, "content", None)
    print(content)
    print(f"\n=== {title} ===")
    if not content:
        print("(空)")
        return

    print(f"共 {len(content)} 个 block\n")
    for i, block in enumerate(content, start=1):
        data = _block_to_dict(block)
        block_type = data.get("type", getattr(block, "type", type(block).__name__))
        print(f"--- [{i}] type={block_type} ---")
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        print()


async def main() -> None:
    agent = build_agent(
        name="Tutor",
        system_prompt=(
            "你是 AgentScope 学习助教。只用中文，回答不超过两句话。"
            "如果问题与 AgentScope / Agent / 工具无关，请礼貌拒绝。"
        ),
        max_iters=4,
    )

    user_msg = UserMsg(
        name="user",
        content="一句话说明：AgentScope 里的 Agent 主要负责什么？",
    )
    result = await agent.reply(user_msg)
    print_msg_summary(result, "reply() 返回的最终消息")
    print_blocks_detail(result)


if __name__ == "__main__":
    asyncio.run(main())
