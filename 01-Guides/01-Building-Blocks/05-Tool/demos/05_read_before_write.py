"""Demo 05：验证内置文件工具的“先读后写”。

所有操作都发生在 TemporaryDirectory 中，脚本结束后自动清理。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from agentscope.state import AgentState
from agentscope.tool import Edit, Read, Write

from _common import chunk_text


async def main() -> None:
    state = AgentState()
    read = Read()
    write = Write()
    edit = Edit()

    with TemporaryDirectory(prefix="agentscope-tool-demo-") as temp_dir:
        target = Path(temp_dir) / "note.txt"
        target.write_text("AgentScope Tool\n", encoding="utf-8")
        absolute = str(target.resolve())

        print("=== 1. 未读取就覆写已有文件：预期失败 ===")
        result = await write.call(absolute, "被盲目覆盖", _agent_state=state)
        print(result.state, chunk_text(result))

        print("\n=== 2. Read 将当前内容写入 tool_context 缓存 ===")
        result = await read.call(absolute, _agent_state=state)
        print(result.state, chunk_text(result))

        print("\n=== 3. 读取后 Edit：预期成功 ===")
        result = await edit.call(
            absolute,
            old_string="AgentScope Tool",
            new_string="AgentScope ToolBase / Toolkit",
            _agent_state=state,
        )
        print(result.state, chunk_text(result))

        print("\n最终文件内容:", target.read_text(encoding="utf-8").strip())

    print("\n本例直接调用 call()，用于展示缓存规则；正式执行还必须经过权限与 Workspace。")


if __name__ == "__main__":
    asyncio.run(main())

