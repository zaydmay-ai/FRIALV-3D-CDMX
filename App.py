import streamlit as st
import plotly.graph_objects as go
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="Frialv 3D CDMX - Pro", layout="wide", page_icon="⚡")
st.title("⚡ Frialv: Escáner de Planos Inteligente")

# --- MENÚ LATERAL ---
with st.sidebar:
    st.header("1. Carga de Archivos")
    archivo_pdf = st.file_uploader("📂 Sube el Plano (PDF)", type=["pdf"])
    archivo_simbolo = st.file_uploader("🎯 Sube el Símbolo a buscar (Imagen)", type=["png", "jpg", "jpeg"])
    
    st.divider()
    st.header("2. Costos y Escala")
    escala = st.number_input("Metros por cada 100px", value=2.0)
    p_tubo = st.number_input("Precio Tubo $/m", value=35.0)
    p_cable = st.number_input("Precio Cable $/m", value=22.0)

# --- PROCESAMIENTO ---
if archivo_pdf and archivo_simbolo:
    with st.spinner('Analizando plano...'):
        # Leer PDF
        doc = fitz.open(stream=archivo_pdf.read(), filetype="pdf")
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_plano = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        plano_cv = cv2.cvtColor(np.array(img_plano), cv2.COLOR_RGB2BGR)
        plano_gris = cv2.cvtColor(plano_cv, cv2.COLOR_BGR2GRAY)

        # Leer Símbolo
        img_simbolo = Image.open(archivo_simbolo)
        simbolo_cv = cv2.cvtColor(np.array(img_simbolo), cv2.COLOR_RGB2BGR)
        simbolo_gris = cv2.cvtColor(simbolo_cv, cv2.COLOR_BGR2GRAY)
        w, h = simbolo_gris.shape[::-1]

        # BUSCAR SÍMBOLOS (Detección IA)
        res = cv2.matchTemplate(plano_gris, simbolo_gris, cv2.TM_CCOEFF_NORMED)
        umbral = 0.7 
        loc = np.where(res >= umbral)
        
        puntos = []
        for pt in zip(*loc[::-1]):
            if not any(np.linalg.norm(np.array(pt) - np.array(p)) < 20 for p in puntos):
                puntos.append(pt)

        st.success(f"✅ ¡Se encontraron {len(puntos)} símbolos!")

        # --- MOSTRAR RESULTADOS ---
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📍 Plano Detectado")
            for pt in puntos:
                cv2.rectangle(plano_cv, pt, (pt[0] + w, pt[1] + h), (255, 140, 0), 4)
            st.image(plano_cv, channels="BGR", use_container_width=True)

        with c2:
            st.subheader("🏗️ Render 3D")
            x_m = [p[0] * (escala/100) for p in puntos]
            y_m = [p[1] * (escala/100) for p in puntos]
            z_m = [0.5] * len(puntos) # Altura contacto

            fig = go.Figure(data=[go.Scatter3d(
                x=x_m, y=y_m, z=z_m, mode='markers+lines',
                marker=dict(size=6, color='orange'),
                line=dict(color='orange', width=4)
            )])
            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)

        # --- PRESUPUESTO ---
        dist = 0
        if len(x_m) > 1:
            for i in range(len(x_m)-1):
                dist += np.sqrt((x_m[i+1]-x_m[i])**2 + (y_m[i+1]-y_m[i])**2)
        
        st.divider()
        st.subheader("📊 Resumen de Inversión")
        k1, k2, k3 = st.columns(3)
        k1.metric("Salidas", len(puntos))
        k2.metric("Tubería", f"{dist:.2f} m")
        total = (dist * p_tubo) + (dist * 3 * p_cable)
        k3.metric("Total Material", f"${total:,.2f}")
else:
    st.warning("⚠️ Sube el PDF y una captura del símbolo (ej. el dibujo de un contacto) para activar el sistema.")
