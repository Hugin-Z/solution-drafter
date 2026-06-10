# -*- coding: utf-8 -*-
"""
_demo_assets.py · demo 共享 fixture：从 outline asset_needs 生成 S2 产物 assets.json

S2 素材链：真实 agent 用其手段(RAG/ripgrep/SQL/网络/人工)逐 section 获取素材产 assets.json。
demo 没有真实手段环境 → 用本 fixture 模拟"agent 获取到素材"的产物(示例素材 / source=demo-fixture),
展示 S2→S4 素材链的产物形态。真实 agent 不调本文件 / 自己用手段产 assets.json(见 prompts/stages/s2-acquire.md)。

手段无关结构: section → {asset_needs, acquired[{asset_type, status, content, source}]}
无任何手段特有字段(无 relevance score / embedding / query)。
"""

from __future__ import annotations


def build_demo_assets(outline_cfg: dict) -> dict:
    """从 outline 的每 section asset_needs 生成 fixture assets.json。

    fixture 策略(展示"有素材 vs 无素材"):
    - 每 section 的 asset_needs:前 N-1 个标 acquired(示例素材 content + source=demo-fixture),
      最后 1 个(若 >1)标 待补充(展示无素材→S4【待补充】链)。
    - asset_needs 仅 1 个的 → acquired(保证 demo 不全待补充)。
    真实 agent 按 s2-acquire.md 用真实手段获取 / 不走本 fixture 逻辑。
    """
    sections: dict = {}
    for sec in outline_cfg.get("outline", []):
        sid = sec["id"]
        needs = sec.get("asset_needs", []) or []
        acquired = []
        for i, atype in enumerate(needs):
            # 最后一个且 needs>1 → 待补充 (展示后果链) / 其余 acquired
            if len(needs) > 1 and i == len(needs) - 1:
                acquired.append({
                    "asset_type": atype, "status": "待补充",
                    "content": None, "source": None,
                })
            else:
                acquired.append({
                    "asset_type": atype, "status": "acquired",
                    "content": f"【示例素材:{atype}】(demo fixture / 真实 agent 用其手段获取)",
                    "source": "demo-fixture",
                })
        sections[sid] = {"asset_needs": needs, "acquired": acquired}
    return {"doc_type": outline_cfg.get("doc_type"), "sections": sections}
