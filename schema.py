"""
schema.py
Railway / OT topology schema with IEC 62443 + Railway signalling extensions.
"""

from dataclasses import dataclass, field
from typing import Literal


# ============================================================
# NODE TYPES
# ============================================================

NodeType = Literal[

    # Core IT
    "firewall",
    "router",
    "switch",
    "server",
    "workstation",

    # OT Generic
    "plc",
    "rtu",
    "hmi",
    "historian",
    "dmz_host",

    # Railway / Kavach
    "ei",                       # Electronic Interlocking
    "kavach_station",           # Station Kavach
    "kavach_onboard",           # Onboard ATP
    "radio_base_station",
    "telecom_gateway",
    "maintenance_terminal",
    "safety_server",

    # Security
    "siem",
    "ids",
    "ips",
    "vpn_gateway",
    "key_management_server",
    "jump_server",
    "data_diode",

    # Infrastructure
    "ntp_server",
    "gps_clock",

    # Fallback
    "unknown",
]


# ============================================================
# ZONES
# ============================================================

ZoneType = Literal[

    # Enterprise
    "enterprise_it",

    # Security Boundary
    "idmz",

    # OT Supervisory
    "supervisory",

    # Railway-specific
    "station_control",
    "interlocking",
    "radio_network",
    "field",
    "onboard",
    "maintenance",
    "security_management",
    "telecom",
]


# ============================================================
# NODE
# ============================================================

@dataclass
class Node:

    id: str
    label: str

    type: NodeType
    zone: ZoneType

    redundant: bool = False

    notes: str = ""

    # Railway / cybersecurity extensions

    safety_critical: bool = False

    security_level: str = ""

    vendor: str = ""

    protocol_stack: list[str] = field(
        default_factory=list
    )


# ============================================================
# CONNECTION
# ============================================================

@dataclass
class Connection:

    source: str
    target: str

    protocol: str

    encrypted: bool = False

    notes: str = ""

    conduit_type: str = ""

    trusted: bool = True

    safety_related: bool = False


# ============================================================
# TOPOLOGY
# ============================================================

@dataclass
class Topology:

    name: str

    description: str

    nodes: list[Node] = field(
        default_factory=list
    )

    connections: list[Connection] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

    # ========================================================
    # EXPORT
    # ========================================================

    def to_dict(self) -> dict:

        return {

            "name":
                self.name,

            "description":
                self.description,

            "metadata":
                self.metadata,

            "nodes":
                [
                    n._dict_
                    for n in self.nodes
                ],

            "connections":
                [
                    c._dict_
                    for c in self.connections
                ],
        }