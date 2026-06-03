"""
export_drawio.py

Railway OT cybersecurity Draw.io renderer.

FINAL STABLE VERSION

Features:
- Purdue layered rendering
- IEC 62443 zone grouping
- Railway semantic coloring
- Secure conduit rendering
- Railway firewall insertion
- Railway asset icon mapping
- Semantic cluster-aware layouts
- External security rendering
- Railway maintenance segmentation
- Trust domain rendering
- Layout-engine coordinate rendering
- Stable conduit aggregation
- Safe zone fallback handling
- Ontology-consistent rendering

DESIGN PRINCIPLE:
Renderer consumes already-classified topology.
NO policy enforcement here.
"""

import json

from collections import defaultdict

from N2G import drawio_diagram

# ============================================================
# PURDUE LEVELS
# ============================================================

PURDUE_LEVELS = [
    "L5 Enterprise",
    "L4 Business",
    "L3.5 IDMZ",
    "L3.5 Security",
    "L3 Operations",
    "L2 Telecom",
    "L1 Telecom",
    "L2 Station Control",
    "L2 Interlocking",
    "L1 Interlocking",
    "L0 Field",
    "Onboard",
]


# ============================================================
# PURDUE COLORS
# ============================================================

LAYER_COLORS = {
    "L5 Enterprise": "#d9e2f3",
    "L4 Business": "#cfe2f3",
    "L3.5 IDMZ": "#f4b183",
    "L3.5 Security": "#ffe599",
    "L3 Operations": "#bdd7ee",
    "L2 Telecom": "#a2c4c9",
    "L1 Telecom": "#b4a7d6",
    "L2 Station Control": "#9fc5e8",
    "L2 Interlocking": "#f4cccc",
    "L1 Interlocking": "#d9ead3",
    "L0 Field": "#b6d7a8",
    "Onboard": "#d9b3ff",
}


# ============================================================
# ZONE COLORS
# ============================================================

ZONE_COLORS = {
    "enterprise_it": "#d9e2f3",
    "idmz": "#f4b183",
    "security_management": "#ffe599",
    "external_security": "#ead1dc",
    "operations": "#bdd7ee",
    "supervisory": "#9fd5ff",
    "maintenance": "#d9d9d9",
    "station_control": "#9fc5e8",
    "telecom": "#a2c4c9",
    "radio_network": "#b4a7d6",
    "interlocking": "#f4cccc",
    "train_detection": "#d9ead3",
    "point_control": "#b6d7a8",
    "signal_control": "#93c47d",
    "field": "#b6d7a8",
    "onboard": "#d9b3ff",
}


# ============================================================
# TRUST DOMAIN COLORS
# ============================================================

TRUST_DOMAIN_COLORS = {
    "railway": "#d9ead3",
    "external_security": "#ead1dc",
    "external_telecom": "#d9d2e9",
    "onboard": "#d9b3ff",
}


# ============================================================
# NODE ICONS
# ============================================================

ICON_MAP = {
    # SECURITY
    "firewall": "shape=mxgraph.cisco.security.firewall",
    "siem": "shape=mxgraph.cisco.servers.server",
    "soc_server": "shape=mxgraph.cisco.servers.server",
    "ndr_server": "shape=mxgraph.cisco.servers.server",
    "kms": "shape=mxgraph.cisco.security.key",
    # NETWORK
    "router": "shape=mxgraph.cisco.routers.router",
    "mpls_router": "shape=mxgraph.cisco.routers.router",
    "distribution_switch": "shape=mxgraph.cisco.switches.layer_3_switch",
    "telecom_switch": "shape=mxgraph.cisco.switches.workgroup_switch",
    "server": "shape=mxgraph.cisco.servers.server",
    "workstation": "shape=mxgraph.cisco.computers.workstation",
    # ENGINEERING
    "engineering_workstation": "shape=mxgraph.cisco.computers.workstation",
    "maintenance_terminal": "shape=mxgraph.cisco.computers.workstation",
    "mtc": "shape=mxgraph.cisco.computers.workstation",
    # OPERATIONS
    "sm_vdu": "shape=mxgraph.cisco.computers.workstation",
    "historian": "shape=mxgraph.cisco.servers.server",
    "nms": "shape=mxgraph.cisco.servers.server",
    "tsrms": "shape=mxgraph.cisco.servers.server",
    "tms": "shape=mxgraph.cisco.servers.server",
    "operations_workstation": "shape=mxgraph.cisco.computers.workstation",
    # INTERLOCKING
    "electronic_interlocking": "shape=mxgraph.cisco.servers.server",
    "vital_processor": "shape=mxgraph.cisco.servers.server",
    "object_controller": "shape=mxgraph.cisco.modules.switch",
    "evaluator_unit": "shape=mxgraph.cisco.modules.switch",
    "s_kavach": "shape=mxgraph.cisco.servers.server",
    "riu": "shape=mxgraph.cisco.modules.switch",
    # RADIO
    "gsmr_radio": "shape=mxgraph.cisco.wireless.access_point",
    "gsm_r_base_station": "shape=mxgraph.cisco.wireless.access_point",
    "lte_radio": "shape=mxgraph.cisco.wireless.access_point",
    "radio_base_station": "shape=mxgraph.cisco.wireless.access_point",
    "radio_modem": "shape=mxgraph.cisco.wireless.access_point",
    "radio_gateway": "shape=mxgraph.cisco.wireless.access_point",
    # ONBOARD
    "l_kavach": "shape=mxgraph.cisco.computers.workstation",
    "dmi": "shape=mxgraph.cisco.computers.workstation",
    "onboard_controller": "shape=mxgraph.cisco.servers.server",
    "train_radio": "shape=mxgraph.cisco.wireless.access_point",
    # FIELD
    "point_machine": "rounded=1",
    "axle_counter": "rounded=1",
    "track_circuit": "rounded=1",
    "signal_lamp": "rounded=1",
    "signal_controller": "rounded=1",
    "rfid_tag": "ellipse",
    "rfid_reader": "ellipse",
}


