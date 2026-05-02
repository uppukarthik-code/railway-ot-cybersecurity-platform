# infra-topology-generator

A Python CLI tool that generates structured, validated network topology JSON for
critical infrastructure systems from plain-English descriptions.

Powered by the Claude API. Compliance validation aligned with **IEC 62443** security
zone design principles and **IEC 61850** substation communication standards.

---

## What it does

1. Takes a plain-English description of a network (typed or from a file)
2. Calls Claude to generate a structured JSON topology (nodes, connections, zones)
3. Runs rule-based IEC 62443 compliance checks against the output
4. Prints the topology JSON and a compliance report

This mirrors the core workflow of an AI-assisted infrastructure design platform:
natural language in → validated, deployment-ready architecture out.

---

## Example output

Input (`examples/substation.txt`):
```
A power utility substation network connecting corporate IT systems to OT equipment.
The OT side includes PLCs, RTUs, an HMI, and a SCADA server...
```

Output (truncated):
```json
{
  "name": "Power Utility Substation Network",
  "description": "Segmented IT/OT network with DMZ, IEC 61850 OT communication, and redundant PLCs.",
  "nodes": [
    { "id": "fw-01", "label": "Perimeter Firewall", "type": "firewall", "zone": "corporate_it", "redundant": false },
    { "id": "plc-01", "label": "Breaker PLC Primary", "type": "plc", "zone": "control", "redundant": true },
    { "id": "rtu-01", "label": "Field RTU 1", "type": "rtu", "zone": "field", "redundant": false }
  ],
  "connections": [
    { "source": "scada-01", "target": "plc-01", "protocol": "IEC 61850 MMS", "encrypted": true }
  ]
}
```

Compliance report:
```
── Compliance Report (IEC 62443) ────────────────────────────────
  ✓ [PASS] IEC62443-OT-ISOLATION
      All OT nodes are correctly isolated from the corporate IT zone.
  ✓ [PASS] IEC62443-DMZ-REQUIRED
      DMZ zone is present or not required for this topology.
  ✓ [PASS] IEC62443-ENCRYPTED-CROSS-ZONE
      All cross-zone connections are encrypted.

  Result: 3 passed, 0 failed, 0 warnings
  ✓ Topology is IEC 62443 compliant
─────────────────────────────────────────────────────────────────
```

---

## Setup

```bash
git clone https://github.com/kchimbodza/infra-topology-generator.git
cd infra-topology-generator
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
```

---

## Usage

**Interactive mode** (type your description):
```bash
python main.py
```

**File input:**
```bash
python main.py --input examples/substation.txt
```

**Save topology to file:**
```bash
python main.py --input examples/substation.txt --output topology.json
```

**Skip compliance validation:**
```bash
python main.py --input examples/substation.txt --no-validate
```

---

## Project structure

```
infra-topology-generator/
├── main.py          # CLI entry point — orchestrates generation and validation
├── schema.py        # Topology data model (Node, Connection, Topology dataclasses)
├── prompts.py       # System prompt and user prompt templates for the LLM
├── validator.py     # Rule-based IEC 62443 compliance checks
└── examples/
    ├── substation.txt       # Power utility substation scenario
    └── water_treatment.txt  # Municipal water treatment facility scenario
```

---

## Compliance rules

| Rule | Standard | Description |
|------|----------|-------------|
| `IEC62443-OT-ISOLATION` | IEC 62443 | OT nodes (PLC, RTU, HMI, historian) must not reside in the corporate IT zone |
| `IEC62443-DMZ-REQUIRED` | IEC 62443 | A DMZ must exist when both corporate IT and OT zones are present |
| `IEC62443-ENCRYPTED-CROSS-ZONE` | IEC 62443 | All connections crossing zone boundaries must be encrypted |

---

## Standards reference

- **IEC 62443** — Security for industrial automation and control systems. Defines security levels and zone/conduit model used for node zone classification in this tool.
- **IEC 61850** — Communication networks and systems in substations. Protocol names (GOOSE, MMS, SAMPLED VALUES) used in generated connection labels.
