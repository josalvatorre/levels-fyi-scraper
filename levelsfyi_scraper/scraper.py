import pathlib
import urllib
from typing import Iterable, NamedTuple, Optional

import bs4

from . import utils
from .CachedRequester import CachedRequester

HTML_PARSER = "html.parser"
ROOT_URL = "https://www.levels.fyi"
COMPANY_DIRECTORY_URL = urllib.parse.urljoin(ROOT_URL, "company")

cache_dir = pathlib.Path(pathlib.Path.cwd(), "cache_dir")
cache_dir.mkdir(exist_ok=True)
cached_requester = CachedRequester(cache_dir)

company_directory = bs4.BeautifulSoup(
    cached_requester.get(COMPANY_DIRECTORY_URL).text,
    HTML_PARSER,
)
swe_urls = sorted(
    urllib.parse.urljoin(
        urllib.parse.urljoin(ROOT_URL, co.a.attrs["href"]),
        "Software-Engineer",
    )
    for co in company_directory.select(".company-outline-container")
)


class LevelSalary(NamedTuple):
    level_name: str
    title: Optional[str]
    layman_title: Optional[str]
    total: int
    base: int
    stock: int
    bonus: int
    pass


def salary_rows(swe_salary_page: bs4.BeautifulSoup) -> Iterable[LevelSalary]:
    def to_dollars(text: str) -> int:
        if text == "N/A":
            return 0
        text = text.strip()

        denomination: int
        if text[-1] == "K":
            denomination = 1_000
        elif text[-1] == "M":
            denomination = 1_000_000
        else:
            raise Exception("unrecognized denomination")

        text = text.lstrip("$").rstrip("KM")
        return int(text) * denomination

    def to_level_salary(row: bs4.Tag) -> LevelSalary:
        level_cell, total_cell, base_cell, stock_cell, bonus_cell = tuple(
            row.children,
        )
        level_name, title, layman_title = tuple(
            None if child is None else child.text
            for child in utils.take_first(
                utils.trail(level_cell.children),
                3,
            )
        )
        total, base, stock, bonus = tuple(
            to_dollars(next(cell.children).text)
            for cell in (total_cell, base_cell, stock_cell, bonus_cell)
        )
        return LevelSalary(
            level_name=level_name,
            title=title,
            layman_title=layman_title,
            total=total,
            base=base,
            stock=stock,
            bonus=bonus,
        )

    rows = swe_salary_page.select(".level-salary-row")
    return map(to_level_salary, rows)


company_salary_rows = [
    rows
    for salary_url in swe_urls
    if (
        rows := utils.if_error(
            lambda: tuple(
                salary_rows(
                    bs4.BeautifulSoup(
                        cached_requester.get(salary_url).text,
                        HTML_PARSER,
                    )
                )
            )
        )
    )
    is not None
]

with open("company_salary_rows.txt", "w") as csr_file:
    print(company_salary_rows, file=csr_file)
