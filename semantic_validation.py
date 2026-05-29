"""
semantic_kernel_validator.py

FINAL HARDENED SEMANTIC KERNEL VALIDATOR

IEC62443 + EN50126 + EN50129 + EN50159 + Kavach

RESPONSIBILITIES
----------------
- ontology integrity validation
- normalization drift detection
- semantic kernel consistency checks
- canonical governance validation
- flow rule integrity validation
- detached-domain governance validation

NOT RESPONSIBLE FOR
-------------------
- topology validation
- policy enforcement
- renderer validation
- runtime inference
"""

from ontology_validator import (
    validate_ontology,
)

from ontology import (
    VALID_ZONES,
    VALID_PROTOCOLS,
    VALID_NODE_TYPES,
    VALID_TRANSPORTS,
    VALID_CONDUITS,
    VALID_PURDUE_LEVELS,
    DETACHED_PURDUE_DOMAINS,
    UNKNOWN_ZONE,
    UNKNOWN_PROTOCOL,
    UNKNOWN_NODE,
    UNKNOWN_TRANSPORT,
)

from aliases import (
    normalize_zone,
    normalize_protocol,
    normalize_node_type,
    normalize_transport,
    ZONE_ALIASES,
    PROTOCOL_ALIASES,
    NODE_TYPE_ALIASES,
    TRANSPORT_ALIASES,
)

from railway_rules import (
    FLOW_RULES,
)

# ============================================================
# HELPERS
# ============================================================


def check_alias_collisions(
    alias_map: dict,
    valid_set: set,
    label: str,
) -> list[str]:

    errors = []

    resolved = {}

    for alias, canonical in alias_map.items():

        if canonical not in valid_set:

            errors.append(f"[INVALID {label} ALIAS TARGET] " f"{alias} -> {canonical}")

        if alias in resolved and resolved[alias] != canonical:

            errors.append(f"[ALIAS COLLISION] " f"{alias}")

        resolved[alias] = canonical

    return errors


# ============================================================
# VALIDATE SEMANTIC KERNEL
# ============================================================


