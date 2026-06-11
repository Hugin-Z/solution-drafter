# solution-drafter

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

中文政企（toG / toB）方案文档生成框架 —— 把零散输入（聊天 / 会议纪要 / 邮件）装配成规范的政府格式 docx（需求方案 / 解决方案建议书 / 实施方案 等）。**Skill（纯文本契约）+ Python 工具链**形态：任何能读 `SKILL.md` 工作流的 LLM agent 都可驱动，下层 Python 负责把 markdown 装配成字体合规的 docx。

> 本仓库是一个**架构与工程实践的开源示范**。其中的公司 / 产品 / 项目 / 客户均为**虚构示例**，不指向任何真实主体。

## 它解决什么

政企方案文档的痛点是固定的：输入零散、输出必须规范（仿宋 / 章节结构 / 政府格式）、内容要查历史素材、同一件事换个文档类型只需套不同骨架。solution-drafter 把这件事拆成**三层解耦 + 5 阶段调度**，让"加新文档类型不动框架、换领域不动文档类型"成为可执行的契约（有测试锁定）。

## 三层解耦架构

```
┌─────────────────────────────────────────────────┐
│  L1 框架层（与文档类型 / 领域无关）              │
│  scripts/ 工具链 + system.md + 5 阶段 stages     │
│  ── 加新文档类型 / 换领域都不动这一层 ──         │
├─────────────────────────────────────────────────┤
│  L2 文档类型层（与领域无关）                     │
│  templates/<doc_type>/outline.yaml               │
│  + prompts/sections/<doc_type>/ + template.docx  │
│  需求方案 / 解决方案建议书 / 实施方案 / ...       │
├─────────────────────────────────────────────────┤
│  L3 领域插件层（可拔插 / run.py override 注入）  │
│  prompts/domain/<vendor>/ 术语 + 决策 + 合规     │
│  + 公司主体字段 / 默认空领域 / 示例虚构领域       │
└─────────────────────────────────────────────────┘
```

## 5 阶段工作流

| 阶段 | 输入 | 输出 | 用户参与 |
|---|---|---|---|
| S1 信息抽取 | 用户零散输入 | `intake.json` | 对话 ack |
| S2 资料获取 | `intake.json` + asset_needs | `assets.json` | 无（agent 用环境手段主动获取 / 手段无关 / 框架只定义 `assets.json` 契约，不提供真实素材库）|
| S3 模板填充 | `intake.json` + outline.yaml | `outline_filled.json` | 无（纯结构化映射）|
| S4 内容生成 | `outline_filled.json` + assets + prompts | `draft.md` | 无（逐 section 落盘 / 长文档不断流）|
| S5 评审修订 | `draft.md` | `final.md` + `final.docx` | 多轮对话迭代 |

阶段间用 JSON / Markdown 文件传递（不靠 context 记忆），每阶段可独立重跑。

## Quickstart

```bash
pip install -r requirements.txt          # python-docx / PyYAML / lxml / opencc

# 跑一个端到端 demo（虚构数据 → 字体合规的 docx）
python examples/demo-需求方案/run.py            # 需求方案 / 默认空领域
python examples/demo-槐序数据领域/run.py        # 接领域插件 → §公司实力由 own_* 填充

# 校验一个文档类型配置
python scripts/validate_outline.py templates/需求方案/outline.yaml --repo-root .

# 跑测试
python -m pytest -q
```

产物在 `examples/demo-*/output/`：`draft.md`（markdown 终稿）+ `<项目名>_<类型>.docx`（字体合规的政府格式 docx）。

## 怎么加一个新文档类型（不动框架）

1. 加 `templates/<doc_type>/outline.yaml`（intake_schema + outline + generation + output / 每 section 写 `asset_needs` + 注册 `s2_acquire` stage）。
2. 加 `prompts/sections/<doc_type>/<NN>.md`（每 section：anchor + intake 依赖 + CoT + 输出格式 + 素材运用 + 红线）。
3. 生成空 `template.docx`。
4. `python scripts/validate_outline.py …` 校验通过。

详见 `SKILL.md` §加新文档类型。

## 怎么接一个领域插件（不动文档类型）

在 `prompts/domain/<vendor>/` 放 4 个文件（`company-profile.md` 含 `own_*` 公司主体字段 + `glossary` / `client-logic` / `compliance`），在 run.py 内拼成 `domain_plugin` 注入（不改 outline.yaml）。`examples/demo-槐序数据领域/` 是一个完整的虚构领域活例子；对照 `demo-解决方案建议书/`（默认空领域 / 公司实力段输出【待补充】）即可看出 L3 接入前后的差异。

详见 `SKILL.md` §自定义领域插件 howto。

## 长文档不断流

LLM 单次输出有 token 上限，几万~几十万字的方案文档一口气生成会被截断。框架的做法是**逐 section 落盘**：每生成完一个 section 立即 `append_markdown` + `save`，再生成下一个；单个 section 过长再按三级标题分批。即使中途断（上下文耗尽 / 进程中断），已写入磁盘的 section 也保住。断点续写本身依赖调用方是 agentic agent，框架诚实声明只保证"逐段落盘不丢"，不保证"自动续写"。

## 仓库结构

```text
scripts/        L1 Python 工具链（docx 渲染 / 字体安全 / outline 校验）
prompts/        system / stages（L1）/ sections（L2）/ domain（L3）
templates/      各文档类型的 outline.yaml + 空 docx 母版
examples/       端到端 demo（含 1 个虚构领域 demo）
tests/          pytest（outline 校验 / demo smoke / 字体安全 / 逐段落盘）
docs/           工程方法论笔记
```

## 设计取舍

为什么这样分层、baseline 怎么锁、契约校验放哪、长文档怎么不断流 —— 这些"踩坑 → 解决"的工程笔记见 [`docs/engineering-notes.md`](docs/engineering-notes.md)。

## License

[MIT](LICENSE)
