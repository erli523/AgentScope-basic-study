"""Context 章节公共辅助：构建带 ContextConfig / offloader 的 Agent。"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any

from agentscope.agent import Agent, ContextConfig
from agentscope.agent._config import ReActConfig
from agentscope.credential import DashScopeCredential, OpenAICredential
from agentscope.model import DashScopeChatModel, OpenAIChatModel
from agentscope.permission import PermissionContext, PermissionMode
from agentscope.state import AgentState
from agentscope.tool import Toolkit
from agentscope.workspace import LocalWorkspace

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
load_env = _msg.load_env
_ENV_PATH = _msg._ENV_PATH
event_brief = _msg.event_brief

load_env()


def build_chat_model(
    *,
    stream: bool = True,
    context_size: int | None = None,
    temperature: float | None = 0.2,
    max_tokens: int | None = 512,
) -> OpenAIChatModel | DashScopeChatModel:
    """按 AI_PROVIDER 构建模型；可缩小 context_size 方便演示压缩触发。"""
    provider = os.getenv("AI_PROVIDER", "deepseek").strip().lower()
    timeout = float(os.getenv("AI_API_TIMEOUT", "60"))

    if provider in {"deepseek", "openai"}:
        if provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
            base_url = os.getenv(
                "DEEPSEEK_BASE_URL",
                "https://api.deepseek.com/v1",
            ).strip()
            model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
            label = "DEEPSEEK_API_KEY"
            default_ctx = 128000
        else:
            api_key = os.getenv("OPENAI_API_KEY", "").strip()
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
            label = "OPENAI_API_KEY"
            default_ctx = 128000

        if not api_key:
            raise SystemExit(f"未检测到 {label}，请写入手册根目录 .env 后重试。")

        return OpenAIChatModel(
            credential=OpenAICredential(api_key=api_key, base_url=base_url),
            model=model_name,
            stream=stream,
            context_size=context_size or default_ctx,
            parameters=OpenAIChatModel.Parameters(
                temperature=temperature,
                max_tokens=max_tokens,
                thinking_enable=False,
            ),
            client_kwargs={"timeout": timeout},
        )

    if provider in {"qwen", "dashscope"}:
        api_key = (
            os.getenv("QWEN_API_KEY", "").strip()
            or os.getenv("DASHSCOPE_API_KEY", "").strip()
        )
        if not api_key:
            raise SystemExit("未检测到 QWEN_API_KEY / DASHSCOPE_API_KEY。")

        base_url = (
            os.getenv("QWEN_BASE_URL", "").strip()
            or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        model_name = os.getenv("QWEN_MODEL", "qwen-plus").strip()
        return OpenAIChatModel(
            credential=OpenAICredential(api_key=api_key, base_url=base_url),
            model=model_name,
            stream=stream,
            context_size=context_size or 128000,
            parameters=OpenAIChatModel.Parameters(
                temperature=temperature,
                max_tokens=max_tokens,
                thinking_enable=False,
            ),
            client_kwargs={"timeout": timeout},
        )

    raise SystemExit(f"不支持 AI_PROVIDER={provider!r}")


def build_agent(
    *,
    name: str = "ContextTutor",
    system_prompt: str = "你是 AgentScope 上下文学习助教，回答简洁。",
    toolkit: Toolkit | None = None,
    context_config: ContextConfig | None = None,
    context_size: int | None = None,
    offloader: Any = None,
    max_iters: int = 6,
    bypass_permission: bool = True,
) -> Agent:
    """创建关注上下文管理的 Agent。"""
    state = None
    if bypass_permission:
        state = AgentState(
            permission_context=PermissionContext(mode=PermissionMode.BYPASS),
        )

    provider = os.getenv("AI_PROVIDER", "deepseek")
    model = build_chat_model(context_size=context_size)
    print(
        f"[config] env={_ENV_PATH if _ENV_PATH.is_file() else '(process env)'} "
        f"provider={provider} context_size={model.context_size} "
        f"max_iters={max_iters}",
    )

    return Agent(
        name=name,
        system_prompt=system_prompt,
        model=model,
        toolkit=toolkit or Toolkit(tools=[]),
        state=state,
        context_config=context_config or ContextConfig(),
        offloader=offloader,
        react_config=ReActConfig(max_iters=max_iters, stop_on_reject=False),
    )


async def make_workspace(subdir: str = "default") -> LocalWorkspace:
    """在 demos/.workspace/<subdir> 下初始化 LocalWorkspace。"""
    workdir = Path(__file__).resolve().parent / ".workspace" / subdir
    workdir.mkdir(parents=True, exist_ok=True)
    ws = LocalWorkspace(workdir=str(workdir))
    await ws.initialize()
    return ws


def print_context_snapshot(agent: Agent, title: str = "Context 快照") -> None:
    """打印 summary / context 长度等，便于观察压缩前后变化。"""
    state = agent.state
    summary = state.summary
    if isinstance(summary, str):
        summary_preview = summary[:200] + ("..." if len(summary) > 200 else "")
        summary_len = len(summary)
    else:
        summary_preview = repr(summary)[:200]
        summary_len = len(summary) if summary else 0

    print(f"\n=== {title} ===")
    print(f"session_id   : {state.session_id}")
    print(f"context_msgs : {len(state.context)}")
    print(f"summary_len  : {summary_len}")
    if summary_len:
        print(f"summary_head : {summary_preview!r}")
    for i, msg in enumerate(state.context[-5:], start=max(1, len(state.context) - 4)):
        role = getattr(msg, "role", "?")
        text = msg.get_text_content()
        preview = text[:60].replace("\n", " ") + ("..." if len(text) > 60 else "")
        print(f"  [{i}] {role}: {preview!r}")


async def estimate_tokens(agent: Agent) -> int:
    """估算当前即将送入模型的 token 数。"""
    kwargs = await agent._prepare_model_input()
    return await agent.model.count_tokens(
        kwargs.get("messages", []),
        kwargs.get("tools"),
    )


def print_msg_summary(msg: Any, title: str = "Msg 摘要") -> None:
    print(f"\n=== {title} ===")
    print(f"role/name : {getattr(msg, 'role', '?')}/{getattr(msg, 'name', '?')}")
    print(f"id        : {getattr(msg, 'id', '')}")
    print(f"text      : {msg.get_text_content()!r}")
    blocks = [getattr(b, "type", type(b).__name__) for b in msg.content]
    print(f"blocks    : {blocks}")
