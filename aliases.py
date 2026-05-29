"""
aliases.py
FINAL CANONICAL NORMALIZATION LAYER
IEC62443 + EN50126 + EN50129 + EN50159 + Kavach
"""

import logging
import re
from ontology import (
    VALID_NODE_TYPES,
    VALID_PROTOCOLS,
    VALID_TRANSPORTS,
    VALID_BEARERS,
    VALID_MEDIA,
    VALID_CONDUITS,
    VALID_ZONES,
    VALID_PURDUE_LEVELS,
    STACK_COMPATIBILITY,
    UNKNOWN_NODE,
    UNKNOWN_PROTOCOL,
    UNKNOWN_TRANSPORT,
    UNKNOWN_ZONE,
    UNKNOWN_BEARER,
    UNKNOWN_MEDIA,
    UNKNOWN_PURDUE,
)

logger = logging.getLogger(__name__)


# ============================================================
# TOKEN NORMALIZATION
# ============================================================
def canonicalize_token(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip().lower()
    value = re.sub(
        r"[\-_]+",
        " ",
        value,
    )
    value = re.sub(
        r"\s+",
        " ",
        value,
    )
    return value.strip()


def to_snake_case(value: str) -> str:
    return canonicalize_token(value).replace(
        " ",
        "_",
    )


# ============================================================
# NODE TYPE ALIASES
# ============================================================
NODE_TYPE_ALIASES = {
    "dmi": "driver_machine_interface",
    "driver machine interface": "driver_machine_interface",
    "driver interface": "driver_machine_interface",
    "cab display": "driver_machine_interface",
    "biu": "brake_interface_unit",
    "brake interface": "brake_interface_unit",
    "brake interface unit": "brake_interface_unit",
    "speed sensor": "speed_sensor",
    "tachometer": "speed_sensor",
    "train radio": "train_radio",
    "radio modem": "train_radio",
    "balise reader": "onboard_rfid_reader",
    "rfid reader": "onboard_rfid_reader",
    "lkavach": "l_kavach",
    "l kavach": "l_kavach",
    "l-kavach": "l_kavach",
    "loco kavach": "l_kavach",
    "gsmr": "railway_radio_base_station",
    "gsm-r": "railway_radio_base_station",
    "gsm r": "railway_radio_base_station",
    "radio bts": "railway_radio_base_station",
    "base station": "railway_radio_base_station",
    "radio gateway": "radio_gateway",
    "skavach": "s_kavach",
    "s-kavach": "s_kavach",
    "s kavach": "s_kavach",
    "stationary kavach": "s_kavach",
    "interlocking": "electronic_interlocking",
    "electronic interlocking": "electronic_interlocking",
    "ei": "electronic_interlocking",
    "object controller": "object_controller",
    "oc": "object_controller",
    "point machine": "point_machine_controller",
    "point machine controller": "point_machine_controller",
    "point controller": "point_machine_controller",
    "signal controller": "signal_controller",
    "axle counter": "axle_counter_head",
    "axle counter evaluator": "axle_counter_evaluator",
    "track circuit": "track_circuit",
    "balise": "trackside_rfid_tag",
    "balise tag": "trackside_rfid_tag",
    "rfid balise": "trackside_rfid_tag",
    "rfid balise tag": "trackside_rfid_tag",
    "eurobalise": "trackside_rfid_tag",
    "traffic management": "tms",
    "traffic management system": "tms",
    "network management system": "nms",
    "operations workstation": "operations_workstation",
    "engineering workstation": "engineering_workstation",
    "soc": "soc_server",
    "soc server": "soc_server",
    "siem": "siem",
    "kms_server": "external_kms_server",
    "key management system": "external_kms_server",
    "external cryptographic kms_server": "external_kms_server",
    "external kms_server": "external_kms_server",
    "firewall": "firewall",
    "next generation firewall": "firewall",
    "ngfw": "firewall",
    "vpn": "vpn_gateway",
    "vpn gateway": "vpn_gateway",
    "jump host": "jump_host",
    "jump server": "jump_host",
    "bastion host": "jump_host",
    "data diode": "data_diode",
    "ids": "ids_sensor",
    "intrusion detection": "ids_sensor",
    "intrusion detection system": "ids_sensor",
    "ips": "ips_sensor",
    "intrusion prevention": "ips_sensor",
    "intrusion prevention system": "ips_sensor",
    "certificate authority": "certificate_authority",
    "ca server": "certificate_authority",
    "pki": "certificate_authority",
    "vulnerability scanner": "vulnerability_scanner",
    "scanner": "vulnerability_scanner",
    "log collector": "log_collector",
    "collector": "log_collector",
    "mpls router": "mpls_router",
    "pe router": "mpls_router",
    "telecom gateway": "telecom_gateway",
    "enterprise server": "enterprise_server",
    "it server": "enterprise_server",
}
# ============================================================
# PROTOCOL ALIASES
# ============================================================
PROTOCOL_ALIASES = {
    "https": "HTTPS",
    "https tls": "HTTPS",
    "ssh": "SSH",
    "snmpv3": "SNMPV3",
    "syslog tls": "SYSLOG_TLS",
    "opc ua": "OPC_UA",
    "opcua": "OPC_UA",
    "mqtt tls": "MQTT_TLS",
    "mqtt/tls": "MQTT_TLS",
    "rasta": "RASTA",
    "euroradio": "EURORADIO",
    "euro radio": "EURORADIO",
    "etcs euroradio": "EURORADIO",
    "eurobalise": "EUROBALISE",
    "mvb": "MVB",
    "wtb": "WTB",
    "can": "CAN",
    "mcomm": "MCOMM",
    "kavach_ei_interface": "KAVACH_EI_INTERFACE",
}
TRANSPORT_ALIASES = {
    "mpls": "mpls",
    "ethernet": "ethernet",
    "wifi": "wifi",
    "rf": "rf",
    "fiber": "fiber_optic",
    "fiber optic": "fiber_optic",
    "serial": "serial_rs485",
    "rs485": "serial_rs485",
    "can bus": "can_bus",
    "mvb bus": "mvb_bus",
    "wtb bus": "wtb_bus",
}
BEARER_ALIASES = {
    "gsmr": "gsm_r",
    "gsm-r": "gsm_r",
    "gsm r": "gsm_r",
    "lte-r": "lte_r",
    "lte r": "lte_r",
}
MEDIA_ALIASES = {
    "rf": "RF_PUBLIC",
    "public rf": "RF_PUBLIC",
    "wireless": "RF_PUBLIC",
    "fiber": "OFC_PRIVATE",
    "optic fiber": "OFC_PRIVATE",
    "ofc": "OFC_PRIVATE",
    "private ip": "PRIVATE_IP_NETWORK",
    "private network": "PRIVATE_IP_NETWORK",
    "copper": "BURIED_COPPER",
}
ZONE_ALIASES = {
    "telecom": "telecom_core",
    "radio": "radio_access",
    "radio network": "radio_access",
    "field devices": "field",
    "corp it": "enterprise_it",
    "enterprise": "enterprise_it",
    "enterprise-it": "enterprise_it",
    "enterprise it zone": "enterprise_it",
    "soc": "security_management",
    "security": "security_management",
    "maintenance zone": "maintenance",
    "trackside": "field",
    "wayside": "field",
    "onboard train": "onboard",
}
PURDUE_ALIASES = {
    "l0": "L0 Field",
    "level 0": "L0 Field",
    "l1": "L1 Interlocking",
    "level 1": "L1 Interlocking",
    "l2": "L2 Interlocking",
    "level 2": "L2 Interlocking",
    "l2 station control": "L2 Interlocking",
    "l3": "L3 Operations",
    "level 3": "L3 Operations",
    "idmz": "L3.5 IDMZ",
    "dmz": "L3.5 IDMZ",
    "security": "L3.5 Security",
    "enterprise": "L5 Enterprise",
}
CONDUIT_ALIASES = {
    "cross zone": "cross_zone_secure",
    "cross-zone": "cross_zone_secure",
    "safety": "safety_critical",
    "enterprise ot": "enterprise_ot",
}


# ============================================================
# NORMALIZERS
# ============================================================
def normalize_node_type(raw: str) -> str:
    if not raw:
        return UNKNOWN_NODE
    value = canonicalize_token(raw)
    canonical = NODE_TYPE_ALIASES.get(value)
    if canonical:
        return canonical
    snake = to_snake_case(value)
    if snake in VALID_NODE_TYPES:
        return snake
    logger.warning("Invalid node type: %s", raw)
    return UNKNOWN_NODE


def normalize_protocol(raw: str) -> str:
    if not raw:
        return UNKNOWN_PROTOCOL
    value = canonicalize_token(raw)
    canonical = PROTOCOL_ALIASES.get(value)
    if canonical:
        return canonical
    upper = value.upper()
    if upper in VALID_PROTOCOLS:
        return upper
    logger.warning("Unknown protocol: %s", raw)
    return UNKNOWN_PROTOCOL


def normalize_transport(raw: str) -> str:
    if not raw:
        return UNKNOWN_TRANSPORT
    value = canonicalize_token(raw)
    canonical = TRANSPORT_ALIASES.get(value)
    if canonical:
        return canonical
    snake = to_snake_case(value)
    if snake in VALID_TRANSPORTS:
        return snake
    logger.warning("Unknown transport: %s", raw)
    return UNKNOWN_TRANSPORT


def normalize_bearer(raw: str) -> str:
    if not raw:
        return UNKNOWN_BEARER
    value = canonicalize_token(raw)
    canonical = BEARER_ALIASES.get(value)
    if canonical:
        return canonical
    snake = to_snake_case(value)
    if snake in VALID_BEARERS:
        return snake
    logger.warning("Unknown bearer: %s", raw)
    return UNKNOWN_BEARER


def normalize_media(raw: str) -> str:
    if not raw:
        return UNKNOWN_MEDIA
    value = canonicalize_token(raw)
    canonical = MEDIA_ALIASES.get(value)
    if canonical:
        return canonical
    upper = value.upper()
    if upper in VALID_MEDIA:
        return upper
    logger.warning("Unknown media: %s", raw)
    return UNKNOWN_MEDIA


def normalize_zone(raw: str) -> str:
    if not raw:
        return UNKNOWN_ZONE
    value = canonicalize_token(raw)
    canonical = ZONE_ALIASES.get(value)
    if canonical:
        return canonical
    snake = to_snake_case(value)
    if snake in VALID_ZONES:
        return snake
    logger.warning("Unknown zone: %s", raw)
    return UNKNOWN_ZONE


def normalize_purdue(raw: str) -> str:
    if not raw:
        return UNKNOWN_PURDUE
    value = canonicalize_token(raw)
    canonical = PURDUE_ALIASES.get(value)
    if canonical in VALID_PURDUE_LEVELS:
        return canonical
    if raw in VALID_PURDUE_LEVELS:
        return raw
    logger.warning("Unknown Purdue level: %s", raw)
    return UNKNOWN_PURDUE


def normalize_conduit(raw: str) -> str:
    if not raw:
        return "unknown"
    value = canonicalize_token(raw)
    canonical = CONDUIT_ALIASES.get(value)
    if canonical:
        return canonical
    snake = to_snake_case(value)
    if snake in VALID_CONDUITS:
        return snake
    logger.warning("Unknown conduit: %s", raw)
    return "unknown"


# ============================================================
# LABEL INFERENCE
# ============================================================
def infer_type_from_label(label: str) -> str:
    if not label:
        return UNKNOWN_NODE
    value = canonicalize_token(label)
    direct = normalize_node_type(value)
    if direct != UNKNOWN_NODE:
        return direct
    tokens = set(
        re.findall(
            r"[a-z0-9]+",
            value,
        )
    )
    best_match = None
    best_score = 0
    for alias, canonical in NODE_TYPE_ALIASES.items():
        alias_tokens = set(alias.split())
        score = len(tokens & alias_tokens)
        if score > best_score:
            best_score = score
            best_match = canonical
    if best_score >= 2:
        return best_match
    return UNKNOWN_NODE


# ============================================================
# STACK VALIDATION
# ============================================================
def is_valid_stack(
    protocol: str,
    transport: str | None = None,
    bearer: str | None = None,
    media: str | None = None,
) -> bool:
    protocol = normalize_protocol(protocol)
    if protocol == UNKNOWN_PROTOCOL:
        return False
    rules = STACK_COMPATIBILITY.get(
        protocol,
        {},
    )
    if transport:
        transport = normalize_transport(transport)
        if transport == UNKNOWN_TRANSPORT:
            return False
        allowed = rules.get(
            "transport",
            [],
        )
        if allowed and transport not in allowed:
            return False
    if bearer:
        bearer = normalize_bearer(bearer)
        if bearer == UNKNOWN_BEARER:
            return False
        allowed = rules.get(
            "bearer",
            [],
        )
        if allowed and bearer not in allowed:
            return False
    if media:
        media = normalize_media(media)
        if media == UNKNOWN_MEDIA:
            return False
        allowed = rules.get(
            "media",
            [],
        )
        if allowed and media not in allowed:
            return False
    return True


# ============================================================
# VALIDATION HELPERS
# ============================================================
def is_valid_protocol(protocol: str) -> bool:
    return normalize_protocol(protocol) in VALID_PROTOCOLS


def is_valid_transport(transport: str) -> bool:
    return normalize_transport(transport) in VALID_TRANSPORTS


def is_valid_bearer(bearer: str) -> bool:
    return normalize_bearer(bearer) in VALID_BEARERS


def is_valid_media(media: str) -> bool:
    return normalize_media(media) in VALID_MEDIA


def is_valid_node_type(node_type: str) -> bool:
    return normalize_node_type(node_type) in VALID_NODE_TYPES


def is_valid_zone(zone: str) -> bool:
    return normalize_zone(zone) in VALID_ZONES


def is_valid_conduit(conduit: str) -> bool:
    return normalize_conduit(conduit) in VALID_CONDUITS
