import base64
import pathlib
import pickle
from typing import Callable, TypeVar

T = TypeVar("T")


class PickleFileCache:
    def __init__(self: "PickleFileCache", cache_root: pathlib.Path) -> None:
        self.cache_root = cache_root
        pass

    def _cache_path(self: "PickleFileCache", key: str) -> pathlib.Path:
        charset = "utf-8"
        file_name = base64.urlsafe_b64encode(bytes(key, encoding=charset))
        return pathlib.Path(
            self.cache_root,
            file_name.decode(encoding=charset),
        )

    def get(self: "PickleFileCache", key: str, getter: Callable[[], T]) -> T:
        cache_path = self._cache_path(key)
        if cache_path.exists():
            with open(cache_path, "rb") as cache_file:
                print(f"cache hit for {key}")
                return pickle.load(cache_file)

        print(f"cache miss for '{key}'")
        value = getter()
        with open(cache_path, "wb") as cache_file:
            pickle.dump(value, cache_file)
        return value

    pass
