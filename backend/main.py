from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="Dnd Buket - Core Recommendation Engine")

# Mengizinkan komunikasi data lintas port antara FastAPI (8000) dan Streamlit (8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_PATH = 'data/katalog_dnd_buket.csv'
FEATURES = ['kategori_bahan', 'rentang_harga', 'warna_wrapper', 'warna_isi', 'momen_acara', 'gender_penerima']

# Pisahkan fitur nominal untuk mempermudah One-Hot Encoding nanti
FEATURES_NOMINAL = ['kategori_bahan', 'warna_wrapper', 'warna_isi', 'momen_acara', 'gender_penerima']

WEIGHTS = {
    'kategori_bahan': 1.0,
    'rentang_harga':  2.0,
    'warna_wrapper':  1.0,
    'warna_isi':      0.8,
    'momen_acara':    1.5,
    'gender_penerima':1.5,
}

HARGA_ORDINAL = {
    '<30k': 1, 
    '35k - 45k': 2, 
    '50k - 70k': 3,
    '80k - 100k': 4, 
    '100k - 150k': 5
}

class ProdukBaru(BaseModel):
    kategori_bahan: str
    rentang_harga: str
    warna_wrapper: str
    warna_isi: str
    momen_acara: str
    gender_penerima: str
    nama_gambar: str

@app.get("/options")
def get_options():
    """Mengambil pilihan unik secara live dari CSV untuk dropdown menu"""
    df = pd.read_csv(CSV_PATH)
    return {col: sorted(df[col].dropna().unique().tolist()) for col in FEATURES}

@app.get("/recommend")
def recommend(bahan: str = "", harga: str = "", warna: str = "", isi: str = "", acara: str = "", gender: str = ""):
    """Mengeksekusi Content-Based Filtering dengan Logika Vektor Nol (Zero-Vector) dan Pembobotan"""
    df = pd.read_csv(CSV_PATH)
    
    # 1. Transformasi One-Hot Encoding HANYA pada data katalog
    catalog_encoded = pd.get_dummies(df[FEATURES])
    
    # 2. Siapkan vektor user berukuran sama persis dengan katalog, isi dengan angka 0
    user_vector = pd.DataFrame(0, index=[0], columns=catalog_encoded.columns)
    
    # 3. Nyalakan saklar (ubah jadi 1) HANYA untuk kriteria yang dipilih oleh user
    if bahan:
        col_name = f"kategori_bahan_{bahan}"
        if col_name in user_vector.columns: user_vector[col_name] = 1
        
    if harga:
        if harga in HARGA_ORDINAL:
            user_vector['rentang_harga_num'] = HARGA_ORDINAL[harga] / 5.0
        
    if warna:
        col_name = f"warna_wrapper_{warna}"
        if col_name in user_vector.columns: user_vector[col_name] = 1
        
    if isi:
        col_name = f"warna_isi_{isi}"
        if col_name in user_vector.columns: user_vector[col_name] = 1
        
    if acara:
        col_name = f"momen_acara_{acara}"
        if col_name in user_vector.columns: user_vector[col_name] = 1
        
    if gender:
        col_name = f"gender_penerima_{gender}"
        if col_name in user_vector.columns: user_vector[col_name] = 1
        
    # Dilakukan setelah user_vector terisi angka 1 agar nilai 1 tersebut ikut dikalikan dengan bobot
    for col in catalog_encoded.columns:
        for feat, weight in WEIGHTS.items():
            if col.startswith(feat):
                catalog_encoded[col] *= weight
                user_vector[col] *= weight
                break
        
    # 4. Hitung nilai kedekatan sudut kosinus (Cosine Similarity)
    # Jika user menekan tombol tanpa memilih kriteria apa pun (vektor isinya 0 semua)
    if user_vector.sum(axis=1).iloc[0] == 0:
        df['similarity_score'] = 0.0
        top_results = df.head(3) # Tampilkan 3 data teratas secara default
    else:
        scores = cosine_similarity(user_vector, catalog_encoded)[0]
        df['similarity_score'] = scores
        top_results = df.sort_values(by='similarity_score', ascending=False).head(3)
    
    return {"status": "success", "data": top_results.to_dict(orient='records')}

@app.post("/add-product")
def add_product(item: ProdukBaru):
    # untuk membersihkan sensitivitas
    bersih_wrapper = item.warna_wrapper.strip().title()
    bersih_isi = item.warna_isi.strip().title()
    
    df = pd.read_csv(CSV_PATH)
    
    # Masukkan data yang sudah dibersihkan ke database
    new_data = item.dict()
    new_data['warna_wrapper'] = bersih_wrapper
    new_data['warna_isi'] = bersih_isi
    
    new_row = pd.DataFrame([new_data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    
    return {"status": "success", "message": "Produk baru berhasil diarsipkan!"}