"""
main.py

CLI entry point for the railway OT topology generator.

PIPELINE:
    LLM
    -> normalize
    -> filter
    -> classify
    -> stack inference
    -> security enrichment
    -> conduit synthesis
    -> cluster
    -> validation
    -> risk analysis
    -> export
"""

import argparse
import json
import os
import re
import sys
import uuid

from pathlib import Path

import anthropic

from dotenv import load_dotenv

from json_repair import repair_json

from prompts import SYSTEM_PROMPT, build_user_prompt

from railway_rules import (
    FORBIDDEN_NODE_TYPES,
    FORBIDDEN_LABEL_PATTERNS,
)

from ontology import (
    VALID_NODE_TYPES,
)

from aliases import (
    normalize_node_type,
    normalize_protocol,
    normalize_zone,
    normalize_purdue,
    normalize_transport,
    normalize_bearer,
    normalize_media,
)
from schema_validator import ensure_topology_schema

from validator import validate, print_report

from export_drawio import export_drawio
from export_graphviz import export_graphviz
from export_purdue import export_purdue

from classifier import classify_topology
from clustering import cluster_topology
from conduits import build_conduits
from security_enrichment import apply_security_controls
from infer_connection_stack import infer_communication_stack

from risk_engine import analyze_risk

from debug import (
    debug_graphviz_layout,
    debug_pipeline_stage,
    export_topology_snapshot,
)

from validators import (
    validate_assets,
    validate_links,
    validate_zones,
    validate_purdue,
    validate_protocols,
    validate_rendering,
)

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

# ============================================================
# OUTPUT PATHS
# ============================================================

OUTPUTS_DIR = PROJECT_ROOT / "outputs"

FRONTEND_DATA_DIR = PROJECT_ROOT / "frontend" / "src" / "data"

DEFAULT_JSON_OUTPUT = OUTPUTS_DIR / "kavach_topology.json"

FRONTEND_JSON_OUTPUT = FRONTEND_DATA_DIR / "topology.json"


# ============================================================
# SAFE JSON EXTRACTION
# ============================================================


def extract_json(raw: str) -> str:

    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if not match:
        raise ValueError("No JSON object found.")

    return match.group(0)


def normalize_node(node: dict) -> dict:
    """
    PURE CANONICAL NORMALIZATION ONLY

    RESPONSIBILITIES
    ----------------
    - canonical field normalization
    - structural cleanup
    - stable ID generation
    - deterministic normalization
    - canonical enum normalization

    DOES NOT
    --------
    - infer ontology semantics
    - infer safety
    - infer security
    - infer risk
    - infer Purdue defaults
    - infer SL/SIL
    - infer hosting semantics
    - infer attack surface
    - apply governance logic
    """

    # ========================================================
    # RAW INPUTS
    # ========================================================

    raw_type = str(
        node.get(
            "type",
            "",
        )
    ).strip()

    raw_zone = str(
        node.get(
            "zone",
            "",
        )
    ).strip()

    raw_purdue = str(
        node.get(
            "purdue_level",
            "",
        )
    ).strip()

    label = str(
        node.get(
            "label",
            node.get(
                "id",
                "",
            ),
        )
    ).strip()

    # ========================================================
    # EMPTY LABEL RECOVERY
    # ========================================================

    if not label:

        label = f"unnamed_node_{uuid.uuid4().hex[:8]}"
    # ========================================================
    # CANONICAL NORMALIZATION
    # ========================================================

    node_type = normalize_node_type(
        raw_type,
    )

    zone = normalize_zone(
        raw_zone,
    )

    purdue_level = normalize_purdue(
        raw_purdue,
    )

    # ========================================================
    # STABLE NODE ID
    # ========================================================

    raw_id = str(
        node.get(
            "id",
            "",
        )
    ).strip()

    if raw_id:

        node_id = raw_id

    else:

        safe_label = re.sub(
            r"[^a-z0-9]+",
            "_",
            label.lower(),
        ).strip("_")

        node_id = f"{node_type}_{safe_label}"

    # ========================================================
    # FINAL CANONICAL NODE
    # ========================================================

    normalized = {
        # ----------------------------------------------------
        # PIPELINE
        # ----------------------------------------------------
        "normalized": True,
        "classified": False,
        "validated": False,
        # ----------------------------------------------------
        # CORE
        # ----------------------------------------------------
        "id": node_id,
        "label": label,
        "type": node_type,
        "zone": zone,
        "purdue_level": purdue_level,
        # ----------------------------------------------------
        # STRUCTURAL
        # ----------------------------------------------------
        "redundant": bool(
            node.get(
                "redundant",
                False,
            )
        ),
        # ----------------------------------------------------
        # OPTIONAL RAW USER FIELDS
        # ----------------------------------------------------
        "vendor": str(
            node.get(
                "vendor",
                "",
            )
        ).strip(),
        "model": str(
            node.get(
                "model",
                "",
            )
        ).strip(),
        "firmware_version": str(
            node.get(
                "firmware_version",
                "",
            )
        ).strip(),
        "operating_system": str(
            node.get(
                "operating_system",
                "",
            )
        ).strip(),
        # ----------------------------------------------------
        # NOTES
        # ----------------------------------------------------
        "notes": str(
            node.get(
                "notes",
                "",
            )
        ).strip(),
    }

    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "[NORMALIZED NODE] "
        f"LABEL={label} | "
        f"TYPE={node_type} | "
        f"ZONE={zone} | "
        f"PURDUE={purdue_level}"
    )

    return normalized


