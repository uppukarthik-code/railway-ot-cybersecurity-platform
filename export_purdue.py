# ============================================================
# HIERARCHICAL PURDUE RENDERER
# IEC62443 + EN50159 + Railway OT
#
# FINAL STABLE HIERARCHICAL VERSION
#
# Purdue Layer
#   -> Functional Domains
#       -> Assets
#
# ============================================================
from collections import defaultdict
import re
from graphviz import Digraph
from ontology import (
    LOW_TRUST_ZONES,
    SEMI_TRUSTED_ZONES,
)

# ============================================================
# PURDUE LAYERS
# ============================================================
CORE_LEVELS = [
    "L5 Enterprise",
    "L4 Business",
    "L3.5 IDMZ",
    "L3.5 Security",
    "L3 Operations",
    "L2",
    "L1",
    "L0 Field",
]
# ============================================================
# LEVEL -> DOMAIN MAPPING
# ============================================================
LEVEL_DOMAINS = {
    "L2": [
        "L2 Telecom",
        "L2 Interlocking",
    ],
    "L1": [
        "L1 Telecom",
        "L1 Interlocking",
    ],
}
# ============================================================
# NODE ORDERING
# ============================================================
LEVEL_NODE_ORDER = {
    "L5 Enterprise": [
        "enterprise_server",
    ],
    "L4 Business": [
        "business_server",
    ],
    "L3.5 IDMZ": [
        "firewall",
        "vpn_gateway",
        "jump_host",
        "data_diode",
    ],
    "L3.5 Security": [
        "siem",
        "soc_server",
        "ids_sensor",
        "ips_sensor",
        "certificate_authority",
        "vulnerability_scanner",
        "log_collector",
    ],
    "L3 Operations": [
        "tms",
        "nms",
        "operations_workstation",
        "engineering_workstation",
    ],
    "L2 Telecom": [
        "mpls_router",
        "telecom_gateway",
    ],
    "L2 Interlocking": [
        "s_kavach",
        "electronic_interlocking",
    ],
    "L1 Telecom": [
        "railway_radio_base_station",
        "radio_gateway",
    ],
    "L1 Interlocking": [
        "axle_counter_evaluator",
        "object_controller",
    ],
    "L0 Field": [
        "point_machine_controller",
        "signal_controller",
        "track_circuit",
        "axle_counter_head",
        "trackside_rfid_tag",
    ],
    "Onboard": [
        "l_kavach",
        "train_radio",
        "driver_machine_interface",
        "brake_interface_unit",
        "speed_sensor",
        "onboard_rfid_reader",
    ],
    "Unknown": [
        "kms_server",
    ],
}
# ============================================================
# COLORS
# ============================================================
LEVEL_COLORS = {
    "L5 Enterprise": "#DCE6F1",
    "L4 Business": "#CFE2F3",
    "L3.5 IDMZ": "#FCE5CD",
    "L3.5 Security": "#FFF2CC",
    "L3 Operations": "#D9EAF7",
    "L2": "#EEEEEE",
    "L1": "#EEEEEE",
    "L2 Telecom": "#D9EAD3",
    "L1 Telecom": "#B6D7A8",
    "L2 Interlocking": "#F4CCCC",
    "L1 Interlocking": "#EA9999",
    "L0 Field": "#E2F0D9",
    "Onboard": "#D9C2E9",
    "Unknown": "#F4E1E1",
}
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
# NODE COLOR
# ============================================================
def get_node_color(node):
    level = node.get(
        "purdue_level",
        "Unknown",
    )
    return LEVEL_COLORS.get(
        level,
        "#FFFFFF",
    )


# ============================================================
# NODE BORDER
# ============================================================
def get_node_border(node):
    sil = str(
        node.get(
            "functional_safety_level",
            "",
        )
    ).upper()
    if node.get("radio_exposed", False):
        return "#7A3DB8"
    if sil == "SIL4":
        return "#8B0000"
    if sil == "SIL3":
        return "#CC0000"
    if sil == "SIL2":
        return "#E69138"
    return "#444444"


