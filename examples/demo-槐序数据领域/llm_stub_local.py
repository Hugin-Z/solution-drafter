# -*- coding: utf-8 -*-
"""
llm_stub_local.py · demo-local stub (proposal-document doc_type / 领域插件演示)

本文件是 demo fixture（非真实 agent 工作流路径）。真实 agent 跑 SKILL.md 工作流时，
在 S4 阶段不调本文件 / agent 自己读 section prompt + domain plugin 生成 markdown。
本 stub 仅用于端到端 demo 跑通管道连通性 + 演示 L3 领域插件切换的效果。

领域插件演示点：同一个 01-company-strength.md section prompt，
- 绑定默认空领域 → §01 公司实力整段【待补充】；
- 绑定真实领域插件（本 demo 的 槐序数据）→ _render_section_01 正则解析 domain_plugin 的
  ## own_* 4 段并填充。找不到 ## own_xxx 段时返回【待补充】（不编造 / 不报错）。

接口签名严格对齐 L1 scripts/llm_stub.py.generate_section_content / 不变.
M5 真实 LLM 接入时本文件与 demo-解决方案建议书/llm_stub_local.py + L1 stub 一起退场.
"""

from __future__ import annotations

import re


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


def _parse_domain_section(domain_plugin: str, section_name: str) -> str:
    """
    从 domain_plugin 字面里抓 `## <section_name>\n\n<内容>\n\n(##|EOF)` 段.

    段缺失行为 (不虚构 / 不报错):
    - 找不到段 → 返回 PLACEHOLDER (不报错)
    - 段内仅含 PLACEHOLDER / 空白 → 返回 PLACEHOLDER (透传)

    输入: domain_plugin (拼接 4 文件后的字面 / 含 ## own_company_brief / ## own_qualifications / ...)
    返回: section 内容 str / 或 PLACEHOLDER.

    边界 (M7-d 修): lookahead 在下一个 h1 或 h2 (^#{1,2}\s) 或 EOF 停。
    own_team_size 是 company-profile.md 最后一个 h2 / 其后拼接的 glossary.md 以 # (h1) 开头 /
    若 lookahead 只认 h2 会越过 h1 把下一文件整段吞入捕获 → draft 正文泄漏 domain 源标题。
    h1+h2 都作边界后 own_team_size 捕获停在 `# glossary` 前 / 不泄漏。
    """
    pattern = re.compile(
        rf"^##\s+{re.escape(section_name)}\s*\n+(.*?)(?=^#{{1,2}}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(domain_plugin)
    if not m:
        return PLACEHOLDER
    content = m.group(1).strip()
    if not content:
        return PLACEHOLDER
    # 段内仅【待补充】视为缺失透传
    if content == PLACEHOLDER or content.startswith(PLACEHOLDER):
        return content   # 保留【待补充】+ 可能的占位说明
    return content


def _render_section_01(intake_data: dict, domain_plugin: str = "") -> str:
    """
    01 公司实力 / 真读 domain_plugin 解析 own_* 4 段 / 段缺失返回【待补充】.

    领域插件演示点: domain_plugin 绑定真实领域时本段由 own_* 字段填充.
    """
    brief = _parse_domain_section(domain_plugin, "own_company_brief")
    quals = _parse_domain_section(domain_plugin, "own_qualifications")
    certs = _parse_domain_section(domain_plugin, "own_certifications")
    team = _parse_domain_section(domain_plugin, "own_team_size")

    # 4 段全缺失 (典型: 默认空领域) → 整段【待补充】
    if brief == PLACEHOLDER and quals == PLACEHOLDER and certs == PLACEHOLDER and team == PLACEHOLDER:
        return (
            f"## 公司实力\n\n"
            f"{PLACEHOLDER}\n\n"
            f"（待 L3 领域插件层提供以下 4 个字段后填充：\n"
            f"own_company_brief / own_qualifications / own_certifications / own_team_size。）\n"
        )

    return (
        f"## 公司实力\n\n"
        f"### 公司简介\n\n{brief}\n\n"
        f"### 资质与认证\n\n{quals}\n\n"
        f"### 产品与技术储备\n\n{certs}\n\n"
        f"### 团队与行业经验\n\n{team}\n"
    )


def _render_section_02(intake_data: dict, domain_plugin: str = "") -> str:
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


def _render_section_03(intake_data: dict, domain_plugin: str = "") -> str:
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


def _render_section_04(intake_data: dict, domain_plugin: str = "") -> str:
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


def _render_section_05(intake_data: dict, domain_plugin: str = "") -> str:
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


def _render_section_06(intake_data: dict, domain_plugin: str = "") -> str:
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
    stub: 接口签名严格对齐 L1 scripts/llm_stub.py.generate_section_content.
    仅 _render_section_01 真读 domain_plugin 填充 own_* / 其他 5 段不变.
    M7-k 高-2: section_assets (S2 产出该 section 素材) / 默认 None 向后兼容.
    """
    renderer = _RENDERERS.get(section_id)
    if renderer is None:
        return (
            f"## {section_title}\n\n"
            f"{PLACEHOLDER} (section_id={section_id} 未注册 demo-local stub renderer)\n"
        )
    return renderer(intake_data, domain_plugin) + _render_assets_block(section_assets)