def normalize_connection(
    conn: dict,
    idx: int,
) -> dict:
    """
    PURE CANONICAL NORMALIZATION ONLY

    RESPONSIBILITIES
    ----------------
    - canonical field normalization
    - structural cleanup
    - ID stabilization
    - protocol normalization
    - transport normalization
    - endpoint normalization

    DOES NOT
    --------
    - infer security semantics
    - infer trust
    - infer safety
    - infer conduit semantics
    - infer open transmission
    - infer wireless
    - infer encryption
    - infer cross-zone
    - infer risk
    """

    # ========================================================
    # RAW VALUES
    # ========================================================

    raw_source = str(
        conn.get(
            "source",
            "",
        )
    ).strip()

    raw_target = str(
        conn.get(
            "target",
            "",
        )
    ).strip()

    # ========================================================
    # REQUIRED ENDPOINTS
    # ========================================================

    if not raw_source or not raw_target:

        print("[WARN] Connection missing source/target.")

        return {}

    raw_protocol = str(
        conn.get(
            "protocol",
            "",
        )
    ).strip()

    raw_transport = str(
        conn.get(
            "transport",
            "",
        )
    ).strip()

    raw_bearer = str(
        conn.get(
            "bearer",
            "",
        )
    ).strip()

    raw_media = str(
        conn.get(
            "media",
            "",
        )
    ).strip()

    # ========================================================
    # NORMALIZATION
    # ========================================================

    protocol = normalize_protocol(
        raw_protocol,
    )

    transport = normalize_transport(
        raw_transport,
    )

    bearer = normalize_bearer(
        raw_bearer,
    )

    media = normalize_media(
        raw_media,
    )

    # ========================================================
    # CONNECTION ID
    # ========================================================

    raw_id = str(
        conn.get(
            "id",
            "",
        )
    ).strip()

    if raw_id:

        connection_id = raw_id

    else:

        safe_source = re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            raw_source,
        ).strip("_")

        safe_target = re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            raw_target,
        ).strip("_")

        safe_protocol = re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            protocol,
        ).strip("_")

        connection_id = (
            f"edge_{idx}_" f"{safe_source}_" f"{safe_target}_" f"{safe_protocol}"
        )

    # ========================================================
    # NOTES
    # ========================================================

    notes = str(
        conn.get(
            "notes",
            "",
        )
    ).strip()

    # ========================================================
    # PHYSICAL PATH
    # ========================================================

    physical_path = str(
        conn.get(
            "physical_path",
            "",
        )
    ).strip()

    # ========================================================
    # FINAL CANONICAL OBJECT
    # ========================================================

    normalized = {
        # ----------------------------------------------------
        # PIPELINE
        # ----------------------------------------------------
        "normalized": True,
        "classified": False,
        "validated": False,
        # ----------------------------------------------------
        # CORE
        # ----------------------------------------------------
        "id": connection_id,
        "source": raw_source,
        "target": raw_target,
        # ----------------------------------------------------
        # COMMUNICATION STACK
        # ----------------------------------------------------
        "protocol": protocol,
        "transport": transport,
        "bearer": bearer,
        "media": media,
        "physical_path": physical_path,
        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------
        "notes": notes,
    }

    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "[NORMALIZED CONNECTION] "
        f"{raw_source} -> {raw_target} | "
        f"PROTO={protocol} | "
        f"TRANSPORT={transport} | "
        f"BEARER={bearer} | "
        f"MEDIA={media}"
    )

    return normalized


