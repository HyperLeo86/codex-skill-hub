#!/usr/bin/env python3
"""Generate a 检索世界 HTML report page and rebuild the history index."""
import argparse
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

VALID_VERDICTS = ("直接用", "改改用", "只借鉴", "淘汰", "待验证")
VERDICT_CLASS = {
    "直接用": "use",
    "改改用": "mod",
    "只借鉴": "idea",
    "淘汰": "dead",
    "待验证": "verify",
}
VERDICT_ICON = {"直接用": "🟢", "改改用": "🟡", "只借鉴": "🔵", "淘汰": "🔴", "待验证": "🟣"}
MATCH_VALUES = ("✅", "⚠️", "❌")
MATCH_CLASS = {"✅": "ok", "⚠️": "warn", "❌": "no"}
MATCH_LABEL = {"input": "输入匹配", "output": "输出匹配", "scenario": "场景匹配", "constraint": "约束匹配"}


def esc(value):
    return html.escape(str(value), quote=True)


def slugify(text):
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", str(text)).strip("-")
    return slug or "untitled"


def default_history_dir():
    docs = Path.home() / "Documents"
    if docs.exists():
        return docs / "solution-scout-history"
    return Path.home() / ".solution-scout-history"


def validate(report):
    errors = []
    if not report.get("query"):
        errors.append("缺少 query")
    candidates = report.get("candidates") or []
    if not candidates:
        errors.append("candidates 为空（至少 1 个候选）")
    recommended = 0
    for i, c in enumerate(candidates):
        if not c.get("name"):
            errors.append(f"candidates[{i}] 缺少 name")
        if not c.get("url"):
            errors.append(f"candidates[{i}] 缺少 url")
        verdict = c.get("verdict", "")
        if verdict not in VALID_VERDICTS:
            errors.append(f"candidates[{i}] verdict 非法：{verdict!r}")
        if c.get("recommended"):
            recommended += 1
        for key, value in (c.get("match") or {}).items():
            if value not in MATCH_VALUES:
                errors.append(f"candidates[{i}] match.{key} 非法：{value!r}")
    if recommended > 1:
        errors.append("recommended 标记超过一个")
    if report.get("mode") and report.get("mode") not in ("normal", "loop"):
        errors.append(f"mode 非法：{report['mode']!r}")
    if errors:
        raise SystemExit("report.json 校验失败：\n- " + "\n- ".join(errors))


def maturity_segments(value):
    try:
        level = int(str(value).upper().replace("L", ""))
    except (TypeError, ValueError):
        level = 0
    level = max(0, min(5, level))
    return "".join(
        '<div class="seg filled"></div>' if i < level else '<div class="seg"></div>'
        for i in range(5)
    )


def badge_html(verdict):
    return (
        f'<span class="badge {VERDICT_CLASS.get(verdict, "verify")}">'
        f'{VERDICT_ICON.get(verdict, "🟣")} {esc(verdict)}</span>'
    )


def match_html(match):
    match = match or {}
    items = []
    for key in ("input", "output", "scenario", "constraint"):
        value = match.get(key, "❌")
        items.append(
            f'<div class="match-item"><div class="m {MATCH_CLASS.get(value, "no")}">{value}</div>'
            f'<div class="t">{MATCH_LABEL[key]}</div></div>'
        )
    return "".join(items)


def links_html(candidate):
    out = [f'<a href="{esc(candidate["url"])}" target="_blank">官网</a>']
    for label, url in (candidate.get("links") or {}).items():
        out.append(f'<a href="{esc(url)}" target="_blank">{esc(label)}</a>')
    return "".join(out)


