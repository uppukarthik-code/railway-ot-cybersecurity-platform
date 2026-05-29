"""
schema.py

FINAL HARDENED CANONICAL RAILWAY OT TOPOLOGY SCHEMA

IEC62443 + EN50126 + EN50129 + EN50159 + Kavach

DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- Deterministic canonical schema
- No inference logic
- No validation logic
- No renderer logic
- No policy logic
- Fully pipeline aligned
"""

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from typing import (
    Literal,
    TypeAlias,
)

from ontology import (
    ASSET_ONTOLOGY,
    ZONE_ONTOLOGY,
    PROTOCOL_ONTOLOGY,
    TRANSPORT_ONTOLOGY,
    BEARER_ONTOLOGY,
    MEDIA_ONTOLOGY,
    PURDUE_LEVELS,
)

# ============================================================
# CANONICAL TYPES
# ============================================================

SemanticLayerType: TypeAlias = Literal[*tuple(list(PURDUE_LEVELS.keys()) + ["Unknown"])]

NodeType: TypeAlias = Literal[*tuple(list(ASSET_ONTOLOGY.keys()) + ["unknown"])]

ZoneType: TypeAlias = Literal[*tuple(list(ZONE_ONTOLOGY.keys()) + ["unknown"])]

ProtocolType: TypeAlias = Literal[*tuple(list(PROTOCOL_ONTOLOGY.keys()) + ["UNKNOWN"])]

TransportType: TypeAlias = Literal[
    *tuple(list(TRANSPORT_ONTOLOGY.keys()) + ["unknown"])
]

BearerType: TypeAlias = Literal[*tuple(list(BEARER_ONTOLOGY.keys()) + ["unknown"])]

MediaType: TypeAlias = Literal[*tuple(list(MEDIA_ONTOLOGY.keys()) + ["unknown"])]

# ============================================================
# FUNCTIONAL CELLS
# ============================================================

FunctionalCellType: TypeAlias = Literal[
    "Enterprise Services",
    "Security Monitoring",
    "SOC Operations",
    "Key Management",
    "Operations Management",
    "Maintenance Engineering",
    "Maintenance Access",
    "Movement Authority",
    "Interlocking Core",
    "Train Detection",
    "Wayside Control",
    "Field Execution",
    "Radio Communication",
    "Trackside Radio",
    "Onboard Radio",
    "Telecom Gateway",
    "Core Transport",
    "Fiber Backbone",
    "Onboard ATP",
    "Event Logging",
    "Detached Domains",
    "General",
]

# ============================================================
# CONNECTION TYPES
# ============================================================

ConnectionType: TypeAlias = Literal[
    "CONTROL",
    "MONITORING",
    "SAFETY",
    "ENGINEERING",
    "AUTHENTICATION",
    "RF",
    "TIME_SYNC",
    "LOGGING",
    "MANAGEMENT",
    "TELEMETRY",
    "UNKNOWN",
]

# ============================================================
# CRITICALITY
# ============================================================

CriticalityType: TypeAlias = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "SIL2",
    "SIL3",
    "SIL4",
]

# ============================================================
# EXPOSURE TYPES
# ============================================================

ExposureType: TypeAlias = Literal[
    "INTERNET",
    "REMOTE_ACCESS",
    "WIRELESS",
    "MAINTENANCE",
    "USB",
    "VENDOR",
]

# ============================================================
# PIPELINE STATE
# ============================================================


@dataclass
class PipelineState:

    normalized: bool = False

    classified: bool = False

    validated: bool = False

    classification_confidence: float = 0.0

    inferred_fields: list[str] = field(default_factory=list)


# ============================================================
# NODE
# ============================================================


