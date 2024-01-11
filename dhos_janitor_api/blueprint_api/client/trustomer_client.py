from typing import Dict

from cachetools import TTLCache, cached
from she_logging import logger

from dhos_janitor_api import config
from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client.common import make_request

_config = config.Configuration()
_cache: TTLCache = TTLCache(1, _config.STATIC_DATA_CACHE_TTL_SEC)


@cached(cache=_cache)
def get_trustomer_config(clients: ClientRepository, system_jwt: str) -> Dict:
    url = f"/gdm/v1/trustomer/{_config.CUSTOMER_CODE.lower()}"
    logger.info("Fetching trustomer config from %s", url)
    response = make_request(
        client=clients.gdm_bff,
        method="get",
        url=url,
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()
