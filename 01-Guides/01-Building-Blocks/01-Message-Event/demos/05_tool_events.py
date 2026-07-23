"""Demo 05：观察工具相关 Event 的先后顺序（需要 DASHSCOPE_API_KEY）

学习目标：
1. 模型决定调用工具时，会先出现 ToolCall* 事件，再出现 ToolResult* 事件；
2. 同一次工具调用用 tool_call_id 串联；
3. 最终文本增量通常出现在工具结果之后（ReAct：先行动，再总结）。

建议对照输出，按时间顺序勾出：
ModelCallStart → ToolCallStart/Delta/End → ToolResultStart/.../End → TextBlockDelta → ReplyEnd
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.event import (
    EventType,
    ModelCallStartEvent,
    ModelCallEndEvent,
    ReplyEndEvent,
    ReplyStartEvent,
    TextBlockDeltaEvent,
    ToolCallStartEvent,
    ToolCallEndEvent,
    ToolResultStartEvent,
    ToolResultEndEvent,
)
from agentscope.message import (
    AssistantMsg,
    TextBlock,
    UserMsg,
)
from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
)
from agentscope.tool import FunctionTool, Toolkit, ToolBase, ToolChunk

from _common import build_agent, event_brief


# ---------------------------------------------------------------------------
# 方式 A：继承 ToolBase，并显式 ALLOW（推荐用于学习示例）
# ---------------------------------------------------------------------------
class QueryDeviceStatus(ToolBase):
    name = "query_device_status"
    description = "查询校园安防设备的在线状态。"
    input_schema = {
        "type": "object",
        "properties": {
            "device_id": {
                "type": "string",
                "description": "设备编号，例如 CAM-EAST-01",
            },
        },
        "required": ["device_id"],
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
            message="只读查询，学习示例中自动放行。",
        )

    async def call(self, device_id: str) -> ToolChunk:
        payload = {
            "device_id": device_id,
            "online": False,
            "offline_minutes": 18,
            "location": "东门",
        }
        return ToolChunk(content=[TextBlock(text=json.dumps(payload, ensure_ascii=False))])


# ---------------------------------------------------------------------------
# 方式 B：FunctionTool（更轻量；默认常要人工确认，本示例配合 BYPASS）
# ---------------------------------------------------------------------------
def get_dispatch_rule(offline_minutes: int) -> str:
    """根据离线分钟数返回派单建议。

    Args:
        offline_minutes: 设备已离线的分钟数。
    """
    if offline_minutes >= 15:
        return "建议直接派单"
    return "建议先人工确认"


async def main() -> None:
    toolkit = Toolkit(
        tools=[
            QueryDeviceStatus(),
            FunctionTool(get_dispatch_rule, is_read_only=True),
        ],
    )
    agent = build_agent(
        system_prompt=(
            "你是校园安防派单助手。"
            "必须先调用 query_device_status 查询设备，"
            "再调用 get_dispatch_rule 得到建议，"
            "最后用一句话给出结论。"
        ),
        toolkit=toolkit,
    )

    user_msg = UserMsg(
        name="user",
        content="请查询设备 CAM-EAST-01，并告诉我是否需要派单。",
    )

    msg: AssistantMsg | None = None
    timeline: list[str] = []

    print("=== 事件时间线 ===\n")
    async for event in agent.reply_stream(user_msg):
        print(event_brief(event))

        if isinstance(event, ReplyStartEvent):
            msg = AssistantMsg(name=event.name, content=[], id=event.reply_id)
            timeline.append("ReplyStart")
        elif isinstance(event, ModelCallStartEvent):
            timeline.append(f"ModelCallStart({event.model_name})")
        elif isinstance(event, ModelCallEndEvent):
            timeline.append(
                f"ModelCallEnd(in={event.input_tokens}, out={event.output_tokens})",
            )
        elif isinstance(event, ToolCallStartEvent):
            timeline.append(f"ToolCallStart({event.tool_call_name})")
        elif isinstance(event, ToolCallEndEvent):
            timeline.append("ToolCallEnd")
        elif isinstance(event, ToolResultStartEvent):
            timeline.append(f"ToolResultStart({event.tool_call_name})")
        elif isinstance(event, ToolResultEndEvent):
            timeline.append(f"ToolResultEnd(state={event.state})")
        elif isinstance(event, TextBlockDeltaEvent):
            if not timeline or not timeline[-1].startswith("TextDelta"):
                timeline.append("TextDelta...")
        elif isinstance(event, ReplyEndEvent):
            timeline.append("ReplyEnd")
        elif event.type == EventType.EXCEED_MAX_ITERS:
            timeline.append("ExceedMaxIters")

        if msg is not None:
            msg.append_event(event)

    print("\n=== 压缩时间线（方便对照 ReAct）===")
    for i, item in enumerate(timeline, 1):
        print(f"{i:02d}. {item}")

    print("\n=== 重建后的消息摘要 ===")
    if msg is None:
        print("未收到 ReplyStartEvent")
        return

    print("最终文本:", msg.get_text_content())
    print("工具调用:", [b.name for b in msg.get_content_blocks("tool_call")])
    print("工具结果:", [b.name for b in msg.get_content_blocks("tool_result")])


if __name__ == "__main__":
    asyncio.run(main())
