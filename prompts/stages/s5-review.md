# S5 评审修订 / stage prompt

## 任务

对 S4 产出的 `draft.md`（合并各 section markdown）做一次性整体评审 + 修订，产出 `final.md`。

## 输入

- `draft.md`（各 section markdown 合并 / 含一级标题 + N 个二级标题段，N = 本 doc_type outline 的 section 数）
- `intake_data`（用户字面）
- 用户多轮对话反馈（M2 不接 / M5 接入）

## 评审维度

1. **红线 verify**
   - 是否含非来源事实（项目名 / 客户名 / 金额 / 时间 / 现有系统 / 参考案例之外的未声明事实）
   - 是否含内部术语外泄（`__PENDING_USER__` / 字段名英文等）
   - 是否扩展了用户字面（"为了完整性再加一段"类）

2. **一致性 verify**
   - 客户名 / 项目名 / 时间 / 金额在各 section 中是否一致
   - 现有系统 list 在多次出现时是否字面一致（不变形）

3. **格式 verify**
   - 二级标题数量是否 = 本 doc_type outline.yaml 的 outline 列表长度（运行时读取 / 勿假设固定值）
   - 二级标题字面是否与 outline.yaml title 对齐
   - 无总结性 footer / 无内部术语注释

4. **可读性 verify**
   - 句式书面语 / 无口语 / 无营销词
   - 段落主旨单一 / 不混杂论点

## 修订规则

- 发现违反红线 / 一致性 / 格式问题 → 直接改 markdown 字面
- 可读性问题 → 改字面但保留事实
- 字段缺失"【待补充】"保留不动（这是 S4 正确产出，不在 S5 修订）

## 输出契约

输出 `final.md` 完整字面（含一级标题 + 各二级标题段 / markdown 格式）。

## 自检（输出前）

- [ ] 二级标题数量 = 本 doc_type outline 的 section 数
- [ ] 客户名 / 项目名 各 section 内一致
- [ ] 无内部术语 / 无总结性 footer
- [ ] 无 S4 阶段未授权扩展的事实
