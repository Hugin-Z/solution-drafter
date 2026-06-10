# 02 项目理解 / section prompt

## anchor

本 section 展示我方对客户业务场景与项目需求的理解深度。区别于 requirement-proposal §01 项目背景（中立陈述）/ §02 客户痛点（问题诊断），本 section 是**站在我方视角对客户问题的再诠释**：把客户痛点翻译为业务术语，体现"我们听懂了"。

## intake 字段依赖

- `project_name`（必填）
- `client_name`（必填）
- `client_industry`（必填）
- `core_pain_points`（选填 list / 我方对痛点的再诠释 / 不是原文复述）

## CoT 生成思路

1. 引导句：本节阐述我方对 {project_name} 项目背景与需求的理解
2. 客户业务定位段：把 `client_name` + `client_industry` 翻译为业务术语（"贵单位作为 <industry> 在 ... 方面承担 ... 职能"）
3. 痛点再诠释段：把 `core_pain_points` 每条翻译为"我们理解到 ..."句式 / 体现我方专业判断 / 不照搬原文
4. 收束句：本次项目的核心挑战与价值

## 输出格式

二级标题 + 引导句 + 3 段正文：

```markdown
## 项目理解

<引导句，约 50 字>

### 客户业务定位

<段落 / 约 150 字>

### 需求理解

<段落 / 含痛点再诠释 / 约 250 字>

### 项目核心挑战与价值

<段落 / 约 100 字>
```

## 素材运用（S2 / assets.json）

本 section 写作时必须读取 `assets.json` 的 `sections.<本 section id>.acquired`（S2 产出 / 见 `prompts/stages/s2-acquire.md`）：

- 每条 `status: "acquired"` 的素材，把其 `content` 实质性织入对应论点（支撑论述，而非堆砌）。
- 每条 `status: "待补充"`（S2 未获取到）的素材，在其应支撑的位置写「【待补充】」，不编造（红线 3）。
- 不在正文暴露 `source` / `asset_type` 等字段名（内部术语不外泄 / 红线 4）。

## 红线复述

- 痛点再诠释不引入用户未提及的事实
- 不夸张表述（"国家战略" / "重大意义"）除非客户字面已用
- `core_pain_points` 字段缺失 → 需求理解段写"基于贵单位前期沟通材料"占位 / 不编造
