# 02 实施方案 / section prompt

## anchor

本 section 给出实施的总体技术路线与方法论：采用什么实施方法、分几条线推进、与现有系统如何衔接。区别于解决方案建议书的方案架构（偏设计），本段偏"怎么落地实施"。

## intake 字段依赖

- `core_pain_points`（选填 list / 决定实施重点）
- `existing_systems`（选填 list / 决定与现有系统衔接的实施动作）

## 生成思路

1. 引导句：本节给出本项目的总体实施方案与技术路线
2. 实施方法论段：采用的实施方法（如分阶段迭代 / 原型先行 / 数据驱动）
3. 实施主线段：分几条线推进（如平台部署线 / 数据治理线 / 应用建设线）/ 每条线对应 `core_pain_points`
4. 系统衔接段：与 `existing_systems` 的对接实施动作

## 输出格式

二级标题 + 引导句 + 3 段正文：

```markdown
## 实施方案

<引导句，约 50 字>

### 实施方法论

<段落>

### 实施主线

<段落 / 含对 core_pain_points 的覆盖>

### 系统衔接

<段落 / 含与 existing_systems 对接>
```

## 素材运用（S2 / assets.json）

本 section 写作时必须读取 `assets.json` 的 `sections.<本 section id>.acquired`（S2 产出 / 见 `prompts/stages/s2-acquire.md`）：

- 每条 `status: "acquired"` 的素材，把其 `content` 实质性织入对应论点（支撑论述，而非堆砌）。
- 每条 `status: "待补充"`（S2 未获取到）的素材，在其应支撑的位置写「【待补充】」，不编造（红线 3）。
- 不在正文暴露 `source` / `asset_type` 等字段名（内部术语不外泄 / 红线 4）。

## 红线复述

- 实施主线条数 ≥ 关键 `core_pain_points` 覆盖需要 / 不强凑
- 系统衔接限于 `existing_systems` 字面 / 不引入用户未提及的系统
- 不承诺用户未要求的实施内容
