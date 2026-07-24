"""Demo 04：在模型运行前预置任务，并验证 TaskCreate 自动分配下一个 ID。"""

from __future__ import annotations

import asyncio

from agentscope.state import AgentState, Task
from agentscope.tool import TaskCreate, Toolkit

from _common import call_task_tool, print_tasks, response_text


async def main() -> None:
    state = AgentState()
    state.tasks_context.tasks.extend(
        [
            Task(
                id="1",
                subject="读取设备告警",
                description="从告警服务获取设备离线信息。",
                metadata={"source": "workflow"},
                blocks=["2"],
            ),
            Task(
                id="2",
                subject="判断是否派单",
                description="依据离线时长和区域等级决定派单。",
                metadata={"source": "workflow"},
                blocked_by=["1"],
            ),
        ],
    )
    print_tasks(state, "预置计划")

    toolkit = Toolkit(tools=[TaskCreate()])
    result = await call_task_tool(
        toolkit,
        state,
        "TaskCreate",
        {
            "subject": "记录审计结果",
            "description": "保存本次决策依据和最终动作。",
            "metadata": {"source": "agent"},
        },
    )
    print("\nTaskCreate:", response_text(result))
    print_tasks(state, "自动追加后")
    print("\n已有最大数字 ID 为 2，因此新任务 ID 应为 3。")


if __name__ == "__main__":
    asyncio.run(main())

