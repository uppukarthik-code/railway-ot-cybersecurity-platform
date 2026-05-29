"""
classifier.py

FINAL HARDENED CLASSIFIER

IEC62443 + EN50126 + EN50129 + EN50159 + Kavach

DESIGN PRINCIPLES
-----------------
ontology.py      -> canonical semantics
railway_rules.py -> governance/policy
aliases.py       -> normalization authority

Classifier responsibilities ONLY:
- semantic enrichment
- topology relationship enrichment
- lightweight semantic annotation

NO:
- policy enforcement
- security requirement inference
- rendering logic
- normalization
- validation
- risk scoring
- conduit policy inference
"""

import logging

from ontology import (
    ASSET_ONTOLOGY,
    PROTOCOL_ONTOLOGY,
    ZONE_ONTOLOGY,
    PURDUE_LEVEL_DESCRIPTIONS,
    DETACHED_PURDUE_DOMAINS,
    UNKNOWN_NODE,
    UNKNOWN_ZONE,
    UNKNOWN_PROTOCOL,
    UNKNOWN_PURDUE,
    UNKNOWN_SAFETY_DOMAIN,
    TRUSTED_ZONES,
    LOW_TRUST_ZONES,
    EXTERNAL_ZONES,
    get_asset_ontology,
    get_protocol_ontology,
)

from aliases import (
    normalize_node_type,
    normalize_protocol,
)

logger = logging.getLogger(__name__)

# ============================================================
# HELPERS
# ============================================================


def infer_trusted_zone(
    zone: str,
) -> bool:

    return zone in TRUSTED_ZONES


def infer_trust_domain(
    zone: str,
) -> str:

    if zone in LOW_TRUST_ZONES:
        return "external"

    if zone == "onboard":
        return "mobile"

    return "railway_trusted"


# ============================================================
# ZONE ENRICHMENT
# ============================================================


def enrich_zone_from_ontology(
    node: dict,
    ontology: dict,
) -> str:

    existing_zone = node.get(
        "zone",
        UNKNOWN_ZONE,
    )

    if existing_zone != UNKNOWN_ZONE and existing_zone in ZONE_ONTOLOGY:

        return existing_zone

    primary_zone = ontology.get(
        "zone",
    )

    if primary_zone:

        return primary_zone

    allowed_zones = ontology.get(
        "allowed_zones",
        [],
    )

    if allowed_zones:

        return allowed_zones[0]

    return UNKNOWN_ZONE


# ============================================================
# NODE CLASSIFICATION
# ============================================================


def classify_node(
    node: dict,
) -> dict:

    if node.get(
        "classified",
        False,
    ):

        return node

    raw_type = str(
        node.get(
            "type",
            UNKNOWN_NODE,
        )
    )

    label = str(
        node.get(
            "label",
            "",
        )
    )

    # ========================================================
    # TYPE
    # ========================================================

    node_type = normalize_node_type(
        raw_type,
    )

    if node_type not in ASSET_ONTOLOGY:

        logger.warning(
            "Invalid node type: %s",
            node_type,
        )

        node_type = UNKNOWN_NODE

    ontology = get_asset_ontology(
        node_type,
    )

    # ========================================================
    # ZONE
    # ========================================================

    existing_zone = node.get(
        "zone",
        UNKNOWN_ZONE,
    )

    if existing_zone == UNKNOWN_ZONE or existing_zone not in ZONE_ONTOLOGY:

        node["zone"] = enrich_zone_from_ontology(
            node,
            ontology,
        )

    zone = node.get(
        "zone",
        UNKNOWN_ZONE,
    )

    # ========================================================
    # PURDUE
    # ========================================================

    existing_purdue = node.get(
        "purdue_level",
        UNKNOWN_PURDUE,
    )

    if existing_purdue == UNKNOWN_PURDUE:

        node["purdue_level"] = ontology.get(
            "purdue",
            UNKNOWN_PURDUE,
        )

    purdue_level = node.get(
        "purdue_level",
        UNKNOWN_PURDUE,
    )

    # ========================================================
    # DETACHED DOMAINS
    # ========================================================

    detached_domain = purdue_level in DETACHED_PURDUE_DOMAINS

    # ========================================================
    # TRUST
    # ========================================================

    is_trusted_zone = infer_trusted_zone(
        zone,
    )

    trust_domain = infer_trust_domain(
        zone,
    )

    # ========================================================
    # SAFETY
    # ========================================================

    safety_critical = ontology.get(
        "safety_critical",
        False,
    )

    safety_domain = ontology.get(
        "safety_domain",
        UNKNOWN_SAFETY_DOMAIN,
    )

    # ========================================================
    # ENRICHMENT
    # ========================================================

    node["raw_type"] = raw_type

    node["normalized_type"] = node_type

    node["type"] = node_type

    # --------------------------------------------------------
    # Trust
    # --------------------------------------------------------

    node["is_trusted_zone"] = is_trusted_zone

    node["trust_domain"] = trust_domain

    # --------------------------------------------------------
    # Purdue metadata
    # --------------------------------------------------------

    node["purdue_description"] = PURDUE_LEVEL_DESCRIPTIONS.get(
        purdue_level,
        purdue_level,
    )

    node["detached_domain"] = detached_domain

    # --------------------------------------------------------
    # Safety
    # --------------------------------------------------------

    node["safety_critical"] = safety_critical

    node["safety_domain"] = safety_domain

    # --------------------------------------------------------
    # Zone semantics
    # --------------------------------------------------------

    node["external_zone"] = zone in EXTERNAL_ZONES

    # --------------------------------------------------------
    # Ontology semantics
    # --------------------------------------------------------

    node["engineering_access"] = ontology.get(
        "engineering_access",
        False,
    )

    node["logic_download_capable"] = ontology.get(
        "logic_download_capable",
        False,
    )

    node["configuration_change_capable"] = ontology.get(
        "configuration_change_capable",
        False,
    )

    node["radio_exposed"] = ontology.get(
        "radio_exposed",
        False,
    )

    node["mobile_asset"] = ontology.get(
        "mobile_asset",
        False,
    )

    node["safety_boundary"] = ontology.get(
        "safety_boundary",
        False,
    )

    # --------------------------------------------------------
    # Pipeline
    # --------------------------------------------------------

    node["classified"] = True

    logger.info(
        "[CLASSIFIED] %s -> %s | %s | %s",
        label,
        node_type,
        zone,
        purdue_level,
    )

    return node


