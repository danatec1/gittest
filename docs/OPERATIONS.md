# 운영 가이드

이 문서는 `danatec1/gittest` 저장소를 Windows 환경에서 주기적으로 실행하고 결과를 비교하는 운영 절차를 정리한 문서입니다.

## 1. 준비

### 저장소 받기

```bash
git clone https://github.com/danatec1/gittest.git
cd gittest
```

### 가상환경 생성 및 패키지 설치

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 환경파일 생성

```bash
copy .env.example .env
```

필요하면 `.env` 파일에서 DB 정보와 기본 검색어를 수정합니다.

---

## 2. 수동 실행

### 2-1. 로그 포함 단일 검색어 수집

```bash
python src/crawl_selenium_logged.py --keyword 산업통상부 --max-pages 30 --save-db
```

### 2-2. 로그 포함 다중 검색어 수집

```bash
python src/run_multi_keywords_logged.py --keywords 산업통상부 국토교통부 보건복지부 --max-pages 20 --save-db
```

### 2-3. 최신 CSV 2개 비교

```bash
python src/auto_compare_latest.py --output-dir output
```

---

## 3. 배치 파일 실행

### 수집용

```bat
windows\run_crawl_logged.bat
```

### 비교용

```bat
windows\run_compare.bat
```

---

## 4. Windows 작업 스케줄러 등록

### 작업 1: 수집

- 이름: `data_go_crawl_logged`
- 프로그램: `C:\path\to\gittest\windows\run_crawl_logged.bat`
- 트리거: 매일 오전 8시

### 작업 2: 비교

- 이름: `data_go_compare`
- 프로그램: `C:\path\to\gittest\windows\run_compare.bat`
- 트리거: 매일 오전 8시 10분

권장 순서:
1. 08:00 수집 시작
2. 08:10 비교 시작

---

## 5. 결과 확인 위치

### 로그

```text
logs/
```

예:
- `logs/crawl_selenium_20260401_201500.log`
- `logs/run_multi_keywords_20260401_202000.log`

### 수집 결과

```text
output/
```

예:
- `data_go_산업통상부_20260401_080000.csv`
- `data_go_산업통상부_20260401_080000.xlsx`
- `data_go_multi_20260401_080500.csv`

### 비교 결과

- `output/compare_result.csv`

---

## 6. 점검 포인트

### 수집이 안 될 때

- Chrome 브라우저 설치 여부 확인
- Selenium 실행 가능 여부 확인
- 사이트 구조 변경 여부 확인
- 방화벽 또는 프록시 환경 확인

### DB 저장이 안 될 때

- `.env`의 MySQL 접속정보 확인
- MySQL 서버 실행 여부 확인
- DB와 테이블 생성 여부 확인

### 비교가 안 될 때

- `output` 폴더에 CSV가 최소 2개 이상 있는지 확인

---

## 7. 추천 운영 순서

1. 수동 실행으로 1회 테스트
2. 로그 파일 생성 확인
3. CSV/Excel 생성 확인
4. MySQL 저장 확인
5. 비교 스크립트 실행 확인
6. 작업 스케줄러 등록

---

## 8. 향후 개선 후보

- README 최신화
- 저장소 이름 변경 (`gittest` → `scraping` 등)
- 일자별 비교 리포트 파일명 개선
- 에러 발생 시 이메일 또는 메신저 알림 추가
- 다중 검색어 결과를 검색어별 파일로 분리 저장
