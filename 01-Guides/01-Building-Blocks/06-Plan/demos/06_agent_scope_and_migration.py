"""Demo 06：两个 AgentState 默认不共享任务，并演示显式计划迁移。"""

from __future__ import annotations

from agentscope.state import AgentState, Task, TaskContext

from _common import print_tasks


def main() -> None:
    manager_state = AgentState()
    worker_state = AgentState()

    manager_state.tasks_context.tasks.append(
        # 显式提供当前 2.0.3 必需的 metadata。
        Task(
            id="1",
            subject="分派复检任务",
            description="把复检任务交给 worker-agent。",
            metadata={"owner_role": "manager"},
        ),
    )

    print_tasks(manager_state, "Manager 的计划")
    print_tasks(worker_state, "Worker 的计划（默认为空）")

    # 显式复制，而不是让两个 Agent 引用同一个可变 TaskContext。
    worker_state.tasks_context = TaskContext.model_validate(
        manager_state.tasks_context.model_dump(),
    )
    worker_state.tasks_context.tasks[0].owner = "worker-agent"

    print_tasks(worker_state, "迁移给 Worker 后")
    print_tasks(manager_state, "Manager 仍保持自己的副本")
    print("\n多 Agent 共享计划需要显式协议；复制状态也不等于自动同步后续更新。")


if __name__ == "__main__":
    main()
