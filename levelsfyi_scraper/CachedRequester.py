import base64
import pathlib
import pickle

import requests
import url_normalize


class CachedRequester:
    def __init__(self: "CachedRequester", cache_root: pathlib.Path) -> None:
        self.cache_root = cache_root
        pass

    def _cache_path(self: "CachedRequester", url: str) -> pathlib.Path:
        charset = "utf-8"
        # strangely, url_normalize does not remove trailing slashes
        normalized_url: str = url_normalize.url_normalize(
            url.rstrip("/"),
            charset,
        )
        url_base64 = base64.urlsafe_b64encode(
            bytes(normalized_url, encoding=charset)
        )
        return pathlib.Path(
            self.cache_root,
            url_base64.decode(),
        )

    def get(self: "CachedRequester", url: str) -> requests.Response:
        cache_path = self._cache_path(url)
        if cache_path.exists():
            with open(cache_path, "rb") as cache_file:
                print("returning from cache")
                return pickle.load(cache_file)

        print(f"making actual request to '{url}'")
        response = requests.get(url)
        with open(cache_path, "wb") as cache_file:
            pickle.dump(response, cache_file)
        return response

    pass
