import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine
import streamlit as st

# Import library cloudinary
import cloudinary
import cloudinary.uploader

# Konfigurasi Database
DB_URL = st.secrets["NEON_DB_URL"]
engine = create_engine(DB_URL)

# Konfigurasi Cloudinary
cloudinary.config( 
  cloud_name = st.secrets["CLOUDINARY_CLOUD_NAME"], 
  api_key = st.secrets["CLOUDINARY_API_KEY"], 
  api_secret = st.secrets["CLOUDINARY_API_SECRET"] 
)

FEATURES = ['kategori_bahan', 'rentang_harga', 'warna_wrapper', 'warna_isi', 'gender_penerima']
FEATURES_NOMINAL = ['kategori_bahan', 'warna_wrapper', 'warna_isi', 'gender_penerima']

WEIGHTS = {
    'kategori_bahan': 1.0,
    'rentang_harga':  2.0,
    'warna_wrapper':  1.0,
    'warna_isi':      0.8,
    'gender_penerima':1.5,
}

HARGA_ORDINAL = {
    '<30k': 1, '35k - 45k': 2, '50k - 70k': 3, '80k - 100k': 4, '100k - 150k': 5
}

def get_data_from_db():
    """Fungsi pembantu untuk menarik data terbaru dari Neon"""
    return pd.read_sql('SELECT * FROM katalog_produk', engine)

def get_options():
    """Mengambil pilihan unik secara live dari database untuk dropdown menu"""
    df = get_data_from_db()
    return {col: sorted(df[col].dropna().unique().tolist()) for col in FEATURES}

def recommend(bahan="", harga="", warna="", isi="", gender=""):
    """Menghitung rekomendasi berdasarkan Cosine Similarity dari data Neon"""
    df = get_data_from_db()

    df['rentang_harga_num'] = df['rentang_harga'].map(HARGA_ORDINAL).fillna(0) / 5.0
    catalog_encoded = pd.get_dummies(df[FEATURES_NOMINAL])
    catalog_encoded['rentang_harga_num'] = df['rentang_harga_num'].values

    user_vector = pd.DataFrame(0.0, index=[0], columns=catalog_encoded.columns)

    if bahan:
        col_name = f"kategori_bahan_{bahan}"
        if col_name in user_vector.columns: user_vector[col_name] = 1
    if harga and harga in HARGA_ORDINAL:
        user_vector['rentang_harga_num'] = HARGA_ORDINAL[harga] / 5.0
    if warna:
        col_name = f"warna_wrapper_{warna}"
        if col_name in user_vector.columns: user_vector[col_name] = 1
    if isi:
        col_name = f"warna_isi_{isi}"
        if col_name in user_vector.columns: user_vector[col_name] = 1
    if gender:
        col_name = f"gender_penerima_{gender}"
        if col_name in user_vector.columns: user_vector[col_name] = 1

    for col in catalog_encoded.columns:
        for feat, weight in WEIGHTS.items():
            if col.startswith(feat):
                catalog_encoded[col] *= weight
                user_vector[col] *= weight
                break

    if user_vector.sum(axis=1).iloc[0] == 0:
        df['similarity_score'] = 0.0
        top_results = df.head(3)
    else:
        scores = cosine_similarity(user_vector, catalog_encoded)[0]
        df['similarity_score'] = scores
        top_results = df.sort_values(by='similarity_score', ascending=False).head(3)

    return {"status": "success", "data": top_results.to_dict(orient='records')}

def add_product(kategori_bahan, rentang_harga, warna_wrapper, warna_isi, gender_penerima, file_gambar):
    """Mengunggah foto ke Cloudinary, lalu menyimpan datanya ke Neon"""
    bersih_wrapper = warna_wrapper.strip().title()
    bersih_isi = warna_isi.strip().title()
    
    try:
        # 1. Upload file bytes langsung ke Cloudinary ke dalam folder 'dnd_buket'
        upload_result = cloudinary.uploader.upload(file_gambar, folder="dnd_buket")
        
        # 2. Ambil URL publik yang dihasilkan Cloudinary
        url_gambar = upload_result['secure_url']
        
        # 3. Siapkan data untuk masuk ke database Neon
        new_data = {
            'kategori_bahan': [kategori_bahan],
            'rentang_harga': [rentang_harga],
            'warna_wrapper': [bersih_wrapper],
            'warna_isi': [bersih_isi],
            'gender_penerima': [gender_penerima],
            'nama_gambar': [url_gambar] # Simpan URL-nya di sini
        }
        
        df_new = pd.DataFrame(new_data)
        df_new.to_sql('katalog_produk', engine, if_exists='append', index=False)
        
        return {"status": "success", "message": "Produk berhasil diarsipkan dengan foto Cloudinary!"}
        
    except Exception as e:
        return {"status": "error", "message": f"Gagal upload: {e}"}