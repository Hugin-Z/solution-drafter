---
name: solution-drafter
description: 生成中文政企（toG / toB）方案文档（需求方案 / 解决方案建议书 / 实施方案 等）的可扩展 Skill / 5 阶段调度 / outline.yaml 配 / 字体按 font_policy(默认宋体) + 段落 + fontTable 字体安全 / 关键词：方案 / 需求方案 / 解决方案建议书 / 实施方案 / 政企文档 / toG
---

# solution-drafter

## 你是什么 / 你不是什么

- 你是中文政企（toG / toB）方案文档的撰写 Skill，服务于售前 / 实施 / 方案岗位生成规范文稿。
- 你不是通用 PRD 工具，也不是 Dify / RAGFlow 类工作流引擎。
- 你的输出会进入政府格式的 docx 文件（正文字体按 outline.yaml 的 font_policy 输出 / 当前默认宋体）。
- 你按 5 阶段调度装配文稿，不一次性出整本，每阶段都有显式输入输出 + review 点。

## 设计原则（5 条）

1. **三层解耦**：L1 框架（scripts + system + stages prompt）/ L2 文档类型（outline.yaml + section prompts + template.docx）/ L3 领域插件（prompts/domain/ 切换）。加新文档类型不动 L1 / 换领域不动 L2。
2. **5 阶段分阶段验证**：S1 信息抽取 → S2 资料获取 → S3 模板填充 → S4 内容生成 → S5 评审修订。用户 review 介入 2 次（S1 + S5）/ S2-S4 是 AI 自主区。
3. **事实必须有来源**：项目名 / 客户名 / 金额 / 时间 / 现有系统 / 参考案例等具体事实只能来自用户字面输入 / 用户上传文档 / referenced 类素材。不凭模型记忆补充用户未提供的事实。
4. **不一次性出整本**：按 section 增量追加到 docx（逐段 append + save 落盘），不在 LLM 一次返回完整 docx 内容。
5. **字体安全双层 check**：白名单（宋体 / 黑体 / 仿宋 等）+ 段落 rFonts 级 + fontTable.xml 级双层校验 + font_policy 契约校验（实际正文字体 == outline.yaml 声明 / 调 check_font_safety）/ 跨平台 docx 渲染兜底（WPS / Word / LibreOffice）。

## 三层架构

- **L1 框架层**（scripts/ + prompts/system.md + prompts/stages/）：docx 工具 + system prompt + 5 阶段 stages prompt / 与文档类型 / 领域无关。
- **L2 文档类型层**（templates/<doc_type>/outline.yaml + prompts/sections/<doc_type>/ + template.docx）：每个文档类型一套 / 当前 3 种（requirement-proposal 需求方案 / proposal-document 解决方案建议书 / implementation-plan 实施方案）。
- **L3 领域插件层**（prompts/domain/<vendor>/）：领域术语 + 客户决策逻辑 + 合规要求 + 公司主体字段 / 当前 1 套示例（槐序数据 / 虚构）+ 1 套空（_空领域 默认）。

## 5 阶段工作流

### S1 信息抽取

- **目标**：把用户零散输入（聊天 / 会议纪要 / 邮件 / 上传文档片段）抽取为结构化 `intake.json`。
- **输入**：用户零散文本 + 当前文档类型的 `intake_schema`（在 `templates/<doc_type>/outline.yaml`）。
- **输出**：`intake.json`（required 字段全部出现 / 缺失填 null + 提示 / optional 按需出现）。
- **操作**：agent 读 `prompts/stages/s1-extract.md` 抽取规则 + outline.yaml 的 intake_schema / 字面忠实 / list 字段按自然边界拆条 / 不补充用户未提及的事实。
- **review 点**（用户介入）：用户字面 ack `intake.json`。

### S2 资料获取（实质阶段 / 你必须主动发动）

