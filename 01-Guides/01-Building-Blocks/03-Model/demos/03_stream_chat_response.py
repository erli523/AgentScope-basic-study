"""Demo 03：观察 Model 的流式 ChatResponse。

注意：这里得到的是 ChatResponse chunk，不是 AgentEvent。
最后一个 is_last=True chunk 保存聚合后的完整结果，不应再和 delta 重复相加。
"""

from __future__ import annotations

import asyncio

from agentscope.message import SystemMsg, UserMsg

from _common import build_model, content_text


async def main() -> None:
    model = build_model(stream=True, temperature=0.1, max_tokens=120)
    messages = [
        SystemMsg(name="system", content="你是简洁的中文技术助教。"),
        UserMsg(name="user", content="用一句话解释什么是流式模型响应。"),
    ]

    raw = await model(messages)
    if not hasattr(raw, "__aiter__"):
        raise RuntimeError("预期 stream=True 返回异步生成器。")

    delta_parts: list[str] = []
    final_text = ""
    chunk_count = 0

    print("=== 实时增量 ===")
    async for chunk in raw:
        chunk_count += 1
        text = content_text(chunk.content)
        block_types = [getattr(block, "type", type(block).__name__) for block in chunk.content]

        if chunk.is_last:
            final_text = text
            print(f"\n[final chunk] blocks={block_types} usage={chunk.usage}")
        else:
            delta_parts.append(text)
            print(text, end="", flush=True)

    delta_text = "".join(delta_parts)
    print("\n=== 对照 ===")
    print("chunk 数量       :", chunk_count)
    print("增量拼接结果     :", repr(delta_text))
    print("最终聚合 chunk   :", repr(final_text))
    print("两者是否一致     :", delta_text == final_text)
    print("不要执行 delta_text + final_text，否则文本会重复。")


if __name__ == "__main__":
    asyncio.run(main())

