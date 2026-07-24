"""Demo 01：查看四个计划工具的 Schema、权限与状态注入属性。"""

from __future__ import annotations

import asyncio
import json

from agentscope.permission import PermissionContext
from agentscope.tool import TaskCreate, TaskGet, TaskList, TaskUpdate, Toolkit


async def main() -> None:
    tools = [TaskCreate(), TaskGet(), TaskList(), TaskUpdate()]
    toolkit = Toolkit(tools=tools)
    schemas = await toolkit.get_tool_schemas()

    print("=== 计划工具 ===")
    for tool, schema in zip(tools, schemas, strict=True):
        function = schema["function"]
        decision = await tool.check_permissions({}, PermissionContext())
        print(
            f"- {tool.name:<10} read_only={str(tool.is_read_only):<5} "
            f"state_injected={str(tool.is_state_injected):<5} "
            f"permission={decision.behavior} "
            f"required={function['parameters'].get('required', [])}",
        )

    update_schema = next(
        item for item in schemas if item["function"]["name"] == "TaskUpdate"
    )
    print("\n=== TaskUpdate Schema ===")
    print(json.dumps(update_schema, ensure_ascii=False, indent=2))
    print("\n注意：工具输入参数叫 status，Task 对象内部字段叫 state。")


if __name__ == "__main__":
    asyncio.run(main())

