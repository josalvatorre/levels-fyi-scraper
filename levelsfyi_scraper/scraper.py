import pathlib

import bs4

from .ResponseCache import ResponseCache

cache_dir = pathlib.Path(pathlib.Path.cwd(), "cache_dir")
cache_dir.mkdir(exist_ok=True)

for _ in range(2):
    response = ResponseCache(cache_dir).get("https://www.levels.fyi/company/")
    data = bs4.BeautifulSoup(response.text, "html.parser")
    print(len(data.body))
    pass
