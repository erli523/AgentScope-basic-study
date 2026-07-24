"""Demo 07：证明 blocked_by 是建议信息，不是强制执行锁。"""

from __future__ import annotations

import asyncio

from agentscope.state import AgentState
from agentscope.tool import TaskCreate, TaskUpdate, Toolkit

from _common import call_task_tool, print_tasks


def ready_task_ids(state: AgentState) -> list[str]:
    """应用层的一个简单就绪检查：所有 blocker 均 completed 才可执行。"""
    by_id = {task.id: task for task in state.tasks_context.tasks}
    ready: list[str] = []
    for task in state.tasks_context.tasks:
        blockers_done = all(
            blocker_id in by_id and by_id[blocker_id].state == "completed"
            for blocker_id in task.blocked_by
        )
        if task.state == "pending" and blockers_done:
            ready.append(task.id)
    return ready


async def main() -> None:
    state = AgentState()
    toolkit = Toolkit(tools=[TaskCreate(), TaskUpdate()])
    for subject in ("完成工单处理", "执行结果复检"):
        await call_task_tool(
            toolkit,
            state,
            "TaskCreate",
            {"subject": subject, "description": subject},
        )
    await call_task_tool(
        toolkit,
        state,
        "TaskUpdate",
        {"task_id": "2", "add_blocked_by": ["1"]},
    )

    print_tasks(state, "初始依赖")
    print("应用层判定可执行任务:", ready_task_ids(state))

    # 尽管 1 未完成，工具仍允许把 2 改成 in_progress。
    await call_task_tool(
        toolkit,
        state,
        "TaskUpdate",
        {"task_id": "2", "status": "in_progress"},
    )
    print_tasks(state, "强行开始被阻塞任务后")
    print("\n结论：Plan 只表达依赖；真正的业务执行层必须再次检查前置条件。")


if __name__ == "__main__":
    asyncio.run(main())