# ============================================================
# NORMALIZE TOPOLOGY
# ============================================================


def normalize_topology(topology: dict) -> dict:

    if not isinstance(topology, dict):

        topology = {}

    # SCHEMA ENFORCEMENT
    # ========================================================

    topology = ensure_topology_schema(
        topology,
    )

    # ========================================================
    # TOPOLOGY ID
    # ========================================================

    topology.setdefault(
        "topology_id",
        str(uuid.uuid4()),
    )

    topology.setdefault(
        "generator_version",
        "1.0.0",
    )

    topology.setdefault(
        "standards",
        [
            "IEC62443",
            "EN50126",
            "EN50129",
            "EN50159",
        ],
    )

    topology.setdefault("name", "Railway OT Topology")

    topology.setdefault("nodes", [])

    topology.setdefault("connections", [])

    normalized_nodes = []

    seen_ids = set()

    label_to_id = {}

    for raw_node in topology.get("nodes", []):

        if not isinstance(raw_node, dict):
            continue

        node = normalize_node(raw_node)

        node_id = node["id"]

        if not node_id:
            continue

        if node_id in seen_ids:
            continue

        seen_ids.add(node_id)

        normalized_nodes.append(node)

        # ========================================================
        # CANONICAL LOOKUP MAP
        # ========================================================

        label = node["label"].strip()

        if label:

            label_to_id[label] = node["id"]

            label_to_id[label.lower()] = node["id"]

    topology["nodes"] = normalized_nodes

    valid_ids = {n["id"] for n in normalized_nodes}

    normalized_connections = []

    for idx, raw_conn in enumerate(topology.get("connections", [])):

        if not isinstance(raw_conn, dict):
            continue

        conn = normalize_connection(raw_conn, idx)

        if not conn:
            continue

        # ========================================================
        # CANONICAL CONNECTION RESOLUTION
        # ========================================================

        conn["source"] = label_to_id.get(
            conn["source"],
            label_to_id.get(
                conn["source"].lower(),
                conn["source"],
            ),
        )

        conn["target"] = label_to_id.get(
            conn["target"],
            label_to_id.get(
                conn["target"].lower(),
                conn["target"],
            ),
        )

        if conn["source"] not in valid_ids:
            continue

        if conn["target"] not in valid_ids:
            continue

        normalized_connections.append(conn)

    topology["connections"] = normalized_connections

    topology = set_pipeline_stage(
        topology,
        "normalized",
    )

    return topology


# ============================================================
# FILTER TOPOLOGY
# ============================================================


def filter_topology(topology: dict) -> dict:

    filtered_nodes = []

    for node in topology.get("nodes", []):

        label = node.get("label", "").lower().strip()

        node_type = node.get("type", "").lower().strip()

        forbidden = False

        if node_type in FORBIDDEN_NODE_TYPES or node_type not in VALID_NODE_TYPES:

            forbidden = True

        for pattern in FORBIDDEN_LABEL_PATTERNS:

            if re.search(
                pattern,
                label,
                re.IGNORECASE,
            ):
                forbidden = True
                break

        if not forbidden:

            filtered_nodes.append(node)

    topology["nodes"] = filtered_nodes

    valid_ids = {n["id"] for n in filtered_nodes}

    filtered_connections = []

    malformed = 0

    for conn in topology.get("connections", []):

        source = conn.get("source")

        target = conn.get("target")

        if source not in valid_ids or target not in valid_ids:

            malformed += 1
            continue

        filtered_connections.append(conn)

    topology["connections"] = filtered_connections

    if malformed:

        print(f"[WARN] Removed {malformed} malformed connections.")

    topology = set_pipeline_stage(
        topology,
        "filtered",
    )

    return topology


# ============================================================
# PIPELINE STAGE
# ============================================================


def set_pipeline_stage(
    topology: dict,
    stage: str,
) -> dict:

    topology["pipeline_stage"] = stage

    topology.setdefault(
        "pipeline_history",
        [],
    )

    history = topology.setdefault(
        "pipeline_history",
        [],
    )

    if not history or history[-1] != stage:
        history.append(stage)

    return topology


# ============================================================
# PIPELINE
# ============================================================


