"""
conduits.py

FINAL HARDENED CONDUIT SYNTHESIS ENGINE

IEC62443 + EN50159 + EN50126 + Railway OT + Kavach

DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- railway_rules.py = governance authority
- classifier.py = semantic enrichment authority
- security_enrichment.py = security policy authority
- aliases.py = normalization authority

RESPONSIBILITIES
----------------
- conduit synthesis
- topology relationship aggregation
- conduit semantic aggregation
- lightweight reporting entities

DOES NOT
---------
- infer trust
- infer safety
- infer security requirements
- generate policy
- generate capabilities
- duplicate semantic reasoning
"""

from ontology import (
    CONDUIT_ONTOLOGY,
    ENGINEERING_ACCESS_TYPES,
)

from railway_rules import (
    get_trust_boundary,
)

from aliases import (
    normalize_protocol,
)

# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_CONDUIT_CLASS = "generic"

# ============================================================
# BUILD CONDUITS
# ============================================================


def build_conduits(
    topology: dict,
) -> dict:

    node_lookup = {
        node["id"]: node
        for node in topology.get(
            "nodes",
            [],
        )
    }

    conduits = []

    seen = set()

    # ========================================================
    # CONNECTION ANALYSIS
    # ========================================================

    for idx, conn in enumerate(
        topology.get(
            "connections",
            [],
        )
    ):

        source_id = conn.get("source")

        target_id = conn.get("target")

        if not source_id or not target_id:

            continue

        source = node_lookup.get(source_id)

        target = node_lookup.get(target_id)

        if not source or not target:

            continue

        # ====================================================
        # ZONES
        # ====================================================

        source_zone = source.get(
            "zone",
            "operations",
        )

        target_zone = target.get(
            "zone",
            "operations",
        )

        # ====================================================
        # PURDUE
        # ====================================================

        source_level = source.get(
            "purdue_level",
            "L3 Operations",
        )

        target_level = target.get(
            "purdue_level",
            "L3 Operations",
        )

        # ====================================================
        # TYPES
        # ====================================================

        source_type = source.get(
            "type",
            "unknown",
        )

        target_type = target.get(
            "type",
            "unknown",
        )

        # ====================================================
        # PROTOCOL
        # ====================================================

        protocol = normalize_protocol(
            conn.get(
                "protocol",
                "UNKNOWN",
            )
        )

        # ====================================================
        # PHYSICAL SEMANTICS
        # ====================================================

        transport = conn.get(
            "transport",
            "unknown",
        )

        bearer = conn.get(
            "bearer",
            "unknown",
        )

        media = conn.get(
            "media",
            "unknown",
        )

        # ====================================================
        # DEDUPLICATION
        # ====================================================

        conduit_key = tuple(
            sorted(
                [
                    source_id,
                    target_id,
                ]
            )
        ) + (protocol,)

        if conduit_key in seen:

            continue

        seen.add(conduit_key)

        # ====================================================
        # RELATIONSHIPS
        # ====================================================

        cross_zone = source_zone != target_zone

        cross_purdue = source_level != target_level

        cross_trust_domain = source.get(
            "trust_domain",
        ) != target.get(
            "trust_domain",
        )

        trust_boundary = bool(
            get_trust_boundary(
                source_zone,
                target_zone,
            )
        )

        # ====================================================
        # SEMANTICS
        # ====================================================

        safety_related = conn.get(
            "safety_related",
            False,
        )

        radio_related = conn.get(
            "radio_related",
            False,
        )

        detached_conduit = conn.get(
            "detached_conduit",
            False,
        )

        # ====================================================
        # ENGINEERING ACCESS
        # ====================================================

        engineering_access = source.get(
            "engineering_access",
            False,
        ) or target.get(
            "engineering_access",
            False,
        )

        # ====================================================
        # CONDUIT CLASS
        # ====================================================

        conduit_class = conn.get(
            "conduit_class",
            DEFAULT_CONDUIT_CLASS,
        )

        # ====================================================
        # CONDUIT VALIDATION
        # ====================================================

        if conduit_class not in CONDUIT_ONTOLOGY:

            conduit_class = DEFAULT_CONDUIT_CLASS

        conduit_meta = CONDUIT_ONTOLOGY.get(
            conduit_class,
            {},
        )

        # ====================================================
        # STABLE CONDUIT ID
        # ====================================================

        safe_protocol = protocol.lower().replace(
            " ",
            "_",
        )

        conduit_id = f"conduit_" f"{source_id}_" f"{target_id}_" f"{safe_protocol}"

        # ====================================================
        # BUILD CONDUIT
        # ====================================================

        conduit = {
            # ------------------------------------------------
            # IDENTITY
            # ------------------------------------------------
            "id": conduit_id,
            "source": source_id,
            "target": target_id,
            # ------------------------------------------------
            # COMMUNICATION
            # ------------------------------------------------
            "protocol": protocol,
            "transport": transport,
            "bearer": bearer,
            "media": media,
            # ------------------------------------------------
            # ZONES
            # ------------------------------------------------
            "source_zone": source_zone,
            "target_zone": target_zone,
            # ------------------------------------------------
            # PURDUE
            # ------------------------------------------------
            "source_level": source_level,
            "target_level": target_level,
            # ------------------------------------------------
            # RELATIONSHIPS
            # ------------------------------------------------
            "cross_zone": cross_zone,
            "cross_purdue": cross_purdue,
            "cross_trust_domain": cross_trust_domain,
            "trust_boundary": trust_boundary,
            # ------------------------------------------------
            # SEMANTICS
            # ------------------------------------------------
            "safety_related": safety_related,
            "radio_related": radio_related,
            "engineering_access": engineering_access,
            "detached_conduit": detached_conduit,
            # ------------------------------------------------
            # CONDUIT
            # ------------------------------------------------
            "conduit_class": conduit_class,
            "conduit_description": conduit_meta.get(
                "description",
                "",
            ),
            # ------------------------------------------------
            # PROVENANCE
            # ------------------------------------------------
            "conduit_synthesized": True,
            "conduit_source": "conduit_engine",
        }

        conduits.append(conduit)

    topology["conduits"] = conduits

    return topology
