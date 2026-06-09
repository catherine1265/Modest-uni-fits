# Input: upload file ATAU kamera. Crop top, bottom, & kartu.

import os
import tempfile

import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

from src.services.decision import load_models, run_decision_cropped

st.set_page_config(page_title="Fashion + Card Checker", layout="wide")
st.title("Fashion + Card Checker")
st.write("Pilih input gambar, lalu crop bagian atas, bawah, dan kartu.")


@st.cache_resource
def get_models():
    return load_models()


models = get_models()


def save_pil(img):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    return tmp.name


# --- Pilih sumber input ---
sumber = st.radio("Sumber gambar:", ["Upload file", "Kamera"], horizontal=True)

if sumber == "Upload file":
    file = st.file_uploader("Upload gambar", type=["jpg", "jpeg", "png"])
else:
    file = st.camera_input("Ambil foto")

if file is not None:
    image = Image.open(file).convert("RGB")
    if image.width > image.height:
        image = image.rotate(90, expand=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Crop TOP")
        crop_top = st_cropper(image, realtime_update=True, key="top")
        st.image(crop_top, width=150)
    with col2:
        st.subheader("Crop BOTTOM")
        crop_bottom = st_cropper(image, realtime_update=True, key="bottom")
        st.image(crop_bottom, width=150)
    with col3:
        st.subheader("Crop KARTU")
        crop_card = st_cropper(image, realtime_update=True, key="card")
        st.image(crop_card, width=150)

    if st.button("Analyze"):
        top_path = save_pil(crop_top)
        bottom_path = save_pil(crop_bottom)
        card_path = save_pil(crop_card)

        result = run_decision_cropped(top_path, bottom_path, card_path, models=models)

        if result["status"] == "PASS":
            st.success("Overall: LULUS")
        else:
            st.error("Overall: TIDAK LULUS")

        st.divider()

        top = result["top"]
        bottom = result["bottom"]
        card = result["card"]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Top")
            st.write(f"Jenis: {top['class']}")
            st.write(f"Confidence: {top['confidence']:.2%}")
            st.write("✅ Terdeteksi" if top["detected"] else "❌ Tidak")
        with c2:
            st.subheader("Bottom")
            st.write(f"Jenis: {bottom['class']}")
            st.write(f"Confidence: {bottom['confidence']:.2%}")
            st.write("✅ Terdeteksi" if bottom["detected"] else "❌ Tidak")
        with c3:
            st.subheader("Kartu")
            st.write("Ada" if card["label"] == 1 else "Tidak ada")
            st.write(f"Confidence: {card['confidence']:.2%}")
            st.write("✅ Lolos" if card["detected"] else "❌ Tidak")

        for p in [top_path, bottom_path, card_path]:
            os.unlink(p)
