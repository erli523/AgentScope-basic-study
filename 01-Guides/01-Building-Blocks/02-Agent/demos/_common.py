"""Agent 示例公共辅助：加载手册根目录 .env，并支持 react_config。"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any

from agentscope.agent import Agent
from agentscope.agent._config import ReActConfig
from agentscope.permission import PermissionContext, PermissionMode
from agentscope.state import AgentState
from agentscope.tool import Toolkit

_MSG_COMMON = (
    Path(__file__).resolve().parents[2]
    / "01-Message-Event"
    / "demos"
    / "_common.py"
)


def _load_msg_common():
    spec = importlib.util.spec_from_file_location("message_event_common", _MSG_COMMON)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载: {_MSG_COMMON}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_msg = _load_msg_common()
build_chat_model = _msg.build_chat_model
event_brief = _msg.event_brief
load_env = _msg.load_env
_ENV_PATH = _msg._ENV_PATH

load_env()


def build_agent(
    *,
    name: str = "Friday",
    system_prompt: str = "你是一个简洁、准确的中文助手。",
    toolkit: Toolkit | None = None,
    max_iters: int = 8,
    stop_on_reject: bool = False,
    bypass_permission: bool = True,
) -> Agent:
    """创建带 ReAct 配置的 Agent。"""
    state = None
    if bypass_permission:
        state = AgentState(
            permission_context=PermissionContext(mode=PermissionMode.BYPASS),
        )

    provider = os.getenv("AI_PROVIDER", "deepseek")
    print(
        f"[config] env={_ENV_PATH if _ENV_PATH.is_file() else '(process env)'} "
        f"provider={provider} max_iters={max_iters}",
    )

    return Agent(
        name=name,
        system_prompt=system_prompt,
        model=build_chat_model(),
        toolkit=toolkit or Toolkit(tools=[]),
        state=state,
        react_config=ReActConfig(
            max_iters=max_iters,
            stop_on_reject=stop_on_reject,
        ),
    )


def print_msg_summary(msg: Any, title: str = "Msg 摘要") -> None:
    print(f"\n=== {title} ===")
    print(f"role/name : {getattr(msg, 'role', '?')}/{getattr(msg, 'name', '?')}")
    print(f"id        : {getattr(msg, 'id', '')}")
    print(f"text      : {msg.get_text_content()!r}")
    blocks = [getattr(b, "type", type(b).__name__) for b in msg.content]
    print(f"blocks    : {blocks}")
    usage = getattr(msg, "usage", None)
    if usage is not None:
        print(f"usage     : {usage}")
