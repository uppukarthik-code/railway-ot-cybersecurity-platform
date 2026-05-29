"""
purdue_validator.py

FINAL HARDENED PURDUE VALIDATOR

IEC62443 + EN50159 + Railway OT + Kavach

RESPONSIBILITIES
----------------
- Purdue level validation
- Asset-to-level consistency verification
- Structural Purdue compliance checks
- Detached Purdue domain validation

NOT RESPONSIBLE FOR
-------------------
- Purdue inference
- Zone validation
- Renderer semantics
- Classification state management
- Cluster validation
"""

from ontology import (
    ASSET_ONTOLOGY,
    VALID_PURDUE_LEVELS,
    VALID_PURDUE_BY_ASSET,
    DETACHED_PURDUE_DOMAINS,
    normalize_purdue,
)

from aliases import (
    normalize_node_type,
)

# ============================================================
# VALIDATE PURDUE
# ============================================================


def validate_purdue(
    topology: dict,
) -> list[str]:

    errors = []

    print("\n══ PURDUE VALIDATION ══")

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
        # CLASSIFICATION STATE
        # ====================================================

        classified = bool(
            node.get(
                "classified",
                False,
            )
        )

        # ====================================================
        # UNCLASSIFIED NODES
        # ====================================================

        if not classified:

            print(f"[WARN] Unclassified node: " f"{node_id}")

            continue

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
        # NORMALIZED PURDUE LEVEL
        # ====================================================

        actual = normalize_purdue(
            node.get(
                "purdue_level",
                "",
            )
        )

        # ====================================================
        # MISSING PURDUE
        # ====================================================

        if not actual:

            msg = f"[MISSING PURDUE] " f"{node_id}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # INVALID PURDUE
        # ====================================================

        if actual not in VALID_PURDUE_LEVELS:

            msg = f"[INVALID PURDUE] " f"{node_id} -> {actual}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # UNKNOWN ASSET TYPE
        # ====================================================

        if asset_type not in ASSET_ONTOLOGY:

            msg = f"[UNKNOWN ASSET TYPE] " f"{node_id} -> {asset_type}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # ALLOWED PURDUE
        # ====================================================

        allowed_purdue = VALID_PURDUE_BY_ASSET.get(
            asset_type,
            set(),
        )

        # ====================================================
        # FALLBACK TO ONTOLOGY PURDUE
        # ====================================================

        if not allowed_purdue:

            ontology_purdue = ASSET_ONTOLOGY.get(
                asset_type,
                {},
            ).get(
                "purdue",
            )

            if ontology_purdue:

                allowed_purdue = {
                    ontology_purdue,
                }

        # ====================================================
        # UNKNOWN PURDUE HANDLING
        # ====================================================

        if actual == "Unknown":

            externally_hosted = bool(
                node.get(
                    "externally_hosted",
                    False,
                )
            )

            if not externally_hosted:

                print(f"[WARN] Unknown Purdue placement: " f"{node_id}")

            continue

        # ====================================================
        # DETACHED DOMAIN VALIDATION
        # ====================================================

        if actual in DETACHED_PURDUE_DOMAINS:

            if allowed_purdue and actual not in allowed_purdue:

                msg = f"[INVALID DETACHED PURDUE] " f"{node_id} -> {actual}"

                print(msg)

                print(f"  Allowed : " f"{sorted(allowed_purdue)}")

                print(f"  Actual  : " f"{actual}")

                errors.append(msg)

            continue

        # ====================================================
        # PURDUE MISMATCH
        # ====================================================

        if allowed_purdue and actual not in allowed_purdue:

            msg = f"[PURDUE MISMATCH] " f"{node_id} -> {actual}"

            print(msg)

            print(f"  Allowed : " f"{sorted(allowed_purdue)}")

            print(f"  Actual  : " f"{actual}")

            errors.append(msg)

    # ========================================================
    # SUMMARY
    # ========================================================

    print(f"\nPURDUE VALIDATION ERRORS: " f"{len(errors)}")

    return sorted(errors)


"""
purdue_validator.py

FINAL HARDENED PURDUE VALIDATOR

IEC62443 + EN50159 + Railway OT + Kavach

RESPONSIBILITIES
----------------
- Purdue level validation
- Asset-to-level consistency verification
- Structural Purdue compliance checks

NOT RESPONSIBLE FOR
-------------------
- Purdue inference
- Zone validation
- Renderer semantics
- Classification state management
"""

from ontology import (
    VALID_PURDUE_LEVELS,
    VALID_PURDUE_BY_ASSET,
    normalize_purdue,
)

# ============================================================
# VALIDATE PURDUE
# ============================================================


def validate_purdue(
    topology: dict,
) -> list[str]:

    errors = []

    print("\n══ PURDUE VALIDATION ══")

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

        asset_type = (
            str(
                node.get(
                    "type",
                    "",
                )
            )
            .strip()
            .lower()
        )

        # ====================================================
        # RAW PURDUE
        # ====================================================

        raw_purdue = node.get(
            "purdue_level",
        )

        if raw_purdue is None or str(raw_purdue).strip() == "":

            msg = f"[MISSING PURDUE] {node_id}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # NORMALIZED PURDUE
        # ====================================================

        actual = normalize_purdue(
            raw_purdue,
        )

        # ====================================================
        # INVALID PURDUE
        # ====================================================

        if actual not in VALID_PURDUE_LEVELS:

            msg = f"[INVALID PURDUE] {node_id} -> {actual}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # UNKNOWN PURDUE
        # ====================================================

        if actual == "Unknown":

            externally_hosted = bool(
                node.get(
                    "externally_hosted",
                    False,
                )
            )

            if not externally_hosted:

                print(f"[WARN] Unknown Purdue placement: " f"{node_id}")

            continue

        # ====================================================
        # ASSET VALIDATION
        # ====================================================

        allowed_purdue = VALID_PURDUE_BY_ASSET.get(
            asset_type,
            set(),
        )

        # ====================================================
        # UNKNOWN ASSET TYPE
        # ====================================================

        if not allowed_purdue:

            msg = f"[UNKNOWN ASSET TYPE] " f"{node_id} -> {asset_type}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # PURDUE MISMATCH
        # ====================================================

        if actual not in allowed_purdue:

            msg = f"[PURDUE MISMATCH] " f"{node_id} -> {actual}"

            print(msg)

            print(f"  Allowed : " f"{sorted(allowed_purdue)}")

            print(f"  Actual  : " f"{actual}")

            errors.append(msg)

    # ========================================================
    # SUMMARY
    # ========================================================

    print(f"\nPURDUE VALIDATION ERRORS: " f"{len(errors)}")

    return sorted(errors)
