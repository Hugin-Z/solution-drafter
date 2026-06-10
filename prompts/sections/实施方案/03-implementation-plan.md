# 03 实施计划 / section prompt

## anchor

本 section 给出实施的时间计划：阶段划分、里程碑、各阶段交付物。读者用本段判断"项目排期是否合理、关键节点在哪"。

## intake 字段依赖

- `project_period`（必填 / 决定阶段划分与排期）

## CoT 生成思路

1. 引导句：本节给出本项目的实施计划与阶段安排
2. 阶段划分段：按 `project_period` 拆阶段（需求调研 / 设计 / 开发部署 / 数据治理 / 试运行 / 验收 / 运维）
3. 里程碑表：各阶段 + 周期 + 关键交付物（markdown 表格）
4. 收束句：进度保障说明

## 输出格式

二级标题 + 引导句 + 阶段划分段 + 里程碑表：

```markdown
## 实施计划

<引导句，约 50 字>

### 阶段划分

<段落 / 引用 project_period>

### 里程碑计划

| 阶段 | 周期 | 关键交付物 |
|---|---|---|
| 需求调研 | <周期> | <交付物> |
| ... | ... | ... |

<进度保障收束句>
```

## 素材运用（S2 / assets.json）

本 section 写作时必须读取 `assets.json` 的 `sections.<本 section id>.acquired`（S2 产出 / 见 `prompts/stages/s2-acquire.md`）：

- 每条 `status: "acquired"` 的素材，把其 `content` 实质性织入对应论点（支撑论述，而非堆砌）。
- 每条 `status: "待补充"`（S2 未获取到）的素材，在其应支撑的位置写「【待补充】」，不编造（红线 3）。
- 不在正文暴露 `source` / `asset_type` 等字段名（内部术语不外泄 / 红线 4）。

## 长 section 分批生成（避免单 section 撞 token 上限）

本 section 较长（含多个三级分层），生成时按**三级标题逐块生成 + 逐块 `append_markdown` + save 落盘**，不在一次输出里写完整个 section（通则见 `prompts/stages/s4-generate.md` 的"逐 section 落盘"节）。

## 红线复述

- 总周期严格按 `project_period` 字面 / 各阶段周期之和不超过总周期
- 不编造具体日期（除非 `project_period` 含明确起止）
- 里程碑交付物限于本方案实施范围
