"""
link_validator.py

FINAL HARDENED LINK VALIDATOR
IEC62443 + EN50159 + Railway OT + Kavach

DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- railway_rules.py = policy authority
- security_enrichment.py = computed-control authority

RESPONSIBILITIES
----------------
- validate modeled flows
- validate directional policy
- validate trust-boundary enforcement
- validate conduit security controls
- validate open-transmission protections
- validate deployable security controls

NOT RESPONSIBLE FOR
-------------------
- semantic inference
- conduit policy inference
- topology rendering
- risk scoring
- normalization logic
"""

from ontology import (
    transport_is_public_network,
    media_is_open_transmission,
    CONDUIT_SECURITY_PROFILES,
)

from railway_rules import (
    FLOW_RULES,
    REQUIRED_LOGICAL_LINKS,
    OPEN_TRANSMISSION_FLOWS,
    ALLOWED_SAFETY_FLOWS,
    get_flow_rule,
    get_trust_boundary,
    is_forbidden_zone_pair,
    is_monitoring_exempt,
    is_firewall_exempt,
    is_inspection_exempt,
)

from aliases import normalize_node_type

# ============================================================
# HELPERS
# ============================================================


def is_open_transmission(
    src_type: str,
    dst_type: str,
) -> bool:

    pair = (
        src_type,
        dst_type,
    )

    reverse = (
        dst_type,
        src_type,
    )

    return pair in OPEN_TRANSMISSION_FLOWS or reverse in OPEN_TRANSMISSION_FLOWS


def is_allowed_safety_flow(
    src_type: str,
    dst_type: str,
) -> bool:

    pair = (
        src_type,
        dst_type,
    )

    reverse = (
        dst_type,
        src_type,
    )

    return pair in ALLOWED_SAFETY_FLOWS or reverse in ALLOWED_SAFETY_FLOWS


# ============================================================
# MAIN VALIDATION
# ============================================================


