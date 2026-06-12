@echo off
echo Menjalankan DnD Bouquett...
start cmd /k "venv\Scripts\activate && uvicorn main:app --reload"
timeout /t 3
start cmd /k "venv\Scripts\activate && streamlit run app.py"
echo.
echo Aplikasi berjalan! Buka: http://localhost:8501
pause