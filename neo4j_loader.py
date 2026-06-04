"""
neo4j_loader.py

Railway OT topology → Neo4j loader.

DESIGN PRINCIPLES:
- railway_rules.py remains source of truth
- ontology.py remains semantic authority
- Neo4j stores evaluated semantic graph
- No duplicated policy logic in Neo4j

Stores:
- Assets
- Zones
- Purdue hierarchy
- Conduits
- Security metadata
- Safety metadata
- Attack surface metadata
- Cyber-physical risk metadata

Supports:
- Attack path analysis
- IEC62443 traversal
- Risk overlays
- Graph diffing
- Digital twin visualization
- Blast radius analysis
- Cyber-informed safety analysis
"""

import json
import os

from neo4j import GraphDatabase

from classifier import classify_topology
from validator import validate
from risk_engine import analyze_risk
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

URI = os.getenv(
    "NEO4J_URI"
)

USERNAME = os.getenv(
    "NEO4J_USERNAME"
)

PASSWORD = os.getenv(
    "NEO4J_PASSWORD"
)



# ============================================================
# NEO4J CONFIG
# ============================================================

NEO4J_URI = URI

NEO4J_USER = USERNAME

NEO4J_PASSWORD = PASSWORD


# ============================================================
# DRIVER
# ============================================================

driver = GraphDatabase.driver(

    NEO4J_URI,

    auth=(
        NEO4J_USER,
        NEO4J_PASSWORD
    )
)


# ============================================================
# LOAD TOPOLOGY JSON
# ============================================================

