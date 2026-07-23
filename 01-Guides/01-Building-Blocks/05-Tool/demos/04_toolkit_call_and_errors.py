"""Demo 04：使用 Toolkit.call_tool 调度工具，并观察正常/错误结果。"""

import asyncio
import json

from agentscope.message import ToolCallBlock
from agentscope.permission import PermissionContext, PermissionMode
from agentscope.state import AgentState
from agentscope.tool import FunctionTool, Toolkit, ToolResponse

from _common import chunk_text


def divide(dividend: float, divisor: float) -> dict:
    """计算两个数字相除。

    Args:
        dividend: 被除数。
        divisor: 除数，不能为 0。
    """
    if divisor == 0:
        raise ValueError("divisor 不能为 0")
    return {"result": dividend / divisor}


async def run_call(toolkit: Toolkit, state: AgentState, input_data: dict) -> None:
    call = ToolCallBlock(
        id=f"divide-{input_data['divisor']}",
        name="divide",
        input=json.dumps(input_data),
    )
    print(f"\n输入：{input_data}")
    async for item in toolkit.call_tool(call, state):
        print(
            f"- {type(item).__name__:<12} state={item.state} "
            f"text={chunk_text(item)!r}",
        )
        if isinstance(item, ToolResponse):
            print("  ↑ 最后一个对象是 Toolkit 聚合后的 ToolResponse")


async def main() -> None:
    toolkit = Toolkit(tools=[FunctionTool(divide, is_read_only=True)])
    state = AgentState(
        permission_context=PermissionContext(mode=PermissionMode.BYPASS),
    )

    await run_call(toolkit, state, {"dividend": 10, "divisor": 2})
    await run_call(toolkit, state, {"dividend": 10, "divisor": 0})

    print("\n注意：直接调用 Toolkit.call_tool 用于学习调度与聚合；完整权限流程由 Agent 驱动。")


if __name__ == "__main__":
    asyncio.run(main())
