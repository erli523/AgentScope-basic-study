"""Demo 06：学习助教 Agent（章节实践任务）

要求：
- 只回答与 AgentScope 学习相关的问题；
- 设置较小的 max_iters；
- 无关问题明确拒绝；
- 相关问题可调用术语工具后作答。
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.message import TextBlock, UserMsg
from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
)
from agentscope.tool import Toolkit, ToolBase, ToolChunk

from _common import build_agent, print_msg_summary


class ScopeFaq(ToolBase):
    name = "agentscope_faq"
    description = "查询 AgentScope 学习常见问题。"
    input_schema = {
        "type": "object",
        "properties": {
            "question_key": {
                "type": "string",
                "description": "关键词：reply / stream / max_iters / observe / toolkit",
            },
        },
        "required": ["question_key"],
    }
    is_concurrency_safe = True
    is_read_only = True

    FAQ = {
        "reply": "reply() 跑完整循环并返回最终 Msg。",
        "stream": "reply_stream() 边跑边产出 Event，适合 UI 与审计。",
        "max_iters": "react_config.max_iters 限制推理-行动轮数，防止死循环。",
        "observe": "observe() 写入上下文但不触发推理，适合注入背景或多 Agent 旁听。",
        "toolkit": "Toolkit 管理工具/MCP/Skill，并向模型暴露可调用能力。",
    }

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW,
            message="FAQ 只读",
        )

    async def call(self, question_key: str) -> ToolChunk:
        key = question_key.strip().lower()
        ans = self.FAQ.get(key, "未收录该关键词，请改问 AgentScope 相关概念。")
        return ToolChunk(
            content=[TextBlock(text=json.dumps({"key": key, "answer": ans}, ensure_ascii=False))],
        )


QUESTIONS = [
    "reply 和 reply_stream 有什么区别？",
    "今天北京天气怎么样？",  # 应拒绝
    "max_iters 有什么用？请先查 faq 再答。",
]


async def main() -> None:
    agent = build_agent(
        name="ScopeTutor",
        system_prompt=(
            "你是 AgentScope 学习助教，只能回答 AgentScope / Agent / Message / Event / Tool 相关问题。\n"
            "规则：\n"
            "1. 无关问题：直接回复「超出学习范围，请提问 AgentScope 相关内容。」\n"
            "2. 相关问题：优先调用 agentscope_faq，再基于结果用一两句话回答。\n"
            "3. 不要编造工具里没有的细节。"
        ),
        toolkit=Toolkit(tools=[ScopeFaq()]),
        max_iters=5,
    )

    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n######## 问题 {i}: {q}")
        result = await agent.reply(UserMsg(name="user", content=q))
        print_msg_summary(result, f"回答 {i}")
        tools = [b.name for b in result.get_content_blocks("tool_call")]
        if tools:
            print("调用了工具:", tools)


if __name__ == "__main__":
    asyncio.run(main())
