"""Demo 05：生成建议规则，并模拟用户接受后加入 PermissionEngine。"""

from __future__ import annotations

import asyncio

from agentscope.permission import PermissionContext, PermissionEngine, PermissionMode
from agentscope.tool import Bash, Write

from _common import brief


async def demo_tool(tool, tool_input: dict) -> None:
    engine = PermissionEngine(PermissionContext(mode=PermissionMode.DEFAULT))
    before = await engine.check_permission(tool, tool_input)
    suggestions = tool.generate_suggestions(tool_input)

    print(f"\n=== {tool.name} ===")
    print("首次判断:", brief(before))
    print("建议规则:")
    for suggestion in suggestions:
        print(" ", suggestion.model_dump())

    # 模拟用户明确点击“以后允许此类调用”，不是自动接受。
    if suggestions:
        engine.add_rule(suggestions[0])
        after = await engine.check_permission(tool, tool_input)
        print("接受规则后:", brief(after))


async def main() -> None:
    await demo_tool(Bash(), {"command": 'git commit -m "docs"'})
    await demo_tool(
        Write(),
        {"file_path": "/project/docs/plan.md", "content": "demo"},
    )
    print("\n真实 UI 必须先展示建议范围，只有用户接受后才能持久化规则。")


if __name__ == "__main__":
    asyncio.run(main())

