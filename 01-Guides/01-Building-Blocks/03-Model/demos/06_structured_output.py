"""Demo 06：用 Pydantic 模型生成并校验结构化输出。"""

from __future__ import annotations

import asyncio
import json
from typing import Literal

from agentscope.message import SystemMsg, UserMsg
from pydantic import BaseModel, Field

from _common import build_model


class ModelStudyCard(BaseModel):
    concept: str = Field(description="AgentScope Model 概念名称")
    summary: str = Field(description="一句话中文解释")
    layer: Literal["credential", "model", "agent"]
    key_points: list[str] = Field(min_length=2, max_length=4)
    risk: str = Field(description="使用时最应注意的风险")


async def main() -> None:
    model = build_model(stream=False, temperature=0.1, max_tokens=300)
    messages = [
        SystemMsg(name="system", content="你是 AgentScope 中文助教。"),
        UserMsg(
            name="user",
            content="为 ChatResponse 生成一张学习卡片，内容准确、简洁。",
        ),
    ]

    response = await model.generate_structured_output(messages, ModelStudyCard)
    # AgentScope 返回 dict；再次经过 Pydantic，执行本地类型与范围校验。
    card = ModelStudyCard.model_validate(response.content)

    print("=== 结构化结果 ===")
    print(json.dumps(card.model_dump(), ensure_ascii=False, indent=2))
    print("\nusage:", response.usage)
    print("\n结构化 JSON 只保证形状通过校验，不保证其中的业务事实天然可信。")


if __name__ == "__main__":
    asyncio.run(main())

