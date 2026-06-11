# -*- coding: utf-8 -*-
"""
llm_stub_local.py · demo-local stub (implementation-plan 6 section)

⚠️ stub 退场说明 (非真实 agent 工作流路径):
demo fixture / 跑通 implementation-plan 端到端管道. 真实 agent 在 S4 自己读 section prompt 生成 / 不调本文件.
接口签名严格对齐 L1 scripts/llm_stub.py.generate_section_content.

section: 01 项目概述 / 02 实施方案 / 03 实施计划 / 04 组织保障 / 05 质量与风险保障 / 06 交付与验收
04 (own_team_size 字段) → 团队架构骨架 + 具体人数【待补充】.
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
    return [str(i) for i in v if i] if isinstance(v, list) else []


def _render_section_01(intake_data: dict, **kw) -> str:
    project_name = _field(intake_data, "project_name")
    client_name = _field(intake_data, "client_name")
    client_industry = _field(intake_data, "client_industry")
    pains = _list_field(intake_data, "core_pain_points")
    bg = (
        f"贵单位 {client_name} 作为 {client_industry}，在数字化建设中存在业务深化与协同需求。"
        if "【待补充】" not in (client_name + client_industry)
        else "基于前期沟通材料，项目建设背景如下。"
    )
    if pains:
        bg += "主要建设动因包括：" + "；".join(pains[:3]) + "。"
    return (
        f"## 项目概述\n\n"
        f"本节概述 {project_name} 的实施背景与总体目标。\n\n"
        f"### 项目背景\n\n{bg}\n\n"
        f"### 建设目标\n\n"
        f"本次实施旨在围绕业务需求构建相应平台与应用能力，提升整体数字化治理水平。\n\n"
        f"### 实施范围\n\n"
        f"本方案覆盖平台部署、数据治理、业务应用建设与系统集成等实施内容。\n"
    )


def _render_section_02(intake_data: dict, **kw) -> str:
    pains = _list_field(intake_data, "core_pain_points")
    existing = _list_field(intake_data, "existing_systems")
    main_line = (
        f"针对贵单位 {len(pains)} 项核心需求分线推进，覆盖平台部署、数据治理与业务应用建设。"
        if pains else "按平台部署、数据治理与业务应用建设分线推进。"
    )
    sys_line = (
        f"与贵单位现有的 {'、'.join(existing[:3])} 等系统完成数据与接口衔接。"
        if existing else f"与现有系统的衔接范围{PLACEHOLDER}。"
    )
    return (
        f"## 实施方案\n\n"
        f"本节给出本项目的总体实施方案与技术路线。\n\n"
        f"### 实施方法论\n\n"
        f"采用分阶段迭代、原型先行、数据驱动的实施方法，确保过程可控、成果可验证。\n\n"
        f"### 实施主线\n\n{main_line}\n\n"
        f"### 系统衔接\n\n{sys_line}\n"
    )


def _render_section_03(intake_data: dict, **kw) -> str:
    period = _field(intake_data, "project_period")
    return (
        f"## 实施计划\n\n"
        f"本节给出本项目的实施计划与阶段安排。\n\n"
        f"### 阶段划分\n\n"
        f"基于 {period} 的总体安排，实施划分为需求调研、方案设计、开发部署、数据治理、试运行与验收等阶段。\n\n"
        f"### 里程碑计划\n\n"
        f"| 阶段 | 周期 | 关键交付物 |\n"
        f"|---|---|---|\n"
        f"| 需求调研 | {PLACEHOLDER} | 需求规格说明 |\n"
        f"| 方案设计 | {PLACEHOLDER} | 详细设计文档 |\n"
        f"| 开发部署 | {PLACEHOLDER} | 平台与应用上线 |\n"
        f"| 数据治理 | {PLACEHOLDER} | 数据汇聚成果 |\n"
        f"| 试运行与验收 | {PLACEHOLDER} | 验收报告 |\n\n"
        f"各阶段周期依据 {period} 细化，确保进度可控。\n"
    )


def _render_section_04(intake_data: dict, **kw) -> str:
    return (
        f"## 组织保障\n\n"
        f"本节给出本项目的组织保障与团队配置。\n\n"
        f"### 项目组织架构\n\n"
        f"项目设项目总负责人、项目经理、技术负责人、实施工程师、质量与测试、运维支持等角色层级。\n\n"
        f"### 角色职责\n\n"
        f"项目经理负责整体计划与协调；技术负责人负责技术方案与质量；实施工程师负责部署与开发；"
        f"质量与测试负责验证；运维支持负责上线后保障。\n\n"
        f"### 人员配置\n\n"
        f"具体团队规模、高级工程师占比与实施团队配置 {PLACEHOLDER}"
        f"（待 L3 领域插件 company-profile 的 own_team_size 字段补充）。\n"
    )


def _render_section_05(intake_data: dict, **kw) -> str:
    return (
        f"## 质量与风险保障\n\n"
        f"本节给出本项目的质量保障与风险控制措施。\n\n"
        f"### 质量保障体系\n\n"
        f"建立阶段评审、测试验证、文档规范与变更控制机制，保障实施过程质量。\n\n"
        f"### 风险识别与应对\n\n"
        f"| 风险类别 | 风险描述 | 应对措施 |\n"
        f"|---|---|---|\n"
        f"| 数据质量 | 多源数据质量参差 | 建立数据校验与清洗机制 |\n"
        f"| 系统集成 | 与现有系统对接复杂 | 提前接口梳理与联调 |\n"
        f"| 实施进度 | 阶段交付延期 | 里程碑管控与资源调配 |\n"
        f"| 需求变更 | 需求范围调整 | 变更评审与版本控制 |\n"
    )


def _render_section_06(intake_data: dict, **kw) -> str:
    refs = _list_field(intake_data, "reference_cases")
    lines = [
        f"## 交付与验收\n",
        f"本节给出本项目的交付物与验收标准。\n",
        f"### 交付物清单\n",
        f"- 软件系统",
        f"- 部署与运维文档",
        f"- 操作手册",
        f"- 培训材料",
        f"- 验收报告\n",
        f"### 验收标准\n",
        f"按初验、试运行、终验分阶段验收，验收依据合同与本方案约定的范围与功能。\n",
    ]
    if refs:
        lines.append("### 同类项目参照\n")
        lines.append(f"参照 {refs[0]} 等同类项目的交付与验收经验组织本项目交付。\n")
    return "\n".join(lines)


_RENDERERS = {
    "01": _render_section_01, "02": _render_section_02, "03": _render_section_03,
    "04": _render_section_04, "05": _render_section_05, "06": _render_section_06,
}


def _render_assets_block(section_assets: dict | None) -> str:
    """消费 S2 产出的本 section 素材 (assets.json 的 sections[<id>])。

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
    section_id: str, section_title: str, section_prompt: str,
    intake_data: dict, intake_fields: list,
    system_prompt: str, stage_prompt: str, domain_plugin: str,
    section_assets: dict | None = None,
) -> str:
    renderer = _RENDERERS.get(section_id)
    if renderer is None:
        return f"## {section_title}\n\n{PLACEHOLDER} (section_id={section_id} 未注册 renderer)\n"
    return renderer(intake_data) + _render_assets_block(section_assets)
