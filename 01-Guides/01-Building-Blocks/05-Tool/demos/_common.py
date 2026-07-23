"""Tool 章节公共辅助。"""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from typing import Any

from agentscope.message import TextBlock
from agentscope.tool import ToolChunk

_AGENT_COMMON = (
    Path(__file__).resolve().parents[2]
    / "02-Agent"
    / "demos"
    / "_common.py"
)


def _load_agent_common():
    spec = importlib.util.spec_from_file_location("tool_agent_common", _AGENT_COMMON)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载公共配置：{_AGENT_COMMON}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_agent_common = _load_agent_common()
build_agent = _agent_common.build_agent
event_brief = _agent_common.event_brief
print_msg_summary = _agent_common.print_msg_summary


def chunk_text(chunk: Any) -> str:
    return "".join(
        block.text
        for block in getattr(chunk, "content", [])
        if isinstance(block, TextBlock)
    )


async def collect_direct_tool(tool: Any, **kwargs: Any) -> list[ToolChunk]:
    """直接执行工具并统一收集单次/流式 ToolChunk。

    仅供独立单元测试；它不等同于 Agent 中完整的权限与事件流程。
    """
    result = tool(**kwargs)
    if inspect.isawaitable(result):
        result = await result

    if isinstance(result, ToolChunk):
        return [result]

    chunks: list[ToolChunk] = []
    if hasattr(result, "__aiter__"):
        async for chunk in result:
            chunks.append(chunk)
        return chunks

    if inspect.isgenerator(result):
        chunks.extend(result)
        return chunks

    raise TypeError(f"工具返回了不支持的类型：{type(result).__name__}")