def run_pipeline(
    topology: dict,
    with_conduits: bool = True,
    debug: bool = False,
) -> dict:

    # ========================================================
    # FILTER
    # ========================================================

    topology = filter_topology(topology)

    if debug:

        debug_pipeline_stage(
            topology,
            "AFTER FILTER",
        )

    # ========================================================
    # CLASSIFICATION
    # ========================================================

    topology = classify_topology(topology)

    topology = set_pipeline_stage(
        topology,
        "classified",
    )

    if debug:

        debug_pipeline_stage(
            topology,
            "AFTER CLASSIFICATION",
        )

    # ========================================================
    # COMMUNICATION STACK INFERENCE
    # ========================================================

    topology = infer_communication_stack(topology)
    topology = set_pipeline_stage(
        topology,
        "stack_inferred",
    )

    if debug:

        debug_pipeline_stage(
            topology,
            "AFTER STACK INFERENCE",
        )

    # ========================================================
    # SECURITY ENRICHMENT
    # ========================================================

    topology = apply_security_controls(topology)
    topology = set_pipeline_stage(
        topology,
        "security_enriched",
    )

    if debug:

        debug_pipeline_stage(
            topology,
            "AFTER SECURITY ENRICHMENT",
        )

    # ========================================================
    # CONDUITS
    # ========================================================

    if with_conduits:

        topology = build_conduits(topology)

        topology = set_pipeline_stage(
            topology,
            "conduits_built",
        )

    else:

        topology = set_pipeline_stage(
            topology,
            "conduits_skipped",
        )

    # ========================================================
    # CLUSTERING
    # ========================================================

    topology = cluster_topology(topology)

    topology = set_pipeline_stage(
        topology,
        "clustered",
    )
    if debug:

        debug_pipeline_stage(
            topology,
            "AFTER CLUSTERING",
        )

    return topology


# ============================================================
# SAVE OUTPUTS
# ============================================================


def save_outputs(topology: dict, output_path: str | None = None):

    output_json = json.dumps(
        topology,
        indent=2,
        ensure_ascii=False,
    )

    OUTPUTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FRONTEND_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if output_path:

        output_file = Path(output_path).resolve()

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file.write_text(
            output_json,
            encoding="utf-8",
        )

        print(f"[OK] Saved: {output_file}")

    DEFAULT_JSON_OUTPUT.write_text(
        output_json,
        encoding="utf-8",
    )

    FRONTEND_JSON_OUTPUT.write_text(
        output_json,
        encoding="utf-8",
    )


# ============================================================
# LLM CALL
# ============================================================


def call_llm(description: str) -> dict:

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("\nGenerating topology...", flush=True)

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8000,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(description),
            }
        ],
    )

    raw = message.content[0].text.strip()

    try:

        extracted = extract_json(raw)

        topology = json.loads(extracted)

        print("[OK] Valid JSON received.")

        topology = set_pipeline_stage(
            topology,
            "normalized",
        )

        return normalize_topology(topology)

    except Exception:

        print("[WARN] Invalid JSON detected.")

    try:

        repaired = repair_json(raw)

        repaired = extract_json(repaired)

        topology = json.loads(repaired)

        print("[OK] JSON repaired successfully.")

        return normalize_topology(topology)

    except Exception as e:

        print("\n[ERROR] JSON repair failed.")

        print(e)

        sys.exit(1)


# ============================================================
# INPUT DESCRIPTION
# ============================================================


def get_description(input_file: str | None) -> str:

    if input_file:

        with open(input_file, encoding="utf-8") as f:

            return f.read().strip()

    print("\nDescribe railway OT infrastructure.")

    print("Press Enter twice to finish.\n")

    lines = []

    while True:

        line = input()

        if line == "" and lines and lines[-1] == "":
            break

        lines.append(line)

    return "\n".join(lines).strip()


# ============================================================
# MAIN
# ============================================================


