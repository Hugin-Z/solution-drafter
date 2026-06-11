# -*- coding: utf-8 -*-
"""
llm_stub.py · LLM 调用 stub (端到端管道验证 / 真实接 LLM API 时替换实现)

⚠️ stub 退场说明 (非真实 agent 工作流路径):
本文件是 tests / demo fixture / 用于端到端 demo 跑通管道连通性 + tests CI.
真实 agent 工作流 (Claude Code / Cline 跑 SKILL.md) 在 S4 阶段不调本文件 / agent 自己读
prompts/sections/<doc_type>/*.md + domain plugin / 自己生成 section markdown.
本 stub 不删 (tests 仍依赖 / fixture 价值) / 仅声明 SKILL.md S4 不走 stub 路径.
详见仓库根 SKILL.md "stub 与真实工作流的关系" 段.

接口契约:
- 函数: generate_section_content(...)
- 入参: section_id / section_title / section_prompt / intake_data / intake_fields
        / system_prompt / stage_prompt / domain_plugin
- 出参: str (markdown / 含 ## <title> + 正文)

stub 实现策略:
- 按 section_id 分支
- 用 intake_data + intake_fields 拼装 markdown
- 缺失字段填"【待补充】" (沿红线 4 / 不外泄内部术语 / 不虚构事实)

真实接入替换:
- 同函数签名 / 同返回类型
- 函数体内 stub 逻辑 → 调 anthropic.Anthropic().messages.create(...)
- 调用方 (run.py) 主流程零改动
"""

from __future__ import annotations


PLACEHOLDER = "【待补充】"


def _field(intake_data: dict, key: str) -> str:
    """取 intake_data 字段值 / 缺失或 null 返回占位字面."""
    v = intake_data.get(key)
    if v is None or v == "" or v == []:
        return PLACEHOLDER
    return str(v)


def _list_field(intake_data: dict, key: str) -> list[str]:
    """取 list 字段 / 缺失返回空 list."""
    v = intake_data.get(key)
    if not isinstance(v, list):
        return []
    return [str(item) for item in v if item]


def _render_section_01(intake_data: dict) -> str:
    project_name = _field(intake_data, "project_name")
    client_name = _field(intake_data, "client_name")
    client_industry = _field(intake_data, "client_industry")
    return (
        f"## 项目背景\n\n"
        f"本项目名称为 {project_name}，建设单位为 {client_name}。"
        f"贵单位作为 {client_industry}，承担相应领域的业务管理与公共服务职能。\n\n"
        f"近年来，行业数字化进程持续推进，业务系统建设逐步从单点应用走向平台化整合。"
        f"贵单位在长期业务实践中积累了多源数据与既有系统能力，亟需通过本项目实现统一汇聚与协同应用。"
        f"本次建设的 {project_name} 即承接这一背景而提出。\n"
    )


def _render_section_02(intake_data: dict) -> str:
    pains = _list_field(intake_data, "core_pain_points")
    existing = _list_field(intake_data, "existing_systems")
    lines = [
        "## 客户痛点\n",
        "经与贵单位前期沟通梳理，目前业务运行中存在以下痛点：\n",
    ]
    if not pains:
        lines.append(f"- {PLACEHOLDER}\n")
    else:
        for p in pains:
            lines.append(f"- {p}\n")
    lines.append("")
    if existing:
        lines.append(
            f"上述痛点与贵单位现有的 {len(existing)} 个业务系统的能力边界相关，"
            f"具体涉及 {existing[0]} 等系统。\n"
        )
    return "\n".join(lines)


def _render_section_03(intake_data: dict) -> str:
    pains = _list_field(intake_data, "core_pain_points")
    existing = _list_field(intake_data, "existing_systems")
    lines = [
        "## 功能需求\n",
        "针对上节梳理的痛点，本项目对新建系统提出以下功能需求：\n",
    ]
    if not pains:
        lines.append(f"### F1 {PLACEHOLDER}\n")
        lines.append(f"{PLACEHOLDER}\n")
    else:
        for idx, p in enumerate(pains, 1):
            lines.append(f"### F{idx} 针对 {p[:20]}... 的能力建设\n")
            lines.append(
                f"系统应具备处理该痛点的能力，"
                f"提供相应业务功能以缓解上述现状。\n"
            )
    if existing:
        idx = len(pains) + 1
        lines.append(f"### F{idx} 与现有系统的对接集成\n")
        lines.append(
            f"系统应支持与 {'、'.join(existing[:2])} 等现有系统的接口对接，"
            f"实现数据互通与业务协同。\n"
        )
    return "\n".join(lines)


