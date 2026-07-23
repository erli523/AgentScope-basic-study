"""Demo 06：根据本次输入动态判断只读性和权限。"""

from __future__ import annotations

import asyncio

from agentscope.message import TextBlock
from agentscope.permission import PermissionBehavior, PermissionContext, PermissionDecision
from agentscope.tool import ToolBase, ToolChunk


class CampusDeviceAction(ToolBase):
    name = "campus_device_action"
    description = "查询设备状态，或对设备执行重启/停用操作。"
    input_schema = {
        "type": "object",
        "properties": {
            "device_id": {"type": "string"},
            "action": {"type": "string", "enum": ["query", "restart", "disable"]},
        },
        "required": ["device_id", "action"],
    }
    is_concurrency_safe = False
    is_read_only = False  # 工具整体可能写；单次是否只读由输入决定

    async def check_read_only(self, tool_input: dict) -> bool:
        return tool_input.get("action") == "query"

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        action = tool_input.get("action")
        if action == "query":
            return PermissionDecision(PermissionBehavior.ALLOW, "查询操作只读")
        if action == "restart":
            return PermissionDecision(PermissionBehavior.ASK, "设备重启需要人工确认")
        return PermissionDecision(
            PermissionBehavior.DENY,
            "学习环境禁止停用设备",
            bypass_immune=True,
        )

    async def call(self, device_id: str, action: str) -> ToolChunk:
        return ToolChunk(content=[TextBlock(text=f"{device_id}: {action} 已执行")])


async def main() -> None:
    tool = CampusDeviceAction()
    context = PermissionContext()

    for action in ("query", "restart", "disable"):
        input_data = {"device_id": "CAM-EAST-01", "action": action}
        read_only = await tool.check_read_only(input_data)
        decision = await tool.check_permissions(input_data, context)
        print(
            f"action={action:<7} read_only={str(read_only):<5} "
            f"decision={decision.behavior} bypass_immune={decision.bypass_immune} "
            f"reason={decision.message}",
        )

    print("\n不要在本例中直接调用 disable；权限判断和执行必须保持为两个明确阶段。")


if __name__ == "__main__":
    asyncio.run(main())

