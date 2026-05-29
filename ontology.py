"""
ontology.py

Canonical Railway OT Cybersecurity Ontology
IEC 62443 + EN50126 + EN50129 + EN50159 + Kavach

SINGLE SOURCE OF TRUTH

Contains ONLY:
- Purdue semantics
- Zone semantics
- Asset semantics
- Protocol semantics
- Conduit semantics
- Media semantics
- Transport semantics
- Bearer semantics
- Compatibility semantics

NO:
- validation logic
- rendering logic
- aliases
- classifier logic
"""

# ============================================================
# UNKNOWN CONSTANTS
# ============================================================

UNKNOWN_NODE = "unknown"

UNKNOWN_PROTOCOL = "UNKNOWN"

UNKNOWN_TRANSPORT = "unknown"

UNKNOWN_MEDIA = "UNKNOWN"

UNKNOWN_BEARER = "unknown"

UNKNOWN_ZONE = "unknown_zone"

UNKNOWN_PURDUE = "Unknown"

UNKNOWN_SAFETY_DOMAIN = "non_vital"

UNKNOWN_CONDUIT = "unknown_conduit"

# ============================================================
# SAFETY DOMAINS
# ============================================================

SAFETY_DOMAINS = {
    "non_vital",
    "safety_adjacent",
    "vital",
    "field_vital",
    "onboard_vital",
}

# ============================================================
# TRUST DOMAINS
# ============================================================

TRUST_DOMAINS = {
    "enterprise",
    "idmz",
    "security_management",
    "operations",
    "maintenance",
    "telecom",
    "radio",
    "safety",
    "field",
    "onboard",
    "external",
    "unknown",
}

# ============================================================
# TRANSIT ZONES
# ============================================================

TRANSIT_ZONES = {
    "idmz",
    "security_management",
    "telecom_core",
    "radio_access",
}

# ============================================================
# EXTERNAL / MOBILE / RF ZONES
# ============================================================

EXTERNAL_ZONES = {
    "external_security",
}

MOBILE_ZONES = {
    "onboard",
}

RF_EXPOSED_ZONES = {
    "radio_access",
    "onboard",
}

# ============================================================
# TRUST CLASSES
# ============================================================

TRUST_CLASSES = {
    "trusted",
    "semi_trusted",
    "low",
}

# ============================================================
# BOUNDARY CONTROL TYPES
# ============================================================

BOUNDARY_CONTROL_TYPES = {
    "firewall",
    "inspection",
    "authenticated_gateway",
    "application_proxy",
    "cryptographic_tunnel",
    "integrity_protection",
    "replay_protection",
    "authentication",
    "radio_monitoring",
}
# ============================================================
# DEPLOYMENT DOMAINS
# ============================================================

DEPLOYMENT_DOMAINS = {
    "enterprise",
    "operations_center",
    "security",
    "telecom",
    "wayside",
    "onboard",
    "unknown",
}


# ============================================================
# PURDUE LEVELS
# ============================================================

PURDUE_LEVELS = {
    "L5 Enterprise": {
        "description": "Enterprise IT",
        "risk_profile": "HIGH_ATTACK_SURFACE",
        "default_trust": False,
    },
    "L4 Business": {
        "description": "Business Systems",
        "risk_profile": "BUSINESS_OPERATIONAL",
        "default_trust": False,
    },
    "L3.5 IDMZ": {
        "description": "Industrial DMZ",
        "risk_profile": "DMZ",
        "default_trust": False,
    },
    "L3.5 Security": {
        "description": "OT Security",
        "risk_profile": "SECURITY_MONITORING",
        "default_trust": True,
    },
    "L3 Operations": {
        "description": "Railway Operations",
        "risk_profile": "OT_OPERATIONS",
        "default_trust": True,
    },
    "L2 Telecom": {
        "description": "Railway Telecom Backbone",
        "risk_profile": "OT_BACKBONE",
        "default_trust": True,
    },
    "L1 Telecom": {
        "description": "Railway RF Access",
        "risk_profile": "RF_ACCESS",
        "default_trust": False,
    },
    "L2 Interlocking": {
        "description": "Vital ATP Services",
        "risk_profile": "SAFETY_CRITICAL",
        "default_trust": True,
    },
    "L1 Interlocking": {
        "description": "Vital Logic",
        "risk_profile": "VITAL_CONTROL",
        "default_trust": True,
    },
    "L0 Field": {
        "description": "Field Devices",
        "risk_profile": "FIELD_DEVICE",
        "default_trust": True,
    },
    "Onboard": {
        "description": "Rolling Stock",
        "risk_profile": "MOBILE_SAFETY",
        "default_trust": True,
    },
    "Unknown": {
        "description": "Unknown Purdue Level",
        "risk_profile": "UNKNOWN",
        "default_trust": False,
    },
}


# ============================================================
# PURDUE PRIORITY
# ============================================================

DEFAULT_PURDUE_PRIORITY = [
    "L0 Field",
    "L1 Telecom",
    "L1 Interlocking",
    "L2 Interlocking",
    "L2 Telecom",
    "L3 Operations",
    "L3.5 Security",
    "L4 Business",
    "L5 Enterprise",
]

# ============================================================
# ZONE ONTOLOGY
# ============================================================

