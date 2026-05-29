"""
graphviz_debug.py
ADVANCED Graphviz layout debugger.
Root-cause analysis for Purdue renderer layout instability.
"""

import subprocess
import csv
import re
from pathlib import Path
from collections import Counter


# ============================================================
# RUN COMMAND
# ============================================================
def run_command(cmd):
    print("\n" + "=" * 60)
    print("RUNNING")
    print("=" * 60)
    print(" ".join(cmd))
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result


# ============================================================
# PARSE PLAIN FILE
# ============================================================
def parse_plain_file(plain_file):
    nodes = []
    with open(
        plain_file,
        encoding="utf-8",
    ) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("node"):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            try:
                nodes.append(
                    {
                        "node": parts[1],
                        "x": float(parts[2]),
                        "y": float(parts[3]),
                        "width": float(parts[4]),
                        "height": float(parts[5]),
                    }
                )
            except Exception:
                continue
    return nodes


# ============================================================
# SAVE CSV
# ============================================================
def save_csv(nodes, output_csv):
    with open(
        output_csv,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "node",
                "x",
                "y",
                "width",
                "height",
            ],
        )
        writer.writeheader()
        for row in nodes:
            writer.writerow(row)


# ============================================================
# ANALYZE DOT
# ============================================================
def analyze_dot(dot_file):
    text = Path(dot_file).read_text(
        encoding="utf-8",
    )
    invisible_edges = len(
        re.findall(
            r'style="?invis',
            text,
        )
    )
    clusters = len(
        re.findall(
            r"subgraph cluster_",
            text,
        )
    )
    groups = len(
        re.findall(
            r"group=",
            text,
        )
    )
    constraint_true = len(
        re.findall(
            r'constraint="?true',
            text,
        )
    )
    constraint_false = len(
        re.findall(
            r'constraint="?false',
            text,
        )
    )
    weights = re.findall(
        r'weight="?([0-9.]+)',
        text,
    )
    minlens = re.findall(
        r'minlen="?([0-9.]+)',
        text,
    )
    relay_nodes = re.findall(
        r"relay_[a-zA-Z0-9_]+",
        text,
    )
    orthogonal_edges = len(
        re.findall(
            r"splines=ortho",
            text,
        )
    )
    compound_enabled = len(
        re.findall(
            r'compound="?true',
            text,
        )
    )
    newrank_enabled = len(
        re.findall(
            r'newrank="?true',
            text,
        )
    )
    print("\n" + "=" * 60)
    print("DOT STRUCTURE INSPECTION")
    print("=" * 60)
    print(f"Invisible edges         : {invisible_edges}")
    print(f"Clusters                : {clusters}")
    print(f"Group enforcement       : {groups}")
    print(f"\nConstraint=true         : {constraint_true}")
    print(f"Constraint=false        : {constraint_false}")
    print(f"\nWeight entries          : {len(weights)}")
    print(f"Minlen entries          : {len(minlens)}")
    print(f"\nRelay nodes             : {len(set(relay_nodes))}")
    print(f"Orthogonal splines      : {orthogonal_edges}")
    print(f"Compound routing        : {compound_enabled}")
    print(f"Newrank enabled         : {newrank_enabled}")
    # ========================================================
    # WEIGHT HISTOGRAM
    # ========================================================
    if weights:
        print("\nEDGE WEIGHT DISTRIBUTION")
        counter = Counter(weights)
        for weight, count in sorted(
            counter.items(),
            key=lambda x: float(x[0]),
        ):
            print(f"  weight={weight:<6} -> {count}")
    # ========================================================
    # MINLEN HISTOGRAM
    # ========================================================
    if minlens:
        print("\nMINLEN DISTRIBUTION")
        counter = Counter(minlens)
        for minlen, count in sorted(
            counter.items(),
            key=lambda x: float(x[0]),
        ):
            print(f"  minlen={minlen:<6} -> {count}")


# ============================================================
# ANALYZE LAYOUT
# ============================================================
def analyze_layout(nodes):
    print("\n" + "=" * 60)
    print("LAYOUT ANALYSIS")
    print("=" * 60)
    print(f"\nTOTAL NODES: {len(nodes)}")
    if not nodes:
        return
    xs = {}
    ys = {}
    for n in nodes:
        x = round(
            n["x"],
            2,
        )
        y = round(
            n["y"],
            2,
        )
        xs.setdefault(x, []).append(n)
        ys.setdefault(y, []).append(n)
    # ========================================================
    # SPREAD ANALYSIS
    # ========================================================
    all_x = [n["x"] for n in nodes]
    all_y = [n["y"] for n in nodes]
    print("\nCOORDINATE SPREAD")
    print(f"X RANGE: " f"{min(all_x):.2f} -> " f"{max(all_x):.2f}")
    print(f"Y RANGE: " f"{min(all_y):.2f} -> " f"{max(all_y):.2f}")
    print(f"X SPREAD: " f"{max(all_x) - min(all_x):.2f}")
    print(f"Y SPREAD: " f"{max(all_y) - min(all_y):.2f}")
    # ========================================================
    # HORIZONTAL GROUPS
    # ========================================================
    print("\nHORIZONTAL GROUPS")
    for y, group in sorted(ys.items()):
        if len(group) > 1:
            print(f"\nY = {y}")
            for g in group:
                print(f"  {g['node']}")
    # ========================================================
    # VERTICAL GROUPS
    # ========================================================
    print("\nVERTICAL GROUPS")
    for x, group in sorted(xs.items()):
        if len(group) > 1:
            print(f"\nX = {x}")
            for g in group:
                print(f"  {g['node']}")
    # ========================================================
    # RELAY NODES
    # ========================================================
    relay_nodes = [n for n in nodes if n["node"].startswith("relay_")]
    if relay_nodes:
        print("\nRELAY NODE ANALYSIS")
        for n in relay_nodes:
            print(f"{n['node']} | " f"X={n['x']:.2f} | " f"Y={n['y']:.2f}")
    # ========================================================
    # CLUSTER EXPLOSION DETECTION
    # ========================================================
    print("\nLAYOUT HEURISTICS")
    x_spread = max(all_x) - min(all_x)
    y_spread = max(all_y) - min(all_y)
    if x_spread > 80:
        print("[WARN] Extreme horizontal expansion detected.")
    if y_spread > 80:
        print("[WARN] Extreme vertical expansion detected.")
    if len(relay_nodes) > 10:
        print("[WARN] Excessive relay nodes detected.")


