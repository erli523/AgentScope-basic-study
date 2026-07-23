"""Demo 01：注册内置工具并查看暴露给 LLM 的 JSON Schema。"""

from __future__ import annotations

import asyncio
import json

from agentscope.tool import Bash, Edit, Glob, Grep, Read, Toolkit, Write


async def main() -> None:
    toolkit = Toolkit(
        tools=[Bash(), Read(), Write(), Edit(), Glob(), Grep()],
    )
    schemas = await toolkit.get_tool_schemas()

    print("=== Toolkit 暴露的工具 ===")
    for schema in schemas:
        function = schema["function"]
        parameters = function["parameters"]
        print(
            f"- {function['name']:<8} required={parameters.get('required', [])} "
            f"description={function.get('description', '')[:45]!r}",
        )

    print("\n=== Read 的完整 Schema ===")
    read_schema = next(item for item in schemas if item["function"]["name"] == "Read")
    print(json.dumps(read_schema, ensure_ascii=False, indent=2))

    print("\n工具 Schema 是发给模型的能力说明；创建 Toolkit 并不会执行这些工具。")


if __name__ == "__main__":
    asyncio.run(main())