ZONE_ONTOLOGY = {
    # ========================================================
    # ENTERPRISE
    # ========================================================
    "enterprise_it": {
        "trust": "low",
        "security_level": "SL1",
        "cyber_criticality": "LOW",
        "operational_criticality": "LOW",
        "safety_criticality": "NONE",
        "trust_domain": "enterprise",
        "deployment_domain": "enterprise",
        "allowed_purdue": ["L5 Enterprise"],
    },
    "business_systems": {
        "trust": "low",
        "security_level": "SL1",
        "cyber_criticality": "LOW",
        "operational_criticality": "LOW",
        "safety_criticality": "NONE",
        "trust_domain": "enterprise",
        "deployment_domain": "enterprise",
        "allowed_purdue": ["L4 Business"],
    },
    # ========================================================
    # IDMZ / SECURITY
    # ========================================================
    "idmz": {
        "trust": "low",
        "security_level": "SL2",
        "cyber_criticality": "HIGH",
        "operational_criticality": "MEDIUM",
        "safety_criticality": "NONE",
        "trust_domain": "idmz",
        "deployment_domain": "enterprise",
        "allowed_purdue": ["L3.5 IDMZ"],
    },
    "security_management": {
        "trust": "semi_trusted",
        "security_level": "SL2",
        "cyber_criticality": "HIGH",
        "operational_criticality": "HIGH",
        "safety_criticality": "NONE",
        "trust_domain": "security_management",
        "deployment_domain": "security",
        "allowed_purdue": ["L3.5 Security"],
    },
    "external_security": {
        "trust": "low",
        "security_level": "SL2",
        "cyber_criticality": "HIGH",
        "operational_criticality": "MEDIUM",
        "safety_criticality": "NONE",
        "trust_domain": "external",
        "deployment_domain": "security",
        "allowed_purdue": ["Unknown"],
    },
    # ========================================================
    # OPERATIONS / MAINTENANCE
    # ========================================================
    "operations": {
        "trust": "semi_trusted",
        "security_level": "SL2",
        "cyber_criticality": "MEDIUM",
        "operational_criticality": "HIGH",
        "safety_criticality": "NONE",
        "trust_domain": "operations",
        "deployment_domain": "operations_center",
        "allowed_purdue": ["L3 Operations"],
    },
    "maintenance": {
        "trust": "semi_trusted",
        "security_level": "SL2",
        "cyber_criticality": "HIGH",
        "operational_criticality": "HIGH",
        "safety_criticality": "NONE",
        "trust_domain": "maintenance",
        "deployment_domain": "operations_center",
        "allowed_purdue": ["L3 Operations"],
    },
    "engineering": {
        "trust": "semi_trusted",
        "security_level": "SL3",
        "cyber_criticality": "HIGH",
        "operational_criticality": "HIGH",
        "safety_criticality": "NONE",
        "trust_domain": "maintenance",
        "deployment_domain": "wayside",
        "allowed_purdue": ["L2 Interlocking"],
    },
    # ========================================================
    # TELECOM
    # ========================================================
    "telecom_core": {
        "trust": "semi_trusted",
        "security_level": "SL2",
        "cyber_criticality": "HIGH",
        "operational_criticality": "HIGH",
        "safety_criticality": "NONE",
        "trust_domain": "telecom",
        "deployment_domain": "telecom",
        "allowed_purdue": ["L2 Telecom"],
    },
    "radio_access": {
        "trust": "low",
        "security_level": "SL2",
        "cyber_criticality": "HIGH",
        "operational_criticality": "HIGH",
        "safety_criticality": "NONE",
        "trust_domain": "radio",
        "deployment_domain": "telecom",
        "allowed_purdue": ["L1 Telecom"],
    },
    # ========================================================
    # SAFETY / INTERLOCKING
    # ========================================================
    "interlocking": {
        "trust": "trusted",
        "security_level": "SL3",
        "cyber_criticality": "HIGH",
        "operational_criticality": "HIGH",
        "safety_criticality": "SIL4",
        "trust_domain": "safety",
        "deployment_domain": "wayside",
        "allowed_purdue": [
            "L2 Interlocking",
            "L1 Interlocking",
        ],
    },
    # ========================================================
    # FIELD
    # ========================================================
    "field": {
        "trust": "trusted",
        "security_level": "SL1",
        "cyber_criticality": "MEDIUM",
        "operational_criticality": "HIGH",
        "safety_criticality": "SIL2",
        "trust_domain": "field",
        "deployment_domain": "wayside",
        "allowed_purdue": ["L0 Field"],
    },
    # ========================================================
    # ONBOARD
    # ========================================================
    "onboard": {
        "trust": "trusted",
        "security_level": "SL2",
        "cyber_criticality": "HIGH",
        "operational_criticality": "HIGH",
        "safety_criticality": "SIL4",
        "trust_domain": "onboard",
        "deployment_domain": "onboard",
        "allowed_purdue": ["Onboard"],
    },
    # ========================================================
    # UNKNOWN
    # ========================================================
    "unknown_zone": {
        "trust": "low",
        "security_level": "SL0",
        "cyber_criticality": "UNKNOWN",
        "operational_criticality": "UNKNOWN",
        "safety_criticality": "UNKNOWN",
        "trust_domain": "unknown",
        "deployment_domain": "unknown",
        "allowed_purdue": ["Unknown"],
    },
}


# ============================================================


VALID_CONDUIT_CLASSES = {
    "generic",
    "engineering_access",
    "radio_safety",
    "passive_telegram",
    "enterprise_ot",
    "idmz_transition",
    "fieldbus",
    "telemetry",
    "management",
    "cross_zone_secure",
    "safety_critical",
}

VALID_STACK_LAYERS = {
    "unknown",
    "application_protocol",
    "management_protocol",
    "monitoring_protocol",
    "industrial_protocol",
    "telemetry_protocol",
    "field_protocol",
    "safety_protocol",
    "transport_protocol",
}

# ============================================================
# SECURITY LEVEL ORDER
# ============================================================

SECURITY_LEVEL_ORDER = {
    "SL0": 0,
    "SL1": 1,
    "SL2": 2,
    "SL3": 3,
    "SL4": 4,
}


# ============================================================
# ASSET ONTOLOGY
# ============================================================

