"""Demo 06：自定义动态只读、参数级规则匹配和 safety ASK。"""

from __future__ import annotations

import asyncio
import fnmatch

from agentscope.message import TextBlock
from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
    PermissionEngine,
    PermissionMode,
    PermissionRule,
)
from agentscope.tool import ToolBase, ToolChunk

from _common import brief


class DeviceControl(ToolBase):
    name = "device_control"
    description = "查询、重启或停用校园设备。"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["get", "restart", "disable"]},
            "device_id": {"type": "string"},
        },
        "required": ["action", "device_id"],
    }
    is_read_only = False
    is_concurrency_safe = False

    async def check_read_only(self, tool_input: dict) -> bool:
        return tool_input.get("action") == "get"

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        if tool_input.get("action") == "disable":
            return PermissionDecision(PermissionBehavior.DENY, "禁止停用设备")
        if tool_input.get("action") == "restart" and str(
            tool_input.get("device_id", ""),
        ).startswith("PROD-"):
            return PermissionDecision(
                PermissionBehavior.ASK,
                "生产设备重启需要人工确认",
                decision_reason="production safety check",
                bypass_immune=True,
            )
        return PermissionDecision(PermissionBehavior.PASSTHROUGH, "继续规则判断")

    def match_rule(self, rule_content: str | None, tool_input: dict) -> bool:
        if rule_content is None:
            return True
        signature = f"{tool_input.get('action')}:{tool_input.get('device_id')}"
        return fnmatch.fnmatch(signature, rule_content)

    async def call(self, action: str, device_id: str) -> ToolChunk:
        return ToolChunk(content=[TextBlock(text=f"{action}: {device_id}")])


async def main() -> None:
    tool = DeviceControl()
    allow_restart_dev = PermissionRule(
        tool_name=tool.name,
        rule_content="restart:DEV-*",
        behavior=PermissionBehavior.ALLOW,
        source="projectSettings",
    )
    engine = PermissionEngine(
        PermissionContext(
            mode=PermissionMode.DEFAULT,
            allow_rules={tool.name: [allow_restart_dev]},
        ),
    )

    for tool_input in [
        {"action": "get", "device_id": "PROD-01"},
        {"action": "restart", "device_id": "DEV-01"},
        {"action": "restart", "device_id": "PROD-01"},
        {"action": "disable", "device_id": "DEV-01"},
    ]:
        decision = await engine.check_permission(tool, tool_input)
        print(f"{tool_input!s:<48} -> {brief(decision)}")

    print("\nDEV 重启命中 allow；PROD 重启的 safety ASK 不能被普通 allow 覆盖。")


if __name__ == "__main__":
    asyncio.run(main())

