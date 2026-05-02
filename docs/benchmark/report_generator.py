"""Generate the static Python benchmark dashboard from JSON artifacts."""

# ruff: noqa: E501

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_results() -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for path in sorted(ROOT.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and isinstance(data.get("system"), dict):
            data["_file"] = path.name
            payloads.append(data)
    if not payloads:
        raise SystemExit("No benchmark JSON files found in docs/benchmark.")
    return payloads


def fmt_ns(value: object) -> str:
    number = float(value)
    if number >= 1_000_000:
        return f"{number / 1_000_000:.3f} ms"
    if number >= 1_000:
        return f"{number / 1_000:.3f} us"
    return f"{number:.1f} ns"


def fmt_bytes(value: object) -> str:
    number = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if number < 1024 or unit == "TiB":
            return f"{number:.1f} {unit}"
        number /= 1024
    return f"{number:.1f} TiB"


def result_map(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(item["name"]): item for item in payload["results"]}  # type: ignore[index]


def ratio_cell(base: dict[str, object] | None, other: dict[str, object] | None) -> str:
    if not base or not other:
        raise ValueError("comparison rows require both benchmark results")
    ratio = float(base["median_ns"]) / float(other["median_ns"])
    cls = "win" if ratio <= 1.0 else "loss"
    return f'<span class="{cls}">{ratio:.2f}x</span>'


def render_payload(payload: dict[str, object]) -> str:
    system = payload["system"]  # type: ignore[index]
    specs = [
        ("Operating System", system.get("os", "")),
        ("Kernel/Release", system.get("release", "")),
        ("Architecture", system.get("machine", "")),
        ("Processor", system["processor"]),
        ("CPU Threads", system.get("cpu_count", "")),
        ("Runner RAM", fmt_bytes(system["ram_bytes"])),
        ("Python Runtime", f"{system['implementation']} {system['python_version']}"),
        ("Python Compiler", system["compiler"]),
        ("Distribution", f"{system['distribution']} {system['distribution_version']}"),
        ("Swiss Ephemeris", system["swiss_ephemeris_version"]),
        ("Configured Functions", system.get("configured_function_count", "")),
        (
            "Benchmarked Functions",
            system.get("benchmarked_function_count", len(payload["results"])),
        ),
        ("Native/Module Path", system.get("native_library") or system["module_file"]),
        ("Generated At UTC", system.get("generated_at_utc", "")),
    ]
    spec_rows = "".join(
        f"<tr><th>{html.escape(str(label))}</th><td>{html.escape(str(value))}</td></tr>"
        for label, value in specs
    )
    rows = []
    for item in payload["results"]:  # type: ignore[index]
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(str(item['name']))}</code></td>"
            f"<td>{fmt_ns(item['median_ns'])}</td>"
            f"<td>{fmt_ns(item['mean_ns'])}</td>"
            f"<td>{fmt_ns(item['min_ns'])}</td>"
            f"<td>{fmt_ns(item['max_ns'])}</td>"
            f"<td>{item.get('warmup', 0)} warmup + {item['iterations']} measured</td>"
            "</tr>"
        )
    return f"""
    <section class="card">
      <h2>{html.escape(str(system["library"]))}</h2>
      <div class="meta">
        <span>{html.escape(str(system["distribution"]))} {html.escape(str(system["distribution_version"]))}</span>
        <span>{html.escape(str(system["system"]))} {html.escape(str(system["machine"]))}</span>
        <span>Python {html.escape(str(system["python_version"]))}</span>
      </div>
      <table class="specs">
        <tbody>{spec_rows}</tbody>
      </table>
      <table>
        <thead>
          <tr><th>Operation</th><th>Median</th><th>Mean</th><th>Min</th><th>Max</th><th>Samples</th></tr>
        </thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </section>
    """


