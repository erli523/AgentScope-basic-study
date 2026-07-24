"""Demo 05：序列化 AgentState，并恢复包含状态和依赖的计划。"""

from __future__ import annotations

import json

from agentscope.state import AgentState, Task

from _common import print_tasks


def main() -> None:
    original = AgentState()
    original.tasks_context.tasks.extend(
        [
            Task(
                id="1",
                subject="整理 Plan 笔记",
                description="总结任务生命周期。",
                state="completed",
                metadata={"source": "manual"},
                blocks=["2"],
            ),
            Task(
                id="2",
                subject="运行 Plan Demo",
                description="验证示例代码。",
                state="in_progress",
                metadata={"source": "manual"},
                blocked_by=["1"],
            ),
        ],
    )

    payload = original.model_dump_json()
    restored = AgentState.model_validate_json(payload)

    print("=== 序列化 JSON（节选）===")
    parsed = json.loads(payload)
    print(json.dumps(parsed["tasks_context"], ensure_ascii=False, indent=2))
    print_tasks(restored, "恢复后的任务")
    print("\n对象是否独立:", restored is not original)
    print("任务内容是否一致:", restored.tasks_context == original.tasks_context)


if __name__ == "__main__":
    main()

