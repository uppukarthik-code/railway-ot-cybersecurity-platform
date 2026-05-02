"""
schema.py
Defines the structured JSON schema for an infrastructure network topology.
All LLM output is validated against this structure before being returned.
"""

from dataclasses import dataclass, field
from typing import Literal


# ── Node types recognised in critical infrastructure networks ─────────────────
NodeType = Literal[
    "firewall",
    "router",
    "switch",
    "server",
    "workstation",
    "plc",           # Programmable Logic Controller (OT)
    "rtu",           # Remote Terminal Unit (OT)
    "hmi",           # Human-Machine Interface (OT)
    "historian",     # OT data historian
    "dmz_host",
    "unknown",
]

# ── Security zone classification (IEC 62443 zone model) ──────────────────────
ZoneType = Literal[
    "corporate_it",  # Level 4/5 — enterprise IT
    "dmz",           # Level 3.5 — demilitarised zone
    "supervisory",   # Level 3   — SCADA / DCS
    "control",       # Level 2   — control systems
    "field",         # Level 1/0 — field devices / OT
]


@dataclass
class Node:
    id: str                          # e.g. "fw-01", "plc-03"
    label: str                       # human-readable name
    type: NodeType
    zone: ZoneType
    redundant: bool = False          # True if a redundant peer exists
    notes: str = ""


@dataclass
class Connection:
    source: str                      # Node id
    target: str                      # Node id
    protocol: str                    # e.g. "IEC 61850 GOOSE", "Modbus TCP", "HTTPS"
    encrypted: bool = False
    notes: str = ""


@dataclass
class Topology:
    name: str
    description: str
    nodes: list[Node] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "nodes": [n.__dict__ for n in self.nodes],
            "connections": [c.__dict__ for c in self.connections],
        }
