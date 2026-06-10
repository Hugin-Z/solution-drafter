# -*- coding: utf-8 -*-
"""
llm_stub_local.py · M3 demo-local stub (proposal-document 6 section)

⚠️ M5 stub 退场说明 (非真实 agent 工作流路径):
本文件是 demo fixture / 用于 M3 端到端 demo 跑通管道连通性 + 验证 L12 demo-stage stub 范式.
真实 agent 工作流 (Claude Code / Cline 跑 SKILL.md) 在 S4 阶段不调本文件 / agent 自己读
prompts/sections/解决方案建议书/*.md + domain plugin / 自己生成 section markdown.
本 stub 不删 (M3 demo 跑通管道证据 + tests 可能依赖) / 仅声明 SKILL.md S4 不走 stub 路径.
详见仓库根 SKILL.md "stub 与真实工作流的关系" 段.

Surface 2 决策 E: demo-local stub 解 / L1 scripts/llm_stub.py 字节级 0 改动 / M3 仅在
本 demo 目录新增本文件 / run.py 改 1 处 import 来源.

接口签名严格对齐 L1 scripts/llm_stub.py.generate_section_content / 不变.
M5 真实 LLM 接入时本文件退场 / 同 L1 stub 一起被 anthropic API 取代.

stub 实现策略 (M3 sales-oriented section):
- 01 公司实力: L2 intake_schema 无字段 / 整段【待补充】 + 4 字段缺口声明
- 02 项目理解: 站我方视角对客户问题再诠释
- 03 方案架构: 5 层 + 技术选型 / 引用 existing_systems + reference_cases
- 04 方案亮点: 反推差异化 / 每痛点对应 1 亮点
- 05 类似案例: reference_cases 逐条 + 承担工作【待补充】
- 06 报价概要: 4 段 / budget_range + project_period
"""

from __future__ import annotations


PLACEHOLDER = "【待补充】"


def _field(intake_data: dict, key: str) -> str:
    v = intake_data.get(key)
    if v is None or v == "" or v == []:
        return PLACEHOLDER
    return str(v)


def _list_field(intake_data: dict, key: str) -> list[str]:
    v = intake_data.get(key)
    if not isinstance(v, list):
        return []
    return [str(item) for item in v if item]


def _render_section_01(intake_data: dict) -> str:
    """01 公司实力 / L2 无字段 / 整段【待补充】 + L3 字段缺口声明."""
    return (
        f"## 公司实力\n\n"
        f"{PLACEHOLDER}\n\n"
        f"（待 L3 领域插件层提供以下 4 个字段后填充：\n"
        f"own_company_brief / own_qualifications / own_certifications / own_team_size。\n"
        f"接入 L3 领域插件 (prompts/domain/<vendor>/company-profile.md 的 own_* 字段) 后本段自动填充。）\n"
    )


def _render_section_02(intake_data: dict) -> str:
    """02 项目理解 / 我方视角对客户问题再诠释."""
    project_name = _field(intake_data, "project_name")
    client_name = _field(intake_data, "client_name")
    client_industry = _field(intake_data, "client_industry")
    pains = _list_field(intake_data, "core_pain_points")

    lines = [
        f"## 项目理解\n",
        f"本节阐述我方对 {project_name} 项目背景与需求的理解。\n",
        f"### 客户业务定位\n",
        f"贵单位 {client_name} 作为 {client_industry}，承担相应领域的业务管理与公共服务职能，"
        f"在数字化建设过程中既有平台基础，也面临业务深化与协同的现实需求。\n",
        f"### 需求理解\n",
    ]
    if pains:
        lines.append("基于前期沟通材料，我方对贵单位当前业务运行状况理解如下：\n")
        for p in pains:
            lines.append(f"- 我们理解到：{p}")
        lines.append("")
    else:
        lines.append("基于贵单位前期沟通材料，我方对当前业务运行状况进行了梳理。\n")
    lines.append("### 项目核心挑战与价值\n")
    lines.append(
        "本项目的核心挑战在于业务数据汇聚与场景化应用的平衡，"
        "通过本次建设可在已有平台基础上释放业务赋能价值。\n"
    )
    return "\n".join(lines)


