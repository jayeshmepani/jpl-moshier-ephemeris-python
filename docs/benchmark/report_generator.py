"""Generate a static benchmark dashboard from JSON artifacts."""

# ruff: noqa: E501

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_results() -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for path in sorted(ROOT.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("system"), dict):
            raise SystemExit(f"Invalid benchmark JSON payload: {path}")
        data["_file"] = path.name
        payloads.append(data)
    if not payloads:
        raise SystemExit("No benchmark JSON files found in docs/benchmark.")
    return payloads


def main() -> None:
    payloads = load_results()
    payload_json = json.dumps(payloads, separators=(",", ":"))
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Swiss Ephemeris Python FFI Benchmark</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{ color-scheme: light; --bg:#f8fafc; --card:#fff; --text:#0f172a; --muted:#475569; --line:#cbd5e1; --accent:#0369a1; --ffi:#2563eb; --pysweph:#dc2626; --pyswisseph:#9333ea; --win:#15803d; --loss:#c2410c; }}
    [data-theme="dark"] {{ color-scheme: dark; --bg:#0f172a; --card:#111827; --text:#f8fafc; --muted:#cbd5e1; --line:#334155; --accent:#38bdf8; --ffi:#60a5fa; --pysweph:#f87171; --pyswisseph:#c084fc; --win:#22c55e; --loss:#f97316; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family:Inter, ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--text); }}
    main {{ max-width:1440px; margin:0 auto; padding:32px 18px; }}
    header {{ display:flex; justify-content:space-between; gap:18px; align-items:flex-start; margin-bottom:24px; }}
    h1 {{ margin:0 0 8px; font-size:clamp(28px,5vw,48px); }}
    h2 {{ margin:0 0 12px; font-size:20px; }}
    p {{ color:var(--muted); max-width:980px; line-height:1.6; }}
    button {{ border:1px solid var(--line); background:var(--card); color:var(--text); border-radius:8px; padding:10px 14px; cursor:pointer; font-weight:700; }}
    .tabs {{ display:flex; flex-wrap:wrap; gap:8px; margin:22px 0; }}
    .tabs button.active {{ outline:2px solid var(--accent); color:var(--accent); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin:18px 0; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:18px; margin:18px 0; overflow-x:auto; }}
    .metric .label {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.05em; font-weight:800; }}
    .metric .value {{ font-size:28px; line-height:1.15; font-weight:900; margin-top:8px; color:var(--accent); overflow-wrap:anywhere; }}
    .meta {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px; color:var(--muted); }}
    .meta span {{ border:1px solid var(--line); border-radius:999px; padding:4px 10px; }}
    table {{ width:100%; border-collapse:collapse; min-width:900px; }}
    th, td {{ border-bottom:1px solid var(--line); padding:10px; text-align:left; vertical-align:top; }}
    th {{ color:var(--accent); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
    code {{ font-family:"JetBrains Mono", Consolas, monospace; }}
    input {{ width:100%; padding:12px 14px; border-radius:8px; border:1px solid var(--line); background:var(--card); color:var(--text); margin:12px 0; }}
    .chart-wrap {{ height:460px; }}
    .win {{ color:var(--win); font-weight:800; }}
    .loss {{ color:var(--loss); font-weight:800; }}
    .pill {{ display:inline-block; border:1px solid var(--line); border-radius:999px; padding:3px 9px; color:var(--muted); }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Swiss Ephemeris Python FFI Benchmark</h1>
        <p>Data-driven benchmark dashboard generated from GitHub Actions artifacts. Every metric and system value is read from JSON output produced by the benchmark jobs.</p>
      </div>
      <button type="button" id="themeToggle">Theme</button>
    </header>
    <section class="tabs" id="tabs"></section>
    <section class="grid" id="cards"></section>
    <section class="card">
      <h2 id="chartTitle">Latency Chart</h2>
      <div class="chart-wrap"><canvas id="latencyChart"></canvas></div>
    </section>
    <section class="card">
      <h2>Comparison Table</h2>
      <input id="search" type="search" aria-label="Search benchmark operations" placeholder="Search operation">
      <div id="comparison"></div>
    </section>
    <section class="card">
      <h2>System Specifications</h2>
      <div id="specs"></div>
    </section>
  </main>
  <script type="application/json" id="benchmark-data">{payload_json}</script>
  <script>
    const payloads = JSON.parse(document.getElementById("benchmark-data").textContent);
    const root = document.documentElement;
    const savedTheme = localStorage.getItem("theme");
    const preferredDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = savedTheme || (preferredDark ? "dark" : "light");
    document.getElementById("themeToggle").addEventListener("click", () => {{
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      localStorage.setItem("theme", next);
    }});

    const fmtNs = (value) => {{
      const n = Number(value);
      if (n >= 1_000_000) return `${{(n / 1_000_000).toFixed(3)}} ms`;
      if (n >= 1_000) return `${{(n / 1_000).toFixed(3)}} us`;
      return `${{n.toFixed(1)}} ns`;
    }};
    const fmtBytes = (value) => {{
      let n = Number(value);
      for (const unit of ["B", "KiB", "MiB", "GiB", "TiB"]) {{
        if (n < 1024 || unit === "TiB") return `${{n.toFixed(1)}} ${{unit}}`;
        n /= 1024;
      }}
    }};
    const esc = (s) => String(s).replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));
    const systems = [...new Set(payloads.map(p => `${{p.system.system}} ${{p.system.machine}}`))].sort();
    let activeSystem = systems[0];
    let chart;

    function bySystem(systemKey) {{
      return payloads.filter(p => `${{p.system.system}} ${{p.system.machine}}` === systemKey);
    }}
    function byDist(items, dist) {{
      return items.find(p => p.system.distribution === dist);
    }}
    function resultMap(payload) {{
      return Object.fromEntries(payload.results.map(r => [r.name, r]));
    }}
    function median(values) {{
      const sorted = values.slice().sort((a,b) => a-b);
      return sorted[Math.floor(sorted.length / 2)];
    }}
    function ratio(a, b) {{
      return a && b ? a.median_ns / b.median_ns : null;
    }}
    function ratioHtml(value) {{
      if (value === null) return "";
      const cls = value <= 1 ? "win" : "loss";
      return `<span class="${{cls}}">${{value.toFixed(2)}}x</span>`;
    }}

    function renderTabs() {{
      document.getElementById("tabs").innerHTML = systems.map(s =>
        `<button type="button" class="${{s === activeSystem ? "active" : ""}}" data-system="${{esc(s)}}">${{esc(s)}}</button>`
      ).join("");
      document.querySelectorAll("#tabs button").forEach(btn => btn.addEventListener("click", () => {{
        activeSystem = btn.dataset.system;
        render();
      }}));
    }}

    function renderCards(items) {{
      const ffi = byDist(items, "swisseph-ffi");
      const pysweph = byDist(items, "pysweph");
      const pyswisseph = byDist(items, "pyswisseph");
      const ffiMap = resultMap(ffi);
      const pyswephMap = pysweph ? resultMap(pysweph) : {{}};
      const ratios = Object.keys(ffiMap).map(k => ratio(ffiMap[k], pyswephMap[k])).filter(v => v !== null);
      const medianRatio = ratios.length ? median(ratios) : 0;
      document.getElementById("cards").innerHTML = [
        ["Runner", activeSystem],
        ["CPU", ffi.system.processor],
        ["Threads", ffi.system.cpu_count],
        ["RAM", fmtBytes(ffi.system.ram_bytes)],
        ["Protocol", `${{ffi.results[0].warmup}} warmup + ${{ffi.results[0].iterations}} measured`],
        ["Configured", `${{ffi.system.configured_function_count}} functions`],
        ["Benchmarked", `${{ffi.system.benchmarked_function_count}} FFI ops`],
        ["Median FFI/pysweph", ratios.length ? `${{medianRatio.toFixed(2)}}x` : ""],
        ["pysweph", pysweph ? pysweph.system.distribution_version : ""],
        ["pyswisseph", pyswisseph ? pyswisseph.system.distribution_version : ""],
      ].map(([label, value]) => `<div class="card metric"><div class="label">${{esc(label)}}</div><div class="value">${{esc(value)}}</div></div>`).join("");
    }}

    function renderChart(items) {{
      const labels = byDist(items, "swisseph-ffi").results.map(r => r.name);
      const datasets = [
        ["swisseph-ffi", "swisseph-ffi", getComputedStyle(root).getPropertyValue("--ffi")],
        ["pysweph", "pysweph", getComputedStyle(root).getPropertyValue("--pysweph")],
        ["pyswisseph", "pyswisseph", getComputedStyle(root).getPropertyValue("--pyswisseph")],
      ].map(([label, dist, color]) => {{
        const payload = byDist(items, dist);
        const map = payload ? resultMap(payload) : {{}};
        return {{ label, data: labels.map(name => map[name] ? map[name].median_ns / 1000 : null), backgroundColor: color, borderColor: color }};
      }});
      if (chart) chart.destroy();
      chart = new Chart(document.getElementById("latencyChart"), {{
        type: "bar",
        data: {{ labels, datasets }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{ y: {{ title: {{ display: true, text: "Median latency (microseconds)" }} }} }},
          plugins: {{ legend: {{ position: "top" }} }}
        }}
      }});
    }}

    function renderComparison(items) {{
      const query = document.getElementById("search").value.toLowerCase();
      const ffi = byDist(items, "swisseph-ffi");
      const rows = ffi.results.filter(r => r.name.toLowerCase().includes(query)).map(r => {{
        const py = byDist(items, "pysweph");
        const pys = byDist(items, "pyswisseph");
        const pyR = py ? resultMap(py)[r.name] : null;
        const pysR = pys ? resultMap(pys)[r.name] : null;
        return `<tr>
          <td><code>${{esc(r.name)}}</code></td>
          <td>${{fmtNs(r.median_ns)}}</td>
          <td>${{pyR ? fmtNs(pyR.median_ns) : ""}}</td>
          <td>${{ratioHtml(ratio(r, pyR))}}</td>
          <td>${{pysR ? fmtNs(pysR.median_ns) : ""}}</td>
          <td>${{ratioHtml(ratio(r, pysR))}}</td>
        </tr>`;
      }}).join("");
      document.getElementById("comparison").innerHTML = `<table>
        <thead><tr><th>Operation</th><th>swisseph-ffi</th><th>pysweph</th><th>FFI / pysweph</th><th>pyswisseph</th><th>FFI / pyswisseph</th></tr></thead>
        <tbody>${{rows}}</tbody>
      </table>`;
    }}

    function renderSpecs(items) {{
      const rows = items.flatMap(p => Object.entries(p.system).map(([k, v]) =>
        `<tr><td><span class="pill">${{esc(p.system.distribution)}}</span></td><th>${{esc(k)}}</th><td>${{esc(typeof v === "number" && k === "ram_bytes" ? fmtBytes(v) : v)}}</td></tr>`
      )).join("");
      document.getElementById("specs").innerHTML = `<table><tbody>${{rows}}</tbody></table>`;
    }}

    function render() {{
      renderTabs();
      const items = bySystem(activeSystem);
      renderCards(items);
      renderChart(items);
      renderComparison(items);
      renderSpecs(items);
    }}
    document.getElementById("search").addEventListener("input", () => renderComparison(bySystem(activeSystem)));
    render();
  </script>
</body>
</html>
"""
    (ROOT / "benchmark.html").write_text(page, encoding="utf-8")
    print("Generated docs/benchmark/benchmark.html")


if __name__ == "__main__":
    main()
