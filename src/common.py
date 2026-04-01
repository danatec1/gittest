from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

BASE_SEARCH_URL = "https://www.data.go.kr/tcs/dss/selectDataSetList.do"
DEFAULT_PAGE_URL = (
    "https://www.data.go.kr/tcs/dss/selectDataSetList.do?"
    "keyword=%EC%82%B0%EC%97%85%ED%86%B5%EC%83%81%EB%B6%80&brm=&svcType=&recmSe=N&conditionType=init&extsn=&kwrdArray="
)


@dataclass
class Settings:
    keyword: str = os.getenv("KEYWORD", "산업통상부")
    max_pages: int = int(os.getenv("MAX_PAGES", "30"))
    page_size: int = int(os.getenv("PAGE_SIZE", "10"))
    headless: bool = os.getenv("HEADLESS", "true").lower() == "true"
    output_dir: str = os.getenv("OUTPUT_DIR", "output")
    mysql_host: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "1234")
    mysql_db: str = os.getenv("MYSQL_DB", "mydb")
    mysql_table: str = os.getenv("MYSQL_TABLE", "data_go_dataset_stats")


def parse_number(text: str | None) -> int | None:
    if not text:
        return None
    match = re.search(r"(\d[\d,]*)", text.replace("\n", " "))
    return int(match.group(1).replace(",", "")) if match else None


def clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def is_noise_line(line: str) -> bool:
    noise_keywords = [
        "조회수", "다운로드", "활용신청", "수정일", "제공기관", "키워드",
        "미리보기", "바로가기", "JSON", "XML", "LINK", "목록", "검색", "페이지",
    ]
    return any(keyword in line for keyword in noise_keywords)


def looks_like_title(line: str) -> bool:
    return len(line) >= 4 and not is_noise_line(line)


def extract_items_from_text(body_text: str, keyword: str, page_no: int) -> list[dict]:
    lines = clean_lines(body_text)
    rows: list[dict] = []

    for i, line in enumerate(lines):
        if not looks_like_title(line):
            continue

        title = line
        view_count = None
        metric_name = None
        metric_value = None

        for j in range(i + 1, min(i + 16, len(lines))):
            current = lines[j]
            if "조회수" in current:
                view_count = parse_number(current)
            if "다운로드" in current:
                metric_name = "다운로드"
                metric_value = parse_number(current)
            if "활용신청" in current:
                metric_name = "활용신청"
                metric_value = parse_number(current)

            if view_count is not None and metric_name is not None and metric_value is not None:
                data_type = "파일데이터" if metric_name == "다운로드" else "오픈API"
                rows.append(
                    {
                        "data_type": data_type,
                        "title": title,
                        "view_count": view_count,
                        "metric_name": metric_name,
                        "metric_value": metric_value,
                        "keyword": keyword,
                        "page_no": page_no,
                    }
                )
                break

    return deduplicate_rows(rows)


def deduplicate_rows(rows: Iterable[dict]) -> list[dict]:
    deduped: list[dict] = []
    seen: set[tuple] = set()
    for row in rows:
        key = (
            row.get("data_type"),
            row.get("title"),
            row.get("view_count"),
            row.get("metric_name"),
            row.get("metric_value"),
            row.get("page_no"),
        )
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped


def deduplicate_title_type(rows: Iterable[dict]) -> list[dict]:
    result: list[dict] = []
    seen: set[tuple] = set()
    for row in rows:
        key = (row.get("data_type"), row.get("title"))
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for row in rows:
        row["collected_at"] = collected_at

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    ordered_cols = [
        "data_type", "title", "view_count", "metric_name", "metric_value",
        "keyword", "page_no", "collected_at",
    ]
    return df[ordered_cols].sort_values(by=["data_type", "title"]).reset_index(drop=True)


def ensure_output_dir(output_dir: str) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_outputs(df: pd.DataFrame, output_dir: str, keyword: str) -> tuple[Path, Path]:
    out_dir = ensure_output_dir(output_dir)
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"data_go_{keyword}_{now_str}.csv"
    xlsx_path = out_dir / f"data_go_{keyword}_{now_str}.xlsx"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)
    return csv_path, xlsx_path


def save_to_mysql(df: pd.DataFrame, settings: Settings) -> None:
    if df.empty:
        return

    engine = create_engine(
        f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}"
        f"@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_db}?charset=utf8mb4"
    )
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {settings.mysql_table} (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        data_type VARCHAR(50),
        title VARCHAR(1000),
        view_count INT,
        metric_name VARCHAR(50),
        metric_value INT,
        keyword VARCHAR(255),
        page_no INT,
        collected_at DATETIME,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_data_go_dataset (data_type, title, collected_at)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))

    df2 = df.copy()
    df2["collected_at"] = pd.to_datetime(df2["collected_at"])
    df2.to_sql(
        name=settings.mysql_table,
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=200,
    )
