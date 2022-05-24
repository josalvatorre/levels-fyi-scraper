import base64
import pathlib
import pickle

import requests
import url_normalize


class ResponseCache:
    def __init__(self: "ResponseCache", cache_root: pathlib.Path) -> None:
        self.cache_root = cache_root
        pass

    def _cache_path(self: "ResponseCache", url: str) -> pathlib.Path:
        charset = "utf-8"
        normalized_url: str = url_normalize.url_normalize(url, charset)
        url_base64 = base64.urlsafe_b64encode(
            bytes(normalized_url, encoding=charset)
        )
        return pathlib.Path(
            self.cache_root,
            url_base64.decode(),
        )

    def get(self: "ResponseCache", url: str) -> requests.Response:
        cache_path = self._cache_path(url)
        if cache_path.exists():
            with open(cache_path, 'rb') as cache_file:
                print("returning from cache")
                return pickle.load(cache_file)

        print("making actual request")
        response = requests.get(url)
        with open(cache_path, 'wb') as cache_file:
            pickle.dump(response, cache_file)
        return response

    pass