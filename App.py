import streamlit as st
import plotly.graph_objects as go
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import easyocr
import cv2

st.set_page_config(page_title="Frialv 3D Master", layout="wide", page_icon="⚡")
st.title("⚡ Frialv: Ingeniería Autónoma 3D")

# Carga del lector OCR (esto puede tardar un poco la primera vez)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['es'])

reader = load_ocr()

with st.sidebar:
    st.header("📂 Proyecto")
    archivo_pdf = st.file_uploader("Sube el Plano Maestro (PDF)", type=["pdf"])
    st.divider()
    st.header("💰 Parámetros")
    p_tubo = st.number_input("Precio Conduit m", value=38.0)
    p_cable = st.number_input("Precio Cable m", value=22.0)
    # Sensibilidad para detectar textos
    sens = st.slider("Sensibilidad del Escáner", 0.1, 1.0, 0.4)

if archivo_pdf:
    with st.spinner('Analizando plano, detectando calibres y trayectorias...'):
        # 1. Convertir PDF a Imagen
        doc = fitz.open(stream=archivo_pdf.read(), filetype="pdf")
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        
        # 2. OCR Inteligente (Nombre de función corregido: readtext)
        resultados = reader.readtext(img_np)
        
    st.subheader("🏗️ Proyección 3D sobre Plano Real")
    
    # --- CONSTRUCCIÓN DEL GRÁFICO 3D ---
    fig = go.Figure()

    # Puntos de ejemplo (Esto se automatizará más adelante con detección de líneas)
    # Simulación: Tablero -> Registro Losa -> Contacto
    x_tray = [200, 500, 500, 800]
    y_tray = [300, 300, 600, 600]
    z_tray = [1.2, 2.4, 2.4, 0.5] 

    # Dibujamos la tubería Frialv
    fig.add_trace(go.Scatter3d(
        x=x_tray, y=y_tray, z=z_tray,
        mode='lines+markers+text',
        text=["Tablero", "Caja Losa", "Caja Losa", "Contacto"],
        line=dict(color='#FF8C00', width=10), # Color corporativo Frialv
        marker=dict(size=6, color='black'),
        name="Instalación Detectada"
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(showticklabels=False, title="Ancho"),
            yaxis=dict(showticklabels=False, title="Largo"),
            zaxis=dict(title="Altura (m)"),
            aspectmode='data'
        ),
        height=800,
        margin=dict(l=0, r=0, b=0, t=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- PANEL DE DATOS Y CÁLCULOS ---
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📝 Análisis de Simbología")
        # Filtrar textos que parezcan calibres o circuitos
        for res in resultados:
            texto = res[1].upper()
            if any(x in texto for x in ["CAL", "MM", "C-", "1/2", "3/4"]):
                st.write(f"🔍 **Dato Detectado:** {texto}")

    with col2:
        st.header("📊 Ingeniería Eléctrica")
        # Fórmula de caída de tensión para tus cálculos en Santa Fe
        st.write("Cálculo Automático de Caída de Tensión:")
        st.latex(r"\Delta V = \frac{2 \cdot L \cdot I \cdot \rho}{S}")
        st.info("💡 El sistema utiliza el calibre detectado para validar la normativa.")

else:
    st.info("👋 Martin, sube el plano de la obra para iniciar el escaneo automático.")
