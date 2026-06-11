# 03 方案架构 / section prompt

## anchor

本 section 给出我方对项目的总体方案架构。区别于 requirement-proposal §04 技术架构概述（需求侧 / "应采用 ... 技术路线"），本 section 是**方案侧 / "我们采用 ..."措辞**。允许出现具体技术选型、平台名、组件名（基于 `existing_systems` + 我方技术储备）。

## intake 字段依赖

- `existing_systems`（选填 list / 决定"与现有系统对接"的具体范围）
- `reference_cases`（选填 list / 决定"参照同类架构"的措辞）
- `core_pain_points`（选填 list / 反推方案模块覆盖哪些痛点）

## CoT 生成思路

1. 引导句：本节给出本项目的总体方案架构与技术路线
2. 总体架构图（占位）：`【图 3.1: 总体方案架构示意图】`
3. 分层描述（典型五层 / 我方按本项目实际调整）：
   - 数据接入与汇聚层（与 `existing_systems` 对接）
   - 数据治理与存储层
   - 平台与中台能力层
   - 业务应用层（覆盖 `core_pain_points`）
   - 集成与开放层（参照 `reference_cases`）
4. 关键技术选型说明段（我方技术栈 / stub 阶段不指定具体厂商 / 真实接入时由 L3 领域插件提供）

## 输出格式

二级标题 + 引导句 + 架构图占位 + 5 个三级标题分层段 + 技术选型段：

```markdown
## 方案架构

<引导句，约 50 字>

**【图 3.1: 总体方案架构示意图】**

### 数据接入与汇聚层

<段落 / 含与 existing_systems 对接说明>

### 数据治理与存储层

<段落>

### 平台与中台能力层

<段落>

### 业务应用层

<段落 / 含对 core_pain_points 的覆盖说明>

### 集成与开放层

<段落 / 含 reference_cases 参照说明>

### 关键技术选型

<段落 / 我方技术栈说明>
```

## 素材运用（S2 / assets.json）

本 section 写作时必须读取 `assets.json` 的 `sections.<本 section id>.acquired`（S2 产出 / 见 `prompts/stages/s2-acquire.md`）：

- 每条 `status: "acquired"` 的素材，把其 `content` 实质性织入对应论点（支撑论述，而非堆砌）。
- 每条 `status: "待补充"`（S2 未获取到）的素材，在其应支撑的位置写「【待补充】」，不编造（红线 3）。
- 不在正文暴露 `source` / `asset_type` 等字段名（内部术语不外泄 / 红线 4）。

## 长 section 分批生成（避免单 section 撞 token 上限）

本 section 较长（含多个三级分层），生成时按**三级标题逐块生成 + 逐块 `append_markdown` + save 落盘**，不在一次输出里写完整个 section（通则见 `prompts/stages/s4-generate.md` 的"逐 section 落盘"节）。

## 红线复述

- 具体厂商 / 产品 / 版本号待 L3 领域插件提供 / 不在 L2 stub 阶段编造
- 集成层措辞限于 `existing_systems` 字面 / 不引入用户未提及的系统
- 业务应用层模块数 ≥ `core_pain_points` 长度（每痛点对应 ≥1 模块）
