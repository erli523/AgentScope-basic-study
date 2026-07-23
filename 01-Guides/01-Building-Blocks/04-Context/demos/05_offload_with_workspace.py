"""Demo 05：Offload —— LocalWorkspace 持久化被压缩/截断的内容（需要 API）。

学习目标：
1. offloader 实现 offload_context / offload_tool_result；
2. LocalWorkspace 按 session_id 写入 sessions/{id}/；
3. 无 offloader 时，移出窗口的内容直接丢弃。

本示例优先演示「压缩后的 context offload」；若供应商压缩失败，
会退化为工具截断 offload（同样会写 tool_result-*.txt）。
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentscope.agent import ContextConfig
from agentscope.message import AssistantMsg, TextBlock, UserMsg
from agentscope.permission import (
    PermissionBehavior,
    PermissionContext,
    PermissionDecision,
)
from agentscope.tool import Toolkit, ToolBase, ToolChunk

from _common import (
    build_agent,
    estimate_tokens,
    make_workspace,
    print_context_snapshot,
)


class DumpReport(ToolBase):
    name = "dump_report"
    description = "返回很长的模拟报告。"
    input_schema = {
        "type": "object",
        "properties": {"topic": {"type": "string"}},
        "required": ["topic"],
    }
    is_concurrency_safe = True
    is_read_only = True

    async def check_permissions(
        self,
        tool_input: dict,
        context: PermissionContext,
    ) -> PermissionDecision:
        return PermissionDecision(
            behavior=PermissionBehavior.ALLOW,
            message="allow",
        )

    async def call(self, topic: str) -> ToolChunk:
        payload = {
            "topic": topic,
            "blob": ("OFFLOAD_BODY_" + topic + "_") * 400,
        }
        return ToolChunk(
            content=[TextBlock(text=json.dumps(payload, ensure_ascii=False))],
        )


def _list_session_files(workdir: Path, session_id: str) -> list[Path]:
    session_dir = workdir / "sessions" / session_id
    if not session_dir.is_dir():
        return []
    return sorted(p for p in session_dir.rglob("*") if p.is_file())


async def main() -> None:
    workspace = await make_workspace("05_offload")
    workdir = Path(workspace.workdir)
    print(f"workspace workdir: {workdir}")

    cfg = ContextConfig(
        trigger_ratio=0.55,
        reserve_ratio=0.12,
        tool_result_limit=100,
    )
    agent = build_agent(
        context_config=cfg,
        context_size=2500,
        offloader=workspace,
        toolkit=Toolkit(tools=[DumpReport()]),
        system_prompt="你是助教。长报告问题必须先调用 dump_report。",
        max_iters=6,
    )

    # 1) 尝试用压缩触发 offload_context → context.jsonl
    filler = "保留事实：仓库名=AgentScope-basic-study；章节=04-Context。"
    for i in range(8):
        await agent.observe(
            [
                UserMsg(
                    name="user",
                    content=f"[{i}] {filler} " + ("背景填充。" * 30),
                ),
                AssistantMsg(
                    name=agent.name,
                    content=f"记录-{i}。" + ("ok。" * 30),
                ),
            ],
        )

    tokens = await estimate_tokens(agent)
    print(f"estimated_tokens before compress≈{tokens}")
    try:
        await agent.compress_context()
        print("compress_context: ok")
    except Exception as exc:  # noqa: BLE001
        print(f"compress_context failed: {type(exc).__name__}: {exc}")
        print("将继续演示工具截断 offload ...")

    print_context_snapshot(agent, "压缩尝试之后")

    # 2) 工具截断 → offload_tool_result → tool_result-*.txt
    await agent.reply(
        UserMsg(name="user", content="请调用 dump_report，主题=offload-demo，并一句话总结。"),
    )

    files = _list_session_files(workdir, agent.state.session_id)
    print("\n=== session 目录落盘文件 ===")
    print(f"session_id: {agent.state.session_id}")
    if not files:
        print("(尚未发现落盘文件；请检查压缩/截断是否实际发生)")
    for path in files:
        rel = path.relative_to(workdir)
        size = path.stat().st_size
        print(f"- {rel} ({size} bytes)")
        if path.suffix in {".txt", ".jsonl"} and size < 2000:
            print("  preview:", path.read_text(encoding="utf-8")[:180].replace("\n", " "))

    print("\n=== 结论 ===")
    print("- sessions/{session_id}/context.jsonl ：被压缩消息的 offload")
    print("- sessions/{session_id}/tool_result-*.txt ：被截断工具输出的 offload")
    print("- Agent 之后可用 Read/Grep 等文件工具回查这些细节（需把文件工具挂进 Toolkit）")


if __name__ == "__main__":
    asyncio.run(main())
