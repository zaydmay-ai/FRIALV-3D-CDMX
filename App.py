import streamlit as st
import plotly.graph_objects as go
import fitz  # PyMuPDF
from PIL import Image

st.set_page_config(page_title="Frialv 3D CDMX", layout="wide")
st.title("⚡ Frialv: Extractor de Planos 3D")

with st.sidebar:
    st.header("⚙️ Configuración")
    p_conduit = st.number_input("Costo m Conduit 3/4\"", value=35.0)
    p_cable = st.number_input("Costo m Cable Cal. 12", value=22.0)
    st.divider()
    archivo_pdf = st.file_uploader("📂 Sube tu plano PDF aquí", type=["pdf"])

if archivo_pdf:
    with st.spinner('Leyendo plano...'):
        doc = fitz.open(stream=archivo_pdf.read(), filetype="pdf")
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        st.subheader("🖼️ Vista Previa del Plano")
        st.image(img, use_container_width=True)

    st.subheader("🏗️ Modelo 3D de la Instalación")
    fig = go.Figure(data=[go.Scatter3d(
        x=[1, 5, 5, 8], y=[1, 1, 6, 6], z=[1.2, 2.4, 2.4, 0.5],
        mode='lines+markers', line=dict(color='orange', width=10)
    )])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👋 Sube un plano en la barra lateral para empezar.")
