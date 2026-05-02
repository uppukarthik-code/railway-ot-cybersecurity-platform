"""
validator.py
Rule-based compliance checks against IEC 62443 design principles.
Runs against the parsed topology JSON after LLM generation.
"""


def validate(topology: dict) -> list[dict]:
    """
    Runs all compliance rules against a topology dict.
    Returns a list of findings — empty list means fully compliant.

    Each finding:
      {
        "rule":    "rule identifier",
        "status":  "PASS" | "FAIL" | "WARN",
        "message": "human-readable explanation"
      }
    """
    findings = []
    nodes = topology.get("nodes", [])
    connections = topology.get("connections", [])

    node_index = {n["id"]: n for n in nodes}
    zones_present = {n["zone"] for n in nodes}

    # ── Rule 1: OT/IT Isolation ───────────────────────────────────────────────
    # IEC 62443: OT nodes must never sit in the corporate_it zone.
    ot_types = {"plc", "rtu", "hmi", "historian"}
    violations = [
        n["id"] for n in nodes
        if n["type"] in ot_types and n["zone"] == "corporate_it"
    ]
    if violations:
        findings.append({
            "rule":    "IEC62443-OT-ISOLATION",
            "status":  "FAIL",
            "message": (
                f"OT node(s) found in corporate_it zone: {', '.join(violations)}. "
                "OT assets must reside in control or field zones only."
            ),
        })
    else:
        findings.append({
            "rule":    "IEC62443-OT-ISOLATION",
            "status":  "PASS",
            "message": "All OT nodes are correctly isolated from the corporate IT zone.",
        })

    # ── Rule 2: DMZ presence ──────────────────────────────────────────────────
    # IEC 62443: A DMZ must exist when corporate_it and supervisory/control zones
    # are both present — direct IT-to-OT connectivity is prohibited.
    ot_zones = {"supervisory", "control", "field"}
    needs_dmz = "corporate_it" in zones_present and bool(zones_present & ot_zones)
    has_dmz = "dmz" in zones_present

    if needs_dmz and not has_dmz:
        findings.append({
            "rule":    "IEC62443-DMZ-REQUIRED",
            "status":  "FAIL",
            "message": (
                "Corporate IT and OT zones are both present but no DMZ zone exists. "
                "IEC 62443 requires a DMZ to prevent direct IT-to-OT connectivity."
            ),
        })
    else:
        findings.append({
            "rule":    "IEC62443-DMZ-REQUIRED",
            "status":  "PASS",
            "message": "DMZ zone is present or not required for this topology.",
        })

    # ── Rule 3: Cross-zone connections must be encrypted ─────────────────────
    # IEC 62443: All traffic crossing a security zone boundary must be encrypted.
    unencrypted_cross_zone = []
    for conn in connections:
        src = node_index.get(conn["source"])
        tgt = node_index.get(conn["target"])
        if src and tgt and src["zone"] != tgt["zone"]:
            if not conn.get("encrypted", False):
                unencrypted_cross_zone.append(
                    f"{conn['source']} -> {conn['target']} ({conn.get('protocol', 'unknown')})"
                )

    if unencrypted_cross_zone:
        findings.append({
            "rule":    "IEC62443-ENCRYPTED-CROSS-ZONE",
            "status":  "FAIL",
            "message": (
                f"Unencrypted cross-zone connection(s) detected: "
                f"{'; '.join(unencrypted_cross_zone)}. "
                "All traffic crossing zone boundaries must be encrypted."
            ),
        })
    else:
        findings.append({
            "rule":    "IEC62443-ENCRYPTED-CROSS-ZONE",
            "status":  "PASS",
            "message": "All cross-zone connections are encrypted.",
        })

    return findings


def print_report(findings: list[dict]) -> None:
    print("\n── Compliance Report (IEC 62443) ────────────────────────────────")
    passed = sum(1 for f in findings if f["status"] == "PASS")
    failed = sum(1 for f in findings if f["status"] == "FAIL")
    warned = sum(1 for f in findings if f["status"] == "WARN")

    for f in findings:
        icon = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠"}.get(f["status"], "?")
        print(f"  {icon} [{f['status']}] {f['rule']}")
        print(f"      {f['message']}")

    print(f"\n  Result: {passed} passed, {failed} failed, {warned} warnings")
    if failed == 0:
        print("  ✓ Topology is IEC 62443 compliant")
    else:
        print("  ✗ Topology has compliance violations — review before deployment")
    print("─────────────────────────────────────────────────────────────────\n")
