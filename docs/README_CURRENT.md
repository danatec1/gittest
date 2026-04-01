# 현재 프로젝트 개요

이 문서는 현재 `gittest` 저장소의 실제 구조와 실행 흐름을 기준으로 정리한 최신 안내 문서입니다.

## 프로젝트 목적

공공데이터포털(data.go.kr)에서 특정 검색어로 검색된 결과 중

- 파일데이터
- 오픈API

목록의 다음 정보를 수집합니다.

- 제목
- 조회수
- 다운로드 수 또는 활용신청 수

수집 결과는 아래로 저장할 수 있습니다.

- CSV
- Excel
- MySQL
- 로그 파일
- 증감 비교 CSV

---

## 핵심 실행 파일

### 단일 검색어 수집
- `src/crawl_selenium.py`
- `src/crawl_selenium_logged.py`

### 다중 검색어 수집
- `src/run_multi_keywords.py`
- `src/run_multi_keywords_logged.py`

### 비교
- `src/compare_outputs.py`
- `src/auto_compare_latest.py`

### 공통 함수
- `src/common.py`
- `src/logger_utils.py`

### Windows 배치 실행
- `windows/run_crawl.bat`
- `windows/run_crawl_logged.bat`
- `windows/run_compare.bat`

---

## 추천 실행 방식

### 1. 일일 수집

```bash
python src/crawl_selenium_logged.py --keyword 산업통상부 --max-pages 30 --save-db
```

### 2. 다중 기관 수집

```bash
python src/run_multi_keywords_logged.py --keywords 산업통상부 국토교통부 보건복지부 --max-pages 20 --save-db
```

### 3. 최신 결과 자동 비교

```bash
python src/auto_compare_latest.py --output-dir output
```

---

## 출력 위치

### 수집 결과
- `output/*.csv`
- `output/*.xlsx`

### 로그
- `logs/*.log`

### 비교 결과
- `output/compare_result.csv`

---

## 현재 권장 운영 순서

1. `windows/run_crawl_logged.bat` 실행
2. `windows/run_compare.bat` 실행
3. 로그 확인
4. CSV/Excel 확인
5. MySQL 확인
6. compare_result.csv 확인

---

## 권장 다음 단계

- 저장소 이름 변경
- README.md를 이 문서 기준으로 재작성
- 작업 스케줄러 XML 템플릿 추가
- 결과 알림 기능 추가