ASSET_ONTOLOGY = {
    "enterprise_server": {
        "zone": "enterprise_it",
        "purdue": "L5 Enterprise",
        "criticality": "LOW",
        "safety_critical": False,
        "safety_domain": "non_vital",
    },
    "siem": {
        "zone": "security_management",
        "purdue": "L3.5 Security",
        "criticality": "HIGH",
        "safety_critical": False,
        "safety_domain": "non_vital",
    },
    "soc_server": {
        "zone": "security_management",
        "purdue": "L3.5 Security",
        "criticality": "HIGH",
        "safety_critical": False,
        "safety_domain": "non_vital",
    },
    "external_kms_server": {
        "zone": "external_security",
        "purdue": "Unknown",
        "criticality": "HIGH",
        "safety_critical": False,
        "safety_domain": "non_vital",
        "crypto_trust_anchor": True,
        "external_dependency": True,
    },
    "tms": {
        "zone": "operations",
        "purdue": "L3 Operations",
        "criticality": "MEDIUM",
        "safety_critical": False,
        "safety_domain": "safety_adjacent",
    },
    "nms": {
        "zone": "operations",
        "purdue": "L3 Operations",
        "criticality": "MEDIUM",
        "safety_critical": False,
        "safety_domain": "non_vital",
    },
    "operations_workstation": {
        "zone": "operations",
        "purdue": "L3 Operations",
        "criticality": "HIGH",
        "safety_critical": False,
        "safety_domain": "non_vital",
    },
    "engineering_workstation": {
        "zone": "operations",
        "allowed_zones": [
            "operations",
            "maintenance",
        ],
        "purdue": "L3 Operations",
        "criticality": "HIGH",
        "safety_critical": False,
        "engineering_access": True,
        "logic_download_capable": True,
        "configuration_change_capable": True,
        "high_privilege": True,
        "safety_domain": "safety_adjacent",
        "requires_mfa": True,
        "requires_session_monitoring": True,
        "privileged_access": True,
    },
    "mpls_router": {
        "zone": "telecom_core",
        "purdue": "L2 Telecom",
        "criticality": "HIGH",
        "safety_critical": False,
        "safety_domain": "non_vital",
    },
    "telecom_gateway": {
        "zone": "telecom_core",
        "purdue": "L2 Telecom",
        "criticality": "HIGH",
        "safety_critical": False,
        "safety_boundary": True,
        "safety_domain": "safety_adjacent",
    },
    "railway_radio_base_station": {
        "zone": "radio_access",
        "purdue": "L1 Telecom",
        "role": "trackside_bts",
        "criticality": "HIGH",
        "radio_exposed": True,
        "safety_domain": "safety_adjacent",
    },
    "radio_gateway": {
        "zone": "radio_access",
        "purdue": "L1 Telecom",
        "criticality": "HIGH",
        "radio_exposed": True,
        "safety_boundary": True,
        "safety_domain": "safety_adjacent",
    },
    "s_kavach": {
        "zone": "interlocking",
        "purdue": "L2 Interlocking",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL4",
        "radio_exposed": True,
        "safety_boundary": True,
        "safety_domain": "vital",
        "requires_conduit_monitoring": True,
        "requires_segmentation": True,
    },
    "remote_interface_unit": {
        "zone": "interlocking",
        "purdue": "L1 Interlocking",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL4",
        "radio_exposed": False,
        "safety_boundary": True,
        "safety_domain": "vital",
        "requires_conduit_monitoring": True,
        "requires_segmentation": True,
    },
    "electronic_interlocking": {
        "zone": "interlocking",
        "purdue": "L2 Interlocking",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL4",
        "safety_boundary": True,
        "safety_domain": "vital",
    },
    "object_controller": {
        "zone": "interlocking",
        "purdue": "L1 Interlocking",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL4",
        "safety_boundary": True,
        "safety_domain": "vital",
    },
    "axle_counter_head": {
        "zone": "field",
        "purdue": "L0 Field",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL2",
        "safety_domain": "field_vital",
    },
    "axle_counter_evaluator": {
        "zone": "interlocking",
        "purdue": "L1 Interlocking",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL4",
        "safety_domain": "vital",
    },
    "point_machine_controller": {
        "zone": "field",
        "purdue": "L0 Field",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL2",
        "safety_domain": "field_vital",
    },
    "signal_controller": {
        "zone": "field",
        "purdue": "L0 Field",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL2",
        "safety_domain": "field_vital",
    },
    "track_circuit": {
        "zone": "field",
        "purdue": "L0 Field",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL4",
        "safety_domain": "field_vital",
    },
    "l_kavach": {
        "zone": "onboard",
        "purdue": "Onboard",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL4",
        "radio_exposed": True,
        "safety_boundary": True,
        "safety_domain": "onboard_vital",
        "mobile_asset": True,
    },
    "train_radio": {
        "zone": "onboard",
        "purdue": "Onboard",
        "role": "onboard_radio",
        "criticality": "HIGH",
        "radio_exposed": True,
        "safety_domain": "onboard_vital",
        "mobile_asset": True,
    },
    "driver_machine_interface": {
        "zone": "onboard",
        "purdue": "Onboard",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL2",
        "safety_domain": "onboard_vital",
        "mobile_asset": True,
    },
    "brake_interface_unit": {
        "zone": "onboard",
        "purdue": "Onboard",
        "criticality": "HIGH",
        "safety_critical": True,
        "functional_safety_level": "SIL3",
        "safety_domain": "onboard_vital",
        "mobile_asset": True,
    },
    "speed_sensor": {
        "zone": "onboard",
        "purdue": "Onboard",
        "criticality": "MEDIUM",
        "safety_critical": True,
        "functional_safety_level": "SIL2",
        "safety_domain": "onboard_vital",
        "mobile_asset": True,
    },
    "onboard_rfid_reader": {
        "zone": "onboard",
        "purdue": "Onboard",
        "criticality": "LOW",
        "safety_critical": False,
        "safety_domain": "safety_adjacent",
        "mobile_asset": True,
    },
    "trackside_rfid_tag": {
        "zone": "field",
        "purdue": "L0 Field",
        "criticality": "LOW",
        "safety_critical": False,
        "safety_domain": "field_vital",
    },
    "firewall": {
        "zone": "idmz",
        "purdue": "L3.5 IDMZ",
        "criticality": "HIGH",
        "security_enforcement": True,
        "safety_domain": "non_vital",
    },
    "vpn_gateway": {
        "zone": "idmz",
        "purdue": "L3.5 IDMZ",
        "criticality": "HIGH",
        "security_enforcement": True,
        "safety_domain": "non_vital",
    },
    "jump_host": {
        "zone": "idmz",
        "purdue": "L3.5 IDMZ",
        "criticality": "HIGH",
        "security_enforcement": True,
        "safety_domain": "non_vital",
    },
    "data_diode": {
        "zone": "idmz",
        "purdue": "L3.5 IDMZ",
        "criticality": "HIGH",
        "unidirectional": True,
        "security_enforcement": True,
        "safety_domain": "non_vital",
    },
    "ids_sensor": {
        "zone": "security_management",
        "purdue": "L3.5 Security",
        "criticality": "HIGH",
        "security_monitoring": True,
        "safety_domain": "non_vital",
    },
    "ips_sensor": {
        "zone": "security_management",
        "purdue": "L3.5 Security",
        "criticality": "HIGH",
        "security_enforcement": True,
        "safety_domain": "non_vital",
    },
    "certificate_authority": {
        "zone": "security_management",
        "purdue": "L3.5 Security",
        "criticality": "HIGH",
        "crypto_trust_anchor": True,
        "safety_domain": "non_vital",
    },
    "vulnerability_scanner": {
        "zone": "security_management",
        "purdue": "L3.5 Security",
        "criticality": "MEDIUM",
        "security_monitoring": True,
        "safety_domain": "non_vital",
    },
    "log_collector": {
        "zone": "security_management",
        "purdue": "L3.5 Security",
        "criticality": "MEDIUM",
        "security_monitoring": True,
        "safety_domain": "non_vital",
    },
    "unknown": {
        "zone": UNKNOWN_ZONE,
        "purdue": UNKNOWN_PURDUE,
        "criticality": "LOW",
        "safety_critical": False,
        "safety_domain": UNKNOWN_SAFETY_DOMAIN,
    },
}

# ============================================================
# CONDUIT ONTOLOGY
# ============================================================

CONDUIT_ONTOLOGY = {
    "intra_zone": {
        "logical": True,
        "cross_zone": False,
    },
    "cross_zone_secure": {
        "logical": True,
        "cross_zone": True,
        "requires_firewall": True,
        "requires_monitoring": True,
    },
    "enterprise_ot": {
        "logical": True,
        "cross_zone": True,
        "requires_idmz": True,
    },
    "safety_critical": {
        "logical": True,
        "safety_related": True,
        "requires_integrity": True,
        "requires_replay_protection": True,
    },
    "radio_safety": {
        "logical": False,
        "wireless": True,
        "open_transmission": True,
        "shared_medium": True,
        "latency_sensitive": True,
        "safety_related": True,
        "requires_integrity": True,
        "requires_replay_protection": True,
        "requires_authentication": True,
    },
    "management": {
        "logical": True,
        "cross_zone": True,
    },
    "engineering_access": {
        "logical": True,
        "cross_zone": True,
        "privileged": True,
    },
    "fieldbus": {
        "logical": False,
        "safety_related": True,
    },
    "passive_telegram": {
        "logical": False,
        "open_transmission": True,
    },
    "telemetry": {
        "logical": True,
    },
    "idmz_transition": {
        "logical": True,
        "cross_zone": True,
    },
    "unknown_conduit": {
        "logical": False,
        "safety_related": False,
        "requires_integrity": False,
        "requires_replay_protection": False,
    },
}

# ============================================================
# CONDUIT SECURITY PROFILES
# ============================================================

