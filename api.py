"""
api.py

Railway OT Cybersecurity Graph API
----------------------------------

PURPOSE:
- Serve Neo4j OT graph
- Serve Cytoscape frontend
- Serve attack-path analytics
- Serve IEC 62443 violations
- Serve Purdue overlays
- Serve zone overlays
- Serve blast radius analytics
- Serve risk overlays

STACK:
- FastAPI
- Neo4j
- NetworkX

INSTALL:
pip install fastapi uvicorn neo4j python-dotenv networkx

RUN:
uvicorn api:app --reload

DOCS:
http://127.0.0.1:8000/docs
"""

# ============================================================
# IMPORTS
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from neo4j import GraphDatabase
from dotenv import load_dotenv

import networkx as nx
import os


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")


# ============================================================
# NEO4J DRIVER
# ============================================================

driver = GraphDatabase.driver(

    URI,

    auth=(
        USERNAME,
        PASSWORD
    )
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(

    title="Railway OT Cybersecurity API",

    version="2.1"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# QUERY HELPER
# ============================================================

def run_query(query, parameters=None):

    with driver.session() as session:

        result = session.run(

            query,

            parameters or {}
        )

        return [r.data() for r in result]


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_float(value, default=0):

    try:

        if value is None:
            return default

        return float(value)

    except Exception:

        return default


def safe_bool(value):

    return bool(value) if value is not None else False


def safe_str(value, default=""):

    return str(value) if value is not None else default


# ============================================================
# BUILD NETWORKX GRAPH
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
        a.is_trusted_zone AS source_trusted,
        a.risk_score AS source_risk,

        b.id AS target_id,
        b.label AS target_label,
        b.zone AS target_zone,
        b.cluster AS target_cluster,
        b.purdue_level AS target_purdue,
        b.criticality AS target_criticality,
        b.is_trusted_zone AS target_trusted,
        b.risk_score AS target_risk,

        r.protocol AS protocol,
        r.encrypted AS encrypted,
        r.cross_zone AS cross_zone,
        r.safety_related AS safety_related,
        r.conduit_type AS conduit_type,
        r.remote_access AS remote_access,
        r.vendor_access AS vendor_access,
        r.risk_score AS edge_risk

    """

    results = run_query(query)

    for r in results:

        # ----------------------------------------------------
        # SOURCE NODE
        # ----------------------------------------------------

        G.add_node(

            r["source_id"],

            label=r["source_label"],

            zone=r["source_zone"],

            cluster=r["source_cluster"],

            purdue=r["source_purdue"],

            criticality=r["source_criticality"],

            trusted=r["source_trusted"],

            risk_score=r["source_risk"]
        )

        # ----------------------------------------------------
        # TARGET NODE
        # ----------------------------------------------------

        G.add_node(

            r["target_id"],

            label=r["target_label"],

            zone=r["target_zone"],

            cluster=r["target_cluster"],

            purdue=r["target_purdue"],

            criticality=r["target_criticality"],

            trusted=r["target_trusted"],

            risk_score=r["target_risk"]
        )

        # ----------------------------------------------------
        # EDGE
        # ----------------------------------------------------

        G.add_edge(

            r["source_id"],

            r["target_id"],

            protocol=r["protocol"],

            encrypted=r["encrypted"],

            cross_zone=r["cross_zone"],

            safety_related=r["safety_related"],

            conduit_type=r["conduit_type"],

            remote_access=r["remote_access"],

            vendor_access=r["vendor_access"],

            risk_score=r["edge_risk"]
        )

    return G


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "status": "running",

        "service": "Railway OT Cybersecurity API",

        "version": "2.1"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    try:

        q = """
        MATCH (n)
        RETURN COUNT(n) AS count
        """

        result = run_query(q)

        return {

            "status": "healthy",

            "neo4j": "connected",

            "nodes": result[0]["count"]
        }

    except Exception as e:

        return {

            "status": "unhealthy",

            "error": str(e)
        }


# ============================================================
# STATS
# ============================================================

@app.get("/stats")
def stats():

    queries = {

        "assets":
            """
            MATCH (a:Asset)
            RETURN COUNT(a) AS count
            """,

        "connections":
            """
            MATCH ()-[r:CONNECTS]->()
            RETURN COUNT(r) AS count
            """,

        "cross_zone":
            """
            MATCH ()-[r:CONNECTS]->()
            WHERE r.cross_zone = true
            RETURN COUNT(r) AS count
            """
    }

    results = {}

    for key, q in queries.items():

        results[key] = run_query(q)[0]["count"]

    return results


# ============================================================
# ASSETS
# ============================================================

@app.get("/assets")
def assets():

    q = """

    MATCH (a:Asset)

    RETURN

        a.id AS id,
        a.label AS label,
        a.type AS type,
        a.zone AS zone,
        a.cluster AS cluster,
        a.purdue_level AS purdue,
        a.criticality AS criticality,
        a.risk_score AS risk_score

    ORDER BY a.zone, a.label

    """

    return run_query(q)


# ============================================================
# SINGLE ASSET
# ============================================================

@app.get("/asset/{asset_id}")
def asset(asset_id: str):

    q = """

    MATCH (a:Asset {id:$id})

    RETURN a

    """

    result = run_query(

        q,

        {

            "id": asset_id
        }
    )

    if not result:

        return {

            "error": "Asset not found"
        }

    return result[0]["a"]


# ============================================================
# CONNECTIONS
# ============================================================

@app.get("/connections")
def connections():

    q = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    RETURN

        a.id AS source,
        b.id AS target,

        r.protocol AS protocol,
        r.encrypted AS encrypted,
        r.cross_zone AS cross_zone,
        r.safety_related AS safety_related,
        r.risk_score AS risk_score

    """

    return run_query(q)


# ============================================================
# CYTOSCAPE
# ============================================================

@app.get("/cytoscape")
def cytoscape():

    elements = []

    # ========================================================
    # NODES
    # ========================================================

    q1 = """

    MATCH (a:Asset)

    RETURN
        a.id AS id,
        a.label AS label,
        a.type AS type,
        a.zone AS zone,
        a.cluster AS cluster,
        a.purdue_level AS purdue,
        a.criticality AS criticality,
        a.is_trusted_zone AS trusted,
        a.risk_score AS risk_score,
        a.zone_color AS color,
        a.x AS x,
        a.y AS y

    """

    nodes = run_query(q1)

    for a in nodes:

        elements.append({

            "data": {

                "id":
                    safe_str(a.get("id")),

                "label":
                    safe_str(a.get("label")),

                "type":
                    safe_str(a.get("type")),

                "zone":
                    safe_str(a.get("zone")),

                "cluster":
                    safe_str(a.get("cluster")),

                "purdue":
                    safe_str(a.get("purdue")),

                "criticality":
                    safe_str(a.get("criticality")),

                "trusted":
                    safe_bool(a.get("trusted")),

                "risk_score":
                    safe_float(a.get("risk_score")),

                "color":
                    safe_str(
                        a.get("color"),
                        "#cccccc"
                    ),

                "x":
                    safe_float(a.get("x")),

                "y":
                    safe_float(a.get("y"))
            }
        })

    # ========================================================
    # EDGES
    # ========================================================

    q2 = """

    MATCH (a:Asset)-[r:CONNECTS]->(b:Asset)

    RETURN

        a.id AS source,
        b.id AS target,

        r.protocol AS protocol,
        r.encrypted AS encrypted,
        r.cross_zone AS cross_zone,
        r.safety_related AS safety_related,
        r.risk_score AS risk_score,
        r.remote_access AS remote_access,
        r.vendor_access AS vendor_access

    """

    edges = run_query(q2)

    for idx, r in enumerate(edges):

        elements.append({

            "data": {

                "id":
                    f"e_{idx}",

                "source":
                    safe_str(r.get("source")),

                "target":
                    safe_str(r.get("target")),

                "label":
                    safe_str(r.get("protocol")),

                "encrypted":
                    safe_bool(r.get("encrypted")),

                "cross_zone":
                    safe_bool(r.get("cross_zone")),

                "safety":
                    safe_bool(r.get("safety_related")),

                "risk_score":
                    safe_float(r.get("risk_score")),

                "remote_access":
                    safe_bool(r.get("remote_access")),

                "vendor_access":
                    safe_bool(r.get("vendor_access"))
            }
        })

    return elements


# ============================================================
# VIOLATIONS
# ============================================================

@app.get("/violations")
def violations():

    findings = []

    q = """

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

    results = run_query(q)

    for r in results:

        findings.append({

            "type": "UNENCRYPTED_CROSS_ZONE",

            "severity": "HIGH",

            "details": r
        })

    return findings


# ============================================================
# ATTACK PATH
# ============================================================

@app.get("/attack-path/{source}/{target}")
def attack_path(source: str, target: str):

    G = build_graph()

    try:

        path = nx.shortest_path(

            G,

            source=source,

            target=target
        )

        formatted = []

        for node_id in path:

            node = G.nodes[node_id]

            formatted.append({

                "id": node_id,

                "label":
                    node.get("label"),

                "zone":
                    node.get("zone"),

                "criticality":
                    node.get("criticality")
            })

        return {

            "source": source,

            "target": target,

            "hops": len(path) - 1,

            "path": formatted
        }

    except Exception as e:

        return {

            "error": str(e)
        }


# ============================================================
# BLAST RADIUS
# ============================================================

@app.get("/blast-radius/{source}")
def blast_radius(source: str, depth: int = 3):

    G = build_graph()

    try:

        lengths = nx.single_source_shortest_path_length(

            G,

            source,

            cutoff=depth
        )

        impacted = []

        for node_id, hops in lengths.items():

            if node_id == source:
                continue

            node = G.nodes[node_id]

            impacted.append({

                "id": node_id,

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

    except Exception as e:

        return {

            "error": str(e)
        }


# ============================================================
# PURDUE
# ============================================================

@app.get("/purdue")
def purdue():

    q = """

    MATCH (a:Asset)

    RETURN

        a.purdue_level AS purdue,

        COUNT(*) AS assets

    ORDER BY purdue

    """

    return run_query(q)


# ============================================================
# ZONES
# ============================================================

@app.get("/zones")
def zones():

    q = """

    MATCH (a:Asset)

    RETURN

        a.zone AS zone,

        COUNT(*) AS assets

    ORDER BY assets DESC

    """

    return run_query(q)


# ============================================================
# RISK OVERLAY
# ============================================================

@app.get("/risk-overlay")
def risk_overlay():

    q = """

    MATCH (a:Asset)

    RETURN

        a.id AS id,
        a.label AS label,
        a.risk_score AS risk_score,
        a.zone AS zone,
        a.criticality AS criticality

    ORDER BY a.risk_score DESC

    """

    return run_query(q)


# ============================================================
# SHUTDOWN
# ============================================================

@app.on_event("shutdown")
def shutdown():

    driver.close()