# ============================================================
# CONNECTION CLASSIFICATION
# ============================================================


def classify_connection(
    conn: dict,
    node_lookup: dict,
) -> dict:

    if conn.get(
        "classified",
        False,
    ):

        return conn

    source = node_lookup.get(conn.get("source"))

    target = node_lookup.get(conn.get("target"))

    if not source or not target:

        return conn

    # ========================================================
    # ZONES
    # ========================================================

    source_zone = source.get(
        "zone",
        UNKNOWN_ZONE,
    )

    target_zone = target.get(
        "zone",
        UNKNOWN_ZONE,
    )

    # ========================================================
    # PROTOCOL
    # ========================================================

    protocol = normalize_protocol(conn.get("protocol"))

    conn["protocol"] = protocol

    conn["protocol_valid"] = (
        protocol in PROTOCOL_ONTOLOGY and protocol != UNKNOWN_PROTOCOL
    )

    protocol_meta = get_protocol_ontology(
        protocol,
    )

    # ========================================================
    # RELATIONSHIPS
    # ========================================================

    cross_zone = source_zone != target_zone

    cross_trust_domain = source.get("trust_domain") != target.get("trust_domain")

    trusted = source.get("is_trusted_zone", False) and target.get(
        "is_trusted_zone", False
    )

    # ========================================================
    # SAFETY
    # ========================================================

    safety_related = protocol_meta.get(
        "safety_related",
        False,
    )

    safety_domain = protocol_meta.get(
        "safety_domain",
        UNKNOWN_SAFETY_DOMAIN,
    )

    # ========================================================
    # OPEN TRANSMISSION
    # ========================================================

    open_transmission = protocol_meta.get(
        "open_transmission",
        False,
    )

    # ========================================================
    # RADIO / WIRELESS
    # ========================================================

    wireless = protocol_meta.get(
        "wireless_capable",
        False,
    )

    radio_related = (
        source_zone == "radio_access" or target_zone == "radio_access" or wireless
    )

    # ========================================================
    # TELECOM
    # ========================================================

    telecom_related = source_zone in {
        "telecom_core",
        "radio_access",
    } or target_zone in {
        "telecom_core",
        "radio_access",
    }

    # ========================================================
    # ENGINEERING
    # ========================================================

    engineering_access = source.get(
        "engineering_access",
        False,
    ) or target.get(
        "engineering_access",
        False,
    )

    # ========================================================
    # ENRICHMENT
    # ========================================================

    conn["cross_zone"] = cross_zone

    conn["cross_trust_domain"] = cross_trust_domain

    conn["trusted"] = trusted

    conn["safety_related"] = safety_related

    conn["safety_domain"] = safety_domain

    conn["open_transmission"] = open_transmission

    conn["wireless"] = wireless

    conn["telecom_related"] = telecom_related

    conn["radio_related"] = radio_related

    conn["engineering_access"] = engineering_access

    conn["classified"] = True

    return conn


# ============================================================
# TOPOLOGY CLASSIFICATION
# ============================================================


def classify_topology(
    topology: dict,
) -> dict:

    nodes = topology.get(
        "nodes",
        [],
    )

    for idx, node in enumerate(nodes):

        nodes[idx] = classify_node(
            node,
        )

    node_lookup = {n["id"]: n for n in nodes}

    connections = topology.get(
        "connections",
        [],
    )

    for idx, conn in enumerate(connections):

        connections[idx] = classify_connection(
            conn,
            node_lookup,
        )

    topology["nodes"] = nodes

    topology["connections"] = connections

    return topology
