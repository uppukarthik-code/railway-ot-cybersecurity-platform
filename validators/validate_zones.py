"""
zone_validator.py

FINAL HARDENED ZONE VALIDATOR

IEC62443 + EN50159 + Railway OT + Kavach

RESPONSIBILITIES
----------------
- Zone validation
- Asset-to-zone consistency verification
- Canonical zoning checks
- Detached-domain zoning validation

NOT RESPONSIBLE FOR
-------------------
- Zone inference
- Trust policy generation
- Semantic recovery
- Classification logic
- Rendering validation
"""

from ontology import (
    ASSET_ONTOLOGY,
    VALID_ZONES,
)

from aliases import (
    normalize_node_type,
    normalize_zone,
)

# ============================================================
# EXTERNALLY HOSTED FORBIDDEN ZONES
# ============================================================

EXTERNAL_HOSTING_FORBIDDEN_ZONES = {
    "interlocking",
    "field",
    "onboard",
}

# ============================================================
# VALIDATE ZONES
# ============================================================


def validate_zones(
    topology: dict,
) -> list[str]:

    errors = []

    print("\n══ ZONE VALIDATION ══")

    print("-" * 50)

    nodes = topology.get(
        "nodes",
        [],
    )

    # ========================================================
    # PROCESS NODES
    # ========================================================

    for node in nodes:

        node_id = str(
            node.get(
                "id",
                "UNKNOWN_ID",
            )
        ).strip()

        # ====================================================
        # NORMALIZED ASSET TYPE
        # ====================================================

        asset_type = normalize_node_type(
            node.get(
                "type",
                "",
            )
        )

        # ====================================================
        # RAW ZONE
        # ====================================================

        raw_zone = str(
            node.get(
                "zone",
                "",
            )
        ).strip()

        # ====================================================
        # NORMALIZED ZONE
        # ====================================================

        zone = normalize_zone(
            raw_zone,
        )

        # ====================================================
        # CLASSIFICATION
        # ====================================================

        classified = bool(
            node.get(
                "classified",
                False,
            )
        )

        # ====================================================
        # MISSING ZONE
        # ====================================================

        if not zone:

            msg = f"[MISSING ZONE] {node_id}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # NONCANONICAL ZONE NORMALIZATION
        # ====================================================

        if raw_zone != zone:

            print(
                f"[WARN] Noncanonical zone normalized: "
                f"{node_id} -> {raw_zone} -> {zone}"
            )

        # ====================================================
        # NONCANONICAL ZONE CASING
        # ====================================================

        if raw_zone and raw_zone != raw_zone.lower():

            print(f"[WARN] Noncanonical zone casing: " f"{node_id} -> {raw_zone}")

        # ====================================================
        # UNKNOWN ZONE
        # ====================================================

        if zone not in VALID_ZONES:

            msg = f"[UNKNOWN ZONE] {node_id} -> {zone}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # UNKNOWN ASSET TYPE
        # ====================================================

        if asset_type not in ASSET_ONTOLOGY:

            msg = f"[UNKNOWN ASSET TYPE] {node_id} -> {asset_type}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # ASSET METADATA
        # ====================================================

        asset_meta = ASSET_ONTOLOGY[asset_type]

        # ====================================================
        # ALLOWED ZONES
        # ====================================================

        allowed_zones = set(
            asset_meta.get(
                "allowed_zones",
                [],
            )
        )

        # ====================================================
        # FALLBACK TO PRIMARY ZONE
        # ====================================================

        ontology_zone = asset_meta.get(
            "zone",
        )

        if not allowed_zones and ontology_zone:

            allowed_zones = {
                ontology_zone,
            }

        # ====================================================
        # ONTOLOGY ZONE METADATA WARNING
        # ====================================================

        if not allowed_zones and not ontology_zone:

            print(f"[WARN] Asset ontology missing zoning metadata: " f"{asset_type}")

        # ====================================================
        # ZONE MISMATCH
        # ====================================================

        if allowed_zones and zone not in allowed_zones:

            msg = f"[ZONE MISMATCH] {node_id} -> {zone}"

            print(msg)

            print(f"  Allowed : {sorted(allowed_zones)}")

            print(f"  Actual  : {zone}")

            errors.append(msg)

        # ====================================================
        # CLASSIFICATION WARNING
        # ====================================================

        if not classified:

            print(f"[WARN] Unclassified node: {node_id}")

        # ====================================================
        # DETACHED / EXTERNAL DOMAIN VALIDATION
        # ====================================================

        externally_hosted = bool(
            node.get(
                "externally_hosted",
                False,
            )
        )

        third_party = bool(
            node.get(
                "third_party",
                False,
            )
        )

        cloud_hosted = bool(
            node.get(
                "cloud_hosted",
                False,
            )
        )

        detached_asset = externally_hosted or third_party or cloud_hosted

        if detached_asset and zone in EXTERNAL_HOSTING_FORBIDDEN_ZONES:

            msg = f"[INVALID EXTERNAL HOSTING ZONE] " f"{node_id} -> {zone}"

            print(msg)

            errors.append(msg)

    # ========================================================
    # SUMMARY
    # ========================================================

    print(f"\nZONE VALIDATION ERRORS: {len(errors)}")

    return sorted(errors)