def validate_links(
    topology: dict,
) -> list[str]:

    errors = set()

    print("\n══ LINK VALIDATION ══")

    print("-" * 50)

    connections = topology.get(
        "connections",
        [],
    )

    nodes = topology.get(
        "nodes",
        [],
    )

    # ========================================================
    # NODE LOOKUP
    # ========================================================

    node_lookup = {
        str(
            node.get(
                "id",
                "",
            )
        ).strip(): node
        for node in nodes
    }

    # ========================================================
    # EXISTING TYPE LINKS
    # ========================================================

    existing_type_links = set()

    for conn in connections:

        src_node = node_lookup.get(str(conn.get("source", "")).strip())

        tgt_node = node_lookup.get(str(conn.get("target", "")).strip())

        if not src_node or not tgt_node:

            continue

        existing_type_links.add(
            (
                src_node.get("type"),
                tgt_node.get("type"),
            )
        )

    # ========================================================
    # REQUIRED LOGICAL FLOWS
    # ========================================================

    for src_type, targets in REQUIRED_LOGICAL_LINKS.items():

        for tgt_type in targets:

            if (
                src_type,
                tgt_type,
            ) not in existing_type_links:

                msg = f"[MISSING REQUIRED LINK] " f"{src_type} -> {tgt_type}"

                print(msg)

                errors.add(msg)

    # ========================================================
    # CONNECTION VALIDATION
    # ========================================================

    for conn in connections:

        src_id = str(
            conn.get(
                "source",
                "",
            )
        ).strip()

        tgt_id = str(
            conn.get(
                "target",
                "",
            )
        ).strip()

        if not src_id or not tgt_id:

            msg = "[INVALID CONNECTION] missing source or target"

            print(msg)

            errors.add(msg)

            continue

        src_node = node_lookup.get(src_id)

        tgt_node = node_lookup.get(tgt_id)

        if not src_node or not tgt_node:

            msg = f"[MISSING NODE REFERENCE] " f"{src_id} -> {tgt_id}"

            print(msg)

            errors.add(msg)

            continue

        src_type = normalize_node_type(
            src_node.get(
                "type",
                "",
            )
        )

        tgt_type = normalize_node_type(
            tgt_node.get(
                "type",
                "",
            )
        )

        src_zone = str(
            src_node.get(
                "zone",
                "",
            )
        ).strip()

        tgt_zone = str(
            tgt_node.get(
                "zone",
                "",
            )
        ).strip()

        # ====================================================
        # FORBIDDEN ZONE LINKS
        # ====================================================

        if is_forbidden_zone_pair(
            src_zone,
            tgt_zone,
        ):

            msg = (
                f"[FORBIDDEN LINK] " f"{src_id}({src_type}) -> " f"{tgt_id}({tgt_type})"
            )

            print(msg)

            errors.add(msg)

            continue

        # ====================================================
        # FLOW RULE LOOKUP
        # ====================================================

        rule = get_flow_rule(
            src_type,
            tgt_type,
        )

        if not rule:

            msg = (
                f"[UNMODELED LINK] " f"{src_id}({src_type}) -> " f"{tgt_id}({tgt_type})"
            )

            print(msg)

            errors.add(msg)

            continue

        # ====================================================
        # TRUST BOUNDARY VALIDATION
        # ====================================================

        boundary = get_trust_boundary(
            src_zone,
            tgt_zone,
        )

        if boundary:

            if boundary.get(
                "firewall_required",
                False,
            ) and not conn.get(
                "firewall",
                False,
            ):

                conduit = conn.get(
                    "conduit_class",
                    "generic",
                )

                if not is_firewall_exempt(conduit):

                    msg = (
                        f"[TRUST BOUNDARY FIREWALL VIOLATION] " f"{src_id} -> {tgt_id}"
                    )

                    print(msg)

                    errors.add(msg)

            if boundary.get(
                "inspection_required",
                False,
            ) and not conn.get(
                "inspection",
                False,
            ):

                conduit = conn.get(
                    "conduit_class",
                    "generic",
                )

                if not is_inspection_exempt(conduit):

                    msg = (
                        f"[TRUST BOUNDARY INSPECTION VIOLATION] "
                        f"{src_id} -> {tgt_id}"
                    )

                    print(msg)

                    errors.add(msg)

        # ====================================================
        # DIRECTION VALIDATION
        # ====================================================

        reverse_rule = FLOW_RULES.get(
            (
                tgt_type,
                src_type,
            )
        )

        if reverse_rule:

            if reverse_rule.get("direction") == "unidirectional":

                if (
                    src_type,
                    tgt_type,
                ) not in FLOW_RULES:

                    msg = (
                        f"[REVERSE DIRECTION VIOLATION] "
                        f"{src_id}({src_type}) -> "
                        f"{tgt_id}({tgt_type})"
                    )

                    print(msg)

                    errors.add(msg)

                    continue

        # ====================================================
        # FLOW POLICY REQUIREMENTS
        # ====================================================

        control_checks = [
            (
                "requires_encryption",
                "encrypted",
                "requires encryption",
            ),
            (
                "requires_integrity",
                "integrity_protected",
                "requires integrity protection",
            ),
            (
                "requires_replay_protection",
                "replay_protected",
                "requires replay protection",
            ),
            (
                "requires_mfa",
                "mfa",
                "requires MFA",
            ),
            (
                "requires_authentication",
                "authenticated",
                "requires authentication",
            ),
            (
                "requires_monitoring",
                "monitoring",
                "requires monitoring",
            ),
            (
                "requires_latency_monitoring",
                "latency_monitoring",
                "requires latency monitoring",
            ),
            (
                "requires_firewall",
                "firewall",
                "requires firewall segmentation",
            ),
            (
                "requires_inspection",
                "inspection",
                "requires conduit inspection",
            ),
        ]

        for (
            required_key,
            capability_key,
            message,
        ) in control_checks:

            if not rule.get(
                required_key,
                False,
            ):

                continue

            if required_key == "requires_monitoring":

                if is_monitoring_exempt(src_type) or is_monitoring_exempt(tgt_type):

                    continue

            if conn.get(
                capability_key,
                False,
            ):

                continue

            msg = (
                f"[POLICY VIOLATION] "
                f"{src_id}({src_type}) -> "
                f"{tgt_id}({tgt_type}) "
                f"{message}"
            )

            print(msg)

            errors.add(msg)

        # ====================================================
        # CONDUIT POLICY VALIDATION
        # ====================================================

        conduit_class = conn.get(
            "conduit_class",
            "generic",
        )

        from ontology import VALID_CONDUITS

        if conduit_class not in VALID_CONDUITS:

            msg = f"[UNKNOWN CONDUIT CLASS] " f"{src_id} -> {tgt_id} -> {conduit_class}"

            print(msg)

            errors.add(msg)

            continue

        conduit_policy = CONDUIT_SECURITY_PROFILES.get(
            conduit_class,
            {},
        )

        conduit_checks = [
            (
                "requires_monitoring",
                "monitoring",
            ),
            (
                "requires_mfa",
                "mfa",
            ),
            (
                "requires_encryption",
                "encrypted",
            ),
            (
                "requires_integrity",
                "integrity_protected",
            ),
            (
                "requires_authentication",
                "authenticated",
            ),
            (
                "requires_inspection",
                "inspection",
            ),
            (
                "requires_firewall",
                "firewall",
            ),
            (
                "requires_replay_protection",
                "replay_protected",
            ),
            (
                "requires_latency_monitoring",
                "latency_monitoring",
            ),
        ]

        for (
            policy_key,
            conn_key,
        ) in conduit_checks:

            if not conduit_policy.get(
                policy_key,
                False,
            ):
                continue

            if conn.get(
                conn_key,
                False,
            ):
                continue

            msg = (
                f"[CONDUIT POLICY VIOLATION] "
                f"{src_id}({src_type}) -> "
                f"{tgt_id}({tgt_type}) "
                f"missing {policy_key}"
            )

            print(msg)

            errors.add(msg)

        # ====================================================
        # OPEN TRANSMISSION VALIDATION
        # ====================================================

        transport = conn.get(
            "transport",
            "",
        )

        media = conn.get(
            "media",
            "",
        )

        if (
            transport_is_public_network(transport)
            or media_is_open_transmission(media)
            or is_open_transmission(
                src_type,
                tgt_type,
            )
        ):

            if conn.get(
                "passive_telegram",
                False,
            ):

                continue

            open_checks = [
                (
                    "integrity_protected",
                    "requires integrity protection",
                ),
                (
                    "replay_protected",
                    "requires replay protection",
                ),
            ]

            for (
                capability_key,
                message,
            ) in open_checks:

                if conn.get(
                    capability_key,
                    False,
                ):

                    continue

                msg = (
                    f"[OPEN TRANSMISSION VIOLATION] "
                    f"{src_id}({src_type}) -> "
                    f"{tgt_id}({tgt_type}) "
                    f"{message}"
                )

                print(msg)

                errors.add(msg)

        # ====================================================
        # SAFETY FLOW VALIDATION
        # ====================================================

        if conn.get(
            "safety_related",
            False,
        ):

            if not conn.get(
                "safety_flow",
                False,
            ):

                msg = (
                    f"[SAFETY FLOW VIOLATION] "
                    f"{src_id}({src_type}) -> "
                    f"{tgt_id}({tgt_type}) "
                    f"missing safety_flow classification"
                )

                print(msg)

                errors.add(msg)

            if not is_allowed_safety_flow(
                src_type,
                tgt_type,
            ):

                msg = (
                    f"[UNAUTHORIZED SAFETY FLOW] "
                    f"{src_id}({src_type}) -> "
                    f"{tgt_id}({tgt_type})"
                )

                print(msg)

                errors.add(msg)

    # ========================================================
    # SUMMARY
    # ========================================================

    print(f"\nLINK VALIDATION ERRORS: " f"{len(errors)}")

    return sorted(errors)
