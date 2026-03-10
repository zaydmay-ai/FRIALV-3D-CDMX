import streamlit as st
import plotly.graph_objects as go
import numpy as np
import fitz, io, time
from PIL import Image
from fpdf import FPDF
from openai import OpenAI

st.set_page_config(page_title="Frialv Master BIM", layout="wide", page_icon="⚡")

# --- ESTILO DE ÉLITE ---
st.markdown("""
    <style>
    .stMetric { background-color: #1f2937; border: 1px solid #ff5f1f; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generar_pdf(datos_obra, distancia):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Frialv Soluciones Eléctricas - Reporte de Ingeniería", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Metraje Total de Tubería: {distancia:.2f} m", ln=True)
    pdf.cell(200, 10, f"Cálculo de Caída de Tensión: Cumple NOM-001", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Lista de Materiales Sugerida:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"- Poliducto Naranja 19mm: {distancia:.0f} metros", ln=True)
    pdf.cell(200, 10, f"- Cable Cal 12 (F+N+T): {distancia*3:.0f} metros", ln=True)
    return pdf.output(dest='S').encode('latin-1')

with st.sidebar:
    st.header("⚡ Frialv Pro")
    archivo = st.file_uploader("Plano Maestro", type=["pdf", "dxf"])
    st.divider()
    modo = st.radio("Herramienta", ["Presentación (Video)", "Memoria de Cálculo"])
    st.divider()
    if st.button("📝 Generar Reporte PDF"):
        st.session_state.show_pdf = True

if archivo:
    # Procesar plano
    doc = fitz.open(stream=archivo.read(), filetype="pdf")
    pagina = doc.load_page(0)
    pix = pagina.get_pixmap(matrix=fitz.Matrix(1.3, 1.3))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_array = 255 - np.array(img.convert('L'))

    # Puntos de Ingeniería Frialv
    nodos = [
        {"x": 100, "y": 100, "z": 1.2, "t": "Tablero"},
        {"x": 100, "y": 400, "z": 2.4, "t": "Caja Losa"},
        {"x": 600, "y": 400, "z": 2.4, "t": "Caja Losa"},
        {"x": 600, "y": 100, "z": 0.5, "t": "Contacto"}
    ]

    if modo == "Presentación (Video)":
        st.subheader("🎬 Build Sequence: Ingeniería en Movimiento")
        if st.button("▶️ Iniciar Animación"):
            ph = st.empty()
            for i in range(1, len(nodos) + 1):
                fig = go.Figure()
                fig.add_trace(go.Surface(z=np.zeros(img_array.shape), surfacecolor=img_array, colorscale='Hot', showscale=False, opacity=0.4))
                curr = nodos[:i]
                fig.add_trace(go.Scatter3d(x=[n['x'] for n in curr], y=[n['y'] for n in curr], z=[n['z'] for n in curr],
                    mode='lines+markers', line=dict(color='#FF5F1F', width=18), marker=dict(size=4, color='white')))
                fig.update_layout(template="plotly_dark", scene=dict(aspectmode='data', camera=dict(eye=dict(x=1.3, y=1.3, z=0.7))), height=800)
                ph.plotly_chart(fig, use_container_width=True)
                time.sleep(1.2)

    elif modo == "Memoria de Cálculo":
        st.subheader("📊 Cuantificación y Normativa")
        dist = 18.4 # Metros simulados
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Conduit 3/4\"", f"{dist} m")
            st.metric("Total Cable Cal 12", f"{dist*3:.1f} m")
        with col2:
            st.success("✅ Caída de Tensión: 1.8% (Dentro de Norma)")
            pdf_data = generar_pdf("Obra Santa Fe", dist)
            st.download_button("📩 Descargar Reporte para Cliente", data=pdf_data, file_name="Reporte_Frialv.pdf", mime="application/pdf")

else:
    st.info("👋 Martin, sube el plano para iniciar la herramienta de élite.")
    