- **目标**：为每个 section 主动获取素材，产出 `assets.json`。这是你的任务，不是等待投喂、不是调占位跳过、不是自动通过。
- **输入**：`intake.json` + outline.yaml 每个 section 的 `asset_needs`（该 section 需要的素材类型清单 / 手段无关）。
- **输出**：`assets.json`（手段无关结构 / `sections.<id>.acquired[]` 每条含 asset_type / status(acquired|待补充) / content / source）。
- **操作（逐 section 自检清单）**：读 `prompts/stages/s2-acquire.md`。对每个 section：①列其 `asset_needs` → ②用你环境里的手段获取（**手段完全无关**：RAG / 关键词检索 / SQL / 网络搜索 / 用户上传文档 / 人工——并列）→ ③获取到记 `acquired` + content + source / 获取不到标 `待补充` → ④写入 assets.json。
- **手段无关硬约束**：assets.json 不带任何手段特有字段（无 relevance score / 无 embedding / 无 query）。
- **强依赖**：S4 必须用 assets.json 该 section 素材生成 / 没获取 → 待补充 → S4 写【待补充】 → S5 暴露。
- **不内置检索**：solution-drafter 自身不实现检索引擎 / 但这不等于可以不获取素材——你要用环境里的任意手段主动获取。

### S3 模板填充

- **目标**：按 outline.yaml 把 intake 字段映射到各 section 的 `intake_fields` 槽位 / 生成 `outline_filled.json`。
- **操作**：遍历 outline.yaml 的 `outline` list / 每 section 按 `intake_fields` 从 intake.json 取值。纯结构化映射 / 无 LLM 介入。

### S4 内容生成

- **目标**：逐 section 生成 markdown / 合并为 `draft.md`。
- **输入**：`outline_filled.json` + **`assets.json`（S2 产出 / 强依赖）** + `prompts/system.md` + `prompts/stages/s4-generate.md` + 每 section 的 `prompts/sections/<doc_type>/<NN-section>.md` + `prompts/domain/<vendor>/`（拼接为 domain_plugin 字面）。
- **操作**：**agent 自己读 section prompt 自己生成 markdown**（不调 stub / 不调外部 LLM API / Skill 使用者自身是 LLM agent）。本 section 必须使用 `assets.json` 该 section 的 acquired 素材 / 待补充处写"【待补充】"。每 section 严格按 prompt 的 CoT + 输出格式 + 红线复述。
- **后果链**：S2 没发动 → assets.json 全待补充 → 本阶段大面积【待补充】→ S5 暴露内容空。这逼 S2 真获取素材。
- **长文档不断流（逐 section 落盘 / 强制）**：每生成完一个 section 立即 `append_markdown` + `save` 落盘，再生成下一个；单个 section 若过长按其三级标题分批 append+save（详见 `prompts/stages/s4-generate.md` 的"逐 section 落盘"节）。不要把整本攒在上下文里最后一次性写（几万~几十万字会撞 token 上限被截断）。
- **已知限制（断点续写依赖调用方 / 不夸大）**：逐 section 落盘保证"已写的不丢"，但"断了之后自动从断点续写"依赖调用方是 agentic agent（如能重读已写入的 draft/docx、判断写到哪、接着写）。非 agentic 的一次性调用在单次 token 上限处仍可能截断且不会自动续——本 Skill 不保证断点续写，只保证逐段落盘不丢已写部分。
- **review 点**：无（进 S5 整体审）。

### S5 评审修订

- **目标**：`draft.md` → `final.md` + `final.docx`（含字体合规验证）。
- **输入**：`draft.md` + 用户多轮对话反馈（红线 verify / 一致性 verify / 格式 verify / 可读性 verify）。
- **输出**：`final.md` + `final.docx`（正文字体按 font_policy / 段落字体合规 / fontTable 字体合规）。
- **操作**：① 走 `s5-review.md` 自检清单（红线 / 一致性 / 格式 / 可读性）核 draft.md → ② 修订得 `final.md` → ③ 3 步 docx 装配（见下）渲染 `final.docx`。
- **review 点**（用户介入）：用户多轮对话审 draft.md → final.md。
- **诚实边界（demo vs 真实）**：demo（非交互）的 S5 是**机械自检 + 透传**——按 s5-review.md 可机械化的清单项（二级标题数 = section 数 / 无内部术语外泄 / 无总结 footer）自检后 `final.md = draft.md` 字面透传，并渲染 `final.docx`（`examples/_demo_s5.py`）。**真实 S5 的"用户多轮评审 + 改写 markdown 字面"仍靠人**，框架不替代人工评审，只保证 S5 被真正走一遍、final.md/final.docx 真产出、s5-review.md 被消费。

