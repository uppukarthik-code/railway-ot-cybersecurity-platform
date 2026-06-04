"""
security_enrichment.py

FINAL HARDENED SECURITY ENRICHMENT
IEC62443 + EN50159 + Railway OT + Kavach

DESIGN PRINCIPLES
-----------------
- ontology.py = semantic authority
- railway_rules.py = governance authority
- CONDUIT_POLICY_REQUIREMENTS = security policy authority

This module:
- infers deployable protocol capabilities
- enriches conduit semantics
- applies conduit security policy requirements
- applies trust-boundary requirements
- enriches explainability/provenance metadata

DOES NOT:
- validate
- classify
- enforce compliance
- mutate canonical normalized identity fields
"""

from ontology import (
    UNKNOWN_PROTOCOL,
    protocol_is_encrypted,
    protocol_is_authenticated,
    protocol_has_integrity,
    protocol_has_replay_protection,
    protocol_is_safety_related,
    get_protocol_ontology,
    CONDUIT_ONTOLOGY,
    CONDUIT_SECURITY_PROFILES,
)

from aliases import (
    normalize_node_type,
    normalize_protocol,
)

from railway_rules import (
    get_flow_rule,
    get_trust_boundary,
    get_transmission_category,
    is_monitoring_exempt,
    is_inspection_exempt,
    is_firewall_exempt,
    has_monitoring_infrastructure,
    is_monitored_zone,
)

# ============================================================
# CONSTANTS
# ============================================================

VALID_CONDUIT_CLASSES = frozenset(CONDUIT_ONTOLOGY.keys())

DEFAULT_CONDUIT_CLASS = "unclassified"

# ============================================================
# PROVENANCE
# ============================================================


def add_requirement_source(
    conn: dict,
    field: str,
    source: str,
):

    requirement_sources = conn.setdefault(
        "requirement_sources",
        {},
    )

    sources = requirement_sources.setdefault(
        field,
        [],
    )

    if source not in sources:

        sources.append(source)


# ============================================================
# CONTROL HELPERS
# ============================================================


def set_required_control(
    conn: dict,
    field: str,
    source: str,
):
    """
    Policy requirement metadata.

    DOES NOT imply capability exists.
    """

    required_field = f"requires_{field}"

    conn[required_field] = True

    add_requirement_source(
        conn,
        required_field,
        source,
    )


def set_default_control(
    conn: dict,
    field: str,
    value: bool,
    source: str,
):
    """
    Capability inference.

    ONLY enrich if absent or currently falsy (never downgrade an
    existing True). Every caller passes value=True, so this only ever
    promotes a default/False capability to True.
    NEVER overwrite operator-declared values.
    """

    if not conn.get(field):

        conn[field] = value

        conn.setdefault(
            f"{field}_source",
            source,
        )


# ============================================================
# FLOW RULE SEMANTICS
# ============================================================


def apply_flow_rule_semantics(
    conn: dict,
    rule: dict,
):

    if not rule:

        return

    # ========================================================
    # CONDUIT CLASS
    # ========================================================

    conn.setdefault(
        "conduit_class",
        rule.get(
            "conduit_class",
            DEFAULT_CONDUIT_CLASS,
        ),
    )

    # ========================================================
    # SAFETY FLOW
    # ========================================================

    if rule.get("safety_flow", False) or rule.get("safety_related", False):

        conn["safety_flow"] = True

        conn.setdefault(
            "safety_flow_source",
            "flow_rule",
        )

    # ========================================================
    # SAFETY RELATED
    # ========================================================

    if rule.get(
        "safety_related",
        False,
    ):

        conn["safety_related"] = True

        conn.setdefault(
            "safety_related_source",
            "flow_rule",
        )

    # ========================================================
    # OPEN TRANSMISSION
    # ========================================================

    if rule.get(
        "open_transmission",
        False,
    ):

        conn["open_transmission"] = True

        conn.setdefault(
            "open_transmission_source",
            "flow_rule",
        )

    # ========================================================
    # PASSIVE TELEGRAM
    # ========================================================

    if rule.get(
        "passive_telegram",
        False,
    ):

        conn["passive_telegram"] = True

        conn.setdefault(
            "passive_telegram_source",
            "flow_rule",
        )