CONDUIT_SECURITY_PROFILES = {
    "safety_critical": {
        "requires_integrity": True,
        "requires_authentication": True,
        "requires_replay_protection": True,
        "requires_monitoring": True,
    },
    "radio_safety": {
        "requires_encryption": True,
        "requires_integrity": True,
        "requires_authentication": True,
        "requires_replay_protection": True,
        "requires_latency_monitoring": True,
        "requires_jamming_detection": True,
        "requires_rf_anomaly_detection": True,
    },
    "engineering_access": {
        "requires_encryption": True,
        "requires_authentication": True,
        "requires_mfa": True,
        "requires_monitoring": True,
    },
    "management": {
        "requires_encryption": True,
        "requires_authentication": True,
        "requires_monitoring": True,
    },
    "fieldbus": {
        "requires_integrity": True,
    },
    "passive_telegram": {
        "requires_integrity": True,
    },
    "cross_zone_secure": {
        "requires_encryption": True,
        "requires_integrity": True,
        "requires_authentication": True,
        "requires_monitoring": True,
    },
    "telemetry": {
        "requires_encryption": True,
        "requires_integrity": True,
        "requires_authentication": True,
        "requires_monitoring": True,
    },
    "idmz_transition": {
        "logical": True,
        "cross_zone": True,
        "requires_firewall": True,
    },
}


# ============================================================
# TRANSMISSION CLASSES
# ============================================================

TRANSMISSION_CLASS = {"open", "closed"}


# ============================================================
# MEDIA ONTOLOGY
# ============================================================

MEDIA_ONTOLOGY = {
    "BURIED_COPPER": {
        "physical": True,
        "open_transmission": False,
        "transmission_class": "closed",
        "public_network": False,
        "supports_encryption": False,
    },
    "OFC_PRIVATE": {
        "physical": True,
        "open_transmission": False,
        "transmission_class": "closed",
        "public_network": False,
        "supports_encryption": True,
    },
    "PRIVATE_IP_NETWORK": {
        "physical": False,
        "open_transmission": False,
        "transmission_class": "closed",
        "public_network": False,
        "supports_encryption": True,
    },
    "RF_PUBLIC": {
        "physical": False,
        "open_transmission": True,
        "transmission_class": "open",
        "public_network": True,
        "supports_encryption": True,
    },
    "UNKNOWN": {
        "physical": False,
        "open_transmission": False,
        "transmission_class": "open",
        "public_network": False,
        "supports_encryption": False,
    },
}

# ============================================================
# TRANSPORT ONTOLOGY
# ============================================================

TRANSPORT_ONTOLOGY = {
    "rf": {
        "wireless": True,
        "public_network": True,
        "shared_medium": True,
        "supports_encryption": True,
        "supports_replay_protection": True,
        "high_jamming_risk": True,
        "deterministic": False,
        "latency_sensitive": True,
        "native_encryption": False,
        "overlay_encryption_possible": True,
    },
    "wifi": {
        "wireless": True,
        "public_network": True,
        "shared_medium": True,
        "supports_encryption": True,
        "high_attack_surface": True,
        "deterministic": False,
        "native_encryption": False,
        "overlay_encryption_possible": True,
    },
    "mpls": {
        "wireless": False,
        "public_network": False,
        "carrier_managed": True,
        "native_encryption": False,
        "overlay_encryption_possible": True,
        "requires_overlay_crypto": True,
        "transport_protocol": True,
        "deterministic": True,
        "latency_sensitive": True,
    },
    "ip_backbone": {
        "wireless": False,
        "public_network": False,
        "supports_encryption": True,
        "deterministic": False,
        "native_encryption": False,
        "overlay_encryption_possible": True,
    },
    "ethernet": {
        "wireless": False,
        "public_network": False,
        "supports_encryption": False,
        "deterministic": True,
        "native_encryption": False,
        "overlay_encryption_possible": True,
    },
    "fiber_optic": {
        "wireless": False,
        "public_network": False,
        "high_physical_security": True,
        "low_emi_susceptibility": True,
        "supports_high_bandwidth": True,
    },
    "copper_cable": {
        "wireless": False,
        "public_network": False,
        "high_emi_susceptibility": True,
        "physically_tappable": True,
    },
    "serial_rs485": {
        "wireless": False,
        "public_network": False,
        "legacy": True,
        "multidrop": True,
        "supports_encryption": False,
        "deterministic": True,
    },
    "can_bus": {
        "wireless": False,
        "public_network": False,
        "legacy": True,
        "broadcast_bus": True,
        "supports_encryption": False,
        "safety_related": True,
        "deterministic": True,
    },
    "mvb_bus": {
        "wireless": False,
        "public_network": False,
        "legacy": True,
        "broadcast_bus": True,
        "supports_encryption": False,
        "safety_related": True,
        "deterministic": True,
    },
    "wtb_bus": {
        "wireless": False,
        "public_network": False,
        "legacy": True,
        "broadcast_bus": True,
        "supports_encryption": False,
        "safety_related": True,
        "deterministic": True,
    },
    "unknown": {
        "wireless": False,
        "public_network": False,
        "supports_encryption": False,
        "deterministic": False,
    },
}

# ============================================================
# BEARER ONTOLOGY
# ============================================================

BEARER_ONTOLOGY = {
    "gsm_r": {
        "wireless": True,
        "public_network": True,
        "supports_encryption": True,
        "railway_radio": True,
    },
    "lte_r": {
        "wireless": True,
        "public_network": True,
        "supports_encryption": True,
        "railway_radio": True,
    },
    "unknown": {
        "wireless": False,
        "public_network": False,
        "supports_encryption": False,
        "railway_radio": False,
    },
}

# ============================================================
# PROTOCOL ONTOLOGY
# ============================================================

