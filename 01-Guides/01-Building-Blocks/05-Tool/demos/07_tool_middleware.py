"""Demo 07：工具中间件的洋葱顺序、参数加工和重试。"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any

from agentscope.message import TextBlock
from agentscope.permission import PermissionBehavior, PermissionContext, PermissionDecision
from agentscope.tool import ToolBase, ToolChunk, ToolMiddlewareBase

from _common import chunk_text, collect_direct_tool


class LoggingMiddleware(ToolMiddlewareBase):
    async def on_tool_call(
        self,
        tool: ToolBase,
        input_kwargs: dict[str, Any],
        next_handler: Callable[..., AsyncGenerator[ToolChunk, None]],
    ) -> AsyncGenerator[ToolChunk, None]:
        print(f"[logging before] {tool.name} {input_kwargs}")
        async for chunk in next_handler(**input_kwargs):
            yield chunk
        print(f"[logging after ] {tool.name}")


class RetryMiddleware(ToolMiddlewareBase):
    def __init__(self, max_attempts: int = 2) -> None:
        self.max_attempts = max_attempts

    async def on_tool_call(
        self,
        tool: ToolBase,
        input_kwargs: dict[str, Any],
        next_handler: Callable[..., AsyncGenerator[ToolChunk, None]],
    ) -> AsyncGenerator[ToolChunk, None]:
        for attempt in range(1, self.max_attempts + 1):
            try:
                print(f"  [retry attempt {attempt}]")
                async for chunk in next_handler(**input_kwargs):
                    yield chunk
                return
            except RuntimeError as exc:
                if attempt == self.max_attempts:
                    raise
                print(f"  [retry caught] {exc}")


class FlakyLookup(ToolBase):
    name = "flaky_lookup"
    description = "第一次失败、第二次成功的学习工具。"
    input_schema = {
        "type": "object",
        "properties": {"term": {"type": "string"}},
        "required": ["term"],
    }
    is_concurrency_safe = False
    is_read_only = True

    def __init__(self) -> None:
        super().__init__(middlewares=[LoggingMiddleware(), RetryMiddleware(2)])
        self.attempts = 0

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        return PermissionDecision(PermissionBehavior.ALLOW, "只读 Demo")

    async def call(self, term: str) -> ToolChunk:
        self.attempts += 1
        if self.attempts == 1:
            raise RuntimeError("模拟瞬时失败")
        return ToolChunk(content=[TextBlock(text=f"{term}: 第二次调用成功")])


async def main() -> None:
    tool = FlakyLookup()
    chunks = await collect_direct_tool(tool, term="Toolkit")
    print("result:", chunk_text(chunks[-1]))
    print("attempts:", tool.attempts)
    print("\n第一个注册的 LoggingMiddleware 是最外层，所以 after 最后执行。")


if __name__ == "__main__":
    asyncio.run(main())

