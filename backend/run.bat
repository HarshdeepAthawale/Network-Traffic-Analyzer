@echo off
REM Simple startup script for the backend on Windows

echo Starting Network Traffic Analyzer Backend...

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the backend
python main.py
