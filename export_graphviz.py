"""
export_graphviz.py
FINAL ONTOLOGY-DRIVEN GRAPHVIZ RENDERER
IEC62443 + EN50159 + Railway OT Cybersecurity Visualization
FINAL STABLE VERSION
- Fully ontology-driven rendering
- Deterministic layout generation
- Stable Purdue ordering
- Renderer metadata aware
- Detached domain support
- Cluster-aware rendering
- Canonical node mapping
- Graphviz-safe layout
- Pure rendering responsibility
"""

from collections import defaultdict
import re
from graphviz import Digraph
from ontology import (
    PURDUE_RENDER_ORDER,
    PURDUE_COLORS,
    ZONE_COLORS,
    CLUSTER_COLORS,
    DETACHED_PURDUE_DOMAINS,
    get_purdue_color,
    get_zone_color,
    get_purdue_order,
    normalize_purdue,
    purdue_rank_sort,
    get_zone_bounds,
)

# ============================================================
# GLOBAL ENGINEERING GRID
# ============================================================
GLOBAL_COLUMNS = [
    "COL1",
    "COL2",
    "COL3",
    "COL4",
    "COL5",
    "COL6",
    "COL7",
    "COL8",
    "COL9",
    "COL10",
    "COL11",
]
# ============================================================
# LOW PRIORITY PROTOCOLS
# ============================================================
LOW_PRIORITY_PROTOCOLS = {
    "SNMPV3",
    "SYSLOG_TLS",
}


# ============================================================
# CLEAN IDS
# ============================================================
def clean_id(value):
    value = str(value).lower()
    value = value.replace(" ", "_")
    value = value.replace("-", "_")
    value = re.sub(
        r"[^a-zA-Z0-9_]",
        "",
        value,
    )
    return value


# ============================================================
# NODE FILL
# ============================================================
def get_node_fill(node):
    render_color = str(
        node.get(
            "render_color",
            "",
        )
    ).strip()
    if render_color:
        return render_color
    level = normalize_purdue(
        node.get(
            "purdue_level",
            "Unknown",
        )
    )
    return get_purdue_color(level)


# ============================================================
# NODE BORDER
# ============================================================
def get_node_border(node):
    render_border = str(
        node.get(
            "render_border",
            "",
        )
    ).strip()
    if render_border:
        return render_border
    sil = str(
        node.get(
            "functional_safety_level",
            "",
        )
    ).upper()
    if sil == "SIL4":
        return "#8B0000"
    if sil == "SIL3":
        return "#CC0000"
    if sil == "SIL2":
        return "#E69138"
    if node.get(
        "safety_critical",
        False,
    ):
        return "#CC0000"
    return "#222222"


# ============================================================
# NODE STYLE
# ============================================================
def get_node_style(node):
    render_style = str(
        node.get(
            "render_style",
            "",
        )
    ).strip()
    if render_style:
        return render_style
    return "rounded,filled"


# ============================================================
# EDGE COLOR
# ============================================================
def get_edge_color(connection):
    render_color = str(
        connection.get(
            "render_color",
            "",
        )
    ).strip()
    if render_color:
        return render_color
    if connection.get(
        "open_transmission",
        False,
    ):
        return "#7A3DB8"
    if connection.get(
        "safety_related",
        False,
    ):
        return "#CC0000"
    if connection.get(
        "encrypted",
        False,
    ):
        return "#38761D"
    return "#E69138"


# ============================================================
# EDGE STYLE
# ============================================================
def get_edge_style(connection):
    render_style = str(
        connection.get(
            "render_style",
            "",
        )
    ).strip()
    if render_style:
        return render_style
    if connection.get(
        "open_transmission",
        False,
    ):
        return "dashed"
    if connection.get(
        "engineering_access",
        False,
    ):
        return "dotted"
    if connection.get(
        "safety_related",
        False,
    ):
        return "bold"
    return "solid"


# ============================================================
# EDGE WIDTH
# ============================================================
def get_edge_width(connection):
    render_penwidth = str(
        connection.get(
            "render_penwidth",
            "",
        )
    ).strip()
    if render_penwidth:
        return render_penwidth
    if connection.get(
        "trust_boundary_crossing",
        False,
    ):
        return "3.0"
    if connection.get(
        "safety_related",
        False,
    ):
        return "2.5"
    return "1.4"


# ============================================================
# CONDUIT LABEL
# ============================================================
def build_edge_label(connection):
    protocol = connection.get(
        "protocol",
        "UNKNOWN",
    )
    parts = [protocol]
    if connection.get(
        "encrypted",
        False,
    ):
        parts.append("ENC")
    else:
        parts.append("UNENC")
    if connection.get(
        "safety_related",
        False,
    ):
        parts.append("SAFE")
    conduit_type = str(
        connection.get(
            "conduit_type",
            "",
        )
    ).strip()
    if conduit_type:
        parts.append(conduit_type)
    return " | ".join(parts)


