"""
ontology_validator.py

FINAL HARDENED ONTOLOGY VALIDATOR

IEC62443 + EN50126 + EN50129 + EN50159 + Kavach

PURPOSE
-------
Validates:

1. Ontology schema integrity
2. Cross-ontology semantic consistency
3. Rules consistency
4. Purdue/Zone semantic alignment
5. Protocol/Transport separation
6. Render consistency
7. Safety/security semantic correctness
8. Canonicalization drift detection
9. Alias normalization stability

NO topology validation.
NO runtime graph validation.
NO classifier runtime validation.
"""

from ontology import (
    ASSET_ONTOLOGY,
    ZONE_ONTOLOGY,
    PURDUE_LEVELS,
    PROTOCOL_ONTOLOGY,
    TRANSPORT_ONTOLOGY,
    CONDUIT_ONTOLOGY,
    ZONE_RENDER_ATTRIBUTES,
    VALID_ZONES,
    VALID_NODE_TYPES,
    VALID_PROTOCOLS,
)

from railway_rules import (
    REQUIRED_LOGICAL_LINKS,
    FORBIDDEN_CONNECTIONS,
    HIGH_RISK_CONNECTIONS,
    CONDITIONALLY_ALLOWED_CONNECTIONS,
)

from aliases import (
    normalize_zone,
    normalize_node_type,
    normalize_protocol,
)

# ============================================================
# HELPERS
# ============================================================


def err(errors, msg):

    print(msg)

    errors.append(msg)


# ============================================================
# CANONICAL CONSTANTS
# ============================================================

VALID_SECURITY_LEVELS = {
    "SL0",
    "SL1",
    "SL2",
    "SL3",
    "SL4",
}

VALID_TRUST_LEVELS = {
    "trusted",
    "semi_trusted",
    "low",
}

VALID_ZONE_PURDUE_MAPPING = {
    "enterprise_it": {
        "L5 Enterprise",
        "L4 Business",
    },
    "business_systems": {
        "L4 Business",
    },
    "idmz": {
        "L3.5 IDMZ",
    },
    "security_management": {
        "L3.5 Security",
    },
    "external_security": {
        "L3.5 Security",
    },
    "operations": {
        "L3 Operations",
    },
    "maintenance": {
        "L3 Operations",
        "L2 Interlocking",
    },
    "telecom_core": {
        "L2 Telecom",
    },
    "radio_access": {
        "L1 Telecom",
    },
    "station_control": {
        "L2 Station Control",
    },
    "interlocking": {
        "L1 Interlocking",
        "L2 Interlocking",
    },
    "train_detection": {
        "L1 Interlocking",
        "L0 Field",
    },
    "point_control": {
        "L0 Field",
    },
    "signal_control": {
        "L0 Field",
    },
    "field": {
        "L0 Field",
    },
    "trackside": {
        "L0 Field",
    },
    "onboard": {
        "Onboard",
    },
}

# ============================================================
# CANONICALIZATION VALIDATION
# ============================================================


def validate_canonicalization():

    errors = []

    print("\nCANONICALIZATION VALIDATION")
    print("-" * 60)

    # ========================================================
    # ZONE NORMALIZATION
    # ========================================================

    for zone in VALID_ZONES:

        normalized = normalize_zone(zone)

        if normalized != zone:

            err(
                errors,
                f"[ZONE CANONICALIZATION DRIFT] " f"{zone} -> {normalized}",
            )

    # ========================================================
    # NODE TYPE NORMALIZATION
    # ========================================================

    for node_type in VALID_NODE_TYPES:

        normalized = normalize_node_type(node_type)

        if normalized != node_type:

            err(
                errors,
                f"[NODE TYPE CANONICALIZATION DRIFT] " f"{node_type} -> {normalized}",
            )

    # ========================================================
    # PROTOCOL NORMALIZATION
    # ========================================================

    for protocol in VALID_PROTOCOLS:

        normalized = normalize_protocol(protocol)

        if normalized != protocol:

            err(
                errors,
                f"[PROTOCOL CANONICALIZATION DRIFT] " f"{protocol} -> {normalized}",
            )

    print(f"\nCANONICALIZATION ERRORS : {len(errors)}")

    return errors


