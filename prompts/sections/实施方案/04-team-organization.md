# 04 组织保障 / section prompt

## anchor

本 section 给出项目实施的组织保障：项目团队架构、角色职责、人员配置。

**重要：团队规模 / 人员配置依赖实施方主体信息（own_team_size 等），不在 intake_schema 内（我方主体字段属 L3 领域插件层）。L3 未提供该字段时，本 section 输出团队架构骨架 + 具体人数 / 配置标【待补充】。**

## intake 字段依赖

- 无 intake_schema 字段
- 实际依赖（L3 领域插件层 / company-profile 的 own_team_size）：项目团队规模 / 角色配置模板

## 生成思路

1. 引导句：本节给出本项目的组织保障与团队配置
2. 项目组织架构段：典型架构（项目总负责人 / 项目经理 / 技术负责人 / 实施工程师 / 质量与测试 / 运维支持）
3. 角色职责段：各角色职责（通用描述 / 不绑定具体人）
4. 人员配置段：具体人数 / 高级工程师占比 → 依赖 L3 own_team_size / 未提供则【待补充】

## 输出格式

二级标题 + 引导句 + 3 段正文：

```markdown
## 组织保障

<引导句，约 50 字>

### 项目组织架构

<段落 / 角色层级>

### 角色职责

<段落 / 各角色职责>

### 人员配置

<段落 / own_team_size 未提供时写【待补充】>
```

## 素材运用（S2 / assets.json）

本 section 写作时必须读取 `assets.json` 的 `sections.<本 section id>.acquired`（S2 产出 / 见 `prompts/stages/s2-acquire.md`）：

- 每条 `status: "acquired"` 的素材，把其 `content` 实质性织入对应论点（支撑论述，而非堆砌）。
- 每条 `status: "待补充"`（S2 未获取到）的素材，在其应支撑的位置写「【待补充】」，不编造（红线 3）。
- 不在正文暴露 `source` / `asset_type` 等字段名（内部术语不外泄 / 红线 4）。

## 红线复述

- 具体人数 / 团队规模缺失（own_team_size 未提供）→ 保留【待补充】 / 不编造人数
- 角色职责用通用描述 / 不脑补具体人名
- 不夸大团队资质（资质类信息走 L3 company-profile）
