"""
render_validator.py

FINAL HARDENED RENDER SAFETY VALIDATOR

IEC62443 + EN50159 + Railway OT + Kavach

RESPONSIBILITIES
----------------
- Rendering validation ONLY
- Structural graph integrity
- Graphviz safety validation
- DrawIO safety validation
- Render metadata validation

NOT RESPONSIBLE FOR
-------------------
- Semantic inference
- Ontology enforcement
- Purdue validation
- Zone validation
- IEC62443 policy validation
- EN50159 compliance logic
- Safety reasoning
"""

import re
from ontology import (
    DETACHED_PURDUE_DOMAINS,
)

# ============================================================
# SAFE GRAPHVIZ REGEX
# ============================================================

SAFE_NODE_ID_REGEX = r"^[a-zA-Z0-9_\-]+$"

# ============================================================
# SAFE LABEL REGEX
#
# Prevent:
# - DOT injection
# - Graphviz HTML label injection
# - XML / DrawIO injection
# ============================================================

SAFE_LABEL_REGEX = r"^[a-zA-Z0-9 _.,:/()\-]+$"

# ============================================================
# VALID RENDER STYLES
# ============================================================

VALID_RENDER_STYLES = {
    "rounded,filled",
    "rounded,dashed,filled",
    "rounded,solid,filled",
    "filled",
}

# ============================================================
# VALID EDGE STYLES
# ============================================================

VALID_EDGE_STYLES = {
    "solid",
    "dashed",
    "dotted",
    "bold",
}

# ============================================================
# VALID HEX COLOR
# ============================================================

HEX_COLOR_REGEX = r"^#[0-9a-fA-F]{6}$"

# ============================================================
# LABEL LIMIT
# ============================================================

MAX_LABEL_LENGTH = 256

# ============================================================
# VALIDATE RENDERING
# ============================================================


