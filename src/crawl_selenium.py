from __future__ import annotations

import argparse
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from common import Settings, DEFAULT_PAGE_URL, extract_items_from_text, deduplicate_rows, deduplicate_title_type, save_outputs, save_to_mysql, to_dataframe


def create_driver(headless: bool) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,3000")
    options.add_argument("--lang=ko-KR")
    return webdriver.Chrome(options=options)


def go_to_next_page(driver: webdriver.Chrome, target_page: int) -> bool:
    try:
        link = driver.find_element(By.LINK_TEXT, str(target_page))
        driver.execute_script("arguments[0].click();", link)
        time.sleep(2)
        return True
    except Exception:
        return False


def crawl(keyword: str, max_pages: int, headless: bool) -> list[dict]:
    driver = create_driver(headless=headless)
    try:
        driver.get(DEFAULT_PAGE_URL)
        time.sleep(3)

        rows: list[dict] = []

        body_text = driver.find_element(By.TAG_NAME, "body").text
        rows.extend(extract_items_from_text(body_text, keyword=keyword, page_no=1))

        for page in range(2, max_pages + 1):
            if not go_to_next_page(driver, page):
                break
            body_text = driver.find_element(By.TAG_NAME, "body").text
            page_rows = extract_items_from_text(body_text, keyword=keyword, page_no=page)
            if not page_rows:
                break
            rows.extend(page_rows)

        rows = deduplicate_rows(rows)
        rows = deduplicate_title_type(rows)
        return rows
    finally:
        driver.quit()


def main() -> None:
    settings = Settings()

    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", default=settings.keyword)
    parser.add_argument("--max-pages", type=int, default=settings.max_pages)
    parser.add_argument("--save-db", action="store_true")
    parser.add_argument("--headless", default=str(settings.headless).lower())
    args = parser.parse_args()

    headless = str(args.headless).lower() == "true"
    rows = crawl(keyword=args.keyword, max_pages=args.max_pages, headless=headless)
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