# ============================================================
# CONDUIT POLICY APPLICATION
# ============================================================


def apply_conduit_policy(
    conn: dict,
    source_type: str,
    target_type: str,
):

    conduit_class = conn.get(
        "conduit_class",
        DEFAULT_CONDUIT_CLASS,
    )

    # ========================================================
    # CONDUIT CLASS VALIDATION
    # ========================================================

    if conduit_class not in VALID_CONDUIT_CLASSES:

        conn["conduit_class_warning"] = True

        conn["invalid_conduit_class"] = conduit_class

        conduit_class = DEFAULT_CONDUIT_CLASS

        conn["conduit_class"] = DEFAULT_CONDUIT_CLASS

    # ========================================================
    # POLICY
    # ========================================================

    policy = CONDUIT_SECURITY_PROFILES.get(
        conduit_class,
        {},
    )

    detached_conduit = conn.get(
        "detached_conduit",
        False,
    )

    # ========================================================
    # MONITORING
    # ========================================================

    if policy.get("requires_monitoring", False) and not detached_conduit:

        monitoring_exempt = is_monitoring_exempt(source_type) or is_monitoring_exempt(
            target_type
        )

        if not monitoring_exempt:

            set_required_control(
                conn,
                "monitoring",
                "conduit_policy",
            )

    # ========================================================
    # MFA
    # ========================================================

    if policy.get("requires_mfa", False):

        set_required_control(
            conn,
            "mfa",
            "conduit_policy",
        )

    # ========================================================
    # ENCRYPTION
    # ========================================================

    if policy.get("requires_encryption", False):

        set_required_control(
            conn,
            "encrypted",
            "conduit_policy",
        )

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    if policy.get("requires_authentication", False):

        set_required_control(
            conn,
            "authentication",
            "conduit_policy",
        )

    # ========================================================
    # INTEGRITY
    # ========================================================

    if policy.get("requires_integrity", False):

        set_required_control(
            conn,
            "integrity_protection",
            "conduit_policy",
        )

    # ========================================================
    # REPLAY PROTECTION
    # ========================================================

    if policy.get("requires_replay_protection", False) and not conn.get(
        "passive_telegram",
        False,
    ):

        set_required_control(
            conn,
            "replay_protection",
            "conduit_policy",
        )

    # ========================================================
    # FIREWALL
    # ========================================================

    if policy.get("requires_firewall", False) and not detached_conduit:

        set_required_control(
            conn,
            "firewall",
            "conduit_policy",
        )

    # ========================================================
    # INSPECTION
    # ========================================================

    if policy.get("requires_inspection", False) and not detached_conduit:

        set_required_control(
            conn,
            "inspection",
            "conduit_policy",
        )

    # ========================================================
    # LATENCY MONITORING
    # ========================================================

    if policy.get(
        "requires_latency_monitoring",
        False,
    ):

        set_required_control(
            conn,
            "latency_monitoring",
            "conduit_policy",
        )


# ============================================================
# MAIN ENRICHMENT
# ============================================================