# ============================================================
# FIREWALL RULES
# ============================================================

FIREWALL_RULES = {
    tuple(sorted(("enterprise_it", "operations"))): "Enterprise Firewall",
    tuple(sorted(("enterprise_it", "interlocking"))): "Critical Safety Firewall",
    tuple(sorted(("enterprise_it", "telecom"))): "Enterprise OT Firewall",
    tuple(sorted(("operations", "interlocking"))): "Safety Segmentation Firewall",
    tuple(sorted(("operations", "telecom"))): "OT Telecom Firewall",
    tuple(sorted(("maintenance", "interlocking"))): "Engineering Access Firewall",
    tuple(sorted(("radio_network", "interlocking"))): "Radio Security Gateway",
    tuple(sorted(("external_security", "operations"))): "External Crypto Gateway",
    tuple(
        sorted(("external_security", "security_management"))
    ): "External Security Gateway",
}


# ============================================================
# NODE FILL
# ============================================================


def infer_node_fill(node):

    sil = str(node.get("functional_safety_level", "")).upper()

    criticality = str(node.get("criticality", "")).upper()

    if sil == "SIL4":
        return "#ffcccc"

    if sil == "SIL3":
        return "#ffe599"

    if criticality == "HIGH":
        return "#cfe2f3"

    if criticality == "MEDIUM":
        return "#d9ead3"

    return "#ffffff"


# ============================================================
# EXPORT
# ============================================================


