# 01 项目概述 / section prompt

## anchor

本 section 是实施方案的开篇，概述项目背景、建设目标、实施范围。读者是客户项目管理方与实施监理，需要快速把握"这个项目要做什么、实施方在干什么"。

## intake 字段依赖

- `project_name`（必填）
- `client_name`（必填）
- `client_industry`（必填）
- `core_pain_points`（选填 list / 概述建设动因）

## CoT 生成思路

1. 引导句：本节概述 {project_name} 的实施背景与总体目标
2. 项目背景段：`client_name` + `client_industry` 的业务背景与建设动因（引用 `core_pain_points`）
3. 建设目标段：本次实施要达成的总体目标
4. 实施范围段：本方案覆盖的实施内容边界

## 输出格式

二级标题 + 引导句 + 3 段正文：

```markdown
## 项目概述

<引导句，约 50 字>

### 项目背景

<段落 / 约 150 字>

### 建设目标

<段落 / 约 120 字>

### 实施范围

<段落 / 约 120 字>
```

## 素材运用（S2 / assets.json）

本 section 写作时必须读取 `assets.json` 的 `sections.<本 section id>.acquired`（S2 产出 / 见 `prompts/stages/s2-acquire.md`）：

- 每条 `status: "acquired"` 的素材，把其 `content` 实质性织入对应论点（支撑论述，而非堆砌）。
- 每条 `status: "待补充"`（S2 未获取到）的素材，在其应支撑的位置写「【待补充】」，不编造（红线 3）。
- 不在正文暴露 `source` / `asset_type` 等字段名（内部术语不外泄 / 红线 4）。

## 红线复述

- 不引入用户未提及的事实
- `core_pain_points` 缺失 → 项目背景段写"基于前期沟通材料"占位 / 不编造
- 建设目标不夸张（不"国内领先" / "行业标杆"除非客户字面已用）