## docx 工具调用三步（S5 必读 / 签名实测照抄）

```python
from pathlib import Path
from docx import Document

from docx_builder import create_section_doc, clean_docx_whitespace
from append_chapter import append_markdown
from check_font_safety import check_font_safety

# body_font = outline.yaml 的 output.font_policy（默认宋体 / 驱动正文字体）
body_font = outline_cfg["output"].get("font_policy", "宋体")

# 1. 创建空 docx 容器（Normal 样式正文字体 = body_font / 内部 save / 返回 Path）
create_section_doc(out_path: Path, body_font: str = "宋体") -> Path

# 2. 逐 section append + save 落盘（长文档不断流 / 不攒齐再写 / 中途断保住已写）
#    每生成完一个 section 立即 append + save；append 是累加语义（对同一 document 反复调）。
document = Document(str(final_docx))
append_markdown(document, doc_title_md, body_font=body_font)        # 一级标题先 append + save
document.save(str(final_docx))
for section_md in 逐个生成的_section:                               # 一次只生成一个 section / 不一口气出整本
    stats: dict = append_markdown(document, section_md, body_font=body_font)
    document.save(str(final_docx))                                 # ← 每 section 立即落盘（断了保住）
# stats 字段（每次 append 返回）: {'headings', 'paragraphs', 'tables', 'figures', 'list_items'}
clean_docx_whitespace(document); document.save(str(final_docx))    # 末尾整体清空格 + final save

# 3. 字体合规验证（declared_font 给定时额外校验实际正文字体 == font_policy 声明）
issues: list[str] = check_font_safety(final_docx, declared_font: str | None = None)
# issues 空 list = 合规 / 非空 = 报告段落 / fontTable / font_policy 契约不一致
```

**字体白名单**（口径以 `scripts/check_font_safety.py` 白名单常量为权威 / 分两层，勿当扁平表）：
- **正文 run 级**（实际渲染字体）：中文 宋体 / 黑体 / 仿宋（含 仿宋_GB2312）/ 微软雅黑；西文**仅** Times New Roman + Consolas（inline code 等宽术语如 `API` `SDK`）。
- **fontTable 级**（仅声明层 / 额外容忍但不应被正文 run 引用）：Arial / Calibri / Cambria。

## 加新文档类型（4 步 / 不动 L1）

1. 加 `templates/<new_doc_type>/outline.yaml`（参照 `templates/需求方案/outline.yaml` / 含 intake_schema + outline + generation + output 四段）。**每个 section 必须写 `asset_needs`（手段无关列该 section 需要的素材类型 / 非空 list / S2 素材链依赖）；`generation.stages` 必须注册 `s2_acquire: prompts/stages/s2-acquire.md`**（缺这两项 validate_outline 硬失败）。
2. 加 `prompts/sections/<new_doc_type>/<NN-section>.md`（每 section 含 anchor + intake 字段依赖 + CoT 生成思路 + 输出格式 + 「## 素材运用（S2 / assets.json）」小节 + 红线复述）。
3. 调 `from docx_builder import create_section_doc; create_section_doc(Path('templates/<new_doc_type>/template.docx'))` 生成空 docx 母版（备存）。
   - **注（template_docx 预留待实现）**：outline 的 `output.template_docx` 是**预留待实现字段**。当前流程不从模板创建文档——S5 装配时一律 `create_section_doc` **重建标准格式容器**（Normal 样式 = font_policy）再 `append_markdown`。"从既有 template.docx 套版创建"是后续能力，validate 不校验该字段，demo 也不消费它。母版文件仅作存档。
4. 跑 `python scripts/validate_outline.py templates/<new_doc_type>/outline.yaml --repo-root .` 校验通过。

**不动**：scripts/ + prompts/system.md + prompts/stages/。

## 切换领域插件 / 自定义领域插件 howto（不动 L2）

L3 领域切换靠 **run.py override**（不改 outline.yaml）：在 run.py 内把 `prompts/domain/<vendor>/` 多文件拼成一段 `domain_plugin` 字面，传给 S4。下面是从零做一套自己领域插件的可照抄步骤。

### ① 文件清单（vendor 目录下放哪些 md）

