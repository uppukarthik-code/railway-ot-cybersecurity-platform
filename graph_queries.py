"""
graph_queries.py

Railway OT Cybersecurity Graph Analytics Engine.

PURPOSE:
- Neo4j graph analytics
- IEC 62443 segmentation analysis
- Attack-path traversal
- Cyber-physical risk traversal
- Blast-radius analysis
- Safety-security coupling analysis
- Zone trust analysis
- Purdue traversal analysis
- Risk heatmap generation
- Cytoscape overlay support
- Digital twin reasoning support

REQUIRES:
pip install neo4j python-dotenv

ENV:
NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv

import os
import json


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
# DRIVER
# ============================================================

driver = GraphDatabase.driver(

    URI,

    auth=(
        USERNAME,
        PASSWORD
    )
)


# ============================================================
# QUERY HELPER
# ============================================================

def run_query(
    query,
    parameters=None
):

    with driver.session() as session:

        result = session.run(

            query,

            parameters or {}
        )

        return [
            r.data()
            for r in result
        ]


# ============================================================
# ALL ASSETS
# ============================================================

def get_all_assets():

    query = """

    MATCH (a:Asset)

    RETURN

        a.id AS id,

        a.label AS label,

        a.zone AS zone,

        a.purdue_level AS purdue,

        a.cluster AS cluster,

        a.criticality AS criticality,

        a.risk_score AS risk_score

    ORDER BY a.zone

    """

    return run_query(query)


# ============================================================
# HIGH RISK ASSETS
# ============================================================

def get_high_risk_assets():

    query = """

    MATCH (a:Asset)

    WHERE

        a.risk_score >= 70

        OR

        a.attack_surface_score >= 70

    RETURN

        a.id AS id,

        a.label AS label,

        a.zone AS zone,

        a.criticality AS criticality,

        a.risk_score AS risk_score,

        a.attack_surface_score
            AS attack_surface

    ORDER BY risk_score DESC

    """

    return run_query(query)


# ============================================================
# SIL4 ASSETS
# ============================================================

def get_sil4_assets():

    query = """

    MATCH (a:Asset)

    WHERE
        a.criticality CONTAINS 'SIL4'

    RETURN

        a.id AS id,

        a.label AS label,

        a.zone AS zone,

        a.purdue_level AS purdue,

        a.risk_score AS risk_score

    """

    return run_query(query)


# ============================================================
# LOW TRUST ASSETS
# ============================================================

def get_low_trust_assets():

    query = """

    MATCH (a:Asset)

    WHERE
        a.trusted_zone = false

    RETURN

        a.id AS id,

        a.label AS label,

        a.zone AS zone,

        a.criticality AS criticality

    """

    return run_query(query)


# ============================================================
# CROSS ZONE CONNECTIONS
# ============================================================

def get_cross_zone_connections():

    query = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    WHERE
        r.cross_zone = true

    RETURN

        a.label AS source,

        b.label AS target,

        a.zone AS source_zone,

        b.zone AS target_zone,

        r.protocol AS protocol,

        r.encrypted AS encrypted,

        r.conduit_type AS conduit_type,

        r.risk_score AS risk_score

    ORDER BY risk_score DESC

    """

    return run_query(query)


# ============================================================
# UNENCRYPTED CONNECTIONS
# ============================================================

def get_unencrypted_connections():

    query = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    WHERE
        r.encrypted = false

    RETURN

        a.label AS source,

        b.label AS target,

        r.protocol AS protocol,

        r.cross_zone AS cross_zone,

        r.safety_related AS safety_related

    """

    return run_query(query)


# ============================================================
# SAFETY CONDUITS
# ============================================================

def get_safety_conduits():

    query = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    WHERE
        r.safety_related = true

    RETURN

        a.label AS source,

        b.label AS target,

        r.protocol AS protocol,

        r.encrypted AS encrypted,

        r.cross_zone AS cross_zone,

        r.risk_score AS risk_score

    """

    return run_query(query)


# ============================================================
# LOW TRUST SAFETY PATHS
# ============================================================