# ============================================================
# ASSET VALIDATION
# ============================================================


def validate_asset_ontology():

    errors = []

    print("\nASSET ONTOLOGY VALIDATION")
    print("-" * 60)

    valid_zones = set(ZONE_ONTOLOGY.keys())

    valid_purdue = set(PURDUE_LEVELS.keys())

    required_fields = {
        "zone",
        "purdue",
        "criticality",
        "safety_critical",
    }

    for asset_name, asset in ASSET_ONTOLOGY.items():

        missing = required_fields - set(asset.keys())

        if missing:

            err(
                errors,
                f"[MISSING ASSET FIELDS] " f"{asset_name} -> {sorted(missing)}",
            )

        zone = asset.get("zone")

        if zone not in valid_zones:

            err(
                errors,
                f"[INVALID ZONE] " f"{asset_name} -> {zone}",
            )

        purdue = asset.get("purdue")

        if purdue not in valid_purdue:

            err(
                errors,
                f"[INVALID PURDUE] " f"{asset_name} -> {purdue}",
            )

        if not isinstance(asset.get("safety_critical"), bool):

            err(
                errors,
                f"[INVALID safety_critical TYPE] " f"{asset_name}",
            )

        # ====================================================
        # ZONE ↔️ PURDUE ALIGNMENT
        # ====================================================

        allowed = VALID_ZONE_PURDUE_MAPPING.get(
            zone,
            set(),
        )

        if purdue not in allowed:

            err(
                errors,
                f"[ZONE/PURDUE MISMATCH] " f"{asset_name} -> " f"{zone} / {purdue}",
            )

    print(f"\nASSET ONTOLOGY ERRORS : {len(errors)}")

    return errors


# ============================================================
# ZONE VALIDATION
# ============================================================


def validate_zone_ontology():

    errors = []

    print("\nZONE ONTOLOGY VALIDATION")
    print("-" * 60)

    required_fields = {
        "trust",
        "security_level",
        "criticality",
    }

    for zone_name, zone in ZONE_ONTOLOGY.items():

        missing = required_fields - set(zone.keys())

        if missing:

            err(
                errors,
                f"[MISSING ZONE FIELDS] " f"{zone_name} -> {sorted(missing)}",
            )

        trust = zone.get("trust")

        if trust not in VALID_TRUST_LEVELS:

            err(
                errors,
                f"[INVALID TRUST LEVEL] " f"{zone_name} -> {trust}",
            )

        sl = zone.get("security_level")

        if sl not in VALID_SECURITY_LEVELS:

            err(
                errors,
                f"[INVALID SECURITY LEVEL] " f"{zone_name} -> {sl}",
            )

    print(f"\nZONE ONTOLOGY ERRORS : {len(errors)}")

    return errors


# ============================================================
# PROTOCOL VALIDATION
# ============================================================


def validate_protocol_ontology():

    errors = []

    print("\nPROTOCOL ONTOLOGY VALIDATION")
    print("-" * 60)

    required_fields = {
        "encrypted",
        "authenticated",
        "integrity_protected",
        "safety_related",
    }

    for proto_name, proto in PROTOCOL_ONTOLOGY.items():

        missing = required_fields - set(proto.keys())

        if missing:

            err(
                errors,
                f"[MISSING PROTOCOL FIELDS] " f"{proto_name} -> {sorted(missing)}",
            )

        for field in required_fields:

            value = proto.get(field)

            if not isinstance(value, bool):

                err(
                    errors,
                    f"[INVALID PROTOCOL TYPE] " f"{proto_name}.{field}",
                )

    print(f"\nPROTOCOL ONTOLOGY ERRORS : {len(errors)}")

    return errors


# ============================================================
# TRANSPORT VALIDATION
# ============================================================


