"""
validator.py
Advanced IEC 62443 + Railway signalling cybersecurity validator.
"""

# ============================================================
# VALIDATION
# ============================================================

def validate(topology: dict) -> list[dict]:

    findings = []

    nodes = topology.get(
        "nodes",
        []
    )

    connections = topology.get(
        "connections",
        []
    )

    node_index = {
        n["id"]: n
        for n in nodes
    }

    zones_present = {
        n["zone"]
        for n in nodes
    }

    # ========================================================
    # RULE 1 — OT / ENTERPRISE ISOLATION
    # ========================================================

    ot_types = {

        "plc",
        "rtu",
        "hmi",
        "historian",
        "ei",
        "kavach_station",
        "kavach_onboard",
        "safety_server",
    }

    violations = []

    for node in nodes:

        if (
            node["type"] in ot_types
            and node["zone"] == "enterprise_it"
        ):

            violations.append(
                node["id"]
            )

    if violations:

        findings.append({

            "rule":
                "IEC62443-OT-ISOLATION",

            "status":
                "FAIL",

            "message":
                (
                    "Safety / OT nodes detected "
                    "inside enterprise IT zone: "
                    + ", ".join(violations)
                )
        })

    else:

        findings.append({

            "rule":
                "IEC62443-OT-ISOLATION",

            "status":
                "PASS",

            "message":
                "All OT/safety nodes properly isolated."
        })

    # ========================================================
    # RULE 2 — IDMZ REQUIRED
    # ========================================================

    ot_zones = {

        "supervisory",
        "station_control",
        "interlocking",
        "radio_network",
        "field",
        "onboard",
    }

    needs_dmz = (

        "enterprise_it" in zones_present
        and bool(
            zones_present & ot_zones
        )
    )

    has_dmz = (
        "idmz" in zones_present
    )

    if needs_dmz and not has_dmz:

        findings.append({

            "rule":
                "IEC62443-IDMZ-REQUIRED",

            "status":
                "FAIL",

            "message":
                (
                    "Enterprise IT and OT "
                    "zones coexist without IDMZ."
                )
        })

    else:

        findings.append({

            "rule":
                "IEC62443-IDMZ-REQUIRED",

            "status":
                "PASS",

            "message":
                "IDMZ present or not required."
        })

    # ========================================================
    # RULE 3 — ENCRYPTION
    # ========================================================

    unencrypted = []

    for conn in connections:

        src = node_index.get(
            conn["source"]
        )

        tgt = node_index.get(
            conn["target"]
        )

        if not src or not tgt:
            continue

        cross_zone = (
            src["zone"] != tgt["zone"]
        )

        if (
            cross_zone
            and not conn.get(
                "encrypted",
                False
            )
        ):

            unencrypted.append(

                f"{conn['source']} -> "
                f"{conn['target']}"
            )

    if unencrypted:

        findings.append({

            "rule":
                "IEC62443-CROSSZONE-ENCRYPTION",

            "status":
                "FAIL",

            "message":
                (
                    "Unencrypted cross-zone "
                    "connections: "
                    + "; ".join(unencrypted)
                )
        })

    else:

        findings.append({

            "rule":
                "IEC62443-CROSSZONE-ENCRYPTION",

            "status":
                "PASS",

            "message":
                "All cross-zone conduits encrypted."
        })

    # ========================================================
    # RULE 4 — SIL-4 DOMAIN ISOLATION
    # ========================================================

    sil4_nodes = []

    for node in nodes:

        if node.get(
            "safety_critical",
            False
        ):

            sil4_nodes.append(node)

    unsafe_links = []

    for conn in connections:

        src = node_index.get(
            conn["source"]
        )

        tgt = node_index.get(
            conn["target"]
        )

        if not src or not tgt:
            continue

        src_safe = src.get(
            "safety_critical",
            False
        )

        tgt_safe = tgt.get(
            "safety_critical",
            False
        )

        if src_safe and tgt["zone"] == "enterprise_it":

            unsafe_links.append(
                conn["source"]
            )

        if tgt_safe and src["zone"] == "enterprise_it":

            unsafe_links.append(
                conn["target"]
            )

    if unsafe_links:

        findings.append({

            "rule":
                "EN50159-SIL4-ISOLATION",

            "status":
                "FAIL",

            "message":
                (
                    "Safety-critical systems "
                    "exposed to enterprise IT: "
                    + ", ".join(unsafe_links)
                )
        })

    else:

        findings.append({

            "rule":
                "EN50159-SIL4-ISOLATION",

            "status":
                "PASS",

            "message":
                "Safety-critical domains isolated."
        })

    # ========================================================
    # RULE 5 — RaSTA ENCRYPTION
    # ========================================================

    rasta_failures = []

    for conn in connections:

        protocol = conn.get(
            "protocol",
            ""
        ).lower()

        if "rasta" in protocol:

            if not conn.get(
                "encrypted",
                False
            ):

                rasta_failures.append(
                    f"{conn['source']} -> "
                    f"{conn['target']}"
                )

    if rasta_failures:

        findings.append({

            "rule":
                "EN50159-RASTA-ENCRYPTION",

            "status":
                "FAIL",

            "message":
                (
                    "Unencrypted RaSTA links: "
                    + "; ".join(rasta_failures)
                )
        })

    else:

        findings.append({

            "rule":
                "EN50159-RASTA-ENCRYPTION",

            "status":
                "PASS",

            "message":
                "All RaSTA links encrypted."
        })

    # ========================================================
    # RULE 6 — IDS / SIEM COVERAGE
    # ========================================================

    security_nodes = {

        "ids",
        "ips",
        "siem"
    }

    security_present = any(

        n["type"] in security_nodes
        for n in nodes
    )

    if not security_present:

        findings.append({

            "rule":
                "IEC62443-MONITORING",

            "status":
                "WARN",

            "message":
                (
                    "No IDS/IPS/SIEM nodes "
                    "detected in topology."
                )
        })

    else:

        findings.append({

            "rule":
                "IEC62443-MONITORING",

            "status":
                "PASS",

            "message":
                "Cybersecurity monitoring present."
        })

    # ========================================================
    # RULE 7 — MAINTENANCE SEGREGATION
    # ========================================================

    maintenance_nodes = [

        n for n in nodes
        if n["zone"] == "maintenance"
    ]

    if not maintenance_nodes:

        findings.append({

            "rule":
                "IEC62443-MAINTENANCE-SEGREGATION",

            "status":
                "WARN",

            "message":
                (
                    "No dedicated maintenance "
                    "zone detected."
                )
        })

    else:

        findings.append({

            "rule":
                "IEC62443-MAINTENANCE-SEGREGATION",

            "status":
                "PASS",

            "message":
                "Maintenance access segregated."
        })

    return findings


