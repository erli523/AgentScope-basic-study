"""Demo 03：用 FunctionTool 包装普通 Python 函数。"""

import asyncio
import json
from typing import Literal

from agentscope.permission import PermissionContext
from agentscope.tool import FunctionTool, Toolkit

from _common import chunk_text, collect_direct_tool


def estimate_alert_priority(
    offline_minutes: int,
    area: Literal["normal", "important"] = "normal",
) -> dict:
    """根据设备离线时间和区域级别估算告警优先级。

    Args:
        offline_minutes: 设备连续离线分钟数，必须大于等于 0。
        area: 区域类型，normal 为普通区域，important 为重点区域。
    """
    if offline_minutes < 0:
        raise ValueError("offline_minutes 不能为负数")
    high = area == "important" or offline_minutes >= 30
    return {"priority": "high" if high else "normal", "offline_minutes": offline_minutes}


async def main() -> None:
    tool = FunctionTool(
        estimate_alert_priority,
        is_read_only=True,
    )
    toolkit = Toolkit(tools=[tool])
    schema = (await toolkit.get_tool_schemas())[0]
    decision = await tool.check_permissions(
        {"offline_minutes": 35, "area": "normal"},
        PermissionContext(),
    )
    chunks = await collect_direct_tool(
        tool,
        offline_minutes=35,
        area="normal",
    )

    print("=== 自动推导的 Schema ===")
    print(json.dumps(schema, ensure_ascii=False, indent=2))
    print("\n默认权限行为:", decision.behavior, "（FunctionTool 默认要求确认）")
    print("执行结果      :", chunk_text(chunks[-1]))


if __name__ == "__main__":
    asyncio.run(main())
