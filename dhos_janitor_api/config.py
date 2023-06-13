from __future__ import annotations

from typing import Dict, Generator, Optional, Set

from environs import Env
from flask import Flask


class Configuration:
    env = Env()
    DHOS_ACTIVATION_AUTH_API: str = env.str("DHOS_ACTIVATION_AUTH_API")
    DHOS_AUDIT_API: str = env.str("DHOS_AUDIT_API")
    DHOS_LOCATIONS_API: str = env.str("DHOS_LOCATIONS_API")
    DHOS_MEDICATIONS_API: str = env.str("DHOS_MEDICATIONS_API")
    DHOS_MESSAGES_API: str = env.str("DHOS_MESSAGES_API")
    DHOS_OBSERVATIONS_API: str = env.str("DHOS_OBSERVATIONS_API")
    DHOS_QUESTIONS_API: str = env.str("DHOS_QUESTIONS_API")
    DHOS_SERVICES_API: str = env.str("DHOS_SERVICES_API")
    DHOS_USERS_API: str = env.str("DHOS_USERS_API")
    DHOS_TELEMETRY_API: str = env.str("DHOS_TELEMETRY_API")
    DHOS_TRUSTOMER_API: str = env.str("DHOS_TRUSTOMER_API")
    DHOS_URL_API: str = env.str("DHOS_URL_API")
    GDM_ARTICLES_API: str = env.str("GDM_ARTICLES_API")
    GDM_BG_READINGS_API: str = env.str("GDM_BG_READINGS_API")
    GDM_BFF: str = env.str("GDM_BFF")

    HS_KEY: str = env.str("HS_KEY")
    PROXY_URL: str = env.str("PROXY_URL").rstrip("/") + "/"
    HS_ISSUER: str = PROXY_URL
    CUSTOMER_CODE: str = env.str("CUSTOMER_CODE")
    POLARIS_API_KEY: str = env.str("POLARIS_API_KEY")
    STATIC_DATA_CACHE_TTL_SEC: int = env.int(
        "STATIC_DATA_CACHE_TTL_SEC", 60 * 60  # Cache for 1 hour by default.
    )

    CLINICIAN_JWT_LIFETIME_SECONDS: int = env.int(
        "CLINICIAN_JWT_LIFETIME_SECONDS", 60 * 60
    )
    PATIENT_JWT_LIFETIME_SECONDS: int = env.int("PATIENT_JWT_LIFETIME_SECONDS", 60 * 60)
    SYSTEM_JWT_LIFETIME_SECONDS: int = env.int(
        "SYSTEM_JWT_LIFETIME_SECONDS", 60 * 60 * 24
    )
    JWT_TTL_COEFFICIENT: float = env.float("JWT_TTL_COEFFICIENT", 0.75)

    # ORDER IS IMPORTANT - determines order in which services are reset.
    RESETTABLE_TARGETS = {
        "dhos_locations_api": "DHOS_LOCATIONS_API",
        "dhos_users_api": "DHOS_USERS_API",
        "dhos_services_api": "DHOS_SERVICES_API",
        "dhos_activation_auth_api": "DHOS_ACTIVATION_AUTH_API",
        "dhos_audit_api": "DHOS_AUDIT_API",
        "dhos_messages_api": "DHOS_MESSAGES_API",
        "dhos_questions_api": "DHOS_QUESTIONS_API",
        "dhos_telemetry_api": "DHOS_TELEMETRY_API",
        "gdm_bg_readings_api": "GDM_BG_READINGS_API",
    }

    # Targets for API calls including those we don't want to reset.
    ALL_TARGETS = {
        "gdm_bff": "GDM_BFF",
        "dhos_medications_api": "DHOS_MEDICATIONS_API",
        "dhos_trustomer_api": "DHOS_TRUSTOMER_API",
        "dhos_url_api": "DHOS_URL_API",
        "gdm_articles_api": "GDM_ARTICLES_API",
        **RESETTABLE_TARGETS,
    }


def init_config(app: Flask) -> None:
    app.config.from_object(Configuration)


def resettable_targets(
    targets: Optional[Set[str]], trustomer_config: Dict
) -> Generator[str, None, None]:
    """Returns the resettable targets in the targets list in the correct order
    If targets is empty simply yields all resettable targets in order.
    """
    use_epr_integration: bool = trustomer_config["gdm_config"].get(
        "use_epr_integration", False
    )

    if targets:
        unknown_targets = targets - Configuration.RESETTABLE_TARGETS.keys()
        if unknown_targets:
            raise ValueError(f"Unknown microservices '{','.join(unknown_targets)}'")
        if not use_epr_integration and "dhos_fuego_api" in targets:
            raise ValueError(f"EPR integration is disabled, can't reset dhos-fuego-api")
    else:
        targets = set(Configuration.RESETTABLE_TARGETS.keys())
        if not use_epr_integration:
            targets.remove("dhos_fuego_api")

    for target in Configuration.RESETTABLE_TARGETS:
        if target in targets:
            yield target
