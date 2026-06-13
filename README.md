# 🌸 DnD Bouquett — Personalized Gift Finder

> Sistem Rekomendasi Berbasis **Weighted Content-Based Filtering** untuk UMKM *dnd bouquett*  
> Mata Kuliah Sistem Rekomendasi
> **Kadek Savita Dyutianaya** — NRP 3324600033
---

## Deskripsi Proyek
Aplikasi web interaktif yang membantu pelanggan menemukan buket handmade yang paling sesuai dengan preferensi mereka (bahan, harga, warna, momen, gender penerima) menggunakan algoritma **Cosine Similarity** dengan pembobotan fitur.

Arsitektur menggunakan pendekatan **Decoupled/Microservices**:
- **Backend Engine** - FastAPI (port 8000)
- **Frontend UI** - Streamlit (port 8501)

---

## Struktur Proyek

```
dnd-bouquett/
├── main.py                    # Backend FastAPI (recommendation engine)
├── app.py                     # Frontend Streamlit (user interface)
├── requirements.txt           # Daftar dependensi Python
├── .env                       # Variabel lingkungan (TIDAK di-push ke GitHub)
├── .env.example               # Template .env untuk referensi
├── .gitignore
├── jalankan.bat               # Script otomatis untuk Windows
├── data/
│   └── katalog_dnd_buket.csv  # Database katalog produk (dinamis)
├── img/
│   └── *.jpg                  # Foto produk (tidak di-push ke GitHub)
└── utils/
    └── ui_helpers.py          # Helper fungsi UI (score bar, badge)
```

---

## Cara Menjalankan (Lokal)

### Prasyarat
- Python **3.9+**
- pip

### 1. Clone Repository

```bash
git clone https://github.com/kadeksavitady/Personalized-Gift-Finder.git
cd dnd-bouquett
```

### 2. Buat & Aktifkan Virtual Environment

```bash
# Buat venv
python -m venv venv

# Aktifkan — Windows
venv\Scripts\activate
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment

Buka file `.env.example`, ubah isinya, lalu **hapus bagian `.example`** dari nama filenya sehingga menjadi `.env`.

Isi file:
```
OWNER_PASSWORD=isi_password_owner_disini
```

### 5. Jalankan Aplikasi

**Cara cepat (Windows):** klik dua kali `jalankan.bat`

**Cara manual (dua terminal terpisah):**

```bash
# Terminal 1 — Backend
uvicorn main:app --reload

# Terminal 2 — Frontend
streamlit run app.py
```

### 6. Buka di Browser

| Layanan | URL |
|---------|-----|
| Aplikasi utama (Streamlit) | http://localhost:8501 |
| API dokumentasi (FastAPI) | http://localhost:8000/docs |
| Owner Dashboard | http://localhost:8501/?view=owner |

---

## Metodologi

### Alur Sistem

```
User Input (Dropdown) 
    → Explicit User Profile Construction
    → One-Hot Encoding (katalog + vektor user)
    → Weighted Feature Matrix
    → Cosine Similarity Calculation
    → Ranking Top-3 (Soft-Matching)
    → Tampil Rekomendasi + Tombol WhatsApp
```

### Fitur yang Digunakan

| Fitur | Tipe | Bobot |
|-------|------|-------|
| `kategori_bahan` | Kategorikal | 1.0 |
| `rentang_harga` | Ordinal | 2.0 |
| `warna_wrapper` | Kategorikal | 1.0 |
| `warna_isi` | Kategorikal | 0.8 |
| `gender_penerima` | Kategorikal | 1.5 |

### Keunggulan Implementasi
- **Zero-Vector Handling**: jika tidak ada kriteria dipilih, tampil 3 produk teratas (tidak pernah kosong)
- **Soft-Matching**: produk terdekat tetap ditampilkan meski tidak ada yang 100% cocok
- **Dynamic Retraining**: menambah produk baru langsung memperbarui matriks tanpa restart server
- **Multi-value Momen**: satu produk dapat cocok untuk beberapa momen sekaligus

---

## Owner Dashboard

Akses fitur manajemen konten melalui URL rahasia:

```
http://localhost:8501/?view=owner
```

Fitur yang tersedia:
- Tambah produk baru ke katalog CSV
- Upload foto produk (.jpg)
- Password terproteksi (dikonfigurasi via `.env`)

---

## Dataset

- **Sumber:** Data primer internal UMKM Dnd Buket @dndbouquett + data sintetis representatif
- **Jumlah awal:** 31 produk (artificial flower, pipecleaner, snack bouquet)
- **Sifat:** Dinamis — dapat diperluas melalui Owner Dashboard tanpa mengubah kode

---