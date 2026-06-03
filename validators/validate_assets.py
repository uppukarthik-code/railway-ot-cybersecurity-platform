"""
asset_validator.py

FINAL HARDENED ASSET VALIDATOR
IEC62443 + EN50159 + Railway OT + Kavach

RESPONSIBILITIES
----------------
- Structural node validation
- Canonical formatting validation
- Graph integrity validation
- Lifecycle-state validation

NOT RESPONSIBLE FOR
-------------------
- Purdue validation
- Zone validation policy
- Semantic inference
- Renderer logic
- Classification logic
"""

import re

from ontology import (
    VALID_NODE_TYPES,
    VALID_ZONES,
    VALID_PURDUE_LEVELS,
    ASSET_ONTOLOGY,
)

# ============================================================
# VALID SAFETY LEVELS
# ============================================================

VALID_SILS = {
    "SIL0",
    "SIL1",
    "SIL2",
    "SIL3",
    "SIL4",
}

# ============================================================
# REQUIRED NODE FIELDS
# ============================================================

REQUIRED_NODE_FIELDS = {
    "id",
    "type",
    "label",
    "zone",
    "purdue_level",
}

# ============================================================
# SAFE GRAPH ID
# ============================================================

SAFE_ID_REGEX = r"^[a-zA-Z0-9_\-]+$"

# ============================================================
# SAFE LABEL FORMAT
# ============================================================

SAFE_LABEL_REGEX = r"^[^\n\r\t<>`]+$"

# ============================================================
# VALIDATE ASSETS
# ============================================================


def validate_assets(
    topology: dict,
) -> list[str]:

    errors = []

    print("\n══ ASSET VALIDATION ══")

    print("-" * 50)

    seen_ids = set()

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
                "",
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

        label = str(
            node.get(
                "label",
                "",
            )
        ).strip()

        # ====================================================
        # REQUIRED FIELD VALIDATION
        # ====================================================

        missing_fields = [field for field in REQUIRED_NODE_FIELDS if field not in node]

        if missing_fields:

            msg = (
                f"[MISSING REQUIRED FIELDS] "
                f"{node_id or '<unknown>'} -> "
                f"{missing_fields}"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # NODE ID
        # ====================================================

        if not node_id:

            msg = "[MISSING NODE ID]"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # SAFE GRAPH ID
        # ====================================================

        if not re.match(
            SAFE_ID_REGEX,
            node_id,
        ):

            msg = f"[INVALID NODE ID FORMAT] {node_id}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # DUPLICATE IDS
        # ====================================================

        if node_id in seen_ids:

            msg = f"[DUPLICATE NODE ID] {node_id}"

            print(msg)

            errors.append(msg)

        seen_ids.add(node_id)

        # ====================================================
        # LABEL
        # ====================================================

        if not label:

            msg = f"[MISSING LABEL] {node_id}"

            print(msg)

            errors.append(msg)

        elif not re.match(
            SAFE_LABEL_REGEX,
            label,
        ):

            msg = f"[UNSAFE LABEL FORMAT] {node_id}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # ASSET TYPE
        # ====================================================

        if not asset_type:

            msg = f"[MISSING ASSET TYPE] {node_id}"

            print(msg)

            errors.append(msg)

        elif asset_type not in VALID_NODE_TYPES:

            msg = f"[UNKNOWN ASSET TYPE] " f"{node_id} -> {asset_type}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # CANONICAL TYPE FORMAT
        # ====================================================

        raw_type = str(
            node.get(
                "type",
                "",
            )
        ).strip()

        if raw_type != raw_type.lower():

            msg = f"[NONCANONICAL TYPE] " f"{node_id} -> {raw_type}"

            print(msg)

            errors.append(msg)

        if " " in raw_type:

            msg = f"[INVALID TYPE FORMAT] " f"{node_id} -> {raw_type}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # ZONE FORMAT
        # ====================================================

        zone = str(
            node.get(
                "zone",
                "",
            )
        ).strip()

        if not zone:

            msg = f"[MISSING ZONE] {node_id}"

            print(msg)

            errors.append(msg)

        elif zone not in VALID_ZONES:

            msg = f"[UNKNOWN ZONE] " f"{node_id} -> {zone}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # PURDUE FORMAT
        # ====================================================

        purdue = str(
            node.get(
                "purdue_level",
                "",
            )
        ).strip()

        if not purdue:

            msg = f"[MISSING PURDUE] {node_id}"

            print(msg)

            errors.append(msg)

        elif purdue not in VALID_PURDUE_LEVELS:

            msg = f"[UNKNOWN PURDUE] " f"{node_id} -> {purdue}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # SAFETY VALIDATION
        # Ontology is authoritative
        # ====================================================

        asset_meta = ASSET_ONTOLOGY.get(
            asset_type,
            {},
        )

        if asset_meta.get(
            "safety_critical",
            False,
        ):

            sil = str(
                asset_meta.get(
                    "functional_safety_level",
                    "",
                )
            ).upper()

            if sil not in VALID_SILS:

                msg = f"[INVALID ONTOLOGY SAFETY LEVEL] " f"{asset_type} -> {sil}"

                print(msg)

                errors.append(msg)

    # ========================================================
    # CONNECTION ENDPOINT VALIDATION
    # ========================================================

    connections = topology.get(
        "connections",
        [],
    )

    for conn in connections:

        src = conn.get(
            "source",
            "",
        )

        dst = conn.get(
            "target",
            "",
        )

        if src not in seen_ids:

            msg = f"[UNKNOWN SOURCE NODE] {src}"

            print(msg)

            errors.append(msg)

        if dst not in seen_ids:

            msg = f"[UNKNOWN TARGET NODE] {dst}"

            print(msg)

            errors.append(msg)

    # ========================================================
    # SUMMARY
    # ========================================================

    print(f"\nASSET VALIDATION ERRORS: " f"{len(errors)}")

    return sorted(errors)
