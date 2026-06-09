"""
Modest Uni Fits — Outfit Compliance Checker
Deteksi apakah outfit sesuai dress code universitas.
"""

import os
import tempfile

import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

from src.services.decision import load_models, run_decision_cropped

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Modest Uni Fits",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Palette
       Vanilla Cream   #FFF7E6
       Blush Petal     #F7C8D3
       Rosewood        #B46A72
       Sage Leaf       #A8B58A
       Midnight Lagoon #2D3A47
    */

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: #FFF7E6;
        min-height: 100vh;
    }

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 3rem;
        max-width: 1080px;
    }

    /* ── Hero ── */
    .hero {
        background: linear-gradient(135deg, #2D3A47 0%, #B46A72 60%, #A9B7C6 100%);
        border-radius: 0 0 36px 36px;
        padding: 3rem 2rem 2.5rem;
        text-align: center;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: '';
        position: absolute;
        bottom: -30px; right: -30px;
        width: 160px; height: 160px;
        background: rgba(249,234,210,0.07);
        border-radius: 50%;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(249,234,210,0.18);
        color: #F7C8D3;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        padding: 4px 16px;
        border-radius: 99px;
        margin-bottom: 1rem;
        border: 1px solid rgba(248,238,194,0.3);
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 800;
        color: #FFF7E6;
        margin: 0 0 0.5rem;
        letter-spacing: -1px;
    }
    .hero p {
        color: #F7C8D3;
        font-size: 0.92rem;
        margin: 0;
        font-weight: 500;
        opacity: 0.85;
    }

    /* ── Step pill ── */
    .step-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #F7C8D3;
        border: 1.5px solid #A9B7C6;
        border-radius: 99px;
        padding: 5px 14px 5px 8px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(131,117,52,0.12);
    }
    .step-num {
        background: linear-gradient(135deg, #B46A72, #2D3A47);
        color: #FFF7E6;
        font-size: 0.65rem;
        font-weight: 800;
        width: 20px; height: 20px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .step-text {
        font-size: 0.73rem;
        font-weight: 700;
        color: #2D3A47;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* ── Source card ── */
    .source-card {
        background: #F7C8D3;
        border: 1.5px solid #A9B7C6;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(131,117,52,0.08);
    }

    /* ── Crop section ── */
    .crop-section {
        background: #F7C8D3;
        border: 1.5px solid #A9B7C6;
        border-radius: 20px;
        padding: 1.25rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 16px rgba(79,81,39,0.08);
    }
    .crop-icon-box {
        width: 38px; height: 38px;
        background: #FFF7E6;
        border: 1.5px solid #A9B7C6;
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .crop-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #2D3A47;
        margin: 0;
    }
    .crop-subtitle {
        font-size: 0.73rem;
        color: #B46A72;
        margin: 0;
    }

    /* ── Analyze button ── */
    .stButton > button {
        background: linear-gradient(135deg, #B46A72 0%, #2D3A47 100%) !important;
        color: #FFF7E6 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        width: 100%;
        box-shadow: 0 4px 16px rgba(79,81,39,0.3) !important;
    }
    .stButton > button:hover {
        opacity: 0.92;
        box-shadow: 0 6px 20px rgba(79,81,39,0.4) !important;
    }

    /* ── Result banner ── */
    .result-banner {
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .result-pass {
        background: linear-gradient(135deg, #F7C8D3, #FFF7E6);
        border: 2px solid #B46A72;
    }
    .result-fail {
        background: linear-gradient(135deg, #f7dede, #f9e8e8);
        border: 2px solid #B46A72;
    }
    .result-emoji { font-size: 3rem; display: block; margin-bottom: 0.5rem; }
    .result-title { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; margin: 0; }
    .result-pass .result-title { color: #2D3A47; }
    .result-fail .result-title { color: #7a3a45; }
    .result-sub { font-size: 0.85rem; font-weight: 500; margin-top: 0.3rem; opacity: 0.75; }
    .result-pass .result-sub { color: #2D3A47; }
    .result-fail .result-sub { color: #7a3a45; }

    /* ── Detail card ── */
    .detail-card {
        background: #F7C8D3;
        border: 1.5px solid #A9B7C6;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 2px 10px rgba(131,117,52,0.08);
    }
    .detail-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .detail-label {
        font-size: 0.68rem;
        font-weight: 700;
        color: #B46A72;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }
    .detail-status-pass {
        background: #A8B58A;
        color: #F7C8D3;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 99px;
    }
    .detail-status-fail {
        background: #B46A72;
        color: white;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 99px;
    }
    .detail-class {
        font-size: 1.3rem;
        font-weight: 800;
        color: #2D3A47;
        margin: 0 0 0.25rem;
        letter-spacing: -0.3px;
    }
    .detail-conf {
        font-size: 0.78rem;
        color: #B46A72;
        margin-bottom: 0.75rem;
    }
    .conf-track {
        background: #FFF7E6;
        border-radius: 99px;
        height: 8px;
        overflow: hidden;
        border: 1px solid rgba(131,117,52,0.2);
    }
    .conf-fill {
        height: 100%;
        border-radius: 99px;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: #F7C8D3;
        border-radius: 20px;
        border: 2px dashed #B46A72;
        margin-top: 1rem;
    }
    .empty-state-icon { font-size: 4rem; margin-bottom: 1rem; display: block; }
    .empty-state h3 { font-size: 1.1rem; font-weight: 700; color: #2D3A47; margin: 0 0 0.4rem; }
    .empty-state p { font-size: 0.85rem; color: #B46A72; margin: 0; }

    /* ── Misc ── */
    hr { border-color: #B46A72; opacity: 0.2; margin: 1.5rem 0; }
    .stRadio > div { gap: 0.75rem; }
    .stRadio label { font-weight: 500; color: #2D3A47; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Caption / helper text */
    .helper-text {
        font-size: 0.82rem;
        color: #B46A72;
        margin: -0.5rem 0 1.2rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ AI Powered · BINUS University</div>
    <h1>👔 Modest Uni Fits</h1>
    <p>Cek kesesuaian outfit dengan dress code kampus — cepat, akurat, otomatis.</p>
</div>
""", unsafe_allow_html=True)


# ── Load models ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Memuat model AI...")
def get_models():
    return load_models()

try:
    models = get_models()
except FileNotFoundError as e:
    st.error(f"⚠️ **Model tidak ditemukan**\n\n{e}")
    st.stop()
except Exception as e:
    st.error(f"⚠️ **Gagal memuat model:** {e}")
    st.stop()


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_pil(img: Image.Image) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    return tmp.name


def conf_bar(value: float, color: str) -> str:
    pct = int(value * 100)
    return f"""
    <div class="conf-track">
        <div class="conf-fill" style="width:{pct}%; background:{color};"></div>
    </div>
    """


def status_badge(detected: bool) -> str:
    if detected:
        return '<span class="detail-status-pass">✓ Lolos</span>'
    return '<span class="detail-status-fail">✗ Tidak Lolos</span>'


# ── Step 1: Image source ──────────────────────────────────────────────────────
st.markdown("""
<div class="step-pill">
    <span class="step-num">1</span>
    <span class="step-text">Pilih Sumber Gambar</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="source-card">', unsafe_allow_html=True)
sumber = st.radio("", ["📁 Upload file", "📷 Kamera"], horizontal=True, label_visibility="collapsed")
file = None
if sumber == "📁 Upload file":
    file = st.file_uploader("Upload gambar outfit", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
else:
    file = st.camera_input("Ambil foto outfit", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


# ── Step 2: Crop ──────────────────────────────────────────────────────────────
if file is not None:
    image = Image.open(file).convert("RGB")

    st.markdown("""
    <div class="step-pill">
        <span class="step-num">2</span>
        <span class="step-text">Crop Tiap Bagian</span>
    </div>
    <p class="helper-text">Sesuaikan kotak crop untuk masing-masing bagian outfit, lalu klik Analisis.</p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="crop-section">
            <div class="crop-icon-box">👕</div>
            <p class="crop-title">Atasan</p>
            <p class="crop-subtitle">Kemeja, kaos, dll.</p>
        </div>
        """, unsafe_allow_html=True)
        crop_top = st_cropper(image, realtime_update=True, key="top", aspect_ratio=(3, 4))
        if crop_top:
            st.image(crop_top, use_container_width=True)

    with col2:
        st.markdown("""
        <div class="crop-section">
            <div class="crop-icon-box">👖</div>
            <p class="crop-title">Bawahan</p>
            <p class="crop-subtitle">Celana, rok, dll.</p>
        </div>
        """, unsafe_allow_html=True)
        crop_bottom = st_cropper(image, realtime_update=True, key="bottom", aspect_ratio=(3, 4))
        if crop_bottom:
            st.image(crop_bottom, use_container_width=True)

    with col3:
        st.markdown("""
        <div class="crop-section">
            <div class="crop-icon-box">🪪</div>
            <p class="crop-title">Kartu Identitas</p>
            <p class="crop-subtitle">KTM / ID card</p>
        </div>
        """, unsafe_allow_html=True)
        crop_card = st_cropper(image, realtime_update=True, key="card", aspect_ratio=(3, 4))
        if crop_card:
            st.image(crop_card, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        analyze = st.button("🔍 Analisis Outfit Sekarang", use_container_width=True)

    # ── Step 3: Results ───────────────────────────────────────────────────────
    if analyze:
        if crop_top is None or crop_bottom is None or crop_card is None:
            st.warning("Pastikan semua bagian sudah di-crop sebelum analisis.")
        else:
            with st.spinner("Menganalisis outfit kamu..."):
                top_path    = save_pil(crop_top)
                bottom_path = save_pil(crop_bottom)
                card_path   = save_pil(crop_card)

                try:
                    result = run_decision_cropped(top_path, bottom_path, card_path, models=models)
                    if result["bottom"]["class"].lower() == "short":
                        result["bottom"]["detected"] = False
                        result["status"] = "FAIL"
                finally:
                    for p in [top_path, bottom_path, card_path]:
                        if os.path.exists(p):
                            os.unlink(p)

            st.markdown("""
            <div class="step-pill">
                <span class="step-num">3</span>
                <span class="step-text">Hasil Analisis</span>
            </div>
            """, unsafe_allow_html=True)

            if result["status"] == "PASS":
                st.markdown("""
                <div class="result-banner result-pass">
                    <span class="result-emoji">🎉</span>
                    <p class="result-title">Outfit Kamu Lolos!</p>
                    <p class="result-sub">Semua komponen sesuai dress code kampus</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-banner result-fail">
                    <span class="result-emoji">⚠️</span>
                    <p class="result-title">Outfit Tidak Lolos</p>
                    <p class="result-sub">Ada komponen yang tidak sesuai dress code kampus</p>
                </div>
                """, unsafe_allow_html=True)

            top    = result["top"]
            bottom = result["bottom"]
            card   = result["card"]

            dc1, dc2, dc3 = st.columns(3, gap="medium")

            with dc1:
                color = "#A8B58A" if top["detected"] else "#B46A72"
                st.markdown(f"""
                <div class="detail-card">
                    <div class="detail-card-header">
                        <span class="detail-label">👕 Atasan</span>
                        {status_badge(top["detected"])}
                    </div>
                    <p class="detail-class">{top['class'].title()}</p>
                    <p class="detail-conf">Confidence: {top['confidence']:.1%}</p>
                    {conf_bar(top['confidence'], color)}
                </div>
                """, unsafe_allow_html=True)

            with dc2:
                color = "#A8B58A" if bottom["detected"] else "#B46A72"
                st.markdown(f"""
                <div class="detail-card">
                    <div class="detail-card-header">
                        <span class="detail-label">👖 Bawahan</span>
                        {status_badge(bottom["detected"])}
                    </div>
                    <p class="detail-class">{bottom['class'].title()}</p>
                    <p class="detail-conf">Confidence: {bottom['confidence']:.1%}</p>
                    {conf_bar(bottom['confidence'], color)}
                </div>
                """, unsafe_allow_html=True)

            with dc3:
                card_label = "Terdeteksi" if card["label"] == 1 else "Tidak Terdeteksi"
                color = "#A8B58A" if card["detected"] else "#B46A72"
                st.markdown(f"""
                <div class="detail-card">
                    <div class="detail-card-header">
                        <span class="detail-label">🪪 Kartu Identitas</span>
                        {status_badge(card["detected"])}
                    </div>
                    <p class="detail-class">{card_label}</p>
                    <p class="detail-conf">Confidence: {card['confidence']:.1%}</p>
                    {conf_bar(card['confidence'], color)}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📋 Lihat log detail keputusan"):
                for reason in result["reasons"]:
                    icon = "✅" if "OK" in reason else "❌"
                    st.markdown(f"{icon} `{reason}`")

else:
    st.markdown("""
    <div class="empty-state">
        <span class="empty-state-icon">👗</span>
        <h3>Belum ada gambar</h3>
        <p>Upload foto outfit atau gunakan kamera untuk mulai pengecekan dress code.</p>
    </div>
    """, unsafe_allow_html=True)
