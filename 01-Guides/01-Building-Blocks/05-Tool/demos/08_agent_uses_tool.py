"""Demo 08：让 Agent 在 ReAct 循环中真实调用自定义工具（需要 API Key）。"""

from __future__ import annotations

import asyncio
import json

from agentscope.event import (
    ModelCallStartEvent,
    ReplyEndEvent,
    ReplyStartEvent,
    ToolCallStartEvent,
    ToolResultEndEvent,
)
from agentscope.message import AssistantMsg, TextBlock, UserMsg
from agentscope.permission import PermissionBehavior, PermissionContext, PermissionDecision
from agentscope.tool import Toolkit, ToolBase, ToolChunk

from _common import build_agent, print_msg_summary


class QueryDeviceStatus(ToolBase):
    name = "query_device_status"
    description = "按设备 ID 查询校园摄像头的当前状态和连续离线分钟数。"
    input_schema = {
        "type": "object",
        "properties": {
            "device_id": {
                "type": "string",
                "description": "摄像头 ID，例如 CAM-EAST-01",
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
        return PermissionDecision(PermissionBehavior.ALLOW, "只读设备查询")

    async def call(self, device_id: str) -> ToolChunk:
        data = {"device_id": device_id, "status": "offline", "offline_minutes": 18}
        return ToolChunk(content=[TextBlock(text=json.dumps(data, ensure_ascii=False))])


async def main() -> None:
    agent = build_agent(
        name="DeviceTutor",
        system_prompt=(
            "你是校园安防助教。回答设备状态前必须调用 query_device_status；"
            "离线超过 15 分钟时建议派单。最终只回答两句话。"
        ),
        toolkit=Toolkit(tools=[QueryDeviceStatus()]),
        max_iters=5,
    )

    rebuilt: AssistantMsg | None = None
    timeline: list[str] = []
    async for event in agent.reply_stream(
        UserMsg(name="user", content="CAM-EAST-01 当前是否需要派单？"),
    ):
        if isinstance(event, ReplyStartEvent):
            rebuilt = AssistantMsg(name=event.name, content=[], id=event.reply_id)
            timeline.append("ReplyStart")
        elif isinstance(event, ModelCallStartEvent):
            timeline.append(f"ModelCall({event.model_name})")
        elif isinstance(event, ToolCallStartEvent):
            timeline.append(f"ToolCall({event.tool_call_name})")
        elif isinstance(event, ToolResultEndEvent):
            timeline.append(f"ToolResult({event.state})")
        elif isinstance(event, ReplyEndEvent):
            timeline.append("ReplyEnd")

        if rebuilt is not None:
            rebuilt.append_event(event)

    print("=== 时间线 ===")
    for index, item in enumerate(timeline, 1):
        print(f"{index:02d}. {item}")
    if rebuilt is not None:
        print_msg_summary(rebuilt, "包含工具调用的最终消息")


if __name__ == "__main__":
    asyncio.run(main())
