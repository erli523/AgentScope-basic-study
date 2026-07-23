"""Demo 02：继承 ToolBase 编写并独立测试只读工具。"""

from __future__ import annotations

import asyncio
import json

from agentscope.message import TextBlock
from agentscope.permission import PermissionBehavior, PermissionContext, PermissionDecision
from agentscope.tool import ToolBase, ToolChunk

from _common import chunk_text, collect_direct_tool


class LookupChapter(ToolBase):
    name = "lookup_chapter"
    description = "按编号查询 AgentScope 学习手册章节名称。"
    input_schema = {
        "type": "object",
        "properties": {
            "chapter": {
                "type": "integer",
                "minimum": 1,
                "maximum": 11,
                "description": "Building Blocks 章节编号，1 到 11",
            },
        },
        "required": ["chapter"],
    }
    is_concurrency_safe = True
    is_read_only = True

    CHAPTERS = {1: "Message-Event", 2: "Agent", 3: "Model", 5: "Tool"}

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW,
            message="本地只读章节查询",
        )

    async def call(self, chapter: int) -> ToolChunk:
        result = {
            "chapter": chapter,
            "name": self.CHAPTERS.get(chapter, "尚未录入"),
        }
        return ToolChunk(content=[TextBlock(text=json.dumps(result, ensure_ascii=False))])


async def main() -> None:
    tool = LookupChapter()
    decision = await tool.check_permissions({"chapter": 5}, PermissionContext())
    chunks = await collect_direct_tool(tool, chapter=5)

    print("name        :", tool.name)
    print("description :", tool.description)
    print("read_only   :", tool.is_read_only)
    print("permission  :", decision.behavior, decision.message)
    print("result      :", chunk_text(chunks[-1]))

    print("\n直接调用适合工具单元测试；在 Agent 中还会经过 Toolkit、权限和事件链。")


if __name__ == "__main__":
    asyncio.run(main())