def apply_security_controls(
    topology: dict,
) -> dict:

    node_lookup = {
        node["id"]: node
        for node in topology.get(
            "nodes",
            [],
        )
    }

    # Security-monitoring instrumentation present in this topology?
    # Monitoring coverage is only credited when real instrumentation
    # (SIEM / IDS / IPS / SOC) exists — never as a blanket waiver.
    monitoring_infra_present = has_monitoring_infrastructure(
        normalize_node_type(node.get("type", ""))
        for node in topology.get("nodes", [])
    )

    for conn in topology.get(
        "connections",
        [],
    ):

        # ====================================================
        # DEFAULT CAPABILITIES
        # ====================================================

        capability_defaults = {
            "encrypted": False,
            "authentication": False,
            "integrity_protection": False,
            "replay_protection": False,
            "monitoring": False,
            "firewall": False,
            "inspection": False,
            "latency_monitoring": False,
            "mfa": False,
            "safety_related": False,
            "safety_flow": False,
            "open_transmission": False,
            "passive_telegram": False,
            "trust_boundary": False,
            "flow_rule_exists": False,
        }

        for key, value in capability_defaults.items():

            conn.setdefault(
                key,
                value,
            )

        # ====================================================
        # DEFAULT REQUIREMENTS
        # ====================================================

        policy_defaults = {
            "requires_encrypted": False,
            "requires_authentication": False,
            "requires_integrity_protection": False,
            "requires_replay_protection": False,
            "requires_monitoring": False,
            "requires_firewall": False,
            "requires_inspection": False,
            "requires_latency_monitoring": False,
            "requires_mfa": False,
        }

        for key, value in policy_defaults.items():

            conn.setdefault(
                key,
                value,
            )

        # NOTE: conduit_class is intentionally NOT seeded here.
        # Seeding "unclassified" before the FLOW_RULES lookup
        # (below) blocked apply_flow_rule_semantics() from ever
        # applying the railway_rules classification. The class is
        # now resolved from FLOW_RULES first and only falls back
        # to the placeholder default in apply_conduit_policy().

        # ====================================================
        # NODE LOOKUP
        # ====================================================

        source = node_lookup.get(conn.get("source"))

        target = node_lookup.get(conn.get("target"))

        if not source or not target:

            continue

        # ====================================================
        # SOURCE / TARGET TYPES
        # ====================================================

        source_type = normalize_node_type(
            source.get(
                "type",
                "unknown",
            )
        )

        target_type = normalize_node_type(
            target.get(
                "type",
                "unknown",
            )
        )

        # ====================================================
        # DETACHED DOMAIN
        # ====================================================

        source_detached = bool(
            source.get(
                "detached_domain",
                False,
            )
        )

        target_detached = bool(
            target.get(
                "detached_domain",
                False,
            )
        )

        conn["detached_conduit"] = source_detached or target_detached

        # ====================================================
        # FLOW RULE
        # ====================================================

        rule = get_flow_rule(
            source_type,
            target_type,
        )

        conn["flow_rule_exists"] = bool(rule)

        if rule:

            conn["flow_rule_category"] = rule.get(
                "category",
                "unknown",
            )

            conn["flow_rule_source"] = "railway_rules"

        apply_flow_rule_semantics(
            conn,
            rule,
        )

        # ====================================================
        # PROTOCOL
        # ====================================================

        protocol = normalize_protocol(
            conn.get(
                "protocol",
                UNKNOWN_PROTOCOL,
            )
        )

        protocol_known = protocol != UNKNOWN_PROTOCOL

        conn["protocol_known"] = protocol_known

        # ====================================================
        # PROTOCOL METADATA
        # ====================================================

        protocol_meta = {}

        if protocol_known:

            protocol_meta = get_protocol_ontology(
                protocol,
            )

            conn["protocol_metadata_source"] = "ontology"

        else:

            conn["protocol_unknown"] = True

        # ====================================================
        # PASSIVE TELEGRAM
        # ====================================================

        if protocol_meta.get(
            "passive_telegram_system",
            False,
        ):

            conn["passive_telegram"] = True

            conn.setdefault(
                "passive_telegram_source",
                "protocol_ontology",
            )

        # ====================================================
        # PROTOCOL CAPABILITIES
        # ====================================================

        if protocol_known:

            if protocol_is_encrypted(protocol):

                set_default_control(
                    conn,
                    "encrypted",
                    True,
                    "protocol_ontology",
                )

            if protocol_is_authenticated(protocol):

                set_default_control(
                    conn,
                    "authentication",
                    True,
                    "protocol_ontology",
                )

            if protocol_has_integrity(protocol):

                set_default_control(
                    conn,
                    "integrity_protection",
                    True,
                    "protocol_ontology",
                )

            if protocol_has_replay_protection(protocol):

                set_default_control(
                    conn,
                    "replay_protection",
                    True,
                    "protocol_ontology",
                )

        # ====================================================
        # SAFETY SEMANTICS
        # ====================================================

        if protocol_known and protocol_is_safety_related(protocol):

            set_default_control(
                conn,
                "safety_related",
                True,
                "protocol_ontology",
            )

            conn["safety_flow"] = True

            conn.setdefault(
                "safety_flow_source",
                "protocol_ontology",
            )

        elif conn.get(
            "safety_related",
            False,
        ):

            conn["safety_flow"] = True

        # ====================================================
        # EN 50159 CATEGORY-1 SAFETY-LAYER CREDIT
        #
        # For a closed trusted transmission (Category 1) over a protocol
        # whose safety layer provides functional integrity (safety code
        # + sequence numbers), EN 50159 is satisfied for INTEGRITY and
        # REPLAY by the safety layer. Cryptographic AUTHENTICATION and
        # ENCRYPTION are deliberately NOT credited and remain required
        # wherever the conduit profile demands them.
        # ====================================================

        if (
            protocol_known
            and get_transmission_category(rule) == 1
            and protocol_meta.get("functional_integrity", False)
        ):

            set_default_control(
                conn,
                "integrity_protection",
                True,
                "en50159_cat1_safety_layer",
            )

            set_default_control(
                conn,
                "replay_protection",
                True,
                "en50159_cat1_safety_layer",
            )

            conn.setdefault(
                "en50159_safety_layer_credited",
                True,
            )

        # ====================================================
        # EN 50159 PASSIVE SAFETY-TELEGRAM INTEGRITY CREDIT
        #
        # A passive safety telegram (e.g. EUROBALISE / RFID_AIR balise)
        # is statically safety-coded; its functional integrity is
        # provided by the telegram safety code regardless of the open
        # air-gap. This credits INTEGRITY only — NOT authentication,
        # encryption or replay (a passive one-way telegram has no
        # session to authenticate or replay-protect).
        # ====================================================

        if (
            protocol_known
            and protocol_meta.get("passive_telegram_system", False)
            and protocol_meta.get("functional_integrity", False)
        ):

            set_default_control(
                conn,
                "integrity_protection",
                True,
                "en50159_passive_telegram",
            )

            conn.setdefault(
                "en50159_safety_layer_credited",
                True,
            )

        # ====================================================
        # TRUST BOUNDARY
        # ====================================================

        source_zone = source.get(
            "zone",
            "unknown",
        )

        target_zone = target.get(
            "zone",
            "unknown",
        )

        # ====================================================
        # SECURITY-MONITORING COVERAGE (topology fidelity)
        #
        # Where deployed monitoring instrumentation (SIEM/IDS/IPS/SOC)
        # exists and a conduit endpoint sits in a SOC-instrumented zone,
        # the conduit IS monitored by that instrumentation. This models
        # real coverage so the deployed `monitoring` control is asserted
        # truthfully; it is gated on instrumentation presence and is not
        # an exemption (remove the instrumentation and the credit is
        # withdrawn).
        # ====================================================

        if monitoring_infra_present and (
            is_monitored_zone(source_zone) or is_monitored_zone(target_zone)
        ):

            set_default_control(
                conn,
                "monitoring",
                True,
                "soc_monitoring_coverage",
            )

        boundary = get_trust_boundary(
            source_zone,
            target_zone,
        )

        if boundary:

            conn["trust_boundary"] = True

            conn["trust_boundary_type"] = boundary.get(
                "boundary_type",
                "unknown",
            )

            conn["trust_boundary_source"] = "railway_rules"

        # ====================================================
        # CONDUIT POLICY
        # ====================================================

        apply_conduit_policy(
            conn,
            source_type,
            target_type,
        )

        # ====================================================
        # TRUST BOUNDARY REQUIREMENTS
        # ====================================================

        if boundary:

            conduit_class = conn.get(
                "conduit_class",
                DEFAULT_CONDUIT_CLASS,
            )

            # ------------------------------------------------
            # FIREWALL
            # ------------------------------------------------

            firewall_exempt = is_firewall_exempt(
                conduit_class,
            )

            if (
                boundary.get(
                    "firewall_required",
                    False,
                )
                and not firewall_exempt
                and not conn.get(
                    "detached_conduit",
                    False,
                )
            ):

                set_required_control(
                    conn,
                    "firewall",
                    "trust_boundary",
                )

            # ------------------------------------------------
            # INSPECTION
            # ------------------------------------------------

            inspection_exempt = is_inspection_exempt(
                conduit_class,
            )

            if (
                boundary.get(
                    "inspection_required",
                    False,
                )
                and not inspection_exempt
                and not conn.get(
                    "detached_conduit",
                    False,
                )
            ):

                set_required_control(
                    conn,
                    "inspection",
                    "trust_boundary",
                )

    return topology