def load_topology_json(
    path: str
) -> dict:

    with open(
        path,
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# CLEAR DATABASE
# ============================================================

def clear_database():

    with driver.session() as session:

        session.run(
            """
            MATCH (n)
            DETACH DELETE n
            """
        )

    print(
        "[OK] Neo4j database cleared."
    )


# ============================================================
# CONSTRAINTS
# ============================================================

def create_constraints():

    queries = [

        """
        CREATE CONSTRAINT asset_id_unique
        IF NOT EXISTS
        FOR (a:Asset)
        REQUIRE a.id IS UNIQUE
        """,

        """
        CREATE CONSTRAINT zone_name_unique
        IF NOT EXISTS
        FOR (z:Zone)
        REQUIRE z.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT purdue_name_unique
        IF NOT EXISTS
        FOR (p:PurdueLevel)
        REQUIRE p.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT cluster_name_unique
        IF NOT EXISTS
        FOR (c:Cluster)
        REQUIRE c.name IS UNIQUE
        """
    ]

    with driver.session() as session:

        for query in queries:

            session.run(query)

    print(
        "[OK] Constraints created."
    )


# ============================================================
# INDEXES
# ============================================================

def create_indexes():

    queries = [

        """
        CREATE INDEX asset_zone_index
        IF NOT EXISTS
        FOR (a:Asset)
        ON (a.zone)
        """,

        """
        CREATE INDEX asset_type_index
        IF NOT EXISTS
        FOR (a:Asset)
        ON (a.type)
        """,

        """
        CREATE INDEX asset_criticality_index
        IF NOT EXISTS
        FOR (a:Asset)
        ON (a.criticality)
        """,

        """
        CREATE INDEX asset_purdue_index
        IF NOT EXISTS
        FOR (a:Asset)
        ON (a.purdue_level)
        """,

        """
        CREATE INDEX asset_cluster_index
        IF NOT EXISTS
        FOR (a:Asset)
        ON (a.cluster)
        """,

        """
        CREATE INDEX asset_risk_index
        IF NOT EXISTS
        FOR (a:Asset)
        ON (a.risk_score)
        """
    ]

    with driver.session() as session:

        for query in queries:

            session.run(query)

    print(
        "[OK] Indexes created."
    )


# ============================================================
# CREATE ZONES
# ============================================================

def create_zones(
    topology: dict
):

    zones = {

        node.get(
            "zone",
            "unknown"
        )

        for node in topology.get(
            "nodes",
            []
        )
    }

    with driver.session() as session:

        for zone in zones:

            session.run(

                """
                MERGE (z:Zone {
                    name: $name
                })
                """,

                {
                    "name": zone
                }
            )

    print(
        f"[OK] Zones created: {len(zones)}"
    )


# ============================================================
# CREATE PURDUE LEVELS
# ============================================================

def create_purdue_levels(
    topology: dict
):

    levels = {

        node.get(
            "purdue_level",
            "Unknown"
        )

        for node in topology.get(
            "nodes",
            []
        )
    }

    with driver.session() as session:

        for level in levels:

            session.run(

                """
                MERGE (p:PurdueLevel {
                    name: $name
                })
                """,

                {
                    "name": level
                }
            )

    print(
        f"[OK] Purdue levels created: "
        f"{len(levels)}"
    )


# ============================================================
# CREATE CLUSTERS
# ============================================================

def create_clusters(
    topology: dict
):

    clusters = {

        node.get(
            "cluster",
            "General"
        )

        for node in topology.get(
            "nodes",
            []
        )
    }

    with driver.session() as session:

        for cluster in clusters:

            session.run(

                """
                MERGE (c:Cluster {
                    name: $name
                })
                """,

                {
                    "name": cluster
                }
            )

    print(
        f"[OK] Clusters created: "
        f"{len(clusters)}"
    )


# ============================================================
# CREATE ASSETS
# ============================================================

def create_assets(
    topology: dict
):

    nodes = topology.get(
        "nodes",
        []
    )

    query = """

    CREATE (a:Asset {

        id: $id,

        label: $label,

        type: $type,

        zone: $zone,

        purdue_level: $purdue_level,

        purdue_group: $purdue_group,

        functional_domain:
            $functional_domain,

        functional_role:
            $functional_role,

        functional_cell:
            $functional_cell,

        cluster:
            $cluster,

        criticality:
            $criticality,

        security_level:
            $security_level,

        security_level_target:
            $security_level_target,

        is_trusted_zone:
            $is_trusted_zone,

        safety_critical:
            $safety_critical,

        functional_safety_level:
            $functional_safety_level,

        security_safety_coupled:
            $security_safety_coupled,

        redundant:
            $redundant,

        rolling_stock_asset:
            $rolling_stock_asset,

        externally_hosted:
            $externally_hosted,

        internet_exposed:
            $internet_exposed,

        remote_accessible:
            $remote_accessible,

        wireless_exposed:
            $wireless_exposed,

        maintenance_exposed:
            $maintenance_exposed,

        portable_media_exposed:
            $portable_media_exposed,

        supports_logic_download:
            $supports_logic_download,

        offline_engineering_asset:
            $offline_engineering_asset,

        portable_media_risk:
            $portable_media_risk,

        attack_surface_score:
            $attack_surface_score,

        blast_radius_score:
            $blast_radius_score,

        exposure_score:
            $exposure_score,

        risk_score:
            $risk_score,

        vendor:
            $vendor,

        model:
            $model,

        firmware_version:
            $firmware_version,

        operating_system:
            $operating_system,

        description:
            $description,

        notes:
            $notes
    })

    """

    with driver.session() as session:

        for node in nodes:

            session.run(

                query,

                {

                    "id":
                        node.get("id"),

                    "label":
                        node.get("label"),

                    "type":
                        node.get("type"),

                    "zone":
                        node.get("zone"),

                    "purdue_level":
                        node.get(
                            "purdue_level"
                        ),

                    "purdue_group":
                        node.get(
                            "purdue_group"
                        ),

                    "functional_domain":
                        node.get(
                            "functional_domain"
                        ),

                    "functional_role":
                        node.get(
                            "functional_role"
                        ),

                    "functional_cell":
                        node.get(
                            "functional_cell"
                        ),

                    "cluster":
                        node.get(
                            "cluster"
                        ),

                    "criticality":
                        node.get(
                            "criticality"
                        ),

                    "security_level":
                        node.get(
                            "security_level"
                        ),

                    "security_level_target":
                        node.get(
                            "security_level_target"
                        ),

                    "is_trusted_zone":
                        node.get(
                            "is_trusted_zone"
                        ),

                    "safety_critical":
                        node.get(
                            "safety_critical"
                        ),

                    "functional_safety_level":
                        node.get(
                            "functional_safety_level"
                        ),

                    "security_safety_coupled":
                        node.get(
                            "security_safety_coupled"
                        ),

                    "redundant":
                        node.get(
                            "redundant"
                        ),

                    "rolling_stock_asset":
                        node.get(
                            "rolling_stock_asset"
                        ),

                    "externally_hosted":
                        node.get(
                            "externally_hosted"
                        ),

                    "internet_exposed":
                        node.get(
                            "internet_exposed"
                        ),

                    "remote_accessible":
                        node.get(
                            "remote_accessible"
                        ),

                    "wireless_exposed":
                        node.get(
                            "wireless_exposed"
                        ),

                    "maintenance_exposed":
                        node.get(
                            "maintenance_exposed"
                        ),

                    "portable_media_exposed":
                        node.get(
                            "portable_media_exposed"
                        ),

                    "supports_logic_download":
                        node.get(
                            "supports_logic_download"
                        ),

                    "offline_engineering_asset":
                        node.get(
                            "offline_engineering_asset"
                        ),

                    "portable_media_risk":
                        node.get(
                            "portable_media_risk"
                        ),

                    "attack_surface_score":
                        node.get(
                            "attack_surface_score",
                            0.0
                        ),

                    "blast_radius_score":
                        node.get(
                            "blast_radius_score",
                            0.0
                        ),

                    "exposure_score":
                        node.get(
                            "exposure_score",
                            0.0
                        ),

                    "risk_score":
                        node.get(
                            "risk_score",
                            0.0
                        ),

                    "vendor":
                        node.get(
                            "vendor"
                        ),

                    "model":
                        node.get(
                            "model"
                        ),

                    "firmware_version":
                        node.get(
                            "firmware_version"
                        ),

                    "operating_system":
                        node.get(
                            "operating_system"
                        ),

                    "description":
                        node.get(
                            "description"
                        ),

                    "notes":
                        node.get(
                            "notes"
                        )
                }
            )

    print(
        f"[OK] Assets created: "
        f"{len(nodes)}"
    )


# ============================================================
# LINK ASSETS
# ============================================================

def link_assets_to_zones():

    with driver.session() as session:

        session.run(

            """
            MATCH (a:Asset)
            MATCH (z:Zone {
                name: a.zone
            })

            MERGE (a)-[:IN_ZONE]->(z)
            """
        )

    print(
        "[OK] Asset-zone links created."
    )


def link_assets_to_purdue():

    with driver.session() as session:

        session.run(

            """
            MATCH (a:Asset)
            MATCH (p:PurdueLevel {
                name: a.purdue_level
            })

            MERGE (a)-[:IN_PURDUE]->(p)
            """
        )

    print(
        "[OK] Asset-Purdue links created."
    )


def link_assets_to_clusters():

    with driver.session() as session:

        session.run(

            """
            MATCH (a:Asset)
            MATCH (c:Cluster {
                name: a.cluster
            })

            MERGE (a)-[:IN_CLUSTER]->(c)
            """
        )

    print(
        "[OK] Asset-cluster links created."
    )


# ============================================================
# CREATE CONNECTIONS
# ============================================================

def create_connections(
    topology: dict
):

    connections = topology.get(
        "connections",
        []
    )

    query = """

    MATCH (a:Asset {
        id: $source
    })

    MATCH (b:Asset {
        id: $target
    })

    CREATE (a)-[:CONNECTS {

        id:
            $id,

        protocol:
            $protocol,

        encrypted:
            $encrypted,

        authenticated:
            $authenticated,

        integrity_protection:
            $integrity_protection,

        safety_related:
            $safety_related,

        trusted:
            $trusted,

        conduit_type:
            $conduit_type,

        cross_zone:
            $cross_zone,

        trust_boundary_crossing:
            $trust_boundary_crossing,

        firewall_traversal:
            $firewall_traversal,

        remote_access:
            $remote_access,

        vendor_access:
            $vendor_access,

        wireless:
            $wireless,

        attack_path_candidate:
            $attack_path_candidate,

        lateral_movement_risk:
            $lateral_movement_risk,

        blast_radius_weight:
            $blast_radius_weight,

        risk_score:
            $risk_score,

        railway_safety_conduit:
            $railway_safety_conduit,

        management_traffic:
            $management_traffic,

        deterministic_network:
            $deterministic_network,

        qos_enabled:
            $qos_enabled,

        notes:
            $notes

    }]->(b)

    """

    with driver.session() as session:

        for conn in connections:

            session.run(

                query,

                {

                    "id":
                        conn.get("id"),

                    "source":
                        conn.get(
                            "source"
                        ),

                    "target":
                        conn.get(
                            "target"
                        ),

                    "protocol":
                        conn.get(
                            "protocol"
                        ),

                    "encrypted":
                        conn.get(
                            "encrypted"
                        ),

                    "authenticated":
                        conn.get(
                            "authenticated"
                        ),

                    "integrity_protection":
                        conn.get(
                            "integrity_protection"
                        ),

                    "safety_related":
                        conn.get(
                            "safety_related"
                        ),

                    "trusted":
                        conn.get(
                            "trusted"
                        ),

                    "conduit_type":
                        conn.get(
                            "conduit_type"
                        ),

                    "cross_zone":
                        conn.get(
                            "cross_zone"
                        ),

                    "trust_boundary_crossing":
                        conn.get(
                            "trust_boundary_crossing"
                        ),

                    "firewall_traversal":
                        conn.get(
                            "firewall_traversal"
                        ),

                    "remote_access":
                        conn.get(
                            "remote_access"
                        ),

                    "vendor_access":
                        conn.get(
                            "vendor_access"
                        ),

                    "wireless":
                        conn.get(
                            "wireless"
                        ),

                    "attack_path_candidate":
                        conn.get(
                            "attack_path_candidate"
                        ),

                    "lateral_movement_risk":
                        conn.get(
                            "lateral_movement_risk"
                        ),

                    "blast_radius_weight":
                        conn.get(
                            "blast_radius_weight",
                            0.0
                        ),

                    "risk_score":
                        conn.get(
                            "risk_score",
                            0.0
                        ),

                    "railway_safety_conduit":
                        conn.get(
                            "railway_safety_conduit"
                        ),

                    "management_traffic":
                        conn.get(
                            "management_traffic"
                        ),

                    "deterministic_network":
                        conn.get(
                            "deterministic_network"
                        ),

                    "qos_enabled":
                        conn.get(
                            "qos_enabled"
                        ),

                    "notes":
                        conn.get(
                            "notes"
                        )
                }
            )

    print(
        f"[OK] Connections created: "
        f"{len(connections)}"
    )


# ============================================================
# CREATE PURDUE HIERARCHY
# ============================================================

def create_purdue_hierarchy():

    hierarchy = [

        ("L5 Enterprise", "L4 Business"),

        ("L4 Business", "L3.5 Security"),

        ("L3.5 Security", "L3 Operations"),

        ("L3 Operations", "L2 Telecom"),

        ("L2 Telecom", "L2 Station Control"),

        ("L2 Station Control", "L2 Interlocking"),

        ("L2 Interlocking", "L1 Interlocking"),

        ("L1 Interlocking", "L0 Field"),

        ("L0 Field", "Onboard")
    ]

    with driver.session() as session:

        for upper, lower in hierarchy:

            session.run(

                """
                MATCH (a:PurdueLevel {
                    name: $upper
                })

                MATCH (b:PurdueLevel {
                    name: $lower
                })

                MERGE (a)-[:TRUST_PATH]->(b)
                """,

                {

                    "upper": upper,

                    "lower": lower
                }
            )

    print(
        "[OK] Purdue hierarchy created."
    )


# ============================================================
# EXPORT PIPELINE
# ============================================================

def export_to_neo4j(
    topology_path: str
):

    print(
        "\n── Railway OT → Neo4j Export ──"
    )

    topology = load_topology_json(
        topology_path
    )

    print(
        f"[INFO] Nodes: "
        f"{len(topology['nodes'])}"
    )

    print(
        f"[INFO] Connections: "
        f"{len(topology['connections'])}"
    )

    # ========================================================
    # SEMANTIC ENRICHMENT
    # ========================================================

    topology = classify_topology(
        topology
    )

    findings = validate(
        topology
    )

    analyze_risk(
        topology
    )

    print(
        f"[INFO] Validation findings: "
        f"{len(findings)}"
    )

    # ========================================================
    # DATABASE
    # ========================================================

    clear_database()

    create_constraints()

    create_indexes()

    create_zones(
        topology
    )

    create_purdue_levels(
        topology
    )

    create_clusters(
        topology
    )

    create_assets(
        topology
    )

    link_assets_to_zones()

    link_assets_to_purdue()

    link_assets_to_clusters()

    create_connections(
        topology
    )

    create_purdue_hierarchy()

    print(
        "\n[OK] Neo4j export complete."
    )


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    export_to_neo4j(
        "outputs/kavach_topology.json"
    )

    driver.close()