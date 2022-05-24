import pathlib

import bs4

from .ResponseCache import ResponseCache

cache_dir = pathlib.Path(pathlib.Path.cwd(), "cache_dir")
cache_dir.mkdir(exist_ok=True)

company_directory = bs4.BeautifulSoup(
    ResponseCache(cache_dir).get("https://www.levels.fyi/company/").text,
    "html.parser",
)
print(company_directory.prettify())
