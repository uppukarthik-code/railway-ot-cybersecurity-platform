"""
layout_engine.py

Backend semantic layout engine for Railway OT Cybersecurity Topology.

PURPOSE:
- Deterministic semantic layout generation
- Purdue + Trust Domain + Functional Cell aware placement
- Backend-driven coordinates
- Draw.io compatible positioning
- Neo4j compatible positioning
- Cytoscape compatible rendering
- Attack-path overlay support
- Blast-radius visualization support
- Graph diffing support
- IEC62443 zone visualization
- Cyber-physical dependency visualization

REQUIRES:
pip install networkx
"""

import json
import networkx as nx

# Single trust-domain derivation authority (assessment finding C-02).
# layout_engine no longer defines its own infer_trust_domain; it consumes
# the classifier projection of the ZONE_ONTOLOGY.trust authority. The
# trust_domain values here are used ONLY for rendering grouping/ordering
# ("Rendering Grouping: layout_engine only"), never for trust decisions.
from classifier import infer_trust_domain as _infer_trust_domain


# ============================================================
# PURDUE HIERARCHY
# ============================================================

PURDUE_Y = {

    "L5 Enterprise": 0,

    "L4 Business": 1,

    "L3.5 IDMZ": 2,

    "L3.5 Security": 3,

    "L3 Operations": 4,

    "L2 Telecom": 5,

    "L2 Station Control": 6,

    "L2 Interlocking": 7,

    "L1 Telecom": 8,

    "L1 Interlocking": 9,

    "L0 Field": 10,

    "Onboard": 11,

    "Unknown": 12
}


# ============================================================
# TRUST DOMAIN ORDER
# ============================================================

# Rendering order, expressed in the authoritative classifier trust-domain
# vocabulary (railway_trusted / mobile / external) — see C-02.
TRUST_DOMAIN_ORDER = [

    "railway_trusted",

    "mobile",

    "external"
]


# ============================================================
# TRUST DOMAIN X OFFSETS
# ============================================================

TRUST_DOMAIN_X = {

    "railway":
        0,

    "external_security":
        5000,

    "external_telecom":
        8500,

    "onboard":
        12000
}


# ============================================================
# SPACING
# ============================================================

CLUSTER_HORIZONTAL_SPACING = 700

NODE_HORIZONTAL_SPACING = 220

VERTICAL_SPACING = 300

ZONE_PADDING_X = 260

ZONE_PADDING_Y = 180


# ============================================================
# LOAD TOPOLOGY
# ============================================================

def load_topology(
    path: str
):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph(
    topology: dict
):

    G = nx.DiGraph()

    for node in topology.get(
        "nodes",
        []
    ):

        G.add_node(

            node["id"],

            **node
        )

    for conn in topology.get(
        "connections",
        []
    ):

        G.add_edge(

            conn["source"],

            conn["target"],

            **conn
        )

    return G


# ============================================================
# TRUST DOMAIN (rendering grouping)
# ============================================================
# The duplicate derivation was removed (assessment finding C-02). Trust
# domain is derived once, by the single authority classifier.
# infer_trust_domain (ZONE_ONTOLOGY.trust -> LOW_TRUST_ZONES/onboard ->
# railway_trusted/mobile/external), imported above as _infer_trust_domain
# and called directly at the rendering-grouping site below.


# ============================================================
# BUILD SEMANTIC GROUPS
# ============================================================

def build_semantic_groups(
    G
):

    groups = {}

    for node_id, data in G.nodes(data=True):

        purdue = data.get(
            "purdue_level",
            "Unknown"
        )

        cluster = data.get(
            "functional_cell",
            "General"
        )

        trust_domain = data.get(
            "trust_domain"
        )

        if not trust_domain:

            trust_domain = _infer_trust_domain(
                data.get(
                    "zone",
                    "",
                )
            )

        data["trust_domain"] = (
            trust_domain
        )

        key = (

            trust_domain,

            purdue,

            cluster
        )

        groups.setdefault(
            key,
            []
        ).append(
            (
                node_id,
                data
            )
        )

    return groups


# ============================================================
# SORT NODES
# ============================================================

