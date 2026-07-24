# 07 Permission System（权限系统）

> 主要依据：用户提供的 AgentScope 2.0.4 官方《权限系统》教程；在线文档：[Permission System](https://docs.agentscope.io/versions/2.0.4/zh/building-blocks/permission-system)

## 本章目标

理解 AgentScope 如何在每次工具调用前综合 Rules、Permission Mode 和工具自身的运行时检查，做出 ALLOW、DENY 或 ASK 决策，并能够为只读探索、交互式开发和无人值守任务设计最小权限策略。

## 决策的三个来源

| 来源 | 作用 |
|---|---|
| Rules | 对特定工具和调用模式设置 ALLOW、DENY 或 ASK，优先级最高 |
| Mode | 为未命中规则的调用提供全局默认策略 |
| Built-in Checks | 工具根据真实参数判断只读、危险路径、命令注入等风险 |

## Demo

目录：[`demos/`](./demos/)

| 序号 | 文件 | 是否需要模型 API | 学习内容 |
|---|---|---:|---|
| 01 | `01_permission_modes.py` | 否 | 五种 Mode 的决策差异 |
| 02 | `02_rule_priority.py` | 否 | Deny、Ask、Allow 规则优先级 |
| 03 | `03_bash_readonly_and_safety.py` | 否 | Bash 只读检测、重定向和危险命令 |
| 04 | `04_file_permissions.py` | 否 | 工作目录、文件规则和危险路径 |
| 05 | `05_suggested_rules.py` | 否 | 生成、接受并持久化建议规则 |
| 06 | `06_custom_permission_tool.py` | 否 | 自定义动态只读和 safety ASK |
| 07 | `07_dont_ask_vs_bypass.py` | 否 | 无人值守模式与 BYPASS 风险 |
| 08 | `08_agent_confirmation_event.py` | 是 | Agent 的 RequireUserConfirmEvent |

## 推荐运行顺序

```bash
conda activate Scope-School
cd 01-Guides/01-Building-Blocks/07-Permission-System/demos

python 01_permission_modes.py
python 02_rule_priority.py
python 03_bash_readonly_and_safety.py
python 04_file_permissions.py
python 05_suggested_rules.py
python 06_custom_permission_tool.py
python 07_dont_ask_vs_bypass.py
python 08_agent_confirmation_event.py
```

只有 `08_agent_confirmation_event.py` 会读取根目录 `.env` 并调用模型。

## 五种 Mode

| Mode | 核心语义 | 推荐场景 |
|---|---|---|
| `DEFAULT` | 未明确允许时询问，尊重 safety ASK | 默认、最安全 |
| `EXPLORE` | 只读调用放行，修改调用拒绝 | 阅读、分析、规划 |
| `ACCEPT_EDITS` | 只读及工作目录内编辑更容易放行 | 用户在场的开发 |
| `BYPASS` | 跳过普通与 safety ASK，但仍尊重显式 deny/ask 和工具 DENY | 强隔离沙箱、完全可信环境 |
| `DONT_ASK` | 所有 ASK 转为 DENY，未明确允许的调用拒绝 | CI、定时任务、无人值守 |

## 学习重点

- 权限必须由代码执行，不能只写在 system prompt；
- deny 规则与显式 ask 规则在所有 Mode（包括 BYPASS）下生效；
- `EXPLORE` 只依据 `check_read_only()`，不会进入一般动态权限检查；
- `bypass_immune=True` 的 safety ASK 在 DEFAULT/ACCEPT_EDITS 下不能被 allow 规则覆盖；
- DONT_ASK 会把 safety ASK 转成 DENY；
- BYPASS 会跳过 safety ASK，因此危险路径必须额外配置 deny 规则；
- 复合 Bash 命令只有全部子命令只读才是只读，输出重定向一定产生副作用；
- ACCEPT_EDITS 只能自动放行配置工作目录内的文件修改；
- ASK 中的 suggested rules 只有用户明确接受后才应写入 PermissionEngine；
- 直接调用 `tool.call()` 会绕过权限系统，正式执行应由 Agent 流程驱动。

## 策略设计提示（通用）

- 只读查询：可用 `EXPLORE` 或精确 allow  
- 普通写操作：`ASK`，或明确的 allow 规则  
- 高风险操作：`ASK` / `DENY`，必要时 `bypass_immune` safety ASK  
- 无人值守：`DONT_ASK` + 精确 allow，避免无护栏的 `BYPASS`  
- 批准、拒绝、规则来源和工具参数应进入审计记录  

## 安全声明

本章 Demo 只调用 `PermissionEngine.check_permission()` 和工具的分析接口。示例中的 `rm -rf /`、`.env` 写入等字符串只用于测试决策，不会真正执行。

## 验收标准

- 能解释三类决策来源及其顺序；
- 能为五种 Mode 预测常见工具调用结果；
- 能编写 allow/deny/ask 规则并验证匹配；
- 能实现动态只读、自定义 DENY 和 safety ASK；
- 能解释为什么 BYPASS 仍需要 deny 规则；
- 能让无人值守任务做到“不询问但默认拒绝”；
- 能处理 Agent 的用户确认事件，并只持久化用户接受的建议规则。

完整总结见：[笔记.md](./笔记.md)