# ============================================================
# REPORTING
# ============================================================

def print_report(findings: list[dict]):

    print(
        "\n── Railway Cybersecurity Compliance Report ─────────────"
    )

    passed = sum(
        1 for f in findings
        if f["status"] == "PASS"
    )

    failed = sum(
        1 for f in findings
        if f["status"] == "FAIL"
    )

    warned = sum(
        1 for f in findings
        if f["status"] == "WARN"
    )

    for finding in findings:

        icon = {

            "PASS": "✓",
            "FAIL": "✗",
            "WARN": "⚠️"

        }.get(
            finding["status"],
            "?"
        )

        print(
            f"\n  {icon} "
            f"[{finding['status']}] "
            f"{finding['rule']}"
        )

        print(
            f"      "
            f"{finding['message']}"
        )

    print("\n──────────────────────────────────────────────────────")

    print(
        f"\n  Result:"
        f" {passed} passed,"
        f" {failed} failed,"
        f" {warned} warnings"
    )

    if failed == 0:

        print(
            "\n  ✓ Topology appears compliant "
            "with IEC 62443 / EN 50159 principles"
        )

    else:

        print(
            "\n  ✗ Critical cybersecurity "
            "violations detected"
        )

    print(
        "\n──────────────────────────────────────────────────────\n"
    )