# ============================================================
# NODE STYLE
# ============================================================
def get_node_style(node):
    zone = node.get("zone")
    if zone in LOW_TRUST_ZONES:
        return "rounded,dashed,filled"
    if zone in SEMI_TRUSTED_ZONES:
        return "rounded,filled"
    return "rounded,solid,filled"


# ============================================================
# EDGE STYLE
# ============================================================
def get_edge_style(conn):
    attrs = {
        "penwidth": "1.5",
        "fontsize": "8",
        "arrowsize": "0.8",
        "constraint": "false",
        "weight": "2",
    }
    # --------------------------------------------------------
    # SAFETY RELATED
    # --------------------------------------------------------
    if conn.get("safety_related", False):
        attrs["color"] = "#CC0000"
    # --------------------------------------------------------
    # ENCRYPTED
    # --------------------------------------------------------
    elif conn.get("encrypted", False):
        attrs["color"] = "#38761D"
    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------
    else:
        attrs["color"] = "#E69138"
    # --------------------------------------------------------
    # EN50159 OPEN TRANSMISSION
    # --------------------------------------------------------
    if (
        conn.get("wireless", False)
        or conn.get("radio_related", False)
        or conn.get("open_transmission", False)
    ):
        attrs["style"] = "dashed"
        attrs["color"] = "#7A3DB8"
        attrs["penwidth"] = "2.2"
    # --------------------------------------------------------
    # ENGINEERING ACCESS
    # --------------------------------------------------------
    if conn.get("engineering_access", False):
        attrs["style"] = "dotted"
        attrs["color"] = "#3C78D8"
    # --------------------------------------------------------
    # UNIDIRECTIONAL
    # --------------------------------------------------------
    if conn.get("unidirectional", False):
        attrs["arrowhead"] = "tee"
    return attrs


