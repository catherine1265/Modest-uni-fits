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

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background */
    .stApp {
        background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 50%, #fff0f6 100%);
        min-height: 100vh;
    }

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 3rem;
        max-width: 1080px;
    }

    /* ── Hero header ── */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #a855f7 50%, #ec4899 100%);
        border-radius: 0 0 32px 32px;
        padding: 3rem 2rem 2.5rem;
        text-align: center;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
        pointer-events: none;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 4px 14px;
        border-radius: 99px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.3);
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 800;
        color: white;
        margin: 0 0 0.5rem;
        letter-spacing: -1px;
        text-shadow: 0 2px 12px rgba(0,0,0,0.15);
    }
    .hero p {
        color: rgba(255,255,255,0.85);
        font-size: 0.95rem;
        margin: 0;
        font-weight: 500;
    }

    /* ── Step pill ── */
    .step-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 99px;
        padding: 5px 14px 5px 8px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .step-num {
        background: linear-gradient(135deg, #667eea, #a855f7);
        color: white;
        font-size: 0.65rem;
        font-weight: 800;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .step-text {
        font-size: 0.75rem;
        font-weight: 700;
        color: #374151;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* ── Source selector ── */
    .source-card {
        background: white;
        border: 1.5px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(102,126,234,0.06);
    }

    /* ── Crop section ── */
    .crop-section {
        background: white;
        border: 1.5px solid #E5E7EB;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(102,126,234,0.08);
    }

    .crop-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #F3F4F6;
    }
    .crop-icon {
        font-size: 1.4rem;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #f0f4ff, #faf5ff);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #E5E7EB;
    }
    .crop-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }
    .crop-subtitle {
        font-size: 0.75rem;
        color: #9CA3AF;
        margin: 0;
    }

    /* ── Analyze button ── */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4) !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(102,126,234,0.5) !important;
    }

    /* ── Result banner ── */
    .result-banner {
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
    }
    .result-banner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        opacity: 0.05;
        background-size: 30px 30px;
    }
    .result-pass {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        border: 2px solid #6EE7B7;
    }
    .result-fail {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border: 2px solid #FCA5A5;
    }
    .result-emoji {
        font-size: 3rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    .result-title {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .result-pass .result-title { color: #065F46; }
    .result-fail .result-title { color: #991B1B; }
    .result-sub {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.3rem;
        opacity: 0.7;
    }
    .result-pass .result-sub { color: #065F46; }
    .result-fail .result-sub { color: #991B1B; }

    /* ── Detail card ── */
    .detail-card {
        background: white;
        border: 1.5px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        height: 100%;
    }
    .detail-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .detail-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .detail-status-pass {
        background: #D1FAE5;
        color: #065F46;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 99px;
    }
    .detail-status-fail {
        background: #FEE2E2;
        color: #991B1B;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 99px;
    }
    .detail-class {
        font-size: 1.3rem;
        font-weight: 800;
        color: #111827;
        margin: 0 0 0.25rem;
        letter-spacing: -0.3px;
    }
    .detail-conf {
        font-size: 0.8rem;
        color: #6B7280;
        margin-bottom: 0.75rem;
    }
    .conf-track {
        background: #F3F4F6;
        border-radius: 99px;
        height: 8px;
        overflow: hidden;
    }
    .conf-fill {
        height: 100%;
        border-radius: 99px;
        transition: width 0.6s ease;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: white;
        border-radius: 20px;
        border: 2px dashed #E5E7EB;
        margin-top: 1rem;
    }
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
    }
    .empty-state h3 {
        font-size: 1.1rem;
        font-weight: 700;
        color: #374151;
        margin: 0 0 0.4rem;
    }
    .empty-state p {
        font-size: 0.85rem;
        color: #9CA3AF;
        margin: 0;
    }

    /* ── Divider ── */
    hr { border-color: #F3F4F6; margin: 1.5rem 0; }

    /* ── Radio ── */
    .stRadio > div { gap: 0.75rem; }
    .stRadio label { font-weight: 500; }

    /* Hide branding ── */
    #MainMenu, footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Hero Header ───────────────────────────────────────────────────────────────
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
    <p style="font-size:0.82rem; color:#6B7280; margin: -0.5rem 0 1rem;">
        Sesuaikan kotak crop untuk masing-masing bagian outfit, lalu klik Analisis.
    </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="crop-section">
            <div class="crop-header">
                <div class="crop-icon">👕</div>
                <div>
                    <p class="crop-title">Atasan</p>
                    <p class="crop-subtitle">Kemeja, kaos, dll.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        crop_top = st_cropper(image, realtime_update=True, key="top", aspect_ratio=(3, 4))
        if crop_top:
            st.image(crop_top, use_container_width=True)

    with col2:
        st.markdown("""
        <div class="crop-section">
            <div class="crop-header">
                <div class="crop-icon">👖</div>
                <div>
                    <p class="crop-title">Bawahan</p>
                    <p class="crop-subtitle">Celana, rok, dll.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        crop_bottom = st_cropper(image, realtime_update=True, key="bottom", aspect_ratio=(3, 4))
        if crop_bottom:
            st.image(crop_bottom, use_container_width=True)

    with col3:
        st.markdown("""
        <div class="crop-section">
            <div class="crop-header">
                <div class="crop-icon">🪪</div>
                <div>
                    <p class="crop-title">Kartu Identitas</p>
                    <p class="crop-subtitle">KTM / ID card</p>
                </div>
            </div>
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

            # Overall banner
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

            # Detail cards
            top    = result["top"]
            bottom = result["bottom"]
            card   = result["card"]

            dc1, dc2, dc3 = st.columns(3, gap="medium")

            with dc1:
                color = "#10B981" if top["detected"] else "#EF4444"
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
                color = "#10B981" if bottom["detected"] else "#EF4444"
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
                color = "#10B981" if card["detected"] else "#EF4444"
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
