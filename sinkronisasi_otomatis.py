import toml
from sqlalchemy import create_engine, text
import cloudinary
import cloudinary.api

# 1. Ambil Kunci dari Secrets
rahasia = toml.load(".streamlit/secrets.toml")
cloudinary.config(cloud_name=rahasia["CLOUDINARY_CLOUD_NAME"], api_key=rahasia["CLOUDINARY_API_KEY"], api_secret=rahasia["CLOUDINARY_API_SECRET"])
engine = create_engine(rahasia["NEON_DB_URL"])

# 2. Ambil semua foto dari folder 'dnd_buket' di Cloudinary
print("🔍 Sedang mencari foto di folder Cloudinary...")
folder_name = "dnd_buket"
resources = cloudinary.api.resources(type="upload", prefix=folder_name, max_results=100)

# 3. Masukkan link ke dalam list
foto_di_awan = {res['public_id'].split('/')[-1]: res['secure_url'] for res in resources['resources']}

# 4. Update database Neon secara otomatis
with engine.begin() as conn:
    for nama_file, url in foto_di_awan.items():
        # Kita asumsikan nama file (tanpa .jpg) sama dengan nama di database
        nama_produk_di_db = nama_file.split('.')[0] 
        query = text("UPDATE katalog_produk SET nama_gambar = :url WHERE nama_gambar = :nama_lama")
        conn.execute(query, {"url": url, "nama_lama": nama_produk_di_db})
        print(f"✅ Berhasil sinkronisasi: {nama_produk_di_db}")

print("🎉 Selesai! Sekarang database dan gudang foto sudah terhubung.")