@echo off
setlocal
cd /d %~dp0\..

if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe src\crawl_selenium_logged.py --save-db
) else (
  python src\crawl_selenium_logged.py --save-db
)

endlocal
