"""
infer_communication_stack.py
FINAL HARDENED COMMUNICATION STACK INFERENCE
IEC62443 + EN50159 + Railway OT + Kavach
Purpose:
- infer transport layer
- infer bearer layer
- infer media layer
- infer open transmission semantics
- infer wireless semantics
- infer EN50159 communication exposure
DOES NOT:
- validate
- enforce policy
- infer security controls
- infer safety policy
- modify topology structure
"""

from ontology import (
    DEFAULT_CONNECTION_STACK,
    PROTOCOL_TRANSPORT_MAP,
    TRANSPORT_MEDIA_MAP,
    BEARER_TRANSPORT_MAP,
    UNKNOWN_PROTOCOL,
    UNKNOWN_TRANSPORT,
    UNKNOWN_MEDIA,
    UNKNOWN_BEARER,
    protocol_is_wireless_capable,
    transport_is_wireless,
    transport_is_public_network,
    transport_is_latency_sensitive,
    transport_has_high_jamming_risk,
    media_is_open_transmission,
    media_is_public_network,
    bearer_is_wireless,
    bearer_is_railway_radio,
)
from aliases import (
    normalize_protocol,
)


# ============================================================
# HELPERS
# ============================================================
def set_if_missing(
    conn: dict,
    field: str,
    value,
):
    if field not in conn or conn[field] in (
        None,
        "",
        UNKNOWN_TRANSPORT,
        UNKNOWN_PROTOCOL,
        UNKNOWN_MEDIA,
        UNKNOWN_BEARER,
    ):
        conn[field] = value
        conn["stack_inferred"] = True


def append_inference_source(
    conn: dict,
    source: str,
):
    conn.setdefault(
        "stack_inference_sources",
        [],
    )
    if source not in conn["stack_inference_sources"]:
        conn["stack_inference_sources"].append(source)


