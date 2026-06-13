import pandas as pd
from sqlalchemy import create_engine

NEON_DB_URL = "postgresql://neondb_owner:npg_OY62IRlahkCX@ep-floral-cherry-aikwumag-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Lokasi file CSV lokal
CSV_PATH = 'backend/data/katalog_dnd_buket.csv'

def jalankan_migrasi():
    print("Membaca file CSV...")
    try:
        # Baca data dari CSV
        df = pd.read_csv(CSV_PATH)
        
        print("Menghubungkan ke Neon Postgres...")
        # Buat mesin penghubung ke database
        engine = create_engine(NEON_DB_URL)
        
        print("Memompa data ke database... (ini mungkin butuh beberapa detik)")
        # Masukkan data ke tabel bernama 'katalog_produk'
        # if_exists='replace' artinya kalau tabelnya sudah ada, akan ditimpa dengan yang baru
        df.to_sql('katalog_produk', engine, if_exists='replace', index=False)
        
        print("✅ Migrasi Sukses! Seluruh data katalog buket sudah masuk ke Neon.")
        
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")

if __name__ == "__main__":
    jalankan_migrasi()