def sort_nodes_semantically(
    nodes
):

    def weight(item):

        _, data = item

        # SIL (functional_safety_level) and severity (criticality) are
        # distinct authorities and must not be conflated (assessment
        # finding C-04). SIL weights read the SIL authority; the HIGH
        # severity weight continues to read criticality.
        sil = str(
            data.get(
                "functional_safety_level",
                ""
            )
        ).upper()

        criticality = str(
            data.get(
                "criticality",
                ""
            )
        ).upper()

        risk = float(
            data.get(
                "risk_score",
                0
            )
        )

        safety = data.get(
            "safety_critical",
            False
        )

        score = 0

        if "SIL4" in sil:
            score += 100

        elif "SIL3" in sil:
            score += 70

        elif "HIGH" in criticality:
            score += 40

        if safety:
            score += 40

        score += risk

        return -score

    return sorted(
        nodes,
        key=weight
    )


# ============================================================
# COMPUTE SEMANTIC LAYOUT
# ============================================================

def compute_semantic_layout(
    G
):

    groups = build_semantic_groups(
        G
    )

    positions = {}

    cluster_compounds = []

    trust_domain_bounds = {}

    # ========================================================
    # GROUP BY TRUST DOMAIN + PURDUE
    # ========================================================

    grouped = {}

    for (

        trust_domain,

        purdue,

        cluster

    ), nodes in groups.items():

        grouped.setdefault(
            trust_domain,
            {}
        ).setdefault(
            purdue,
            []
        ).append(
            (
                cluster,
                nodes
            )
        )

    # ========================================================
    # LAYOUT
    # ========================================================

    for trust_domain in TRUST_DOMAIN_ORDER:

        domain_groups = grouped.get(
            trust_domain,
            {}
        )

        domain_x_offset = (
            TRUST_DOMAIN_X.get(
                trust_domain,
                0
            )
        )

        domain_positions = []

        for purdue, cluster_sets in domain_groups.items():

            level_y = (

                PURDUE_Y.get(
                    purdue,
                    12
                )

                * VERTICAL_SPACING
            )

            cluster_sets = sorted(
                cluster_sets,
                key=lambda x: x[0]
            )

            total_clusters = len(
                cluster_sets
            )

            total_width = (

                (
                    total_clusters - 1
                )

                * CLUSTER_HORIZONTAL_SPACING
            )

            start_x = -(
                total_width / 2
            )

            # ------------------------------------------------
            # EACH CLUSTER
            # ------------------------------------------------

            for cluster_idx, (

                cluster_name,

                nodes

            ) in enumerate(cluster_sets):

                cluster_x = (

                    domain_x_offset

                    +

                    start_x

                    +

                    (
                        cluster_idx
                        *
                        CLUSTER_HORIZONTAL_SPACING
                    )
                )

                sorted_nodes = (
                    sort_nodes_semantically(
                        nodes
                    )
                )

                node_count = len(
                    sorted_nodes
                )

                node_width = (

                    (
                        node_count - 1
                    )

                    * NODE_HORIZONTAL_SPACING
                )

                node_start_x = (

                    cluster_x

                    -

                    node_width / 2
                )

                cluster_positions = []

                # =============================================
                # PLACE NODES
                # =============================================

                for idx, (

                    node_id,

                    data

                ) in enumerate(sorted_nodes):

                    x = (

                        node_start_x

                        +

                        (
                            idx
                            *
                            NODE_HORIZONTAL_SPACING
                        )
                    )

                    y = level_y

                    positions[node_id] = {

                        "x":
                            round(x, 2),

                        "y":
                            round(y, 2)
                    }

                    cluster_positions.append(
                        (x, y)
                    )

                    domain_positions.append(
                        (x, y)
                    )

                # =============================================
                # CLUSTER COMPOUNDS
                # =============================================

                if cluster_positions:

                    xs = [
                        p[0]
                        for p in cluster_positions
                    ]

                    ys = [
                        p[1]
                        for p in cluster_positions
                    ]

                    cluster_compounds.append({

                        "id":
                            f"{trust_domain}{purdue}{cluster_name}",

                        "trust_domain":
                            trust_domain,

                        "cluster":
                            cluster_name,

                        "purdue":
                            purdue,

                        "x1":
                            min(xs)
                            - ZONE_PADDING_X,

                        "y1":
                            min(ys)
                            - ZONE_PADDING_Y,

                        "x2":
                            max(xs)
                            + ZONE_PADDING_X,

                        "y2":
                            max(ys)
                            + ZONE_PADDING_Y
                    })

        # ====================================================
        # TRUST DOMAIN BOUNDS
        # ====================================================

        if domain_positions:

            xs = [
                p[0]
                for p in domain_positions
            ]

            ys = [
                p[1]
                for p in domain_positions
            ]

            trust_domain_bounds[
                trust_domain
            ] = {

                "x1":
                    min(xs) - 500,

                "y1":
                    min(ys) - 260,

                "x2":
                    max(xs) + 500,

                "y2":
                    max(ys) + 260
            }

    return (

        positions,

        cluster_compounds,

        trust_domain_bounds
    )


