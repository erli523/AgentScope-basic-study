"""Demo 01：比较五种 PermissionMode 对同一自定义工具的决策。"""

from __future__ import annotations

import asyncio

from agentscope.message import TextBlock
from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
    PermissionEngine,
    PermissionMode,
)
from agentscope.tool import ToolBase, ToolChunk

from _common import brief


class ResourceAction(ToolBase):
    name = "resource_action"
    description = "查询或修改学习资源。"
    input_schema = {
        "type": "object",
        "properties": {
            "operation": {"type": "string", "enum": ["get", "update", "forbidden"]},
            "target": {"type": "string"},
        },
        "required": ["operation", "target"],
    }
    is_read_only = False
    is_concurrency_safe = False

    async def check_read_only(self, tool_input: dict) -> bool:
        return tool_input.get("operation") == "get"

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        if tool_input.get("operation") == "forbidden":
            return PermissionDecision(PermissionBehavior.DENY, "工具明确禁止该操作")
        if str(tool_input.get("target", "")).startswith("prod-"):
            return PermissionDecision(
                PermissionBehavior.ASK,
                "生产资源操作需要确认",
                bypass_immune=True,
            )
        return PermissionDecision(PermissionBehavior.PASSTHROUGH, "交给规则和 Mode")

    async def call(self, operation: str, target: str) -> ToolChunk:
        return ToolChunk(content=[TextBlock(text=f"{operation}: {target}")])


async def main() -> None:
    tool = ResourceAction()
    cases = [
        {"operation": "get", "target": "dev-note"},
        {"operation": "update", "target": "dev-note"},
        {"operation": "update", "target": "prod-camera"},
        {"operation": "forbidden", "target": "dev-note"},
    ]

    for mode in PermissionMode:
        engine = PermissionEngine(PermissionContext(mode=mode))
        print(f"\n=== {mode.value} ===")
        for tool_input in cases:
            decision = await engine.check_permission(tool, tool_input)
            label = f"{tool_input['operation']} / {tool_input['target']}"
            print(f"{label:<27} -> {brief(decision)}")

    print("\nEXPLORE 只看只读性；BYPASS 会跳过 safety ASK，但工具自己的 DENY 仍生效。")


if __name__ == "__main__":
    asyncio.run(main())