# ============================================================
# MAIN STACK INFERENCE
# ============================================================
def infer_communication_stack(
    topology: dict,
) -> dict:
    for conn in topology.get(
        "connections",
        [],
    ):
        conn.setdefault(
            "stack_inferred",
            False,
        )
        conn.setdefault(
            "stack_inference_sources",
            [],
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
        conn["protocol"] = protocol
        # ====================================================
        # UNKNOWN PROTOCOL
        # ====================================================
        if protocol == UNKNOWN_PROTOCOL:
            continue
        # ====================================================
        # DEFAULT STACK
        # ====================================================
        stack = DEFAULT_CONNECTION_STACK.get(
            protocol,
            {},
        )
        # ====================================================
        # TRANSPORT
        # ====================================================
        previous_transport = conn.get("transport")
        set_if_missing(
            conn,
            "transport",
            stack.get(
                "transport",
                UNKNOWN_TRANSPORT,
            ),
        )
        if previous_transport != conn.get("transport"):
            conn.setdefault(
                "transport_source",
                "default_connection_stack",
            )
            append_inference_source(
                conn,
                "default_connection_stack",
            )
        # ====================================================
        # BEARER
        # ====================================================
        previous_bearer = conn.get("bearer")
        set_if_missing(
            conn,
            "bearer",
            stack.get(
                "bearer",
                UNKNOWN_BEARER,
            ),
        )
        if previous_bearer != conn.get("bearer"):
            conn.setdefault(
                "bearer_source",
                "default_connection_stack",
            )
            append_inference_source(
                conn,
                "default_connection_stack",
            )
        # ====================================================
        # MEDIA
        # ====================================================
        previous_media = conn.get("media")
        set_if_missing(
            conn,
            "media",
            stack.get(
                "media",
                UNKNOWN_MEDIA,
            ),
        )
        if previous_media != conn.get("media"):
            conn.setdefault(
                "media_source",
                "default_connection_stack",
            )
            append_inference_source(
                conn,
                "default_connection_stack",
            )
        # ====================================================
        # TRANSPORT INFERENCE
        # ====================================================
        transport = conn.get(
            "transport",
            UNKNOWN_TRANSPORT,
        )
        if transport == UNKNOWN_TRANSPORT:
            allowed_transports = sorted(
                PROTOCOL_TRANSPORT_MAP.get(
                    protocol,
                    [],
                )
            )
            if allowed_transports:
                transport = allowed_transports[0]
                conn["transport"] = transport
                conn.setdefault(
                    "transport_source",
                    "protocol_transport_map",
                )
                conn["stack_inferred"] = True
                append_inference_source(
                    conn,
                    "protocol_transport_map",
                )
        # ====================================================
        # MEDIA INFERENCE
        # ====================================================
        media = conn.get(
            "media",
            UNKNOWN_MEDIA,
        )
        if media == UNKNOWN_MEDIA:
            allowed_media = sorted(
                TRANSPORT_MEDIA_MAP.get(
                    transport,
                    [],
                )
            )
            if allowed_media:
                media = allowed_media[0]
                conn["media"] = media
                conn.setdefault(
                    "media_source",
                    "transport_media_map",
                )
                conn["stack_inferred"] = True
                append_inference_source(
                    conn,
                    "transport_media_map",
                )
        # ====================================================
        # BEARER INFERENCE
        # ====================================================
        bearer = conn.get(
            "bearer",
            UNKNOWN_BEARER,
        )
        if bearer == UNKNOWN_BEARER:
            for candidate_bearer in sorted(BEARER_TRANSPORT_MAP.keys()):
                transports = BEARER_TRANSPORT_MAP[candidate_bearer]
                if transport in transports:
                    bearer = candidate_bearer
                    conn["bearer"] = bearer
                    conn.setdefault(
                        "bearer_source",
                        "bearer_transport_map",
                    )
                    conn["stack_inferred"] = True
                    append_inference_source(
                        conn,
                        "bearer_transport_map",
                    )
                    break
        # ====================================================
        # DETACHED CONDUITS
        # ====================================================
        detached_conduit = conn.get(
            "detached_conduit",
            False,
        )
        # ====================================================
        # TRANSPORT SEMANTICS
        # ====================================================
        if transport_is_wireless(transport):
            conn.setdefault(
                "wireless",
                True,
            )
            conn.setdefault(
                "wireless_source",
                "transport_ontology",
            )
        if transport_is_public_network(transport) and not detached_conduit:
            conn.setdefault(
                "public_network",
                True,
            )
            conn.setdefault(
                "public_network_source",
                "transport_ontology",
            )
        if transport_is_latency_sensitive(transport):
            conn.setdefault(
                "latency_sensitive",
                True,
            )
            conn.setdefault(
                "latency_sensitive_source",
                "transport_ontology",
            )
        if transport_has_high_jamming_risk(transport) and not detached_conduit:
            conn.setdefault(
                "high_jamming_risk",
                True,
            )
            conn.setdefault(
                "high_jamming_risk_source",
                "transport_ontology",
            )
        # ====================================================
        # MEDIA SEMANTICS
        # ====================================================
        if media_is_open_transmission(media) and not detached_conduit:
            conn.setdefault(
                "open_transmission",
                True,
            )
            conn.setdefault(
                "open_transmission_source",
                "media_ontology",
            )
        if media_is_public_network(media) and not detached_conduit:
            conn.setdefault(
                "public_network",
                True,
            )
            conn.setdefault(
                "public_network_source",
                "media_ontology",
            )
        # ====================================================
        # BEARER SEMANTICS
        # ====================================================
        if bearer_is_wireless(bearer):
            conn.setdefault(
                "wireless",
                True,
            )
            conn.setdefault(
                "wireless_source",
                "bearer_ontology",
            )
        if bearer_is_railway_radio(bearer):
            conn.setdefault(
                "railway_radio",
                True,
            )
            conn.setdefault(
                "railway_radio_source",
                "bearer_ontology",
            )
        # ====================================================
        # RADIO RELATED
        # ====================================================
        if (
            conn.get(
                "wireless",
                False,
            )
            or conn.get(
                "railway_radio",
                False,
            )
            or protocol_is_wireless_capable(protocol)
        ):
            conn.setdefault(
                "radio_related",
                True,
            )
            conn.setdefault(
                "radio_related_source",
                "stack_inference",
            )
        # ====================================================
        # EN50159 COMMUNICATION EXPOSURE
        # ====================================================
        if conn.get(
            "open_transmission",
            False,
        ):
            conn["communication_system_type"] = "open"
        else:
            conn["communication_system_type"] = "closed"
        conn.setdefault(
            "communication_system_type_source",
            "en50159_inference",
        )
        # ====================================================
        # DEBUG
        # ====================================================
        print(
            f"[STACK] "
            f"{conn.get('source')} -> "
            f"{conn.get('target')} | "
            f"PROTO={protocol} | "
            f"TRANSPORT={conn.get('transport')} | "
            f"BEARER={conn.get('bearer')} | "
            f"MEDIA={conn.get('media')} | "
            f"OPEN={conn.get('open_transmission', False)} | "
            f"DETACHED={detached_conduit}"
        )
    return topology