def validate_rendering(
    topology: dict,
) -> list[str]:

    errors = []

    print("\n══ RENDER VALIDATION ══")

    print("-" * 50)

    nodes = topology.get(
        "nodes",
        [],
    )

    connections = topology.get(
        "connections",
        [],
    )

    seen_ids = set()

    # ========================================================
    # NODE VALIDATION
    # ========================================================

    for node in nodes:

        node_id = str(
            node.get(
                "id",
                "",
            )
        ).strip()

        label = str(
            node.get(
                "label",
                "",
            )
        ).strip()

        # ====================================================
        # NODE ID
        # ====================================================

        if not node_id:

            msg = "[RENDER ERROR] Missing node id"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # SAFE GRAPHVIZ ID
        # ====================================================

        if not re.match(
            SAFE_NODE_ID_REGEX,
            node_id,
        ):

            msg = f"[RENDER ERROR] Unsafe node id: {node_id}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # DUPLICATE IDS
        # ====================================================

        if node_id in seen_ids:

            msg = f"[RENDER ERROR] Duplicate node id: {node_id}"

            print(msg)

            errors.append(msg)

        seen_ids.add(node_id)

        # ====================================================
        # LABEL
        # ====================================================

        if not label:

            msg = f"[RENDER ERROR] Missing label: {node_id}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # LABEL LENGTH
        # ====================================================

        elif len(label) > MAX_LABEL_LENGTH:

            msg = f"[RENDER ERROR] Label too long: {node_id}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # LABEL SAFETY
        # ====================================================

        elif not re.match(
            SAFE_LABEL_REGEX,
            label,
        ):

            msg = f"[RENDER ERROR] " f"Unsafe render label: " f"{node_id}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # CLUSTER
        # ====================================================

        cluster = str(
            node.get(
                "cluster",
                "",
            )
        ).strip()

        if not cluster:

            print(f"[WARN] Missing cluster: {node_id}")

        # ====================================================
        # DETACHED DOMAIN RENDER ISOLATION
        #
        # Detached Purdue domains should render
        # inside isolated visual clusters.
        #
        # This is a rendering safety validation,
        # NOT Purdue semantic validation.
        # ====================================================

        purdue = str(
            node.get(
                "purdue_level",
                "",
            )
        ).strip()

        zone = str(
            node.get(
                "zone",
                "",
            )
        ).strip()

        is_detached = (
            purdue
            in {
                "Onboard",
                "Unknown",
            }
            or zone == "external_security"
        )

        if is_detached:

            detached_cluster = str(
                node.get(
                    "detached_cluster",
                    "",
                )
            ).strip()

            if not detached_cluster:

                msg = (
                    f"[RENDER ERROR] "
                    f"Detached Purdue node missing "
                    f"detached_cluster: "
                    f"{node_id}"
                )

                print(msg)

                errors.append(msg)

            elif detached_cluster == cluster:

                msg = (
                    f"[RENDER ERROR] "
                    f"Detached Purdue node uses "
                    f"primary cluster: "
                    f"{node_id}"
                )

                print(msg)

                errors.append(msg)

        # ====================================================
        # RENDER COLOR
        # ====================================================

        render_color = str(
            node.get(
                "render_color",
                "",
            )
        ).strip()

        if not render_color:

            print(f"[WARN] Missing render color: {node_id}")

        elif not re.match(
            HEX_COLOR_REGEX,
            render_color,
        ):

            msg = (
                f"[RENDER ERROR] "
                f"Invalid render color: "
                f"{node_id} -> {render_color}"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # RENDER STYLE
        # ====================================================

        render_style = str(
            node.get(
                "render_style",
                "",
            )
        ).strip()

        if render_style and render_style not in VALID_RENDER_STYLES:

            msg = (
                f"[RENDER ERROR] "
                f"Invalid render style: "
                f"{node_id} -> {render_style}"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # RENDER BORDER
        # ====================================================

        render_border = str(
            node.get(
                "render_border",
                "",
            )
        ).strip()

        if render_border and not re.match(
            HEX_COLOR_REGEX,
            render_border,
        ):

            msg = (
                f"[RENDER ERROR] "
                f"Invalid render border color: "
                f"{node_id} -> {render_border}"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # RENDER PENWIDTH
        # ====================================================

        render_penwidth = str(
            node.get(
                "render_penwidth",
                "",
            )
        ).strip()

        if render_penwidth:

            try:

                value = float(render_penwidth)

                if value <= 0:

                    raise ValueError

            except ValueError:

                msg = (
                    f"[RENDER ERROR] "
                    f"Invalid render penwidth: "
                    f"{node_id} -> {render_penwidth}"
                )

                print(msg)

                errors.append(msg)

    # ========================================================
    # CONNECTION VALIDATION
    # ========================================================

    valid_node_ids = {
        str(
            n.get(
                "id",
                "",
            )
        ).strip()
        for n in nodes
    }

    seen_edges = set()

    for conn in connections:

        source = str(
            conn.get(
                "source",
                "",
            )
        ).strip()

        target = str(
            conn.get(
                "target",
                "",
            )
        ).strip()

        protocol = str(
            conn.get(
                "protocol",
                "",
            )
        ).strip()

        # ====================================================
        # SOURCE / TARGET
        # ====================================================

        if not source or not target:

            msg = f"[RENDER ERROR] Malformed connection: {conn}"

            print(msg)

            errors.append(msg)

            continue

        # ====================================================
        # NODE EXISTENCE
        # ====================================================

        if source not in valid_node_ids:

            msg = f"[RENDER ERROR] Unknown source node: {source}"

            print(msg)

            errors.append(msg)

        if target not in valid_node_ids:

            msg = f"[RENDER ERROR] Unknown target node: {target}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # PROTOCOL LABEL
        # ====================================================

        if not protocol:

            print(f"[WARN] Missing protocol label: {source} -> {target}")

        elif len(protocol) > MAX_LABEL_LENGTH:

            msg = (
                f"[RENDER ERROR] " f"Protocol label too long: " f"{source} -> {target}"
            )

            print(msg)

            errors.append(msg)

        elif not re.match(
            SAFE_LABEL_REGEX,
            protocol,
        ):

            msg = f"[RENDER ERROR] " f"Unsafe protocol label: " f"{source} -> {target}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # SELF LOOP
        # ====================================================

        if source == target:

            msg = f"[RENDER ERROR] Self-loop connection: {source}"

            print(msg)

            errors.append(msg)

        # ====================================================
        # DUPLICATE EDGE
        # ====================================================

        edge_key = (
            source,
            target,
            protocol,
            str(
                conn.get(
                    "transport",
                    "",
                )
            ).strip(),
            str(
                conn.get(
                    "media",
                    "",
                )
            ).strip(),
            str(
                conn.get(
                    "conduit_class",
                    "",
                )
            ).strip(),
        )

        if edge_key in seen_edges:

            msg = f"[RENDER ERROR] Duplicate edge: {edge_key}"

            print(msg)

            errors.append(msg)

        seen_edges.add(edge_key)

        # ====================================================
        # CONNECTION RENDER COLOR
        # ====================================================

        render_color = str(
            conn.get(
                "render_color",
                "",
            )
        ).strip()

        if render_color and not re.match(
            HEX_COLOR_REGEX,
            render_color,
        ):

            msg = (
                f"[RENDER ERROR] "
                f"Invalid connection render color: "
                f"{source} -> {target} -> {render_color}"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # CONNECTION RENDER STYLE
        # ====================================================

        render_style = str(
            conn.get(
                "render_style",
                "",
            )
        ).strip()

        if render_style and render_style not in VALID_EDGE_STYLES:

            msg = (
                f"[RENDER ERROR] "
                f"Invalid connection render style: "
                f"{source} -> {target} -> {render_style}"
            )

            print(msg)

            errors.append(msg)

        # ====================================================
        # CONNECTION RENDER PENWIDTH
        # ====================================================

        render_penwidth = str(
            conn.get(
                "render_penwidth",
                "",
            )
        ).strip()

        if render_penwidth:

            try:

                value = float(render_penwidth)

                if value <= 0:

                    raise ValueError

            except ValueError:

                msg = (
                    f"[RENDER ERROR] "
                    f"Invalid connection render penwidth: "
                    f"{source} -> {target} -> {render_penwidth}"
                )

                print(msg)

                errors.append(msg)

    # ========================================================
    # SUMMARY
    # ========================================================

    print(f"\nRENDER VALIDATION ERRORS: {len(errors)}")

    return sorted(errors)