PROTOCOL_ONTOLOGY = {
    "RASTA": {
        "encrypted": False,
        "supports_encryption": True,
        "authenticated": True,
        "integrity_protected": True,
        "replay_protected": True,
        "wireless_capable": True,
        "safety_related": True,
        "protocol_class": "safety",
        "safety_domain": "vital",
        "stack_layer": "safety_protocol",
        "safety_flow": True,
    },
    "MCOMM": {
        "encrypted": True,
        "authenticated": True,
        "integrity_protected": True,
        "replay_protected": True,
        "wireless_capable": True,
        "safety_related": True,
        "protocol_class": "safety",
        "safety_domain": "vital",
        "stack_layer": "safety_protocol",
        "safety_flow": True,
    },
    "EURORADIO": {
        "encrypted": True,
        "authenticated": True,
        "integrity_protected": True,
        "replay_protected": True,
        "wireless_capable": True,
        "safety_related": True,
        "protocol_class": "safety",
        "safety_domain": "vital",
        "stack_layer": "safety_protocol",
        "safety_flow": True,
    },
    "EUROBALISE": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "legacy_safety_bus": True,
        "safety_related": True,
        "protocol_class": "fieldbus",
        "safety_domain": "field_vital",
        "functional_integrity": True,
        "stack_layer": "field_protocol",
        "passive_telegram_system": True,
    },
    "MVB": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "legacy_safety_bus": True,
        "safety_related": True,
        "protocol_class": "fieldbus",
        "safety_domain": "onboard_vital",
        "functional_integrity": True,
        "stack_layer": "field_protocol",
        "safety_flow": True,
    },
    "WTB": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "legacy_safety_bus": True,
        "safety_related": True,
        "protocol_class": "fieldbus",
        "safety_domain": "onboard_vital",
        "functional_integrity": True,
        "stack_layer": "field_protocol",
        "safety_flow": True,
    },
    "CAN": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "legacy_safety_bus": True,
        "safety_related": True,
        "protocol_class": "fieldbus",
        "safety_domain": "field_vital",
        "functional_integrity": True,
        "stack_layer": "field_protocol",
        "safety_flow": True,
    },
    "HTTPS": {
        "encrypted": True,
        "authenticated": True,
        "integrity_protected": True,
        "protocol_class": "management",
        "safety_related": False,
        "safety_domain": "non_vital",
        "stack_layer": "application_protocol",
        "replay_protected": True,
    },
    "SSH": {
        "encrypted": True,
        "authenticated": True,
        "integrity_protected": True,
        "protocol_class": "engineering",
        "safety_related": False,
        "safety_domain": "non_vital",
        "stack_layer": "application_protocol",
        "replay_protected": True,
    },
    "SYSLOG_TLS": {
        "encrypted": True,
        "authenticated": False,
        "supports_authentication": True,
        "integrity_protected": True,
        "protocol_class": "monitoring",
        "safety_related": False,
        "safety_domain": "non_vital",
        "stack_layer": "monitoring_protocol",
    },
    "SNMPV3": {
        "encrypted": True,
        "authenticated": True,
        "integrity_protected": True,
        "protocol_class": "management",
        "safety_related": False,
        "safety_domain": "non_vital",
        "stack_layer": "management_protocol",
        "replay_protected": True,
    },
    "OPC_UA": {
        "encrypted": True,
        "authenticated": True,
        "integrity_protected": True,
        "industrial_protocol": True,
        "protocol_class": "industrial",
        "safety_related": False,
        "safety_domain": "safety_adjacent",
        "stack_layer": "industrial_protocol",
        "replay_protected": True,
    },
    "MQTT_TLS": {
        "encrypted": True,
        "authenticated": True,
        "integrity_protected": True,
        "protocol_class": "telemetry",
        "safety_related": False,
        "safety_domain": "non_vital",
        "stack_layer": "telemetry_protocol",
    },
    "RFID_AIR": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "wireless_capable": True,
        "open_transmission": True,
        "protocol_class": "field_transport",
        "safety_related": True,
        "safety_domain": "field_vital",
        "stack_layer": "field_protocol",
        "passive_telegram_system": True,
    },
    "L2_TRANSPORT": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "wireless_capable": False,
        "safety_related": False,
        "protocol_class": "transport",
        "safety_domain": "non_vital",
        "stack_layer": "transport_protocol",
    },
    "MPLS": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "wireless_capable": False,
        "safety_related": False,
        "protocol_class": "transport",
        "safety_domain": "non_vital",
        "stack_layer": "transport_protocol",
    },
    "IP": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "wireless_capable": False,
        "safety_related": False,
        "protocol_class": "transport",
        "safety_domain": "non_vital",
        "stack_layer": "transport_protocol",
    },
    "KAVACH_EI_INTERFACE": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": True,
        "replay_protected": True,
        "wireless_capable": False,
        "safety_related": True,
        "protocol_class": "safety",
        "safety_domain": "vital",
        "stack_layer": "safety_protocol",
    },
    "UNKNOWN": {
        "encrypted": False,
        "authenticated": False,
        "integrity_protected": False,
        "replay_protected": False,
        "wireless_capable": False,
        "safety_related": False,
        "protocol_class": "unknown",
        "safety_domain": "non_vital",
        "stack_layer": "unknown",
    },
}

# ============================================================
# PROTOCOL → TRANSPORT
# ============================================================

PROTOCOL_TRANSPORT_MAP = {
    "EURORADIO": ["rf"],
    "MCOMM": ["rf"],
    "RASTA": ["ip_backbone", "ethernet"],
    "MVB": ["mvb_bus"],
    "WTB": ["wtb_bus"],
    "CAN": ["can_bus"],
    "HTTPS": ["ip_backbone", "ethernet"],
    "SSH": ["ip_backbone", "ethernet"],
    "SNMPV3": ["ip_backbone", "ethernet"],
    "SYSLOG_TLS": ["ip_backbone", "ethernet"],
    "OPC_UA": ["ip_backbone", "ethernet"],
    "MQTT_TLS": ["ip_backbone", "ethernet"],
    "RFID_AIR": ["rf"],
    "KAVACH_EI_INTERFACE": ["ethernet"],
}

# ============================================================
# TRANSPORT → MEDIA
# ============================================================

TRANSPORT_MEDIA_MAP = {
    "rf": ["RF_PUBLIC"],
    "mpls": ["PRIVATE_IP_NETWORK"],
    "ip_backbone": ["PRIVATE_IP_NETWORK"],
    "ethernet": ["PRIVATE_IP_NETWORK"],
    "fiber_optic": ["OFC_PRIVATE"],
    "copper_cable": ["BURIED_COPPER"],
    "serial_rs485": ["BURIED_COPPER"],
    "can_bus": ["BURIED_COPPER"],
    "mvb_bus": ["BURIED_COPPER"],
    "wtb_bus": ["BURIED_COPPER"],
}

# ============================================================
# BEARER → TRANSPORT
# ============================================================

BEARER_TRANSPORT_MAP = {
    "gsm_r": ["rf"],
    "lte_r": ["rf"],
}

# ============================================================
# STACK COMPATIBILITY
# ============================================================

STACK_COMPATIBILITY = {
    "EURORADIO": {
        "transport": ["rf"],
        "bearer": ["gsm_r", "lte_r"],
        "media": ["RF_PUBLIC"],
    },
    "MCOMM": {
        "transport": ["rf"],
        "bearer": ["gsm_r", "lte_r"],
        "media": ["RF_PUBLIC"],
    },
    "RASTA": {
        "transport": ["ip_backbone", "ethernet"],
        "media": ["PRIVATE_IP_NETWORK"],
    },
    "KAVACH_EI_INTERFACE": {
        "transport": ["ethernet"],
        "media": ["PRIVATE_IP_NETWORK"],
    },
    "MVB": {
        "transport": ["mvb_bus"],
        "media": ["BURIED_COPPER"],
    },
    "WTB": {
        "transport": ["wtb_bus"],
        "media": ["BURIED_COPPER"],
    },
    "CAN": {
        "transport": ["can_bus"],
        "media": ["BURIED_COPPER"],
    },
}

# ============================================================
# DEFAULT CONNECTION STACKS
# ============================================================

