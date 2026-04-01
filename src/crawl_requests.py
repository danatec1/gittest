from __future__ import annotations

import argparse
import time

import requests
from bs4 import BeautifulSoup

from common import BASE_SEARCH_URL, Settings, extract_items_from_text, deduplicate_rows, deduplicate_title_type, save_outputs, save_to_mysql, to_dataframe


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}


def fetch_page(keyword: str, page: int, page_size: int) -> str:
    data = {
        "keyword": keyword,
        "page": str(page),
        "pageSize": str(page_size),
    }
    response = requests.post(BASE_SEARCH_URL, headers=HEADERS, data=data, timeout=30)
    response.raise_for_status()
    return response.text


def crawl(keyword: str, max_pages: int, page_size: int) -> list[dict]:
    rows: list[dict] = []
    for page in range(1, max_pages + 1):
        html = fetch_page(keyword=keyword, page=page, page_size=page_size)
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text("\n")
        page_rows = extract_items_from_text(text, keyword=keyword, page_no=page)
        if not page_rows:
            break
        rows.extend(page_rows)
        time.sleep(0.5)

    rows = deduplicate_rows(rows)
    rows = deduplicate_title_type(rows)
    return rows


def main() -> None:
    settings = Settings()

    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", default=settings.keyword)
    parser.add_argument("--max-pages", type=int, default=settings.max_pages)
    parser.add_argument("--page-size", type=int, default=settings.page_size)
    parser.add_argument("--save-db", action="store_true")
    args = parser.parse_args()

    rows = crawl(keyword=args.keyword, max_pages=args.max_pages, page_size=args.page_size)
    df = to_dataframe(rows)

    print(df.head(20))
    print(f"rows={len(df)}")

    if not df.empty:
        csv_path, xlsx_path = save_outputs(df, settings.output_dir, args.keyword)
        print(f"saved csv: {csv_path}")
        print(f"saved xlsx: {xlsx_path}")
        if args.save_db:
            save_to_mysql(df, settings)
            print("saved mysql")


if __name__ == "__main__":
    main()
