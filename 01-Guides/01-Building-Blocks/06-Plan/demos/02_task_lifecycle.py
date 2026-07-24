"""Demo 02：通过 Toolkit 完成任务创建、开始、查看和完成。"""

from __future__ import annotations

import asyncio

from agentscope.state import AgentState
from agentscope.tool import TaskCreate, TaskGet, TaskList, TaskUpdate, Toolkit

from _common import call_task_tool, print_tasks, response_text


async def main() -> None:
    state = AgentState()
    toolkit = Toolkit(tools=[TaskCreate(), TaskGet(), TaskList(), TaskUpdate()])

    for subject, description in [
        ("阅读官方文档", "阅读 Plan 官方教程并提取核心概念。"),
        ("编写最小示例", "演示 TaskCreate、TaskList 和 TaskUpdate。"),
        ("验证运行结果", "运行示例并核对任务状态。"),
    ]:
        result = await call_task_tool(
            toolkit,
            state,
            "TaskCreate",
            {"subject": subject, "description": description},
        )
        print("TaskCreate:", result.state, response_text(result))

    print_tasks(state, "创建后")

    result = await call_task_tool(
        toolkit,
        state,
        "TaskUpdate",
        {"task_id": "1", "status": "in_progress", "owner": "planner"},
    )
    print("\nTaskUpdate(in_progress):", response_text(result))

    result = await call_task_tool(
        toolkit,
        state,
        "TaskGet",
        {"task_id": "1"},
    )
    print("\nTaskGet(1):\n", response_text(result))

    await call_task_tool(
        toolkit,
        state,
        "TaskUpdate",
        {"task_id": "1", "status": "completed"},
    )
    result = await call_task_tool(toolkit, state, "TaskList", {})
    print("\nTaskList:\n", response_text(result))
    print_tasks(state, "完成第一个任务后")


if __name__ == "__main__":
    asyncio.run(main())

