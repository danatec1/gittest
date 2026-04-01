# scraping

공공데이터포털(data.go.kr)에서 특정 검색어(기본값: `산업통상부`)로 **파일데이터**와 **오픈API** 목록을 수집하고,
`제목`, `조회수`, `다운로드/활용신청 수`를 CSV, Excel, MySQL로 저장하는 예제 프로젝트입니다.

## 기능

- Selenium 기반 크롤링
- requests 기반 HTML 수집 보조 스크립트
- CSV / Excel 저장
- MySQL 적재
- Windows 작업 스케줄러 배치 파일 예제
- `.env` 기반 설정

## 수집 컬럼

- `data_type`: 파일데이터 / 오픈API
- `title`: 제목
- `view_count`: 조회수
- `metric_name`: 다운로드 / 활용신청
- `metric_value`: 다운로드 수 또는 활용신청 수
- `keyword`: 검색어
- `page_no`: 수집 페이지
- `collected_at`: 수집 시각

## 설치

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 실행

### 1) Selenium 버전

```bash
python src/crawl_selenium.py --keyword 산업통상부 --max-pages 30 --save-db
```

### 2) requests 버전

```bash
python src/crawl_requests.py --keyword 산업통상부 --max-pages 30
```

## `.env` 예시

루트에 `.env` 파일을 만들어 아래처럼 설정합니다.

```env
KEYWORD=산업통상부
MAX_PAGES=30
PAGE_SIZE=10
HEADLESS=true
OUTPUT_DIR=output

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=1234
MYSQL_DB=mydb
MYSQL_TABLE=data_go_dataset_stats
```

## MySQL 테이블 생성

```sql
SOURCE sql/create_table.sql;
```

또는 내용을 복사해서 직접 실행합니다.

## Windows 작업 스케줄러

`windows/run_crawl.bat`를 작업 스케줄러에 등록하면 매일 자동 수집할 수 있습니다.

예시:
- 프로그램: `C:\path\to\scraping\windows\run_crawl.bat`
- 트리거: 매일 오전 8시

## 주의

- 공공 사이트 구조가 바뀌면 선택자와 파서 로직을 수정해야 할 수 있습니다.
- 수집 전 사이트의 이용약관, robots 정책, 호출 빈도를 확인하세요.
- 오픈API 목록은 `다운로드`가 아닌 `활용신청` 지표가 노출될 수 있으므로 `metric_name`과 `metric_value`로 저장합니다.

## 프로젝트 구조

```text
scraping/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ sql/
│  └─ create_table.sql
├─ windows/
│  └─ run_crawl.bat
└─ src/
   ├─ common.py
   ├─ crawl_selenium.py
   ├─ crawl_requests.py
   └─ fetch_console_example.js
```