DEFAULT_CONNECTION_STACK = {
    "EURORADIO": {
        "transport": "rf",
        "bearer": "gsm_r",
        "media": "RF_PUBLIC",
    },
    "MCOMM": {
        "transport": "rf",
        "bearer": "gsm_r",
        "media": "RF_PUBLIC",
    },
    "RASTA": {
        "transport": "ip_backbone",
        "media": "PRIVATE_IP_NETWORK",
    },
    "HTTPS": {
        "transport": "ip_backbone",
        "media": "PRIVATE_IP_NETWORK",
    },
    "SSH": {
        "transport": "ip_backbone",
        "media": "PRIVATE_IP_NETWORK",
    },
    "SNMPV3": {
        "transport": "ip_backbone",
        "media": "PRIVATE_IP_NETWORK",
    },
    "SYSLOG_TLS": {
        "transport": "ip_backbone",
        "media": "PRIVATE_IP_NETWORK",
    },
    "OPC_UA": {
        "transport": "ethernet",
        "media": "PRIVATE_IP_NETWORK",
    },
    "MQTT_TLS": {
        "transport": "ip_backbone",
        "media": "PRIVATE_IP_NETWORK",
    },
    "RFID_AIR": {
        "transport": "rf",
        "media": "RF_PUBLIC",
    },
    "L2 TRANSPORT": {
        "transport": "ethernet",
        "media": "PRIVATE_IP_NETWORK",
    },
}

# ============================================================
# LOOKUPS
# ============================================================

VALID_ZONES = set(ZONE_ONTOLOGY.keys())

VALID_PROTOCOLS = set(PROTOCOL_ONTOLOGY.keys())

VALID_TRANSPORTS = set(TRANSPORT_ONTOLOGY.keys())

VALID_MEDIA = set(MEDIA_ONTOLOGY.keys())

VALID_BEARERS = set(BEARER_ONTOLOGY.keys())

VALID_NODE_TYPES = set(ASSET_ONTOLOGY.keys())

VALID_CONDUITS = set(CONDUIT_ONTOLOGY.keys())

VALID_PURDUE_LEVELS = set(PURDUE_LEVELS.keys())

# ============================================================
# TRUST GROUPS
# ============================================================

TRUSTED_ZONES = {z for z, v in ZONE_ONTOLOGY.items() if v.get("trust") == "trusted"}

SEMI_TRUSTED_ZONES = {
    z for z, v in ZONE_ONTOLOGY.items() if v.get("trust") == "semi_trusted"
}

LOW_TRUST_ZONES = {z for z, v in ZONE_ONTOLOGY.items() if v.get("trust") == "low"}

# ============================================================
# ASSET NORMALIZATION
# ============================================================

for asset_name, asset in ASSET_ONTOLOGY.items():

    if "allowed_purdue" not in asset:

        asset["allowed_purdue"] = [asset.get("purdue", UNKNOWN_PURDUE)]

    if "allowed_zones" not in asset:

        asset["allowed_zones"] = [asset.get("zone", UNKNOWN_ZONE)]

    if "safety_domain" not in asset:

        asset["safety_domain"] = UNKNOWN_SAFETY_DOMAIN

# ============================================================
# SAFETY LOOKUPS
# ============================================================

SAFETY_CRITICAL_TYPES = {
    k for k, v in ASSET_ONTOLOGY.items() if v.get("safety_critical", False)
}

# ============================================================
# SEMANTIC GROUPS
# ============================================================

ENCRYPTED_PROTOCOLS = {
    protocol
    for protocol, props in PROTOCOL_ONTOLOGY.items()
    if props.get("encrypted", False)
}

SAFETY_PROTOCOLS = {
    protocol
    for protocol, props in PROTOCOL_ONTOLOGY.items()
    if props.get("safety_related", False)
}

LEGACY_PROTOCOLS = {
    protocol
    for protocol, props in PROTOCOL_ONTOLOGY.items()
    if props.get("legacy_safety_bus", False)
}

MANAGEMENT_PROTOCOLS = {
    protocol
    for protocol, props in PROTOCOL_ONTOLOGY.items()
    if props.get("protocol_class") == "management"
}

PUBLIC_NETWORK_TRANSPORTS = {
    transport
    for transport, props in TRANSPORT_ONTOLOGY.items()
    if props.get("public_network", False)
}

ENGINEERING_ACCESS_TYPES = {
    asset
    for asset, props in ASSET_ONTOLOGY.items()
    if props.get("engineering_access", False)
}

# ============================================================
# PKI / TRUST ANCHOR TYPES
# ============================================================

PKI_INTERMEDIARY_TYPES = {
    asset
    for asset, props in ASSET_ONTOLOGY.items()
    if (
        props.get("crypto_trust_anchor", False)
        or props.get("engineering_access", False)
        or props.get("security_enforcement", False)
    )
} | {
    "s_kavach",
    "l_kavach",
    "train_radio",
}

TRUST_ANCHOR_TYPES = {
    asset
    for asset, props in ASSET_ONTOLOGY.items()
    if props.get("crypto_trust_anchor", False)
}


HIGH_ATTACK_SURFACE_TYPES = {
    asset
    for asset, props in ASSET_ONTOLOGY.items()
    if (
        props.get("radio_exposed", False)
        or props.get("engineering_access", False)
        or props.get("safety_boundary", False)
    )
}

REMOTE_ACCESS_CAPABLE_TYPES = {
    asset
    for asset, props in ASSET_ONTOLOGY.items()
    if (props.get("engineering_access", False) or props.get("high_privilege", False))
}

RADIO_ATTACK_SURFACE_TYPES = {
    asset
    for asset, props in ASSET_ONTOLOGY.items()
    if props.get("radio_exposed", False)
}

UNENCRYPTED_PROTOCOLS = {
    protocol
    for protocol, props in PROTOCOL_ONTOLOGY.items()
    if (not props.get("encrypted", False) and protocol != UNKNOWN_PROTOCOL)
}

# ============================================================
# ASSET CONSTRAINT LOOKUPS
# ============================================================

VALID_PURDUE_BY_ASSET = {
    asset: set(asset_props.get("allowed_purdue", []))
    for asset, asset_props in ASSET_ONTOLOGY.items()
}

ALLOWED_ZONES_BY_ASSET = {
    asset: set(asset_props.get("allowed_zones", []))
    for asset, asset_props in ASSET_ONTOLOGY.items()
}


# ============================================================
# ZONE REQUIREMENTS
# ============================================================

ZONE_REQUIREMENTS = {
    zone: {
        "security_level": props.get(
            "security_level",
            "SL1",
        ),
        "trust": props.get(
            "trust",
            "low",
        ),
    }
    for zone, props in ZONE_ONTOLOGY.items()
}

# ============================================================
# ACCESSORS
# ============================================================


def get_zone_deployment_domain(zone: str) -> str:

    return get_zone_ontology(zone).get(
        "deployment_domain",
        "external",
    )


def get_asset_ontology(node_type: str) -> dict:

    if not node_type:

        return ASSET_ONTOLOGY[UNKNOWN_NODE]

    return ASSET_ONTOLOGY.get(
        str(node_type).strip().lower(),
        ASSET_ONTOLOGY[UNKNOWN_NODE],
    )


def get_bearer_ontology(bearer: str) -> dict:

    if not bearer:

        return BEARER_ONTOLOGY[UNKNOWN_BEARER]

    return BEARER_ONTOLOGY.get(
        str(bearer).strip().lower(),
        BEARER_ONTOLOGY[UNKNOWN_BEARER],
    )


