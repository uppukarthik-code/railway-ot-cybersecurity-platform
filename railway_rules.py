"""
railway_rules.py
FINAL CANONICAL POLICY ENGINE
IEC62443 + EN50159 + Railway OT + Kavach
UPDATED ARCHITECTURE
--------------------
- Zone-aware
- Conduit-aware
- Transit-aware
- PKI-aware
- Safety-aware
- Radio-aware
DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- railway_rules.py = governance authority
- validator.py = enforcement authority
NO:
- renderer logic
- ontology duplication
- classification logic
"""

from ontology import (
    TRANSIT_ZONES,
    PKI_INTERMEDIARY_TYPES,
    CONDUIT_SECURITY_PROFILES,
    BOUNDARY_CONTROL_TYPES,
)

# ============================================================
# FORBIDDEN TYPES
# ============================================================
FORBIDDEN_NODE_TYPES = {
    "internet_gateway",
    "mail_server",
    "domain_controller",
    "active_directory",
    "public_wifi",
    "cloud_proxy",
}
# ============================================================
# FORBIDDEN LABEL REGEX
# ============================================================
FORBIDDEN_LABEL_PATTERNS = [
    r"\binternet\s+gateway\b",
    r"\bmail\s+server\b",
    r"\bdomain\s+controller\b",
    r"\bactive\s+directory\b",
    r"\bpublic\s+wifi\b",
    r"\bcloud\s+proxy\b",
]
# ============================================================
# FORBIDDEN CONNECTIONS
# ============================================================
FORBIDDEN_CONNECTIONS = {
    ("enterprise_it", "interlocking"): {
        "direction": "bidirectional",
        "reason": "enterprise_to_safety_forbidden",
    },
    ("enterprise_it", "field"): {
        "direction": "bidirectional",
        "reason": "enterprise_to_field_forbidden",
    },
    ("enterprise_it", "onboard"): {
        "direction": "bidirectional",
        "reason": "enterprise_to_train_forbidden",
    },
}
# ============================================================
# FORBIDDEN FLOWS (asset-type granularity)
# ============================================================
# Type-level forbidden flows for architecturally invalid edges that a
# zone-pair rule cannot express without over-blocking legitimate
# traffic in the same zone pair (e.g. the valid RF air interface
# train_radio -> railway_radio_base_station shares the
# interlocking/onboard <-> radio_access space).
#
# INVESTIGATED & REJECTED:
#   s_kavach -> railway_radio_base_station ("radio_base_station")
#     The Stationary-Kavach (SIL4 vital, interlocking zone) must reach
#     the radio network through the telecom backhaul and the
#     radio_gateway safety boundary:
#         telecom_gateway -> radio_gateway -> railway_radio_base_station
#     A direct s_kavach -> BTS edge:
#       * bypasses the rf_transition trust boundary
#         (firewall / inspection / authentication),
#       * attaches a vital safety controller straight onto the open-RF
#         base station with no controlled backhaul mediation,
#       * collapses the L2 Interlocking -> L1 Telecom Purdue layering.
#     Not architecturally valid -> forbidden; generation is prevented
#     (see main.filter_topology) and the link validator reports it.
FORBIDDEN_FLOWS = {
    ("s_kavach", "railway_radio_base_station"): {
        "direction": "bidirectional",
        "reason": "vital_controller_direct_open_rf_bypasses_radio_gateway",
    },
}


def is_forbidden_flow(src_type, dst_type):
    """True when an asset-type pair is an architecturally forbidden
    flow. Matches either direction for bidirectional entries."""
    if (src_type, dst_type) in FORBIDDEN_FLOWS:
        return True
    reverse = FORBIDDEN_FLOWS.get((dst_type, src_type))
    if reverse and reverse.get("direction") == "bidirectional":
        return True
    return False


