## Cara Menjalankan
Kamu harus membuka dua terminal sekaligus:

Terminal 1 (Jalankan Backend):
Bash
cd backend
uvicorn main:app --reload

Terminal 2 (Jalankan Frontend):
Bash
cd frontend
streamlit run app_ui.py