# ============================================================
# PARSE XDOT CLUSTER BOUNDS
# ============================================================
def analyze_xdot_clusters(xdot_file):
    text = Path(xdot_file).read_text(
        encoding="utf-8",
    )
    clusters = re.findall(
        r"(cluster_[^ ]+).*?bb=\"([0-9.,]+)\"",
        text,
        re.DOTALL,
    )
    print("\n" + "=" * 60)
    print("CLUSTER BOUNDING BOX ANALYSIS")
    print("=" * 60)
    for cluster_name, bb in clusters:
        try:
            x1, y1, x2, y2 = map(
                float,
                bb.split(","),
            )
            width = x2 - x1
            height = y2 - y1
            print(f"{cluster_name:<32} " f"W={width:.2f} " f"H={height:.2f}")
            if width > 40:
                print("  [WARN] Excessive cluster width.")
            if height > 20:
                print("  [WARN] Excessive cluster height.")
        except Exception:
            continue


# ============================================================
# FULLY RESOLVED DOT ANALYSIS
# ============================================================
def analyze_resolved_dot(resolved_dot_file):
    text = Path(resolved_dot_file).read_text(
        encoding="utf-8",
    )
    rank_constraints = len(
        re.findall(
            r"rank=",
            text,
        )
    )
    print("\n" + "=" * 60)
    print("RESOLVED DOT ANALYSIS")
    print("=" * 60)
    print(f"Rank constraints: {rank_constraints}")


# ============================================================
# MAIN DEBUG FUNCTION
# ============================================================
def debug_graphviz_layout(dot_file):
    print("\n" + "=" * 60)
    print("ADVANCED KAVACH PURDUE GRAPH DEBUGGER")
    print("=" * 60)
    dot_path = Path(dot_file)
    debug_dir = dot_path.parent / "debug"
    debug_dir.mkdir(
        exist_ok=True,
    )
    svg_file = debug_dir / "kavach_debug.svg"
    plain_file = debug_dir / "kavach_debug.plain"
    xdot_file = debug_dir / "kavach_debug.xdot"
    resolved_dot = debug_dir / "resolved_layout.dot"
    csv_file = debug_dir / "node_coordinates.csv"
    # ========================================================
    # SVG
    # ========================================================
    run_command(
        [
            "dot",
            "-Tsvg",
            str(dot_path),
            "-o",
            str(svg_file),
        ]
    )
    # ========================================================
    # PLAIN
    # ========================================================
    run_command(
        [
            "dot",
            "-Tplain",
            str(dot_path),
            "-o",
            str(plain_file),
        ]
    )
    # ========================================================
    # XDOT
    # ========================================================
    run_command(
        [
            "dot",
            "-Txdot",
            str(dot_path),
            "-o",
            str(xdot_file),
        ]
    )
    # ========================================================
    # RESOLVED DOT
    # ========================================================
    run_command(
        [
            "dot",
            "-Tdot",
            str(dot_path),
            "-o",
            str(resolved_dot),
        ]
    )
    # ========================================================
    # STRUCTURE ANALYSIS
    # ========================================================
    analyze_dot(dot_path)
    # ========================================================
    # LAYOUT ANALYSIS
    # ========================================================
    nodes = parse_plain_file(plain_file)
    analyze_layout(nodes)
    # ========================================================
    # CLUSTER ANALYSIS
    # ========================================================
    analyze_xdot_clusters(xdot_file)
    # ========================================================
    # RESOLVED DOT ANALYSIS
    # ========================================================
    analyze_resolved_dot(resolved_dot)
    # ========================================================
    # CSV EXPORT
    # ========================================================
    save_csv(
        nodes,
        csv_file,
    )
    # ========================================================
    # FINAL
    # ========================================================
    print("\n" + "=" * 60)
    print("CSV GENERATED")
    print("=" * 60)
    print(csv_file)
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)
    print("\nGenerated files:")
    print(svg_file)
    print(plain_file)
    print(xdot_file)
    print(resolved_dot)
    print(csv_file)


# ============================================================
# ENTRYPOINT
# ============================================================
if __name__ == "__main__":
    debug_graphviz_layout("outputs/kavach_purdue.dot")
