import streamlit as st
import os
from utils.ui_helpers import score_bar, badge_kategori, badge_rank
import urllib.parse
import pipeline

st.set_page_config(page_title="DnD Bouquett – Gift Finder", page_icon="🌸", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #fdf6f9 !important;
    color: #2d1a24 !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #fdf6f9; }
::-webkit-scrollbar-thumb { background: #f9a8d4; border-radius: 4px; }
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 2.5rem !important; padding-bottom: 2.5rem !important; max-width: 1200px !important; }
.title-brand {
    font-family: 'Playfair Display', serif;
    color: #be185d;
    font-size: 48px;
    font-weight: 600;
    letter-spacing: -0.3px;
    line-height: 1.1;
    margin-bottom: 4px;
}
.title-brand span { color: #3a7d44; font-style: italic; font-weight: 400; }
.subtitle-brand { color: #a16070; font-size: 14px; font-weight: 300; letter-spacing: 0.03em; margin-bottom: 0; }
hr { border: none !important; border-top: 1px solid #f5ccd8 !important; margin: 18px 0 !important; }
.sidebar-title { font-family: 'Playfair Display', serif; font-size: 17px; font-weight: 600; color: #be185d; margin-bottom: 16px; }
.field-label { font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; color: #a16070; margin-bottom: 4px; display: block; }

.stSelectbox > div > div { background: #fdf6f9 !important; border: 1px solid #f5ccd8 !important; border-radius: 10px !important; color: #2d1a24 !important; font-size: 13px !important; }
.stSelectbox > div > div:focus-within { border-color: #be185d !important; box-shadow: 0 0 0 3px rgba(190, 24, 93, 0.1) !important; }
.stSelectbox svg { fill: #d4799a !important; }
.stTextInput > div > div > input { background: #fdf6f9 !important; border: 1px solid #f5ccd8 !important; border-radius: 10px !important; color: #2d1a24 !important; font-size: 13px !important; }
.stTextInput > div > div > input:focus { border-color: #be185d !important; box-shadow: 0 0 0 3px rgba(190, 24, 93, 0.1) !important; }
.stTextInput > div > div > input::placeholder { color: #c9a0ac !important; }
[data-testid="stCaptionContainer"] p { color: #a16070 !important; font-size: 11px !important; }
[data-testid="stFileUploader"] section { background: #fdf6f9 !important; border: 1px dashed #f5ccd8 !important; border-radius: 10px !important; }
[data-testid="stFileUploader"] section button { background: rgba(161, 96, 112, 0.08) !important; color: #a16070 !important; border: 1px solid #f5ccd8 !important; box-shadow: none !important; width: auto !important; border-radius: 8px !important; transition: all 0.2s ease !important; }
[data-testid="stFileUploader"] section button:hover { background: rgba(161, 96, 112, 0.15) !important; color: #be185d !important; transform: none !important; box-shadow: none !important; }
[data-testid="stFileUploader"] section button:focus, [data-testid="stFileUploader"] section button:active { background: rgba(161, 96, 112, 0.08) !important; color: #a16070 !important; box-shadow: none !important; transform: none !important; }
.stButton > button { background: #be185d !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; font-weight: 500 !important; letter-spacing: 0.02em !important; padding: 11px 18px !important; width: 100% !important; box-shadow: 0 4px 14px rgba(190, 24, 93, 0.18) !important; transition: all 0.2s ease !important; }
.stButton > button:hover { background: #9d174d !important; transform: translateY(-1px) !important; box-shadow: 0 6px 18px rgba(190, 24, 93, 0.25) !important; }
.stButton > button:active { transform: translateY(0px) !important; }
[data-testid="stFormSubmitButton"] > button { background: #be185d !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-size: 13px !important; font-weight: 500 !important; padding: 11px 18px !important; width: 100% !important; box-shadow: 0 4px 14px rgba(190, 24, 93, 0.18) !important; transition: all 0.2s ease !important; }
[data-testid="stFormSubmitButton"] > button:hover { background: #9d174d !important; transform: translateY(-1px) !important; box-shadow: 0 6px 18px rgba(190, 24, 93, 0.25) !important; }
.secondary-btn-container .stButton > button { background: #ffffff !important; color: #be185d !important; border: 1px solid #f5ccd8 !important; box-shadow: none !important; }
.secondary-btn-container .stButton > button:hover { background: #fef3f7 !important; box-shadow: none !important; transform: none !important; }
.stAlert { background: #fef3f7 !important; border: 1px solid #f9a8d4 !important; border-radius: 14px !important; color: #9d174d !important; }
[data-testid="stAlert"] p, [data-testid="stAlert"] span { color: #9d174d !important; }
[data-testid="stAlert"] svg { fill: #be185d !important; }
[data-testid="stVerticalBlockBorderDriven"] { background: #ffffff !important; border: 1px solid #f0e8ed !important; border-radius: 18px !important; padding: 18px !important; transition: all 0.25s ease !important; }
[data-testid="stVerticalBlockBorderDriven"]:hover { border-color: #f9a8d4 !important; box-shadow: 0 8px 24px rgba(190, 24, 93, 0.08) !important; transform: translateY(-2px) !important; }
[data-testid="stImage"] img { border-radius: 12px !important; object-fit: cover !important; }
.badge-kategori { display: inline-block; background: #fef3f7; color: #9d174d; padding: 2px 9px; border-radius: 20px; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; border: 1px solid #f9a8d4; }
.badge-kategori-green { display: inline-block; background: #eaf3de; color: #27500a; padding: 2px 9px; border-radius: 20px; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; border: 1px solid #c0dd97; }
.badge-kategori-teal { display: inline-block; background: #e1f5ee; color: #085041; padding: 2px 9px; border-radius: 20px; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; border: 1px solid #9fe1cb; }
.badge-rank-1 { display: inline-block; background: #fef3f7; color: #9d174d; border: 1px solid #f9a8d4; padding: 2px 9px; border-radius: 20px; font-size: 9px; font-weight: 700; }
.badge-rank-other { display: inline-block; background: #f4f4f2; color: #5f5e5a; border: 1px solid #d3d1c7; padding: 2px 9px; border-radius: 20px; font-size: 9px; font-weight: 700; }
.score-wrap { margin: 8px 0 4px; }
.score-bar-bg { height: 4px; background: #fde8f0; border-radius: 4px; overflow: hidden; }
.score-bar-fill { height: 4px; background: #f9a8d4; border-radius: 4px; }
.score-text { font-size: 11px; color: #a16070; margin-top: 4px; }
.product-price { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 600; color: #be185d; margin-top: 4px; }
.admin-label { font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; color: #a16070; border-left: 3px solid #be185d; padding-left: 8px; margin-bottom: 16px; border-radius: 0; }
</style>
""", unsafe_allow_html=True)

query_params = st.query_params
is_owner_route = query_params.get("view") == "owner"

if is_owner_route:
    st.markdown("<div class='title-brand'>⚙️ Owner <span>Dashboard</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-brand'>Sistem Manajemen Konten — DnD Bouquett Internal</div>", unsafe_allow_html=True)
    st.write("---")

    password_input = st.text_input("Password Hak Akses:", type="password", placeholder="Masukkan kata sandi internal...")

    OWNER_PASSWORD = os.getenv("OWNER_PASSWORD", "default_fallback")
    if password_input == OWNER_PASSWORD:
        st.success("Akses diterima! Silakan perbarui katalog produk.")

        with st.form("form_tambah_barang", clear_on_submit=True):
            st.markdown("<div class='admin-label'>Data Produk Baru</div>", unsafe_allow_html=True)
            
            # Ambil opsi warna dari backend
            try:
                opts = pipeline.get_options()
                opsi_wrapper = opts.get('warna_wrapper', [])
                opsi_isi = opts.get('warna_isi', [])
            except:
                opsi_wrapper = []
                opsi_isi = []

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<span class='field-label'>Kategori Bahan</span>", unsafe_allow_html=True)
                st.caption("Pilih jenis bahan utama buket.")
                in_bahan = st.selectbox("Kategori Bahan", ["artificial", "pipecleaner", "snack"], label_visibility="collapsed")

                st.markdown("<span class='field-label'>Rentang Harga</span>", unsafe_allow_html=True)
                st.caption("Pilih rentang harga jual buket ini.")
                in_harga = st.selectbox("Rentang Harga", ["<30k", "35k - 45k", "50k - 70k", "80k - 100k", "100k - 150k"], label_visibility="collapsed")

                st.markdown("<span class='field-label'>Warna Wrapper</span>", unsafe_allow_html=True)
                st.caption("Warna kertas/plastik pembungkus luar buket.")
                in_wrapper = st.selectbox("Warna Wrapper", opsi_wrapper if opsi_wrapper else ["—"], label_visibility="collapsed")

                st.markdown("<span class='field-label'>Warna Isi</span>", unsafe_allow_html=True)
                st.caption("Warna dominan bunga atau isi buket.")
                in_isi = st.selectbox("Warna Isi", opsi_isi if opsi_isi else ["—"], label_visibility="collapsed")

            with c2:
                st.markdown("<span class='field-label'>Gender Penerima</span>", unsafe_allow_html=True)
                st.caption("Target gender yang cocok untuk buket ini.")
                in_gender = st.selectbox("Gender Penerima", ["Perempuan", "Laki-laki", "Netral"], label_visibility="collapsed")

                st.markdown("<span class='field-label'>Nama File Foto</span>", unsafe_allow_html=True)
                st.caption("Nama unik untuk file foto, tanpa ekstensi .jpg.")
                in_img_code = st.text_input("Nama File Foto", placeholder="Contoh: artificial_11", label_visibility="collapsed")

                st.markdown("<span class='field-label'>Upload Foto Produk</span>", unsafe_allow_html=True)
                st.caption("Upload foto buket dalam format .jpg.")
                in_file = st.file_uploader("Upload Foto (.jpg)", type=["jpg", "jpeg"], label_visibility="collapsed")

            st.write("")
            btn_submit = st.form_submit_button("Daftarkan & Upload Produk")

            if btn_submit:
                errors = []
                if not in_file:
                    errors.append("Foto produk belum diupload.")
                if in_wrapper == "—" or in_isi == "—":
                    errors.append("Opsi warna tidak tersedia — pastikan database berjalan.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    # Ambil wujud asli file gambar yang diupload
                    file_bytes = in_file.getvalue()
                    
                    # Lempar datanya langsung ke pipeline (tanpa payload_post)
                    result = pipeline.add_product(
                        kategori_bahan=in_bahan, 
                        rentang_harga=in_harga, 
                        warna_wrapper=in_wrapper, 
                        warna_isi=in_isi, 
                        gender_penerima=in_gender, 
                        file_gambar=file_bytes
                    )
                    
                    if result["status"] == "success":
                        st.success(result["message"])
                        st.balloons()
                    else:
                        st.error(result["message"])
            else:
                    st.error("Lengkapi semua field teks dan upload foto produk!")
    elif password_input:
        st.error("Kata sandi salah. Akses ditolak.")

else:
    st.markdown("<div class='title-brand'>🌸 DnD <span>Bouquett</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-brand'>Temukan buket handmade yang berbicara dari hatimu — dipersonalisasi untukmu.</div>", unsafe_allow_html=True)
    st.write("---")

    try:
        opts = pipeline.get_options()
        col_sidebar, col_content = st.columns([1, 2.8], gap="large")

        with col_sidebar:
            with st.container(border=True):
                st.markdown("<div class='sidebar-title'>✦ Atur Kriteria Kado</div>", unsafe_allow_html=True)

                st.markdown("<span class='field-label'>Kategori Bahan</span>", unsafe_allow_html=True)
                f_bahan = st.selectbox("Kategori Bahan", [""] + opts['kategori_bahan'], label_visibility="collapsed")

                st.markdown("<span class='field-label'>Rentang Harga</span>", unsafe_allow_html=True)
                f_harga = st.selectbox("Rentang Harga", [""] + opts['rentang_harga'], label_visibility="collapsed")

                st.markdown("<span class='field-label'>Warna Wrapper</span>", unsafe_allow_html=True)
                f_wrapper = st.selectbox("Warna Wrapper", [""] + opts['warna_wrapper'], label_visibility="collapsed")

                st.markdown("<span class='field-label'>Warna Isi</span>", unsafe_allow_html=True)
                f_isi = st.selectbox("Warna Isi", [""] + opts['warna_isi'], label_visibility="collapsed")

                st.markdown("<span class='field-label'>Untuk Siapa?</span>", unsafe_allow_html=True)
                f_gender = st.selectbox("Untuk Siapa", [""] + opts['gender_penerima'], label_visibility="collapsed")

                st.write("")
                btn_cari = st.button("Temukan Buket Impian!", use_container_width=True)

        with col_content:
            if btn_cari:
                payload = {
                    "bahan": f_bahan, "harga": f_harga, "warna": f_wrapper,
                    "isi": f_isi, "gender": f_gender
                }
                res = pipeline.recommend(bahan=f_bahan, harga=f_harga, warna=f_wrapper, isi=f_isi, gender=f_gender)

                st.markdown(
                    "<p style='font-family:Playfair Display,serif; font-size:22px; "
                    "font-weight:600; color:#2d1a24; margin-bottom:16px;'>"
                    "✦ 3 Rekomendasi Terbaik Untukmu</p>",
                    unsafe_allow_html=True
                )

                cols_card = st.columns(3, gap="medium")
                for i, item in enumerate(res['data']):
                    rank = i + 1
                    bahan = item['kategori_bahan'].lower()

                    if bahan == "artificial":
                        badge_kat_html = f"<span class='badge-kategori'>{item['kategori_bahan'].upper()}</span>"
                    elif bahan == "snack":
                        badge_kat_html = f"<span class='badge-kategori-green'>{item['kategori_bahan'].upper()}</span>"
                    else:
                        badge_kat_html = f"<span class='badge-kategori-teal'>{item['kategori_bahan'].upper()}</span>"

                    with cols_card[i]:
                        with st.container(border=True):
                            # Mengambil nama atau URL dari database
                            data_foto = item['nama_gambar']
                            
                            # LOGIKA HYBRID:
                            # 1. Jika data baru (berupa link Cloudinary)
                            if str(data_foto).startswith("http"):
                                st.image(data_foto, use_container_width=True)
                                
                            # 2. Jika data lama (berupa nama file lokal)
                            else:
                                img_path = f"img/{data_foto}.jpg"
                                # Cek apakah file lokalnya ada di laptop/server
                                if os.path.exists(img_path):
                                    st.image(img_path, use_container_width=True)
                                # 3. Jika benar-benar tidak ada gambar (Failsafe)
                                else:
                                    bg = {"artificial": "#fef3f7", "snack": "#eaf3de"}.get(bahan, "#e1f5ee")
                                    st.markdown(
                                        f"<div style='height:100px; background:{bg}; border-radius:12px; "
                                        f"display:flex; align-items:center; justify-content:center; "
                                        f"font-size:30px; margin:8px 0;'>🌸</div>",
                                        unsafe_allow_html=True
                                    )
                            
                            # Tampilkan gambar langsung dari URL Cloudinary
                            url_foto = item['nama_gambar']
                            
                            if url_foto.startswith("http"):
                                st.image(url_foto, use_container_width=True)
                            else:
                                # Jika ada data lama yang belum pakai URL
                                st.info("Tidak ada foto")   
                            
                            st.markdown(
                                f"<p style='font-family:Playfair Display,serif; font-size:15px; "
                                f"font-weight:600; color:#2d1a24; margin:8px 0 2px; line-height:1.3;'>"
                                f"{item['warna_wrapper']} × {item['warna_isi']}</p>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='product-price'>Rp {item['rentang_harga']}</div>",
                                unsafe_allow_html=True
                            )
                            match_pct = item['similarity_score'] * 100
                            st.markdown(score_bar(match_pct), unsafe_allow_html=True)
                            st.markdown(
                                f"<p style='font-size:11px; color:#a16070; margin:6px 0 12px; line-height:1.6;'>"
                                f"💝 {item['gender_penerima']}</p>",
                                unsafe_allow_html=True
                            )
                            teks_pesan = (
                                f"Halo Admin Dnd Buket! 🌸\n\n"
                                f"Saya menggunakan Gift Finder dan ingin memesan buket ini:\n"
                                f"- Jenis: {item['kategori_bahan'].upper()}\n"
                                f"- Warna: {item['warna_wrapper']} x {item['warna_isi']}\n"
                                f"- Budget: Rp {item['rentang_harga']}\n\n"
                                f"Apakah ready?"
                            )
                            pesan_encoded = urllib.parse.quote(teks_pesan)
                            nomor_wa = "6281244170440"
                            link_wa = f"https://wa.me/{nomor_wa}?text={pesan_encoded}"
                            st.link_button(
                                "💌 Pesan via WhatsApp",
                                url=link_wa,
                                use_container_width=True
                            )
            else:
                st.markdown(
                    "<div style='margin-top:70px; text-align:center;'>"
                    "<div style='font-size:52px; margin-bottom:14px;'>🌸</div>"
                    "<p style='font-family:Playfair Display,serif; font-size:22px; "
                    "font-weight:600; color:#d4799a;'>Pilih kriteria kado di sebelah kiri,</p>"
                    "<p style='font-size:13px; color:#a16070; margin-top:6px;'>"
                    "lalu klik <b style='color:#be185d;'>Temukan Buket Impian</b> untuk melihat rekomendasi.</p>"
                    "</div>",
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan sistem atau gagal terhubung ke Database Neon: {e}")