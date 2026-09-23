@echo off
echo Starting PS-27 Automatic Block Planning Backend (FastAPI + OR-Tools)...
cd backend
call .\venv\Scripts\activate
python -m uvicorn main:app --reload --port 8000
