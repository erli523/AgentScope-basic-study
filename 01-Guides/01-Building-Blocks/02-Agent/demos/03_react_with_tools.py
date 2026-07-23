"""Demo 03：带工具的 ReAct —— 看清「推理 → 行动 → 再推理」

学习目标：
1. Agent 在一轮 reply 内可能多次调用模型；
2. 工具结果会回填，再进入下一轮推理；
3. 最终 Msg 会同时包含 tool_call / tool_result / text。
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.event import (
    ModelCallStartEvent,
    ReplyEndEvent,
    ReplyStartEvent,
    ToolCallStartEvent,
    ToolResultEndEvent,
)
from agentscope.message import AssistantMsg, TextBlock, UserMsg
from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
)
from agentscope.tool import Toolkit, ToolBase, ToolChunk

from _common import build_agent, print_msg_summary


class LookupTerm(ToolBase):
    name = "lookup_term"
    description = "查询 AgentScope 术语的简短解释。"
    input_schema = {
        "type": "object",
        "properties": {
            "term": {
                "type": "string",
                "description": "术语，例如 Agent / Message / Event / Toolkit",
            },
        },
        "required": ["term"],
    }
    is_concurrency_safe = True
    is_read_only = True

    GLOSSARY = {
        "agent": "无状态的推理-行动循环引擎，负责调模型、调工具并产出消息/事件。",
        "message": "完整会话单元，用于上下文持久化与消息气泡渲染。",
        "event": "流式增量单元，用于 SSE、UI 与人工介入。",
        "toolkit": "工具集合管理器，向模型暴露可用能力并执行 tool call。",
    }

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW,
            message="只读术语查询",
        )

    async def call(self, term: str) -> ToolChunk:
        key = term.strip().lower()
        text = self.GLOSSARY.get(key, f"未收录术语：{term}")
        return ToolChunk(
            content=[TextBlock(text=json.dumps({"term": term, "explain": text}, ensure_ascii=False))],
        )
# check_permissions
# 必须
# @abstractmethod，不写类都实例化不了
# call
# 普通工具必须覆盖
# 基类默认会 raise NotImplementedError；只有 is_external_tool=True 的外部工具可以不实现真正执行逻辑
# 当一个模型发出tool_call的时候 
# 我们需要审核 也就是 check_permissions 来决定是否允许调用
# 如果允许 则调用 call 方法
# 如果不允许 则抛出 PermissionError

# call 方法 返回一个 ToolChunk 对象
# ToolChunk 对象 包含一个 content 列表
# content 列表 包含一个 TextBlock 对象
# TextBlock 对象 包含一个 text 字段
# text 字段 包含一个字符串


async def main() -> None:
    agent = build_agent(
        name="Tutor",
        system_prompt=(
            "你是 AgentScope 助教。"
            "回答术语问题前，必须先调用 lookup_term 工具查询，"
            "再基于工具结果用一句话总结。"
        ),

# 这里有一些超纲 ，首先就是这里 使用了 工具 工具相关的内容 其实在 05 model之中 
# 这里 tool=Toolkit(tools=[])
#    tools=[Bash(), Read(), Write(), Edit()],
        toolkit=Toolkit(tools=[LookupTerm()]),
        max_iters=6,
    )

    timeline: list[str] = []
    msg: AssistantMsg | None = None

    async for event in agent.reply_stream(
        UserMsg(name="user", content="请解释 Agent 在 AgentScope 里是什么。"),
    ):
        if isinstance(event, ReplyStartEvent):
            msg = AssistantMsg(name=event.name, content=[], id=event.reply_id)
            timeline.append("ReplyStart")
        elif isinstance(event, ModelCallStartEvent):
            timeline.append(f"ModelCall({event.model_name})")
        elif isinstance(event, ToolCallStartEvent):
            timeline.append(f"ToolCall({event.tool_call_name})")
        elif isinstance(event, ToolResultEndEvent):
            timeline.append(f"ToolResult({event.state})")
        elif isinstance(event, ReplyEndEvent):
            timeline.append("ReplyEnd")

        if msg is not None:
            msg.append_event(event)

    print("=== ReAct 时间线 ===")
    for i, item in enumerate(timeline, 1):
        print(f"{i:02d}. {item}")

    if msg is not None:
        print_msg_summary(msg)
        print("tool_calls :", [b.name for b in msg.get_content_blocks("tool_call")])
        print("tool_results:", [b.name for b in msg.get_content_blocks("tool_result")])


if __name__ == "__main__":
    asyncio.run(main())


# === ReAct 时间线 ===
# 01. ReplyStart
# 02. ModelCall(deepseek-v4-flash)
# 03. ToolCall(lookup_term)
# 04. ToolResult(success)
# 05. ModelCall(deepseek-v4-flash)
# 06. ReplyEnd

# === Msg 摘要 ===
# role/name : assistant/Tutor
# id        : a2f9825443ec44869d1eb5e3325a6b8c
# text      : '在 AgentScope 中，**Agent** 是一个无状态的推理-行动循环引擎，负责调用模型、调用工具并产出消息或事件。'
# blocks    : ['thinking', 'tool_call', 'tool_result', 'thinking', 'text']
# usage     : input_tokens=773 output_tokens=116
# tool_calls : ['lookup_term']
# tool_results: ['lookup_term']