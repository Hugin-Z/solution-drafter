# S4 内容生成 / stage prompt

## 任务

按当前 section 的 prompt 字面 + 上游 `outline_filled.json` 字段值，生成该 section 的 markdown draft。

## 输入

- `system_prompt`（框架级写作风格 / 红线）
- 当前 section 的 `section_prompt`（section 专属 anchor + CoT + 输出格式）
- `intake_data`（intake.json dict）
- `intake_fields`（outline.yaml 指定的该 section 依赖的 intake 字段清单）
- **`assets.json` 该 section 的 `acquired` 素材（S2 产出 / 强依赖 / 见下"S2 素材强依赖"）**
- `domain_plugin`（领域插件 glossary / 默认空领域 / 切真实领域插件后注入业务字面）

## 输出契约

输出**仅 section markdown 字面**，不输出多余说明 / 不输出代码块包裹：

```markdown
## <section title>

<段落 1 / 列表 / 表格 / ...>

<段落 2 / ...>
```

- 第一行必须是 `## <section title>`（二级标题 / 与 outline.yaml 字面对齐 / 下游 append_chapter 解析）
- 后续按 section_prompt 指定的子结构（### / 段落 / 列表 / 表格）展开
- 不在最后追加 "---" / "End" / 总结性 footer

## 逐 section 落盘（长文档不断流 / 强制）

逐 section 生成时，**每生成完一个 section 立即落盘，再生成下一个**，不要把整本攒在上下文里最后一次性写：

1. 先建空 docx 容器（`create_section_doc`），把一级标题 `append_markdown` 进去并 `document.save()`。
2. **对每个 section：生成该 section markdown → `append_markdown(document, 本section_md)` → `document.save()` 落盘 → 再生成下一个。**
3. 全部 section 写完后做一次整体清理（`clean_docx_whitespace`）+ final `save`。

**原因**：LLM 单次输出有 token 上限，几万~几十万字的长方案文档若一口气生成整本会被截断；逐 section 落盘后，即使中途断（上下文耗尽 / 进程中断），已写入磁盘的 section 也保住，可重读续写——而"攒齐再写"在最后一次 save 前磁盘是空的，中途断已生成的全丢。

**单 section 超长再分批（通则）**：若**单个 section 本身**展开很长（如"方案架构""实施计划"含多个三级分层），按其**三级标题逐块生成 + 逐块 `append_markdown` + save**，不在一次输出里写完整个 section（同理避免单 section 撞单次 token 上限被截）。

## S2 素材强依赖（核心 / 后果链）

**本 section 的内容生成必须使用 `assets.json` 中该 section 的 `acquired` 素材**，不能只靠 section prompt 套话 + intake 字段填空：

- 读 `assets.json.sections[<本 section id>].acquired`，把每条 `status: "acquired"` 的素材 `content` 实质性用进对应论述（不是堆砌 / 是支撑论点）。
- 某 asset_need 的 `status: "待补充"`（S2 没获取到）→ 该素材支撑的论述处**写"【待补充】"**，不编造。
- **后果链**：若 S2 未发动（assets.json 为空 / 全待补充）→ 本 section 大面积【待补充】→ S5 评审暴露"内容空"。这是有意设计：**跳过 S2 的后果在 S5 显性化**，逼 S2 真发动。
- 素材来源（assets.json 的 `source`）保留可溯源 / 不在最终 markdown 里暴露 source 字段（内部术语不外泄 / 红线 4）。

**逐 section 落实（与 section prompt 配合）**：每个 section prompt 末尾有「## 素材运用（S2 / assets.json）」小节，列出该 section 必须消费的 acquired 素材步骤。执行该 section 的 CoT 时，按其「素材运用」小节逐条把 acquired 素材织入论点 / 待补充落「【待补充】」。**不允许只跟 CoT 填 intake 字段而跳过素材运用步骤**（这是 M7-j 链断后 M7-k 把素材依赖下沉到每个 section 的目的）。

**已知限制（逼发动强度 / R10 不夸大）**：上述强依赖 + 后果链是 prompt 级约束，**不是机器闸门**。一个倾向「把话说圆」的 agent 仍可能跳过 S2、用套话把 intake 字段填满 draft 而不触发大面积【待补充】。本机制让 S2→S4 素材链可执行 / 可见 / 可验，但真实发动强度中等，最终靠真实使用与 S5 评审暴露——不假设它能强制每个 agent 必然发动 S2。

## 生成约束

1. **不扩展 intake**：仅基于 `intake_fields` 列出的 intake 字段 + `intake_data` 实际值 + `assets.json` 该 section 素材生成；不引入未声明字段。
2. **字面缺失填【待补充】**：`intake_fields` 中某字段在 `intake_data` 缺失或为 null，对应位置写"【待补充】"，不编造。
3. **不输出内部术语**：`__PENDING_USER__` / `intake_fields` / 字段名英文等不出现在 markdown 里。
4. **list 字段渲染为列表**：`core_pain_points` / `existing_systems` 等 list 字段渲染为 markdown `-` 列表，不堆叠为一段。
5. **字数遵从 section_prompt**：section_prompt 若指定字数（"约 300 字"），按其执行 ±10%；未指定则不刻意压缩或扩张。

## 自检（输出前）

- [ ] 首行 `## <section title>` 与 outline.yaml 字面对齐
- [ ] 仅引用 `intake_fields` 字段
- [ ] 缺失字段写"【待补充】"
- [ ] 无内部术语外泄
- [ ] 无总结性 footer
