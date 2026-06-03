"""
purdue_mapper.py

Railway Purdue semantic inference layer.

DESIGN PRINCIPLE:
NO duplicated mappings.

Single source of truth:
    railway_rules.py

This module ONLY:
- infers Purdue levels
- provides helper utilities
- provides grouping helpers
"""

from railway_rules import RAILWAY_PURDUE_LEVELS, VALID_PURDUE_BY_ASSET

# ============================================================
# ZONE → DEFAULT PURDUE
# ============================================================

ZONE_TO_PURDUE = {
    "enterprise_it": "L5 Enterprise",
    "idmz": "L3.5 Security",
    "security_management": "L3.5 Security",
    "external_security": "External Security",
    "operations": "L3 Operations",
    "maintenance": "L3 Operations",
    "supervisory": "L2 Station Control",
    "station_control": "L2 Station Control",
    "telecom": "L2 Telecom",
    "radio_network": "L1 Telecom",
    "interlocking": "L2 Interlocking",
    "train_detection": "L1 Interlocking",
    "point_control": "L0 Field",
    "signal_control": "L0 Field",
    "field": "L0 Field",
    "onboard": "Onboard",
}


# ============================================================
# INFER PURDUE
# ============================================================


def infer_purdue_level(asset_type: str, zone: str | None = None) -> str:
    """
    Infer Purdue level.

    Priority:
    1. Asset-specific mapping
    2. Zone-based fallback
    """

    asset_type = str(asset_type).lower()

    if zone:
        zone = str(zone).lower()

    # --------------------------------------------------------
    # ASSET MAPPING
    # --------------------------------------------------------

    allowed = VALID_PURDUE_BY_ASSET.get(asset_type, [])

    if allowed:
        return allowed[0]

    # --------------------------------------------------------
    # ZONE FALLBACK
    # --------------------------------------------------------

    if zone:

        return ZONE_TO_PURDUE.get(zone, "L0 Field")

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return "L3 Operations"


# ============================================================
# HELPERS
# ============================================================


def is_enterprise_level(level: str) -> bool:

    return level in {"L5 Enterprise", "L4 Business"}


def is_ot_level(level: str) -> bool:

    return level in {
        "L3.5 Security",
        "L3 Operations",
        "L2 Telecom",
        "L1 Telecom",
        "L2 Station Control",
        "L2 Interlocking",
        "L1 Interlocking",
        "L0 Field",
        "Onboard",
    }


def is_safety_level(level: str) -> bool:

    return level in {"L2 Interlocking", "L1 Interlocking", "L0 Field", "Onboard"}


def normalize_level(level: str) -> str:
    """
    Normalize aliases.
    """

    aliases = {
        "L4/L5": "L5 Enterprise",
        "L3.5 IDMZ": "L3.5 Security",
        "L2 Supervisory": "L2 Station Control",
        "L1 Sensing": "L1 Interlocking",
        "L0 Physical": "L0 Field",
        "Mobile OT": "Onboard",
        "Transport": "L2 Telecom",
        "Radio": "L1 Telecom",
        "External PKI": "External Security",
        "External kms_server": "External Security",
    }

    return aliases.get(level, level)
