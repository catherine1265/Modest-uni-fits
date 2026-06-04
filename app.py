# Tampilan Streamlit. Upload 1 gambar -> 4 hasil.

import os
import tempfile

import streamlit as st

from src.services.decision import load_models, run_decision

st.set_page_config(page_title="Fashion + Card Checker", layout="centered")
st.title("Fashion + Card Checker")
st.write("Upload 1 gambar untuk dicek: jenis top, jenis bottom, kartu, dan kelulusan.")


@st.cache_resource
def get_models():
    return load_models()


models = get_models()

uploaded = st.file_uploader("Upload gambar", type=["jpg", "jpeg", "png"])

if uploaded is not None:
    st.image(uploaded, use_container_width=True)

    suffix = os.path.splitext(uploaded.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        tmp_path = tmp.name

    if st.button("Cek"):
        result = run_decision(tmp_path, models=models)

        if result["status"] == "PASS":
            st.success("Overall: LULUS")
        else:
            st.error("Overall: TIDAK LULUS")

        st.divider()

        top = result["top"]
        bottom = result["bottom"]
        card = result["card"]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Top")
            st.write(f"Jenis: {top['class']}")
            st.write(f"Confidence: {top['confidence']:.2%}")
            st.write("✅ Terdeteksi" if top["detected"] else "❌ Tidak")

        with col2:
            st.subheader("Bottom")
            st.write(f"Jenis: {bottom['class']}")
            st.write(f"Confidence: {bottom['confidence']:.2%}")
            st.write("✅ Terdeteksi" if bottom["detected"] else "❌ Tidak")

        with col3:
            st.subheader("Kartu")
            st.write("Ada" if card["label"] == 1 else "Tidak ada")
            st.write(f"Confidence: {card['confidence']:.2%}")
            st.write("✅ Lolos" if card["detected"] else "❌ Tidak")

    os.unlink(tmp_path)
