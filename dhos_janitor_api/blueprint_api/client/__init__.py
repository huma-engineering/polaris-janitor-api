from dataclasses import dataclass

import httpx
from flask import Flask


@dataclass(frozen=True)
class ClientRepository:
    dhos_activation_auth_api: httpx.Client
    dhos_audit_api: httpx.Client
    dhos_locations_api: httpx.Client
    dhos_medications_api: httpx.Client
    dhos_messages_api: httpx.Client
    dhos_questions_api: httpx.Client
    dhos_services_api: httpx.Client
    dhos_users_api: httpx.Client
    dhos_telemetry_api: httpx.Client
    dhos_trustomer_api: httpx.Client
    dhos_url_api: httpx.Client
    gdm_articles_api: httpx.Client
    gdm_bg_readings_api: httpx.Client
    gdm_bff: httpx.Client

    @classmethod
    def from_app(cls, app: Flask) -> "ClientRepository":
        return cls(
            **{
                k: httpx.Client(base_url=app.config[v])
                for k, v in app.config["ALL_TARGETS"].items()
            }
        )
