"""
Validation test for review fixes #1 and #3 (no LLM call).

Runs the REAL pipeline functions on a synthetic topology and checks:
  #1  encrypted protocol (HTTPS) gets its capabilities promoted
      False -> True, and the per-control invariant the validator relies
      on (requires_encrypted => encrypted) holds.
  #1 negative control: an unencrypted protocol (EUROBALISE) is NOT
      over-promoted; its crypto capabilities stay False.
  #3  infer_connection_stack flags stack_inferred=True when it fills a
      missing transport from the default stack.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema_validator import ensure_topology_schema
from classifier import classify_topology
from infer_connection_stack import infer_communication_stack
from security_enrichment import apply_security_controls
from validator import validate

CRYPTO_CAPS = ["encrypted", "authentication",
               "integrity_protection", "replay_protection"]


def get_finding(findings, rule):
    """Resilient lookup — returns the finding dict or None."""
    for f in findings:
        if f.get("rule") == rule:
            return f
    return None


def conn_by_id(topo, cid):
    for c in topo["connections"]:
        if c.get("id") == cid:
            return c
    return None


def build_topology():
    return {
        "nodes": [
            {"id": "ews1", "label": "EWS", "type": "engineering_workstation"},
            {"id": "siem1", "label": "SIEM", "type": "siem"},
            {"id": "bal1", "label": "Balise", "type": "trackside_rfid_tag"},
            {"id": "obu1", "label": "OnboardReader", "type": "onboard_rfid_reader"},
        ],
        "connections": [
            # positive: encrypted protocol, transport omitted on purpose
            {"id": "https", "source": "ews1", "target": "siem1",
             "protocol": "HTTPS"},
            # negative control: unencrypted protocol
            {"id": "ebal", "source": "bal1", "target": "obu1",
             "protocol": "EUROBALISE"},
        ],
    }


def run():
    topo = ensure_topology_schema(build_topology())
    topo = classify_topology(topo)
    topo = infer_communication_stack(topo)
    topo = apply_security_controls(topo)
    findings = validate(topo)

    https = conn_by_id(topo, "https")
    ebal = conn_by_id(topo, "ebal")

    results = []

    # ---- Fix #1: capability promotion on encrypted protocol ----------
    https_caps = {c: https.get(c) for c in CRYPTO_CAPS}
    fix1_promote = all(https_caps[c] is True for c in CRYPTO_CAPS)
    results.append(("FIX #1  HTTPS capabilities promoted to True", fix1_promote))

    # ---- Fix #1 downstream invariant (text-free) ---------------------
    # The validator flags a violation iff requires_X but capability X is
    # absent. Assert that false-positive condition is gone for encryption.
    invariant_ok = not (https.get("requires_encrypted", False)
                        and not https.get("encrypted", False))
    results.append(("FIX #1  requires_encrypted => encrypted holds", invariant_ok))

    # ---- Fix #1 negative control: no over-promotion ------------------
    neg_ok = (ebal.get("encrypted") is False
              and ebal.get("authentication") is False)
    results.append(("FIX #1  EUROBALISE stays unencrypted (neg control)", neg_ok))

    # ---- Fix #3: stack_inferred provenance ---------------------------
    fix3 = (https.get("stack_inferred") is True
            and https.get("transport") not in (None, "", "unknown"))
    results.append(("FIX #3  stack_inferred flagged True", fix3))

    # ---- Sanity: validator still produced findings -------------------
    conduit_finding = get_finding(findings, "CONDUIT-PROFILE-VALIDATION")
    results.append(("SANITY  validator returned findings",
                    conduit_finding is not None))

    print("\n" + "=" * 64)
    print("RESULT SUMMARY")
    print("=" * 64)
    print("HTTPS capabilities     :", https_caps)
    print("HTTPS requires_encrypted:", https.get("requires_encrypted"))
    print("HTTPS stack_inferred   :", https.get("stack_inferred"),
          "| transport:", https.get("transport"))
    print("EUROBALISE crypto caps :",
          {c: ebal.get(c) for c in CRYPTO_CAPS})
    print("-" * 64)
    for label, ok in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    overall = all(ok for _, ok in results)
    print("=" * 64)
    print("OVERALL:", "PASS" if overall else "FAIL")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(run())