# ============================================================
# SORT NODES
# ============================================================
def sort_nodes(nodes):
    return sorted(
        purdue_rank_sort(nodes),
        key=lambda n: (
            get_purdue_order(
                normalize_purdue(
                    n.get(
                        "purdue_level",
                        "Unknown",
                    )
                )
            ),
            str(
                n.get(
                    "cluster",
                    "",
                )
            ).lower(),
            str(
                n.get(
                    "type",
                    "",
                )
            ).lower(),
            str(
                n.get(
                    "label",
                    "",
                )
            ).lower(),
        ),
    )


# ============================================================
# RESOLVE NODE ID
# ============================================================
def resolve_node_id(
    node_map,
    value,
):
    if not value:
        return None
    normalized = clean_id(value)
    return (
        node_map.get(value)
        or node_map.get(str(value).lower())
        or node_map.get(normalized)
    )


# ============================================================
# ADD NODE
# ============================================================
def add_node(
    graph,
    node,
    node_map,
):
    safe_id = clean_id(node["id"])
    # ========================================================
    # LOOKUP MAP
    # ========================================================
    node_map[node["id"]] = safe_id
    node_map[node["label"]] = safe_id
    node_map[node["label"].lower()] = safe_id
    node_map[clean_id(node["id"])] = safe_id
    node_map[clean_id(node["label"])] = safe_id
    # ========================================================
    # LABEL
    # ========================================================
    label_lines = [
        node["label"],
        f"[{node['type']}]",
    ]
    sil = str(
        node.get(
            "functional_safety_level",
            "",
        )
    ).strip()
    if sil:
        label_lines.append(sil)
    sl = str(
        node.get(
            "security_level",
            "",
        )
    ).strip()
    if sl:
        label_lines.append(sl)
    label = "\n".join(label_lines)
    # ========================================================
    # NODE ARGS
    # ========================================================
    node_args = {
        "label": label,
        "shape": "box",
        "style": get_node_style(node),
        "fillcolor": get_node_fill(node),
        "color": get_node_border(node),
        "penwidth": str(
            node.get(
                "render_penwidth",
                "2",
            )
        ),
        "width": "2.4",
        "height": "0.9",
        "fontname": "Arial",
        "fontsize": "10",
    }
    graph.node(
        safe_id,
        **node_args,
    )
    return safe_id


