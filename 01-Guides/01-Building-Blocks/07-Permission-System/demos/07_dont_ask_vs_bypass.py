"""Demo 07：比较敏感文件 safety ASK 在 DONT_ASK 与 BYPASS 下的结果。

只进行权限判断，不写入任何文件。
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionEngine,
    PermissionMode,
    PermissionRule,
)
from agentscope.tool import Write

from _common import brief


async def main() -> None:
    sensitive = str((Path.home() / ".env").resolve())
    tool_input = {"file_path": sensitive, "content": "NEVER_WRITTEN=true"}
    write = Write()

    contexts = [
        ("DEFAULT", PermissionContext(mode=PermissionMode.DEFAULT)),
        ("DONT_ASK", PermissionContext(mode=PermissionMode.DONT_ASK)),
        ("BYPASS", PermissionContext(mode=PermissionMode.BYPASS)),
        (
            "BYPASS + deny",
            PermissionContext(
                mode=PermissionMode.BYPASS,
                deny_rules={
                    "Write": [
                        PermissionRule(
                            tool_name="Write",
                            rule_content="**/.env",
                            behavior=PermissionBehavior.DENY,
                            source="demo",
                        ),
                    ],
                },
            ),
        ),
    ]

    print(f"敏感目标：{sensitive}")
    print("以下只判断权限，不执行 Write。\n")
    for label, context in contexts:
        decision = await PermissionEngine(context).check_permission(write, tool_input)
        print(f"{label:<15} -> {brief(decision)}")

    print("\n无人值守推荐 DONT_ASK；BYPASS 必须用显式 deny 规则补回护栏。")


if __name__ == "__main__":
    asyncio.run(main())

