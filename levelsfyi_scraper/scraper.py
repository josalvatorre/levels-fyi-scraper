import pathlib
import urllib

import bs4

from .CachedRequester import CachedRequester

ROOT_URL = "https://www.levels.fyi"
COMPANY_DIRECTORY_URL = urllib.parse.urljoin(ROOT_URL, "company")

cache_dir = pathlib.Path(pathlib.Path.cwd(), "cache_dir")
cache_dir.mkdir(exist_ok=True)
cached_requester = CachedRequester(cache_dir)

company_directory = bs4.BeautifulSoup(
    cached_requester.get(COMPANY_DIRECTORY_URL).text,
    "html.parser",
)
company_urls = sorted(
    urllib.parse.urljoin(ROOT_URL, co.a.attrs["href"])
    for co in company_directory.select(".company-outline-container")
)
print(company_urls[:5])
