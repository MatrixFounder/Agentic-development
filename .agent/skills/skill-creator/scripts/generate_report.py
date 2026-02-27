#!/usr/bin/env python3
"""
Generate an HTML report from a benchmark.json file.

Takes the JSON output from aggregate_benchmark.py and generates a visual HTML report
showing comparison between configurations.

Usage:
    python generate_report.py benchmark.json
"""

import argparse
import html
import json
import sys
from pathlib import Path


def generate_html(data: dict) -> str:
    """Generate HTML report from benchmark data."""
    metadata = data.get("metadata", {})
    skill_name = metadata.get("skill_name", "Unknown Skill")
    title_prefix = html.escape(skill_name + " \u2014 ")
    run_summary = data.get("run_summary", {})
    
    # Exclude delta from configs
    configs = [k for k in run_summary if k != "delta"]
    
    html_parts = ["""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>""" + title_prefix + """Benchmark Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Lora:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Lora', Georgia, serif; max-width: 100%; margin: 0 auto; padding: 20px; background: #faf9f5; color: #141413; }
        h1 { font-family: 'Poppins', sans-serif; color: #141413; }
        .summary { background: white; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #e8e6dc; }
        table { border-collapse: collapse; background: white; border: 1px solid #e8e6dc; border-radius: 6px; width: 100%; margin-bottom: 30px; }
        th, td { padding: 10px 15px; text-align: left; border: 1px solid #e8e6dc; }
        th { font-family: 'Poppins', sans-serif; background: #141413; color: #faf9f5; font-weight: 500; }
        .delta-col { background: #f0f6fc; }
        .pass { color: #788c5d; font-weight: bold; }
        .fail { color: #c44; font-weight: bold; }
    </style>
</head>
<body>
    <h1>""" + title_prefix + """Benchmark Report</h1>
    <div class="summary">
        <p><strong>Model:</strong> """ + html.escape(metadata.get("executor_model", "Unknown")) + """</p>
        <p><strong>Timestamp:</strong> """ + html.escape(metadata.get("timestamp", "Unknown")) + """</p>
        <p><strong>Evals Run:</strong> """ + html.escape(str(metadata.get("evals_run", []))) + """</p>
    </div>
    
    <h2>Aggregate Summary</h2>
    <table>
        <thead>
            <tr>
                <th>Metric</th>
"""]

    for config in configs:
        html_parts.append(f"                <th>{html.escape(config)}</th>\n")
    if "delta" in run_summary:
        html_parts.append('                <th class="delta-col">Delta</th>\n')
        
    html_parts.append("""            </tr>
        </thead>
        <tbody>
""")

    metrics = [
        ("Pass Rate", "pass_rate", lambda v: f"{v*100:.1f}%"),
        ("Time (s)", "time_seconds", lambda v: f"{v:.1f}s"),
        ("Tokens", "tokens", lambda v: f"{v:.0f}")
    ]
    
    for label, key, formatter in metrics:
        html_parts.append(f"            <tr>\n                <td><strong>{label}</strong></td>\n")
        for config in configs:
            mean = run_summary.get(config, {}).get(key, {}).get("mean", 0)
            stddev = run_summary.get(config, {}).get(key, {}).get("stddev", 0)
            val_str = f"{formatter(mean)} ± {formatter(stddev)}"
            html_parts.append(f"                <td>{html.escape(val_str)}</td>\n")
            
        if "delta" in run_summary:
            delta_val = run_summary["delta"].get(key, "-")
            if key == "pass_rate" and delta_val != "-":
                # pass rate delta is usually stored as a string like "+0.15" by aggregate_benchmark
                try:
                    num = float(delta_val)
                    delta_str = f"{num*100:+.1f}%"
                    css = "pass" if num > 0 else "fail" if num < 0 else ""
                except ValueError:
                    delta_str = str(delta_val)
                    css = ""
                html_parts.append(f'                <td class="delta-col"><span class="{css}">{html.escape(delta_str)}</span></td>\n')
            else:
                html_parts.append(f'                <td class="delta-col">{html.escape(str(delta_val))}</td>\n')
        html_parts.append("            </tr>\n")

    html_parts.append("""        </tbody>
    </table>
""")

    # Detailed runs table
    runs = data.get("runs", [])
    if runs:
        html_parts.append("""    <h2>Detailed Runs</h2>
    <table>
        <thead>
            <tr>
                <th>Eval ID</th>
                <th>Config</th>
                <th>Run #</th>
                <th>Pass Rate</th>
                <th>Time (s)</th>
                <th>Tokens</th>
            </tr>
        </thead>
        <tbody>
""")
        for run in sorted(runs, key=lambda r: (r.get("eval_id", 0), r.get("configuration", ""), r.get("run_number", 0))):
            res = run.get("result", {})
            pr = res.get("pass_rate", 0)
            css = "pass" if pr == 1.0 else "fail" if pr == 0.0 else ""
            html_parts.append(f"""            <tr>
                <td>{run.get("eval_id", "-")}</td>
                <td>{html.escape(run.get("configuration", "-"))}</td>
                <td>{run.get("run_number", "-")}</td>
                <td class="{css}">{pr*100:.0f}% ({res.get("passed", 0)}/{res.get("total", 0)})</td>
                <td>{res.get("time_seconds", 0):.1f}s</td>
                <td>{res.get("tokens", 0)}</td>
            </tr>
""")
        html_parts.append("""        </tbody>
    </table>
""")

    if data.get("notes"):
        html_parts.append("    <h2>Analyzer Notes</h2>\n    <ul>\n")
        for note in data["notes"]:
            html_parts.append(f"        <li>{html.escape(note)}</li>\n")
        html_parts.append("    </ul>\n")

    html_parts.append("""</body>
</html>""")

    return "".join(html_parts)


def main():
    parser = argparse.ArgumentParser(description="Generate HTML report from benchmark.json")
    parser.add_argument("input", help="Path to benchmark.json")
    parser.add_argument("-o", "--output", default=None, help="Output HTML file (default: input_base.html)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(input_path.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
        sys.exit(1)
    html_output = generate_html(data)

    output_path = args.output or input_path.with_suffix(".html")
    Path(output_path).write_text(html_output)
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
