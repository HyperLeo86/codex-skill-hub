#!/usr/bin/env python3
"""Semantic Compiler 辅助模块（v0.2）。

职责（允许 LLM 参与语义判断）：
- Claim Extraction / Task Recognition / Priority / Uncertainty / Provenance
- 组装 Core PIR + Task View

本模块只提供确定性辅助函数与契约常量；语义判断由 LLM / 上游完成。
Renderer 层禁止 import 本模块做语义判断（职责分层）。
"""
import json
from datetime import datetime, timezone

EPISTEMIC_STATES = {"VERIFIED", "UNKNOWN", "UNMEASURED", "UNSTABLE", "UNVERIFIED", "N/A"}
DERIVATION_TYPES = {"DIRECT_FACT", "DERIVED", "INTERPRETATION", "ASSUMPTION"}
TASKS = {"browse", "compare", "diagnose", "decide", "learn", "monitor"}
VIEW_TYPES = {"decision", "diagnosis", "comparison", "monitor", "browse", "learning"}
PRIORITIES = {"critical", "important", "supporting", "technical"}

_TASK_HINTS = {
    "compare": ["对比", "比较", "vs", "差异", "选哪个"],
    "monitor": ["监控", "状态", "异常", "告警", "变化"],
    "diagnose": ["问题在哪", "定位", "排查", "故障", "为什么"],
    "decide": ["怎么办", "决定", "是否", "下一步", "行动"],
    "browse": ["浏览", "分类", "目录", "概览"],
    "learn": ["学习", "理解", "教程", "顺序"],
}


def build_meta(title, task, source, generated_at=None, version="0.2"):
    if task not in TASKS:
        raise ValueError(f"task 非法：{task!r}（允许 {sorted(TASKS)}）")
    if not title or not source:
        raise ValueError("title 与 source 必填")
    return {
        "title": title,
        "task": task,
        "source": source,
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "version": version,
    }


def make_evidence(id_, source_id, locator, verified, source_type=None, detail=None,
                  content_hash=None, snapshot=None, captured_at=None):
    ev = {
        "id": id_,
        "source_id": source_id,
        "locator": locator,
        "verified": bool(verified),
    }
    for key, val in (("source_type", source_type), ("detail", detail),
                     ("content_hash", content_hash), ("snapshot", snapshot),
                     ("captured_at", captured_at)):
        if val is not None:
            ev[key] = val
    return ev


def make_claim(claim_id, content, derivation_type, epistemic_state,
               priority="supporting", evidence=None, outcome=None):
    if derivation_type not in DERIVATION_TYPES:
        raise ValueError(f"derivation_type 非法：{derivation_type!r}")
    if epistemic_state not in EPISTEMIC_STATES:
        raise ValueError(f"epistemic_state 非法：{epistemic_state!r}")
    if priority not in PRIORITIES:
        raise ValueError(f"priority 非法：{priority!r}")
    claim = {
        "claim_id": claim_id,
        "content": content,
        "derivation_type": derivation_type,
        "epistemic_state": epistemic_state,
        "priority": priority,
    }
    if evidence:
        claim["evidence"] = list(evidence)
    if outcome is not None:
        claim["outcome"] = outcome
    return claim


def make_view(view_type, **fields):
    if view_type not in VIEW_TYPES:
        raise ValueError(f"view_type 非法：{view_type!r}")
    return {"type": view_type, **fields}


def build_pir(meta, summary, claims, evidence, view, relations=None,
              uncertainty=None, technical=None, metadata=None):
    pir = {
        "meta": meta,
        "summary": summary,
        "claims": list(claims),
        "evidence": list(evidence),
        "view": view,
    }
    for key, val in (("relations", relations), ("uncertainty", uncertainty),
                     ("technical", technical), ("metadata", metadata)):
        if val is not None:
            pir[key] = val
    return pir


def recognize_task_hint(text):
    """关键词启发式任务识别（LLM 不可用时的降级）；不确定返回 None。"""
    hits = [task for task, hints in _TASK_HINTS.items() if any(h in text for h in hints)]
    return hits[0] if len(hits) == 1 else None


def assumption_claims(claims):
    return [c for c in claims if c.get("derivation_type") == "ASSUMPTION"]


def to_json(pir):
    return json.dumps(pir, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    meta = build_meta("示例 PIR", "decide", "demo")
    ev = make_evidence("ev-1", "demo-source", "line 1", True, detail="示例证据")
    claim = make_claim("c-1", "示例结论", "DIRECT_FACT", "VERIFIED", priority="critical", evidence=["ev-1"])
    view = make_view("decision", state="OK", action="无")
    print(to_json(build_pir(meta, "示例摘要。", [claim], [ev], view)))
