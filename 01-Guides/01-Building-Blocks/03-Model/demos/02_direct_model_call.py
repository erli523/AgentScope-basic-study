"""Demo 02：绕过 Agent，直接调用 Model。

学习目标：
1. Model 接收 AgentScope Msg 列表；
2. stream=False 时返回一个完整 ChatResponse；
3. Model 只完成一次生成，不负责 Context 与 ReAct 循环。
"""

from __future__ import annotations

import asyncio

from agentscope.message import SystemMsg, UserMsg

from _common import build_model, call_and_collect, content_text


async def main() -> None:
    model = build_model(stream=False, temperature=0.1, max_tokens=120)
    messages = [
        SystemMsg(name="system", content="你是 AgentScope 中文助教，回答不超过两句话。"),
        UserMsg(name="user", content="Model 层和 Agent 层的主要区别是什么？"),
    ]

    response, chunks = await call_and_collect(model, messages)

    print("=== 完整 ChatResponse ===")
    print("type    :", response.type)
    print("id      :", response.id)
    print("is_last :", response.is_last)
    print("blocks  :", [getattr(block, "type", type(block).__name__) for block in response.content])
    print("text    :", content_text(response.content))
    print("usage   :", response.usage)
    print("chunks  :", len(chunks), "(stream=False，因此应为 0)")


if __name__ == "__main__":
    asyncio.run(main())

