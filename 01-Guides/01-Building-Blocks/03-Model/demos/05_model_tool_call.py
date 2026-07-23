"""Demo 05：直接让 Model 生成工具调用，但不执行工具。

这用于观察 Model 与 Agent 的职责边界：
- Model 根据工具 Schema 生成 ToolCallBlock；
- Agent/Toolkit 才负责权限检查、真实执行、结果回填和再次推理。
"""

from __future__ import annotations

import asyncio

from agentscope.message import SystemMsg, UserMsg
from agentscope.tool import ToolChoice

from _common import build_model, call_and_collect, content_text


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_model_term",
            "description": "查询 AgentScope Model 相关术语。",
            "parameters": {
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "要查询的术语，例如 ChatResponse 或 Credential",
                    },
                },
                "required": ["term"],
            },
        },
    },
]


async def main() -> None:
    model = build_model(stream=False, temperature=0.0, max_tokens=120)
    messages = [
        SystemMsg(
            name="system",
            content="你只负责选择合适的工具。用户询问术语时调用 lookup_model_term。",
        ),
        UserMsg(name="user", content="请查询 ChatResponse 的含义。"),
    ]

    response, _ = await call_and_collect(
        model,
        messages,
        tools=TOOLS,
        # auto 对 DeepSeek、DashScope 和 OpenAI-compatible 的兼容性更好。
        tool_choice=ToolChoice(mode="auto"),
    )

    print("=== Model 返回内容块 ===")
    for block in response.content:
        block_type = getattr(block, "type", type(block).__name__)
        print(f"- type={block_type}: {block.model_dump(exclude_none=True)}")

    tool_calls = [
        block
        for block in response.content
        if getattr(block, "type", None) == "tool_call"
    ]
    print("\n工具调用数量:", len(tool_calls))
    print("普通文本      :", repr(content_text(response.content)))

    if tool_calls:
        print("\n关键结论：这里只生成了调用意图，lookup_model_term 并没有真正执行。")
    else:
        print("\n当前模型没有选择工具。请检查模型工具能力，或增强系统提示后重试。")


if __name__ == "__main__":
    asyncio.run(main())

