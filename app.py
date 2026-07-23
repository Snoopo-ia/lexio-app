import os
import streamlit as st
from PIL import Image
from google import genai

# ---------------------------------------------------------
# Configuración de la página (Estilo Lexio)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Lexio — IA para tus Facturas",
    page_icon="🔍",
    layout="centered"
)

st.markdown("""
    <style>
    .main {
        background-color: #0d1117;
    }
    stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Conexión con la API de Gemini
# ---------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Falta configurar la GEMINI_API_KEY en los Secretos del sistema.")
    st.stop()

# Inicializar el cliente oficial
client = genai.Client(api_key=api_key)

# ---------------------------------------------------------
# Interfaz de Usuario
# ---------------------------------------------------------
st.title("LEXIO")
st.caption("Inteligencia Artificial contra cobros indebidos y letra chica.")

st.markdown("---")

st.subheader("1. Subí tu factura o comprobante")
uploaded_file = st.file_uploader(
    "Saca una foto o subí el archivo (JPG, PNG)", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Factura cargada", use_container_width=True)
    
    if st.button("🔍 Analizar Factura con Lexio"):
        with st.spinner("Lexio está auditando los ítems y la letra chica..."):
            try:
                prompt = """
                Actúa como un auditor experto en consumo y derecho del consumidor en Argentina (Ley 24.240).
                Analiza la imagen de la factura adjunta y realiza lo siguiente:
                
                1. DIAGNÓSTICO RÁPIDO:
                   - Empresa / Servicio.
                   - Monto Total.
                   - Identifica si hay ítems sospechosos, aumentos no notificados, cargos administrativos fijos o servicios no solicitados.
                
                2. EVALUACIÓN LEGAL:
                   - Indica en 2 oraciones si hay fundamento para un reclamo según la Ley de Defensa del Consumidor (Ley 24.240) o resoluciones aplicables.
                
                3. CARTA DE RECLAMO FORMAL:
                   - Redacta una carta/email de reclamo formal lista para enviar a la empresa.
                   - Incluye variables entre corchetes como [Nombre del Cliente], [Número de Usuario/Cuenta].
                   - Cita los artículos legales relevantes de forma firme y profesional.
                
                Muestra la respuesta organizada con títulos claros en Markdown.
                """
                
                # Modelo actualizado oficialmente
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=[image, prompt]
                )
                
                st.success("¡Análisis completado con éxito!")
                st.markdown("---")
                st.markdown(response.text)
                
                st.markdown("---")
                st.info("💡 **¿Qué hacer ahora?** Copiá la carta de reclamo generada arriba y enviala por mail a la casilla de Atención al Cliente o Legales de la empresa.")
                
            except Exception as e:
                st.error(f"Ocurrió un error al procesar la imagen: {e}")

# Pie de página legal
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("⚠️ **Descargo de responsabilidad:** Lexio es un asistente impulsado por Inteligencia Artificial para la autogestión de reclamos. No presta asesoramiento jurídico profesional ni representación legal directa.")
