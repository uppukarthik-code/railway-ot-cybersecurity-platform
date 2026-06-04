"""
validator.py
FINAL CANONICAL VALIDATOR
IEC62443 + EN50159 + EN50126 + Railway OT
DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- railway_rules.py = governance authority
- security_enrichment.py = deployed-control authority
Validator responsibilities ONLY:
- topology validation
- policy enforcement
- compatibility verification
- trust validation
- safety-domain validation
NO:
- ontology duplication
- rendering logic
- classification logic
- risk analysis
- semantic inference
"""

from ontology import (
    ASSET_ONTOLOGY,
    STACK_COMPATIBILITY,
    RADIO_ATTACK_SURFACE_TYPES,
    get_asset_ontology,
)
from railway_rules import (
    get_flow_rule,
    get_trust_boundary,
    is_forbidden_zone_pair,
    is_forbidden_flow,
)
from aliases import normalize_node_type


# ============================================================
# RESULT BUILDER
# ============================================================
def build_result(
    rule,
    passed,
    fail_message,
    pass_message,
    severity="MEDIUM",
    recommendation="",
):
    return {
        "rule": rule,
        "status": ("PASS" if passed else "FAIL"),
        "severity": ("INFO" if passed else severity),
        "message": (pass_message if passed else fail_message),
        "recommendation": recommendation,
    }


