import streamlit as st
import os
import re
import json
import html
import logging
import urllib.parse
import uuid
from groq import Groq
from utils.ui_helpers import score_bar, badge_kategori, badge_rank
import pipeline

# Muat .env untuk pemakaian lokal (GROQ_API_KEY, OWNER_PASSWORD, dll).
# Dibungkus try/except supaya deployment tanpa python-dotenv tidak error.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

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
/* Tombol Mulai Percakapan Baru di dalam chat (gaya outline) */
.st-key-chat_clear button {
    background: #ffffff !important; background-color: #ffffff !important; color: #be185d !important;
    border: 1px solid #f5ccd8 !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; font-weight: 500 !important;
    padding: 11px 18px !important; width: 100% !important; box-shadow: none !important; transition: all 0.2s ease !important;
}
.st-key-chat_clear button:hover {
    background: #fef3f7 !important; border-color: #f9a8d4 !important; transform: none !important; box-shadow: none !important;
}
.st-key-chat_clear button p { color: inherit !important; }
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
/* Tombol chatbot berlabel (pojok kanan atas) */
[class*="st-key-chat_toggle"] { align-items: flex-end !important; }
[class*="st-key-chat_toggle"] .stButton { display: flex !important; justify-content: flex-end !important; width: 100% !important; }
[class*="st-key-chat_toggle"] [data-testid="stTooltipHoverTarget"] { width: auto !important; }
[class*="st-key-chat_toggle"] .stButton button {
    width: auto !important; min-width: 0 !important; height: 44px !important; min-height: 44px !important;
    padding: 0 22px !important; border-radius: 30px !important;
    font-size: 13px !important; font-weight: 500 !important; letter-spacing: 0.02em !important;
    white-space: nowrap !important;
}
[class*="st-key-chat_toggle"] .stButton button p, [class*="st-key-chat_toggle"] .stButton button span { color: inherit !important; margin: 0 !important; font-size: 13px !important; white-space: nowrap !important; }
/* Tertutup: pink solid biar jelas itu tombol chatbot */
.st-key-chat_toggle_closed .stButton button {
    background: #be185d !important; background-color: #be185d !important; color: #ffffff !important; border: none !important;
    box-shadow: 0 6px 18px rgba(190, 24, 93, 0.28) !important;
}
.st-key-chat_toggle_closed .stButton button:hover { background: #9d174d !important; transform: translateY(-1px) !important; }
/* Terbuka: putih outline (tombol tutup) */
.st-key-chat_toggle_open .stButton button {
    background: #ffffff !important; background-color: #ffffff !important; color: #be185d !important; border: 1px solid #f5ccd8 !important;
    box-shadow: none !important;
}
.st-key-chat_toggle_open .stButton button:hover { background: #fef3f7 !important; border-color: #f9a8d4 !important; transform: none !important; }
/* Kolom ketik chat: menempel di bawah halaman (gaya room chat) */
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: #fdf6f9 !important; }
[data-testid="stChatInput"] {
    max-width: 720px !important; margin-left: auto !important; margin-right: auto !important;
    background: #ffffff !important; border: 1px solid #f5ccd8 !important; border-radius: 26px !important;
    box-shadow: 0 6px 20px rgba(190, 24, 93, 0.06) !important;
}
[data-testid="stChatInput"]:focus-within { border-color: #be185d !important; box-shadow: 0 0 0 3px rgba(190, 24, 93, 0.1) !important; }
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] [data-baseweb="textarea"], [data-testid="stChatInput"] [data-baseweb="base-input"] { background: transparent !important; border: none !important; }
[data-testid="stChatInput"] textarea { color: #2d1a24 !important; font-size: 14px !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #c9a0ac !important; }
[data-testid="stChatInputSubmitButton"] { background: #be185d !important; color: #ffffff !important; border-radius: 50% !important; }
[data-testid="stChatInputSubmitButton"]:disabled { background: #f5ccd8 !important; color: #ffffff !important; }
/* Chat: pesan customer = pill netral, jawaban chatbot = teks polos (tanpa bubble) */
.chat-row-user { display: flex; justify-content: flex-end; margin: 14px 0 8px; }
.chat-bubble-user {
    max-width: 72%;
    background: #f1efef;
    color: #2d1a24;
    padding: 10px 20px;
    border-radius: 24px;
    font-size: 14px;
    line-height: 1.55;
    overflow-wrap: anywhere;
}
/* Formatting markdown jawaban chatbot (bold, list) supaya rapi & lega */
[data-testid="stMarkdownContainer"] p { line-height: 1.7; }
[data-testid="stMarkdownContainer"] ul, [data-testid="stMarkdownContainer"] ol { padding-left: 1.3rem; margin: 6px 0 12px; }
[data-testid="stMarkdownContainer"] li { margin-bottom: 6px; line-height: 1.65; }
[data-testid="stMarkdownContainer"] strong { color: #2d1a24; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# GROQ CLIENT (untuk fitur Tanya MinDee)
# ==========================================================
GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
_groq_client = None

# Memori percakapan (otomatis, tanpa aksi apa pun dari pelanggan)
MAX_HISTORY_MESSAGES = 20      # jumlah pesan terakhir (user + MinDee) yang dikirim ke LLM
MAX_USER_TURNS_FOR_PREFS = 6   # jumlah pesan pelanggan terakhir untuk ekstraksi preferensi
HISTORY_DIR = "chat_histories"
PERSIST_HISTORY = True         # False = riwayat hanya di memori sesi (hilang saat halaman di-refresh)


def get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY belum diset di environment/.env")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


# Kategori valid yang cocok persis dengan backend/main.py
HARGA_OPTIONS = ["<30k", "35k - 45k", "50k - 70k", "80k - 100k", "100k - 150k"]
BAHAN_OPTIONS = ["artificial", "pipecleaner", "snack"]
GENDER_OPTIONS = ["Perempuan", "Laki-laki", "Netral"]

# ----------------------------------------------------------
# Sanitasi output LLM: buang blok <think>...</think> (termasuk yang
# belum tertutup / baru setengah tag saat streaming) supaya proses
# "berpikir" model tidak bocor ke tampilan.
# ----------------------------------------------------------
_THINK_CLOSED_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_THINK_OPEN_RE = re.compile(r"<think>.*$", re.DOTALL | re.IGNORECASE)
_PARTIAL_TAG_RE = re.compile(r"</?(?:think|thin|thi|th|t)?$", re.IGNORECASE)


def clean_llm_text(text: str) -> str:
    text = _THINK_CLOSED_RE.sub("", text)
    text = _THINK_OPEN_RE.sub("", text)
    text = _PARTIAL_TAG_RE.sub("", text)
    return text.lstrip()


def _pick_valid(value, allowed) -> str:
    """Pastikan nilai hasil LLM benar-benar salah satu opsi yang valid."""
    return value if isinstance(value, str) and value in allowed else ""


# ----------------------------------------------------------
# Memori percakapan (conversation history)
# ----------------------------------------------------------
def build_user_context(messages: list, max_turns: int = MAX_USER_TURNS_FOR_PREFS) -> str:
    """Gabungkan beberapa pesan pelanggan terakhir (urut dari lama ke baru)
    supaya preferensi dari pesan sebelumnya tidak hilang."""
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"][-max_turns:]
    return "\n".join(user_msgs)


# ----------------------------------------------------------
# Penyimpanan riwayat otomatis (satu file JSON per sesi, seperti bot Telegram)
# ----------------------------------------------------------
_SID_RE = re.compile(r"[a-f0-9]{32}")


def get_session_id() -> str:
    """ID sesi acak yang disimpan di URL (?sid=...), supaya riwayat tetap
    diingat walau halaman di-refresh. Nilai dari URL divalidasi ketat
    (32 karakter hex) karena dipakai sebagai nama file."""
    sid = st.query_params.get("sid", "")
    if not _SID_RE.fullmatch(sid or ""):
        sid = uuid.uuid4().hex
        st.query_params["sid"] = sid
    return sid


def _history_path(sid: str) -> str:
    return os.path.join(HISTORY_DIR, f"riwayat_chat_{sid}.json")


def _json_default(o):
    # Jaga-jaga kalau ada tipe numpy di data produk
    return o.item() if hasattr(o, "item") else str(o)


def load_history(sid: str) -> list:
    if not PERSIST_HISTORY:
        return []
    path = _history_path(sid)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return []


def save_history(sid: str, messages: list):
    if not PERSIST_HISTORY:
        return
    try:
        os.makedirs(HISTORY_DIR, exist_ok=True)
        with open(_history_path(sid), "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False, default=_json_default)
    except OSError:
        logger.exception("Gagal menyimpan riwayat chat %s", sid)


def clear_history(sid: str):
    try:
        os.remove(_history_path(sid))
    except OSError:
        pass


def reset_chat():
    """Mulai percakapan baru: kosongkan memori sesi sekaligus file riwayatnya."""
    st.session_state.chat_messages = []
    clear_history(st.session_state.chat_sid)


def extract_preferences(user_message: str, opts: dict) -> dict:
    """Ekstrak preferensi bebas dari chat pelanggan menjadi field terstruktur
    yang cocok dengan parameter pipeline.recommend().

    user_message boleh berisi beberapa pesan pelanggan berurutan
    (lihat build_user_context)."""
    warna_wrapper_opts = opts.get("warna_wrapper", [])
    warna_isi_opts = opts.get("warna_isi", [])

    system_prompt = f"""Kamu adalah ekstraktor preferensi untuk sistem rekomendasi buket DnD Bouquett.
Dari pesan pelanggan, ekstrak preferensi berikut. WAJIB kembalikan HANYA JSON valid,
tanpa markdown code fence, tanpa penjelasan tambahan.

Input berisi beberapa pesan pelanggan berurutan; gabungkan preferensinya, dan jika ada yang berubah, pakai yang terbaru.

Field dan nilai yang DIPERBOLEHKAN (pilih persis salah satu, atau "" jika tidak disebutkan/tidak cocok):
- bahan: salah satu dari {BAHAN_OPTIONS}
- harga: salah satu dari {HARGA_OPTIONS} (kalau pelanggan sebut nominal rupiah, pilih rentang paling mendekati)
- warna: salah satu dari {warna_wrapper_opts}
- isi: salah satu dari {warna_isi_opts}
- gender: salah satu dari {GENDER_OPTIONS}

Format output (JSON murni, tanpa apa pun selain ini):
{{"bahan": "", "harga": "", "warna": "", "isi": "", "gender": ""}}
"""
    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        reasoning_effort="none",
    )
    raw = clean_llm_text(response.choices[0].message.content or "")
    raw = raw.replace("```json", "").replace("```", "").strip()

    # Ambil objek JSON pertama saja, kalau model menambah teks di sekitarnya
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    try:
        parsed = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        parsed = {}

    return {
        "bahan": _pick_valid(parsed.get("bahan"), BAHAN_OPTIONS),
        "harga": _pick_valid(parsed.get("harga"), HARGA_OPTIONS),
        "warna": _pick_valid(parsed.get("warna"), warna_wrapper_opts),
        "isi": _pick_valid(parsed.get("isi"), warna_isi_opts),
        "gender": _pick_valid(parsed.get("gender"), GENDER_OPTIONS),
    }


def stream_chat_reply(user_message: str, items: list, history=None):
    """Generator yang menghasilkan potongan teks jawaban secara bertahap (efek mengetik).

    history: daftar pesan sebelumnya (tanpa pesan pelanggan yang sedang diproses)
    berbentuk [{"role": "user"/"assistant", "content": "..."}, ...]."""
    if not items:
        static_reply = (
            "Kak, boleh cerita sedikit lagi soal budget atau warna favoritnya? "
            "Biar MinDee carikan buket yang paling pas ya 🌸"
        )
        for word in static_reply.split(" "):
            yield word + " "
        return

    system_prompt = (
        "Namamu MinDee, asisten customer service virtual yang ramah untuk dnd.bouquet (Dear n Deep). "
        "Sebut dirimu 'MinDee' (bukan 'aku' atau 'saya'), dan panggil pelanggan 'Kak'. "
        "Tulis HANYA kalimat pembuka singkat (1-2 kalimat) yang menanggapi permintaan pelanggan dan "
        "mengantar ke daftar rekomendasi. JANGAN sebut jenis bahan, warna, atau harga, dan JANGAN buat list: "
        "daftar pilihan akan ditambahkan otomatis oleh sistem. "
        "Jangan gunakan HTML dan jangan tampilkan proses berpikir."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for m in (history or [])[-MAX_HISTORY_MESSAGES:]:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({
        "role": "user",
        "content": f"Pesan pelanggan: {user_message}\nJumlah pilihan yang ditemukan: {len(items)}",
    })

    client = get_groq_client()
    stream = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.5,
        reasoning_effort="none",
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

    # Detail produk (bahan, warna, harga) dibuat oleh kode, BUKAN oleh LLM,
    # supaya ejaan & angkanya selalu persis sama dengan data di database.
    yield "\n\n" + build_options_markdown(items)
    yield "\n\nKalau ada yang cocok, klik tombol **Pesan via WhatsApp** di bawah kartu produk ya, Kak 🌸"


def build_options_markdown(items: list) -> str:
    lines = []
    for it in items:
        bahan = str(it.get("kategori_bahan", "")).strip().capitalize()
        lines.append(
            f"- **{bahan}** dengan kombinasi warna **{it.get('warna_wrapper')} x {it.get('warna_isi')}**, "
            f"harga **Rp {it.get('rentang_harga')}**"
        )
    return "\n".join(lines)


def render_user_bubble(text: str):
    """Pesan customer: pill rounded warna netral. Teks di-escape supaya
    karakter seperti < > & tidak merusak HTML."""
    safe = html.escape(text).replace("\n", "<br>")
    st.markdown(
        f"<div class='chat-row-user'><div class='chat-bubble-user'>{safe}</div></div>",
        unsafe_allow_html=True,
    )


def render_assistant_text(text: str):
    """Jawaban chatbot: teks polos tanpa bubble, dirender sebagai Markdown
    (bold, list, dll). Tanpa unsafe_allow_html, jadi tag HTML tidak akan
    tampil/bocor sebagai kode."""
    st.markdown(text)


def render_recommendation_cards(items: list):
    """Kartu hasil rekomendasi — dipakai bersama oleh tab manual & tab chatbot."""
    if not items:
        return

    cols_card = st.columns(min(len(items), 3), gap="medium")
    for i, item in enumerate(items):
        bahan = item['kategori_bahan'].lower()

        if bahan == "artificial":
            badge_kat_html = f"<span class='badge-kategori'>{item['kategori_bahan'].upper()}</span>"
        elif bahan == "snack":
            badge_kat_html = f"<span class='badge-kategori-green'>{item['kategori_bahan'].upper()}</span>"
        else:
            badge_kat_html = f"<span class='badge-kategori-teal'>{item['kategori_bahan'].upper()}</span>"

        with cols_card[i % len(cols_card)]:
            with st.container(border=True):
                data_foto = str(item.get('nama_gambar') or "")

                if data_foto.startswith("http"):
                    st.image(data_foto, width='stretch')
                else:
                    bg = {"artificial": "#fef3f7", "snack": "#eaf3de"}.get(bahan, "#e1f5ee")
                    st.markdown(
                        f"<div style='height:140px; background:{bg}; border-radius:12px; "
                        f"display:flex; align-items:center; justify-content:center; "
                        f"font-size:40px;'>🌸</div>",
                        unsafe_allow_html=True
                    )

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


def render_chat_tab(opts: dict):
    st.markdown("<div class='sidebar-title' style='text-align:center;'>✦ Tanya MinDee</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#a16070; font-size:13px; margin-bottom:4px;'>"
        "Buket seperti apa yang ingin kamu cari? let MinDee know yaa!</p>"
        "<p style='text-align:center; color:#c9a0ac; font-size:11px; margin-bottom:20px;'>"
        "Perintah: <b>/clear</b> atau <b>/reset</b> untuk mulai percakapan baru · "
        "<b>/exit</b> untuk kembali ke pencarian manual</p>",
        unsafe_allow_html=True,
    )

    # Riwayat dimuat otomatis (dari file jika ada), jadi konteks tidak hilang.
    if "chat_sid" not in st.session_state:
        st.session_state.chat_sid = get_session_id()
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = load_history(st.session_state.chat_sid)

    # chat_input WAJIB dipanggil di level teratas (di luar columns/container)
    # supaya otomatis menempel di bawah halaman seperti room chat.
    user_input = st.chat_input("Contoh: mau buket buat ibu, budget 100rb, suka warna pastel...")

    # ---- Perintah khusus (diketik di kolom chat) ----
    cmd = (user_input or "").strip().lower()
    if cmd in ("/clear", "/reset"):
        reset_chat()
        st.rerun()
    if cmd == "/exit":
        st.session_state.view = "manual"
        st.rerun()

    _, col_chat, _ = st.columns([1, 3, 1])

    with col_chat:
        # ---- Tombol: mulai percakapan baru (riwayat diingat otomatis selama sesi) ----
        b1, _ = st.columns([1, 2])
        with b1:
            if st.button("🗑️ Mulai Percakapan Baru", key="chat_clear"):
                reset_chat()
                st.rerun()

        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                render_user_bubble(msg["content"])
            else:
                render_assistant_text(msg["content"])
                if msg.get("items"):
                    render_recommendation_cards(msg["items"])

        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            render_user_bubble(user_input)

            items = []
            try:
                with st.spinner("Mencari rekomendasi terbaik..."):
                    # Preferensi diekstrak dari beberapa pesan pelanggan terakhir,
                    # bukan hanya pesan terbaru, supaya konteks sesi tidak hilang.
                    prefs = extract_preferences(
                        build_user_context(st.session_state.chat_messages), opts
                    )
                    res = pipeline.recommend(
                        bahan=prefs["bahan"],
                        harga=prefs["harga"],
                        warna=prefs["warna"],
                        isi=prefs["isi"],
                        gender=prefs["gender"],
                    )
                    items = res.get("data", [])

                # Efek mengetik: teks polos (Markdown), bertahap, kursor "▌" di ujung.
                # [:-1] karena pesan terakhir (pelanggan) dikirim terpisah di dalam fungsi.
                placeholder = st.empty()
                full_text = ""
                for piece in stream_chat_reply(
                    user_input, items, history=st.session_state.chat_messages[:-1]
                ):
                    full_text += piece
                    placeholder.markdown(clean_llm_text(full_text) + " ▌")

                reply = clean_llm_text(full_text)
                placeholder.markdown(reply)  # render final tanpa kursor

            except Exception:
                # Detail error hanya di log server, tidak ditampilkan ke pelanggan
                logger.exception("Gagal memproses chat pelanggan")
                items = []
                reply = "Maaf Kak, MinDee lagi sibuk nih. Coba lagi sebentar ya! 🙏"
                render_assistant_text(reply)

            st.session_state.chat_messages.append({"role": "assistant", "content": reply, "items": items})
            save_history(st.session_state.chat_sid, st.session_state.chat_messages)
            if items:
                render_recommendation_cards(items)


query_params = st.query_params
is_owner_route = query_params.get("view") == "owner"

if is_owner_route:
    st.markdown("<div class='title-brand'>⚙️ Owner <span>Dashboard</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-brand'>Sistem Manajemen Konten — DnD Bouquett Internal</div>", unsafe_allow_html=True)
    st.write("---")

    password_input = st.text_input("Password Hak Akses:", type="password", placeholder="Masukkan kata sandi internal...")

    # Tanpa fallback: kalau OWNER_PASSWORD belum diset, akses ditolak.
    OWNER_PASSWORD = os.getenv("OWNER_PASSWORD")
    if not OWNER_PASSWORD:
        st.error("OWNER_PASSWORD belum diset di server. Akses dashboard ditutup.")
    elif password_input == OWNER_PASSWORD:
        st.success("Akses diterima! Silakan perbarui katalog produk.")

        with st.form("form_tambah_barang", clear_on_submit=True):
            st.markdown("<div class='admin-label'>Data Produk Baru</div>", unsafe_allow_html=True)

            try:
                opts = pipeline.get_options()
                opsi_wrapper = opts.get('warna_wrapper', [])
                opsi_isi = opts.get('warna_isi', [])
            except Exception:
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
                    file_bytes = in_file.getvalue()

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
    elif password_input:
        st.error("Kata sandi salah. Akses ditolak.")

else:
    st.session_state.setdefault("view", "manual")

    def toggle_chat_view():
        st.session_state.view = "manual" if st.session_state.view == "chat" else "chat"

    in_chat = st.session_state.view == "chat"

    head_left, head_right = st.columns([3, 1], vertical_alignment="top")
    with head_left:
        st.markdown("<div class='title-brand'>🌸 DnD <span>Bouquett</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle-brand'>Temukan buket handmade yang berbicara dari hatimu — dipersonalisasi untukmu.</div>", unsafe_allow_html=True)
    with head_right:
        with st.container(key="chat_toggle_open" if in_chat else "chat_toggle_closed"):
            st.button(
                "✕  Tutup MinDee" if in_chat else "🤖  Tanya MinDee",
                key="chat_toggle_btn",
                on_click=toggle_chat_view,
                help="Kembali ke pencarian" if in_chat else "Ceritakan kado yang kamu cari, MinDee bantu carikan",
            )
    st.write("---")

    try:
        opts = pipeline.get_options()

        if not in_chat:
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
                    res = pipeline.recommend(bahan=f_bahan, harga=f_harga, warna=f_wrapper, isi=f_isi, gender=f_gender)

                    st.markdown(
                        "<p style='font-family:Playfair Display,serif; font-size:22px; "
                        "font-weight:600; color:#2d1a24; margin-bottom:16px;'>"
                        "✦ 3 Rekomendasi Terbaik Untukmu</p>",
                        unsafe_allow_html=True
                    )
                    render_recommendation_cards(res.get('data', []))
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

        else:
            render_chat_tab(opts)

    except Exception:
        logger.exception("Gagal memuat aplikasi / terhubung ke database")
        st.error("❌ Terjadi kesalahan sistem. Coba muat ulang halaman beberapa saat lagi.")