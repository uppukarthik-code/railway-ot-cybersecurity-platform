"""
attack_paths.py

Railway OT Cybersecurity Attack Path Engine.

PURPOSE:
- Cyber attack propagation modeling
- IEC 62443 traversal analysis
- Railway OT lateral movement analysis
- Safety escalation analysis
- Blast radius estimation
- Multi-stage intrusion modeling
- Purdue escalation analysis
- Vendor-access propagation analysis
- Remote-access attack analysis
- Digital twin cyber reasoning

REQUIRES:
pip install neo4j python-dotenv networkx
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv

import os
import json
import networkx as nx


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")


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
# PURDUE ORDER
# ============================================================

PURDUE_ORDER = {

    "L5 Enterprise": 5,
    "L4 Business": 4,
    "L3.5 Security": 3.5,
    "L3 Operations": 3,
    "L2 Telecom": 2.8,
    "L2 Station Control": 2.5,
    "L2 Interlocking": 2.2,
    "L1 Interlocking": 1,
    "L0 Field": 0,
    "Onboard": 0
}


# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph():

    G = nx.DiGraph()

    query = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    RETURN

        a.id AS source_id,
        a.label AS source_label,
        a.zone AS source_zone,
        a.cluster AS source_cluster,
        a.purdue_level AS source_purdue,
        a.criticality AS source_criticality,
        a.trusted_zone AS source_trusted,
        a.risk_score AS source_risk,
        a.internet_exposed AS source_internet,
        a.remote_accessible AS source_remote,

        b.id AS target_id,
        b.label AS target_label,
        b.zone AS target_zone,
        b.cluster AS target_cluster,
        b.purdue_level AS target_purdue,
        b.criticality AS target_criticality,
        b.trusted_zone AS target_trusted,
        b.risk_score AS target_risk,
        b.internet_exposed AS target_internet,
        b.remote_accessible AS target_remote,

        r.protocol AS protocol,
        r.encrypted AS encrypted,
        r.cross_zone AS cross_zone,
        r.safety_related AS safety_related,
        r.conduit_type AS conduit_type,
        r.remote_access AS remote_access,
        r.vendor_access AS vendor_access,
        r.risk_score AS edge_risk

    """

    with driver.session() as session:

        results = session.run(query)

        for r in results:

            # ------------------------------------------------
            # SOURCE NODE
            # ------------------------------------------------

            G.add_node(

                r["source_id"],

                label=
                    r["source_label"],

                zone=
                    r["source_zone"],

                cluster=
                    r["source_cluster"],

                purdue=
                    r["source_purdue"],

                criticality=
                    r["source_criticality"],

                trusted=
                    r["source_trusted"],

                risk_score=
                    r["source_risk"],

                internet_exposed=
                    r["source_internet"],

                remote_accessible=
                    r["source_remote"]
            )

            # ------------------------------------------------
            # TARGET NODE
            # ------------------------------------------------

            G.add_node(

                r["target_id"],

                label=
                    r["target_label"],

                zone=
                    r["target_zone"],

                cluster=
                    r["target_cluster"],

                purdue=
                    r["target_purdue"],

                criticality=
                    r["target_criticality"],

                trusted=
                    r["target_trusted"],

                risk_score=
                    r["target_risk"],

                internet_exposed=
                    r["target_internet"],

                remote_accessible=
                    r["target_remote"]
            )

            # ------------------------------------------------
            # EDGE
            # ------------------------------------------------

            G.add_edge(

                r["source_id"],

                r["target_id"],

                protocol=
                    r["protocol"],

                encrypted=
                    r["encrypted"],

                cross_zone=
                    r["cross_zone"],

                safety_related=
                    r["safety_related"],

                conduit_type=
                    r["conduit_type"],

                remote_access=
                    r["remote_access"],

                vendor_access=
                    r["vendor_access"],

                edge_risk=
                    r["edge_risk"]
            )

    return G


# ============================================================
# CLASSIFY RISK
# ============================================================

def classify_risk(score):

    if score >= 160:
        return "CRITICAL"

    if score >= 110:
        return "HIGH"

    if score >= 60:
        return "MEDIUM"

    return "LOW"


# ============================================================
# PATH RISK
# ============================================================

