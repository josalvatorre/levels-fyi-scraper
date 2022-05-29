import itertools
import json
import pathlib
import statistics
import urllib
from typing import (
    Iterable,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

import bs4

from . import utils
from .CachedRequester import CachedRequester
from .PickleFileCache import PickleFileCache

T = TypeVar("T")

HTML_PARSER = "html.parser"
ROOT_URL = "https://www.levels.fyi"
COMPANY_DIRECTORY_URL = urllib.parse.urljoin(ROOT_URL, "company")

cache_dir = pathlib.Path(pathlib.Path.cwd(), "cache_dir")
requests_cache_dir = pathlib.Path(cache_dir, "requests")
salary_levels_cache_dir = pathlib.Path(cache_dir, "salary-urls")

for dir_ in (requests_cache_dir, salary_levels_cache_dir):
    dir_.mkdir(exist_ok=True, parents=True)

cached_requester = CachedRequester(requests_cache_dir)
salary_levels_cache = PickleFileCache(salary_levels_cache_dir)

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

    def names(self: "LevelSalary") -> Tuple[str, ...]:
        return tuple(
            name
            for name in (self.level_name, self.title, self.layman_title)
            if name is not None
        )

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


def guess_entry_mid_mean_tc(salaries: Sequence[LevelSalary]) -> int:
    def index_with_substring_match(
        substrings: Sequence[str],
        default: T,
    ) -> Union[int, T]:
        return next(
            (
                i
                for i, level in enumerate(salaries)
                if any(
                    any(substr in desc for substr in substrings)
                    for desc in map(str.lower, level.names())
                )
            ),
            default,
        )

    if len(salaries) == 0:
        raise Exception("no salary rows given")
    elif len(salaries) == 1:
        # This surely indicates incomplete data. However, there's no way to
        # tell what level this is. We have to guess that it represents the mean
        # for all levels.
        return salaries[0].total

    entry_index = index_with_substring_match(("entry", "junior"), 0)
    senior_index = index_with_substring_match(
        ("senior",),
        min(2, len(salaries) - 1),
    )
    if entry_index == senior_index:
        # Apparently, there are companies where senior is entry level.
        return salaries[entry_index].total

    return statistics.mean(
        itertools.islice(
            (salary.total for salary in salaries),
            entry_index,
            senior_index,
        )
    )


def company_name_from_url(url: str) -> str:
    chunks = url.split("/")
    return chunks[chunks.index("company") + 1]


company_salary_rows = {
    company_name_from_url(salary_url): salary_levels_cache.get(
        company_name_from_url(salary_url),
        lambda: utils.if_error(
            lambda: tuple(
                salary_rows(
                    bs4.BeautifulSoup(
                        cached_requester.get(salary_url).text,
                        HTML_PARSER,
                    )
                )
            ),
            "error getting salary rows",
        ),
    )
    for salary_url in swe_urls
}
highest_pre_senior_companies = sorted(
    (
        (name, rows)
        for name, rows in company_salary_rows.items()
        if isinstance(rows, tuple) and 0 < len(rows)
    ),
    key=lambda pair: utils.if_error(
        lambda: guess_entry_mid_mean_tc(pair[1]),
        float("-inf"),
    ),
)

with open("company_salary_rows.txt", "w") as csr_file:
    print(
        json.dumps(
            highest_pre_senior_companies,
            sort_keys=True,
            indent=4,
            default=lambda salary_row: salary_row._asdict(),
        ),
        file=csr_file,
    )
