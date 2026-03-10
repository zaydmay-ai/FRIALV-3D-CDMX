import streamlit as st
import plotly.graph_objects as go
import fitz
from PIL import Image
import numpy as np
import ezdxf
import io
from openai import OpenAI

st.set_page_config(page_title="Frialv 3D Night Mode", layout="wide", page_icon="⚡")
st.title("⚡ Frialv: Visualización BIM de Élite")

# Conector con la IA
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

with st.sidebar:
    st.header("🏢 Control de Obra")
    archivo = st.file_uploader("Subir Plano (DXF o PDF)", type=["pdf", "dxf"])
    st.divider()
    modo_noche = st.toggle("🌙 Activar Modo Noche", value=True)
    st.header("📐 Ajustes Z")
    z_losa = st.slider("Altura de Losa (m)", 2.0, 3.5, 2.4)
    z_contacto = st.slider("Altura Contactos (m)", 0.3, 0.6, 0.5)

if archivo:
    with st.spinner('Generando render de alta definición...'):
        # 1. Convertir plano a textura
        doc = fitz.open(stream=archivo.read(), filetype="pdf" if archivo.name.endswith('pdf') else "dxf")
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Puntos detectados (Lógica Frialv Z)
        puntos = [
            {"t": "Tablero", "x": 150, "y": 150, "z": 1.2, "luz": False},
            {"t": "Caja Losa", "x": 150, "y": 450, "z": z_losa, "luz": True},
            {"t": "Caja Losa", "x": 650, "y": 450, "z": z_losa, "luz": True},
            {"t": "Contacto", "x": 850, "y": 450, "z": z_contacto, "luz": False}
        ]

    # --- RENDER 3D BIM ---
    fig = go.Figure()

    # Trazado de tubería Naranja Neón
    x, y, z = [p['x'] for p in puntos], [p['y'] for p in puntos], [p['z'] for p in puntos]
    
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines+markers',
        line=dict(color='#FF5F1F', width=18), # Naranja Neón grueso
        marker=dict(size=4, color='white'),
        name="Tubería Frialv"
    ))

    # --- EFECTO MODO NOCHE (Luminarias) ---
    if modo_noche:
        for p in puntos:
            if p['luz']:
                # Añadir un "brillo" alrededor de los focos
                fig.add_trace(go.Scatter3d(
                    x=[p['x']], y=[p['y']], z=[p['z']],
                    mode='markers',
                    marker=dict(size=25, color='yellow', opacity=0.3),
                    name="Luz Encendida",
                    showlegend=False
                ))

    # El "Piso" con el plano
    img_array = np.array(img.convert('L'))
    # Si es modo noche, invertimos el plano para que se vea oscuro
    if modo_noche: img_array = 255 - img_array 
    
    fig.add_trace(go.Surface(
        z=np.zeros(img_array.shape),
        surfacecolor=img_array,
        colorscale='Greys' if not modo_noche else 'Ice',
        showscale=False,
        opacity=0.6,
        name="Plano de Obra"
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(title="Z (m)", range=[0, 4], backgroundcolor="black" if modo_noche else "white"),
            aspectmode='data'
        ),
        paper_bgcolor="black" if modo_noche else "white",
        margin=dict(l=0, r=0, b=0, t=0),
        height=850
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- PANEL DE RESULTADOS ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    dist = sum(np.sqrt((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2 + (z[i]-z[i-1])**2) for i in range(1, len(x))) / 15
    
    c1.metric("Poliducto Naranja", f"{dist:.2f} m")
    c2.metric("Salidas Totales", len(puntos))
    c3.metric("Potencia Est.", f"{len([p for p in puntos if p['luz']])*60}W")

else:
    st.info("👋 Martin, sube el plano para activar el Modo Noche de Frialv.")
