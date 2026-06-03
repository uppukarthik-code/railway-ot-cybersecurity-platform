"""
schema_validator.py

Canonical topology schema enforcement.

RESPONSIBILITIES
----------------
- structural completeness
- default field population
- datatype stabilization
- collection initialization

DOES NOT
--------
- classify
- infer security
- infer conduits
- infer Purdue
- validate policy
"""

from copy import deepcopy

# ============================================================
# ROOT DEFAULTS
# ============================================================

ROOT_DEFAULTS = {
    "topology_id": "",
    "name": "Railway OT Topology",
    "generator_version": "1.0.0",
    "pipeline_stage": "normalized",
    "pipeline_history": [],
    "standards": [
        "IEC62443",
        "EN50126",
        "EN50129",
        "EN50159",
    ],
    "nodes": [],
    "connections": [],
    "conduits": [],
    "clusters": [],
}

# ============================================================
# NODE DEFAULTS
# ============================================================

NODE_DEFAULTS = {
    "normalized": False,
    "classified": False,
    "validated": False,
    "id": "",
    "label": "",
    "type": "unknown",
    "zone": "unknown_zone",
    "purdue_level": "Unknown",
    "vendor": "",
    "model": "",
    "firmware_version": "",
    "operating_system": "",
    "notes": "",
    "redundant": False,
    "safety_critical": False,
    "externally_hosted": False,
    "detached_domain": False,
    "protocol_stack": [],
    "mitre_techniques": [],
    "exposure_vectors": [],
    "sources": {},
}

# ============================================================
# CONNECTION DEFAULTS
# ============================================================

CONNECTION_DEFAULTS = {
    "normalized": False,
    "classified": False,
    "validated": False,
    "id": "",
    "source": "",
    "target": "",
    "protocol": "UNKNOWN",
    "transport": "unknown",
    "bearer": "unknown",
    "media": "UNKNOWN",
    "physical_path": "",
    "notes": "",
    "encrypted": False,
    "authenticated": False,
    "integrity_protected": False,
    "replay_protected": False,
    "wireless": False,
    "open_transmission": False,
    "safety_related": False,
    "cross_zone": False,
    "cross_trust_boundary": False,
    "detached_conduit": False,
    "sources": {},
}

# ============================================================
# CONDUIT DEFAULTS
# ============================================================

CONDUIT_DEFAULTS = {
    "id": "",
    "conduit_type": "unknown_conduit",
    "source_zone": "",
    "target_zone": "",
    "logical": False,
    "cross_zone": False,
    "safety_related": False,
    "requires_integrity": False,
    "requires_authentication": False,
    "requires_replay_protection": False,
    "requires_encryption": False,
    "requires_monitoring": False,
}

# ============================================================
# CLUSTER DEFAULTS
# ============================================================

CLUSTER_DEFAULTS = {
    "name": "General",
    "nodes": [],
    "zone": "",
    "purdue_level": "",
}

# ============================================================
# INTERNAL
# ============================================================


def apply_defaults(
    obj: dict,
    defaults: dict,
) -> dict:

    result = deepcopy(defaults)

    if isinstance(obj, dict):
        result.update(obj)

    return result


# ============================================================
# MAIN
# ============================================================


def ensure_topology_schema(
    topology: dict,
) -> dict:

    if not isinstance(topology, dict):
        topology = {}

    # ========================================================
    # ROOT
    # ========================================================

    topology = apply_defaults(
        topology,
        ROOT_DEFAULTS,
    )

    # ========================================================
    # NODES
    # ========================================================

    normalized_nodes = []

    for node in topology["nodes"]:

        if not isinstance(node, dict):
            continue

        normalized_nodes.append(
            apply_defaults(
                node,
                NODE_DEFAULTS,
            )
        )

    topology["nodes"] = normalized_nodes

    # ========================================================
    # CONNECTIONS
    # ========================================================

    normalized_connections = []

    for conn in topology["connections"]:

        if not isinstance(conn, dict):
            continue

        normalized_connections.append(
            apply_defaults(
                conn,
                CONNECTION_DEFAULTS,
            )
        )

    topology["connections"] = normalized_connections

    # ========================================================
    # CONDUITS
    # ========================================================

    normalized_conduits = []

    for conduit in topology["conduits"]:

        if not isinstance(conduit, dict):
            continue

        normalized_conduits.append(
            apply_defaults(
                conduit,
                CONDUIT_DEFAULTS,
            )
        )

    topology["conduits"] = normalized_conduits

    # ========================================================
    # CLUSTERS
    # ========================================================

    normalized_clusters = []

    for cluster in topology["clusters"]:

        if not isinstance(cluster, dict):
            continue

        normalized_clusters.append(
            apply_defaults(
                cluster,
                CLUSTER_DEFAULTS,
            )
        )

    topology["clusters"] = normalized_clusters

    return topology
