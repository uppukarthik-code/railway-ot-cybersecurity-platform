from graphviz import Digraph
import re


ZONE_COLORS = {
    "enterprise_it": "lightblue",
    "idmz": "orange",
    "supervisory": "yellow",
    "station_control": "red",
    "interlocking": "pink",
    "field": "lightgreen",
    "onboard": "violet",
    "maintenance": "gray",
    "security_management": "gold",
    "telecom": "cyan",
}


def clean_id(value):
    """
    Graphviz-safe identifier
    """
    value = value.lower()
    value = value.replace(" ", "_")
    value = value.replace("-", "_")
    value = re.sub(r"[^a-zA-Z0-9_]", "", value)
    return value


def export_graphviz(topology, output_name):

    dot = Digraph(
        comment=topology["name"],
        format="svg"
    )

    dot.attr(rankdir="LR")
    dot.attr(fontname="Arial")

    node_map = {}

    # ─────────────────────────────────────────────
    # NODES
    # ─────────────────────────────────────────────
    for node in topology["nodes"]:

        safe_id = clean_id(node["id"])
        node_map[node["id"]] = safe_id

        zone = node.get("zone", "unknown")

        color = ZONE_COLORS.get(
            zone,
            "white"
        )

        label = (
            f"{node['label']}\n"
            f"[{zone}]"
        )

        dot.node(
            safe_id,
            label=label,
            shape="box",
            style="filled,rounded",
            fillcolor=color
        )

    # ─────────────────────────────────────────────
    # CONNECTIONS
    # ─────────────────────────────────────────────
    for conn in topology["connections"]:

        src = node_map.get(conn["source"])
        tgt = node_map.get(conn["target"])

        if not src or not tgt:
            continue

        protocol = conn.get("protocol", "")

        if conn.get("encrypted"):
            protocol += " 🔒"

        dot.edge(
            src,
            tgt,
            label=protocol
        )

    # ─────────────────────────────────────────────
    # EXPORT
    # ─────────────────────────────────────────────
    dot.render(
        output_name,
        cleanup=True
    )