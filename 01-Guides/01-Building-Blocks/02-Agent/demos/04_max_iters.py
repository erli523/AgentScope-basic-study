"""Demo 04：max_iters —— 防止 Agent 无限调用工具

学习目标：
1. react_config.max_iters 限制「推理-行动」轮数（默认常见为 20）；
2. 触顶时会产出 ExceedMaxItersEvent；
3. 正式项目应设合理上限，并在编排层处理「未完成」状态。

本例故意让工具永远返回「请继续」，并设置很小的 max_iters，方便观察截断。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.event import (
    ExceedMaxItersEvent,
    ModelCallStartEvent,
    ReplyEndEvent,
    ToolCallStartEvent,
    ToolResultEndEvent,
)
from agentscope.message import TextBlock, UserMsg
from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
)
from agentscope.tool import Toolkit, ToolBase, ToolChunk

from _common import build_agent


class NeverDoneProbe(ToolBase):
    name = "probe_status"
    description = "探测任务是否完成。返回当前状态字符串。"
    input_schema = {
        "type": "object",
        "properties": {
            "step": {
                "type": "integer",
                "description": "当前探测步数，从 1 开始递增。",
            },
        },
        "required": ["step"],
    }
    is_concurrency_safe = True
    is_read_only = True

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW,
            message="学习示例自动放行",
        )

    async def call(self, step: int) -> ToolChunk:
        # 故意永不完成，逼出 ExceedMaxIters
        return ToolChunk(
            content=[TextBlock(text=f"step={step}: 尚未完成，请继续调用 probe_status")],
        )


async def main() -> None:
    agent = build_agent(
        name="Looper",
        system_prompt=(
            "你必须反复调用 probe_status，每次把 step 加 1，"
            "直到工具明确返回「已完成」。"
            "在完成前不要给出最终结论。"
        ),
        toolkit=Toolkit(tools=[NeverDoneProbe()]),
        max_iters=2,  # 故意设得很小
    )

    saw_exceed = False
    counts = {"model": 0, "tool": 0}

    async for event in agent.reply_stream(
        UserMsg(name="user", content="请开始探测，直到完成。"),
    ):
        if isinstance(event, ModelCallStartEvent):
            counts["model"] += 1
            print(f"[model] #{counts['model']}")
        elif isinstance(event, ToolCallStartEvent):
            counts["tool"] += 1
            print(f"[tool ] #{counts['tool']} -> {event.tool_call_name}")
        elif isinstance(event, ToolResultEndEvent):
            print(f"[result] state={event.state}")
        elif isinstance(event, ExceedMaxItersEvent):
            saw_exceed = True
            print(f"[EXCEED_MAX_ITERS] reply_id={event.reply_id[:8]}... name={event.name}")
        elif isinstance(event, ReplyEndEvent):
            print("[ReplyEnd]")

    print("\n=== 结论 ===")
    print(f"是否观察到 ExceedMaxItersEvent: {saw_exceed}")
    print("预期：max_iters=2 时，通常会在少量工具调用后被框架强制截断。")


if __name__ == "__main__":
    asyncio.run(main())
