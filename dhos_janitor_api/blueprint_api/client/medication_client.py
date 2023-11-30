from typing import Dict, List, Optional

from cachetools import TTLCache, cached

from dhos_janitor_api import config
from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client.common import make_request

_config = config.Configuration()
_cache: TTLCache = TTLCache(1, _config.STATIC_DATA_CACHE_TTL_SEC)


@cached(cache=_cache)
def get_medications(
    clients: ClientRepository, medication_tag: Optional[str]
) -> List[Dict]:
    response = make_request(
        client=clients.gdm_bff,
        method="get",
        url="/gdm/v1/medication",
        headers={
            "Authorization": _config.POLARIS_API_KEY,
            "X-Trustomer": _config.CUSTOMER_CODE.lower(),
            "X-Product": "gdm",
        },
        params={"tag": medication_tag},
    )
    return [
        {k: m[k] for k in ("name", "sct_code", "unit", "uuid")} for m in response.json()
    ]