def get_low_trust_safety_paths():

    query = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    WHERE

        r.safety_related = true

        AND

        (
            a.trusted_zone = false
            OR
            b.trusted_zone = false
        )

    RETURN

        a.label AS source,

        b.label AS target,

        a.zone AS source_zone,

        b.zone AS target_zone,

        r.protocol AS protocol,

        r.encrypted AS encrypted,

        r.risk_score AS risk_score

    ORDER BY r.risk_score DESC

    """

    return run_query(query)


# ============================================================
# SAFETY + INTERNET EXPOSURE
# ============================================================

def get_exposed_safety_assets():

    query = """

    MATCH (a:Asset)

    WHERE

        a.safety_critical = true

        AND

        (
            a.internet_exposed = true

            OR

            a.remote_accessible = true

            OR

            a.wireless_exposed = true
        )

    RETURN

        a.label AS asset,

        a.zone AS zone,

        a.criticality AS criticality,

        a.internet_exposed AS internet,

        a.remote_accessible AS remote,

        a.wireless_exposed AS wireless,

        a.risk_score AS risk_score

    ORDER BY risk_score DESC

    """

    return run_query(query)


# ============================================================
# IEC62443 VIOLATIONS
# ============================================================

def get_iec62443_violations():

    violations = []

    # --------------------------------------------------------
    # UNENCRYPTED CROSS-ZONE
    # --------------------------------------------------------

    query_1 = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    WHERE

        r.cross_zone = true

        AND

        r.encrypted = false

    RETURN

        a.label AS source,

        b.label AS target,

        r.protocol AS protocol

    """

    for r in run_query(query_1):

        violations.append({

            "type":
                "UNENCRYPTED_CROSS_ZONE",

            "severity":
                "HIGH",

            "details":
                r
        })

    # --------------------------------------------------------
    # LOW TRUST SAFETY
    # --------------------------------------------------------

    query_2 = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    WHERE

        r.safety_related = true

        AND

        (
            a.trusted_zone = false
            OR
            b.trusted_zone = false
        )

    RETURN

        a.label AS source,

        b.label AS target,

        r.protocol AS protocol

    """

    for r in run_query(query_2):

        violations.append({

            "type":
                "LOW_TRUST_SAFETY_PATH",

            "severity":
                "CRITICAL",

            "details":
                r
        })

    # --------------------------------------------------------
    # SAFETY + REMOTE ACCESS
    # --------------------------------------------------------

    query_3 = """

    MATCH (a:Asset)

    WHERE

        a.safety_critical = true

        AND

        (
            a.remote_accessible = true

            OR

            a.internet_exposed = true
        )

    RETURN

        a.label AS asset,

        a.zone AS zone

    """

    for r in run_query(query_3):

        violations.append({

            "type":
                "REMOTE_EXPOSED_SAFETY_ASSET",

            "severity":
                "CRITICAL",

            "details":
                r
        })

    return violations


# ============================================================
# ATTACK PATHS
# ============================================================

def find_attack_paths(

    source_asset,

    target_asset,

    max_depth=8
):

    query = f"""

    MATCH path =

    shortestPath(

        (a:Asset {{id:$source}})
        -
        [:CONNECTS*..{max_depth}]
        ->
        (b:Asset {{id:$target}})

    )

    RETURN path

    """

    with driver.session() as session:

        result = session.run(

            query,

            {

                "source":
                    source_asset,

                "target":
                    target_asset
            }
        )

        paths = []

        for record in result:

            path = record["path"]

            nodes = []

            for node in path.nodes:

                nodes.append({

                    "id":
                        node.get("id"),

                    "label":
                        node.get("label"),

                    "zone":
                        node.get("zone"),

                    "criticality":
                        node.get("criticality"),

                    "risk_score":
                        node.get("risk_score")
                })

            paths.append(nodes)

        return paths


# ============================================================
# ATTACK PATH CANDIDATES
# ============================================================

def get_attack_path_candidates():

    query = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    WHERE

        r.attack_path_candidate = true

        OR

        r.remote_access = true

        OR

        r.vendor_access = true

    RETURN

        a.label AS source,

        b.label AS target,

        r.protocol AS protocol,

        r.risk_score AS risk_score,

        r.remote_access AS remote_access,

        r.vendor_access AS vendor_access

    ORDER BY r.risk_score DESC

    """

    return run_query(query)


# ============================================================
# BLAST RADIUS
# ============================================================

def get_blast_radius(
    asset_id,
    depth=3
):

    query = f"""

    MATCH path =

    (a:Asset {{id:$asset_id}})
    -
    [:CONNECTS*1..{depth}]
    ->
    (b:Asset)

    RETURN DISTINCT

        b.id AS id,

        b.label AS label,

        b.zone AS zone,

        b.criticality AS criticality,

        b.risk_score AS risk_score

    """

    return run_query(

        query,

        {

            "asset_id":
                asset_id
        }
    )


# ============================================================
# SEGMENTATION ANALYSIS
# ============================================================

