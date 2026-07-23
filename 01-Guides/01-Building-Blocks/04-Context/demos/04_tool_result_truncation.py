"""Demo 04：工具结果截断 tool_result_limit（需要 API）。

学习目标：
1. 过大的工具输出会在进入 context 前被截断；
2. 截断处会出现 <<<TRUNCATED>>> 提醒；
3. limit 太低会丢关键信息，太高又可能一次填满窗口。
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.agent import ContextConfig
from agentscope.event import ToolResultEndEvent
from agentscope.message import TextBlock, UserMsg
from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
)
from agentscope.tool import Toolkit, ToolBase, ToolChunk

from _common import build_agent, print_context_snapshot, print_msg_summary


class DumpReport(ToolBase):
    name = "dump_report"
    description = "返回一份很长的模拟巡检报告文本。"
    input_schema = {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "报告主题"},
        },
        "required": ["topic"],
    }
    is_concurrency_safe = True
    is_read_only = True

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW,
            message="只读报告",
        )

    async def call(self, topic: str) -> ToolChunk:
        # 故意制造超长输出，触发截断
        body = {
            "topic": topic,
            "lines": [f"L{i:04d}: detail about {topic} " + ("x" * 40) for i in range(200)],
            "secret_tail": "ONLY_IN_FULL_REPORT::TAIL_MARKER",
        }
        return ToolChunk(
            content=[TextBlock(text=json.dumps(body, ensure_ascii=False))],
        )


async def main() -> None:
    cfg = ContextConfig(tool_result_limit=120)  # tokens，课堂演示用的小阈值
    agent = build_agent(
        system_prompt=(
            "你是运维助教。收到报告类问题时，必须先调用 dump_report，"
            "再基于工具结果用一句话总结。不要编造未出现的尾部标记。"
        ),
        toolkit=Toolkit(tools=[DumpReport()]),
        context_config=cfg,
        max_iters=6,
    )

    saw_truncation = False
    async for event in agent.reply_stream(
        UserMsg(name="user", content="请用 dump_report 生成主题=context-limit 的报告并总结。"),
    ):
        if isinstance(event, ToolResultEndEvent):
            # 结果最终会进 context；这里先标记事件发生
            pass

    # 从 context 里找 tool_result 文本是否含截断标记
    for msg in agent.state.context:
        for block in msg.get_content_blocks("tool_result"):
            text = ""
            output = getattr(block, "output", None)
            if isinstance(output, str):
                text = output
            elif isinstance(output, list):
                text = "".join(
                    getattr(b, "text", "") for b in output if hasattr(b, "text")
                )
            if "<<<TRUNCATED>>>" in text:
                saw_truncation = True
            print("\n=== tool_result 预览 ===")
            print(text[:400] + ("..." if len(text) > 400 else ""))
            print(f"contains_tail_marker: {'ONLY_IN_FULL_REPORT::TAIL_MARKER' in text}")
            print(f"contains_TRUNCATED  : {'<<<TRUNCATED>>>' in text}")

    print_context_snapshot(agent, "截断后的 Context")
    if agent.state.context:
        print_msg_summary(agent.state.context[-1], "上下文最后一条消息")

    print("\n=== 结论 ===")
    print(f"- 是否观察到截断标记: {saw_truncation}")
    print("- 未挂 offloader 时，被截掉的后半段会丢失（本 demo 未挂 workspace）。")
    print("- 下一章/本目录 05 会演示 offload 把截断内容落到文件。")


if __name__ == "__main__":
    asyncio.run(main())