@dataclass
class Node:

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    pipeline: PipelineState = field(default_factory=PipelineState)

    # --------------------------------------------------------
    # CORE
    # --------------------------------------------------------

    id: str = ""

    label: str = ""

    type: NodeType = "unknown"

    zone: ZoneType = "unknown"

    purdue_level: SemanticLayerType = "Unknown"

    # --------------------------------------------------------
    # FUNCTIONAL MODEL
    # --------------------------------------------------------

    functional_domain: str = ""

    functional_role: str = ""

    functional_cell: FunctionalCellType = "General"

    safety_function: str = ""

    safety_domain: str = "non_vital"

    description: str = ""

    # --------------------------------------------------------
    # ARCHITECTURE
    # --------------------------------------------------------

    cluster: str = ""

    redundant: bool = False

    is_trusted_zone: bool = False

    detached_domain: bool = False

    rolling_stock_asset: bool = False

    externally_hosted: bool = False

    asset_owner: str = ""

    # --------------------------------------------------------
    # SAFETY / SECURITY
    # --------------------------------------------------------

    criticality: CriticalityType = "LOW"

    safety_critical: bool = False

    functional_safety_level: str = ""

    security_level: str = ""

    security_level_target: str = ""

    security_safety_coupled: bool = False

    trust_domain: str = ""

    # --------------------------------------------------------
    # EXPOSURE
    # --------------------------------------------------------

    exposure_vectors: list[ExposureType] = field(default_factory=list)

    # --------------------------------------------------------
    # ENGINEERING / MAINTENANCE
    # --------------------------------------------------------

    supports_logic_download: bool = False

    offline_engineering_asset: bool = False

    portable_media_risk: bool = False

    maintenance_mode: bool = False

    logic_download_capable: bool = False

    configuration_change_capable: bool = False

    engineering_access: bool = False

    # --------------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------------

    patch_window_days: int = 0

    availability_constraint: str = ""

    downtime_tolerance_minutes: int = 0

    # --------------------------------------------------------
    # ENGINEERING METADATA
    # --------------------------------------------------------

    vendor: str = ""

    model: str = ""

    firmware_version: str = ""

    operating_system: str = ""

    serial_number: str = ""

    protocol_stack: list[ProtocolType] = field(default_factory=list)

    # --------------------------------------------------------
    # ATTACK MODEL
    # --------------------------------------------------------

    mitre_techniques: list[str] = field(default_factory=list)

    attack_surface: bool = False

    radio_exposed: bool = False

    open_network_exposed: bool = False

    # --------------------------------------------------------
    # RENDERING
    # --------------------------------------------------------

    render_color: str = ""

    render_shape: str = ""

    render_rank: str = ""

    render_group: str = ""

    # --------------------------------------------------------
    # PROVENANCE
    # --------------------------------------------------------

    sources: dict = field(default_factory=dict)

    # --------------------------------------------------------
    # NOTES
    # --------------------------------------------------------

    notes: str = ""


# ============================================================
# CONNECTION
# ============================================================


@dataclass
class Connection:

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    pipeline: PipelineState = field(default_factory=PipelineState)

    # --------------------------------------------------------
    # CORE
    # --------------------------------------------------------

    id: str = ""

    source: str = ""

    target: str = ""

    protocol: ProtocolType = "UNKNOWN"

    transport: TransportType = "unknown"

    bearer: BearerType = "unknown"

    media: MediaType = "unknown"

    physical_path: str = ""

    connection_type: ConnectionType = "UNKNOWN"

    conduit_id: str = ""

    conduit_class: str = "generic"

    # --------------------------------------------------------
    # DERIVED SEMANTICS
    # --------------------------------------------------------

    wireless: bool = False

    public_network: bool = False

    open_transmission: bool = False

    shared_medium: bool = False

    latency_sensitive: bool = False

    safety_related: bool = False

    safety_flow: bool = False

    encrypted: bool = False

    authentication: bool = False

    integrity_protection: bool = False

    replay_protection: bool = False

    monitoring: bool = False

    firewall: bool = False

    inspection: bool = False

    latency_monitoring: bool = False

    mfa: bool = False

    unidirectional: bool = False

    firewall_traversal: bool = False

    session_managed: bool = False

    # --------------------------------------------------------
    # REQUIRED CONTROLS
    # --------------------------------------------------------

    requires_encrypted: bool = False

    requires_authentication: bool = False

    requires_integrity_protection: bool = False

    requires_replay_protection: bool = False

    requires_monitoring: bool = False

    requires_firewall: bool = False

    requires_inspection: bool = False

    requires_latency_monitoring: bool = False

    requires_mfa: bool = False

    # --------------------------------------------------------
    # ZONE / TRUST
    # --------------------------------------------------------

    cross_zone: bool = False

    trust_boundary_crossing: bool = False

    trust_boundary: bool = False

    detached_conduit: bool = False

    remote_access: bool = False

    vendor_access: bool = False

    shared_infrastructure: bool = False

    # --------------------------------------------------------
    # EN50159 / SAFETY
    # --------------------------------------------------------

    rasta_protected: bool = False

    sequence_validation: bool = False

    timeout_supervision: bool = False

    safety_boundary: bool = False

    railway_safety_conduit: bool = False

    telecom_related: bool = False

    engineering_access: bool = False

    management_traffic: bool = False

    security_monitoring: bool = False

    passive_telegram: bool = False

    communication_system_type: str = ""

    safety_domain: str = "non_vital"

    # --------------------------------------------------------
    # NETWORK
    # --------------------------------------------------------

    bandwidth: str = ""

    latency_requirement: str = ""

    deterministic_network: bool = False

    qos_enabled: bool = False

    # --------------------------------------------------------
    # ATTACK GRAPH
    # --------------------------------------------------------

    attack_path_candidate: bool = False

    lateral_movement_risk: bool = False

    high_risk_conduit: bool = False

    # --------------------------------------------------------
    # RENDERING
    # --------------------------------------------------------

    render_style: str = ""

    render_color: str = ""

    render_penwidth: str = ""

    # --------------------------------------------------------
    # PROVENANCE
    # --------------------------------------------------------

    sources: dict = field(default_factory=dict)

    # --------------------------------------------------------
    # NOTES
    # --------------------------------------------------------

    notes: str = ""


