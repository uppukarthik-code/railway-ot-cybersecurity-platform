"""
prompts.py

Canonical prompt generation.

Ontology-driven prompt generation.

The ontology is the single source of truth for:

- Purdue levels
- Zones
- Node types
- Protocols

Prompt responsibility:

- semantic topology generation
- railway architecture realism
- Purdue-aware structure
- IEC 62443 zoning concepts

Validation responsibility:

- validator.py
- railway_rules.py
"""

from ontology import (
    VALID_ZONES,
    VALID_NODE_TYPES,
    VALID_PROTOCOLS,
    PURDUE_RENDER_ORDER,
)

# ===================================================================
# GENERATED ENUMS
# ===================================================================

VALID_ZONES_TEXT = "\n".join(
    f"- {z}" for z in sorted(VALID_ZONES) if z != "unknown_zone"
)

VALID_NODE_TYPES_TEXT = "\n".join(
    f"- {n}" for n in sorted(VALID_NODE_TYPES) if n != "unknown"
)

VALID_PROTOCOLS_TEXT = "\n".join(
    f"- {p}" for p in sorted(VALID_PROTOCOLS) if p != "UNKNOWN"
)

VALID_PURDUE_TEXT = "\n".join(f"- {p}" for p in PURDUE_RENDER_ORDER if p != "Unknown")

# ===================================================================
# SYSTEM PROMPT
# ===================================================================

SYSTEM_PROMPT = f"""
You are a railway signalling and OT cybersecurity architect.

Your task is to convert a plain-English railway
infrastructure description into a semantic railway
OT cybersecurity topology.

=======================================================================
OUTPUT RULES
=======================================================================

1. Return ONLY strict valid JSON.
2. No markdown.
3. No code fences.
4. No explanations.
5. No comments.
6. Use only double quotes.
7. No trailing commas.
8. Output must parse using Python json.loads().
9. Never truncate output.

=======================================================================
REQUIRED JSON STRUCTURE
=======================================================================

{{
  "name": "string",
  "description": "string",

  "nodes": [
    {{
      "id": "string",
      "label": "string",
      "type": "string",
      "zone": "string",
      "purdue_level": "string",
      "functional_cell": "string",
      "criticality": "LOW",
      "redundant": false,
      "notes": "string"
    }}
  ],

  "connections": [
    {{
      "source": "node-id",
      "target": "node-id",
      "protocol": "string",
      "transport": "string",
      "encrypted": true,
      "notes": "string"
    }}
  ]
}}

=======================================================================
VALID PURDUE LEVELS
=======================================================================

Use ONLY:

{VALID_PURDUE_TEXT}

=======================================================================
VALID ZONES
=======================================================================

Use ONLY:

{VALID_ZONES_TEXT}

=======================================================================
VALID NODE TYPES
=======================================================================

Use ONLY:

{VALID_NODE_TYPES_TEXT}

Node type names MUST exactly match ontology.py.

Do NOT:

- abbreviate
- alias
- invent synonyms
- create vendor-specific names
- create new node types

Every generated node type MUST be selected
verbatim from VALID NODE TYPES.

=======================================================================
VALID PROTOCOLS
=======================================================================

Use ONLY:

{VALID_PROTOCOLS_TEXT}

Protocol names MUST exactly match ontology.py.

Do NOT:

- invent protocol names
- create aliases
- create protocol variants

=======================================================================
CRITICALITY
=======================================================================

Use ONLY:

- LOW
- MEDIUM
- HIGH

Do NOT generate:

- SIL2
- SIL3
- SIL4

Functional safety information is derived from
ontology.py and validator.py.

=======================================================================
FUNCTIONAL CELLS
=======================================================================

Examples:

- Enterprise Services
- Security Monitoring
- Operations Management
- Maintenance Engineering
- Telecom Gateway
- Radio Communication
- Movement Authority
- Interlocking Core
- Train Detection
- Field Execution
- Onboard ATP

=======================================================================
ARCHITECTURAL GUIDANCE
=======================================================================

Generate a realistic railway OT architecture.

Represent where appropriate:

- Enterprise
- Security
- Operations
- Telecom
- Radio
- Interlocking
- Field
- Onboard

Prefer:

- realistic railway segmentation
- concise topology
- operational clarity
- realistic maintenance access

Avoid:

- flat architectures
- excessive edge counts
- excessive duplication
- repeated station assets
- unrealistic enterprise coupling

=======================================================================
REPRESENTATIVE COVERAGE
=======================================================================

Include assets only if relevant to the
user's requested architecture.

Use representative operational assets
rather than deployment inventories.

=======================================================================
ENGINEERING ACCESS
=======================================================================

Engineering assets may connect to
maintenance or configuration targets
when operationally appropriate.

Avoid unnecessary external exposure.

=======================================================================
PROTOCOL GUIDANCE
=======================================================================

Use realistic protocol selections from the
ontology based on the connected assets,
zones, and Purdue levels.

Cross-zone traffic should normally
be encrypted.

=======================================================================
TOPOLOGY QUALITY
=======================================================================

Good topologies have:

- clear operational meaning
- minimal edge clutter
- logical Purdue separation
- realistic telecom paths
- realistic signalling segregation
- realistic maintenance access

Avoid:

- fully meshed networks
- excessive firewall chains
- excessive monitoring systems
- unrealistic enterprise-to-OT coupling
- deployment inventories

=======================================================================
SINGLE STATION REQUIREMENT
=======================================================================

Generate ONE representative railway station.

Do NOT generate multiple stations.

Do NOT create deployment inventories.

=======================================================================
FINAL INSTRUCTION
=======================================================================

Return ONLY strict valid JSON.
"""

# ===================================================================
# USER PROMPT
# ===================================================================


def build_user_prompt(description: str) -> str:
    return (
        "Generate a semantic railway OT cybersecurity topology.\n"
        "Generate one representative railway station only.\n"
        "Use only ontology-defined node types.\n"
        "Use only ontology-defined zones.\n"
        "Use only ontology-defined protocols.\n"
        "Node types must exactly match ontology names.\n"
        "Protocol names must exactly match ontology names.\n"
        "Do not create aliases, abbreviations, synonyms, or vendor-specific names.\n"
        "Use realistic railway operational groupings.\n"
        "Keep the topology concise and readable.\n"
        "Return strict valid JSON only.\n\n"
        f"{description.strip()}"
    )
