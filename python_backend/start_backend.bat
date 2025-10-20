@echo off
echo Starting Python FastAPI Backend...
cd /d "%~dp0"
uvicorn setup:app --reload --port 8000

