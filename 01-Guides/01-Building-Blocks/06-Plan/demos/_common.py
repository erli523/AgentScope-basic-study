"""Plan 章节公共辅助。"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from agentscope.message import TextBlock, ToolCallBlock
from agentscope.state import AgentState
from agentscope.tool import Toolkit, ToolResponse

_AGENT_COMMON = (
    Path(__file__).resolve().parents[2]
    / "02-Agent"
    / "demos"
    / "_common.py"
)


def _load_agent_common():
    spec = importlib.util.spec_from_file_location("plan_agent_common", _AGENT_COMMON)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载公共配置：{_AGENT_COMMON}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_agent_common = _load_agent_common()
build_agent = _agent_common.build_agent
print_msg_summary = _agent_common.print_msg_summary


def response_text(response: Any) -> str:
    return "".join(
        block.text
        for block in getattr(response, "content", [])
        if isinstance(block, TextBlock)
    )


async def call_task_tool(
    toolkit: Toolkit,
    state: AgentState,
    name: str,
    input_data: dict[str, Any],
    call_id: str | None = None,
) -> ToolResponse:
    """通过 Toolkit 调用任务工具，让 _agent_state 自动注入。"""
    tool_call = ToolCallBlock(
        id=call_id or f"{name}-{len(state.tasks_context.tasks) + 1}",
        name=name,
        input=json.dumps(input_data, ensure_ascii=False),
    )
    final: ToolResponse | None = None
    async for item in toolkit.call_tool(tool_call, state):
        if isinstance(item, ToolResponse):
            final = item
    if final is None:
        raise RuntimeError(f"{name} 未返回最终 ToolResponse")
    return final


def print_tasks(state: AgentState, title: str = "任务清单") -> None:
    print(f"\n=== {title} ===")
    if not state.tasks_context.tasks:
        print("(空)")
        return
    for task in state.tasks_context.tasks:
        print(
            f"id={task.id} state={task.state:<11} owner={task.owner or '-':<8} "
            f"subject={task.subject!r} blocks={task.blocks} blocked_by={task.blocked_by}",
        )

