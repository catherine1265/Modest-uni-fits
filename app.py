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

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Modest Uni Fits",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    /* ── Header ── */
    .app-header {
        text-align: center;
        padding: 2rem 0 1.5rem;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 2rem;
    }
    .app-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .app-header p {
        color: #6B7280;
        margin: 0.4rem 0 0;
        font-size: 0.95rem;
    }

    /* ── Step label ── */
    .step-label {
        display: inline-block;
        background: #F3F4F6;
        color: #374151;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 0.4rem;
    }

    /* ── Crop card ── */
    .crop-card {
        background: #FAFAFA;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .crop-card h3 {
        font-size: 0.9rem;
        font-weight: 600;
        color: #111827;
        margin: 0 0 0.6rem;
    }

    /* ── Result badge ── */
    .result-banner {
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 1.5rem 0;
        letter-spacing: -0.3px;
    }
    .result-pass {
        background: #ECFDF5;
        color: #065F46;
        border: 1.5px solid #6EE7B7;
    }
    .result-fail {
        background: #FEF2F2;
        color: #991B1B;
        border: 1.5px solid #FCA5A5;
    }

    /* ── Detail card ── */
    .detail-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1rem 1.2rem;
    }
    .detail-card h4 {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin: 0 0 0.6rem;
    }
    .detail-value {
        font-size: 1.05rem;
        font-weight: 600;
        color: #111827;
    }
    .detail-sub {
        font-size: 0.8rem;
        color: #9CA3AF;
        margin-top: 2px;
    }
    .badge-pass { color: #059669; font-weight: 600; }
    .badge-fail { color: #DC2626; font-weight: 600; }

    /* ── Confidence bar ── */
    .conf-bar-bg {
        background: #F3F4F6;
        border-radius: 99px;
        height: 6px;
        margin-top: 6px;
        overflow: hidden;
    }
    .conf-bar-fill {
        height: 100%;
        border-radius: 99px;
        background: #6366F1;
    }

    /* ── Divider ── */
    hr { border-color: #F3F4F6; }

    /* ── Button ── */
    .stButton > button {
        background: #111827 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.55rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.02em !important;
        width: 100%;
    }
    .stButton > button:hover {
        background: #374151 !important;
    }

    /* ── Radio ── */
    .stRadio > div { gap: 0.5rem; }

    /* Hide streamlit branding ── */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>👔 Modest Uni Fits</h1>
    <p>Cek apakah outfit kamu sesuai dress code kampus — upload foto, crop tiap bagian, lalu analisis.</p>
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


def conf_bar(value: float, color: str = "#6366F1") -> str:
    pct = int(value * 100)
    return f"""
    <div class="conf-bar-bg">
        <div class="conf-bar-fill" style="width:{pct}%; background:{color};"></div>
    </div>
    """


def status_icon(detected: bool) -> str:
    return "✅ Lolos" if detected else "❌ Tidak lolos"


# ── Step 1: Image source ──────────────────────────────────────────────────────
st.markdown('<span class="step-label">Langkah 1 — Pilih Sumber Gambar</span>', unsafe_allow_html=True)
sumber = st.radio("", ["📁 Upload file", "📷 Kamera"], horizontal=True, label_visibility="collapsed")

file = None
if sumber == "📁 Upload file":
    file = st.file_uploader("Upload gambar outfit", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
else:
    file = st.camera_input("Ambil foto outfit", label_visibility="collapsed")

# ── Step 2: Crop & Analyze ────────────────────────────────────────────────────
if file is not None:
    image = Image.open(file).convert("RGB")

    st.markdown("---")
    st.markdown('<span class="step-label">Langkah 2 — Crop Tiap Bagian</span>', unsafe_allow_html=True)
    st.caption("Sesuaikan crop box untuk masing-masing area, lalu klik **Analisis**.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="crop-card"><h3>👕 Atasan (Top)</h3>', unsafe_allow_html=True)
        crop_top = st_cropper(image, realtime_update=True, key="top", aspect_ratio=(3, 4))
        if crop_top:
            st.image(crop_top, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="crop-card"><h3>👖 Bawahan (Bottom)</h3>', unsafe_allow_html=True)
        crop_bottom = st_cropper(image, realtime_update=True, key="bottom", aspect_ratio=(3, 4))
        if crop_bottom:
            st.image(crop_bottom, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="crop-card"><h3>🪪 Kartu Identitas</h3>', unsafe_allow_html=True)
        crop_card = st_cropper(image, realtime_update=True, key="card", aspect_ratio=(3, 4))
        if crop_card:
            st.image(crop_card, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        analyze = st.button("🔍 Analisis Outfit", use_container_width=True)

    # ── Step 3: Results ───────────────────────────────────────────────────────
    if analyze:
        if crop_top is None or crop_bottom is None or crop_card is None:
            st.warning("Pastikan semua bagian sudah di-crop sebelum analisis.")
        else:
            with st.spinner("Menganalisis outfit..."):
                top_path    = save_pil(crop_top)
                bottom_path = save_pil(crop_bottom)
                card_path   = save_pil(crop_card)

                try:
                    result = run_decision_cropped(top_path, bottom_path, card_path, models=models)
                finally:
                    for p in [top_path, bottom_path, card_path]:
                        if os.path.exists(p):
                            os.unlink(p)

            # Overall banner
            if result["status"] == "PASS":
                st.markdown('<div class="result-banner result-pass">✅ Outfit Sesuai Dress Code — LULUS</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-banner result-fail">❌ Outfit Tidak Sesuai Dress Code — TIDAK LULUS</div>', unsafe_allow_html=True)

            # Detail cards
            st.markdown('<span class="step-label">Detail Hasil</span>', unsafe_allow_html=True)
            top    = result["top"]
            bottom = result["bottom"]
            card   = result["card"]

            dc1, dc2, dc3 = st.columns(3)

            with dc1:
                color = "#059669" if top["detected"] else "#DC2626"
                st.markdown(f"""
                <div class="detail-card">
                    <h4>👕 Atasan</h4>
                    <div class="detail-value">{top['class'].title()}</div>
                    <div class="detail-sub">Confidence: {top['confidence']:.1%}</div>
                    {conf_bar(top['confidence'], color)}
                    <div style="margin-top:8px;" class="{'badge-pass' if top['detected'] else 'badge-fail'}">
                        {status_icon(top['detected'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with dc2:
                color = "#059669" if bottom["detected"] else "#DC2626"
                st.markdown(f"""
                <div class="detail-card">
                    <h4>👖 Bawahan</h4>
                    <div class="detail-value">{bottom['class'].title()}</div>
                    <div class="detail-sub">Confidence: {bottom['confidence']:.1%}</div>
                    {conf_bar(bottom['confidence'], color)}
                    <div style="margin-top:8px;" class="{'badge-pass' if bottom['detected'] else 'badge-fail'}">
                        {status_icon(bottom['detected'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with dc3:
                card_label = "Terdeteksi" if card["label"] == 1 else "Tidak terdeteksi"
                color = "#059669" if card["detected"] else "#DC2626"
                st.markdown(f"""
                <div class="detail-card">
                    <h4>🪪 Kartu Identitas</h4>
                    <div class="detail-value">{card_label}</div>
                    <div class="detail-sub">Confidence: {card['confidence']:.1%}</div>
                    {conf_bar(card['confidence'], color)}
                    <div style="margin-top:8px;" class="{'badge-pass' if card['detected'] else 'badge-fail'}">
                        {status_icon(card['detected'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Reasons / detail log
            with st.expander("📋 Lihat detail keputusan"):
                for reason in result["reasons"]:
                    icon = "✅" if "OK" in reason else "❌"
                    st.markdown(f"{icon} {reason}")

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 3rem 1rem; color: #9CA3AF;">
        <div style="font-size:3rem; margin-bottom:0.75rem;">👕</div>
        <div style="font-size:1rem; font-weight:500; color:#374151;">Belum ada gambar</div>
        <div style="font-size:0.85rem; margin-top:0.3rem;">Upload foto atau gunakan kamera untuk mulai.</div>
    </div>
    """, unsafe_allow_html=True)