def analyze_zone_segmentation():

    query = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    RETURN

        a.zone AS source_zone,

        b.zone AS target_zone,

        COUNT(*) AS total_connections,

        SUM(
            CASE
                WHEN r.cross_zone = true
                THEN 1
                ELSE 0
            END
        ) AS cross_zone_connections

    ORDER BY total_connections DESC

    """

    return run_query(query)


# ============================================================
# PURDUE ANALYSIS
# ============================================================

def analyze_purdue_levels():

    query = """

    MATCH (a:Asset)

    RETURN

        a.purdue_level AS purdue,

        COUNT(*) AS assets,

        AVG(a.risk_score) AS avg_risk

    ORDER BY purdue

    """

    return run_query(query)


# ============================================================
# RISK HEATMAP
# ============================================================

def generate_risk_heatmap():

    query = """

    MATCH (a:Asset)

    RETURN

        a.id AS id,

        a.label AS label,

        a.zone AS zone,

        a.risk_score AS risk_score,

        a.attack_surface_score
            AS attack_surface_score,

        a.exposure_score
            AS exposure_score

    ORDER BY risk_score DESC

    """

    return run_query(query)


# ============================================================
# GRAPH STATISTICS
# ============================================================

def graph_statistics():

    stats = {}

    # --------------------------------------------------------
    # ASSETS
    # --------------------------------------------------------

    q1 = """

    MATCH (a:Asset)

    RETURN COUNT(a) AS count

    """

    stats["assets"] = (
        run_query(q1)[0]["count"]
    )

    # --------------------------------------------------------
    # CONNECTIONS
    # --------------------------------------------------------

    q2 = """

    MATCH ()-[r:CONNECTS]->()

    RETURN COUNT(r) AS count

    """

    stats["connections"] = (
        run_query(q2)[0]["count"]
    )

    # --------------------------------------------------------
    # ZONES
    # --------------------------------------------------------

    q3 = """

    MATCH (z:Zone)

    RETURN COUNT(z) AS count

    """

    stats["zones"] = (
        run_query(q3)[0]["count"]
    )

    # --------------------------------------------------------
    # SAFETY CONDUITS
    # --------------------------------------------------------

    q4 = """

    MATCH ()-[r:CONNECTS]->()

    WHERE r.safety_related = true

    RETURN COUNT(r) AS count

    """

    stats["safety_conduits"] = (
        run_query(q4)[0]["count"]
    )

    # --------------------------------------------------------
    # HIGH RISK ASSETS
    # --------------------------------------------------------

    q5 = """

    MATCH (a:Asset)

    WHERE a.risk_score >= 70

    RETURN COUNT(a) AS count

    """

    stats["high_risk_assets"] = (
        run_query(q5)[0]["count"]
    )

    return stats


# ============================================================
# EXPORT JSON
# ============================================================

def export_json(
    data,
    output_file
):

    with open(

        output_file,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            data,

            f,

            indent=2
        )

    print(
        f"[OK] Exported: "
        f"{output_file}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n==============================")
    print("GRAPH STATISTICS")
    print("==============================")

    stats = graph_statistics()

    print(
        json.dumps(
            stats,
            indent=2
        )
    )

    print("\n==============================")
    print("IEC62443 VIOLATIONS")
    print("==============================")

    violations = (
        get_iec62443_violations()
    )

    print(
        json.dumps(
            violations,
            indent=2
        )
    )

    export_json(

        violations,

        "outputs/iec62443_violations.json"
    )

    print("\n==============================")
    print("LOW TRUST SAFETY PATHS")
    print("==============================")

    low_trust = (
        get_low_trust_safety_paths()
    )

    print(
        json.dumps(
            low_trust,
            indent=2
        )
    )

    export_json(

        low_trust,

        "outputs/low_trust_safety_paths.json"
    )

    print("\n==============================")
    print("UNENCRYPTED CONNECTIONS")
    print("==============================")

    unencrypted = (
        get_unencrypted_connections()
    )

    print(
        json.dumps(
            unencrypted,
            indent=2
        )
    )

    export_json(

        unencrypted,

        "outputs/unencrypted_connections.json"
    )

    print("\n==============================")
    print("HIGH RISK ASSETS")
    print("==============================")

    high_risk = (
        get_high_risk_assets()
    )

    print(
        json.dumps(
            high_risk,
            indent=2
        )
    )

    export_json(

        high_risk,

        "outputs/high_risk_assets.json"
    )

    print("\n==============================")
    print("DONE")
    print("==============================")

    driver.close()