- `company-profile.md`（公司主体字段 / **含 own_* 4 个程序约定 anchor / 见 ②**）
- `glossary.md`（领域术语）/ `client-logic.md`（客户决策逻辑）/ `compliance.md`（合规要求）
- 空缺文件不致命：override 函数对缺失文件返回占位注释（见 ③），但对应 section 会落【待补充】。

### ② anchor 命名规范（诚实区分：程序约定 vs 自由结构）

- **程序约定 anchor（名字不能改 / 改了 section prompt 按名解析不到 → 渲染【待补充】）**：仅 `company-profile.md` 的 4 个 `own_*`——`## own_company_brief` / `## own_qualifications` / `## own_certifications` / `## own_team_size`。被 2 个 section prompt 按名解析：`解决方案建议书/01-company-strength`、`实施方案/04-team-organization`。做自己领域插件时这 4 个段标题**必须照抄**。
- **自由结构 anchor（名字随便起 / 领域内容自由组织）**：`glossary.md` / `client-logic.md` / `compliance.md` 内的中文 anchor（如 `## 平台与产品术语` / `## 客户决策链` / `## 数据安全与等保`）不被程序解析，按你领域自由命名。

### ③ run.py override 模板（可照抄）

```python
DOMAIN_DIR = REPO_ROOT / "prompts" / "domain" / "<vendor 目录>"
DOMAIN_FILES = ["company-profile.md", "glossary.md", "client-logic.md", "compliance.md"]

def load_domain() -> str:
    parts: list[str] = []
    for fname in DOMAIN_FILES:
        p = DOMAIN_DIR / fname
        parts.append(p.read_text(encoding="utf-8") if p.exists() else f"<!-- {fname} 不存在 -->\n")
    return "\n\n".join(parts)

# 主流程：把 load_domain() 结果作为 domain_plugin 传入 generate_section_content（不改 outline.yaml）
```

活例子见 `examples/demo-槐序数据领域/run.py`（虚构领域 / `load_domain()` 拼 4 文件 / §01 公司实力由 own_* 填充）。

### ④ 空领域 vs 真实领域

- **默认（不 override）**：`outline.yaml.generation.domain_plugin = prompts/domain/_空领域/glossary.md` → sales 类 section（含 own_* 缺口的）输出整段【待补充】，不虚构。
- **真实领域**：run.py override 拼 vendor 多文件 → sales 类 section 用真实公司字面填充。切换不改 outline.yaml / 不改 L1 / 不改 section prompt。
- 字面来源红线：vendor 文件里的公司名 / 资质 / 标准号等必须真实脱敏字面，不凭模型记忆编造。

## 严格禁止事项

1. **事实有来源 / 内部术语不外泄 / 不扩展用户字面**（设计原则 3）。
2. **不一次性出整本 docx**：必须按 section 逐段 `append_markdown` + save / 不在 LLM 单次返回整本 markdown。
3. **不跳阶段**：S1 必须先于 S4 / S5 必须在 S4 之后 / 用户 review 介入 2 次（S1 + S5）不可省。
4. **不在 Skill 内部再调外部 LLM API**：Skill 工作流中 agent 自身即 LLM（Skill 使用者）。
5. **不内置检索**：S2 不实现检索引擎，但必须用环境手段主动获取素材；不得以"调占位"为由跳过 S2。
6. **不虚构领域内容**：公司名 / 产品名 / 资质表 / 标准号等必须来自 `prompts/domain/<vendor>/` 真实字面。

## stub 与真实工作流的关系

仓库内的 stub 文件（`scripts/llm_stub.py` + 各 `examples/demo-*/llm_stub_local.py`）+ `PlaceholderAssetsProvider`（scripts/assets_provider.py）+ demo 的 fixture `assets.json` 是 **tests / demo fixture**：用于端到端 demo 跑通管道连通性 + tests CI（按 section_id 拼装 markdown 字面 / 不调任何 LLM）。

**真实 agent 工作流不调 stub**：agent（如 Claude Code / Cline 这类 LLM）在 S4 阶段自己读 section prompt 自己生成 markdown / 不 import 任何 stub。stub 保留作为 fixture / 不在本 Skill 工作流路径上暴露。

---

架构哲学 / 怎么用 / 怎么扩展：见 `README.md`。
工程方法论（设计决策背后的"踩坑→解决"）：见 `docs/engineering-notes.md`。
