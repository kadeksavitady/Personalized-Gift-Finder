@echo off
echo Menjalankan DnD Bouquett...
start cmd /k "cd /d %~dp0backend && ..\venv\Scripts\activate && uvicorn main:app --reload"
timeout /t 5
start cmd /k "cd /d %~dp0frontend && ..\venv\Scripts\activate && streamlit run app.py"
echo.
echo Aplikasi berjalan! Buka: http://localhost:8501
pause