def calculate_path_risk(
    G,
    path
):

    score = 0

    findings = []

    traversed_zones = set()

    traversed_purdue = []

    # --------------------------------------------------------
    # NODE RISKS
    # --------------------------------------------------------

    for node_id in path:

        node = G.nodes[node_id]

        traversed_zones.add(
            node.get("zone")
        )

        traversed_purdue.append(
            node.get("purdue")
        )

        criticality = str(
            node.get(
                "criticality",
                ""
            )
        ).upper()

        # ----------------------------------------------------
        # SIL4
        # ----------------------------------------------------

        if "SIL4" in criticality:

            score += 50

            findings.append(
                "SIL4 asset traversal"
            )

        # ----------------------------------------------------
        # SIL3
        # ----------------------------------------------------

        elif "SIL3" in criticality:

            score += 30

            findings.append(
                "SIL3 asset traversal"
            )

        # ----------------------------------------------------
        # LOW TRUST
        # ----------------------------------------------------

        if not node.get(
            "trusted",
            False
        ):

            score += 20

            findings.append(
                "Low trust asset"
            )

        # ----------------------------------------------------
        # INTERNET
        # ----------------------------------------------------

        if node.get(
            "internet_exposed",
            False
        ):

            score += 35

            findings.append(
                "Internet exposed asset"
            )

        # ----------------------------------------------------
        # REMOTE
        # ----------------------------------------------------

        if node.get(
            "remote_accessible",
            False
        ):

            score += 25

            findings.append(
                "Remote accessible asset"
            )

    # --------------------------------------------------------
    # EDGE RISKS
    # --------------------------------------------------------

    for i in range(len(path) - 1):

        edge = G.get_edge_data(

            path[i],

            path[i + 1]
        )

        # ----------------------------------------------------
        # UNENCRYPTED
        # ----------------------------------------------------

        if not edge.get(
            "encrypted",
            False
        ):

            score += 20

            findings.append(
                "Unencrypted conduit"
            )

        # ----------------------------------------------------
        # CROSS-ZONE
        # ----------------------------------------------------

        if edge.get(
            "cross_zone",
            False
        ):

            score += 20

            findings.append(
                "Cross-zone traversal"
            )

        # ----------------------------------------------------
        # SAFETY
        # ----------------------------------------------------

        if edge.get(
            "safety_related",
            False
        ):

            score += 40

            findings.append(
                "Safety conduit traversal"
            )

        # ----------------------------------------------------
        # REMOTE ACCESS
        # ----------------------------------------------------

        if edge.get(
            "remote_access",
            False
        ):

            score += 30

            findings.append(
                "Remote access conduit"
            )

        # ----------------------------------------------------
        # VENDOR ACCESS
        # ----------------------------------------------------

        if edge.get(
            "vendor_access",
            False
        ):

            score += 25

            findings.append(
                "Vendor access conduit"
            )

    # --------------------------------------------------------
    # PURDUE ESCALATION
    # --------------------------------------------------------

    purdue_values = []

    for p in traversed_purdue:

        purdue_values.append(

            PURDUE_ORDER.get(
                p,
                0
            )
        )

    if len(set(purdue_values)) >= 3:

        score += 30

        findings.append(
            "Multi-layer Purdue traversal"
        )

    # --------------------------------------------------------
    # MULTI-ZONE
    # --------------------------------------------------------

    if len(traversed_zones) >= 3:

        score += 25

        findings.append(
            "Multi-zone propagation"
        )

    return {

        "risk_score":
            score,

        "severity":
            classify_risk(score),

        "zones":
            list(traversed_zones),

        "findings":
            list(set(findings))
    }


# ============================================================
# FORMAT PATH
# ============================================================

def format_path(
    G,
    path
):

    formatted = []

    for node_id in path:

        node = G.nodes[node_id]

        formatted.append({

            "id":
                node_id,

            "label":
                node.get("label"),

            "zone":
                node.get("zone"),

            "cluster":
                node.get("cluster"),

            "purdue":
                node.get("purdue"),

            "criticality":
                node.get("criticality"),

            "risk_score":
                node.get("risk_score")
        })

    return formatted


# ============================================================
# SHORTEST PATH
# ============================================================

def shortest_attack_path(

    G,

    source,

    target
):

    try:

        path = nx.shortest_path(

            G,

            source=source,

            target=target
        )

        risk = calculate_path_risk(
            G,
            path
        )

        return {

            "type":
                "shortest_path",

            "source":
                source,

            "target":
                target,

            "path":
                format_path(
                    G,
                    path
                ),

            "hops":
                len(path) - 1,

            "risk":
                risk
        }

    except Exception as e:

        return {

            "error":
                str(e)
        }


# ============================================================
# ALL ATTACK PATHS
# ============================================================

