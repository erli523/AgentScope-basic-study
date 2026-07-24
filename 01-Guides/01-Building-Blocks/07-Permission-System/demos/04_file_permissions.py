"""Demo 04：检查工作目录、文件 allow rule 与危险路径保护；不写文件。"""

from __future__ import annotations

import asyncio
from pathlib import Path

from agentscope.permission import (
    AdditionalWorkingDirectory,
    PermissionBehavior,
    PermissionContext,
    PermissionEngine,
    PermissionMode,
    PermissionRule,
)
from agentscope.tool import Read, Write

from _common import brief


async def main() -> None:
    project = Path(__file__).resolve().parents[4]
    normal_file = str((project / "notes" / "demo.md").resolve())
    sensitive_file = str((project / ".env").resolve())
    outside_file = str((project.parent / "outside-demo.md").resolve())

    context = PermissionContext(
        mode=PermissionMode.ACCEPT_EDITS,
        working_directories={
            str(project): AdditionalWorkingDirectory(
                path=str(project),
                source="demo",
            ),
        },
        allow_rules={
            "Read": [
                PermissionRule(
                    tool_name="Read",
                    rule_content=str(project / "**"),
                    behavior=PermissionBehavior.ALLOW,
                    source="demo",
                ),
            ],
        },
    )
    engine = PermissionEngine(context)

    cases = [
        (Read(), {"file_path": normal_file}, "读取项目文件"),
        (Write(), {"file_path": normal_file, "content": "demo"}, "写入工作目录"),
        (Write(), {"file_path": outside_file, "content": "demo"}, "写入目录外"),
        (Write(), {"file_path": sensitive_file, "content": "demo"}, "写入 .env"),
    ]

    print("以下只进行权限判断，不会读取或写入文件。\n")
    for tool, tool_input, label in cases:
        decision = await engine.check_permission(tool, tool_input)
        print(f"{label:<14} path={tool_input['file_path']}\n  -> {brief(decision)}")

    print("\n工作目录内普通编辑可放行；目录外操作和敏感文件仍需要确认。")


if __name__ == "__main__":
    asyncio.run(main())