def _render_section_03(intake_data: dict) -> str:
    """03 方案架构 / 5 层 + 技术选型 / 引用 existing_systems + reference_cases."""
    existing = _list_field(intake_data, "existing_systems")
    refs = _list_field(intake_data, "reference_cases")
    pains = _list_field(intake_data, "core_pain_points")

    lines = [
        f"## 方案架构\n",
        f"本节给出本项目的总体方案架构与技术路线。\n",
        f"**【图 3.1: 总体方案架构示意图】**\n",
        f"### 数据接入与汇聚层\n",
    ]
    if existing:
        lines.append(
            f"通过标准接口与贵单位现有的 {'、'.join(existing[:3])} 等系统进行数据汇聚，"
            f"建立统一的数据进入通道。\n"
        )
    else:
        lines.append(f"{PLACEHOLDER}\n")
    lines += [
        f"### 数据治理与存储层\n",
        f"采用湖仓一体化的数据存储路线，对接入数据进行清洗、关联与主题化组织。\n",
        f"### 平台与中台能力层\n",
        f"提供数据中台、业务中台与三维 / 时空可视化能力，支撑上层应用快速构建。\n",
        f"### 业务应用层\n",
    ]
    if pains:
        lines.append(
            f"针对贵单位 {len(pains)} 项核心痛点，本方案规划相应业务功能模块予以覆盖。\n"
        )
    else:
        lines.append("规划相应业务功能模块。\n")
    lines += [
        f"### 集成与开放层\n",
    ]
    if refs:
        lines.append(
            f"参照 {refs[0]} 等同类项目实践，提供标准化集成接口与开放能力。\n"
        )
    else:
        lines.append("提供标准化集成接口与开放能力。\n")
    lines += [
        f"### 关键技术选型\n",
        f"本方案的关键技术选型由我方技术栈与本项目实际需求共同确定，"
        f"具体厂商 / 产品 / 版本待 L3 领域插件层提供。\n",
    ]
    return "\n".join(lines)


def _render_section_04(intake_data: dict) -> str:
    """04 方案亮点 / 反推差异化 / 每痛点对应 1 亮点."""
    pains = _list_field(intake_data, "core_pain_points")
    existing = _list_field(intake_data, "existing_systems")

    lines = [
        f"## 方案亮点\n",
        f"本方案相对常规做法的差异化优势如下：\n",
    ]
    if not pains:
        lines.append(f"### 亮点 1 {PLACEHOLDER}\n")
        lines.append(f"{PLACEHOLDER}\n")
    else:
        for idx, p in enumerate(pains, 1):
            short = p[:30] + ("..." if len(p) > 30 else "")
            lines.append(f"### 亮点 {idx} 针对 {short} 的差异化设计\n")
            lines.append(
                f"针对该痛点，本方案采用区别于常规集成模式的设计思路，"
                f"实质性提升业务运行效率。\n"
            )
    if existing:
        idx = len(pains) + 1 if pains else 1
        lines.append(f"### 亮点 {idx} 与现有系统的深度协同\n")
        lines.append(
            f"区别于一次性数据导入的常规做法，本方案与 {'、'.join(existing[:2])} 等现有系统"
            f"建立持续协同机制。\n"
        )
    return "\n".join(lines)


