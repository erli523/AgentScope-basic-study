"""Demo 03：TaskUpdate 自动维护双向依赖，并在删除时清理引用。"""

from __future__ import annotations

import asyncio

from agentscope.state import AgentState
from agentscope.tool import TaskCreate, TaskList, TaskUpdate, Toolkit

from _common import call_task_tool, print_tasks, response_text


async def main() -> None:
    state = AgentState()
    toolkit = Toolkit(tools=[TaskCreate(), TaskList(), TaskUpdate()])

    for subject in ("查询设备状态", "创建维修工单", "执行结果复检"):
        await call_task_tool(
            toolkit,
            state,
            "TaskCreate",
            {"subject": subject, "description": f"完成：{subject}"},
        )

    # 2 依赖 1；3 依赖 2。工具会同步维护反向 blocks 边。
    await call_task_tool(
        toolkit,
        state,
        "TaskUpdate",
        {"task_id": "2", "add_blocked_by": ["1"]},
    )
    await call_task_tool(
        toolkit,
        state,
        "TaskUpdate",
        {"task_id": "3", "add_blocked_by": ["2"]},
    )
    print_tasks(state, "建立依赖后")

    result = await call_task_tool(toolkit, state, "TaskList", {})
    print("\nTaskList 会标记未解决阻塞：\n", response_text(result))

    # 删除任务 2 后，1.blocks 与 3.blocked_by 中的 "2" 都应被清理。
    await call_task_tool(
        toolkit,
        state,
        "TaskUpdate",
        {"task_id": "2", "status": "deleted"},
    )
    print_tasks(state, "删除任务 2 后")
    print("\n验证：任务 2 已硬删除，其他任务对 ID=2 的依赖引用已清理。")


if __name__ == "__main__":
    asyncio.run(main())

