from __future__ import annotations

import argparse
from pathlib import Path

from crawl_requests import crawl
from common import Settings, save_outputs, save_to_mysql, to_dataframe


def main() -> None:
    settings = Settings()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=[settings.keyword],
        help="여러 검색어를 공백으로 구분해 입력합니다. 예: --keywords 산업통상부 국토교통부 보건복지부",
    )
    parser.add_argument("--max-pages", type=int, default=settings.max_pages)
    parser.add_argument("--page-size", type=int, default=settings.page_size)
    parser.add_argument("--save-db", action="store_true")
    args = parser.parse_args()

    all_rows = []
    for keyword in args.keywords:
        print(f"[start] keyword={keyword}")
        rows = crawl(keyword=keyword, max_pages=args.max_pages, page_size=args.page_size)
        all_rows.extend(rows)
        print(f"[done] keyword={keyword}, rows={len(rows)}")

    df = to_dataframe(all_rows)
    print(df.head(20))
    print(f"total rows={len(df)}")

    if not df.empty:
        save_outputs(df, settings.output_dir, "multi")
        if args.save_db:
            save_to_mysql(df, settings)
            print("saved mysql")


if __name__ == "__main__":
    main()
