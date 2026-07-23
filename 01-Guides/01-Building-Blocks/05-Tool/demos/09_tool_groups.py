"""Demo 09：通过 reset_tools 元工具激活 Tool Group（无需模型）。"""

import asyncio
import json

from agentscope.message import ToolCallBlock
from agentscope.state import AgentState
from agentscope.tool import FunctionTool, ToolGroup, Toolkit


def handbook_status() -> str:
    """返回学习手册状态。"""
    return "handbook ready"


def query_work_order(order_id: str) -> dict:
    """查询工单。

    Args:
        order_id: 工单 ID。
    """
    return {"order_id": order_id, "status": "processing"}


async def schema_names(toolkit: Toolkit, state: AgentState) -> list[str]:
    schemas = await toolkit.get_tool_schemas(state.tool_context.activated_groups)
    return [item["function"]["name"] for item in schemas]


async def main() -> None:
    toolkit = Toolkit(
        tools=[FunctionTool(handbook_status, is_read_only=True)],
        tool_groups=[
            ToolGroup(
                name="work_order",
                description="校园工单查询工具",
                instructions="查询前必须确认 order_id。",
                tools=[FunctionTool(query_work_order, is_read_only=True)],
            ),
        ],
    )
    state = AgentState()

    print("激活前:", await schema_names(toolkit, state))
    reset_schema = next(
        item
        for item in await toolkit.get_tool_schemas(state.tool_context.activated_groups)
        if item["function"]["name"] == "reset_tools"
    )
    print("reset_tools 参数:", json.dumps(reset_schema["function"]["parameters"], ensure_ascii=False))

    reset_call = ToolCallBlock(
        id="activate-work-order",
        name="reset_tools",
        input=json.dumps({"work_order": True}),
    )
    async for _ in toolkit.call_tool(reset_call, state):
        pass

    print("激活后:", await schema_names(toolkit, state))
    print("activated_groups:", state.tool_context.activated_groups)
    print("\nbasic 工具始终存在；额外组只有激活后才暴露给模型。")


if __name__ == "__main__":
    asyncio.run(main())
