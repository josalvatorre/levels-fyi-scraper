# Levels FYI Web Scraper

It runs through all [`levels fyi`](https://www.levels.fyi/) company pages and sorts by
sub-senior (eg entry, mid) total compensation.

## Running

I recommend running inside of a tmux session. The scraper takes a long time to run the first time.
However, it progressively caches webpages, so it runs fast the following times.

```python
cd path/to/levels-fyi-scraper
pip3 install -r requirements.txt
python3 -m levelsfyi_scraper.scraper
```

Results are in `company_salary_rows_ascending.txt` and `company_salary_rows_descending.txt`.

## Caveats

Most company pages on levels fyi don't have enough data points to show salary statistics.
For example: at time of writing, [Coda](https://www.levels.fyi/company/Coda/salaries/Software-Engineer/)
doesn't have enough data for Levels FYI to visualize salary row bars like it does for
[`Google`](https://www.levels.fyi/company/Coda/salaries/Software-Engineer/). That means that this
scraper will ignore most companies, which are quite small.

I sort by sub-senior total compensation because I am a mid-level engineer. Results vary when
sorting by different levels.