def export_drawio(topology, output_name="outputs/kavach.drawio"):

    diagram = drawio_diagram()

    diagram.add_diagram("Railway Purdue Architecture")

    # ========================================================
    # TRUST DOMAINS
    # ========================================================

    trust_bounds = topology.get("trust_domain_bounds", {})

    for domain, bounds in trust_bounds.items():

        fill = TRUST_DOMAIN_COLORS.get(domain, "#ffffff")

        label = domain.replace("_", " ").title()

        diagram.add_node(
            id=f"trust_{domain}",
            label=label,
            x_pos=bounds["x1"],
            y_pos=bounds["y1"],
            width=(bounds["x2"] - bounds["x1"]),
            height=(bounds["y2"] - bounds["y1"]),
            style=(
                "shape=swimlane;"
                "horizontal=0;"
                "rounded=1;"
                "container=1;"
                "collapsible=0;"
                "strokeWidth=3;"
                "dashed=0;"
                f"fillColor={fill};"
                "fontSize=20;"
                "fontStyle=1;"
            ),
        )

    # ========================================================
    # GROUP BY ZONE
    # ========================================================

    zones = defaultdict(list)

    for node in topology.get("nodes", []):

        zone = node.get("zone", "field")

        zones[zone].append(node)

    zone_bounds = topology.get("zone_bounds", {})

    zone_positions = {}

    # ========================================================
    # DRAW ZONES
    # ========================================================

    for zone_name, nodes in zones.items():

        bounds = zone_bounds.get(zone_name)

        # ====================================================
        # SAFE FALLBACK
        # ====================================================

        if not bounds:

            print(f"[WARN] Missing zone bounds for: {zone_name}")

            bounds = {
                "x1": 100,
                "y1": 100,
                "x2": 500,
                "y2": 400,
            }

        zone_x = bounds["x1"]

        zone_y = bounds["y1"]

        zone_width = bounds["x2"] - bounds["x1"]

        zone_height = bounds["y2"] - bounds["y1"]

        zone_id = f"zone_{zone_name}"

        zone_positions[zone_name] = (zone_x, zone_y)

        diagram.add_node(
            id=zone_id,
            label=zone_name.replace("_", " ").title(),
            x_pos=zone_x,
            y_pos=zone_y,
            width=zone_width,
            height=zone_height,
            style=(
                "rounded=1;"
                "strokeWidth=2;"
                "dashed=0;"
                f"fillColor={ZONE_COLORS.get(zone_name, '#ffffff')};"
                "fontStyle=1;"
                "fontSize=15;"
            ),
        )

        # ====================================================
        # DRAW NODES
        # ====================================================

        for node in nodes:

            pos = node.get("position", {})

            x = pos.get("x", 0)

            y = pos.get("y", 0)

            node_type = node.get("type", "")

            label = f"{node['label']}" f"\\n[{node_type}]"

            style = ICON_MAP.get(node_type, "rounded=1")

            fill = infer_node_fill(node)

            border = "#000000"

            if node.get("safety_critical", False):

                border = "#cc0000"

            if node.get("external_zone", False):

                border = "#7a3db8"

            diagram.add_node(
                id=node["id"],
                label=label,
                x_pos=x,
                y_pos=y,
                width=170,
                height=70,
                style=(
                    style + ";whiteSpace=wrap;"
                    ";html=1;"
                    ";strokeWidth=2;"
                    f";strokeColor={border};"
                    f";fillColor={fill};"
                ),
            )

    # ========================================================
    # NODE LOOKUP
    # ========================================================

    node_lookup = {n["id"]: n for n in topology.get("nodes", [])}

    # ========================================================
    # CONDUIT AGGREGATION
    # ========================================================

    conduits = {}

    for conn in topology.get("connections", []):

        src = node_lookup.get(conn["source"])

        dst = node_lookup.get(conn["target"])

        if not src or not dst:
            continue

        src_zone = src.get("zone", "field")

        dst_zone = dst.get("zone", "field")

        if src_zone == dst_zone:
            continue

        key = tuple(sorted([src_zone, dst_zone]))

        if key not in conduits:

            conduits[key] = {
                "encrypted": True,
                "protocols": set(),
                "safety_related": False,
            }

        conduits[key]["encrypted"] &= conn.get("encrypted", False)

        conduits[key]["safety_related"] |= conn.get("safety_related", False)

        conduits[key]["protocols"].add(conn.get("protocol", "Unknown"))

    # ========================================================
    # DRAW CONDUITS
    # ========================================================

    rendered_firewalls = set()

    for (src_zone, dst_zone), conduit in conduits.items():

        src_id = f"zone_{src_zone}"

        dst_id = f"zone_{dst_zone}"

        protocols = ", ".join(sorted(conduit["protocols"]))

        encrypted = conduit["encrypted"]

        safety_related = conduit["safety_related"]

        color = "#008000" if encrypted else "#cc0000"

        stroke = "5" if safety_related else "3"

        label = f"{protocols} [ENC]" if encrypted else f"{protocols} [UNENC]"

        firewall_key = tuple(sorted([src_zone, dst_zone]))

        firewall_name = FIREWALL_RULES.get(firewall_key)

        # ====================================================
        # FIREWALL PATH
        # ====================================================

        if firewall_name:

            fw_id = firewall_name.replace(" ", "_")

            if fw_id not in rendered_firewalls:

                src_pos = zone_positions.get(
                    src_zone,
                    (100, 100),
                )

                dst_pos = zone_positions.get(
                    dst_zone,
                    (500, 500),
                )

                fw_x = (src_pos[0] + dst_pos[0]) // 2

                fw_y = (src_pos[1] + dst_pos[1]) // 2

                diagram.add_node(
                    id=fw_id,
                    label=firewall_name,
                    x_pos=fw_x,
                    y_pos=fw_y,
                    width=130,
                    height=64,
                    style=(
                        "shape=mxgraph.cisco.security.firewall;"
                        "html=1;"
                        "fontSize=11;"
                    ),
                )

                rendered_firewalls.add(fw_id)

            diagram.add_link(
                src_id, fw_id, style=(f"strokeWidth={stroke};" f"strokeColor={color};")
            )

            diagram.add_link(
                fw_id,
                dst_id,
                label=label,
                style=(
                    f"strokeWidth={stroke};" f"strokeColor={color};" "endArrow=classic;"
                ),
            )

        # ====================================================
        # DIRECT PATH
        # ====================================================

        else:

            diagram.add_link(
                src_id,
                dst_id,
                label=label,
                style=(
                    f"strokeWidth={stroke};"
                    f"strokeColor={color};"
                    "rounded=1;"
                    "endArrow=classic;"
                ),
            )

    # ========================================================
    # EXPORT
    # ========================================================

    diagram.dump_file(filename=output_name.split("/")[-1], folder="./outputs")

    print("\nDraw.io exported successfully.")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    with open("outputs/kavach_topology_layout.json", encoding="utf-8") as f:

        topology = json.load(f)

    export_drawio(topology, "outputs/kavach.drawio")
