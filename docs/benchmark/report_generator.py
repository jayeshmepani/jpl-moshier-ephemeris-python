"""Generate the Python benchmark dashboard from benchmark JSON artifacts."""

# ruff: noqa: E501

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PREFERRED_COMPARISON = "pysweph"


def os_key(system: dict[str, Any]) -> str:
    os_name = str(system.get("os", ""))
    if "Linux" in os_name:
        return "Linux"
    if "Darwin" in os_name or "macOS" in os_name:
        return "macOS"
    if "Windows" in os_name:
        return "Windows"
    return os_name or str(system.get("system", "Unknown"))


def is_new_payload(data: dict[str, Any]) -> bool:
    return isinstance(data.get("system"), dict) and isinstance(data.get("results"), dict)


def load_payloads() -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for path in sorted(ROOT.glob("*.json")):
        if path.name.startswith("local-"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not is_new_payload(data):
            continue
        data["_file"] = path.name
        payloads.append(data)
    if not payloads:
        raise SystemExit("No valid benchmark JSON files found in docs/benchmark.")
    return payloads


def safe_ratio(ffi: float | int, ext: float | int) -> float:
    if ext == 0:
        return 1.0 if ffi == 0 else 999.9
    return float(ffi) / float(ext)


def ratio_map(ffi: dict[str, float | int], ext: dict[str, float | int]) -> dict[str, float]:
    keys = ("mean", "median", "p95", "stddev", "min", "max", "mem")
    return {key: safe_ratio(ffi[key], ext[key]) for key in keys}


def merge_payloads(payloads: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_system: dict[str, list[dict[str, Any]]] = {}
    for payload in payloads:
        by_system.setdefault(os_key(payload["system"]), []).append(payload)

    merged: dict[str, dict[str, Any]] = {}
    for key, items in by_system.items():
        ffi_payload = next(
            (item for item in items if item["system"].get("distribution") == "swisseph-ffi"),
            None,
        )
        if ffi_payload is None:
            continue

        comparison_payload = next(
            (item for item in items if item["system"].get("distribution") == PREFERRED_COMPARISON),
            None,
        ) or next(
            (item for item in items if item["system"].get("benchmark_library") == "swisseph"), None
        )

        comparison_results = comparison_payload["results"] if comparison_payload else {}
        results: dict[str, Any] = {}
        for name, record in ffi_payload["results"].items():
            ffi_stats = record.get("ffi")
            if not ffi_stats:
                results[name] = {
                    "ffi": None,
                    "ext": None,
                    "accuracy": None,
                    "ffi_error": record.get("error"),
                }
                continue
            ext_record = comparison_results.get(name, {})
            ext_stats = ext_record.get("ext") if isinstance(ext_record, dict) else None
            results[name] = {
                "ffi": ffi_stats,
                "ext": ext_stats,
                "accuracy": bool(ext_stats),
                "ratios": ratio_map(ffi_stats, ext_stats) if ext_stats else None,
                "comparison_package": comparison_payload["system"].get("distribution")
                if comparison_payload and ext_stats
                else None,
                "comparison_error": ext_record.get("error")
                if isinstance(ext_record, dict)
                else None,
            }

        system = dict(ffi_payload["system"])
        system["comparison_package"] = (
            comparison_payload["system"].get("distribution")
            if comparison_payload
            else "not-captured"
        )
        system["comparison_package_version"] = (
            comparison_payload["system"].get("distribution_version")
            if comparison_payload
            else "not-captured"
        )
        system["comparison_module"] = (
            comparison_payload["system"].get("module_file")
            if comparison_payload
            else "not-captured"
        )
        system["compared_function_count"] = sum(1 for item in results.values() if item.get("ext"))
        merged[key] = {"system": system, "results": results}

    if not merged:
        raise SystemExit("No swisseph-ffi benchmark payloads found to render.")
    return merged


def main() -> None:
    all_data = merge_payloads(load_payloads())
    data_json = json.dumps(all_data, separators=(",", ":"))
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Swiss Ephemeris Python Multi-OS Performance Audit</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #f1f5f9; --card: #ffffff; --primary: #2563eb; --success: #059669; --danger: #ef4444;
            --text: #0f172a; --text-muted: #64748b; --border: #e2e8f0; --ffi: #3b82f6; --ext: #ef4444; --chart-grid: #e2e8f0;
        }}
        [data-theme="dark"] {{
            --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --text-muted: #f1f5f9; --border: #334155;
            --chart-grid: rgba(255,255,255,0.15); --primary: #60a5fa;
        }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 1rem; transition: background 0.3s, color 0.3s; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{ display: flex; flex-direction: column; align-items: center; margin: 2rem 0 1rem 0; position: relative; }}
        .theme-toggle {{ position: absolute; right: 0; top: 0; background: var(--card); border: 1px solid var(--border); padding: 0.5rem 1rem; border-radius: 0.75rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; font-weight: 600; color: var(--text); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }}
        .system-tabs {{ display: flex; gap: 0.5rem; margin-bottom: 2rem; background: var(--border); padding: 0.3rem; border-radius: 1rem; width: fit-content; margin-left: auto; margin-right: auto; }}
        .tab-btn {{ padding: 0.75rem 1.5rem; border: none; background: transparent; color: var(--text-muted); font-weight: 700; cursor: pointer; border-radius: 0.75rem; transition: all 0.2s; font-size: 0.9rem; }}
        .tab-btn.active {{ background: var(--card); color: var(--primary); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }}
        .badge {{ display: inline-block; padding: 0.5rem 1rem; background: var(--primary); color: #fff; font-weight: 800; border-radius: 9999px; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 1rem; }}
        [data-theme="dark"] .badge {{ color: #000; background: var(--primary); }}
        h1 {{ font-size: clamp(1.5rem, 5vw, 2.5rem); font-weight: 800; margin: 0; letter-spacing: 0; color: var(--text); text-align: center; }}
        .subtitle {{ color: var(--text-muted); margin-bottom: 2rem; text-align: center; max-width: 960px; line-height: 1.55; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); }}
        .card h3 {{ margin: 0 0 1rem 0; font-size: 0.875rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; }}
        .card .value {{ font-size: 2.25rem; font-weight: 800; line-height: 1; margin-bottom: 0.5rem; color: var(--primary); }}
        .specs-list {{ list-style: none; padding: 0; margin: 0; }}
        .specs-list li {{ display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; gap: 10px; }}
        .specs-label {{ font-weight: 600; color: var(--text-muted); }}
        .specs-value {{ text-align: right; color: var(--text); font-weight: 500; overflow-wrap: anywhere; }}
        .chart-section {{ background: var(--card); border-radius: 1rem; padding: 1.5rem; border: 1px solid var(--border); margin-bottom: 2rem; }}
        .chart-container {{ position: relative; height: 550px; width: 100%; }}
        .search-box {{ width: 100%; padding: 1rem; background: var(--card); color: var(--text); border: 1px solid var(--border); border-radius: 0.75rem; font-size: 1rem; box-sizing: border-box; outline: none; margin-bottom: 1rem; }}
        .table-wrapper {{ overflow-x: auto; border-radius: 1rem; border: 1px solid var(--border); background: var(--card); }}
        table {{ width: 100%; border-collapse: collapse; min-width: 900px; }}
        th {{ background: rgba(0,0,0,0.02); text-align: left; padding: 1rem; font-weight: 800; color: var(--text); border-bottom: 2px solid var(--border); font-size: 0.75rem; text-transform: uppercase; position: sticky; top: 0; z-index: 10; }}
        td {{ padding: 1rem; border-bottom: 1px solid var(--border); font-size: 0.9rem; color: var(--text); }}
        code {{ font-family: 'JetBrains Mono', Consolas, monospace; }}
        .tag {{ padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.7rem; font-weight: 800; display: inline-block; }}
        .tag-match {{ background: #dcfce7; color: #166534; }}
        .tag-pro {{ background: #e0f2fe; color: #0369a1; }}
        .tag-na {{ background: #f1f5f9; color: #475569; }}
        [data-theme="dark"] .tag-match {{ background: #064e3b; color: #4ade80; }}
        [data-theme="dark"] .tag-pro {{ background: #0c4a6e; color: #7dd3fc; }}
        [data-theme="dark"] .tag-na {{ background: #334155; color: #e2e8f0; }}
        @media (max-width: 900px) {{ .theme-toggle {{ position: static; margin-bottom: 1rem; }} .card[style] {{ grid-column: auto !important; }} }}
    </style>
</head>
<body data-theme="light">
    <div class="container">
        <header>
            <button class="theme-toggle" id="themeToggle"><span id="themeLabel"></span></button>
            <div class="badge">Multi-OS Performance Audit</div>
            <h1>FFI vs. Python C-Extension Transparency</h1>
            <p class="subtitle">True Transparency: system specs, protocol counts, library versions, function counts, latency stats, and comparison availability are generated from benchmark JSON artifacts.</p>
            <div class="system-tabs" id="systemTabs"></div>
        </header>

        <div class="grid">
            <div class="card">
                <h3>Compute Power</h3>
                <ul class="specs-list">
                    <li><span class="specs-label">Processor</span><span class="specs-value" id="spec-cpu"></span></li>
                    <li><span class="specs-label">Cores/Threads</span><span class="specs-value" id="spec-cores"></span></li>
                    <li><span class="specs-label">Frequency</span><span class="specs-value" id="spec-freq"></span></li>
                    <li><span class="specs-label">Architecture</span><span class="specs-value" id="spec-arch"></span></li>
                    <li><span class="specs-label">Instruction Sets</span><span class="specs-value" id="spec-instr"></span></li>
                </ul>
            </div>
            <div class="card" style="grid-column: span 2;">
                <h3>Software Stack</h3>
                <ul class="specs-list">
                    <li><span class="specs-label">Operating System</span><span class="specs-value" id="spec-os"></span></li>
                    <li><span class="specs-label">Runner RAM</span><span class="specs-value" id="spec-ram"></span></li>
                    <li><span class="specs-label">Python Runtime</span><span class="specs-value" id="spec-python"></span></li>
                    <li><span class="specs-label">Python Compiler</span><span class="specs-value" id="spec-compiler"></span></li>
                    <li><span class="specs-label">Library</span><span class="specs-value" id="spec-lib"></span></li>
                    <li><span class="specs-label">Comparison Package</span><span class="specs-value" id="spec-comparison"></span></li>
                    <li><span class="specs-label">Generated At</span><span class="specs-value" id="spec-date"></span></li>
                </ul>
            </div>
        </div>

        <div class="grid" style="grid-template-columns: 1fr 2fr;">
            <div class="card">
                <h3>Bridge Overhead</h3>
                <div class="value" id="overall-median"></div>
                <p style="margin:0; font-size:0.9rem; color:var(--text-muted)">Median latency delta vs compared Python C-extension package</p>
                <div id="status-text" style="font-weight: 700; margin-top: 1rem;"></div>
            </div>
            <div class="card">
                <h3>Accuracy & Parity Glossary</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div class="glossary-item">
                        <span class="tag tag-match">WRAPPER-COMPARED</span>
                        <p style="font-size: 0.75rem; color: var(--text-muted)">The Python extension exposes a benchmarkable wrapper method for this C function name.</p>
                    </div>
                    <div class="glossary-item">
                        <span class="tag tag-pro">FFI-ONLY</span>
                        <p style="font-size: 0.75rem; color: var(--text-muted)">The raw C function is benchmarked through swisseph-ffi; no direct Python extension comparison is rendered for that function.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="chart-section">
            <h2 style="margin: 0 0 1.5rem 0">Complexity Matrix (Top 30 Functions)</h2>
            <div class="chart-container"><canvas id="latencyChart"></canvas></div>
        </div>

        <div class="card" style="margin-bottom: 2rem; border-left: 5px solid var(--primary);">
            <h3>Audit Executive Summary</h3>
            <div id="birds-eye" style="font-size: 1.1rem; line-height: 1.6;"></div>
        </div>

        <input type="text" id="searchInput" class="search-box" aria-label="Search 106 functions">

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr><th>Function</th><th>FFI Mean</th><th>Python C-Ext Mean</th><th>Ratio</th><th>P95 Stability</th><th>Verification</th></tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>

    <script>
        const allSystems = {data_json};
        const systemKeys = Object.keys(allSystems);
        let currentKey = systemKeys[0];
        let myChart = null;

        const tabsContainer = document.getElementById('systemTabs');
        systemKeys.forEach(key => {{
            const btn = document.createElement('button');
            btn.className = `tab-btn ${{key === currentKey ? 'active' : ''}}`;
            btn.innerText = key;
            btn.onclick = () => switchSystem(key);
            tabsContainer.appendChild(btn);
        }});

        function switchSystem(key) {{
            currentKey = key;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.innerText === key));
            renderDashboard();
        }}

        function setText(id, value) {{
            document.getElementById(id).innerText = value === null || value === undefined ? '' : String(value);
        }}

        function comparedEntries(results) {{
            return Object.entries(results).filter(e => e[1].ffi && e[1].ext && e[1].ratios);
        }}

        function ffiEntries(results) {{
            return Object.entries(results).filter(e => e[1].ffi);
        }}

        function renderDashboard() {{
            const data = allSystems[currentKey];
            const system = data.system;
            const results = data.results;

            setText('spec-cpu', system.cpu);
            setText('spec-cores', system.cores);
            setText('spec-freq', system.freq);
            setText('spec-arch', system.arch);
            setText('spec-instr', system.instr);
            setText('spec-ram', system.ram);
            setText('spec-os', system.os);
            setText('spec-python', `${{system.python_implementation}} ${{system.python}}`);
            setText('spec-compiler', system.python_compiler);
            setText('spec-lib', system.library);
            setText('spec-comparison', `${{system.comparison_package}} ${{system.comparison_package_version}}`);
            setText('spec-date', system.date);

            const allResults = ffiEntries(results);
            const comparedResults = comparedEntries(results);
            if (comparedResults.length > 0) {{
                const validRatios = comparedResults.map(e => e[1].ratios.mean).filter(r => !isNaN(r) && isFinite(r));
                const sortedRatios = validRatios.sort((a,b) => a-b);
                const medianRatio = sortedRatios[Math.floor(sortedRatios.length / 2)];
                const overheadPct = ((medianRatio - 1) * 100).toFixed(0);
                setText('overall-median', (overheadPct > 0 ? '+' : '') + overheadPct + '%');
                setText('status-text', medianRatio < 1.3 ? 'PRO-TIER PERFORMANCE' : 'STANDARD OVERHEAD');
                document.getElementById('status-text').style.color = medianRatio < 1.3 ? 'var(--success)' : 'var(--primary)';
                const ffiWins = comparedResults.filter(e => e[1].ratios.mean < 1.0).length;
                const winPct = ((ffiWins / comparedResults.length) * 100).toFixed(0);
                document.getElementById('birds-eye').innerHTML = `On this system, swisseph-ffi benchmarks all <strong>${{allResults.length}}</strong> raw C functions. The selected Python C-extension package exposes <strong>${{comparedResults.length}}</strong> directly benchmarked wrapper operations here. FFI is <strong>${{overheadPct}}%</strong> different at the median and is faster in <strong>${{ffiWins}}</strong> compared operations (${{winPct}}%).`;
            }} else {{
                setText('overall-median', 'FFI-ONLY');
                setText('status-text', 'PROFILING MODE');
                document.getElementById('status-text').style.color = 'var(--primary)';
                document.getElementById('birds-eye').innerHTML = `High-precision FFI latency profiling for <strong>${{allResults.length}}</strong> raw C functions on ${{currentKey}}. No Python C-extension comparison data was captured for this system.`;
            }}

            renderTable(document.getElementById('searchInput').value);
            renderChart(comparedResults.length > 0 ? comparedResults : allResults);
        }}

        function renderTable(q = '') {{
            const results = allSystems[currentKey].results;
            const body = document.getElementById('tableBody');
            body.innerHTML = '';
            Object.entries(results).forEach(([name, res]) => {{
                if (q && !name.toLowerCase().includes(q.toLowerCase())) return;
                if (!res.ffi) return;
                const tr = document.createElement('tr');
                const ratioValue = res.ext && res.ratios ? res.ratios.mean : null;
                const ratioText = ratioValue === null ? 'N/A' : ratioValue.toFixed(2) + 'x';
                const ratioColor = ratioValue === null ? 'var(--text-muted)' : (ratioValue > 1 ? 'var(--danger)' : 'var(--success)');
                const tagClass = res.ext ? 'tag-match' : 'tag-pro';
                const tagText = res.ext ? 'WRAPPER-COMPARED' : 'FFI-ONLY';
                tr.innerHTML = `<td style="font-family:'JetBrains Mono', Consolas, monospace; color:var(--primary); font-weight:700">${{name}}</td><td>${{res.ffi.mean.toFixed(2)}} µs</td><td>${{res.ext ? res.ext.mean.toFixed(2) + ' µs' : 'N/A'}}</td><td style="font-weight:800; color:${{ratioColor}}">${{ratioText}}</td><td style="color:var(--text-muted)">${{res.ffi.p95.toFixed(2)}} µs</td><td><span class="tag ${{tagClass}}">${{tagText}}</span></td>`;
                body.appendChild(tr);
            }});
        }}

        function renderChart(dataEntries) {{
            const top30 = dataEntries.slice().sort((a,b) => b[1].ffi.mean - a[1].ffi.mean).slice(0, 30);
            const ctx = document.getElementById('latencyChart').getContext('2d');
            if (myChart) myChart.destroy();
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            const gridColor = isDark ? 'rgba(255,255,255,0.15)' : '#e2e8f0';
            const textColor = isDark ? '#f1f5f9' : '#64748b';

            myChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: top30.map(e => e[0].replace('swe_', '')),
                    datasets: [
                        {{ label: 'FFI Implementation', data: top30.map(e => e[1].ffi.mean), backgroundColor: '#3b82f6' }},
                        {{ label: 'Python C-Extension', data: top30.map(e => e[1].ext ? e[1].ext.mean : 0), backgroundColor: '#ef4444' }}
                    ]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom', labels: {{ color: textColor }} }},
                        tooltip: {{ mode: 'index', intersect: false }}
                    }},
                    scales: {{
                        y: {{ type: 'logarithmic', grid: {{ color: gridColor }}, ticks: {{ color: textColor }}, title: {{ display: true, text: 'Latency (µs) [LOG SCALE]', color: textColor }} }},
                        x: {{ ticks: {{ color: textColor, font: {{ size: 10, weight: 'bold' }} }} }}
                    }}
                }}
            }});
        }}

        const themeToggle = document.getElementById('themeToggle');
        function applyTheme(theme) {{
            document.body.setAttribute('data-theme', theme);
            document.getElementById('themeLabel').innerText = theme === 'light' ? 'Dark Mode' : 'Light Mode';
            localStorage.setItem('theme', theme);
            if (myChart) renderDashboard();
        }}
        applyTheme(localStorage.getItem('theme') || 'light');
        themeToggle.onclick = () => applyTheme(document.body.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
        document.getElementById('searchInput').oninput = (e) => renderTable(e.target.value);
        renderDashboard();
    </script>
</body>
</html>
"""
    (ROOT / "benchmark.html").write_text(html, encoding="utf-8")
    print("Generated docs/benchmark/benchmark.html")


if __name__ == "__main__":
    main()
