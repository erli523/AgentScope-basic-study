"""Demo 01：创建 Message 与 Content Block（无需 API Key）

学习目标：
1. UserMsg / AssistantMsg / SystemMsg 分别对应什么角色；
2. content 可以是字符串，也可以是内容块列表；
3. 助手消息可包含思考、工具调用、工具结果等多种块。
"""

from __future__ import annotations

from agentscope.message import (
    AssistantMsg,
    SystemMsg,
    TextBlock,
    ThinkingBlock,
    ToolCallBlock,
    ToolCallState,
    ToolResultBlock,
    ToolResultState,
    UserMsg,
)


def main() -> None:
    # 1) 最常见：字符串会自动包装成 TextBlock
    user_msg = UserMsg(name="user", content="校园东门摄像头离线了，帮我判断是否需要派单。")
    system_msg = SystemMsg(name="system", content="你是校园安防派单助手。")
    assistant_msg = AssistantMsg(name="Friday", content="收到，我先核对设备状态。")

    print("=== 基础消息 ===")
    for msg in (user_msg, system_msg, assistant_msg):
        print(
            f"role={msg.role:<9} name={msg.name:<8} "
            f"id={msg.id[:8]}... text={msg.get_text_content()!r}"
        )

    # 2) 显式内容块：更贴近真实 Agent 回复（思考 → 文本 → 工具调用 → 工具结果）
    rich_assistant = AssistantMsg(
        name="Friday",
        content=[
            ThinkingBlock(thinking="先查设备状态，再决定是人工确认还是直接派单。"),
            TextBlock(text="我先查询设备状态。"),
            ToolCallBlock(
                id="tool_call_1",
                name="query_device_status",
                input='{"device_id": "CAM-EAST-01"}',
                state=ToolCallState.FINISHED,
            ),
            ToolResultBlock(
                id="tool_call_1",
                name="query_device_status",
                output="设备离线，持续 18 分钟。",
                state=ToolResultState.SUCCESS,
            ),
            TextBlock(text="设备已离线超过 15 分钟，建议直接派单。"),
        ],
    )

    print("\n=== 富内容助手消息（按块打印）===")
    for block in rich_assistant.content:
        block_type = getattr(block, "type", type(block).__name__)
        print(f"- {block_type}: {block.model_dump(exclude_none=True)}")

    # 3) 角色约束：user 消息不能放 ToolCallBlock
    print("\n=== 角色约束演示 ===")
    try:
        UserMsg(
            name="user",
            content=[
                TextBlock(text="非法示例"),
                ToolCallBlock(
                    id="bad",
                    name="query_device_status",
                    input="{}",
                    state=ToolCallState.PENDING,
                ),
            ],
        )
    except Exception as exc:  # noqa: BLE001 - 学习示例，故意展示校验失败
        print(f"预期失败：{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