def rec_card_html(candidate):
    maturity = candidate.get("maturity", "L0")
    notes = []
    if candidate.get("known_issues"):
        notes.append(f"⚠️ 已知坑：{esc(candidate['known_issues'])}")
    if candidate.get("reason"):
        notes.append(f"结论理由：{esc(candidate['reason'])}")
    note_html = ""
    if notes:
        note_html = '<div class="note">' + '</div><div class="note">'.join(notes) + "</div>"
    return f"""<div class="card">
  <div class="rec-head">
    <h3>{esc(candidate['name'])}</h3>
    {badge_html(candidate.get('verdict', '待验证'))}
    <span class="badge">成熟度 {esc(maturity)}</span>
  </div>
  <p class="one-liner">{esc(candidate.get('one_liner', ''))}</p>
  <div class="links">{links_html(candidate)}</div>
  <div class="grid">
    <div class="kv"><div class="label">类型</div><div class="value">{esc(candidate.get('type', '—'))}</div></div>
    <div class="kv"><div class="label">许可证 / 成本</div><div class="value">{esc(candidate.get('license_cost', '—'))}</div></div>
    <div class="kv"><div class="label">最近更新</div><div class="value">{esc(candidate.get('last_update', '—'))}</div></div>
    <div class="kv"><div class="label">上手难度</div><div class="value">{esc(candidate.get('effort', '—'))}</div></div>
  </div>
  <div class="maturity">
    <div class="lbl">成熟度（离直接用有多远：L0–L5）</div>
    <div class="bar">{maturity_segments(maturity)}</div>
  </div>
  <div class="match">{match_html(candidate.get('match'))}</div>
  {note_html}
</div>"""


def table_html(candidates):
    rows = []
    for c in candidates:
        verdict = c.get("verdict", "待验证")
        rows.append(
            f"<tr><td>{esc(c['name'])}</td><td>{esc(c.get('type', '—'))}</td>"
            f"<td>{esc(c.get('maturity', '—'))}</td><td>{esc(c.get('license_cost', '—'))}</td>"
            f"<td>{esc(c.get('one_liner', ''))}</td>"
            f'<td><span class="status-dot {VERDICT_CLASS.get(verdict, "verify")}"></span>{esc(verdict)}</td></tr>'
        )
    return "".join(rows)


def list_html(items):
    return "".join(f"<li>{esc(item)}</li>" for item in (items or []))


