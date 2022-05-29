import pathlib

import requests

from . import utils
from .PickleFileCache import PickleFileCache


class CachedRequester:
    def __init__(self: "CachedRequester", cache_root: pathlib.Path) -> None:
        self.cache = PickleFileCache(cache_root=cache_root)
        pass

    def get(self: "CachedRequester", url: str) -> requests.Response:
        return self.cache.get(
            utils.normalized_http_url(url),
            lambda: requests.get(url),
        )

    def clear(
        self: "CachedRequester", url: str, missing_ok: bool = False
    ) -> None:
        self.cache.clear(url, missing_ok)
        pass

    pass
