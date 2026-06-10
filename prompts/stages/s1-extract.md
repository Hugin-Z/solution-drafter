# S1 信息抽取 / stage prompt

## 任务

从用户提供的零散输入（聊天记录 / 会议纪要 / 邮件 / 上传文档片段）中抽取结构化字段，产出 `intake.json`。

## 输入

- 用户提供的零散文本
- 当前文档类型的 `intake_schema`（含 `required` + `optional` 字段清单）

## 输出契约

严格按 `intake_schema` 字段清单输出 JSON：

```json
{
  "<required 字段 1>": "...",
  "<required 字段 2>": "...",
  "<optional 字段 1>": "...",
  "...": "..."
}
```

## 抽取规则

1. **required 字段全部必须出现**：若用户输入未涵盖某个 required 字段，对应值填 `null`，并在 chat 端追加一条"待用户补充：<字段名>"提示。
2. **optional 字段按需出现**：用户输入未涉及的 optional 字段直接省略 key，不写 `null`。
3. **字面忠实**：字段值字面忠于用户输入，不重写 / 不润色 / 不补充具体数字。
4. **list 字段拆条**：`core_pain_points` / `existing_systems` / `reference_cases` 等 list 字段，按用户输入的自然边界拆条，不合并不拆分。
5. **歧义保留原文**：用户输入含歧义（如"大约 8 个月或一年"）时，字段值保留原文，不擅自选择一个值。

## 自检（输出前）

- [ ] required 字段全部出现（缺失项值为 `null` + 提示）
- [ ] JSON 合法（双引号 / 无尾逗号）
- [ ] 字符串字段值未经过模型记忆补充
- [ ] list 字段元素来自用户输入的自然拆条