CSS = """
  :root {
    --bg:#f5f6f8; --card:#fff; --ink:#1c2333; --muted:#6b7280; --line:#e5e7eb;
    --green:#16a34a; --amber:#d97706; --blue:#2563eb; --red:#dc2626; --violet:#7c3aed;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
    background:var(--bg); color:var(--ink); line-height:1.6; padding:32px 16px; }
  .wrap { max-width:960px; margin:0 auto; }
  .header { background:linear-gradient(135deg,#1e3a8a,#3b82f6); color:#fff;
    border-radius:14px; padding:28px 32px; box-shadow:0 8px 24px rgba(30,58,138,.18); }
  .header .meta { font-size:13px; opacity:.85; margin-bottom:8px; }
  .header h1 { font-size:26px; font-weight:700; }
  .header .query { font-size:14px; opacity:.9; margin-top:10px; }
  .chips { margin-top:16px; display:flex; flex-wrap:wrap; gap:8px; }
  .chip { font-size:12px; padding:4px 12px; border-radius:999px;
    background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.35); }
  .section { margin-top:24px; }
  .section h2 { font-size:17px; margin-bottom:12px; display:flex; align-items:center; gap:8px; }
  .section h2::before { content:""; width:4px; height:18px; background:#3b82f6; border-radius:2px; }
  .card { background:var(--card); border-radius:14px; padding:24px 28px;
    border:1px solid var(--line); box-shadow:0 2px 8px rgba(17,24,39,.05); }
  .badge { display:inline-block; font-size:12px; font-weight:600; padding:3px 12px;
    border-radius:999px; margin-left:6px; vertical-align:middle; }
  .badge.use { background:#f0fdf4; color:var(--green); border:1px solid #bbf7d0; }
  .badge.mod { background:#fffbeb; color:var(--amber); border:1px solid #fde68a; }
  .badge.idea { background:#eff6ff; color:var(--blue); border:1px solid #bfdbfe; }
  .badge.dead { background:#fef2f2; color:var(--red); border:1px solid #fecaca; }
  .badge.verify { background:#f5f3ff; color:var(--violet); border:1px solid #ddd6fe; }
  .rec-head { display:flex; flex-wrap:wrap; align-items:center; gap:12px; margin-bottom:6px; }
  .rec-head h3 { font-size:22px; }
  .one-liner { color:var(--muted); font-size:15px; margin-bottom:18px; }
  .links { margin-bottom:20px; }
  .links a { display:inline-block; margin:0 8px 8px 0; padding:7px 16px; border-radius:8px;
    text-decoration:none; font-size:13px; font-weight:600; background:#eff6ff; color:var(--blue);
    border:1px solid #bfdbfe; transition:.15s; }
  .links a:hover { background:#dbeafe; }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  @media (max-width:720px) { .grid { grid-template-columns:1fr; } }
  .kv { background:#fafafa; border:1px solid var(--line); border-radius:10px; padding:14px 16px; }
  .kv .label { font-size:12px; color:var(--muted); margin-bottom:4px; }
  .kv .value { font-size:14px; font-weight:600; }
  .maturity { margin-top:20px; }
  .maturity .lbl { font-size:12px; color:var(--muted); margin-bottom:6px; }
  .bar { display:flex; gap:6px; }
  .seg { flex:1; height:10px; border-radius:5px; background:#e5e7eb; }
  .seg.filled { background:linear-gradient(90deg,#22c55e,#16a34a); }
  .match { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-top:18px; }
  .match-item { text-align:center; border:1px solid var(--line); border-radius:10px; padding:12px 8px; }
  .match-item .m { font-size:20px; }
  .match-item .t { font-size:12px; color:var(--muted); margin-top:4px; }
  .ok { color:var(--green); } .warn { color:var(--amber); } .no { color:var(--red); }
  .note { background:#fffbeb; border:1px solid #fde68a; border-radius:10px;
    padding:14px 16px; font-size:14px; margin-top:16px; }
  .note-line { font-size:13px; color:var(--muted); margin-top:10px; }
  table { width:100%; border-collapse:collapse; font-size:13.5px; }
  th, td { padding:10px 12px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }
  th { background:#f9fafb; font-size:12px; color:var(--muted); }
  tr:last-child td { border-bottom:none; }
  .status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }
  .dot-green, .status-dot.use { background:var(--green); }
  .dot-amber, .status-dot.mod { background:var(--amber); }
  .dot-blue, .status-dot.idea { background:var(--blue); }
  .dot-red, .status-dot.dead { background:var(--red); }
  .status-dot.verify { background:var(--violet); }
  .next { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:16px 18px; }
  .next h4 { font-size:14px; color:var(--green); margin-bottom:6px; }
  .next ol { margin-left:18px; font-size:14px; }
  .src { font-size:13px; color:var(--muted); }
  .src li { margin:4px 0; }
  .src a { color:var(--blue); text-decoration:none; }
  .src a:hover { text-decoration:underline; }
  .footer { margin-top:28px; text-align:center; font-size:12px; color:#9ca3af; }
  .footer a { color:var(--blue); text-decoration:none; }
"""

REPORT_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{QUERY}}</title>
<style>""" + CSS + """</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="meta">{{META}}</div>
    <h1>{{QUERY}}</h1>
    <div class="query">需求：{{CONSTRAINTS}}</div>
    <div class="chips">{{CHIPS}}</div>
  </div>
  <div class="section"><h2>推荐方案</h2>{{REC_CARD}}</div>
  <div class="section"><h2>候选对比</h2><div class="card"><table>
    <thead><tr><th>方案</th><th>类型</th><th>成熟度</th><th>成本</th><th>一句话定位</th><th>结论</th></tr></thead>
    <tbody>{{TABLE}}</tbody>
  </table></div></div>
  <div class="section"><h2>下一步（最小试跑）</h2>
    <div class="next"><h4>验证计划</h4><ol>{{NEXT}}</ol></div></div>
  <div class="section"><h2>来源与搜索记录</h2><div class="card src">
    <ul>{{SOURCES}}</ul>{{UNSEARCHED}}{{LOOP_NOTES}}{{HISTORY_REUSED}}{{RETRIEVAL_LOG}}{{ASSUMPTIONS}}
  </div></div>
  <div class="footer">由 检索世界 生成 · <a href="{{INDEX_LINK}}">返回检索历史</a></div>