def get_protocol_ontology(protocol: str) -> dict:

    if not protocol:

        return PROTOCOL_ONTOLOGY[UNKNOWN_PROTOCOL]

    return PROTOCOL_ONTOLOGY.get(
        str(protocol).strip().upper(),
        PROTOCOL_ONTOLOGY[UNKNOWN_PROTOCOL],
    )


def get_transport_ontology(transport: str) -> dict:

    if not transport:

        return TRANSPORT_ONTOLOGY[UNKNOWN_TRANSPORT]

    return TRANSPORT_ONTOLOGY.get(
        str(transport).strip().lower(),
        TRANSPORT_ONTOLOGY[UNKNOWN_TRANSPORT],
    )


def get_media_ontology(media: str) -> dict:

    if not media:

        return MEDIA_ONTOLOGY[UNKNOWN_MEDIA]

    return MEDIA_ONTOLOGY.get(
        str(media).strip().upper(),
        MEDIA_ONTOLOGY[UNKNOWN_MEDIA],
    )


def get_zone_ontology(zone: str) -> dict:

    if not zone:

        return ZONE_ONTOLOGY[UNKNOWN_ZONE]

    return ZONE_ONTOLOGY.get(
        str(zone).strip().lower(),
        ZONE_ONTOLOGY[UNKNOWN_ZONE],
    )


def get_conduit_profile(conduit_class: str) -> dict:

    if not conduit_class:

        return {}

    return CONDUIT_SECURITY_PROFILES.get(
        str(conduit_class).strip().lower(),
        {},
    )


def transport_is_public_network(transport: str) -> bool:

    return get_transport_ontology(transport).get(
        "public_network",
        False,
    )


def transport_is_wireless(transport: str) -> bool:

    return get_transport_ontology(transport).get(
        "wireless",
        False,
    )


def transport_is_latency_sensitive(transport: str) -> bool:

    return get_transport_ontology(transport).get(
        "latency_sensitive",
        False,
    )


def transport_has_high_jamming_risk(transport: str) -> bool:

    return get_transport_ontology(transport).get(
        "high_jamming_risk",
        False,
    )


def media_is_open_transmission(media: str) -> bool:

    return get_media_ontology(media).get(
        "open_transmission",
        False,
    )


def media_is_public_network(media: str) -> bool:

    return get_media_ontology(media).get(
        "public_network",
        False,
    )


def bearer_is_wireless(bearer: str) -> bool:

    return get_bearer_ontology(bearer).get(
        "wireless",
        False,
    )


def bearer_is_railway_radio(bearer: str) -> bool:

    return get_bearer_ontology(bearer).get(
        "railway_radio",
        False,
    )


def protocol_is_safety_related(protocol: str) -> bool:

    return get_protocol_ontology(protocol).get(
        "safety_related",
        False,
    )


def protocol_is_wireless_capable(protocol: str) -> bool:

    return get_protocol_ontology(protocol).get(
        "wireless_capable",
        False,
    )


def protocol_is_encrypted(protocol: str) -> bool:

    return get_protocol_ontology(protocol).get(
        "encrypted",
        False,
    )


def protocol_is_authenticated(protocol: str) -> bool:

    return get_protocol_ontology(protocol).get(
        "authenticated",
        False,
    )


def protocol_has_integrity(protocol: str) -> bool:

    return get_protocol_ontology(protocol).get(
        "integrity_protected",
        False,
    )


def protocol_has_replay_protection(protocol: str) -> bool:

    return get_protocol_ontology(protocol).get(
        "replay_protected",
        False,
    )


def asset_has_engineering_access(asset_type: str) -> bool:

    return get_asset_ontology(asset_type).get(
        "engineering_access",
        False,
    )


def get_zone_trust_domain(
    zone: str,
) -> str:

    return get_zone_ontology(zone).get(
        "trust_domain",
        "unknown",
    )


def zones_cross_trust_domain(
    src_zone: str,
    dst_zone: str,
) -> bool:

    return get_zone_trust_domain(src_zone) != get_zone_trust_domain(dst_zone)


def is_transit_zone(zone: str) -> bool:

    return str(zone).strip().lower() in TRANSIT_ZONES


def is_transit_flow(src_zone: str, dst_zone: str) -> bool:

    return is_transit_zone(src_zone) or is_transit_zone(dst_zone)


def is_valid_pki_endpoint(asset_type: str) -> bool:

    return str(asset_type).strip().lower() in PKI_INTERMEDIARY_TYPES


def protocol_is_safety_flow(protocol: str) -> bool:

    return get_protocol_ontology(protocol).get(
        "safety_flow",
        False,
    )


# ============================================================
# LEGACY
# ============================================================

PURDUE_SEMANTICS = PURDUE_LEVELS

PURDUE_LEVEL_DESCRIPTIONS = {k: v["description"] for k, v in PURDUE_LEVELS.items()}

REQUIRED_LINKS = {}


# ============================================================
# ONTOLOGY CONSISTENCY CHECKS
# ============================================================

assert UNKNOWN_PROTOCOL in PROTOCOL_ONTOLOGY
assert UNKNOWN_TRANSPORT in TRANSPORT_ONTOLOGY
assert UNKNOWN_MEDIA in MEDIA_ONTOLOGY
assert UNKNOWN_BEARER in BEARER_ONTOLOGY
assert UNKNOWN_ZONE in ZONE_ONTOLOGY
assert UNKNOWN_NODE in ASSET_ONTOLOGY

for protocol, transports in PROTOCOL_TRANSPORT_MAP.items():

    assert protocol in PROTOCOL_ONTOLOGY

    for transport in transports:

        assert transport in TRANSPORT_ONTOLOGY

for transport, media_list in TRANSPORT_MEDIA_MAP.items():

    assert transport in TRANSPORT_ONTOLOGY

    for media in media_list:

        assert media in MEDIA_ONTOLOGY

for bearer, transports in BEARER_TRANSPORT_MAP.items():

    assert bearer in BEARER_ONTOLOGY

    for transport in transports:

        assert transport in TRANSPORT_ONTOLOGY

for asset_name, asset in ASSET_ONTOLOGY.items():

    zone = asset.get("zone", UNKNOWN_ZONE)
    purdue = asset.get("purdue", UNKNOWN_PURDUE)

    assert zone in ZONE_ONTOLOGY, f"Invalid zone in asset {asset_name}: {zone}"

    assert (
        purdue in PURDUE_LEVELS
    ), f"Invalid Purdue level in asset {asset_name}: {purdue}"

    allowed = ZONE_ONTOLOGY[zone].get(
        "allowed_purdue",
        [],
    )

    assert purdue in allowed, (
        f"Asset {asset_name} violates zone Purdue policy: "
        f"{purdue} not allowed in {zone}"
    )

    missing = []

    for conduit_name in VALID_CONDUIT_CLASSES:

        if (
            conduit_name not in CONDUIT_SECURITY_PROFILES
            and conduit_name not in CONDUIT_ONTOLOGY
            and conduit_name != "generic"
        ):
            missing.append(conduit_name)

    assert not missing, "Undefined conduit classes: " + ", ".join(sorted(missing))

