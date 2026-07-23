"""Demo 07：使用完全相同的调用代码切换模型供应商。

默认只调用 AI_PROVIDER 当前值。若同时配置了多个 Key：
python 07_switch_providers.py --providers deepseek qwen openai
"""

from __future__ import annotations

import argparse
import asyncio
import os
import time

from agentscope.message import SystemMsg, UserMsg

from _common import (
    build_model,
    call_and_collect,
    content_text,
    safe_model_summary,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--providers",
        nargs="+",
        default=[os.getenv("AI_PROVIDER", "deepseek")],
        help="deepseek qwen dashscope openai 中的一个或多个",
    )
    return parser.parse_args()


async def run_provider(provider: str) -> None:
    try:
        model = build_model(
            provider=provider,
            stream=False,
            temperature=0.0,
            max_tokens=100,
        )
    except ValueError as exc:
        print(f"\n[{provider}] 跳过：{exc}")
        return

    summary = safe_model_summary(model, provider)
    messages = [
        SystemMsg(name="system", content="你是中文技术助教，只回答一句话。"),
        UserMsg(name="user", content="AgentScope 为什么要抽象统一的 Model 接口？"),
    ]

    started = time.perf_counter()
    try:
        response, _ = await call_and_collect(model, messages)
    except Exception as exc:  # noqa: BLE001 - 对比 Demo 需要展示供应商错误
        print(f"\n[{provider}/{summary['model']}] 调用失败：{type(exc).__name__}: {exc}")
        return
    elapsed = time.perf_counter() - started

    print(f"\n=== {provider} / {summary['model']} ===")
    print("耗时 :", f"{elapsed:.2f}s")
    print("回答 :", content_text(response.content))
    print("usage:", response.usage or "未返回")


async def main() -> None:
    args = parse_args()
    for provider in args.providers:
        await run_provider(provider.strip().lower())

    print("\n比较结果时不要只看文风，还要比较工具、结构化输出、usage、延迟和错误行为。")


if __name__ == "__main__":
    asyncio.run(main())

