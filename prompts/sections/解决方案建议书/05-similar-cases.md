# 05 类似案例 / section prompt

## anchor

本 section 列举我方与本项目相似的过往交付案例，作为方案可行性的实证。每个案例需含 4 要素：客户名 / 项目背景 / 我方承担工作 / 交付成果。

## intake 字段依赖

- `reference_cases`（选填 list）

## CoT 生成思路

1. 引导句：本节列举我方与本项目相似的过往交付案例
2. 逐条渲染 `reference_cases`：
   - 案例名 / 客户行业 / 实施年份（来源：reference_cases 字面）
   - 项目背景与挑战（基于 `client_industry` + `core_pain_points` 反推 / 不脑补具体数字）
   - 我方承担工作（L3 领域插件层提供 / M2/M3 stub 阶段写【待补充】）
   - 交付成果（同上）
3. 若 `reference_cases` 为空 / 整段写【待补充】

## 输出格式

二级标题 + 引导句 + N 个三级标题案例段：

```markdown
## 类似案例

<引导句，约 50 字>

### 案例一 <案例名>

- 客户行业：<行业>
- 实施年份：<年份>
- 项目背景：<段落>
- 我方承担工作：【待补充】（待 L3 领域插件提供）
- 交付成果：【待补充】（待 L3 领域插件提供）

### 案例二 <案例名>

- 客户行业：<行业>
- 实施年份：<年份>
- 项目背景：<段落>
- 我方承担工作：【待补充】
- 交付成果：【待补充】

...
```

## 素材运用（S2 / assets.json）

本 section 写作时必须读取 `assets.json` 的 `sections.<本 section id>.acquired`（S2 产出 / 见 `prompts/stages/s2-acquire.md`）：

- 每条 `status: "acquired"` 的素材，把其 `content` 实质性织入对应论点（支撑论述，而非堆砌）。
- 每条 `status: "待补充"`（S2 未获取到）的素材，在其应支撑的位置写「【待补充】」，不编造（红线 3）。
- 不在正文暴露 `source` / `asset_type` 等字段名（内部术语不外泄 / 红线 4）。

## 红线复述

- 案例数 = `reference_cases` 长度，不增不减
- 我方承担工作 / 交付成果在 L2 intake_schema 不存在 / 整段【待补充】 / 待 L3 领域插件层填充
- 不脑补客户决策细节 / 投资额 / 服务期等具体数字
