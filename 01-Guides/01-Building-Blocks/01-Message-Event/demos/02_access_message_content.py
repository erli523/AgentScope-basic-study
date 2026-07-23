"""Demo 02：访问与过滤 Message 内容（无需 API Key）

学习目标：
1. get_text_content()：只取最终展示给用户的文本；
2. get_content_blocks(type)：按块类型过滤；
3. has_content_blocks(type)：判断消息里是否含某类块。

实践提示：
- 保存进上下文 / 展示给用户时，通常主要用文本与必要的工具结果；
- 不要把流式中间事件原样塞进下一轮模型输入。
"""

from __future__ import annotations

from agentscope.message import (
    AssistantMsg,
    TextBlock,
    ThinkingBlock,
    ToolCallBlock,
    ToolCallState,
    ToolResultBlock,
    ToolResultState,
)


def build_sample_msg() -> AssistantMsg:
    return AssistantMsg(
        name="Friday",
        content=[
            ThinkingBlock(thinking="超时 30 分钟，应触发督办。"),
            TextBlock(text="检测到工单超时。"),
            ToolCallBlock(
                id="tc_1",
                name="escalate_work_order",
                input='{"work_order_id": "WO-1001"}',
                state=ToolCallState.FINISHED,
            ),
            ToolResultBlock(
                id="tc_1",
                name="escalate_work_order",
                output="督办通知已发送。",
                state=ToolResultState.SUCCESS,
            ),
            TextBlock(text="已完成督办升级。"),
        ],
    )


def main() -> None:
    msg = build_sample_msg()

    print("=== 全部文本（通常用于最终回答）===")
    print(msg.get_text_content(separator="\n"))

    print("\n=== 是否包含工具调用 / 工具结果 ===")
    print("has tool_call  :", msg.has_content_blocks("tool_call"))
    print("has tool_result:", msg.has_content_blocks("tool_result"))
    print("has thinking   :", msg.has_content_blocks("thinking"))

    print("\n=== 工具调用块 ===")
    for block in msg.get_content_blocks("tool_call"):
        print(f"- name={block.name}, input={block.input}, state={block.state}")

    print("\n=== 工具结果块 ===")
    for block in msg.get_content_blocks("tool_result"):
        print(f"- name={block.name}, output={block.output!r}, state={block.state}")

    print("\n=== 思考块（通常只给前端调试，不一定给用户）===")
    for block in msg.get_content_blocks("thinking"):
        print(f"- {block.thinking}")


if __name__ == "__main__":
    main()
