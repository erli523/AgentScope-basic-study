"""Demo 08：让 Agent 使用四个任务工具生成显式计划（需要 API Key）。"""

from __future__ import annotations

import asyncio

from agentscope.event import (
    ReplyEndEvent,
    ReplyStartEvent,
    ToolCallStartEvent,
    ToolResultEndEvent,
)
from agentscope.message import AssistantMsg, UserMsg
from agentscope.tool import TaskCreate, TaskGet, TaskList, TaskUpdate, Toolkit

from _common import build_agent, print_msg_summary, print_tasks


async def main() -> None:
    agent = build_agent(
        name="Planner",
        system_prompt=(
            "你是 AgentScope 学习计划助手。收到复杂学习请求后："
            "先用 TaskCreate 创建 3 个离散任务；"
            "再用 TaskUpdate 让后一个任务依赖前一个任务；"
            "最后调用 TaskList 检查计划。"
            "本轮只制定计划，不执行任务，也不要把任务标记 completed。"
        ),
        toolkit=Toolkit(
            tools=[TaskCreate(), TaskGet(), TaskList(), TaskUpdate()],
        ),
        max_iters=10,
    )

    timeline: list[str] = []
    rebuilt: AssistantMsg | None = None
    async for event in agent.reply_stream(
        UserMsg(
            name="user",
            content="规划学习 AgentScope RAG：阅读文档、编写 Demo、运行验证。",
        ),
    ):
        if isinstance(event, ReplyStartEvent):
            rebuilt = AssistantMsg(name=event.name, content=[], id=event.reply_id)
            timeline.append("ReplyStart")
        elif isinstance(event, ToolCallStartEvent):
            timeline.append(f"ToolCall({event.tool_call_name})")
        elif isinstance(event, ToolResultEndEvent):
            timeline.append(f"ToolResult({event.state})")
        elif isinstance(event, ReplyEndEvent):
            timeline.append("ReplyEnd")

        if rebuilt is not None:
            rebuilt.append_event(event)

    print("=== 计划工具时间线 ===")
    for index, item in enumerate(timeline, 1):
        print(f"{index:02d}. {item}")
    print_tasks(agent.state, "AgentState 中的最终计划")
    if rebuilt is not None:
        print_msg_summary(rebuilt, "Agent 最终回答")


if __name__ == "__main__":
    asyncio.run(main())
