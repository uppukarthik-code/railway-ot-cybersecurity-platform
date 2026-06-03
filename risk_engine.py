"""
risk_engine.py

FINAL CANONICAL RISK ENGINE
IEC62443 + EN50159 + Railway OT + Kavach

DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- railway_rules.py = governance authority
- security_enrichment.py = deployed-control authority
- validator.py = enforcement authority
- risk_engine.py = residual risk reasoning only

RESPONSIBILITIES
----------------
- residual cybersecurity risk analysis
- trust-boundary risk analysis
- systemic OT exposure analysis
- conduit/control deficiency analysis

DOES NOT
---------
- duplicate ontology semantics
- duplicate classifier logic
- duplicate policy logic
- infer controls
- infer protocols
- render
"""

from ontology import (
    ASSET_ONTOLOGY,
    ZONE_REQUIREMENTS,
    SECURITY_LEVEL_ORDER,
    UNKNOWN_PROTOCOL,
    UNKNOWN_NODE,
    UNKNOWN_ZONE,
    get_zone_trust_domain,
)

# ============================================================
# SEVERITY WEIGHTS
# ============================================================

SEVERITY_WEIGHTS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

# ============================================================
# HELPERS
# ============================================================


def add_finding(
    findings,
    severity,
    finding_type,
    message,
    recommendation="",
    affected_assets=None,
):

    findings.append(
        {
            "severity": severity,
            "type": finding_type,
            "message": message,
            "recommendation": recommendation,
            "affected_assets": affected_assets or [],
        }
    )


def sl_value(sl: str) -> int:

    return SECURITY_LEVEL_ORDER.get(
        sl,
        0,
    )


def risk_exists(
    seen_risks,
    risk_key,
):

    return risk_key in seen_risks


def register_risk(
    seen_risks,
    risk_key,
):

    seen_risks.add(risk_key)


# ============================================================
# MAIN ANALYSIS
# ============================================================


