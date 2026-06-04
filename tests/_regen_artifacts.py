"""
Regenerate topology.json render metadata + visual artifacts (no LLM).

Applies ONLY the deterministic clustering stage (which now derives
detached_cluster) to the existing topology, re-saves it via the real
save path, and regenerates the Draw.io / Purdue / Graphviz exports
using the existing export pipeline.
"""

import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

from clustering import cluster_topology
from export_drawio import export_drawio
from export_graphviz import export_graphviz
from export_purdue import export_purdue
from main import save_outputs, OUTPUTS_DIR, FRONTEND_JSON_OUTPUT

with open(FRONTEND_JSON_OUTPUT, encoding="utf-8") as fh:
    topo = json.load(fh)

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    topo = cluster_topology(topo)

save_outputs(topo)

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

results = {}
for label, fn, arg in [
    ("graphviz", export_graphviz, str(OUTPUTS_DIR / "kavach_graphviz")),
    ("purdue", export_purdue, str(OUTPUTS_DIR / "kavach_purdue")),
    ("drawio", export_drawio, str(OUTPUTS_DIR / "kavach.drawio")),
]:
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            fn(topo, arg)
        results[label] = "OK"
    except Exception as e:
        results[label] = f"ERROR: {type(e).__name__}: {e}"

print("REGEN RESULTS:")
for k, v in results.items():
    print(f"  {k:9s}: {v}")
