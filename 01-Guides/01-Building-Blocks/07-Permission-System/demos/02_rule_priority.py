"""Demo 02：显式 Deny/Ask/Allow 规则在 BYPASS 中仍有优先级。"""

from __future__ import annotations

import asyncio

from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionEngine,
    PermissionMode,
    PermissionRule,
)
from agentscope.tool import Bash

from _common import brief


def rule(pattern: str, behavior: PermissionBehavior) -> PermissionRule:
    return PermissionRule(
        tool_name="Bash",
        rule_content=pattern,
        behavior=behavior,
        source="demo",
    )


async def main() -> None:
    context = PermissionContext(
        mode=PermissionMode.BYPASS,
        deny_rules={"Bash": [rule("rm:*", PermissionBehavior.DENY)]},
        ask_rules={"Bash": [rule("git push:*", PermissionBehavior.ASK)]},
        allow_rules={"Bash": [rule("npm run:*", PermissionBehavior.ALLOW)]},
    )
    engine = PermissionEngine(context)
    bash = Bash()

    commands = [
        "rm demo.txt",
        "git push origin main",
        "npm run test",
        "echo hello",
    ]
    for command in commands:
        decision = await engine.check_permission(bash, {"command": command})
        print(f"{command:<25} -> {brief(decision)}")

    print("\n即使 mode=BYPASS，显式 deny 与 ask 规则仍然有效。")


if __name__ == "__main__":
    asyncio.run(main())

