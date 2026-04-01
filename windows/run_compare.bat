@echo off
setlocal
cd /d %~dp0\..

if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe src\auto_compare_latest.py --output-dir output
) else (
  python src\auto_compare_latest.py --output-dir output
)

endlocal