def _render_section_05(intake_data: dict) -> str:
    """05 类似案例 / reference_cases 逐条 + 承担工作【待补充】."""
    refs = _list_field(intake_data, "reference_cases")
    client_industry = _field(intake_data, "client_industry")

    lines = [
        f"## 类似案例\n",
        f"我方在 {client_industry} 领域的类似交付案例如下：\n",
    ]
    if not refs:
        lines.append(f"{PLACEHOLDER}\n")
    else:
        for idx, case in enumerate(refs, 1):
            ordinal = ["一", "二", "三", "四", "五", "六", "七", "八"][min(idx - 1, 7)]
            lines += [
                f"### 案例{ordinal} {case}\n",
                f"- 客户行业：{client_industry}",
                f"- 项目背景：贵公司在该项目中针对类似业务场景进行了平台化建设。",
                f"- 我方承担工作：{PLACEHOLDER}（待 L3 领域插件层提供）",
                f"- 交付成果：{PLACEHOLDER}（待 L3 领域插件层提供）",
                "",
            ]
    return "\n".join(lines)


def _render_section_06(intake_data: dict) -> str:
    """06 报价概要 / 4 段 / budget_range + project_period."""
    budget = _field(intake_data, "budget_range")
    period = _field(intake_data, "project_period")

    lines = [
        f"## 报价概要\n",
        f"本节给出本次报价口径与构成。\n",
        f"### 报价总体口径\n",
        f"本次报价在贵单位预算范围 {budget} 内，按本方案的功能与服务范围进行配置。\n",
        f"### 阶段划分\n",
        f"基于 {period} 的总体安排，报价按建设期与运维期分阶段构成。\n",
        f"### 主要项构成\n",
        f"- 软件许可",
        f"- 硬件设备（如有）",
        f"- 系统集成与实施",
        f"- 项目培训",
        f"- 运维服务（运维期）\n",
        f"### 报价说明\n",
        f"本报价含税口径，有效期 90 天，付款节奏按建设期分期与运维期年度结算执行。\n",
    ]
    return "\n".join(lines)


_RENDERERS = {
    "01": _render_section_01,
    "02": _render_section_02,
    "03": _render_section_03,
    "04": _render_section_04,
    "05": _render_section_05,
    "06": _render_section_06,
}


def _render_assets_block(section_assets: dict | None) -> str:
    """M7-k 高-2: 消费 S2 产出的本 section 素材 (assets.json 的 sections[<id>])。

    acquired 的 content 拼成支撑句进正文 / 待补充的素材点位落【待补充】(不编造 / 红线 3)。
    section_assets=None (未传 / 向后兼容) → 空串。demo fixture / 真实 agent 自读自消费。
    """
    if not section_assets:
        return ""
    acquired = section_assets.get("acquired") or []
    parts: list[str] = []
    for item in acquired:
        atype = item.get("asset_type", "")
        if item.get("status") == "acquired" and item.get("content"):
            parts.append(f"依据已获取的{atype}素材：{item['content']}")
        else:
            parts.append(f"（{atype}相关素材尚未获取，此处{PLACEHOLDER}。）")
    if not parts:
        return ""
    return "\n" + "\n\n".join(parts) + "\n"


def generate_section_content(
    section_id: str,
    section_title: str,
    section_prompt: str,
    intake_data: dict,
    intake_fields: list,
    system_prompt: str,
    stage_prompt: str,
    domain_plugin: str,
    section_assets: dict | None = None,
) -> str:
    """
    Stub 实现 / 按 section_id 分支渲染 proposal-document 6 section markdown.

    M5 替换点: 函数体替换为 anthropic.Anthropic().messages.create(...) 调用 /
    入参拼装 system_prompt + stage_prompt + section_prompt + intake_data 投喂 LLM /
    本文件 + scripts/llm_stub.py 一起退场.
    M7-k 高-2: section_assets (S2 产出该 section 素材) / 默认 None 向后兼容.
    """
    renderer = _RENDERERS.get(section_id)
    if renderer is None:
        return (
            f"## {section_title}\n\n"
            f"{PLACEHOLDER} (section_id={section_id} 未注册 demo-local stub renderer)\n"
        )
    return renderer(intake_data) + _render_assets_block(section_assets)
