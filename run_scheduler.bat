@echo off
echo Starting AI Study Scheduler...
python main.py
if errorlevel 1 (
    echo An error occurred while running the application.
    echo Please check the error message above.
    pause
)