def all_attack_paths(

    G,

    source,

    target,

    cutoff=8
):

    findings = []

    try:

        paths = nx.all_simple_paths(

            G,

            source=source,

            target=target,

            cutoff=cutoff
        )

        for path in paths:

            risk = calculate_path_risk(
                G,
                path
            )

            findings.append({

                "source":
                    source,

                "target":
                    target,

                "path":
                    format_path(
                        G,
                        path
                    ),

                "hops":
                    len(path) - 1,

                "risk":
                    risk
            })

        findings.sort(

            key=lambda x:
                x["risk"]["risk_score"],

            reverse=True
        )

        return findings

    except Exception as e:

        return [

            {

                "error":
                    str(e)
            }
        ]


# ============================================================
# ENTERPRISE → SAFETY PATHS
# ============================================================

def enterprise_to_safety_paths(G):

    enterprise = []
    sil4 = []

    for node_id, data in G.nodes(data=True):

        purdue = str(
            data.get(
                "purdue",
                ""
            )
        )

        criticality = str(
            data.get(
                "criticality",
                ""
            )
        ).upper()

        if "L5" in purdue:

            enterprise.append(node_id)

        if "SIL4" in criticality:

            sil4.append(node_id)

    findings = []

    for src in enterprise:

        for dst in sil4:

            try:

                results = all_attack_paths(

                    G,

                    src,

                    dst,

                    cutoff=8
                )

                findings.extend(results)

            except:
                pass

    findings.sort(

        key=lambda x:
            x.get(
                "risk",
                {}
            ).get(
                "risk_score",
                0
            ),

        reverse=True
    )

    return findings


# ============================================================
# LATERAL MOVEMENT
# ============================================================

def lateral_movement_analysis(G):

    findings = []

    for u, v, edge in G.edges(data=True):

        source = G.nodes[u]
        target = G.nodes[v]

        target_criticality = str(
            target.get(
                "criticality",
                ""
            )
        ).upper()

        if (

            not source.get(
                "trusted",
                False
            )

            and

            (
                "SIL4" in target_criticality
                or
                "SIL3" in target_criticality
            )
        ):

            findings.append({

                "type":
                    "LOW_TRUST_TO_SAFETY",

                "source":
                    source.get("label"),

                "target":
                    target.get("label"),

                "protocol":
                    edge.get("protocol"),

                "cross_zone":
                    edge.get("cross_zone"),

                "encrypted":
                    edge.get("encrypted"),

                "severity":
                    "CRITICAL"
            })

    return findings


# ============================================================
# BLAST RADIUS
# ============================================================

def blast_radius_analysis(
    G,
    source,
    depth=3
):

    impacted = []

    lengths = nx.single_source_shortest_path_length(

        G,

        source,

        cutoff=depth
    )

    for node_id, hops in lengths.items():

        if node_id == source:
            continue

        node = G.nodes[node_id]

        impacted.append({

            "id":
                node_id,

            "label":
                node.get("label"),

            "zone":
                node.get("zone"),

            "criticality":
                node.get("criticality"),

            "hops":
                hops
        })

    return impacted


# ============================================================
# EXPORT
# ============================================================

def export_json(
    data,
    output
):

    with open(

        output,

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
        f"{output}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n===================================")
    print("BUILDING GRAPH")
    print("===================================")

    G = build_graph()

    print(
        f"[OK] Nodes: {len(G.nodes)}"
    )

    print(
        f"[OK] Edges: {len(G.edges)}"
    )

    # --------------------------------------------------------
    # ENTERPRISE → SAFETY
    # --------------------------------------------------------

    print("\n===================================")
    print("ENTERPRISE TO SIL4 ATTACK PATHS")
    print("===================================")

    attack_paths = (

        enterprise_to_safety_paths(G)
    )

    print(

        json.dumps(
            attack_paths[:5],
            indent=2
        )
    )

    export_json(

        attack_paths,

        "outputs/attack_paths.json"
    )

    # --------------------------------------------------------
    # LATERAL MOVEMENT
    # --------------------------------------------------------

    print("\n===================================")
    print("LATERAL MOVEMENT")
    print("===================================")

    lateral = lateral_movement_analysis(
        G
    )

    print(

        json.dumps(
            lateral,
            indent=2
        )
    )

    export_json(

        lateral,

        "outputs/lateral_movement.json"
    )

    # --------------------------------------------------------
    # BLAST RADIUS
    # --------------------------------------------------------

    print("\n===================================")
    print("BLAST RADIUS")
    print("===================================")

    blast = blast_radius_analysis(

        G,

        "enterprise_network",

        depth=4
    )

    print(

        json.dumps(
            blast[:10],
            indent=2
        )
    )

    export_json(

        blast,

        "outputs/blast_radius.json"
    )

    print("\n===================================")
    print("DONE")
    print("===================================")

    driver.close()