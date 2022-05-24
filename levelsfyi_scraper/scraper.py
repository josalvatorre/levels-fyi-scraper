import itertools
import pathlib

from .ResponseCache import ResponseCache

cache_dir = pathlib.Path(pathlib.Path.cwd(), "cache_dir")
cache_dir.mkdir(exist_ok=True)

for _ in range(2):
    response = ResponseCache(cache_dir).get("https://www.levels.fyi/company/")
    text = response.text
    for line in itertools.islice(text, 0, 5):
        print(line)
    pass