def _render_section_04(intake_data: dict) -> str:
    existing = _list_field(intake_data, "existing_systems")
    refs = _list_field(intake_data, "reference_cases")
    lines = [
        "## 技术架构概述\n",
        "本系统采用分层技术架构，覆盖数据、平台、应用、集成四个层面：\n",
        "### 数据层\n",
        "采用统一的数据汇聚与存储技术路线，支持结构化与非结构化数据的混合管理。\n",
        "### 平台层\n",
        "提供基础能力服务，包括数据治理、服务注册、统一认证等中台能力。\n",
        "### 应用层\n",
        "面向业务用户提供功能交互界面，支持桌面端与移动端访问。\n",
        "### 集成层\n",
    ]
    if existing:
        lines.append(
            f"通过标准接口与贵单位现有的 {'、'.join(existing[:3])} 等系统进行对接，"
            f"实现数据与业务协同。\n"
        )
    else:
        lines.append(f"{PLACEHOLDER}\n")
    if refs:
        lines.append(f"本架构思路参考 {refs[0]} 等同类项目的实践经验。\n")
    lines.append("**【图 4.1: 总体技术架构示意图】**\n")
    return "\n".join(lines)


def _render_section_05(intake_data: dict) -> str:
    project_period = _field(intake_data, "project_period")
    return (
        f"## 非功能需求\n\n"
        f"本系统需满足以下非功能性要求：\n\n"
        f"### 性能\n\n"
        f"系统应满足行业典型量级的响应时间与并发承载，支撑日常业务平稳运行。\n\n"
        f"### 可用性\n\n"
        f"基于 {project_period} 的总体周期，建设期内提供基础可用保障，"
        f"运维期内提供持续可用性服务，重要业务时段保持稳定运行。\n\n"
        f"### 安全\n\n"
        f"系统应满足相应等级的网络安全保护要求，"
        f"数据传输与存储应采用加密保护，访问应基于角色与权限管控。\n\n"
        f"### 兼容性\n\n"
        f"系统应兼容主流浏览器与操作系统，"
        f"对外接口应遵循行业通用标准，便于与现有系统对接。\n\n"
        f"### 扩展性\n\n"
        f"架构应支持后续用户规模与数据量的增长，"
        f"业务功能模块可按需扩展，避免重大重构。\n"
    )


def _render_section_06(intake_data: dict) -> str:
    project_period = _field(intake_data, "project_period")
    budget_range = _field(intake_data, "budget_range")
    lines = [
        "## 实施计划\n",
        f"基于 {project_period} 的总体安排，本项目按以下节奏推进：\n",
        "### 阶段一：规划设计\n",
        "建设期前期，开展需求细化、方案设计与技术选型评审。"
        "关键交付物为详细设计方案与系统总体技术规范。\n",
        "### 阶段二：建设开发\n",
        "建设期中期，完成核心功能开发、数据接入与界面实现。"
        "关键交付物为系统功能模块与集成接口。\n",
        "### 阶段三：测试验收\n",
        "建设期末期，开展系统测试、用户验收与试运行。"
        "关键交付物为测试报告与验收材料。\n",
        "### 阶段四：运维保障\n",
        "进入运维期，提供运行维护、故障响应与版本演进服务。"
        "关键交付物为运维记录与月度报告。\n",
    ]
    if budget_range != PLACEHOLDER:
        lines.append(
            f"### 投入节奏\n\n"
            f"总体预算安排为 {budget_range}，"
            f"按建设期与运维期分阶段投入。\n"
        )
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
    """消费 S2 产出的本 section 素材 (assets.json 的 sections[<id>])。

    acquired 的 content 拼成支撑句进正文 / 待补充的素材点位落【待补充】(不编造 / 红线 3)。
    section_assets=None (未传 / 向后兼容) → 空串 (不破坏旧调用)。

    注: 本 stub 是 demo fixture (非真 LLM)。真实 agent 自读 assets.json 自行消费
    (见 prompts/stages/s4-generate.md + 各 section prompt 的 "素材运用" 小节)。
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
    Stub 实现 / 按 section_id 分支渲染 markdown.

    真实接入替换点: 函数体替换为 anthropic.Anthropic().messages.create(...) 调用,
    入参拼装 system_prompt + stage_prompt + section_prompt + intake_data
    + section_assets (S2 产出该 section 素材) 投喂 LLM, 返回 LLM 输出的 markdown 字面.

    section_assets = assets.json["sections"][<id>] (S2 产出 / 强依赖)。
    默认 None 向后兼容。
    """
    renderer = _RENDERERS.get(section_id)
    if renderer is None:
        return (
            f"## {section_title}\n\n"
            f"{PLACEHOLDER} (section_id={section_id} 未注册 stub renderer)\n"
        )
    return renderer(intake_data) + _render_assets_block(section_assets)
