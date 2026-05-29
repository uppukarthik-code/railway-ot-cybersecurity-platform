"""
protocol_validator.py

FINAL HARDENED PROTOCOL VALIDATOR

IEC62443 + EN50159 + Railway OT + Kavach

DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- railway_rules.py = governance authority

RESPONSIBILITIES
----------------
- protocol validation
- protocol capability verification
- deployed-control consistency validation
- protocol semantic consistency validation

NOT RESPONSIBLE FOR
-------------------
- inference logic
- conduit generation
- normalization logic
"""

from ontology import (
    VALID_PROTOCOLS,
    LEGACY_PROTOCOLS,
    UNKNOWN_PROTOCOL,
    get_protocol_ontology,
)

# ============================================================
# BOOLEAN NORMALIZATION
# ============================================================


def as_bool(value):

    if isinstance(value, bool):

        return value

    if isinstance(value, str):

        return value.strip().lower() in {
            "true",
            "1",
            "yes",
        }

    return bool(value)


# ============================================================
# MAIN VALIDATION
# ============================================================


def validate_protocols(
    topology: dict,
) -> list[str]:

    errors = []

    print("\n══ PROTOCOL VALIDATION ══")

    print("-" * 60)

    for conn in topology.get(
        "connections",
        [],
    ):

        conn_id = str(
            conn.get(
                "id",
                "UNKNOWN_CONN",
            )
        ).strip()

        source = str(
            conn.get(
                "source",
                "UNKNOWN",
            )
        ).strip()

        target = str(
            conn.get(
                "target",
                "UNKNOWN",
            )
        ).strip()

        protocol = conn.get("protocol")

        # ====================================================
        # MISSING PROTOCOL
        # ====================================================

        if protocol is None or str(protocol).strip() == "":

            msg = f"[MISSING PROTOCOL] " f"{conn_id} " f"({source} -> {target})"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # NORMALIZATION
        # ====================================================

        protocol = str(protocol).strip().upper()

        # ====================================================
        # UNKNOWN PROTOCOL
        # ====================================================

        if protocol not in VALID_PROTOCOLS:

            msg = f"[UNKNOWN PROTOCOL] " f"{protocol} " f"({source} -> {target})"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # UNKNOWN PLACEHOLDER
        # ====================================================

        if protocol == UNKNOWN_PROTOCOL:

            print(
                f"[INFO] Unknown protocol placeholder used " f"({source} -> {target})"
            )

            continue

        # ====================================================
        # ONTOLOGY LOOKUP
        # ====================================================

        protocol_meta = get_protocol_ontology(protocol)

        stack_layer = protocol_meta.get(
            "stack_layer",
            "unknown",
        )

        protocol_class = protocol_meta.get(
            "protocol_class",
            "unknown",
        )

        passive_telegram = as_bool(
            protocol_meta.get(
                "passive_telegram_system",
                False,
            )
        )

        # ====================================================
        # DEPLOYED CONNECTION CAPABILITIES
        # ====================================================

        encrypted = as_bool(
            conn.get(
                "encrypted",
                False,
            )
        )

        authenticated = as_bool(
            conn.get(
                "authenticated",
                False,
            )
        )

        integrity_protected = as_bool(
            conn.get(
                "integrity_protected",
                False,
            )
        )

        replay_protected = as_bool(
            conn.get(
                "replay_protected",
                False,
            )
        )

        safety_related = as_bool(
            conn.get(
                "safety_related",
                False,
            )
        )

        safety_flow = as_bool(
            conn.get(
                "safety_flow",
                False,
            )
        )

        # ====================================================
        # CONTROL SOURCES
        # ====================================================

        encrypted_source = str(
            conn.get(
                "encrypted_source",
                "",
            )
        )

        authenticated_source = str(
            conn.get(
                "authenticated_source",
                "",
            )
        )

        integrity_source = str(
            conn.get(
                "integrity_protected_source",
                "",
            )
        )

        replay_source = str(
            conn.get(
                "replay_protected_source",
                "",
            )
        )

        # ====================================================
        # POLICY REQUIREMENTS
        # ====================================================

        requires_encryption = as_bool(
            conn.get(
                "requires_encryption",
                False,
            )
        )

        requires_authentication = as_bool(
            conn.get(
                "requires_authentication",
                False,
            )
        )

        requires_integrity = as_bool(
            conn.get(
                "requires_integrity",
                False,
            )
        )

        requires_replay_protection = as_bool(
            conn.get(
                "requires_replay_protection",
                False,
            )
        )

        # ====================================================
        # PROTOCOL CAPABILITIES
        # ====================================================

        native_encrypted = as_bool(
            protocol_meta.get(
                "encrypted",
                False,
            )
        )

        supports_encryption = as_bool(
            protocol_meta.get(
                "supports_encryption",
                native_encrypted,
            )
        )

        native_authenticated = as_bool(
            protocol_meta.get(
                "authenticated",
                False,
            )
        )

        native_integrity = as_bool(
            protocol_meta.get(
                "integrity_protected",
                False,
            )
        )

        native_replay = as_bool(
            protocol_meta.get(
                "replay_protected",
                False,
            )
        )

        expected_safety = as_bool(
            protocol_meta.get(
                "safety_related",
                False,
            )
        )

        # ====================================================
        # INVALID NATIVE CAPABILITY CLAIMS
        # ====================================================

        capability_checks = [
            (
                encrypted,
                encrypted_source,
                supports_encryption,
                "ENCRYPTION",
            ),
            (
                authenticated,
                authenticated_source,
                native_authenticated,
                "AUTHENTICATION",
            ),
            (
                integrity_protected,
                integrity_source,
                native_integrity,
                "INTEGRITY",
            ),
            (
                replay_protected,
                replay_source,
                native_replay,
                "REPLAY",
            ),
        ]

        for (
            actual,
            source_tag,
            supported,
            label,
        ) in capability_checks:

            if actual and source_tag == "protocol_ontology" and not supported:

                msg = (
                    f"[INVALID {label} CLAIM] "
                    f"{protocol} "
                    f"cannot natively provide "
                    f"{label.lower()} "
                    f"({source} -> {target})"
                )

                print(msg)

                errors.append(msg)

        # ====================================================
        # REQUIRED ENCRYPTION
        # ====================================================

        if requires_encryption and not encrypted:

            msg = (
                f"[UNENCRYPTED REQUIRED CONNECTION] "
                f"{protocol} "
                f"({source} -> {target})"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # REQUIRED AUTHENTICATION
        # ====================================================

        if requires_authentication and not authenticated:

            msg = f"[MISSING AUTHENTICATION] " f"{protocol} " f"({source} -> {target})"

            print(msg)

            errors.append(msg)

        # ====================================================
        # REQUIRED INTEGRITY
        # ====================================================

        if requires_integrity and not integrity_protected and not passive_telegram:

            msg = (
                f"[MISSING INTEGRITY PROTECTION] "
                f"{protocol} "
                f"({source} -> {target})"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # REQUIRED REPLAY PROTECTION
        # ====================================================

        if requires_replay_protection and not replay_protected and not passive_telegram:

            msg = (
                f"[MISSING REPLAY PROTECTION] " f"{protocol} " f"({source} -> {target})"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # SAFETY CONSISTENCY
        # ====================================================

        if safety_flow and expected_safety and not safety_related:

            msg = f"[SAFETY FLAG MISMATCH] " f"{protocol} " f"({source} -> {target})"

            print(msg)

            errors.append(msg)

        # ====================================================
        # LEGACY NOTICE
        # ====================================================

        if protocol in LEGACY_PROTOCOLS:

            print(f"[INFO] Legacy protocol detected: " f"{protocol}")

        # ====================================================
        # DEBUG OUTPUT
        # ====================================================

        print(
            f"[VALIDATED] "
            f"{protocol} | "
            f"class={protocol_class} | "
            f"layer={stack_layer} | "
            f"encrypted={encrypted} | "
            f"authenticated={authenticated} | "
            f"integrity={integrity_protected} | "
            f"replay={replay_protected} | "
            f"safety_related={safety_related} | "
            f"safety_flow={safety_flow}"
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)

    print(f"PROTOCOL VALIDATION ERRORS: " f"{len(errors)}")

    print("=" * 60)

    return errors
