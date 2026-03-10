import streamlit as st
import plotly.graph_objects as go
import fitz
from PIL import Image
import numpy as np
import ezdxf
import io
from openai import OpenAI

st.set_page_config(page_title="Frialv 3D BIM Élite", layout="wide", page_icon="⚡")
st.title("⚡ Frialv: Visualización BIM de Élite")

# Conector con la IA (Secrets)
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("🔑 Falta llave en Secrets")
    st.stop()

with st.sidebar:
    st.header("🏢 Control de Obra")
    archivo = st.file_uploader("Subir Plano (DXF o PDF)", type=["pdf", "dxf"])
    st.divider()
    modo_noche = st.toggle("🌙 Activar Modo Noche", value=True)
    z_losa = st.slider("Altura de Losa (m)", 2.0, 3.5, 2.4)
    z_contacto = st.slider("Altura Contactos (m)", 0.3, 0.6, 0.5)

if archivo:
    with st.spinner('Optimizando y generando render 3D...'):
        # 1. Procesar Plano y REDUCIR TAMAÑO (Downsampling)
        doc = fitz.open(stream=archivo.read(), filetype="pdf" if archivo.name.endswith('pdf') else "dxf")
        pagina = doc.load_page(0)
        # Bajamos el zoom a 1.2 para que no pese 200MB
        pix = pagina.get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Redimensionar si la imagen sigue siendo gigante (Max 1200px)
        if img.width > 1200:
            img.thumbnail((1200, 1200))

        # 2. Puntos de Ingeniería
        puntos = [
            {"t": "Tablero", "x": 100, "y": 100, "z": 1.2, "luz": False},
            {"t": "Caja Losa", "x": 100, "y": 400, "z": z_losa, "luz": True},
            {"t": "Caja Losa", "x": 600, "y": 400, "z": z_losa, "luz": True},
            {"t": "Contacto", "x": 800, "y": 400, "z": z_contacto, "luz": False}
        ]

    # --- RENDER 3D BIM OPTIMIZADO ---
    fig = go.Figure()

    # Tubería Frialv
    x, y, z = [p['x'] for p in puntos], [p['y'] for p in puntos], [p['z'] for p in puntos]
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines+markers',
        line=dict(color='#FF5F1F', width=12),
        marker=dict(size=4, color='white'),
        name="Tubería"
    ))

    # Luces
    if modo_noche:
        for p in puntos:
            if p['luz']:
                fig.add_trace(go.Scatter3d(
                    x=[p['x']], y=[p['y']], z=[p['z']],
                    mode='markers',
                    marker=dict(size=20, color='yellow', opacity=0.3),
                    showlegend=False
                ))

    # Piso (Plano optimizado)
    img_array = np.array(img.convert('L'))
    if modo_noche: img_array = 255 - img_array 
    
    # Usamos una malla más ligera para el Surface
    fig.add_trace(go.Surface(
        z=np.zeros(img_array.shape),
        surfacecolor=img_array,
        colorscale='Greys' if not modo_noche else 'Ice',
        showscale=False,
        opacity=0.6
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            zaxis=dict(title="Z (m)", range=[0, 4]),
            aspectmode='data'
        ),
        paper_bgcolor="black" if modo_noche else "white",
        margin=dict(l=0, r=0, b=0, t=0), height=750
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- RESULTADOS ---
    st.divider()
    dist = sum(np.sqrt((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2 + (z[i]-z[i-1])**2) for i in range(1, len(x))) / 10
    st.metric("Metraje Real de Poliducto", f"{dist:.2f} m")

else:
    st.info("👋 Sube el plano para iniciar.")