def main():

    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Railway OT Semantic Topology Generator"
    )

    parser.add_argument(
        "--input",
        "-i",
        default=None,
    )

    parser.add_argument(
        "--output",
        "-o",
        default=None,
    )

    parser.add_argument(
        "--debug",
        action="store_true",
    )

    parser.add_argument(
        "--with-conduits",
        action="store_true",
    )

    parser.add_argument(
        "--no-validate",
        action="store_true",
    )

    args = parser.parse_args()

    # ========================================================
    # API KEY
    # ========================================================

    if "ANTHROPIC_API_KEY" not in os.environ:

        print("[ERROR] Missing ANTHROPIC_API_KEY")

        sys.exit(1)

    print("\n── Railway Semantic Architecture Generator ──")

    # ========================================================
    # DESCRIPTION
    # ========================================================

    description = get_description(args.input)

    if not description:

        print("[ERROR] Empty description.")

        sys.exit(1)

    # ========================================================
    # GENERATE
    # ========================================================

    raw_topology = call_llm(description)

    # ========================================================
    # RAW DEBUG
    # ========================================================

    if args.debug:

        debug_pipeline_stage(
            raw_topology,
            "RAW LLM OUTPUT",
        )

        export_topology_snapshot(
            raw_topology,
            "outputs/raw_llm_output.json",
        )

    # ========================================================
    # RAW VALIDATION
    # ========================================================

    if args.debug:

        validation_report = {
            "asset_errors": validate_assets(raw_topology),
            "link_errors": validate_links(raw_topology),
            "zone_errors": validate_zones(raw_topology),
            "purdue_errors": validate_purdue(raw_topology),
            "protocol_errors": validate_protocols(raw_topology),
        }

        print("\n" + "=" * 60)
        print("RAW TOPOLOGY VALIDATION")
        print("=" * 60)

        total_errors = 0

        for category, errors in validation_report.items():

            print(f"\n{category}")

            if not errors:

                print("  OK")

            else:

                total_errors += len(errors)

                for err in errors:

                    print(f"  - {err}")

        print(f"\nRAW VALIDATION ERRORS: {total_errors}")

    # ========================================================
    # PIPELINE
    # ========================================================

    pipeline_topology = run_pipeline(
        raw_topology,
        with_conduits=args.with_conduits,
        debug=args.debug,
    )

    # ========================================================
    # POST VALIDATION
    # ========================================================

    if args.debug:

        validation_report = {
            "asset_errors": validate_assets(pipeline_topology),
            "link_errors": validate_links(pipeline_topology),
            "zone_errors": validate_zones(pipeline_topology),
            "purdue_errors": validate_purdue(pipeline_topology),
            "protocol_errors": validate_protocols(pipeline_topology),
            "render_errors": validate_rendering(pipeline_topology),
        }

        print("\n" + "=" * 60)
        print("POST PIPELINE VALIDATION")
        print("=" * 60)

        total_errors = 0

        for category, errors in validation_report.items():

            print(f"\n{category}")

            if not errors:

                print("  OK")

            else:

                total_errors += len(errors)

                for err in errors:

                    print(f"  - {err}")

        print(f"\nPIPELINE VALIDATION ERRORS: {total_errors}")

    # ========================================================
    # CORE VALIDATION
    # ========================================================

    if not args.no_validate:

        findings = validate(pipeline_topology)

        print_report(findings)

        analyze_risk(pipeline_topology)

    # ========================================================
    # SAVE OUTPUTS
    # ========================================================

    save_outputs(
        pipeline_topology,
        args.output,
    )

    OUTPUTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # RENDERING DEBUG
    # ========================================================

    print("\nFINAL RENDER NODES:")
    for n in pipeline_topology["nodes"]:
        print(
            n["label"],
            "|",
            n["type"],
            "|",
            n["purdue_level"],
        )
    print("\nFINAL CONNECTIONS:")
    for conn in pipeline_topology["connections"]:
        print(
            conn["source"],
            "->",
            conn["target"],
        )

    # ========================================================
    # EXPORT
    # ========================================================

    print("\nGenerating architecture outputs...")

    # ========================================================
    # GRAPHVIZ SEMANTIC TOPOLOGY
    # ========================================================

    export_graphviz(
        pipeline_topology,
        str(OUTPUTS_DIR / "kavach_graphviz"),
    )

    # ========================================================
    # PURDUE SECURITY ARCHITECTURE
    # ========================================================

    export_purdue(
        pipeline_topology,
        str(OUTPUTS_DIR / "kavach_purdue"),
    )

    # ========================================================
    # DRAWIO ENGINEERING DIAGRAM
    # ========================================================

    export_drawio(
        pipeline_topology,
        str(OUTPUTS_DIR / "kavach.drawio"),
    )

    print("\nAll architecture outputs generated.")

    # ========================================================
    # LAYOUT DEBUG
    # ========================================================

    if args.debug:

        try:

            print("\n" + "=" * 60)
            print("GRAPH LAYOUT DEBUGGING")
            print("=" * 60)

            print("\nDEBUG GRAPHVIZ TOPOLOGY")
            debug_graphviz_layout(str(OUTPUTS_DIR / "kavach_graphviz.dot"))

            print("\nDEBUG PURDUE RENDER")
            debug_graphviz_layout(str(OUTPUTS_DIR / "kavach_purdue.dot"))

        except Exception as e:

            print("\n[DEBUG ERROR]")

            print(e)


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()