# ============================================================
# APPLY POSITIONS
# ============================================================

def apply_positions(
    topology,
    positions
):

    for node in topology.get(
        "nodes",
        []
    ):

        node_id = node["id"]

        if node_id in positions:

            node["position"] = {

                "x":
                    positions[node_id]["x"],

                "y":
                    positions[node_id]["y"]
            }

    return topology


# ============================================================
# COMPUTE ZONE BOUNDS
# ============================================================

def compute_zone_bounds(
    topology
):

    zones = {}

    for node in topology.get(
        "nodes",
        []
    ):

        zone = node.get(
            "zone",
            "unknown"
        )

        pos = node.get(
            "position",
            {}
        )

        x = pos.get("x", 0)

        y = pos.get("y", 0)

        zones.setdefault(
            zone,
            []
        ).append(
            (x, y)
        )

    bounds = {}

    for zone, coords in zones.items():

        xs = [c[0] for c in coords]

        ys = [c[1] for c in coords]

        bounds[zone] = {

            "x1":
                min(xs) - 280,

            "y1":
                min(ys) - 180,

            "x2":
                max(xs) + 280,

            "y2":
                max(ys) + 180
        }

    return bounds


# ============================================================
# COMPUTE RISK OVERLAY
# ============================================================

def compute_attack_surface_overlay(
    topology
):

    overlay = []

    for node in topology.get(
        "nodes",
        []
    ):

        risk = float(
            node.get(
                "risk_score",
                0
            )
        )

        exposure = float(
            node.get(
                "exposure_score",
                0
            )
        )

        attack_surface = float(
            node.get(
                "attack_surface_score",
                0
            )
        )

        total = (
            risk
            +
            exposure
            +
            attack_surface
        )

        overlay.append({

            "id":
                node["id"],

            "risk_heat":
                round(total, 2)
        })

    return overlay


# ============================================================
# GRAPH METADATA
# ============================================================

def enrich_graph_metadata(
    topology
):

    topology["graph_metadata"] = {

        "generated_by":
            "layout_engine.py",

        "layout_engine":
            "Semantic Purdue Layout",

        "supports_attack_paths":
            True,

        "supports_zone_overlays":
            True,

        "supports_graph_diffing":
            True,

        "supports_risk_overlay":
            True,

        "supports_cluster_compounds":
            True,

        "supports_blast_radius":
            True,

        "supports_neo4j":
            True,

        "supports_drawio_export":
            True
    }

    return topology


# ============================================================
# SAVE
# ============================================================

def save_topology(
    topology,
    output_path
):

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            topology,

            f,

            indent=2
        )

    print(
        f"[OK] Layout saved: "
        f"{output_path}"
    )


# ============================================================
# MAIN ENGINE
# ============================================================

def generate_layout(

    input_path,

    output_path
):

    # ========================================================
    # LOAD
    # ========================================================

    topology = load_topology(
        input_path
    )

    # ========================================================
    # BUILD GRAPH
    # ========================================================

    G = build_graph(
        topology
    )

    # ========================================================
    # COMPUTE LAYOUT
    # ========================================================

    (
        positions,

        compounds,

        trust_bounds

    ) = compute_semantic_layout(
        G
    )

    # ========================================================
    # APPLY POSITIONS
    # ========================================================

    topology = apply_positions(

        topology,

        positions
    )

    # ========================================================
    # ZONE BOUNDS
    # ========================================================

    topology["zone_bounds"] = (

        compute_zone_bounds(
            topology
        )
    )

    # ========================================================
    # TRUST DOMAIN BOUNDS
    # ========================================================

    topology["trust_domain_bounds"] = (
        trust_bounds
    )

    # ========================================================
    # CLUSTER COMPOUNDS
    # ========================================================

    topology["cluster_compounds"] = (
        compounds
    )

    # ========================================================
    # RISK OVERLAY
    # ========================================================

    topology["risk_overlay"] = (

        compute_attack_surface_overlay(
            topology
        )
    )

    # ========================================================
    # METADATA
    # ========================================================

    topology = enrich_graph_metadata(
        topology
    )

    # ========================================================
    # SAVE
    # ========================================================

    save_topology(

        topology,

        output_path
    )

    print(
        "[OK] Layout generation complete."
    )


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    INPUT = (
        "outputs/kavach_topology.json"
    )

    OUTPUT = (
        "outputs/kavach_topology_layout.json"
    )

    generate_layout(

        INPUT,

        OUTPUT
    )