def render_comparison(payloads: list[dict[str, object]]) -> str:
    groups: dict[str, list[dict[str, object]]] = {}
    for payload in payloads:
        system = payload["system"]  # type: ignore[index]
        key = f"{system.get('system')} {system.get('machine')}"
        groups.setdefault(key, []).append(payload)

    sections = []
    for group, items in sorted(groups.items()):
        ffi = next((p for p in items if p["system"].get("library") == "swisseph-ffi"), None)  # type: ignore[index]
        if not ffi:
            continue
        ffi_results = result_map(ffi)
        rows = []
        for name, ffi_result in ffi_results.items():
            cells = [
                f"<td><code>{html.escape(name)}</code></td>",
                f"<td>{fmt_ns(ffi_result['median_ns'])}</td>",
            ]
            for label in ("pysweph", "pyswisseph"):
                other_payload = next(
                    (p for p in items if p["system"].get("distribution") == label),  # type: ignore[index]
                    None,
                )
                other_result = result_map(other_payload).get(name) if other_payload else None
                if other_result is None:
                    cells.append("<td></td><td></td>")
                    continue
                cells.append(f"<td>{fmt_ns(other_result['median_ns'])}</td>")
                cells.append(f"<td>{ratio_cell(ffi_result, other_result)}</td>")
            rows.append(f"<tr>{''.join(cells)}</tr>")
        sections.append(
            f"""
            <section class="card">
              <h2>{html.escape(group)} Comparison</h2>
              <table>
                <thead>
                  <tr>
                    <th>Operation</th>
                    <th>swisseph-ffi</th>
                    <th>pysweph</th>
                    <th>FFI / pysweph</th>
                    <th>pyswisseph</th>
                    <th>FFI / pyswisseph</th>
                  </tr>
                </thead>
                <tbody>{"".join(rows)}</tbody>
              </table>
            </section>
            """
        )
    return "\n".join(sections)


def main() -> None:
    payloads = load_results()
    json_payload = json.dumps(payloads, separators=(",", ":"))
    rendered = "\n".join(render_payload(payload) for payload in payloads)
    comparison = render_comparison(payloads)
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Swiss Ephemeris Python FFI Benchmark</title>
  <style>
    :root {{ color-scheme: light; --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --muted: #475569; --line: #cbd5e1; --accent: #0369a1; --win: #15803d; --loss: #c2410c; }}
    [data-theme="dark"] {{ color-scheme: dark; --bg: #0f172a; --card: #111827; --text: #f8fafc; --muted: #cbd5e1; --line: #334155; --accent: #38bdf8; --win: #22c55e; --loss: #f97316; }}
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: var(--bg); color: var(--text); }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 32px 18px; }}
    header {{ margin-bottom: 24px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }}
    .theme-toggle {{ border: 1px solid var(--line); background: var(--card); color: var(--text); border-radius: 8px; padding: 10px 14px; cursor: pointer; font-weight: 700; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(28px, 5vw, 48px); }}
    h2 {{ margin: 0 0 12px; font-size: 20px; }}
    p {{ color: var(--muted); max-width: 980px; line-height: 1.6; }}
    .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 18px; margin: 18px 0; overflow-x: auto; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; color: var(--muted); }}
    .meta span {{ border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 760px; }}
    .specs {{ min-width: 0; margin-bottom: 18px; }}
    .specs th {{ width: 220px; }}
    .specs td {{ word-break: break-word; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }}
    th {{ color: var(--accent); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
    code {{ font-family: "JetBrains Mono", Consolas, monospace; }}
    .win {{ color: var(--win); font-weight: 700; }}
    .loss {{ color: var(--loss); font-weight: 700; }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="topbar">
        <div>
          <h1>Swiss Ephemeris Python FFI Benchmark</h1>
        </div>
        <button class="theme-toggle" type="button" id="themeToggle">Theme</button>
      </div>
      <p>
        Multi-system benchmark generated from GitHub Actions JSON artifacts.
        The comparison installs <code>swisseph-ffi</code>, <code>pysweph</code>,
        and <code>pyswisseph</code> in separate virtual environments because the
        extension packages share the <code>swisseph</code> import name.
      </p>
    </header>
    {comparison}
    {rendered}
  </main>
  <script type="application/json" id="benchmark-data">{html.escape(json_payload)}</script>
  <script>
    const root = document.documentElement;
    const savedTheme = localStorage.getItem("theme");
    const preferredDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = savedTheme || (preferredDark ? "dark" : "light");
    document.getElementById("themeToggle").addEventListener("click", () => {{
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      localStorage.setItem("theme", next);
    }});
  </script>
</body>
</html>
"""
    (ROOT / "benchmark.html").write_text(page, encoding="utf-8")
    print("Generated docs/benchmark/benchmark.html")


if __name__ == "__main__":
    main()
