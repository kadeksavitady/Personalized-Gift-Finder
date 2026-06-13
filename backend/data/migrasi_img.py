import os
import pandas as pd
from sqlalchemy import create_engine
import cloudinary
import cloudinary.uploader

# 1. MASUKKAN KUNCI RAHASIAMU DI SINI (Hanya untuk keperluan script ini saja)
NEON_DB_URL = ""
CLOUDINARY_CLOUD_NAME = ""
CLOUDINARY_API_KEY = ""
CLOUDINARY_API_SECRET = ""

# Konfigurasi Cloudinary
cloudinary.config( 
  cloud_name = CLOUDINARY_CLOUD_NAME, 
  api_key = CLOUDINARY_API_KEY, 
  api_secret = CLOUDINARY_API_SECRET 
)

# Hubungkan ke Neon
engine = create_engine(NEON_DB_URL)

def jalankan_migrasi_total():
    print("Membaca data katalog lama dari Neon...")
    df = pd.read_sql("SELECT * FROM katalog_produk", engine)
    
    perubahan = False

    for index, row in df.iterrows():
        nama_gambar = row['nama_gambar']
        
        # Jika isinya belum berupa URL Cloudinary (berarti masih format lama seperti "pipecleaner_01")
        if not str(nama_gambar).startswith("http"):
            # Sesuaikan letak folder img kamu di sini
            jalur_file = f"frontend/img/{nama_gambar}.jpg"
            
            if os.path.exists(jalur_file):
                print(f"🚀 Mengunggah {nama_gambar}.jpg ke Cloudinary...")
                try:
                    # Upload ke folder dnd_buket di Cloudinary
                    hasil = cloudinary.uploader.upload(jalur_file, folder="dnd_buket")
                    url_baru = hasil['secure_url']
                    
                    # Ganti teks di tabel Pandas dengan URL baru
                    df.at[index, 'nama_gambar'] = url_baru
                    perubahan = True
                    print(f"✅ Berhasil! Tautan baru: {url_baru}")
                except Exception as e:
                    print(f"❌ Gagal mengunggah {nama_gambar}: {e}")
            else:
                print(f"⚠️ File fisik tidak ditemukan di laptop: {jalur_file}")

    # Simpan kembali tabel yang sudah diperbarui tautannya ke Neon
    # Simpan kembali tabel yang sudah diperbarui tautannya ke Neon
    # Simpan kembali tabel yang sudah diperbarui tautannya ke Neon
    if perubahan:
        print("\nMenyimpan pembaruan tautan ke database Neon...")
        
        # Menggunakan engine.begin() agar transaksinya dibungkus dengan aman (otomatis commit/rollback)
        with engine.begin() as koneksi_aman:
            df.to_sql('katalog_produk', con=koneksi_aman, if_exists='replace', index=False)
            
        print("🎉 Selesai! Semua foto buket lama sudah resmi berada di Cloud.")

if __name__ == "__main__":
    jalankan_migrasi_total()