# ============================================================
# SORT NODES
# ============================================================
def sort_nodes(level, nodes):
    desired_order = LEVEL_NODE_ORDER.get(level, [])

    def get_sort_key(node):
        node_type = clean_id(node.get("type", ""))
        for idx, pattern in enumerate(desired_order):
            if pattern == node_type:
                return idx
        return 999

    return sorted(
        nodes,
        key=get_sort_key,
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
    # --------------------------------------------------------
    # NODE LOOKUP MAP
    # --------------------------------------------------------
    node_map[node["id"]] = safe_id
    node_map[node["label"]] = safe_id
    node_map[node["type"]] = safe_id
    node_map[clean_id(node["id"])] = safe_id
    node_map[clean_id(node["label"])] = safe_id
    node_map[clean_id(node["type"])] = safe_id
    # --------------------------------------------------------
    # LABEL
    # --------------------------------------------------------
    label_lines = [
        node["label"],
        f"[{node['type']}]",
    ]
    sil = node.get(
        "functional_safety_level",
        "",
    )
    if sil:
        label_lines.append(str(sil))
    security_level = node.get(
        "security_level",
        "",
    )
    if security_level:
        label_lines.append(str(security_level))
    label = "\n".join(label_lines)
    # --------------------------------------------------------
    # PEN WIDTH
    # --------------------------------------------------------
    penwidth = "2"
    if str(sil).upper() == "SIL4":
        penwidth = "3"
    graph.node(
        safe_id,
        label=label,
        shape="box",
        style=get_node_style(node),
        fillcolor=get_node_color(node),
        color=get_node_border(node),
        penwidth=penwidth,
        width="2.4",
        height="0.9",
        fontsize="15",
        fontname="Arial",
    )
    return safe_id


# ============================================================
# RESOLVE NODE ID
# ============================================================
def resolve_node_id(node_map, value):
    if not value:
        return None
    normalized = clean_id(value)
    return node_map.get(value) or node_map.get(normalized)


# ============================================================
# EXPORT PURDUE
# ============================================================
def export_purdue(
    topology,
    output_name="outputs/kavach_purdue",
    show_connections=False,
):
    dot = Digraph("RailwayPurdue")
    dot.engine = "dot"
    # ========================================================
    # GLOBAL GRAPH SETTINGS
    # ========================================================
    dot.attr(
        rankdir="TB",
        splines="ortho",
        compound="true",
        newrank="true",
        overlap="false",
        concentrate="false",
        nodesep="1.0",
        ranksep="2.0 equally",
        pad="0.4",
        bgcolor="white",
    )
    dot.attr(
        "node",
        fontname="Arial",
    )
    dot.attr(
        "edge",
        fontname="Arial",
    )
    # ========================================================
    # GROUP NODES
    # ========================================================
    level_groups = defaultdict(list)
    for node in topology.get("nodes", []):
        level = node.get(
            "purdue_level",
            "Unknown",
        )
        level_groups[level].append(node)
    node_map = {}
    # ========================================================
    # GLOBAL PURDUE ANCHORS
    # ========================================================
    previous_anchor = None
    for level in CORE_LEVELS:
        anchor_id = f"{clean_id(level)}_anchor"
        dot.node(
            anchor_id,
            label="",
            shape="point",
            width="0.01",
            height="0.01",
            style="invis",
        )
        if previous_anchor:
            dot.edge(
                previous_anchor,
                anchor_id,
                style="invis",
                weight="100",
            )
        previous_anchor = anchor_id
    # ========================================================
    # DETACHED ONBOARD DOMAIN
    # ========================================================
    onboard_nodes = level_groups.get("Onboard", [])
    if onboard_nodes:
        with dot.subgraph(name="cluster_onboard") as onboard:
            onboard.attr(
                label="Mobile Onboard Domain",
                style="rounded,dashed,filled",
                fillcolor="#F3E8FF",
                color="#7A3DB8",
                penwidth="3",
            )
            with onboard.subgraph() as row:
                row.attr(rank="same")
                for node in sort_nodes(
                    "Onboard",
                    onboard_nodes,
                ):
                    add_node(
                        row,
                        node,
                        node_map,
                    )
        # ----------------------------------------------------
        # LIGHT ANCHORING TO L0
        # ----------------------------------------------------
        first_onboard = clean_id(
            sort_nodes(
                "Onboard",
                onboard_nodes,
            )[
                0
            ]["id"]
        )
        dot.edge(
            "l0_field_anchor",
            first_onboard,
            style="invis",
            weight="5",
            constraint="true",
        )
    # ========================================================
    # EXTERNAL SECURITY DOMAIN
    # ========================================================
    external_nodes = []
    for level, nodes in level_groups.items():
        for node in nodes:
            zone = node.get("zone", "")
            if zone == "external_security":
                external_nodes.append(node)
    if external_nodes:
        with dot.subgraph(name="cluster_external_security") as external:
            external.attr(
                label="External Security Services",
                style="rounded,dashed,filled",
                fillcolor="#FDE9E7",
                color="#AA4444",
                penwidth="3",
                margin="20",
                fontsize="18",
                fontname="Arial Bold",
            )
            with external.subgraph() as row:
                row.attr(rank="same")
                for node in sort_nodes(
                    "Unknown",
                    external_nodes,
                ):
                    add_node(
                        row,
                        node,
                        node_map,
                    )
        # ----------------------------------------------------
        # LIGHT ANCHORING TO SECURITY
        # ----------------------------------------------------
        first_external = clean_id(
            sort_nodes(
                "Unknown",
                external_nodes,
            )[
                0
            ]["id"]
        )
        dot.edge(
            "l35_security_anchor",
            first_external,
            style="invis",
            weight="5",
            constraint="true",
        )
    # ========================================================
    # STANDARD LEVELS
    # ========================================================
    for level in CORE_LEVELS:
        # ====================================================
        # HIERARCHICAL L2/L1
        # ====================================================
        if level in LEVEL_DOMAINS:
            with dot.subgraph(name=f"cluster_{clean_id(level)}") as parent_cluster:
                parent_cluster.attr(
                    label=level,
                    style="rounded,filled",
                    fillcolor="#F8F8F8",
                    color="#999999",
                    penwidth="2",
                    margin="24",
                    fontsize="18",
                    fontname="Arial Bold",
                )
                with parent_cluster.subgraph() as same_rank:
                    same_rank.attr(rank="same")
                    for domain in LEVEL_DOMAINS[level]:
                        domain_nodes = level_groups.get(
                            domain,
                            [],
                        )
                        if not domain_nodes:
                            continue
                        domain_color = LEVEL_COLORS.get(
                            domain,
                            "#EEEEEE",
                        )
                        with same_rank.subgraph(
                            name=f"cluster_{clean_id(domain)}"
                        ) as domain_cluster:
                            domain_cluster.attr(
                                label=domain,
                                style="rounded,filled",
                                fillcolor=f"{domain_color}22",
                                color=domain_color,
                                penwidth="2",
                                margin="18",
                                fontsize="15",
                            )
                            with domain_cluster.subgraph() as row:
                                row.attr(rank="same")
                                previous_node = None
                                for node in sort_nodes(
                                    domain,
                                    domain_nodes,
                                ):
                                    node_id = add_node(
                                        row,
                                        node,
                                        node_map,
                                    )
                                    if previous_node:
                                        row.edge(
                                            previous_node,
                                            node_id,
                                            style="invis",
                                            weight="5",
                                            constraint="false",
                                        )
                                    previous_node = node_id
            # ------------------------------------------------
            # ATTACH LAYER TO GLOBAL ANCHOR
            # ------------------------------------------------
            first_domain = LEVEL_DOMAINS[level][0]
            domain_nodes = level_groups.get(
                first_domain,
                [],
            )
            if domain_nodes:
                first_node_id = clean_id(
                    sort_nodes(
                        first_domain,
                        domain_nodes,
                    )[
                        0
                    ]["id"]
                )
                dot.edge(
                    f"{clean_id(level)}_anchor",
                    first_node_id,
                    style="invis",
                    weight="20",
                )
        # ====================================================
        # NORMAL LEVELS
        # ====================================================
        else:
            nodes = level_groups.get(level, [])
            if not nodes:
                continue
            level_color = LEVEL_COLORS.get(
                level,
                "#EEEEEE",
            )
            with dot.subgraph(name=f"cluster_{clean_id(level)}") as cluster:
                cluster.attr(
                    label=level,
                    style="rounded,filled",
                    fillcolor=f"{level_color}22",
                    color=level_color,
                    penwidth="2",
                    margin="24",
                    fontsize="18",
                    fontname="Arial Bold",
                )
                with cluster.subgraph() as row:
                    row.attr(rank="same")
                    previous_node = None
                    for node in sort_nodes(
                        level,
                        nodes,
                    ):
                        node_id = add_node(
                            row,
                            node,
                            node_map,
                        )
                        if previous_node:
                            row.edge(
                                previous_node,
                                node_id,
                                style="invis",
                                weight="5",
                                constraint="false",
                            )
                        previous_node = node_id
            # ------------------------------------------------
            # ATTACH TO GLOBAL ANCHOR
            # ------------------------------------------------
            first_node_id = clean_id(sort_nodes(level, nodes)[0]["id"])
            dot.edge(
                f"{clean_id(level)}_anchor",
                first_node_id,
                style="invis",
                weight="20",
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
            dot.edge(
                src,
                tgt,
                **get_edge_style(conn),
            )
    # ========================================================
    # EXPORT
    # ========================================================
    dot.render(
        output_name,
        format="svg",
        cleanup=True,
    )
    dot.save(f"{output_name}.dot")
    print(f"\nGenerated: {output_name}.svg")
