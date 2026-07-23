"""Demo 01：观察 Context 三层结构（无需 API Key）。

学习目标：
1. 模型输入 ≈ System Prompt + Summary（可选）+ Context（最近消息）；
2. ContextConfig 控制何时压缩、保留多少、工具结果上限；
3. observe 只写入 context，不触发推理，也不会立刻产生 summary。
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.agent import ContextConfig
from agentscope.message import AssistantMsg, UserMsg

from _common import build_agent, print_context_snapshot


async def main() -> None:
    cfg = ContextConfig(
        trigger_ratio=0.8,
        reserve_ratio=0.1,
        tool_result_limit=3000,
    )
    agent = build_agent(context_config=cfg, context_size=128000)

    print("=== ContextConfig ===")
    print(
        json.dumps(
            {
                "trigger_ratio": cfg.trigger_ratio,
                "reserve_ratio": cfg.reserve_ratio,
                "tool_result_limit": cfg.tool_result_limit,
            },
            ensure_ascii=False,
            indent=2,
        ),
    )

    print("\n=== 模型一次调用看到的三层（概念）===")
    print("1) System Prompt  : agent 创建时的角色说明 + skill/中间件注入")
    print("2) Summary        : 压缩后的历史摘要（尚未压缩时为空）")
    print("3) Context        : state.context 里最近未压缩的 Msg 列表")

    await agent.observe(
        [
            UserMsg(name="user", content="约束：项目代号固定为 AS-CTX-01。"),
            AssistantMsg(name=agent.name, content="已记录项目代号 AS-CTX-01。"),
            UserMsg(name="user", content="下一问请优先引用该代号。"),
        ],
    )
    print_context_snapshot(agent, "observe 之后（尚无 summary）")

    print("\n=== 结论 ===")
    print("- summary 仍为空：压缩还没发生。")
    print("- context 已有 3 条消息：这些会进入下一次 model 调用。")
    print("- Context ≠ 整段永久记忆；过长时会被压缩成 summary。")


if __name__ == "__main__":
    asyncio.run(main())
