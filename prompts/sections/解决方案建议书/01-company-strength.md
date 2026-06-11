# 01 公司实力 / section prompt

## anchor

本 section 是解决方案建议书的开篇，定位我方（本公司）的资质、规模、技术储备、行业经验。读者是客户评审人员，需要在 1 分钟内判断"这家公司能不能干这事"。

**重要：本 section 依赖我方公司信息字段，当前 L2 intake_schema 不含该类字段。该类字段应在 L3 领域插件层（如 `prompts/domain/<vendor>/company-profile.md` 的 own_* 字段）以"我方主体卡片"形式提供。未接领域插件时 `intake_data` 中无对应字段，输出整段【待补充】。**

## intake 字段依赖

- 无 intake_schema 字段
- 实际依赖（L3 领域插件层填充）：
  - `own_company_brief`（公司简介 / 成立年份 / 员工规模 / 行业地位）
  - `own_qualifications`（资质清单 / ISO / CMMI / 测绘资质 / 等级保护资质等）
  - `own_certifications`（产品认证 / 行业认证）
  - `own_team_size`（项目团队规模 / 行业经验年限）

## 生成思路

1. 检查 `domain_plugin` 是否含 own_company_* 字段
2. 若含 → 按段落渲染（公司简介 / 资质 / 产品 / 团队四段）
3. 若不含 → 输出整段【待补充】+ 内联标注"待 L3 领域插件提供 own_company_brief / own_qualifications / own_certifications / own_team_size 4 个字段"
4. 不脑补公司名 / 资质名 / 数字（红线 3）

## 输出格式

二级标题 + 4 个三级标题段（若 L3 提供）/ 或单段【待补充】：

```markdown
## 公司实力

### 公司简介

<段落 / 由 own_company_brief 字段渲染>

### 资质与认证

<段落 / 由 own_qualifications + own_certifications 字段渲染>

### 产品与技术储备

<段落>

### 团队与行业经验

<段落 / 由 own_team_size 字段渲染>
```

或（L3 未提供）：

```markdown
## 公司实力

【待补充】（待 L3 领域插件提供 own_company_brief / own_qualifications / own_certifications / own_team_size 4 个字段）
```

## 素材运用（S2 / assets.json）

本 section 写作时必须读取 `assets.json` 的 `sections.<本 section id>.acquired`（S2 产出 / 见 `prompts/stages/s2-acquire.md`）：

- 每条 `status: "acquired"` 的素材，把其 `content` 实质性织入对应论点（支撑论述，而非堆砌）。
- 每条 `status: "待补充"`（S2 未获取到）的素材，在其应支撑的位置写「【待补充】」，不编造（红线 3）。
- 不在正文暴露 `source` / `asset_type` 等字段名（内部术语不外泄 / 红线 4）。

## 红线复述

- 不脑补公司名 / 资质名 / 数字 / 团队规模
- L3 未提供 → 整段【待补充】+ 字段缺口声明
- 不引用 L2 intake 中的客户字段（客户痛点等）拼凑公司实力描述