def analyze_risk(
    topology,
):

    findings = []

    seen_risks = set()

    nodes = topology.get(
        "nodes",
        [],
    )

    connections = topology.get(
        "connections",
        [],
    )

    conduits = topology.get(
        "conduits",
        [],
    )

    # ========================================================
    # NODE LOOKUP
    # ========================================================

    node_index = {n["id"]: n for n in nodes}

    # ========================================================
    # RULE 1 — REQUIRED ENCRYPTION MISSING
    # ========================================================

    for conn in connections:

        if conn.get(
            "requires_encrypted",
            False,
        ) and not conn.get(
            "encrypted",
            False,
        ):

            risk_key = (
                "REQUIRED_ENCRYPTION_MISSING",
                conn["source"],
                conn["target"],
            )

            if risk_exists(
                seen_risks,
                risk_key,
            ):

                continue

            register_risk(
                seen_risks,
                risk_key,
            )

            add_finding(
                findings,
                "CRITICAL",
                "REQUIRED_ENCRYPTION_MISSING",
                (
                    f"Connection "
                    f"{conn['source']} -> "
                    f"{conn['target']} "
                    f"requires encryption "
                    f"but is not encrypted."
                ),
                ("Deploy authenticated " "and encrypted communication."),
                [
                    conn["source"],
                    conn["target"],
                ],
            )

    # ========================================================
    # RULE 2 — REQUIRED INTEGRITY MISSING
    # ========================================================

    for conn in connections:

        if conn.get(
            "requires_integrity_protection",
            False,
        ) and not conn.get(
            "integrity_protection",
            False,
        ):

            if conn.get(
                "passive_telegram",
                False,
            ):

                continue

            risk_key = (
                "INTEGRITY_PROTECTION_MISSING",
                conn["source"],
                conn["target"],
            )

            if risk_exists(
                seen_risks,
                risk_key,
            ):

                continue

            register_risk(
                seen_risks,
                risk_key,
            )

            severity = (
                "CRITICAL"
                if conn.get(
                    "safety_flow",
                    False,
                )
                else "HIGH"
            )

            add_finding(
                findings,
                severity,
                "INTEGRITY_PROTECTION_MISSING",
                (
                    f"Connection "
                    f"{conn['source']} -> "
                    f"{conn['target']} "
                    f"requires integrity protection."
                ),
                ("Deploy cryptographic " "integrity validation mechanisms."),
                [
                    conn["source"],
                    conn["target"],
                ],
            )

    # ========================================================
    # RULE 3 — REQUIRED REPLAY PROTECTION MISSING
    # ========================================================

    for conn in connections:

        if conn.get(
            "requires_replay_protection",
            False,
        ) and not conn.get(
            "replay_protection",
            False,
        ):

            if conn.get(
                "passive_telegram",
                False,
            ):

                continue

            risk_key = (
                "REPLAY_PROTECTION_MISSING",
                conn["source"],
                conn["target"],
            )

            if risk_exists(
                seen_risks,
                risk_key,
            ):

                continue

            register_risk(
                seen_risks,
                risk_key,
            )

            severity = (
                "CRITICAL"
                if conn.get(
                    "safety_flow",
                    False,
                )
                else "HIGH"
            )

            add_finding(
                findings,
                severity,
                "REPLAY_PROTECTION_MISSING",
                (
                    f"Connection "
                    f"{conn['source']} -> "
                    f"{conn['target']} "
                    f"requires replay protection."
                ),
                ("Implement anti-replay " "sequence validation."),
                [
                    conn["source"],
                    conn["target"],
                ],
            )

    # ========================================================
    # RULE 4 — CROSS TRUST SAFETY FLOW
    # ========================================================

    for conn in connections:

        if not conn.get(
            "safety_flow",
            False,
        ):

            continue

        if not conn.get(
            "cross_trust_domain",
            False,
        ):

            continue

        risk_key = (
            "LOW_TRUST_SAFETY_FLOW",
            conn["source"],
            conn["target"],
        )

        if risk_exists(
            seen_risks,
            risk_key,
        ):

            continue

        register_risk(
            seen_risks,
            risk_key,
        )

        add_finding(
            findings,
            "HIGH",
            "LOW_TRUST_SAFETY_FLOW",
            (
                f"Safety-critical flow "
                f"{conn['source']} -> "
                f"{conn['target']} "
                f"crosses trust boundaries."
            ),
            ("Restrict safety communication " "to trusted OT conduits."),
            [
                conn["source"],
                conn["target"],
            ],
        )

    # ========================================================
    # RULE 5 — OPEN SAFETY FLOW WITHOUT INTEGRITY
    # ========================================================

    for conn in connections:

        if not conn.get(
            "safety_flow",
            False,
        ):

            continue

        if not conn.get(
            "open_transmission",
            False,
        ):

            continue

        if conn.get(
            "passive_telegram",
            False,
        ):

            continue

        if conn.get(
            "integrity_protection",
            False,
        ):

            continue

        risk_key = (
            "OPEN_SAFETY_NO_INTEGRITY",
            conn["source"],
            conn["target"],
        )

        if risk_exists(
            seen_risks,
            risk_key,
        ):

            continue

        register_risk(
            seen_risks,
            risk_key,
        )

        add_finding(
            findings,
            "CRITICAL",
            "OPEN_SAFETY_NO_INTEGRITY",
            (
                f"Open transmission safety flow "
                f"{conn['source']} -> "
                f"{conn['target']} "
                f"lacks integrity protection."
            ),
            ("Apply EN50159 integrity " "protection mechanisms."),
            [
                conn["source"],
                conn["target"],
            ],
        )

    # ========================================================
    # RULE 6 — UNKNOWN PROTOCOL
    # ========================================================

    for conn in connections:

        if (
            conn.get(
                "protocol",
                UNKNOWN_PROTOCOL,
            )
            == UNKNOWN_PROTOCOL
        ):

            risk_key = (
                "UNKNOWN_PROTOCOL",
                conn["source"],
                conn["target"],
            )

            if risk_exists(
                seen_risks,
                risk_key,
            ):

                continue

            register_risk(
                seen_risks,
                risk_key,
            )

            add_finding(
                findings,
                "HIGH",
                "UNKNOWN_PROTOCOL",
                (
                    f"Connection "
                    f"{conn['source']} -> "
                    f"{conn['target']} "
                    f"uses unknown protocol."
                ),
                ("Classify and validate " "protocol semantics."),
                [
                    conn["source"],
                    conn["target"],
                ],
            )

    # ========================================================
    # RULE 7 — UNKNOWN NODE TYPE
    # ========================================================

    for node in nodes:

        if (
            node.get(
                "type",
                UNKNOWN_NODE,
            )
            == UNKNOWN_NODE
        ):

            risk_key = (
                "UNKNOWN_NODE_TYPE",
                node["id"],
            )

            if risk_exists(
                seen_risks,
                risk_key,
            ):

                continue

            register_risk(
                seen_risks,
                risk_key,
            )

            add_finding(
                findings,
                "HIGH",
                "UNKNOWN_NODE_TYPE",
                (f"Node " f"{node['label']} " f"has unknown semantic type."),
                ("Classify node into " "canonical ontology."),
                [
                    node["id"],
                ],
            )

    # ========================================================
    # RULE 8 — UNKNOWN ZONE
    # ========================================================

    for node in nodes:

        if (
            node.get(
                "zone",
                UNKNOWN_ZONE,
            )
            == UNKNOWN_ZONE
        ):

            risk_key = (
                "UNKNOWN_ZONE",
                node["id"],
            )

            if risk_exists(
                seen_risks,
                risk_key,
            ):

                continue

            register_risk(
                seen_risks,
                risk_key,
            )

            add_finding(
                findings,
                "HIGH",
                "UNKNOWN_ZONE",
                (f"Node " f"{node['label']} " f"has unknown zone placement."),
                ("Assign node into " "approved OT security zone."),
                [
                    node["id"],
                ],
            )

    # ========================================================
    # RULE 9 — ENGINEERING WORKSTATION EXPOSURE
    # ========================================================

    for node in nodes:

        if node.get("type") != "engineering_workstation":

            continue

        zone = node.get(
            "zone",
            "",
        )

        asset_meta = ASSET_ONTOLOGY.get(
            node.get("type"),
            {},
        )

        allowed_zones = set(
            asset_meta.get(
                "allowed_zones",
                [],
            )
        )

        if allowed_zones and zone not in allowed_zones:

            risk_key = (
                "ENGINEERING_WS_ZONE",
                node["id"],
            )

            if not risk_exists(
                seen_risks,
                risk_key,
            ):

                register_risk(
                    seen_risks,
                    risk_key,
                )

                add_finding(
                    findings,
                    "HIGH",
                    "ENGINEERING_WS_ZONE",
                    (f"{node['label']} " f"is outside approved zones."),
                    ("Place engineering systems " "inside isolated maintenance zones."),
                    [node["id"]],
                )

        if node.get(
            "internet_exposed",
            False,
        ):

            risk_key = (
                "ENGINEERING_WS_EXPOSED",
                node["id"],
            )

            if not risk_exists(
                seen_risks,
                risk_key,
            ):

                register_risk(
                    seen_risks,
                    risk_key,
                )

                add_finding(
                    findings,
                    "CRITICAL",
                    "ENGINEERING_WS_EXPOSED",
                    (f"{node['label']} " f"is internet exposed."),
                    ("Remove internet exposure " "from engineering assets."),
                    [node["id"]],
                )

    # ========================================================
    # RULE 10 — SECURITY LEVEL DEFICIENCY
    # ========================================================

    for node in nodes:

        zone = node.get(
            "zone",
            "",
        )

        expected_sl = ZONE_REQUIREMENTS.get(
            zone,
            {},
        ).get(
            "security_level",
            "SL1",
        )

        actual_sl = node.get(
            "security_level",
            expected_sl,
        )

        if sl_value(actual_sl) < sl_value(expected_sl):

            risk_key = (
                "SECURITY_LEVEL_MISMATCH",
                node["id"],
            )

            if risk_exists(
                seen_risks,
                risk_key,
            ):

                continue

            register_risk(
                seen_risks,
                risk_key,
            )

            add_finding(
                findings,
                "MEDIUM",
                "SECURITY_LEVEL_MISMATCH",
                (
                    f"{node['label']} "
                    f"uses {actual_sl} "
                    f"inside zone {zone} "
                    f"requiring {expected_sl}."
                ),
                ("Increase hardening to " "required IEC62443 target SL."),
                [node["id"]],
            )

    # ========================================================
    # RULE 11 — SAFETY TO LOW TRUST EXPOSURE
    # ========================================================

    for conn in connections:

        src = node_index.get(conn.get("source"))

        tgt = node_index.get(conn.get("target"))

        if not src or not tgt:

            continue

        src_safety = src.get(
            "safety_critical",
            False,
        )

        tgt_safety = tgt.get(
            "safety_critical",
            False,
        )

        src_trust = get_zone_trust_domain(
            src.get(
                "zone",
                "",
            )
        )

        tgt_trust = get_zone_trust_domain(
            tgt.get(
                "zone",
                "",
            )
        )

        if src_safety and tgt_trust != "railway_trusted":

            risk_key = (
                "SAFETY_TO_LOW_TRUST",
                src["id"],
                tgt["id"],
            )

            if not risk_exists(
                seen_risks,
                risk_key,
            ):

                register_risk(
                    seen_risks,
                    risk_key,
                )

                add_finding(
                    findings,
                    "CRITICAL",
                    "SAFETY_TO_LOW_TRUST",
                    (f"{src['label']} " f"is reachable from " f"low-trust domain."),
                    ("Enforce IDMZ segmentation " "and monitored conduits."),
                    [
                        src["id"],
                        tgt["id"],
                    ],
                )

        if tgt_safety and src_trust != "railway_trusted":

            risk_key = (
                "SAFETY_TO_LOW_TRUST",
                tgt["id"],
                src["id"],
            )

            if not risk_exists(
                seen_risks,
                risk_key,
            ):

                register_risk(
                    seen_risks,
                    risk_key,
                )

                add_finding(
                    findings,
                    "CRITICAL",
                    "SAFETY_TO_LOW_TRUST",
                    (f"{tgt['label']} " f"is reachable from " f"low-trust domain."),
                    ("Enforce IDMZ segmentation " "and monitored conduits."),
                    [
                        src["id"],
                        tgt["id"],
                    ],
                )

    # ========================================================
    # RULE 12 — SIL ASSET IN LOW TRUST DOMAIN
    # ========================================================

    for node in nodes:

        if not node.get(
            "safety_critical",
            False,
        ):

            continue

        trust_domain = get_zone_trust_domain(
            node.get(
                "zone",
                "",
            )
        )

        if trust_domain != "railway_trusted":

            risk_key = (
                "SIL_LOW_TRUST_PLACEMENT",
                node["id"],
            )

            if risk_exists(
                seen_risks,
                risk_key,
            ):

                continue

            register_risk(
                seen_risks,
                risk_key,
            )

            add_finding(
                findings,
                "CRITICAL",
                "SIL_LOW_TRUST_PLACEMENT",
                (
                    f"{node['label']} "
                    f"is safety critical but "
                    f"placed in low-trust domain."
                ),
                ("Move safety-critical assets " "into trusted OT domains."),
                [node["id"]],
            )

    # ========================================================
    # RULE 13 — CONDUIT TRUST BOUNDARY
    # ========================================================

    for conduit in conduits:

        if not conduit.get(
            "trust_boundary",
            False,
        ):

            continue

        if not conduit.get(
            "engineering_access",
            False,
        ):

            continue

        risk_key = (
            "ENGINEERING_TRUST_BOUNDARY",
            conduit["id"],
        )

        if risk_exists(
            seen_risks,
            risk_key,
        ):

            continue

        register_risk(
            seen_risks,
            risk_key,
        )

        add_finding(
            findings,
            "HIGH",
            "ENGINEERING_TRUST_BOUNDARY",
            (f"Engineering conduit " f"{conduit['id']} " f"crosses trust boundaries."),
            ("Deploy monitored jump-host " "and MFA protected access."),
            [
                conduit["source"],
                conduit["target"],
            ],
        )

    # ========================================================
    # SORT FINDINGS
    # ========================================================

    findings.sort(
        key=lambda x: (
            -SEVERITY_WEIGHTS.get(
                x["severity"],
                0,
            ),
            x["type"],
        )
    )

    # ========================================================
    # REPORTING
    # ========================================================

    if findings:

        print(
            "\n── Railway Cybersecurity Risk Analysis " "─────────────────────────────"
        )

        for finding in findings:

            print(f"\n[{finding['severity']}] " f"{finding['type']}")

            print(f"  {finding['message']}")

            if finding.get(
                "recommendation",
            ):

                print(f"  Recommendation: " f"{finding['recommendation']}")

        print("\n────────────────────────────────────────────────────")

    else:

        print("\n[OK] No major cybersecurity risks detected.")

    return findings