</div>
</body>
</html>"""


def render_report(report, history_dir, run_dir):
    candidates = report.get("candidates") or []
    rec = next((c for c in candidates if c.get("recommended")), None)
    if rec is None:
        rec = next((c for c in candidates if c.get("verdict") == "直接用"), None)
    if rec is None:
        rec = next((c for c in candidates if c.get("verdict") == "改改用"), None)
    if rec is None and candidates:
        rec = candidates[0]

    chips = []
    if report.get("type"):
        chips.append(f'<span class="chip">{esc(report["type"])}</span>')
    for channel in report.get("channels") or []:
        chips.append(f'<span class="chip">{esc(channel)}</span>')
    chips.append(f'<span class="chip">候选 {len(candidates)} 个</span>')
    if report.get("history_reused"):
        chips.append(f'<span class="chip">历史回灌 {len(report["history_reused"])} 条</span>')

    mode = report.get("mode", "normal")
    mode_label = "深度扫描" if mode == "loop" else "普通模式"
    rounds_txt = f" · {report.get('rounds', '')} 轮" if mode == "loop" and report.get("rounds") else ""
    meta = f"{report.get('date') or date.today().isoformat()} · {mode_label}{rounds_txt} · 检索时长 {report.get('duration_minutes', '—')} 分钟"
    unsearched = ""
    if report.get("unsearched"):
        unsearched = f'<p class="note-line">未搜索渠道：{esc("、".join(report["unsearched"]))}</p>'
    loop_notes = ""
    if report.get("loop_notes"):
        loop_notes = '<p class="note-line">循环记录：' + esc("；".join(report["loop_notes"])) + "</p>"
    history_reused = ""
    if report.get("history_reused"):
        history_reused = '<p class="note-line">历史回灌：' + esc("；".join(report["history_reused"])) + "</p>"
    retrieval_log = ""
    if report.get("retrieval_log"):
        log_lines = []
        for item in report["retrieval_log"]:
            variant = item.get("variant", "")
            engines = ",".join(item.get("engines") or [])
            hits = item.get("hits", "—")
            useful = item.get("useful", "—")
            log_lines.append(f"{variant}（{engines}，命中 {hits}，有用 {useful}）")
        retrieval_log = '<p class="note-line">检索日志：' + esc("；".join(log_lines)) + "</p>"
    assumptions = ""
    if report.get("assumptions"):
        assumptions = f'<p class="note-line">假设：{esc("；".join(report["assumptions"]))}</p>'
    index_link = "../index.html" if run_dir.resolve() != history_dir.resolve() else "index.html"

    return (
        REPORT_SHELL.replace("{{META}}", meta)
        .replace("{{QUERY}}", esc(report.get("query", "未命名检索")))
        .replace("{{CONSTRAINTS}}", esc(report.get("constraints", "")))
        .replace("{{CHIPS}}", "".join(chips))
        .replace("{{REC_CARD}}", rec_card_html(rec) if rec else '<div class="card">未找到合适候选</div>')
        .replace("{{TABLE}}", table_html(candidates))
        .replace("{{NEXT}}", list_html(report.get("next_steps") or []))
        .replace("{{SOURCES}}", list_html(report.get("sources") or []))
        .replace("{{UNSEARCHED}}", unsearched)
        .replace("{{LOOP_NOTES}}", loop_notes)
        .replace("{{HISTORY_REUSED}}", history_reused)
        .replace("{{RETRIEVAL_LOG}}", retrieval_log)
        .replace("{{ASSUMPTIONS}}", assumptions)
        .replace("{{INDEX_LINK}}", esc(index_link))
    )


INDEX_CSS = """
  :root {
    --bg:#f5f6f8; --card:#fff; --ink:#1c2333; --muted:#6b7280; --line:#e5e7eb;
    --green:#16a34a; --amber:#d97706; --blue:#2563eb; --red:#dc2626; --violet:#7c3aed;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
    background:var(--bg); color:var(--ink); line-height:1.6; padding:32px 16px; }
  .wrap { max-width:1080px; margin:0 auto; }
  .header { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center;
    gap:16px; margin-bottom:24px; }
  .header h1 { font-size:26px; }
  .header .sub { color:var(--muted); font-size:14px; }
  .stats { display:flex; gap:24px; margin-bottom:20px; }
  .stat b { font-size:22px; display:block; }
  .stat span { font-size:12px; color:var(--muted); }
  .filters { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:20px; }
  .f-btn { border:1px solid var(--line); background:var(--card); color:var(--muted);
    padding:6px 14px; border-radius:999px; font-size:13px; cursor:pointer; transition:.15s; }
  .f-btn.active { background:var(--ink); color:#fff; border-color:var(--ink); }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; }
  .rc { background:var(--card); border:1px solid var(--line); border-radius:14px;
    padding:18px 20px; text-decoration:none; color:inherit;
    box-shadow:0 2px 8px rgba(17,24,39,.05); transition:.15s; }
  .rc:hover { transform:translateY(-2px); box-shadow:0 8px 20px rgba(17,24,39,.1); }
  .rc .date { font-size:12px; color:var(--muted); margin-bottom:6px; }
  .rc h3 { font-size:17px; margin-bottom:6px; }
  .rc .desc { font-size:13px; color:var(--muted); margin-bottom:12px; min-height:40px; }
  .rc .tags { display:flex; flex-wrap:wrap; gap:6px; }
  .tag { font-size:11px; padding:3px 10px; border-radius:999px; font-weight:600; }
  .tag.use { background:#f0fdf4; color:var(--green); border:1px solid #bbf7d0; }
  .tag.mod { background:#fffbeb; color:var(--amber); border:1px solid #fde68a; }
  .tag.idea { background:#eff6ff; color:var(--blue); border:1px solid #bfdbfe; }
  .tag.dead { background:#fef2f2; color:var(--red); border:1px solid #fecaca; }
  .tag.verify { background:#f5f3ff; color:var(--violet); border:1px solid #ddd6fe; }
  .tag.gray { background:#f9fafb; color:var(--muted); border:1px solid var(--line); }
  .empty { grid-column:1/-1; background:var(--card); border:2px dashed var(--line);
    border-radius:14px; padding:48px 24px; text-align:center; color:var(--muted); }
  .empty h4 { font-size:16px; margin-bottom:8px; color:var(--ink); }
  .footer { margin-top:28px; text-align:center; font-size:12px; color:#9ca3af; }
"""

INDEX_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>我的检索历史 · 检索世界</title>
<style>""" + INDEX_CSS + """</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div>
      <h1>我的检索历史</h1>
      <div class="sub">检索世界 · 每次检索自动归档到这里</div>
    </div>
  </div>
  <div class="stats">
    <div class="stat"><b>{{COUNT}}</b><span>总检索次数</span></div>
    <div class="stat"><b>{{USED}}</b><span>可直接用</span></div>
  </div>
  <div class="filters">
    <button class="f-btn active" data-filter="all">全部</button>
    <button class="f-btn" data-filter="use">🟢 直接用</button>
    <button class="f-btn" data-filter="mod">🟡 改改用</button>
    <button class="f-btn" data-filter="idea">🔵 只借鉴</button>
    <button class="f-btn" data-filter="dead">🔴 淘汰</button>
    <button class="f-btn" data-filter="verify">🟣 待验证</button>
  </div>
  <div class="grid">{{CARDS}}</div>
  <div class="footer">历史库价值：下次想查同类问题，先看这里，可能 5 分钟就得到答案。</div>
</div>
<script>
  document.querySelectorAll(".f-btn").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll(".f-btn").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      var f = b.dataset.filter;
      document.querySelectorAll(".rc").forEach(function (c) {
        c.style.display = (f === "all" || c.dataset.v === f) ? "" : "none";
      });
    });
  });
</script>
</body>
</html>"""


def render_index(entries, history_dir):
    cards = []
    used = 0
    for entry in sorted(entries, key=lambda e: e["date"], reverse=True):
        report = entry["report"]
        candidates = report.get("candidates") or []
        rec = next((c for c in candidates if c.get("recommended")), None)
        if rec is None:
            rec = candidates[0] if candidates else {}
        verdict = rec.get("verdict", "待验证") if rec else "待验证"
        if verdict == "直接用":
            used += 1
        tags = [
            f'<span class="tag {VERDICT_CLASS.get(verdict, "verify")}">'
            f'{VERDICT_ICON.get(verdict, "🟣")} {esc(verdict)}</span>'
        ]
        if report.get("type"):
            tags.append(f'<span class="tag gray">{esc(report["type"])}</span>')
        desc = rec.get("one_liner", "") if rec else ""
        cards.append(
            f'<a class="rc" data-v="{VERDICT_CLASS.get(verdict, "verify")}" href="{entry["rel"]}">'
            f'<div class="date">{entry["date"]} · {entry["duration"]} 分钟</div>'
            f'<h3>{esc(report.get("query", "未命名"))}</h3>'
            f'<div class="desc">{esc(desc)}</div>'
            f'<div class="tags">{"".join(tags)}</div></a>'
        )
    if not cards:
        cards.append(
            '<div class="empty"><h4>还没有检索记录</h4>'
            "<p>运行 检索世界 后，结果会自动归档到这里。</p></div>"
        )
    return (
        INDEX_SHELL.replace("{{COUNT}}", str(len(entries)))
        .replace("{{USED}}", str(used))
        .replace("{{CARDS}}", "".join(cards))
    )


def main():
    parser = argparse.ArgumentParser(description="Generate 检索世界 HTML report and history index.")
    parser.add_argument("report", type=Path, help="Path to report.json")
    parser.add_argument(
        "--history-dir",
        type=Path,
        default=None,
        help=f"History root (default: {default_history_dir()})",
    )
    args = parser.parse_args()

    report_path = args.report
    if not report_path.exists():
        raise SystemExit(f"找不到 report.json：{report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    validate(report)

    history_dir = (args.history_dir or default_history_dir()).resolve()
    inside_history = history_dir == report_path.resolve().parent or history_dir in report_path.resolve().parents
    if inside_history:
        run_dir = report_path.resolve().parent
    else:
        slug = f"{report.get('date') or date.today().isoformat()}-{slugify(report.get('query', 'untitled'))[:40]}"
        run_dir = history_dir / slug
        run_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(report_path, run_dir / "report.json")
        report_path = run_dir / "report.json"

    history_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "report.html").write_text(
        render_report(report, history_dir, run_dir), encoding="utf-8"
    )

    entries = []
    for sub in sorted(history_dir.iterdir()):
        if sub.is_dir() and (sub / "report.json").exists():
            try:
                data = json.loads((sub / "report.json").read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            entries.append(
                {
                    "date": data.get("date", ""),
                    "duration": data.get("duration_minutes", "—"),
                    "report": data,
                    "rel": f"{sub.name}/report.html",
                }
            )
    (history_dir / "index.html").write_text(render_index(entries, history_dir), encoding="utf-8")

    print(f"结果页：{run_dir / 'report.html'}")
    print(f"历史索引：{history_dir / 'index.html'}")


if __name__ == "__main__":
    main()
