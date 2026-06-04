"""
Governance-model delta harness (no LLM).

Loads the real frontend topology, runs the link + purdue validators, and
prints a stable, sorted error list so a before/after delta can be diffed.
Run with `--tag baseline` or `--tag post` to label the snapshot.
"""

import argparse
import io
import json
import os
import sys
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators.validate_links import validate_links
from validators.validate_purdue import validate_purdue
from conduits import build_conduits

TOPO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend", "src", "data", "topology.json",
)


def run(tag):
    with open(TOPO, encoding="utf-8") as fh:
        topo = json.load(fh)

    # Resolve conduit_class from FLOW_RULES exactly as the real
    # pipeline does (main.run_pipeline -> build_conduits), so the
    # validators see the governance-assigned conduit class rather than
    # the stale "generic" placeholder baked into the stored topology.
    # Silence the pipeline/validators' own prints; we only want the
    # returned error lists.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        topo = build_conduits(topo)
        link_errors = validate_links(topo)
        purdue_errors = validate_purdue(topo)

    snapshot = {
        "link_errors": sorted(link_errors),
        "purdue_errors": sorted(purdue_errors),
    }

    out = os.path.join(os.path.dirname(__file__), f"_delta_{tag}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)

    print(f"== {tag.upper()} ==")
    print(f"LINK errors   : {len(link_errors)}")
    for e in snapshot["link_errors"]:
        print(f"  - {e}")
    print(f"PURDUE errors : {len(purdue_errors)}")
    for e in snapshot["purdue_errors"]:
        print(f"  - {e}")
    print(f"(written to {out})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="baseline")
    run(ap.parse_args().tag)