# ============================================================
# RENDER COLORS
# ============================================================
ZONE_COLORS = {
    # Enterprise
    "enterprise_it": "#d9e2f3",
    "business_systems": "#ddebf7",
    # IDMZ / Security
    "idmz": "#f4cccc",
    "security_management": "#ea9999",
    "external_security": "#e6b8af",
    # Operations
    "operations": "#d9ead3",
    "engineering": "#b6d7a8",
    "maintenance": "#93c47d",
    # Telecom
    "telecom_core": "#cfe2f3",
    "radio_access": "#9fc5e8",
    # Safety / Interlocking
    "interlocking": "#ffe599",
    # Field
    "field": "#f9cb9c",
    # Onboard
    "onboard": "#d5a6bd",
    # Unknown
    "unknown_zone": "#cccccc",
}
# ============================================================
# PURDUE COLORS
# ============================================================
PURDUE_COLORS = {
    "L5 Enterprise": "#1f4e79",
    "L4 Business": "#2f75b5",
    "L3.5 IDMZ": "#c00000",
    "L3.5 Security": "#e06666",
    "L3 Operations": "#6aa84f",
    "L2 Telecom": "#3d85c6",
    "L1 Telecom": "#6fa8dc",
    "L2 Interlocking": "#f1c232",
    "L1 Interlocking": "#ffd966",
    "L0 Field": "#f6b26b",
    "Onboard": "#8e7cc3",
    "Unknown": "#999999",
}

# ============================================================
# PURDUE RENDER ORDER
# TOP -> BOTTOM
# ============================================================

PURDUE_RENDER_ORDER = [
    "L5 Enterprise",
    "L4 Business",
    "L3.5 IDMZ",
    "L3.5 Security",
    "L3 Operations",
    "L2 Telecom",
    "L1 Telecom",
    "L2 Interlocking",
    "L1 Interlocking",
    "L0 Field",
    "Onboard",
    "Unknown",
]


# ============================================================
# ZONE BOUNDS
# Graph clustering / rendering hierarchy
# ============================================================

# ============================================================
# CLUSTER COLORS
# ============================================================

CLUSTER_COLORS = {
    "Enterprise Services": "#d9e2f3",
    "Security Monitoring": "#ffe599",
    "SOC Operations": "#fff2cc",
    "Key Management": "#ead1dc",
    "Operations Management": "#bdd7ee",
    "Maintenance Engineering": "#d9d9d9",
    "Maintenance Access": "#d0e0e3",
    "Movement Authority": "#f4cccc",
    "Interlocking Core": "#ea9999",
    "Train Detection": "#d9ead3",
    "Wayside Control": "#b6d7a8",
    "Field Execution": "#93c47d",
    "Radio Communication": "#d9b3ff",
    "Trackside Radio": "#c9daf8",
    "Onboard Radio": "#d5a6bd",
    "Telecom Gateway": "#a2c4c9",
    "Core Transport": "#76a5af",
    "Fiber Backbone": "#6fa8dc",
    "Onboard ATP": "#d9b3ff",
    "Event Logging": "#cccccc",
    "General": "#eeeeee",
}

# ============================================================
# DETACHED DOMAINS
# ============================================================

DETACHED_PURDUE_DOMAINS = {"Onboard", "Unknown", "external_security"}

# ============================================================
# ZONE BOUNDS
# ============================================================


ZONE_BOUNDS = {
    "enterprise_it": {
        "group": "enterprise",
        "rank": 1,
    },
    "business_systems": {
        "group": "enterprise",
        "rank": 2,
    },
    "idmz": {
        "group": "security",
        "rank": 3,
    },
    "security_management": {
        "group": "security",
        "rank": 4,
    },
    "external_security": {
        "group": "security",
        "rank": 5,
    },
    "operations": {
        "group": "operations",
        "rank": 6,
    },
    "engineering": {
        "group": "operations",
        "rank": 7,
    },
    "maintenance": {
        "group": "operations",
        "rank": 8,
    },
    "telecom_core": {
        "group": "telecom",
        "rank": 9,
    },
    "radio_access": {
        "group": "telecom",
        "rank": 10,
    },
    "interlocking": {
        "group": "safety",
        "rank": 11,
    },
    "field": {
        "group": "field",
        "rank": 12,
    },
    "onboard": {
        "group": "mobile",
        "rank": 13,
    },
    "unknown_zone": {
        "group": "unknown",
        "rank": 99,
    },
}

# ============================================================
# RENDER ACCESSORS
# ============================================================


def get_zone_color(zone: str) -> str:

    return ZONE_COLORS.get(
        str(zone).strip().lower(),
        "#CCCCCC",
    )


def get_purdue_color(level: str) -> str:

    return PURDUE_COLORS.get(
        normalize_purdue(level),
        "#999999",
    )


def get_zone_bounds(zone: str) -> dict:

    return ZONE_BOUNDS.get(
        str(zone).strip().lower(),
        {
            "group": "unknown",
            "rank": 99,
        },
    )


# ============================================================
# CLUSTER ACCESSORS
# ============================================================


def get_cluster_color(
    cluster: str,
) -> str:
    """
    Canonical cluster color lookup.
    """

    return CLUSTER_COLORS.get(
        str(cluster).strip(),
        "#eeeeee",
    )


def is_valid_cluster(
    cluster: str,
) -> bool:
    """
    Canonical cluster validation.
    """

    return str(cluster).strip() in CLUSTER_COLORS


def normalize_cluster(
    cluster: str,
) -> str:
    """
    Canonical cluster normalization.
    """

    if not cluster:

        return "General"

    cluster = str(cluster).strip()

    for canonical in CLUSTER_COLORS:

        if canonical.lower() == cluster.lower():

            return canonical

    return "General"


# ============================================================
# PURDUE HELPERS
# ============================================================


def get_purdue_order(level: str) -> int:
    """
    Deterministic Purdue sorting order.
    Lower number = higher layer.
    """

    return PURDUE_ORDER_INDEX.get(
        normalize_purdue(level),
        999,
    )


# ============================================================
# PURDUE ORDER INDEX
# ============================================================

PURDUE_ORDER_INDEX = {level: idx for idx, level in enumerate(PURDUE_RENDER_ORDER)}


def is_valid_purdue(level: str) -> bool:
    """
    Canonical Purdue validation.
    """

    return normalize_purdue(level) != "Unknown"


def normalize_purdue(level: str) -> str:
    """
    Canonical Purdue normalization.
    """

    if not level:

        return "Unknown"

    level = str(level).strip()

    for canonical in PURDUE_RENDER_ORDER:

        if canonical.lower() == level.lower():

            return canonical

    return "Unknown"


def purdue_rank_sort(nodes: list[dict]) -> list[dict]:
    """
    Stable deterministic Purdue sorting.
    """

    return sorted(
        nodes,
        key=lambda n: (
            get_purdue_order(
                n.get(
                    "purdue_level",
                    "Unknown",
                )
            ),
            str(
                n.get(
                    "zone",
                    "",
                )
            ).lower(),
            str(
                n.get(
                    "type",
                    "",
                )
            ).lower(),
            str(
                n.get(
                    "label",
                    "",
                )
            ).lower(),
        ),
    )
