"""Model 章节公共辅助：加载根目录 .env 并构建可配置模型。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import certifi
from agentscope.credential import DashScopeCredential, OpenAICredential
from agentscope.message import TextBlock
from agentscope.model import (
    ChatResponse,
    DashScopeChatModel,
    OpenAIChatModel,
)
from dotenv import load_dotenv

_HANDBOOK_ROOT = Path(__file__).resolve().parents[4]
_ENV_PATH = _HANDBOOK_ROOT / ".env"


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    model_name: str
    api_key: str
    base_url: str | None
    native_dashscope: bool = False


def load_env() -> Path | None:
    """加载根目录 .env，并修复部分 conda 环境的 CA 路径。"""
    current = os.environ.get("SSL_CERT_FILE", "").strip()
    if not current or not Path(current).is_file():
        ca_path = certifi.where()
        if Path(ca_path).is_file():
            os.environ["SSL_CERT_FILE"] = ca_path
            os.environ.setdefault("REQUESTS_CA_BUNDLE", ca_path)

    if _ENV_PATH.is_file():
        load_dotenv(_ENV_PATH, override=False)
        return _ENV_PATH
    load_dotenv(override=False)
    return None


load_env()


def get_provider_config(provider: str | None = None) -> ProviderConfig:
    """读取一个供应商配置；不会打印或返回脱敏前的配置摘要。"""
    selected = (provider or os.getenv("AI_PROVIDER", "deepseek")).strip().lower()

    if selected == "deepseek":
        config = ProviderConfig(
            provider=selected,
            model_name=os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip(),
            api_key=os.getenv("DEEPSEEK_API_KEY", "").strip(),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip(),
        )
        key_name = "DEEPSEEK_API_KEY"
    elif selected == "openai":
        config = ProviderConfig(
            provider=selected,
            model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
            api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
        )
        key_name = "OPENAI_API_KEY"
    elif selected in {"qwen", "dashscope"}:
        use_compatible = selected == "qwen" and os.getenv(
            "QWEN_USE_COMPATIBLE",
            "true",
        ).strip().lower() in {"1", "true", "yes"}
        config = ProviderConfig(
            provider=selected,
            model_name=(
                os.getenv("QWEN_MODEL", "").strip()
                or os.getenv("DASHSCOPE_MODEL", "").strip()
                or "qwen-plus"
            ),
            api_key=(
                os.getenv("QWEN_API_KEY", "").strip()
                or os.getenv("DASHSCOPE_API_KEY", "").strip()
            ),
            base_url=(
                os.getenv("QWEN_BASE_URL", "").strip()
                or os.getenv("DASHSCOPE_BASE_URL", "").strip()
                or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            ) if use_compatible else None,
            native_dashscope=not use_compatible,
        )
        key_name = "QWEN_API_KEY / DASHSCOPE_API_KEY"
    else:
        raise ValueError(
            f"不支持 AI_PROVIDER={selected!r}，可选 deepseek/qwen/dashscope/openai",
        )

    if not config.api_key:
        raise ValueError(f"未检测到 {key_name}，请先配置手册根目录 .env。")
    return config


def build_model(
    *,
    provider: str | None = None,
    stream: bool = True,
    temperature: float | None = None,
    max_tokens: int | None = None,
    thinking_enable: bool = False,
) -> OpenAIChatModel | DashScopeChatModel:
    """构建 Model；参数在构造时集中配置，供 Agent 或直接调用复用。"""
    config = get_provider_config(provider)
    timeout = float(os.getenv("AI_API_TIMEOUT", "60"))

    if config.native_dashscope:
        parameters = DashScopeChatModel.Parameters(
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_enable=thinking_enable,
        )
        return DashScopeChatModel(
            credential=DashScopeCredential(api_key=config.api_key),
            model=config.model_name,
            parameters=parameters,
            stream=stream,
            client_kwargs={"timeout": timeout},
        )

    parameters = OpenAIChatModel.Parameters(
        temperature=temperature,
        max_tokens=max_tokens,
        thinking_enable=thinking_enable,
    )
    return OpenAIChatModel(
        credential=OpenAICredential(
            api_key=config.api_key,
            base_url=config.base_url,
        ),
        model=config.model_name,
        parameters=parameters,
        stream=stream,
        client_kwargs={"timeout": timeout},
    )


def safe_model_summary(model: Any, provider: str | None = None) -> dict[str, Any]:
    """只展示非敏感配置，绝不读取/打印 credential 中的 API Key。"""
    config = get_provider_config(provider)
    parameters = getattr(model, "parameters", None)
    if hasattr(parameters, "model_dump"):
        parameters = parameters.model_dump(exclude_none=True)
    return {
        "class": type(model).__name__,
        "provider": config.provider,
        "model": getattr(model, "model", config.model_name),
        "stream": getattr(model, "stream", None),
        "context_size": getattr(model, "context_size", None),
        "base_url": config.base_url or "DashScope native SDK",
        "parameters": parameters,
        "credential": "configured (hidden)",
    }


def content_text(content: Any) -> str:
    """从 ChatResponse.content 中提取文本块。"""
    return "".join(
        block.text
        for block in content
        if isinstance(block, TextBlock)
    )


async def call_and_collect(
    model: OpenAIChatModel | DashScopeChatModel,
    messages: list[Any],
    **kwargs: Any,
) -> tuple[ChatResponse, list[ChatResponse]]:
    """统一处理 stream=False/True，返回最终响应与增量 chunk。"""
    raw = await model(messages, **kwargs)
    if isinstance(raw, ChatResponse):
        return raw, []

    chunks: list[ChatResponse] = []
    final: ChatResponse | None = None
    async for chunk in raw:
        if chunk.is_last:
            final = chunk
        else:
            chunks.append(chunk)

    if final is None:
        raise RuntimeError("模型流结束，但没有收到 is_last=True 的最终 ChatResponse。")
    return final, chunks

