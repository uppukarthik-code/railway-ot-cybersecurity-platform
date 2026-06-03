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
    },
    # ========================================================
    # RADIO TRANSPORT
    # ========================================================
    ("radio_gateway", "railway_radio_base_station"): {
        "direction": "bidirectional",
        "category": "radio_transport",
        "conduit_class": "radio_safety",
        "open_transmission": False,
    },
    # ========================================================
    # TRAIN ↔️ BTS RF
    # ========================================================
    ("train_radio", "railway_radio_base_station"): {
        "direction": "bidirectional",
        "category": "wireless_train_control",
        "conduit_class": "radio_safety",
        "open_transmission": True,
    },
    # ========================================================
    # ONBOARD RADIO INTERFACE
    # ========================================================
    ("l_kavach", "train_radio"): {
        "direction": "bidirectional",
        "category": "radio_interface",
        "conduit_class": "radio_safety",
        "internal_trusted": True,
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
    },
    ("object_controller", "point_machine_controller"): {
        "direction": "bidirectional",
        "category": "field_actuation",
        "conduit_class": "fieldbus",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
    },
    ("object_controller", "signal_controller"): {
        "direction": "bidirectional",
        "category": "signal_control",
        "conduit_class": "fieldbus",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
    },
    ("object_controller", "axle_counter_evaluator"): {
        "direction": "bidirectional",
        "category": "train_detection",
        "conduit_class": "fieldbus",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
    },
    
    ("axle_counter_evaluator", "axle_counter_head"): {
    "direction": "bidirectional",
    "category": "train_detection",
    "conduit_class": "fieldbus",
    "safety_related": True,
    "safety_flow": True,
    "internal_trusted": True,
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
    },
    ("l_kavach", "brake_interface_unit"): {
        "direction": "unidirectional",
        "category": "braking_control",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
    },
    ("speed_sensor", "l_kavach"): {
        "direction": "unidirectional",
        "category": "speed_feedback",
        "conduit_class": "safety_critical",
        "safety_related": True,
        "safety_flow": True,
        "internal_trusted": True,
    },
    ("onboard_rfid_reader", "l_kavach"): {
        "direction": "unidirectional",
        "category": "balise_data",
        "conduit_class": "passive_telegram",
        "safety_related": True,
        "safety_flow": True,
        "open_transmission": True,
        "internal_trusted": True,
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
