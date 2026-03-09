import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuración de la página para celular
st.set_page_config(page_title="Frialv 3D CDMX", layout="centered")

st.title("⚡ Frialv: Diseño de Instalaciones 3D")
st.subheader("CDMX - Soluciones Eléctricas")

# --- MENÚ LATERAL ---
with st.sidebar:
    st.header("Configuración")
    precio_tubo = st.number_input("Precio/m Tubo 3/4\"", value=35.0)
    precio_cable = st.number_input("Precio/m Cable Cal. 12", value=22.0)
    st.divider()
    archivo_pdf = st.file_uploader("📂 Subir Plano PDF", type=["pdf"])

# --- VISUALIZADOR 3D ---
st.write("### 🏗️ Modelo de Instalación")

# Ejemplo: Conexión de Tablero a Caja y Contacto
# Coordenadas (X, Y, Z) en metros
x = [0, 2, 2, 4]
y = [0, 0, 3, 3]
z = [1.2, 2.4, 2.4, 0.5] # Alturas reales: 1.2 tablero, 2.4 losa, 0.5 contacto

fig = go.Figure()

# Línea de tubería (Color naranja Frialv)
fig.add_trace(go.Scatter3d(
    x=x, y=y, z=z,
    mode='lines+markers+text',
    text=["Tablero", "Caja Losa", "Bajada", "Contacto"],
    line=dict(color='#FF8C00', width=10),
    marker=dict(size=5, color='black'),
    name="Conduit"
))

fig.update_layout(
    margin=dict(l=0, r=0, b=0, t=0),
    scene=dict(xaxis_title='X (m)', yaxis_title='Y (m)', zaxis_title='Z (m)'),
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# --- CÁLCULOS ---
distancia = 12.5 # Esto se calculará del plano después
st.divider()
st.write("### 📊 Presupuesto Estimado")
col1, col2 = st.columns(2)
col1.metric("Metros Tubería", f"{distancia} m")
total = (distancia * precio_tubo) + (distancia * 3 * precio_cable)
col2.metric("Inversión Material", f"${total:,.2f} MXN")

if st.button("📤 Enviar Reporte a WhatsApp"):
    st.success("Reporte listo. (Aquí conectaremos con tu número)")
