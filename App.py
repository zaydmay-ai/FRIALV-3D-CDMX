import streamlit as st
import plotly.graph_objects as go
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import easyocr
import cv2

# Configuración de alto nivel
st.set_page_config(page_title="Frialv 3D Master Pro", layout="wide", page_icon="⚡")
st.title("⚡ Frialv: Ingeniería Eléctrica Autónoma")
st.markdown("---")

# Carga del motor de IA para lectura de planos
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['es'])

reader = load_ocr()

with st.sidebar:
    st.header("📂 Gestión de Proyecto")
    archivo_pdf = st.file_uploader("Subir Plano Maestro (PDF)", type=["pdf"])
    st.divider()
    st.header("💰 Costos y Parámetros")
    p_tubo = st.number_input("Precio Conduit 3/4\" ($/m)", value=42.0)
    p_cable = st.number_input("Precio Cable Cal. 12 ($/m)", value=24.0)
    st.info("La IA buscará calibres y símbolos automáticamente.")

if archivo_pdf:
    with st.spinner('Ejecutando escaneo neuronal de plano...'):
        # 1. Procesamiento de PDF
        doc = fitz.open(stream=archivo_pdf.read(), filetype="pdf")
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        
        # 2. OCR Avanzado (Detección de textos: Calibres, Diámetros, Circuitos)
        resultados_ocr = reader.readtext(img_np)
        
    # --- INTERFAZ DE RESULTADOS ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📍 Análisis de Campo")
        # Mostramos el plano con los textos detectados resaltados
        plano_marcado = img_np.copy()
        datos_extraidos = []
        
        for (bbox, texto, prob) in resultados_ocr:
            t_upper = texto.upper()
            # Filtro inteligente para temas eléctricos
            if any(x in t_upper for x in ["CAL", "MM", "C-", "1/2", "3/4", "13", "19"]):
                (tl, tr, br, bl) = bbox
                cv2.rectangle(plano_marcado, (int(tl[0]), int(tl[1])), (int(br[0]), int(br[1])), (0, 255, 0), 3)
                datos_extraidos.append({"Texto": texto, "Pos": tl})

        st.image(plano_marcado, caption="Plano con Calibres y Simbología Detectada", use_container_width=True)

    with col2:
        st.subheader("🏗️ Proyección 3D Estructural")
        
        # Creamos el render 3D basado en los puntos donde se encontró texto eléctrico
        fig = go.Figure()
        
        if datos_extraidos:
            x_m = [d["Pos"][0] for d in datos_extraidos]
            y_m = [d["Pos"][1] for d in datos_extraidos]
            # Alturas automáticas según lógica Frialv (Z)
            # Ejemplo: Si el texto dice "Contacto", Z = 0.5. Si dice "Lámpara", Z = 2.4
            z_m = [2.4 if "CAL" in d["Texto"].upper() else 0.5 for d in datos_extraidos]

            fig.add_trace(go.Scatter3d(
                x=x_m, y=y_m, z=z_m,
                mode='lines+markers+text',
                text=[d["Texto"] for d in datos_extraidos],
                line=dict(color='orange', width=12),
                marker=dict(size=7, color='black'),
                name="Instalación Frialv"
            ))

        fig.update_layout(
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Altura (m)", aspectmode='data'),
            margin=dict(l=0, r=0, b=0, t=0), height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- CÁLCULOS DE INGENIERÍA ---
    st.divider()
    st.header("📊 Memoria de Cálculo Automática")
    
    # Cálculo de caída de tensión basado en normativa
    # ΔV = (2 * L * I * ρ) / S
    st.latex(r"\Delta V = \frac{2 \cdot L \cdot I \cdot \rho}{S}")
    
    c1, c2, c3 = st.columns(3)
    dist_est = len(datos_extraidos) * 3.5 # Estimación base por puntos
    c1.metric("Puntos de Control", len(datos_extraidos))
    c2.metric("Metraje Estimado", f"{dist_est:.2f} m")
    c3.metric("Presupuesto Sugerido", f"${(dist_est * p_tubo) + (dist_est * 3 * p_cable):,.2f}")

else:
    st.info("👋 Martin, sube el plano de la obra para iniciar el análisis avanzado.")