def validate_transport_ontology():

    errors = []

    print("\nTRANSPORT ONTOLOGY VALIDATION")
    print("-" * 60)

    required_fields = {
        "wireless",
        "public_network",
    }

    for name, transport in TRANSPORT_ONTOLOGY.items():

        missing = required_fields - set(transport.keys())

        if missing:

            err(
                errors,
                f"[MISSING TRANSPORT FIELDS] " f"{name} -> {sorted(missing)}",
            )

        for field in required_fields:

            value = transport.get(field)

            if not isinstance(value, bool):

                err(
                    errors,
                    f"[INVALID TRANSPORT TYPE] " f"{name}.{field}",
                )

    print(f"\nTRANSPORT ONTOLOGY ERRORS : {len(errors)}")

    return errors


# ============================================================
# CONDUIT VALIDATION
# ============================================================


def validate_conduit_ontology():

    errors = []

    print("\nCONDUIT ONTOLOGY VALIDATION")
    print("-" * 60)

    for conduit_name, conduit in CONDUIT_ONTOLOGY.items():

        if not isinstance(conduit, dict):

            err(
                errors,
                f"[INVALID CONDUIT TYPE] " f"{conduit_name}",
            )

            continue

        physical = conduit.get("physical", False)

        logical = conduit.get("logical", False)

        wireless = conduit.get("wireless", False)

        if physical and logical:

            err(
                errors,
                f"[PHYSICAL/LOGICAL CONFLICT] " f"{conduit_name}",
            )

        if physical and wireless:

            err(
                errors,
                f"[PHYSICAL/WIRELESS CONFLICT] " f"{conduit_name}",
            )

    print(f"\nCONDUIT ONTOLOGY ERRORS : {len(errors)}")

    return errors


# ============================================================
# RENDER VALIDATION
# ============================================================


def validate_render_metadata():

    errors = []

    print("\nRENDER VALIDATION")
    print("-" * 60)

    valid_zones = set(ZONE_ONTOLOGY.keys())

    for zone in valid_zones:

        if zone not in ZONE_RENDER_ATTRIBUTES:

            err(
                errors,
                f"[MISSING RENDER METADATA] " f"{zone}",
            )

            continue

        meta = ZONE_RENDER_ATTRIBUTES[zone]

        required = {
            "color",
            "external",
            "detached",
        }

        missing = required - set(meta.keys())

        if missing:

            err(
                errors,
                f"[INCOMPLETE RENDER METADATA] " f"{zone} -> {sorted(missing)}",
            )

    print(f"\nRENDER ERRORS : {len(errors)}")

    return errors


# ============================================================
# PROTOCOL ↔️ TRANSPORT SEPARATION
# ============================================================


def validate_protocol_transport_separation():

    errors = []

    print("\nPROTOCOL / TRANSPORT SEPARATION")
    print("-" * 60)

    transport_names = {x.upper() for x in TRANSPORT_ONTOLOGY.keys()}

    protocol_names = {x.upper() for x in PROTOCOL_ONTOLOGY.keys()}

    overlap = transport_names.intersection(protocol_names)

    for item in overlap:

        err(
            errors,
            f"[TRANSPORT/PROTOCOL OVERLAP] {item}",
        )

    print(f"\nSEPARATION ERRORS : {len(errors)}")

    return errors


# ============================================================
# RULE CONSISTENCY VALIDATION
# ============================================================