# ============================================================
# HIGH RISK CONNECTIONS
# ============================================================
HIGH_RISK_CONNECTIONS = {
    ("enterprise_it", "operations"): {
        "direction": "unidirectional",
        "risk": "it_ot_exposure",
    },
    ("maintenance", "interlocking"): {
        "direction": "unidirectional",
        "risk": "engineering_access",
    },
    ("telecom_core", "interlocking"): {
        "direction": "bidirectional",
        "risk": "telecom_to_safety",
    },
    ("radio_access", "onboard"): {
        "direction": "bidirectional",
        "risk": "wireless_train_control",
    },
}
# ============================================================
# TRUST BOUNDARIES
# ============================================================
TRUST_BOUNDARIES = {
    ("enterprise_it", "idmz"): {
        "direction": "bidirectional",
        "boundary_type": "enterprise_idmz",
        "required_controls": {
            "firewall",
            "inspection",
        },
    },
    ("idmz", "operations"): {
        "direction": "bidirectional",
        "boundary_type": "idmz_ot",
        "required_controls": {
            "firewall",
            "inspection",
        },
    },
    ("operations", "interlocking"): {
        "direction": "unidirectional",
        "boundary_type": "ot_safety",
        "required_controls": {
            "firewall",
            "inspection",
            "integrity_protection",
            "authentication",
        },
    },
    ("telecom_core", "radio_access"): {
        "direction": "bidirectional",
        "boundary_type": "rf_transition",
        "required_controls": {
            "firewall",
            "inspection",
            "authentication",
        },
    },
    ("radio_access", "onboard"): {
        "direction": "bidirectional",
        "boundary_type": "wireless_mobile",
        "required_controls": {
            "integrity_protection",
            "replay_protection",
            "authentication",
            "radio_monitoring",
        },
    },
}
# ============================================================
# FLOW RULES
# ============================================================
FLOW_RULES = {
    # ========================================================
    # SECURITY MONITORING
    # ========================================================
    ("enterprise_server", "siem"): {
        "direction": "unidirectional",
        "category": "logging",
        "conduit_class": "management",
        "mandatory": True,
    },
    ("siem", "soc_server"): {
        "direction": "unidirectional",
        "category": "security_monitoring",
        "conduit_class": "management",
        "mandatory": True,
    },
    ("tms", "siem"): {
        "direction": "unidirectional",
        "category": "security_logging",
        "conduit_class": "management",
    },
    ("nms", "siem"): {
        "direction": "unidirectional",
        "category": "security_logging",
        "conduit_class": "management",
    },
    # ========================================================
    # SOC ARCHITECTURE (detection / prevention / vuln mgmt)
    # ========================================================
    # IDS/IPS sensor alerts and vulnerability findings feed the SOC
    # analytics plane. All are management-plane, one-way telemetry
    # (sensor -> collector); none is a control path.
    ("ids_sensor", "siem"): {
        "direction": "unidirectional",
        "category": "intrusion_detection",
        "conduit_class": "management",
    },
    ("ips_sensor", "siem"): {
        "direction": "unidirectional",
        "category": "intrusion_prevention",
        "conduit_class": "management",
    },
    ("vulnerability_scanner", "soc_server"): {
        "direction": "unidirectional",
        "category": "vulnerability_management",
        "conduit_class": "management",
    },
    # The IDMZ data diode is a physically one-way device shipping
    # mirrored/aggregated logs up into the SIEM. Direction is
    # hardware-enforced unidirectional.
    ("data_diode", "siem"): {
        "direction": "unidirectional",
        "category": "security_logging",
        "conduit_class": "management",
    },
    # ========================================================
    # IDMZ ACCESS ARCHITECTURE
    # ========================================================
    # Brokered remote-access chain through the IDMZ:
    #   firewall -> vpn_gateway -> jump_host -> (eng|ops) workstation.
    # The firewall->vpn and vpn->jump legs are management-plane; the
    # jump_host -> workstation legs cross the IDMZ->operations trust
    # boundary and are privileged engineering access (MFA-gated via the
    # engineering_access conduit). cross_trust marks the boundary hop.
    ("firewall", "vpn_gateway"): {
        "direction": "unidirectional",
        "category": "secure_access_chain",
        "conduit_class": "management",
    },
    ("vpn_gateway", "jump_host"): {
        "direction": "unidirectional",
        "category": "secure_access_chain",
        "conduit_class": "management",
    },
    ("jump_host", "engineering_workstation"): {
        "direction": "unidirectional",
        "category": "engineering_access",
        "conduit_class": "engineering_access",
        "cross_trust": True,
    },
    ("jump_host", "operations_workstation"): {
        "direction": "unidirectional",
        "category": "engineering_access",
        "conduit_class": "engineering_access",
        "cross_trust": True,
    },
    # ========================================================
    # PKI / KEY MANAGEMENT
    # ========================================================
    ("external_kms_server", "s_kavach"): {
        "direction": "bidirectional",
        "category": "key_management",
        "conduit_class": "management",
    },
    ("external_kms_server", "l_kavach"): {
        "direction": "bidirectional",
        "category": "key_management",
        "conduit_class": "management",
    },
   
   
    # ========================================================
    # ENGINEERING ACCESS
    # ========================================================
    ("engineering_workstation", "electronic_interlocking"): {
        "direction": "unidirectional",
        "category": "engineering_access",
        "conduit_class": "engineering_access",
        "cross_trust": True,
    },
    ("engineering_workstation", "s_kavach"): {
        "direction": "unidirectional",
        "category": "engineering_access",
        "conduit_class": "engineering_access",
        "cross_trust": True,
    },
    ("engineering_workstation", "l_kavach"): {
        "direction": "unidirectional",
        "category": "engineering_access",
        "conduit_class": "engineering_access",
        "cross_trust": True,
    },
    # ========================================================
    # OPERATIONS
    # ========================================================
    ("tms", "s_kavach"): {
        "direction": "unidirectional",
        "category": "traffic_management",
        "conduit_class": "enterprise_ot",
        "safety_adjacent": True,
    },
    ("operations_workstation", "electronic_interlocking"): {
        "direction": "bidirectional",
        "category": "traffic_management",
        "conduit_class": "engineering_access",
        "safety_adjacent": True,
    },
    # ========================================================
    # MANAGEMENT
    # ========================================================
    ("nms", "mpls_router"): {
        "direction": "bidirectional",
        "category": "network_management",
        "conduit_class": "management",
        "mandatory": True,
    },
    # ========================================================
    # TELECOM BACKHAUL
    # ========================================================
    ("telecom_gateway", "radio_gateway"): {
        "direction": "bidirectional",
        "category": "radio_backhaul",
        "conduit_class": "cross_zone_secure",
        # EN 50159 Category 2 — controlled transmission (managed
        # backhaul with known participants); transport security via
        # IPsec/MACsec.
        "transmission_category": 2,
    },
    # ========================================================
    # RADIO TRANSPORT
    # ========================================================
    ("radio_gateway", "railway_radio_base_station"): {
        "direction": "bidirectional",
        "category": "radio_transport",
        "conduit_class": "radio_safety",
        "open_transmission": False,
        # EN 50159 Category 2 — wired/managed backhaul segment to the
        # base station (NOT the RF air interface).
        "transmission_category": 2,
    },
    # ========================================================
    # TRAIN ↔️ BTS RF
    # ========================================================
    ("train_radio", "railway_radio_base_station"): {
        "direction": "bidirectional",
        "category": "wireless_train_control",
        "conduit_class": "radio_safety",
        "open_transmission": True,
        "safety_related": True,
        "safety_flow": True,
        # EN 50159 Category 3 — open RF transmission, unknown adversary.
        # Cryptographic authentication, integrity and replay protection
        # remain mandatory (no safety-layer credit permitted).
        "transmission_category": 3,
    },
    # ========================================================
    # ONBOARD RADIO INTERFACE
    # ========================================================
    ("l_kavach", "train_radio"): {
        "direction": "bidirectional",
        "category": "radio_interface",
        # Internal onboard MVB handoff between the Loco-Kavach safety
        # computer and the onboard radio — NOT an RF transmission path.
        # The RF leg is train_radio -> railway_radio_base_station.
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    # ========================================================
    # INTERLOCKING
    # ========================================================
    ("electronic_interlocking", "s_kavach"): {
        "direction": "unidirectional",
        "category": "interlocking_access",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        # EN 50159 Category 1 — closed trusted transmission (vital
        # EI<->Kavach interface, KAVACH_EI_INTERFACE safety layer).
        "transmission_category": 1,
    },
    # ========================================================
    # INTERLOCKING TRAIN DETECTION
    # ========================================================
    # Vital train-detection inputs to the interlocking. The axle
    # counter evaluator sits in the interlocking zone (vital), so it
    # uses the safety_critical conduit; the track circuit is a field
    # (L0) vital detector on a closed copper/CAN segment (fieldbus).
    # Both are EN 50159 Category 1 closed trusted transmission.
    ("electronic_interlocking", "axle_counter_evaluator"): {
        "direction": "bidirectional",
        "category": "train_detection",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    ("electronic_interlocking", "track_circuit"): {
        "direction": "bidirectional",
        "category": "train_detection",
        "conduit_class": "fieldbus",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    # ========================================================
    # FIELD CONTROL
    # ========================================================
    ("electronic_interlocking", "object_controller"): {
        "direction": "bidirectional",
        "category": "field_control",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "mandatory": True,
        "transmission_category": 1,
    },
    ("object_controller", "point_machine_controller"): {
        "direction": "bidirectional",
        "category": "field_actuation",
        "conduit_class": "fieldbus",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    ("object_controller", "signal_controller"): {
        "direction": "bidirectional",
        "category": "signal_control",
        "conduit_class": "fieldbus",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    ("object_controller", "axle_counter_evaluator"): {
        "direction": "bidirectional",
        "category": "train_detection",
        "conduit_class": "fieldbus",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },

    ("axle_counter_evaluator", "axle_counter_head"): {
    "direction": "bidirectional",
    "category": "train_detection",
    "conduit_class": "fieldbus",
    "safety_related": True,
    "safety_flow": True,
    "internal_trusted": True,
    "transmission_category": 1,
},
    
    # ========================================================
    # ONBOARD KAVACH
    # ========================================================
    ("l_kavach", "driver_machine_interface"): {
        "direction": "bidirectional",
        "category": "onboard_vital",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    ("l_kavach", "brake_interface_unit"): {
        "direction": "unidirectional",
        "category": "braking_control",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    ("speed_sensor", "l_kavach"): {
        "direction": "unidirectional",
        "category": "speed_feedback",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    # Trackside RFID balise -> onboard reader air interface. This is
    # the actual open balise air-gap (RFID_AIR). Protection is the
    # passive safety-coded telegram (passive_telegram exemption); the
    # onboard_rfid_reader -> l_kavach leg below carries the decoded
    # telegram onward. EN 50159 Category 3 open transmission, no
    # cryptographic credit.
    ("trackside_rfid_tag", "onboard_rfid_reader"): {
        "direction": "unidirectional",
        "category": "balise_telegram",
        "conduit_class": "passive_telegram",
        "safety_related": True,
        "safety_flow": True,
        "open_transmission": True,
        "passive_telegram": True,
        "internal_trusted": True,
        "transmission_category": 3,
    },
    ("onboard_rfid_reader", "l_kavach"): {
        "direction": "unidirectional",
        "category": "balise_data",
        "conduit_class": "passive_telegram",
        "safety_related": True,
        "safety_flow": True,
        "open_transmission": True,
        "passive_telegram": True,
        "internal_trusted": True,
        # EN 50159 Category 3 — open balise air-gap. Protection is the
        # passive safety-coded telegram (passive_telegram exemption);
        # no cryptographic credit applied.
        "transmission_category": 3,
    },
    # ========================================================
    # RIU / AUTO SECTION
    # ========================================================
    ("remote_interface_unit", "s_kavach"): {
        "direction": "bidirectional",
        "category": "auto_section_interface",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
        "transmission_category": 1,
    },
    # ========================================================
    # MODELLING COMPLETENESS  (assessment finding D-01)
    # ========================================================
    # Legitimate architectural flows that exist in the reference
    # topology but had no governance rule (reported as UNMODELED /
    # UNAUTHORIZED-FLOWS). Modelled here so the governance authority
    # describes them; no security control is relaxed — any missing
    # control on these flows now surfaces as a genuine finding.
    #
    # Enterprise -> IDMZ ingress (crosses enterprise_idmz boundary).
    ("enterprise_server", "firewall"): {
        "direction": "unidirectional",
        "category": "enterprise_idmz_ingress",
        "conduit_class": "idmz_transition",
        "cross_trust": True,
    },
    # Operator HMI <-> Traffic Management System (operations plane).
    ("operations_workstation", "tms"): {
        "direction": "bidirectional",
        "category": "operational_control",
        "conduit_class": "management",
    },
    # Network-management plane (SNMPv3 to network elements).
    ("tms", "nms"): {
        "direction": "unidirectional",
        "category": "network_management",
        "conduit_class": "management",
    },
    ("nms", "telecom_gateway"): {
        "direction": "bidirectional",
        "category": "network_management",
        "conduit_class": "management",
    },
    # Telecom backhaul transport. EN 50159 Category 2 — controlled
    # transmission (managed IP/MPLS core, known participants); transport
    # security (IPsec/MACsec) is expected, so an unprotected bearer
    # correctly raises a finding rather than being exempted.
    ("tms", "mpls_router"): {
        "direction": "unidirectional",
        "category": "operational_backhaul",
        "conduit_class": "cross_zone_secure",
        "transmission_category": 2,
    },
    ("mpls_router", "telecom_gateway"): {
        "direction": "bidirectional",
        "category": "telecom_backhaul",
        "conduit_class": "cross_zone_secure",
        "transmission_category": 2,
    },
    # Loco-Kavach <-> Stationary-Kavach end-to-end safety association.
    # This is the core Kavach movement-authority exchange carried over
    # the open RF bearer (MCOMM). Modelled as EN 50159 Category 3 open
    # transmission with the radio_safety conduit — distinct from the
    # FORBIDDEN s_kavach -> railway_radio_base_station physical edge:
    # this is an end-to-end safety layer between the two safety
    # endpoints, exactly the EN 50159 open-transmission model. Full
    # cryptographic + timeliness protection remains mandatory.
    ("l_kavach", "s_kavach"): {
        "direction": "bidirectional",
        "category": "kavach_safety_association",
        "conduit_class": "radio_safety",
        "safety_related": True,
        "safety_flow": True,
        "open_transmission": True,
        "transmission_category": 3,
    },
}
# ============================================================
# SIL RULES
# ============================================================
SIL_ISOLATION_RULES = {
    "SIL4": {
        "allow_low_trust_direct_access": False,
        "allow_enterprise_connectivity": False,
        "requires_monitored_conduits": True,
    },
    "SIL3": {
        "allow_low_trust_direct_access": False,
        "requires_monitored_conduits": True,
    },
}
# ============================================================
# POLICY EXEMPTIONS
# ============================================================
POLICY_EXEMPTIONS = {
    "monitoring": {
        "siem",
        "soc_server",
        "ids_sensor",
        "ips_sensor",
    },
    "inspection": {},
    "firewall": {},
}


# ============================================================
# MONITORING HELPERS
# ============================================================
def is_monitoring_exempt(asset_type: str) -> bool:
    return str(asset_type).strip().lower() in POLICY_EXEMPTIONS.get(
        "monitoring",
        set(),
    )


def is_inspection_exempt(conduit_type: str) -> bool:
    return str(conduit_type).strip().lower() in POLICY_EXEMPTIONS.get(
        "inspection",
        set(),
    )


def is_firewall_exempt(conduit_type: str) -> bool:
    return str(conduit_type).strip().lower() in POLICY_EXEMPTIONS.get(
        "firewall",
        set(),
    )


# ============================================================
# FLOW HELPERS
# ============================================================
def get_flow_rule(src_type, dst_type):
    direct = FLOW_RULES.get((src_type, dst_type))
    if direct:
        return direct
    reverse = FLOW_RULES.get((dst_type, src_type))
    if reverse and reverse.get("direction") == "bidirectional":
        return reverse
    return None


def get_effective_flow_policy(rule):
    if not rule:
        return {}
    effective = dict(rule)
    conduit_class = rule.get("conduit_class")
    conduit_profile = CONDUIT_SECURITY_PROFILES.get(
        conduit_class,
        {},
    )
    for key, value in conduit_profile.items():
        effective.setdefault(key, value)
    return effective


def is_transit_zone(zone):
    return zone in TRANSIT_ZONES


def is_transit_flow(src_zone, dst_zone):
    return src_zone in TRANSIT_ZONES or dst_zone in TRANSIT_ZONES


def is_valid_pki_flow(src_type, dst_type):
    pki_sources = {
        "external_kms_server",
        "certificate_authority",
    }
    if src_type not in pki_sources:
        return False
    return dst_type in PKI_INTERMEDIARY_TYPES


def is_safety_flow(rule):
    if not rule:
        return False
    return rule.get("safety_flow", False)


def get_transmission_category(rule):
    """
    EN 50159 transmission category for a flow rule.

    1 = closed trusted transmission
    2 = controlled transmission
    3 = open transmission
    Returns None when the flow carries no declared category.
    """
    if not rule:
        return None
    return rule.get("transmission_category")


# ============================================================
# PREFERRED PROTOCOLS (topology-generation determinism)
# ============================================================
# Governance-mandated protocol for specific asset pairs. Topology
# generation (LLM) must never leave these as UNKNOWN or assign a
# non-representative bearer. These reflect the real railway/Kavach
# architecture, not a relaxation of any requirement.
PREFERRED_PROTOCOLS = {
    # Vital Stationary-Kavach <-> Electronic-Interlocking interface.
    ("electronic_interlocking", "s_kavach"): "KAVACH_EI_INTERFACE",
    # Trackside RFID balise air interface (passive safety telegram).
    ("trackside_rfid_tag", "onboard_rfid_reader"): "RFID_AIR",
    ("onboard_rfid_reader", "l_kavach"): "RFID_AIR",
    # IP backhaul segments protected by a transport-security overlay.
    ("telecom_gateway", "radio_gateway"): "IPSEC",
    ("radio_gateway", "railway_radio_base_station"): "IPSEC",
}


def get_preferred_protocol(src_type, dst_type):
    """Return the governance-mandated protocol for an asset pair, or
    None. Matches either direction (railway conduits are modelled
    bidirectionally)."""
    direct = PREFERRED_PROTOCOLS.get((src_type, dst_type))
    if direct:
        return direct
    return PREFERRED_PROTOCOLS.get((dst_type, src_type))


# ============================================================
# SECURITY MONITORING COVERAGE (topology fidelity)
# ============================================================
# Asset types that constitute deployed security-monitoring
# instrumentation. Their presence in a topology means the SOC has
# network monitoring capability to instrument the OT zones.
MONITORING_INFRASTRUCTURE_TYPES = {
    "siem",
    "soc_server",
    "ids_sensor",
    "ips_sensor",
}

# Zones instrumented by the reference Kavach SOC monitoring stack
# (ground network IDS/IPS + SIEM) and the onboard event-recording /
# safety-monitoring function of the Loco-Kavach. This models WHERE
# monitoring coverage actually exists; it is NOT an exemption — the
# credit it enables is gated on monitoring instrumentation being
# present in the topology (see has_monitoring_infrastructure).
MONITORED_ZONES = {
    "security_management",
    "operations",
    "idmz",
    "interlocking",
    "telecom_core",
    "radio_access",
    "field",
    "onboard",
}


def has_monitoring_infrastructure(node_types):
    """True when the topology contains deployed monitoring
    instrumentation (SIEM / IDS / IPS / SOC)."""
    return any(t in MONITORING_INFRASTRUCTURE_TYPES for t in node_types)


def is_monitored_zone(zone):
    """True when the zone is within the SOC's monitoring coverage."""
    return zone in MONITORED_ZONES


# ============================================================
# TRUST BOUNDARY HELPERS
# ============================================================
def get_trust_boundary(src_zone, dst_zone):
    boundary = TRUST_BOUNDARIES.get((src_zone, dst_zone))
    if boundary:
        return boundary
    reverse = TRUST_BOUNDARIES.get((dst_zone, src_zone))
    if reverse and reverse.get("direction") == "bidirectional":
        return reverse
    return None


# ============================================================
# FORBIDDEN CONNECTION HELPERS
# ============================================================
def is_forbidden_zone_pair(src_zone, dst_zone):
    rule = FORBIDDEN_CONNECTIONS.get((src_zone, dst_zone))
    if rule:
        return True
    reverse = FORBIDDEN_CONNECTIONS.get((dst_zone, src_zone))
    if reverse and reverse.get("direction") == "bidirectional":
        return True
    return False


# ============================================================
# HIGH RISK CONNECTION HELPERS
# ============================================================
def get_high_risk_connection(src_zone, dst_zone):
    risk = HIGH_RISK_CONNECTIONS.get((src_zone, dst_zone))
    if risk:
        return risk
    reverse = HIGH_RISK_CONNECTIONS.get((dst_zone, src_zone))
    if reverse and reverse.get("direction") == "bidirectional":
        return reverse
    return None


# ============================================================
# AUTO GENERATED FLOW SETS
# ============================================================
def generate_required_logical_links():
    required = {}
    for (src, dst), rule in FLOW_RULES.items():
        if not rule.get("mandatory", False):
            continue
        required.setdefault(src, set()).add(dst)
    return required


REQUIRED_LOGICAL_LINKS = generate_required_logical_links()


def expand_bidirectional_flow_set(predicate):
    flows = set()
    for (src, dst), rule in FLOW_RULES.items():
        if not predicate(rule):
            continue
        flows.add((src, dst))
        if rule.get("direction") == "bidirectional":
            flows.add((dst, src))
    return flows


OPEN_TRANSMISSION_FLOWS = expand_bidirectional_flow_set(
    lambda r: r.get("open_transmission")
)
ALLOWED_SAFETY_FLOWS = expand_bidirectional_flow_set(lambda r: r.get("safety_related"))
INTERNAL_TRUSTED_FLOWS = expand_bidirectional_flow_set(
    lambda r: r.get("internal_trusted")
)
