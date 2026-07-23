"""Demo 03：手动触发上下文压缩 compress_context（需要 API）。

学习目标：
1. 缩小 context_size + 提高 trigger 灵敏度，便于课堂演示；
2. compress_context 低于阈值时是空操作；超过阈值才真正压缩；
3. 压缩后：较早消息进入 summary，最近消息留在 context。

注意：
- 压缩内部会走 generate_structured_output；若当前供应商
  （尤其 DeepSeek thinking）对 forced tool_choice 不友好，可能失败。
- 可改 AI_PROVIDER=qwen / openai 再试，或增大 max_tokens。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.agent import ContextConfig
from agentscope.message import AssistantMsg, UserMsg

from _common import (
    build_agent,
    estimate_tokens,
    print_context_snapshot,
)


async def main() -> None:
    # 故意把窗口做小，方便用少量消息触发压缩
    context_size = 2500
    cfg = ContextConfig(
        trigger_ratio=0.55,
        reserve_ratio=0.12,
        tool_result_limit=2000,
    )
    agent = build_agent(
        context_config=cfg,
        context_size=context_size,
        system_prompt=(
            "你是项目助教。必须记住：项目代号=AS-CTX-01，"
            "部署环境=staging，负责人=Ming。"
        ),
        max_iters=3,
    )

    filler = (
        "背景补充：本周要完成 Context 学习，包括压缩、工具截断与 offload。"
        "请在后续回答中保留项目代号、环境和负责人信息。"
    )
    # 注入多轮较长消息，抬高 token 估算
    for i in range(8):
        await agent.observe(
            [
                UserMsg(
                    name="user",
                    content=f"[{i + 1}/8] {filler} 额外备注：轮次-{i + 1}，"
                    f"{'重点约束请保留。' * 8}",
                ),
                AssistantMsg(
                    name=agent.name,
                    content=f"已记录轮次-{i + 1} 的背景与约束。" + ("确认。" * 20),
                ),
            ],
        )

    before_tokens = await estimate_tokens(agent)
    threshold = int(cfg.trigger_ratio * agent.model.context_size)
    print(f"context_size={agent.model.context_size}")
    print(f"threshold≈{threshold} (trigger_ratio={cfg.trigger_ratio})")
    print(f"estimated_tokens before≈{before_tokens}")
    print_context_snapshot(agent, "压缩前")

    print("\n>>> 调用 await agent.compress_context()")
    try:
        await agent.compress_context()
    except Exception as exc:  # noqa: BLE001 - demo 需要展示供应商差异
        print(f"压缩失败: {type(exc).__name__}: {exc}")
        print(
            "提示：可切换 AI_PROVIDER=qwen 或 openai 后重试；"
            "DeepSeek thinking 模式对结构化摘要 tool_choice 可能不兼容。",
        )
        return

    after_tokens = await estimate_tokens(agent)
    print(f"\nestimated_tokens after≈{after_tokens}")
    print_context_snapshot(agent, "压缩后")

    # 验证关键约束是否仍可通过 summary/context 回忆
    from _common import print_msg_summary

    reply = await agent.reply(
        UserMsg(
            name="user",
            content="项目代号、部署环境和负责人分别是什么？各用词组回答。",
        ),
    )
    print_msg_summary(reply, "压缩后追问关键事实")

    print("\n=== 结论 ===")
    print("- 低于阈值：compress_context 直接返回（空操作）。")
    print("- 超过阈值：旧消息 → summary，最近消息 → 新 context。")
    print("- 验收点：压缩后仍应能答出关键约束。")


if __name__ == "__main__":
    asyncio.run(main())
