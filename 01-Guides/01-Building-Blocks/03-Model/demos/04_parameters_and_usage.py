"""Demo 04：通过命令行调整模型参数并观察 usage。"""

from __future__ import annotations

import argparse
import asyncio
import json

from agentscope.message import SystemMsg, UserMsg

from _common import build_model, call_and_collect, content_text, safe_model_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=120)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    model = build_model(
        stream=False,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    messages = [
        SystemMsg(name="system", content="你是中文技术助教，回答简洁。"),
        UserMsg(
            name="user",
            content="列出学习 AgentScope Model 层最重要的三个检查点。",
        ),
    ]

    response, _ = await call_and_collect(model, messages)

    print("=== 生效配置（无密钥）===")
    print(json.dumps(safe_model_summary(model), ensure_ascii=False, indent=2))
    print("\n=== 回答 ===")
    print(content_text(response.content))
    print("\n=== Usage ===")
    print(response.usage or "供应商未返回 usage")
    print("\ncontext_size 是容量配置；usage 才是本次请求的实际 token 统计。")


if __name__ == "__main__":
    asyncio.run(main())

