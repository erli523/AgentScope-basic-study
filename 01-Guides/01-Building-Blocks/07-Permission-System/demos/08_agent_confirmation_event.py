"""Demo 08：Agent 遇到 ASK 时产生 RequireUserConfirmEvent（需要 API Key）。

本例只观察确认请求，不自动批准，也不执行重启动作。
"""

from __future__ import annotations

import asyncio

from agentscope.event import RequireUserConfirmEvent
from agentscope.message import TextBlock, UserMsg
from agentscope.permission import PermissionBehavior, PermissionContext, PermissionDecision
from agentscope.tool import Toolkit, ToolBase, ToolChunk

from _common import build_agent


class RestartDevice(ToolBase):
    name = "restart_device"
    description = "重启指定校园摄像头。用户明确要求重启时使用。"
    input_schema = {
        "type": "object",
        "properties": {"device_id": {"type": "string"}},
        "required": ["device_id"],
    }
    is_read_only = False
    is_concurrency_safe = False

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        return PermissionDecision(
            PermissionBehavior.ASK,
            f"重启设备 {tool_input.get('device_id')} 需要用户确认",
        )

    async def call(self, device_id: str) -> ToolChunk:
        # 本 Demo 不会确认，因此此方法不应被执行。
        return ToolChunk(content=[TextBlock(text=f"设备 {device_id} 已重启")])


async def main() -> None:
    agent = build_agent(
        name="SafeOperator",
        system_prompt="你是设备运维助手。用户要求重启时必须调用 restart_device。",
        toolkit=Toolkit(tools=[RestartDevice()]),
        max_iters=4,
        bypass_permission=False,
    )

    saw_confirmation = False
    async for event in agent.reply_stream(
        UserMsg(name="user", content="请重启摄像头 CAM-EAST-01。"),
    ):
        if isinstance(event, RequireUserConfirmEvent):
            saw_confirmation = True
            print("=== RequireUserConfirmEvent ===")
            for call in event.tool_calls:
                print("tool :", call.name)
                print("input:", call.input)
                print("state:", call.state)
                print("suggested_rules:", call.suggested_rules)

    print("\n是否收到确认事件:", saw_confirmation)
    print("脚本没有发送 UserConfirmResultEvent，因此不会执行 restart_device。")


if __name__ == "__main__":
    asyncio.run(main())

