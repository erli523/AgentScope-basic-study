"""Demo 01：创建并检查 Model（不会发出模型请求）。

学习目标：
1. Credential、Model 和 Parameters 在构造阶段如何组合；
2. 配置来自根目录 .env，而不是硬编码；
3. 日志中只打印安全摘要，绝不打印 API Key。
"""

from __future__ import annotations

import json

from _common import build_model, safe_model_summary


def main() -> None:
    model = build_model(
        stream=True,
        temperature=0.2,
        max_tokens=256,
    )

    print("=== Model 安全配置摘要 ===")
    print(json.dumps(safe_model_summary(model), ensure_ascii=False, indent=2))

    print("\n=== 关键结论 ===")
    print("- 此脚本只创建客户端，不消耗模型 token。")
    print("- credential 已配置，但摘要故意不读取、不打印 API Key。")
    print("- 同一个 model 对象既可交给 Agent，也可被业务代码直接调用。")


if __name__ == "__main__":
    main()

