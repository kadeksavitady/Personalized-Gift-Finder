"""
Script Migrasi Foto ke Cloudinary
==================================
Jalankan SEKALI di laptop kamu (bukan di Streamlit):
    pip install cloudinary sqlalchemy psycopg2-binary
    python migrate_to_cloudinary.py

Pastikan folder img/ ada di direktori yang sama dengan script ini.
"""

import os
import cloudinary
import cloudinary.uploader
from sqlalchemy import create_engine, text

# ─────────────────────────────────────────
# GANTI NILAI INI DENGAN KREDENSIAL KAMU
# ─────────────────────────────────────────
NEON_DB_URL = "postgresql://neondb_owner:npg_OY62IRlahkCX@ep-floral-cherry-aikwumag-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
CLOUDINARY_CLOUD_NAME = "dfrw5ikge"
CLOUDINARY_API_KEY = "252887715447945"
CLOUDINARY_API_SECRET = "sDo-h1xtCjh3odMFnJntTVMmuq8"
IMG_FOLDER         = "frontend/img"
# ─────────────────────────────────────────

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key    = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET,
)

engine = create_engine(NEON_DB_URL)
 
def migrate():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT nama_gambar FROM katalog_produk")
        ).fetchall()
 
        print(f"Total baris di database: {len(rows)}")
        print("=" * 50)
 
        sukses, skip, gagal = 0, 0, 0
 
        for row in rows:
            nama_gambar = str(row[0] or "").strip()
 
            # Sudah URL Cloudinary → skip
            if nama_gambar.startswith("http"):
                print(f"[SKIP] sudah URL: {nama_gambar[:60]}...")
                skip += 1
                continue
 
            # Kosong → skip
            if not nama_gambar:
                print(f"[SKIP] nama_gambar kosong")
                skip += 1
                continue
 
            # Cari file lokal
            img_path = os.path.join(IMG_FOLDER, f"{nama_gambar}.jpg")
            if not os.path.exists(img_path):
                print(f"[GAGAL] file tidak ditemukan: {img_path}")
                gagal += 1
                continue
 
            # Upload ke Cloudinary
            try:
                result = cloudinary.uploader.upload(
                    img_path,
                    folder="dnd_buket",
                    public_id=nama_gambar,
                    overwrite=True,
                )
                url_baru = result["secure_url"]
 
                # Update Neon — match berdasarkan nama_gambar lama
                conn.execute(
                    text("UPDATE katalog_produk SET nama_gambar = :url WHERE nama_gambar = :lama"),
                    {"url": url_baru, "lama": nama_gambar}
                )
                conn.commit()
 
                print(f"[OK] {nama_gambar} → {url_baru}")
                sukses += 1
 
            except Exception as e:
                print(f"[ERROR] {nama_gambar} → {e}")
                gagal += 1
 
        print("=" * 50)
        print(f"Selesai! ✅ Sukses: {sukses} | ⏭ Skip: {skip} | ❌ Gagal: {gagal}")
 
if __name__ == "__main__":
    migrate()