# ============================================================
# EXPORT
# ============================================================
def export_graphviz(
    topology,
    output_name="outputs/kavach_graphviz",
    show_connections=True,
    debug=False,
):
    dot = Digraph(
        "Railway_OT",
        format="svg",
    )
    # ========================================================
    # GLOBAL SETTINGS
    # ========================================================
    dot.attr(
        rankdir="TB",
        splines="ortho",
        compound="true",
        newrank="true",
        overlap="false",
        concentrate="false",
        nodesep="0.8",
        ranksep="1.2",
        bgcolor="white",
        pad="0.5",
    )
    dot.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fontname="Arial",
        fontsize="10",
    )
    dot.attr(
        "edge",
        fontname="Arial",
        fontsize="8",
    )
    # ========================================================
    # GROUP NODES
    # ========================================================
    level_groups = defaultdict(list)
    for node in topology.get(
        "nodes",
        [],
    ):
        level = normalize_purdue(
            node.get(
                "purdue_level",
                "Unknown",
            )
        )
        level_groups[level].append(node)
    # ========================================================
    # DETERMINISTIC SORTING
    # ========================================================
    for level in level_groups:
        level_groups[level] = sort_nodes(level_groups[level])
    node_map = {}
    # ========================================================
    # DETACHED DOMAINS
    # ========================================================
    for detached_level in DETACHED_PURDUE_DOMAINS:
        detached_nodes = level_groups.get(
            detached_level,
            [],
        )
        if not detached_nodes:
            continue
        cluster_color = get_purdue_color(detached_level)
        cluster_name = clean_id(detached_level)
        with dot.subgraph(name=f"cluster_{cluster_name}") as detached:
            detached.attr(
                label=f"{detached_level} Domain",
                style="rounded,dashed,filled",
                fillcolor=f"{cluster_color}22",
                color=cluster_color,
                penwidth="3",
                margin="8",
            )
            for node in detached_nodes:
                add_node(
                    detached,
                    node,
                    node_map,
                )
    # ========================================================
    # PURDUE CLUSTERS
    # ========================================================
    for idx, level in enumerate(PURDUE_RENDER_ORDER):
        if level in DETACHED_PURDUE_DOMAINS:
            continue
        nodes = level_groups.get(
            level,
            [],
        )
        if not nodes:
            continue
        cluster_color = get_purdue_color(level)
        with dot.subgraph(name=f"cluster_{idx}") as cluster:
            cluster.attr(
                label=level,
                style="rounded,filled",
                fillcolor=f"{cluster_color}22",
                color=cluster_color,
                fontsize="18",
                fontname="Arial Bold",
                margin="24",
            )
            cluster.attr(rank="same")
            # ------------------------------------------------
            # GROUP BY ZONE
            # ------------------------------------------------
            zone_groups = defaultdict(list)
            for node in nodes:
                zone = str(
                    node.get(
                        "zone",
                        "unknown_zone",
                    )
                ).strip()
                zone_groups[zone].append(node)
            # ------------------------------------------------
            # ZONE CLUSTERS
            # ------------------------------------------------
            for zidx, (
                zone,
                zone_nodes,
            ) in enumerate(
                sorted(
                    zone_groups.items(),
                    key=lambda x: x[0],
                )
            ):
                zone_color = get_zone_color(zone)
                bounds = get_zone_bounds(zone)
                margin = str(
                    bounds.get(
                        "margin",
                        "16",
                    )
                )
                with cluster.subgraph(name=f"cluster_{idx}_{zidx}") as zone_cluster:
                    zone_cluster.attr(
                        label=zone,
                        style="rounded,dashed",
                        color=zone_color,
                        fontsize="12",
                        margin=margin,
                    )
                    semantic_groups = defaultdict(list)
                    for node in zone_nodes:
                        semantic_cluster = str(
                            node.get(
                                "cluster",
                                "General Systems",
                            )
                        ).strip()
                        semantic_groups[semantic_cluster].append(node)
                    # ----------------------------------------
                    # SEMANTIC SUBCLUSTERS
                    # ----------------------------------------
                    for sidx, (
                        semantic_cluster,
                        semantic_nodes,
                    ) in enumerate(
                        sorted(
                            semantic_groups.items(),
                            key=lambda x: x[0],
                        )
                    ):
                        semantic_nodes = sort_nodes(semantic_nodes)
                        semantic_color = CLUSTER_COLORS.get(
                            semantic_cluster,
                            "#EEEEEE",
                        )
                        with zone_cluster.subgraph(
                            name=f"cluster_{idx}{zidx}{sidx}"
                        ) as semantic_subcluster:
                            semantic_subcluster.attr(
                                label=semantic_cluster,
                                style="rounded,filled",
                                color="lightgray",
                                fillcolor=semantic_color,
                                fontsize="10",
                                margin="10",
                            )
                            previous_node = None
                            for node in semantic_nodes:
                                safe_id = add_node(
                                    semantic_subcluster,
                                    node,
                                    node_map,
                                )
                                if previous_node:
                                    semantic_subcluster.edge(
                                        previous_node,
                                        safe_id,
                                        style="invis",
                                        weight="10",
                                    )
                                previous_node = safe_id
    # ========================================================
    # FORCE VERTICAL ORDER
    # ========================================================
    filtered_levels = [
        level for level in PURDUE_RENDER_ORDER if level not in DETACHED_PURDUE_DOMAINS
    ]
    for i in range(len(filtered_levels) - 1):
        upper = filtered_levels[i]
        lower = filtered_levels[i + 1]
        upper_nodes = level_groups.get(
            upper,
            [],
        )
        lower_nodes = level_groups.get(
            lower,
            [],
        )
        if upper_nodes and lower_nodes:
            dot.edge(
                clean_id(upper_nodes[0]["id"]),
                clean_id(lower_nodes[0]["id"]),
                style="invis",
                weight="25",
            )
    # ========================================================
    # CONNECTIONS
    # ========================================================
    if show_connections:
        for conn in topology.get(
            "connections",
            [],
        ):
            protocol = conn.get(
                "protocol",
                "",
            )
            if protocol in LOW_PRIORITY_PROTOCOLS:
                continue
            src = resolve_node_id(
                node_map,
                conn.get("source"),
            )
            tgt = resolve_node_id(
                node_map,
                conn.get("target"),
            )
            if not src or not tgt:
                continue
            label = build_edge_label(conn)
            dot.edge(
                src,
                tgt,
                label=label,
                color=get_edge_color(conn),
                style=get_edge_style(conn),
                penwidth=get_edge_width(conn),
                arrowsize="0.8",
            )
    # ========================================================
    # EXPORT
    # ========================================================
    try:
        dot.render(
            output_name,
            cleanup=True,
        )
        dot.save(f"{output_name}.dot")
        print(f"\nGenerated: {output_name}.svg")
    except Exception as e:
        dot.save(f"{output_name}_FAILED.dot")
        print("\n[GRAPHVIZ RENDER FAILURE]")
        print(str(e))
        print(f"\nDOT FILE SAVED: " f"{output_name}_FAILED.dot")