def validate_rules_consistency():

    errors = []

    print("\nRULE CONSISTENCY VALIDATION")
    print("-" * 60)

    valid_assets = set(ASSET_ONTOLOGY.keys())

    valid_zones = set(ZONE_ONTOLOGY.keys())

    # ========================================================
    # REQUIRED LOGICAL LINKS
    # ========================================================

    for source, targets in REQUIRED_LOGICAL_LINKS.items():

        if source not in valid_assets:

            err(
                errors,
                f"[INVALID RULE SOURCE] {source}",
            )

        for target in targets:

            if target not in valid_assets:

                err(
                    errors,
                    f"[INVALID RULE TARGET] " f"{source} -> {target}",
                )

    # ========================================================
    # ZONE RULES
    # ========================================================

    zone_pair_rules = [
        FORBIDDEN_CONNECTIONS,
        HIGH_RISK_CONNECTIONS,
    ]

    for rules in zone_pair_rules:

        for source, target in rules:

            if source not in valid_zones:

                err(
                    errors,
                    f"[INVALID ZONE SOURCE] {source}",
                )

            if target not in valid_zones:

                err(
                    errors,
                    f"[INVALID ZONE TARGET] {target}",
                )

    # ========================================================
    # ASSET RULES
    # ========================================================

    asset_pair_rules = [
        CONDITIONALLY_ALLOWED_CONNECTIONS,
    ]

    for rules in asset_pair_rules:

        for source, target in rules:

            if source not in valid_assets:

                err(
                    errors,
                    f"[INVALID ASSET SOURCE] {source}",
                )

            if target not in valid_assets:

                err(
                    errors,
                    f"[INVALID ASSET TARGET] {target}",
                )

    print(f"\nRULE CONSISTENCY ERRORS : {len(errors)}")

    return errors


# ============================================================
# CROSS ONTOLOGY VALIDATION
# ============================================================


def validate_cross_ontology_consistency():

    errors = []

    print("\nCROSS ONTOLOGY VALIDATION")
    print("-" * 60)

    for asset_name, asset in ASSET_ONTOLOGY.items():

        zone = asset.get("zone")

        trust = ZONE_ONTOLOGY.get(
            zone,
            {},
        ).get(
            "trust",
        )

        safety = asset.get(
            "safety_critical",
            False,
        )

        sil = asset.get(
            "functional_safety_level",
            "",
        )

        # ====================================================
        # SAFETY + LOW TRUST
        # ====================================================

        if safety and trust == "low":

            print(f"[WARN] SAFETY ASSET IN LOW TRUST ZONE " f"{asset_name} -> {zone}")

        # ====================================================
        # SIL4 + LOW TRUST
        # ====================================================

        if sil == "SIL4" and trust == "low":

            print(f"[WARN] SIL4 ASSET IN LOW TRUST ZONE " f"{asset_name}")

    print(f"\nCROSS ONTOLOGY ERRORS : {len(errors)}")

    return errors


# ============================================================
# UNKNOWN GOVERNANCE
# ============================================================


def validate_unknown_governance():

    errors = []

    print("\nUNKNOWN GOVERNANCE VALIDATION")
    print("-" * 60)

    if "unknown" not in ASSET_ONTOLOGY:

        err(
            errors,
            "[MISSING UNKNOWN ASSET]",
        )

    if "UNKNOWN" not in PROTOCOL_ONTOLOGY:

        err(
            errors,
            "[MISSING UNKNOWN PROTOCOL]",
        )

    print(f"\nUNKNOWN GOVERNANCE ERRORS : {len(errors)}")

    return errors


# ============================================================
# MASTER VALIDATOR
# ============================================================


def validate_ontology():

    all_errors = {}

    all_errors["canonicalization_errors"] = validate_canonicalization()

    all_errors["asset_errors"] = validate_asset_ontology()

    all_errors["zone_errors"] = validate_zone_ontology()

    all_errors["protocol_errors"] = validate_protocol_ontology()

    all_errors["transport_errors"] = validate_transport_ontology()

    all_errors["conduit_errors"] = validate_conduit_ontology()

    all_errors["render_errors"] = validate_render_metadata()

    all_errors["separation_errors"] = validate_protocol_transport_separation()

    all_errors["rules_errors"] = validate_rules_consistency()

    all_errors["cross_errors"] = validate_cross_ontology_consistency()

    all_errors["unknown_errors"] = validate_unknown_governance()

    total = sum(len(v) for v in all_errors.values())

    print("\n" + "=" * 60)
    print("ONTOLOGY VALIDATION SUMMARY")
    print("=" * 60)

    for category, errs in all_errors.items():

        print(f"{category}: {len(errs)}")

    print(f"\nTOTAL ERRORS : {total}")

    return all_errors


# ============================================================
# ENTRYPOINT
# ============================================================

if __name__ == "__main__":

    validate_ontology()
