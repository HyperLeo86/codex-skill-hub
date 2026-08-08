#!/usr/bin/env python3
"""Regression runner: unit, golden, boundary, calibration, score, cache, render."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(script: str, *args: str):
    return subprocess.run(
        [PY, str(ROOT / "scripts" / script), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def parse_stdout(proc):
    return json.loads(proc.stdout.strip().splitlines()[-1])


def test_protocol_hash_determinism():
    p1 = run("protocol_hash.py", "--protocol-dir", str(ROOT / "protocol"))
    p2 = run("protocol_hash.py", "--protocol-dir", str(ROOT / "protocol"))
    if p1.returncode != 0 or p2.returncode != 0:
        return False, f"exit {p1.returncode}/{p2.returncode}"
    h1, h2 = parse_stdout(p1)["protocol_hash"], parse_stdout(p2)["protocol_hash"]
    return h1 == h2, f"hash={h1[:16]}…"


def test_snapshot_determinism():
    with tempfile.TemporaryDirectory() as td:
        out1, out2 = Path(td) / "b1.json", Path(td) / "b2.json"
        r1 = run("build_snapshot.py", "--target", str(ROOT / "tests/golden/pure-skill"), "--skill-file", "SKILL.md.fixture", "--out", str(out1))
        r2 = run("build_snapshot.py", "--target", str(ROOT / "tests/golden/pure-skill"), "--skill-file", "SKILL.md.fixture", "--out", str(out2))
        if r1.returncode != 0 or r2.returncode != 0:
            return False, f"exit {r1.returncode}/{r2.returncode}"
        h1, h2 = parse_stdout(r1)["evidence_bundle_hash"], parse_stdout(r2)["evidence_bundle_hash"]
        return h1 == h2, f"bundle_hash={h1[:16]}…"


def test_static_golden():
    with tempfile.TemporaryDirectory() as td:
        bundle, facts = Path(td) / "bundle.json", Path(td) / "facts.json"
        run("build_snapshot.py", "--target", str(ROOT / "tests/golden/pure-skill"), "--skill-file", "SKILL.md.fixture", "--out", str(bundle))
        proc = run("static_checks.py", "--bundle", str(bundle), "--facts-out", str(facts))
        out = parse_stdout(proc)
        return out["pass"] and out["pass_rate"] == 1.0, f"pass_rate={out['pass_rate']} failed={out['failed']}"


def test_static_boundary():
    with tempfile.TemporaryDirectory() as td:
        bundle, facts = Path(td) / "bundle.json", Path(td) / "facts.json"
        run("build_snapshot.py", "--target", str(ROOT / "tests/boundary/missing-reference"), "--skill-file", "SKILL.md.fixture", "--out", str(bundle))
        proc = run("static_checks.py", "--bundle", str(bundle), "--facts-out", str(facts))
        out = parse_stdout(proc)
        return "references_resolve" in out["failed"], f"failed={out['failed']}"


def test_decision_cases(kind: str, rel_path: str):
    cases = json.loads((ROOT / rel_path).read_text(encoding="utf-8"))
    results = []
    with tempfile.TemporaryDirectory() as td:
        for case in cases:
            feat = Path(td) / f"{case['id']}.json"
            feat.write_text(json.dumps({"features": case["features"]}, ensure_ascii=False), encoding="utf-8")
            proc = run(
                "decision_engine.py",
                "--features", str(feat),
                "--audit-status", case.get("audit_status", "CERTIFIED"),
                "--out", str(Path(td) / "out.json"),
            )
            out = parse_stdout(proc) if proc.returncode == 0 else {"lifecycle_decision": "ERROR", "lifecycle_status": "ERROR", "provisional_direction": None}
            exp = case["expected"]
            ok = (
                out.get("lifecycle_decision") == exp["lifecycle_decision"]
                and out.get("lifecycle_status") == exp["lifecycle_status"]
                and out.get("provisional_direction") == exp.get("provisional_direction")
            )
            results.append((case["id"], ok, f"{out.get('lifecycle_decision')}/{out.get('lifecycle_status')}/{out.get('provisional_direction')}"))
    failed = [r for r in results if not r[1]]
    return not failed, f"{len(results) - len(failed)}/{len(results)} passed; failed={[r[0] for r in failed]}"


def _semantic_file(path: Path, fields: dict):
    path.write_text(json.dumps({"features": fields}, ensure_ascii=False), encoding="utf-8")


def test_evidence_verify_valid():
    with tempfile.TemporaryDirectory() as td:
        sem = Path(td) / "s.json"
        _semantic_file(sem, {"identity_clear": {"value": "YES", "evidence": [{"file": "SKILL.md.fixture", "line_start": 1, "line_end": 3}]}})
        proc = run("verify_evidence.py", "--target", str(ROOT / "tests/golden/pure-skill"), "--semantic", str(sem), "--out", str(Path(td) / "v.json"))
        out = parse_stdout(proc)
        return out["verified_fields"] == 1 and out["unknown_fields"] == [], f"out={out}"


def test_evidence_verify_invalid():
    with tempfile.TemporaryDirectory() as td:
        sem = Path(td) / "s.json"
        _semantic_file(sem, {"identity_clear": {"value": "YES", "evidence": [{"file": "SKILL.md.fixture", "line_start": 9999, "line_end": 10000}]}})
        proc = run("verify_evidence.py", "--target", str(ROOT / "tests/golden/pure-skill"), "--semantic", str(sem), "--out", str(Path(td) / "v.json"))
        out = parse_stdout(proc)
        return out["verified_fields"] == 0 and out["unknown_fields"] == ["identity_clear"], f"out={out}"


def test_repro_gate(expected_status: str, diff: bool, independent: bool):
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "a.json", Path(td) / "b.json"
        _semantic_file(a, {"identity_clear": "YES", "unique_value": "YES"})
        _semantic_file(b, {"identity_clear": "YES", "unique_value": "NO" if diff else "YES"})
        cmd = ["--run-a", str(a), "--run-b", str(b), "--critical-fields", "identity_clear,unique_value", "--out", str(Path(td) / "r.json")]
        if independent:
            cmd.append("--independent")
        proc = run("compare_semantic_runs.py", *cmd)
        out = parse_stdout(proc)
        return out["semantic_status"] == expected_status, f"status={out['semantic_status']} agreement={out['semantic_agreement']}"


def test_decision_withheld():
    with tempfile.TemporaryDirectory() as td:
        feat = Path(td) / "f.json"
        _semantic_file(feat, {"identity_clear": "UNKNOWN", "value_established": "YES"})
        proc = run("decision_engine.py", "--features", str(feat), "--audit-status", "CERTIFIED", "--out", str(Path(td) / "o.json"))
        out = parse_stdout(proc)
        ok = out["lifecycle_decision"] is None and out["lifecycle_status"] == "WITHHELD"
        return ok, f"decision={out['lifecycle_decision']} status={out['lifecycle_status']} missing={out['missing_fields']}"


def test_audit_status_gate():
    with tempfile.TemporaryDirectory() as td:
        feat = Path(td) / "f.json"
        _semantic_file(feat, {"identity_clear": "YES"})
        proc = run("decision_engine.py", "--features", str(feat), "--audit-status", "UNSTABLE", "--out", str(Path(td) / "o.json"))
        out = parse_stdout(proc)
        ok = out["lifecycle_decision"] is None and out["lifecycle_status"] == "WITHHELD"
        return ok, f"decision={out['lifecycle_decision']} status={out['lifecycle_status']}"


def test_cache_content_addressed():
    with tempfile.TemporaryDirectory() as td:
        cache = Path(td) / "cache"
        ev, ph = "e" * 64, "p" * 64
        key_proc = run("audit_cache.py", "--evidence-hash", ev, "--protocol-hash", ph, "--cache-dir", str(cache))
        key = parse_stdout(key_proc)["audit_key"]
        result = {"audit_key": key, "audit_status": "CERTIFIED", "lifecycle_decision": "KEEP"}
        res = Path(td) / "r.json"
        res.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        run("audit_cache.py", "--evidence-hash", ev, "--protocol-hash", ph, "--cache-dir", str(cache), "--store", str(res))
        g1 = parse_stdout(run("audit_cache.py", "--evidence-hash", ev, "--protocol-hash", ph, "--cache-dir", str(cache), "--get"))
        g2 = parse_stdout(run("audit_cache.py", "--evidence-hash", ev, "--protocol-hash", ph, "--cache-dir", str(cache), "--get"))
        ok = g1["cache"] == "HIT" and g1["result"] == g2["result"] and g1["result"]["audit_key"] == key
        return ok, f"key={key[:16]}… hit={g1['cache']}"


def test_render_determinism():
    with tempfile.TemporaryDirectory() as td:
        result = {
            "audit_key": "k",
            "target_skill": "demo",
            "target_snapshot_hash": "s",
            "evidence_bundle_hash": "e",
            "protocol_version": "1.2.0",
            "protocol_hash": "p",
            "audit_status": "INSUFFICIENT_EVIDENCE",
            "health_score": 87,
            "health_score_status": "PARTIAL",
            "maturity_level": {"level": "L3", "name": "Tested"},
            "certification_level": {"level": "C1", "name": "EvidenceCollected"},
            "scope": "full",
            "lifecycle_decision": None,
            "lifecycle_status": "WITHHELD",
            "withheld_reason": "missing_required_evidence",
            "missing_fields": ["usage_frequency"],
            "provisional_direction": "KEEP_CANDIDATE",
            "reproducibility": "UNVERIFIED",
            "blocker_count": 2,
            "p1_blocker_count": 2,
            "blockers": [
                {"priority": "P1", "gap": "缺少真实 Usage Evidence", "impact": "无法判断长期必要性"},
                {"priority": "P1", "gap": "未完成独立语义复现", "impact": "无法认证"},
            ],
            "findings": {"Identity": {"status": "healthy", "evidence": "ev"}},
            "metrics": {
                "semantic_agreement": None,
                "snapshot_coverage": 0.8,
                "decision_evidence_coverage": 0.9375,
                "usage_coverage": 0.0,
                "behavior_coverage": 1.0,
                "reproducibility_coverage": 0.0,
            },
            "why": ["missing usage_frequency"],
            "impact": {"summary": "none", "details": []},
            "required_changes": ["收集真实 Usage Evidence", "独立执行两次 Semantic Extraction"],
        }
        res = Path(td) / "r.json"
        res.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        out1, out2 = Path(td) / "m1.md", Path(td) / "m2.md"
        out_en = Path(td) / "m-en.md"
        run("render_report.py", "--result", str(res), "--out", str(out1), "--locale", "zh-CN")
        run("render_report.py", "--result", str(res), "--out", str(out2), "--locale", "zh-CN")
        run("render_report.py", "--result", str(res), "--out", str(out_en), "--locale", "en")
        zh = out1.read_text(encoding="utf-8")
        main_part = zh.split("<details>")[0]
        same = out1.read_bytes() == out2.read_bytes()
        locale_works = out1.read_bytes() != out_en.read_bytes() and "核心状态" in zh
        structure_ok = all(
            token in zh
            for token in (
                "🧩 Skill Audit",
                "当前判断",
                "核心状态",
                "能力审计",
                "当前阻塞项",
                "覆盖情况",
                "生命周期判断",
                "审计元数据",
                "<details>",
                "暂缓裁决",
                "94%",
                "KEEP 候选",
            )
        )
        no_machine_noise = "0.9375" not in main_part and "WITHHELD（关键证据不足，未裁决） (WITHHELD)" not in zh
        return same and locale_works and structure_ok and no_machine_noise, f"same={same} locale={locale_works} structure={structure_ok} noise_ok={no_machine_noise}"


def _score_card_inputs(td: Path, target: Path, skill_file: str, behavior: dict):
    bundle, facts = Path(td) / "bundle.json", Path(td) / "facts.json"
    run("build_snapshot.py", "--target", str(target), "--skill-file", skill_file, "--out", str(bundle))
    run("static_checks.py", "--bundle", str(bundle), "--facts-out", str(facts))
    feats = Path(td) / "features.json"
    feats.write_text('{"features": {}}', encoding="utf-8")
    bhv = Path(td) / "behavior.json"
    bhv.write_text(json.dumps(behavior, ensure_ascii=False), encoding="utf-8")
    return bundle, facts, feats, bhv


def test_score_card_golden():
    with tempfile.TemporaryDirectory() as td:
        bundle, facts, feats, bhv = _score_card_inputs(
            Path(td), ROOT / "tests/golden/pure-skill", "SKILL.md.fixture",
            {"test_suite_pass": False, "calibration_pass": False, "migration_pass": False},
        )
        proc = run("score_card.py", "--bundle", str(bundle), "--facts", str(facts), "--features", str(feats), "--behavior", str(bhv), "--out", str(Path(td) / "score.json"))
        out = parse_stdout(proc)
        ok = (
            out["health_score"] == 100
            and out["maturity_level"]["level"] == "L2"
            and out["certification_level"]["level"] == "C1"
            and out["health_score_status"] == "PARTIAL"
            and out["p1_blocker_count"] == 2
            and out["blocker_count"] == 3
            and out["semantic_agreement"] is None
            and out["metrics"]["usage_coverage"] == 0.0
            and out["metrics"]["reproducibility_coverage"] == 0.0
        )
        return ok, f"health={out['health_score']}/{out['health_score_status']} maturity={out['maturity_level']} cert={out['certification_level']} blockers={out['blocker_count']}/p1={out['p1_blocker_count']}"


def test_score_card_determinism():
    with tempfile.TemporaryDirectory() as td:
        bundle, facts, feats, bhv = _score_card_inputs(
            Path(td), ROOT / "tests/golden/pure-skill", "SKILL.md.fixture",
            {"test_suite_pass": False, "calibration_pass": False, "migration_pass": False},
        )
        o1, o2 = Path(td) / "s1.json", Path(td) / "s2.json"
        run("score_card.py", "--bundle", str(bundle), "--facts", str(facts), "--features", str(feats), "--behavior", str(bhv), "--out", str(o1))
        run("score_card.py", "--bundle", str(bundle), "--facts", str(facts), "--features", str(feats), "--behavior", str(bhv), "--out", str(o2))
        same = o1.read_bytes() == o2.read_bytes()
        return same, f"score_bytes={len(o1.read_bytes())}"


def test_score_card_self_l4():
    with tempfile.TemporaryDirectory() as td:
        bundle, facts, feats, bhv = _score_card_inputs(
            Path(td), ROOT, "SKILL.md",
            {"test_suite_pass": True, "calibration_pass": True, "migration_pass": False},
        )
        proc = run("score_card.py", "--bundle", str(bundle), "--facts", str(facts), "--features", str(feats), "--behavior", str(bhv), "--out", str(Path(td) / "score.json"))
        out = parse_stdout(proc)
        ok = (
            out["maturity_level"]["level"] == "L4"
            and out["certification_level"]["level"] == "C1"
            and out["health_score_status"] == "PARTIAL"
            and out["self_audit"] is True
            and out["blocker_count"] == 3
            and out["p1_blocker_count"] == 2
        )
        return ok, f"maturity={out['maturity_level']} cert={out['certification_level']} health={out['health_score_status']} blockers={out['blocker_count']}/p1={out['p1_blocker_count']}"


def test_regressions(passed: set):
    cases = json.loads((ROOT / "tests/regressions/cases.json").read_text(encoding="utf-8"))
    missing = [c["id"] for c in cases if c["expect"] not in passed]
    return not missing, f"mapped {len(cases) - len(missing)}/{len(cases)} regression cases"


def main() -> int:
    tests = [
        ("protocol_hash_determinism", test_protocol_hash_determinism),
        ("snapshot_determinism", test_snapshot_determinism),
        ("static_golden", test_static_golden),
        ("static_boundary", test_static_boundary),
        ("decision_unit", lambda: test_decision_cases("unit", "tests/unit/decision-cases.json")),
        ("calibration", lambda: test_decision_cases("calibration", "tests/calibration/cases.json")),
        ("evidence_verify_valid", test_evidence_verify_valid),
        ("evidence_verify_invalid", test_evidence_verify_invalid),
        ("repro_gate_stable", lambda: test_repro_gate("STABLE", diff=False, independent=True)),
        ("repro_gate_unstable", lambda: test_repro_gate("UNSTABLE", diff=True, independent=True)),
        ("repro_gate_unverified", lambda: test_repro_gate("UNVERIFIED", diff=False, independent=False)),
        ("decision_withheld", test_decision_withheld),
        ("audit_status_gate", test_audit_status_gate),
        ("cache_content_addressed", test_cache_content_addressed),
        ("render_determinism", test_render_determinism),
        ("score_card_golden", test_score_card_golden),
        ("score_card_determinism", test_score_card_determinism),
        ("score_card_self_l4", test_score_card_self_l4),
    ]

    passed = set()
    failed = []
    for name, fn in tests:
        try:
            ok, msg = fn()
        except Exception as exc:
            ok, msg = False, f"exception: {exc}"
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {msg}")
        if ok:
            passed.add(name)
        else:
            failed.append(name)

    ok, msg = test_regressions(passed)
    print(f"{'PASS' if ok else 'FAIL'}  regressions: {msg}")
    if not ok:
        failed.append("regressions")

    print("RESULT", "ALL_PASS" if not failed else f"FAILED={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
