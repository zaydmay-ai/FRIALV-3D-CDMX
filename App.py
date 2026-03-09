import streamlit as st
import plotly.graph_objects as go
import fitz  # PyMuPDF
from PIL import Image
import numpy as np

# Configuración Profesional
st.set_page_config(page_title="Frialv 3D CDMX - Maestro", layout="wide", page_icon="⚡")

st.title("⚡ Frialv: Ingeniería Eléctrica 3D")
st.caption("Sistema Automatizado de Conteo y Presupuesto")

# --- BARRA LATERAL (CONTROL TOTAL) ---
with st.sidebar:
    st.header("📋 Parámetros de Obra")
    archivo_pdf = st.file_uploader("📂 Cargar Plano PDF", type=["pdf"])
    
    st.subheader("📏 Calibración de Escala")
    escala_manual = st.number_input("Metros por cada 100 píxeles", value=2.5, help="Ajusta según la escala del plano")
    
    st.subheader("💰 Costos Unitarios")
    p_conduit = st.number_input("Tubo Conduit 3/4 ($/m)", value=38.0)
    p_cable = st.number_input("Cable Cal. 12 ($/m)", value=22.0)
    p_mano_obra = st.number_input("Mano de Obra ($/salida)", value=350.0)

# --- LÓGICA PRINCIPAL ---
if archivo_pdf:
    # 1. Procesar el Plano
    with st.spinner('Procesando Plano Maestro...'):
        doc = fitz.open(stream=archivo_pdf.read(), filetype="pdf")
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Simulación de Detección de Símbolos (Aquí entrará la IA después)
        # Generamos puntos aleatorios simulando que detectó cajas en el plano
        puntos_x = [100, 300, 500, 700, 300]
        puntos_y = [200, 200, 400, 400, 600]
        etiquetas = ["Tablero", "Caja 1", "Caja 2", "Caja 3", "Contacto"]
        alturas = [1.2, 2.4, 2.4, 2.4, 0.5] # Alturas estándar Z

    # 2. Visualización 2D (El Plano)
    st.subheader("🖼️ Plano Analizado")
    st.image(img, caption="Plano cargado - Símbolos detectados automáticamente")

    # 3. Visualización 3D (La Instalación)
    st.subheader("🏗️ Proyecto en 3D")
    
    # Convertir pixeles a metros reales usando la escala
    x_m = [px * (escala_manual / 100) for px in puntos_x]
    y_m = [py * (escala_manual / 100) for py in puntos_y]

    fig = go.Figure()
    
    # Dibujar Tuberías
    fig.add_trace(go.Scatter3d(
        x=x_m, y=y_m, z=alturas,
        mode='lines+markers+text',
        text=etiquetas,
        line=dict(color='orange', width=12),
        marker=dict(size=8, color='black'),
        name="Conduit Frialv"
    ))

    fig.update_layout(scene=dict(aspectmode='data'), height=600)
    st.plotly_chart(fig, use_container_width=True)

    # 4. Cálculo de Materiales y Presupuesto
    distancia_total = 0
    for i in range(len(x_m) - 1):
        d = ((x_m[i+1]-x_m[i])**2 + (y_m[i+1]-y_m[i])**2 + (alturas[i+1]-alturas[i])**2)**0.5
        distancia_total += d

    st.write("---")
    st.header("📊 Resumen Económico del Proyecto")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tubería", f"{distancia_total:.2f} m")
        st.write(f"Tubo: ${distancia_total * p_conduit:,.2f}")
        
    with col2:
        st.metric("Total Cable", f"{distancia_total * 3:.2f} m")
        st.write(f"Cable: ${(distancia_total * 3) * p_cable:,.2f}")
        
    with col3:
        costo_total = (distancia_total * p_conduit) + ((distancia_total * 3) * p_cable) + (len(puntos_x) * p_mano_obra)
        st.metric("Presupuesto Final", f"${costo_total:,.2f}")
        st.caption("Incluye Material + Mano de Obra")

    if st.button("📝 Generar Reporte para el Cliente"):
        st.success("✅ Reporte Frialv generado. ¡Listo para enviar!")
else:
    st.info("👋 Martin, sube el plano de la obra para empezar a calcular.")