# ============================================================
# MAIN VALIDATION
# ============================================================
def validate(
    topology,
):
    findings = []
    nodes = topology.get(
        "nodes",
        [],
    )
    connections = topology.get(
        "connections",
        [],
    )
    node_lookup = {n["id"]: n for n in nodes}
    # ========================================================
    # VALID NODE TYPES
    # ========================================================
    invalid_types = []
    for node in nodes:
        node_type = node.get(
            "type",
            "",
        )
        if node_type not in ASSET_ONTOLOGY:
            invalid_types.append(f"{node['id']} ({node_type})")
    findings.append(
        build_result(
            rule="VALID-NODE-TYPES",
            passed=(len(invalid_types) == 0),
            fail_message=("Invalid node types: " + "; ".join(invalid_types)),
            pass_message="All node types valid.",
            severity="HIGH",
            recommendation="Normalize node types.",
        )
    )
    # ========================================================
    # PURDUE VALIDATION
    # ========================================================
    purdue_violations = []
    for node in nodes:
        node_type = node.get("type")
        actual = node.get("purdue_level")
        asset_meta = get_asset_ontology(
            node_type,
        )
        allowed = set(
            asset_meta.get(
                "allowed_purdue",
                [],
            )
        )
        if allowed and actual not in allowed:
            purdue_violations.append(
                f"{node['id']} " f"({actual} not in {sorted(allowed)})"
            )
    findings.append(
        build_result(
            rule="PURDUE-PLACEMENT",
            passed=(len(purdue_violations) == 0),
            fail_message=("Invalid Purdue placement: " + "; ".join(purdue_violations)),
            pass_message="Purdue placement valid.",
            severity="HIGH",
            recommendation="Align assets to Purdue levels.",
        )
    )
    # ========================================================
    # ZONE VALIDATION
    # ========================================================
    zone_violations = []
    for node in nodes:
        node_type = node.get("type")
        zone = node.get("zone")
        asset_meta = get_asset_ontology(
            node_type,
        )
        allowed = set(
            asset_meta.get(
                "allowed_zones",
                [],
            )
        )
        if allowed and zone not in allowed:
            zone_violations.append(
                f"{node['id']} " f"({zone} not in {sorted(allowed)})"
            )
    findings.append(
        build_result(
            rule="ZONE-PLACEMENT",
            passed=(len(zone_violations) == 0),
            fail_message=("Invalid zoning: " + "; ".join(zone_violations)),
            pass_message="Zone placement valid.",
            severity="CRITICAL",
            recommendation="Review IEC62443 zoning.",
        )
    )
    # ========================================================
    # UNAUTHORIZED FLOWS
    # ========================================================
    unauthorized_flows = []
    reverse_direction_violations = []
    for conn in connections:
        src = node_lookup.get(conn["source"])
        dst = node_lookup.get(conn["target"])
        if not src or not dst:
            continue
        src_type = src.get("type")
        dst_type = dst.get("type")
        rule = get_flow_rule(
            src_type,
            dst_type,
        )
        if rule:
            continue
        reverse_rule = get_flow_rule(
            dst_type,
            src_type,
        )
        if reverse_rule:
            reverse_direction_violations.append(
                f"{conn['source']} -> " f"{conn['target']}"
            )
        else:
            unauthorized_flows.append(f"{conn['source']} -> " f"{conn['target']}")
    findings.append(
        build_result(
            rule="UNAUTHORIZED-FLOWS",
            passed=(len(unauthorized_flows) == 0),
            fail_message=("Unauthorized flows: " + "; ".join(unauthorized_flows)),
            pass_message="All flows authorized.",
            severity="CRITICAL",
            recommendation="Remove unauthorized communications.",
        )
    )
    findings.append(
        build_result(
            rule="REVERSE-DIRECTION-VIOLATIONS",
            passed=(len(reverse_direction_violations) == 0),
            fail_message=(
                "Reverse-direction violations: "
                + "; ".join(reverse_direction_violations)
            ),
            pass_message="Flow directions valid.",
            severity="HIGH",
            recommendation="Correct directional policy violations.",
        )
    )
    # ========================================================
    # FORBIDDEN CONNECTIONS
    # ========================================================
    forbidden_violations = []
    for conn in connections:
        src = node_lookup.get(conn["source"])
        dst = node_lookup.get(conn["target"])
        if not src or not dst:
            continue
        if is_forbidden_zone_pair(
            src.get("zone"),
            dst.get("zone"),
        ) or is_forbidden_flow(
            normalize_node_type(src.get("type")),
            normalize_node_type(dst.get("type")),
        ):
            forbidden_violations.append(f"{conn['source']} -> " f"{conn['target']}")
    findings.append(
        build_result(
            rule="FORBIDDEN-CONNECTIONS",
            passed=(len(forbidden_violations) == 0),
            fail_message=("Forbidden connections: " + "; ".join(forbidden_violations)),
            pass_message="No forbidden connections.",
            severity="CRITICAL",
            recommendation="Remove prohibited conduits.",
        )
    )
    # ========================================================
    # STACK COMPATIBILITY
    # ========================================================
    compatibility_violations = []
    for conn in connections:
        protocol = conn.get("protocol")
        transport = conn.get("transport")
        media = conn.get("media")
        bearer = conn.get("bearer")
        stack = STACK_COMPATIBILITY.get(
            protocol,
            {},
        )
        allowed_transport = set(
            stack.get(
                "transport",
                [],
            )
        )
        allowed_media = set(
            stack.get(
                "media",
                [],
            )
        )
        allowed_bearer = set(
            stack.get(
                "bearer",
                [],
            )
        )
        if allowed_transport and transport not in allowed_transport:
            compatibility_violations.append(
                f"{conn['source']} -> "
                f"{conn['target']} "
                f"({protocol} incompatible "
                f"with transport={transport})"
            )
        if allowed_media and media not in allowed_media:
            compatibility_violations.append(
                f"{conn['source']} -> "
                f"{conn['target']} "
                f"({protocol} incompatible "
                f"with media={media})"
            )
        if allowed_bearer and bearer not in allowed_bearer:
            compatibility_violations.append(
                f"{conn['source']} -> "
                f"{conn['target']} "
                f"({protocol} incompatible "
                f"with bearer={bearer})"
            )
    findings.append(
        build_result(
            rule="STACK-COMPATIBILITY",
            passed=(len(compatibility_violations) == 0),
            fail_message=(
                "Compatibility violations: " + "; ".join(compatibility_violations)
            ),
            pass_message="Stack compatibility valid.",
            severity="HIGH",
            recommendation="Align protocol stack.",
        )
    )
    # ========================================================
    # REQUIRED CONTROL VALIDATION
    # ========================================================
    conduit_violations = []
    for conn in connections:
        required_controls = {
            "requires_encrypted": "encrypted",
            "requires_authentication": "authentication",
            "requires_integrity_protection": "integrity_protection",
            "requires_replay_protection": "replay_protection",
            "requires_monitoring": "monitoring",
            "requires_firewall": "firewall",
            "requires_inspection": "inspection",
            "requires_latency_monitoring": "latency_monitoring",
            "requires_mfa": "mfa",
        }
        for required_field, deployed_field in required_controls.items():
            if not conn.get(
                required_field,
                False,
            ):
                continue
            if not conn.get(
                deployed_field,
                False,
            ):
                conduit_violations.append(
                    f"{conn['source']} -> "
                    f"{conn['target']} "
                    f"(missing {deployed_field})"
                )
    findings.append(
        build_result(
            rule="CONDUIT-PROFILE-VALIDATION",
            passed=(len(conduit_violations) == 0),
            fail_message=(
                "Conduit profile violations: " + "; ".join(conduit_violations)
            ),
            pass_message="Conduit profiles satisfied.",
            severity="CRITICAL",
            recommendation="Apply conduit security controls.",
        )
    )
    # ========================================================
    # TRUST BOUNDARY VALIDATION
    # ========================================================
    trust_violations = []
    for conn in connections:
        src = node_lookup.get(conn["source"])
        dst = node_lookup.get(conn["target"])
        if not src or not dst:
            continue
        boundary = get_trust_boundary(
            src.get("zone"),
            dst.get("zone"),
        )
        if not boundary:
            continue
        required_controls = boundary.get(
            "required_controls",
            set(),
        )
        for control in required_controls:
            if not conn.get(
                control,
                False,
            ):
                trust_violations.append(
                    f"{conn['source']} -> " f"{conn['target']} " f"(missing {control})"
                )
    findings.append(
        build_result(
            rule="TRUST-BOUNDARY-PROTECTION",
            passed=(len(trust_violations) == 0),
            fail_message=("Trust boundary violations: " + "; ".join(trust_violations)),
            pass_message="Trust boundaries protected.",
            severity="HIGH",
            recommendation="Protect trust-boundary conduits.",
        )
    )
    # ========================================================
    # SIL4 LOW TRUST EXPOSURE
    # ========================================================
    sil_violations = []
    for node in nodes:
        # Safety placement is gated on the asset-level safety_critical
        # flag (classifier-enriched from ASSET_ONTOLOGY) — the same
        # authority the risk engine uses (Rule 12). The prior gate read
        # node["functional_safety_level"], a field never populated
        # anywhere in the pipeline (assessment finding E-01), so the
        # gate never fired and the rule was a vacuous PASS. SIL is only
        # modelled at zone granularity in the ontology, and every SIL4
        # zone (interlocking, onboard) is itself trusted — so a literal
        # zone-SIL4 gate would be structurally unsatisfiable; the asset
        # safety_critical flag travels with the asset and keeps the rule
        # live (it fires for a safety asset relocated into a low-trust
        # zone). Trust uses the ontology trust authority via the
        # enriched is_trusted_zone flag; the prior
        # get_zone_trust_domain(zone) != "railway_trusted" predicate was
        # degenerate / always true — see assessment finding D-01.
        if node.get(
            "safety_critical",
            False,
        ) and not node.get(
            "is_trusted_zone",
            False,
        ):
            sil_violations.append(node["id"])
    findings.append(
        build_result(
            rule="SIL4-LOW-TRUST-EXPOSURE",
            passed=(len(sil_violations) == 0),
            fail_message=(
                "SIL4 assets in low-trust zones: " + "; ".join(sil_violations)
            ),
            pass_message="SIL4 trust placement valid.",
            severity="CRITICAL",
            recommendation="Move SIL4 assets into trusted OT zones.",
        )
    )
    # ========================================================
    # RADIO VALIDATION
    # ========================================================
    radio_violations = []
    for conn in connections:
        src = node_lookup.get(conn["source"])
        dst = node_lookup.get(conn["target"])
        if not src or not dst:
            continue
        src_type = src.get("type")
        dst_type = dst.get("type")
        radio_endpoint = (
            src_type in RADIO_ATTACK_SURFACE_TYPES
            or dst_type in RADIO_ATTACK_SURFACE_TYPES
        )
        if not radio_endpoint:
            continue
        if not conn.get(
            "open_transmission",
            False,
        ):
            continue
        # Passive safety-coded telegrams (e.g. the balise air-gap) are
        # exempt from cryptographic encryption and replay protection per
        # EN 50159 — protection is the passive safety-coded telegram, and
        # freshness derives from location coding / odometry, not a crypto
        # replay control. Integrity (the safety code) is still required.
        # This mirrors the passive_telegram exemption already honoured by
        # validators/validate_links.py and defined in railway_rules,
        # resolving the cross-validator enforcement inconsistency
        # (assessment finding E-01). No requirement is removed for any
        # non-passive open-RF flow.
        passive_telegram = conn.get(
            "passive_telegram",
            False,
        )
        if not passive_telegram and not conn.get(
            "encrypted",
            False,
        ):
            radio_violations.append(
                f"{conn['source']} -> " f"{conn['target']} " f"(missing encryption)"
            )
        if not conn.get(
            "integrity_protection",
            False,
        ):
            radio_violations.append(
                f"{conn['source']} -> "
                f"{conn['target']} "
                f"(missing integrity protection)"
            )
        if not passive_telegram and not conn.get(
            "replay_protection",
            False,
        ):
            radio_violations.append(
                f"{conn['source']} -> "
                f"{conn['target']} "
                f"(missing replay protection)"
            )
    findings.append(
        build_result(
            rule="RADIO-PROTECTION",
            passed=(len(radio_violations) == 0),
            fail_message=("Unprotected RF conduits: " + "; ".join(radio_violations)),
            pass_message="Radio protection valid.",
            severity="HIGH",
            recommendation="Apply EN50159 protections.",
        )
    )
    # ========================================================
    # SAFETY DOMAIN VALIDATION
    # ========================================================
    safety_domain_violations = []
    for conn in connections:
        if not conn.get(
            "safety_flow",
            False,
        ):
            continue
        src = node_lookup.get(conn["source"])
        dst = node_lookup.get(conn["target"])
        if not src or not dst:
            continue
        src_domain = src.get(
            "safety_domain",
            "non_vital",
        )
        dst_domain = dst.get(
            "safety_domain",
            "non_vital",
        )
        if (
            src_domain == "non_vital"
            and dst_domain == "vital"
            and not conn.get(
                "firewall",
                False,
            )
        ):
            safety_domain_violations.append(f"{conn['source']} -> " f"{conn['target']}")
    findings.append(
        build_result(
            rule="SAFETY-DOMAIN-BOUNDARY",
            passed=(len(safety_domain_violations) == 0),
            fail_message=(
                "Safety-domain violations: " + "; ".join(safety_domain_violations)
            ),
            pass_message="Safety-domain boundaries protected.",
            severity="CRITICAL",
            recommendation="Isolate vital safety domains.",
        )
    )
    return findings


# ============================================================
# PRINT REPORT
# ============================================================
def print_report(
    findings,
):
    print("\n══ Railway Cybersecurity Validation ══")
    for finding in findings:
        status = finding.get(
            "status",
            "UNKNOWN",
        )
        severity = finding.get(
            "severity",
            "INFO",
        )
        rule = finding.get(
            "rule",
            "UNKNOWN",
        )
        message = finding.get(
            "message",
            "",
        )
        icon = "✓" if status == "PASS" else "✗"
        print(f"\n{icon} " f"[{severity}] " f"{rule}")
        print(f"  {message}")
        recommendation = finding.get(
            "recommendation",
            "",
        )
        if recommendation:
            print(f"  Recommendation: " f"{recommendation}")