def validate_semantic_kernel():

    print("\n" + "=" * 60)
    print("SEMANTIC KERNEL VALIDATION")
    print("=" * 60)

    errors = []

    # ========================================================
    # ONTOLOGY VALIDATION
    # ========================================================

    ontology_report = validate_ontology()

    ontology_error_count = sum(len(v) for v in ontology_report.values())

    if ontology_error_count > 0:

        errors.append(f"Ontology validation failed: " f"{ontology_error_count} errors")

    # ========================================================
    # CANONICALIZATION DRIFT
    # ========================================================

    print("\nCANONICALIZATION DRIFT CHECK")
    print("-" * 60)

    # --------------------------------------------------------
    # ZONES
    # --------------------------------------------------------

    for zone in sorted(VALID_ZONES):

        normalized = normalize_zone(zone)

        if normalized != zone:

            msg = f"[ZONE DRIFT] " f"{zone} -> {normalized}"

            print(msg)

            errors.append(msg)

    # --------------------------------------------------------
    # PROTOCOLS
    # --------------------------------------------------------

    for proto in sorted(VALID_PROTOCOLS):

        normalized = normalize_protocol(proto)

        if normalized != proto:

            msg = f"[PROTOCOL DRIFT] " f"{proto} -> {normalized}"

            print(msg)

            errors.append(msg)

    # --------------------------------------------------------
    # NODE TYPES
    # --------------------------------------------------------

    for node_type in sorted(VALID_NODE_TYPES):

        normalized = normalize_node_type(node_type)

        if normalized != node_type:

            msg = f"[NODE TYPE DRIFT] " f"{node_type} -> {normalized}"

            print(msg)

            errors.append(msg)

    # --------------------------------------------------------
    # TRANSPORTS
    # --------------------------------------------------------

    for transport in sorted(VALID_TRANSPORTS):

        normalized = normalize_transport(transport)

        if normalized != transport:

            msg = f"[TRANSPORT DRIFT] " f"{transport} -> {normalized}"

            print(msg)

            errors.append(msg)

    # ========================================================
    # STRICT CANONICAL FORMAT
    # ========================================================

    print("\nCANONICAL FORMAT CHECK")
    print("-" * 60)

    for zone in VALID_ZONES:

        if zone != zone.lower():

            errors.append(f"[NONCANONICAL ZONE] " f"{zone}")

    for node_type in VALID_NODE_TYPES:

        if node_type != node_type.lower():

            errors.append(f"[NONCANONICAL NODE TYPE] " f"{node_type}")

    for transport in VALID_TRANSPORTS:

        if transport != transport.lower():

            errors.append(f"[NONCANONICAL TRANSPORT] " f"{transport}")

    # ========================================================
    # FLOW RULE CONSISTENCY
    # ========================================================

    print("\nFLOW RULE CONSISTENCY")
    print("-" * 60)

    seen_flow_rules = set()

    for (
        source,
        target,
    ), rule in FLOW_RULES.items():

        if (source, target) in seen_flow_rules:

            msg = f"[DUPLICATE FLOW RULE] " f"{source} -> {target}"

            print(msg)

            errors.append(msg)

        seen_flow_rules.add((source, target))

        if source not in VALID_NODE_TYPES:

            msg = f"[INVALID FLOW SOURCE] " f"{source}"

            print(msg)

            errors.append(msg)

        if target not in VALID_NODE_TYPES:

            msg = f"[INVALID FLOW TARGET] " f"{target}"

            print(msg)

            errors.append(msg)

        conduit_class = rule.get(
            "conduit_class",
        )

        if conduit_class and conduit_class not in VALID_CONDUITS:

            msg = (
                f"[INVALID FLOW CONDUIT CLASS] "
                f"{source} -> {target} -> {conduit_class}"
            )

            print(msg)

            errors.append(msg)

    # ========================================================
    # DETACHED DOMAIN GOVERNANCE
    # ========================================================

    print("\nDETACHED DOMAIN GOVERNANCE")
    print("-" * 60)

    for level in DETACHED_PURDUE_DOMAINS:

        if level not in VALID_PURDUE_LEVELS:

            msg = f"[INVALID DETACHED PURDUE DOMAIN] " f"{level}"

            print(msg)

            errors.append(msg)

    # ========================================================
    # ALIAS VALIDATION
    # ========================================================

    print("\nALIAS VALIDATION")
    print("-" * 60)

    errors.extend(
        check_alias_collisions(
            ZONE_ALIASES,
            VALID_ZONES,
            "ZONE",
        )
    )

    errors.extend(
        check_alias_collisions(
            PROTOCOL_ALIASES,
            VALID_PROTOCOLS,
            "PROTOCOL",
        )
    )

    errors.extend(
        check_alias_collisions(
            NODE_TYPE_ALIASES,
            VALID_NODE_TYPES,
            "NODE TYPE",
        )
    )

    errors.extend(
        check_alias_collisions(
            TRANSPORT_ALIASES,
            VALID_TRANSPORTS,
            "TRANSPORT",
        )
    )

    # ========================================================
    # UNKNOWN GOVERNANCE
    # ========================================================

    print("\nUNKNOWN GOVERNANCE")
    print("-" * 60)

    unknown_tests = {
        "zone": normalize_zone("THIS_IS_INVALID"),
        "protocol": normalize_protocol("THIS_IS_INVALID"),
        "node": normalize_node_type("THIS_IS_INVALID"),
        "transport": normalize_transport("THIS_IS_INVALID"),
    }

    expected = {
        "zone": UNKNOWN_ZONE,
        "protocol": UNKNOWN_PROTOCOL,
        "node": UNKNOWN_NODE,
        "transport": UNKNOWN_TRANSPORT,
    }

    for key, value in unknown_tests.items():

        if value != expected[key]:

            msg = f"[UNKNOWN GOVERNANCE FAILURE] " f"{key} -> {value}"

            print(msg)

            errors.append(msg)

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("SEMANTIC KERNEL SUMMARY")
    print("=" * 60)

    if not errors:

        print("\n[OK] Semantic kernel validation passed.")

    else:

        print(f"\n[FATAL] {len(errors)} semantic errors detected.")

        for err in errors:

            print(f"  - {err}")

    return sorted(errors)
