"""
clustering.py

FINAL HARDENED RAILWAY OT CLUSTERING ENGINE

IEC62443 + EN50126 + EN50129 + EN50159 + Kavach

DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- classifier.py = enrichment authority
- aliases.py = normalization authority

Clustering responsibilities ONLY:
- presentation grouping
- deterministic subsystem organization
- renderer-friendly grouping
- detached domain grouping

NO:
- semantic inference
- regex classification
- policy enforcement
- ontology duplication
- heuristic recovery
"""

from ontology import (
    DETACHED_PURDUE_DOMAINS,
)

# ============================================================
# CLUSTER ORDER
# ============================================================

CLUSTER_ORDER = [
    "Enterprise Services",
    "External Security Services",
    "Security Management",
    "Operations Management",
    "Maintenance Systems",
    "Telecom Network",
    "Radio Communication",
    "Interlocking Core",
    "Train Detection",
    "Field Equipment",
    "Onboard Systems",
    "Detached Domains",
    "General Systems",
]

# ============================================================
# CLUSTER COLORS
# ============================================================

CLUSTER_COLORS = {
    "Enterprise Services": "#d9e2f3",
    "External Security Services": "#c9daf8",
    "Security Management": "#ffe599",
    "Operations Management": "#bdd7ee",
    "Maintenance Systems": "#d9d9d9",
    "Telecom Network": "#a2c4c9",
    "Radio Communication": "#d9b3ff",
    "Interlocking Core": "#f4cccc",
    "Train Detection": "#d9ead3",
    "Field Equipment": "#b6d7a8",
    "Onboard Systems": "#d5a6bd",
    "Detached Domains": "#f6d7b0",
    "General Systems": "#eeeeee",
}

# ============================================================
# CLUSTER TOPOLOGY
# ============================================================


def cluster_topology(
    topology: dict,
) -> dict:
    """
    Build deterministic presentation clusters
    from already-classified topology metadata.
    """

    clusters = {}

    # ========================================================
    # PROCESS NODES
    # ========================================================

    for node in topology.get(
        "nodes",
        [],
    ):

        cluster_name = infer_cluster(node)

        node["cluster"] = cluster_name

        # ----------------------------------------------------
        # DETACHED RENDER ISOLATION
        #
        # Detached Purdue domains render inside an isolated
        # visual cluster, distinct from their primary cluster.
        # This is presentation grouping only (rendering safety
        # contract enforced by validate_rendering), NOT Purdue
        # or zone semantic assignment.
        # ----------------------------------------------------

        detached_cluster = infer_detached_cluster(node)

        if detached_cluster:

            node["detached_cluster"] = detached_cluster

        if cluster_name not in clusters:

            clusters[cluster_name] = {
                "name": cluster_name,
                "purdue_level": node.get(
                    "purdue_level",
                    "Unknown",
                ),
                "zone": node.get(
                    "zone",
                    "unknown",
                ),
                "color": CLUSTER_COLORS.get(
                    cluster_name,
                    "#eeeeee",
                ),
                "nodes": [],
            }

        clusters[cluster_name]["nodes"].append(node)

    # ========================================================
    # ORDER CLUSTERS
    # ========================================================

    ordered_clusters = []

    for cluster_name in CLUSTER_ORDER:

        if cluster_name in clusters:

            ordered_clusters.append(clusters[cluster_name])

    # ========================================================
    # APPEND REMAINING
    # ========================================================

    for cluster_name, cluster in clusters.items():

        if cluster_name not in CLUSTER_ORDER:

            ordered_clusters.append(cluster)

    topology["clusters"] = ordered_clusters

    return topology


# ============================================================
# CLUSTER INFERENCE
# ============================================================


def infer_cluster(
    node: dict,
) -> str:
    """
    Deterministic presentation clustering.

    Uses ONLY canonical classified metadata.
    """

    zone = node.get(
        "zone",
        "",
    )

    node_type = node.get(
        "type",
        "",
    )

    purdue = node.get(
        "purdue_level",
        "",
    )

    # ========================================================
    # DETACHED DOMAINS
    # ========================================================

    if purdue in DETACHED_PURDUE_DOMAINS:

        return "Detached Domains"

    # ========================================================
    # ENTERPRISE
    # ========================================================

    if zone == "enterprise_it":

        return "Enterprise Services"

    # ========================================================
    # IDMZ / EXTERNAL SECURITY
    # ========================================================

    if zone in {
        "idmz",
        "external_security",
    }:

        return "External Security Services"

    # ========================================================
    # SECURITY MANAGEMENT
    # ========================================================

    if zone == "security_management":

        return "Security Management"

    # ========================================================
    # MAINTENANCE
    # ========================================================

    if zone == "maintenance":

        return "Maintenance Systems"

    # ========================================================
    # OPERATIONS
    # ========================================================

    if zone == "operations":

        return "Operations Management"

    # ========================================================
    # TELECOM
    # ========================================================

    if zone == "telecom_core":

        return "Telecom Network"

    # ========================================================
    # RADIO
    # ========================================================

    if zone == "radio_access":

        return "Radio Communication"

    # ========================================================
    # INTERLOCKING
    # ========================================================

    if zone == "interlocking":

        return "Interlocking Core"

    # ========================================================
    # TRACKSIDE
    # ========================================================

    if zone == "trackside":

        return "Train Detection"

    # ========================================================
    # FIELD
    # ========================================================

    if zone == "field":

        return "Field Equipment"

    # ========================================================
    # ONBOARD
    # ========================================================

    if zone == "onboard":

        return "Onboard Systems"

    # ========================================================
    # TYPE-BASED FALLBACKS
    # ========================================================

    if node_type in {
        "axle_counter_head",
        "track_circuit",
        "axle_counter_evaluator",
    }:

        return "Train Detection"

    if node_type in {
        "point_machine_controller",
        "signal_controller",
        "trackside_rfid_tag",
    }:

        return "Field Equipment"

    # ========================================================
    # GENERIC FALLBACK
    # ========================================================

    return "General Systems"


# ============================================================
# DETACHED CLUSTER INFERENCE
# ============================================================


def infer_detached_cluster(
    node: dict,
) -> str:
    """
    Deterministic isolated cluster for detached render nodes.

    A node renders detached when its Purdue level is a detached
    domain, or when it lives in the external_security zone (the
    rendering safety contract enforced by validate_rendering).

    Returns an isolated cluster name derived from the detachment
    reason, guaranteed distinct from the node's primary cluster.
    Returns "" for nodes that are not detached.

    Uses ONLY canonical classified metadata. No semantic
    inference, no Purdue/zone reassignment.
    """

    purdue = node.get(
        "purdue_level",
        "",
    )

    zone = node.get(
        "zone",
        "",
    )

    if purdue in DETACHED_PURDUE_DOMAINS:

        return f"{purdue} Domain"

    if zone in DETACHED_PURDUE_DOMAINS:

        return f"{zone} Domain"

    return ""
