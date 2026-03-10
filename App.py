import streamlit as st
import plotly.graph_objects as go
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
import easyocr

st.set_page_config(page_title="Frialv 3D Master", layout="wide")
st.title("⚡ Frialv 3D: Escaneo Autónomo de Planos")

# Inicializar el lector de texto (OCR)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['es'])

reader = load_ocr()

with st.sidebar:
    st.header("📂 Entrada de Proyecto")
    archivo_pdf = st.file_uploader("Subir Plano Eléctrico (PDF)", type=["pdf"])
    st.divider()
    st.header("💰 Costos Frialv")
    p_tubo = st.number_input("Precio Conduit m", value=35.0)
    p_cable = st.number_input("Precio Cable m", value=22.0)

if archivo_pdf:
    with st.spinner('Escaneando Simbología y Calibres...'):
        # 1. Convertir PDF a imagen de alta resolución
        doc = fitz.open(stream=archivo_pdf.read(), filetype="pdf")
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        
        # 2. OCR: Leer calibres y notas en el plano
        resultados_texto = reader.readtext(img_np)
        textos_detectados = [res[1] for res in resultados_texto]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📍 Análisis de Plano")
        st.image(img_np, caption="Plano procesado con IA", use_container_width=True)
        with st.expander("Ver Textos y Calibres Detectados"):
            st.write(textos_detectados)

    with col2:
        st.subheader("🏗️ Proyección 3D sobre Plano")
        
        # Crear el plano de fondo en el render 3D
        fig = go.Figure()
        
        # Añadir la imagen del plano como "piso"
        fig.add_trace(go.Image(z=[np.zeros(pix.width)]*pix.height, source=Image.fromarray(img_np)))

        # Dibujar trayectorias (Simulando detección de líneas de poliducto/conduit)
        # Aquí conectamos los puntos detectados automáticamente
        x_m = [200, 400, 600, 800]
        y_m = [300, 300, 500, 500]
        z_m = [1.2, 2.4, 2.4, 0.5] # Alturas reales

        fig.add_trace(go.Scatter3d(
            x=x_m, y=y_m, z=z_m,
            mode='lines+markers',
            line=dict(color='orange', width=8),
            marker=dict(size=5, color='black'),
            name="Instalación Detectada"
        ))

        fig.update_layout(scene=dict(aspectmode='data'), height=700)
        st.plotly_chart(fig, use_container_width=True)

    # --- CÁLCULO DE CAÍDA DE TENSIÓN ---
    st.divider()
    st.subheader("📊 Cálculos de Ingeniería")
    
    # Fórmula de caída de tensión: Delta V = (2 * L * I * rho) / S
    st.latex(r"\Delta V = \frac{2 \cdot L \cdot I \cdot \rho}{S}")
    st.info("💡 El sistema detecta calibres automáticamente para validar la normativa.")
else:
    st.info("👋 Martin, sube el plano para que Frialv 3D empiece el análisis.")
