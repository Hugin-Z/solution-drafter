# S2 资料获取 / stage prompt

## 这是你的任务，不是等待投喂

**你现在必须为每个 section 主动获取素材，产出 `assets.json`。这是 S2 阶段你要完成的实质工作，不是占位、不是自动通过、不是等别人把素材递给你。** 没有 assets.json，S4 无法生成有料的内容（S4 强依赖本阶段产出 / 见 s4-generate.md）。

## 输入

- `intake.json`（S1 产出 / 客户字面事实）
- `templates/<doc_type>/outline.yaml` 的每个 section 的 `asset_needs`（该 section 需要的**素材类型清单** / 手段无关）
- 你所在环境可用的一切获取手段

## 手段完全由你定（手段无关）

`asset_needs` 只声明"需要什么类型的素材"，**不规定"怎么获取"**。满足需求的手段是并列的，用你环境里有的：

- 语义检索（RAG / 向量库）
- 关键词检索（ripgrep / grep / 全文索引，如 agentic-kb-lite）
- 数据库查询（SQL / 知识图谱）
- 网络搜索
- 用户已上传文档 / referenced 类素材
- 人工提供 / 你直接知道的可溯源事实

**不假设任何特定手段**。ripgrep 是关键词匹配、SQL 是查询、RAG 是语义召回——它们都能满足"获取某类素材"的需求，结果都装进同一个 `assets.json` 结构。

## 逐 section 自检清单（可执行 / 有终点）

对 outline 的**每一个 section**，依次执行：

1. **列需求**：读该 section 的 `asset_needs`，列出它需要的素材类型。
2. **获取**：用你的手段为每个素材类型获取实际素材内容。
3. **记录**：
   - 获取到 → `status: "acquired"` / `content` 填素材内容 / `source` 标来源（如 `"ripgrep:案例库"` / `"RAG"` / `"用户上传文档 X"` / `"人工"`）
   - 获取不到 → `status: "待补充"` / `content: null` / `source: null`
4. **写入** `assets.json` 该 section 的条目。

**完成判定**：assets.json 含所有 section 的素材状态（每个 asset_need 都有 acquired 或待补充 的明确记录）。不允许任何 section 缺条目。

## assets.json 结构（手段无关）

```json
{
  "doc_type": "<doc_type id>",
  "sections": {
    "01": {
      "asset_needs": ["公司资质", "产品能力"],
      "acquired": [
        {"asset_type": "公司资质", "status": "acquired", "content": "<素材内容>", "source": "<你的来源标注>"},
        {"asset_type": "产品能力", "status": "待补充", "content": null, "source": null}
      ]
    },
    "02": { "...": "..." }
  }
}
```

- `status` ∈ `{acquired, 待补充}`
- `source` 是自由字符串，标你的获取来源（ripgrep / RAG / SQL / 网络 / 人工 / 上传文档 均可）
- **不带任何手段特有字段**（无 relevance score / 无 embedding / 无 query）—— 任何手段的结果都装得进

## 红线

- **不虚构素材**（红线 3）：获取不到就标 `待补充`，不编造资质 / 案例 / 数字 / 厂商。
- **素材必须可溯源**：`source` 标清来源，便于 S5 核验。
- **每个 section 都要走一遍**：不允许"看到 asset_needs 但不发动" / 不允许跳过某 section。

## 自检（产出前）

- [ ] outline 每个 section 在 assets.json 都有条目
- [ ] 每个 asset_need 都有 acquired / 待补充 明确状态
- [ ] acquired 的 content 非空 + source 已标
- [ ] 待补充的不编造内容
- [ ] assets.json 结构无手段特有字段（手段无关）
