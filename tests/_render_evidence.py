"""
Rendering-fix evidence harness (no LLM).

Loads the real frontend topology, optionally re-runs the deterministic
clustering stage (the only stage touched by the rendering fix), and prints
stable, sorted findings counts so a before/after delta can be diffed.

Usage:
    python tests/_render_evidence.py --tag before
    python tests/_render_evidence.py --tag after --recluster
"""

import argparse
import contextlib
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators import (
    validate_assets,
    validate_links,
    validate_zones,
    validate_purdue,
    validate_protocols,
    validate_rendering,
)
from validator import validate
from risk_engine import analyze_risk
from clustering import cluster_topology

TOPO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend", "src", "data", "topology.json",
)


def _silent(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return fn(*a)


def run(tag, recluster):
    with open(TOPO, encoding="utf-8") as fh:
        topo = json.load(fh)

    if recluster:
        topo = _silent(cluster_topology, topo)

    validators = {
        "assets": validate_assets,
        "links": validate_links,
        "zones": validate_zones,
        "purdue": validate_purdue,
        "protocols": validate_protocols,
        "rendering": validate_rendering,
    }

    counts = {}
    render_detail = []
    for name, fn in validators.items():
        errs = _silent(fn, topo)
        counts[name] = sorted(errs)
        if name == "rendering":
            render_detail = sorted(errs)

    findings = _silent(validate, topo)
    fail = [f for f in findings if str(f.get("status", "")).upper() == "FAIL"]

    risk = _silent(analyze_risk, topo)
    risk_count = len(risk) if isinstance(risk, (list, tuple)) else len(risk or [])

    snapshot = {
        "validator_counts": {k: len(v) for k, v in counts.items()},
        "validate_fail_count": len(fail),
        "validate_fail_rules": sorted(f.get("rule", "") for f in fail),
        "risk_findings_count": risk_count,
        "render_errors": render_detail,
    }

    out = os.path.join(os.path.dirname(__file__), f"_render_{tag}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)

    print(f"== {tag.upper()} (recluster={recluster}) ==")
    for k, v in counts.items():
        print(f"  {k:10s}: {len(v)}")
    print(f"  validate FAIL : {len(fail)}  rules={snapshot['validate_fail_rules']}")
    print(f"  risk findings : {risk_count}")
    if render_detail:
        print("  render errors:")
        for e in render_detail:
            print(f"    - {e}")
    print(f"(written to {out})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="before")
    ap.add_argument("--recluster", action="store_true")
    run(ap.parse_args().tag, ap.parse_args().recluster)