# ============================================================
# CONDUIT
# ============================================================


@dataclass
class Conduit:

    # --------------------------------------------------------
    # CORE
    # --------------------------------------------------------

    id: str = ""

    conduit_class: str = "generic"

    conduit_type: str = ""

    source: str = ""

    target: str = ""

    source_zone: ZoneType = "unknown"

    target_zone: ZoneType = "unknown"

    source_level: SemanticLayerType = "Unknown"

    target_level: SemanticLayerType = "Unknown"

    protocol: ProtocolType = "UNKNOWN"

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    cross_zone: bool = False

    cross_purdue: bool = False

    trust_boundary: bool = False

    detached_conduit: bool = False

    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    monitoring: bool = False

    firewall: bool = False

    inspection: bool = False

    trusted_conduit: bool = False

    segmented: bool = False

    unidirectional: bool = False

    security_level_required: str = ""

    # --------------------------------------------------------
    # SEMANTICS
    # --------------------------------------------------------

    safety_related: bool = False

    telecom_related: bool = False

    engineering_access: bool = False

    radio_related: bool = False

    attack_path_candidate: bool = False

    lateral_movement_risk: bool = False

    # --------------------------------------------------------
    # POLICY / CONTROL
    # --------------------------------------------------------

    security_controls: list[str] = field(default_factory=list)

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    conduit_metadata: dict = field(default_factory=dict)

    # --------------------------------------------------------
    # PROVENANCE
    # --------------------------------------------------------

    sources: dict = field(default_factory=dict)

    # --------------------------------------------------------
    # NOTES
    # --------------------------------------------------------

    description: str = ""

    notes: str = ""


# ============================================================
# TOPOLOGY
# ============================================================


@dataclass
class Topology:

    name: str

    description: str

    standard: str = "IEC 62443"

    railway_system: str = "Kavach"

    architecture_type: str = "Railway Signalling OT"

    # --------------------------------------------------------
    # PIPELINE METADATA
    # --------------------------------------------------------

    pipeline_version: str = "v1"

    ontology_version: str = "v1"

    layout_strategy: str = "clustered"

    validation_profile: str = "strict"

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    nodes: list[Node] = field(default_factory=list)

    connections: list[Connection] = field(default_factory=list)

    conduits: list[Conduit] = field(default_factory=list)

    clusters: list[dict] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    # ========================================================
    # EXPORT
    # ========================================================

    def to_dict(self) -> dict:

        return {
            "name": self.name,
            "description": self.description,
            "standard": self.standard,
            "railway_system": self.railway_system,
            "architecture_type": self.architecture_type,
            "pipeline_version": self.pipeline_version,
            "ontology_version": self.ontology_version,
            "layout_strategy": self.layout_strategy,
            "validation_profile": self.validation_profile,
            "metadata": self.metadata,
            "nodes": [asdict(n) for n in self.nodes],
            "connections": [asdict(c) for c in self.connections],
            "conduits": [asdict(c) for c in self.conduits],
            "clusters": self.clusters,
        }
