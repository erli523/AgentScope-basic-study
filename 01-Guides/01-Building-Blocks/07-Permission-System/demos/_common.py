"""Permission System 章节公共辅助。"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from agentscope.permission import PermissionDecision, PermissionEngine

_AGENT_COMMON = (
    Path(__file__).resolve().parents[2]
    / "02-Agent"
    / "demos"
    / "_common.py"
)


def _load_agent_common():
    spec = importlib.util.spec_from_file_location("permission_agent_common", _AGENT_COMMON)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载公共配置：{_AGENT_COMMON}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_agent_common = _load_agent_common()
build_agent = _agent_common.build_agent


async def decide(
    engine: PermissionEngine,
    tool: Any,
    tool_input: dict[str, Any],
) -> PermissionDecision:
    return await engine.check_permission(tool, tool_input)


def brief(decision: PermissionDecision) -> str:
    return (
        f"behavior={decision.behavior.value:<5} "
        f"bypass_immune={str(decision.bypass_immune):<5} "
        f"message={decision.message!r}"
    )

