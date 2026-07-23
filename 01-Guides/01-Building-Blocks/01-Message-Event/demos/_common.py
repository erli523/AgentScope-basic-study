"""Message / Event 示例的公共辅助。

优先从手册根目录的 `.env` 加载配置。

环境变量：
- AI_PROVIDER：deepseek | qwen | openai | dashscope（默认 deepseek）
- DeepSeek：DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL / DEEPSEEK_MODEL
- Qwen：QWEN_API_KEY 或 DASHSCOPE_API_KEY，以及对应 BASE_URL / MODEL
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import certifi
from agentscope.agent import Agent
from agentscope.credential import DashScopeCredential, OpenAICredential
from agentscope.model import DashScopeChatModel, OpenAIChatModel
from agentscope.permission import PermissionContext, PermissionMode
from agentscope.state import AgentState
from agentscope.tool import Toolkit
from dotenv import load_dotenv

_HANDBOOK_ROOT = Path(__file__).resolve().parents[4]
_ENV_PATH = _HANDBOOK_ROOT / ".env"


def _ensure_ssl_cert_env() -> None:
    """修复 conda 环境中 SSL_CERT_FILE 指向不存在路径的问题。"""
    current = os.environ.get("SSL_CERT_FILE", "").strip()
    if current and Path(current).is_file():
        return
    ca_path = certifi.where()
    if Path(ca_path).is_file():
        os.environ["SSL_CERT_FILE"] = ca_path
        os.environ.setdefault("REQUESTS_CA_BUNDLE", ca_path)


def load_env() -> Path | None:
    """加载手册根目录 `.env`，返回实际加载的路径。"""
    _ensure_ssl_cert_env()
    if _ENV_PATH.is_file():
        load_dotenv(_ENV_PATH, override=False)
        return _ENV_PATH
    load_dotenv(override=False)
    return None


load_env()


def build_chat_model() -> DashScopeChatModel | OpenAIChatModel:
    """按 AI_PROVIDER 构建聊天模型。"""
    provider = os.getenv("AI_PROVIDER", "deepseek").strip().lower()

    if provider in {"deepseek", "openai"}:
        if provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
            model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
            label = "DEEPSEEK_API_KEY"
        else:
            api_key = os.getenv("OPENAI_API_KEY", "").strip()
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
            label = "OPENAI_API_KEY"

        if not api_key:
            raise SystemExit(f"未检测到 {label}，请写入手册根目录 .env 后重试。")

        return OpenAIChatModel(
            credential=OpenAICredential(api_key=api_key, base_url=base_url),
            model=model_name,
            stream=True,
            client_kwargs={"timeout": float(os.getenv("AI_API_TIMEOUT", "60"))},
        )

    if provider in {"qwen", "dashscope"}:
        api_key = (
            os.getenv("QWEN_API_KEY", "").strip()
            or os.getenv("DASHSCOPE_API_KEY", "").strip()
        )
        if not api_key:
            raise SystemExit("未检测到 QWEN_API_KEY / DASHSCOPE_API_KEY。")

        # 兼容模式走 OpenAI SDK；原生 DashScope 也可
        use_compatible = os.getenv("QWEN_USE_COMPATIBLE", "true").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        model_name = (
            os.getenv("QWEN_MODEL", "").strip()
            or os.getenv("DASHSCOPE_MODEL", "").strip()
            or "qwen-plus"
        )

        if use_compatible:
            base_url = (
                os.getenv("QWEN_BASE_URL", "").strip()
                or os.getenv("DASHSCOPE_BASE_URL", "").strip()
                or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            return OpenAIChatModel(
                credential=OpenAICredential(api_key=api_key, base_url=base_url),
                model=model_name,
                stream=True,
                client_kwargs={"timeout": float(os.getenv("AI_API_TIMEOUT", "60"))},
            )

        return DashScopeChatModel(
            credential=DashScopeCredential(api_key=api_key),
            model=model_name,
        )

    raise SystemExit(
        f"不支持的 AI_PROVIDER={provider!r}，可选：deepseek / qwen / openai / dashscope",
    )


def build_agent(
    *,
    name: str = "Friday",
    system_prompt: str = "你是一个简洁、准确的中文助手。",
    toolkit: Toolkit | None = None,
    bypass_permission: bool = True,
) -> Agent:
    """创建一个最小可运行 Agent。

    学习示例默认 BYPASS 权限，避免工具卡在人工确认。
    正式项目请按角色配置更严格的 PermissionMode。
    """
    state = None
    if bypass_permission:
        state = AgentState(
            permission_context=PermissionContext(mode=PermissionMode.BYPASS),
        )

    provider = os.getenv("AI_PROVIDER", "deepseek")
    print(f"[config] env={_ENV_PATH if _ENV_PATH.is_file() else '(process env)'} provider={provider}")

    return Agent(
        name=name,
        system_prompt=system_prompt,
        model=build_chat_model(),
        toolkit=toolkit or Toolkit(tools=[]),
        state=state,
    )


def event_brief(event: Any) -> str:
    """把事件压缩成一行，便于观察事件流顺序。"""
    event_type = getattr(event, "type", type(event).__name__)
    parts = [f"type={event_type}"]

    for field in (
        "reply_id",
        "block_id",
        "tool_call_id",
        "tool_call_name",
        "model_name",
        "state",
    ):
        value = getattr(event, field, None)
        if value is not None:
            text = str(value)
            if field == "reply_id" and len(text) > 8:
                text = text[:8] + "..."
            parts.append(f"{field}={text}")

    delta = getattr(event, "delta", None)
    if isinstance(delta, str) and delta:
        preview = delta.replace("\n", "\\n")
        if len(preview) > 40:
            preview = preview[:40] + "..."
        parts.append(f"delta={preview!r}")

    return " | ".join(parts)
