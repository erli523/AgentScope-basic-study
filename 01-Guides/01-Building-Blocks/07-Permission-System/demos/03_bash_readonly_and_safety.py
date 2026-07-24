"""Demo 03：只分析 Bash 命令权限，不执行任何命令。"""

from __future__ import annotations

import asyncio

from agentscope.permission import PermissionContext, PermissionEngine, PermissionMode
from agentscope.tool import Bash

from _common import brief


async def main() -> None:
    bash = Bash()
    engine = PermissionEngine(PermissionContext(mode=PermissionMode.DEFAULT))
    commands = [
        "git status",
        "cat README.md | grep AgentScope",
        "echo hello > output.txt",
        "rm -rf /",
        "echo $(whoami)",
    ]

    print("注意：以下命令只做静态权限分析，不会执行。\n")
    for command in commands:
        read_only = await bash.check_read_only({"command": command})
        decision = await engine.check_permission(bash, {"command": command})
        print(f"{command:<38} read_only={str(read_only):<5} -> {brief(decision)}")

    print("\n重定向会失去只读属性；动态命令结构和危险删除会触发 ASK。")


if __name__ == "__main__":
    asyncio.run(main())

