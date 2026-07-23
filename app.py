import os
import streamlit as st
from PIL import Image
from google import genai

# ---------------------------------------------------------
# Configuración de la página y Estilo Premium (Dark Mode)
# ---------------------------------------------------------
st.set_page_config(
    page_title="LEXIO — Auditoría Inteligente de Facturas",
    page_icon="⚖️",
    layout="centered"
)

# Inyección de CSS para diseño personalizado
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0e14;
        color: #e4e6eb;
    }

    .main-title {
        font-weight: 700;
        font-size: 3rem !important;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-title {
        font-weight: 400;
        font-size: 1.1rem;
        color: #b0b3b8;
        text-align: center;
        margin-bottom: 2rem;
    }

    [data-testid="stFileUploader"] {
        background-color: #1c1f26;
        border: 2px dashed #3a3d42;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white !important;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        border-radius: 10px;
        height: 3.5rem;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }

    .result-card {
        background-color: #1c1f26;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #2d3139;
    }
    
    .card-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1rem;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Conexión con el Cliente Oficial de GenAI
# ---------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Error de configuración: Falta la clave API de Gemini en los Secretos.")
    st.stop()

# Inicializar cliente oficial
client = genai.Client(api_key=api_key)

# ---------------------------------------------------------
# Interfaz de Usuario
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">LEXIO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Defensa Inteligente del Consumidor contra cobros indebidos y letra chica.</p>', unsafe_allow_html=True)

st.markdown("---")

with st.container():
    st.markdown("### 1️⃣ Subí tu factura")
    st.caption("Saca una foto clara o subí el archivo (JPG, PNG)")
    
    uploaded_file = st.file_uploader(
        "Arrastrá tu archivo aquí", 
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image(image, caption="Vista previa del documento", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    analyze_btn = st.button("🔍 Iniciar Auditoría Legal con Lexio")
    
    if analyze_btn:
        with st.spinner("Lexio está escaneando ítems, impuestos y letra chica..."):
            
            prompt = """
            Actúa como un auditor experto en consumo y derecho del consumidor en Argentina (Ley 24.240).
            Analiza profesionalmente la imagen de la factura adjunta y genera un informe estructurado en Markdown.
            
            Usa títulos claros (##) y viñetas. Estructura la respuesta EXACTAMENTE así:

            ## 📋 Diagnóstico Rápido
            * **Empresa / Servicio:** [Nombre]
            * **Monto Total:** [Monto]
            * **Puntos Críticos:** [Analiza ítems sospechosos, aumentos no notificados, cargos administrativos fijos o servicios no solicitados en viñetas claras]

            ## ⚖️ Evaluación Legal
            [Redacta aquí una evaluación legal profesional y concisa de 2 o 3 oraciones, indicando si hay fundamento para un reclamo basado en la Ley 24.240 u otras normativas argentinas aplicables]

            ## 📨 Carta de Reclamo Formal
            [Redacta una carta/email de reclamo formal completa, lista para copiar y pegar]
            [Usa variables entre corchetes como [Nombre del Cliente], [Número de Cuenta]]
            [Cita los artículos legales relevantes con firmeza y profesionalismo]
            """

            # Modelos estándar oficiales
            modelos_disponibles = [
                'gemini-2.0-flash',
                'gemini-2.5-flash',
                'gemini-1.5-flash'
            ]
            
            response = None
            ultimo_error = None

            # Bucle anti-fallos
            for mod in modelos_disponibles:
                try:
                    res = client.models.generate_content(
                        model=mod,
                        contents=[prompt, image]
                    )
                    if res and res.text:
                        response = res
                        break
                except Exception as e:
                    ultimo_error = e
                    continue

            if response:
                st.balloons()
                st.success("¡Auditoría completada con éxito!")
                st.markdown("<br>", unsafe_allow_html=True)
                
                with st.container():
                    st.markdown(response.text)
                
                st.markdown("---")
                st.markdown("""
                    <div class="result-card">
                        <div class="card-header">💡 Siguientes Pasos</div>
                        <p>Copiá la <b>Carta de Reclamo Formal</b> generada arriba y enviala por mail a la casilla de Atención al Cliente o Legales de la empresa. ¡No olvides completar los datos entre corchetes!</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Ocurrió un problema de conexión con la API: {ultimo_error}")

# Pie de página legal
st.markdown("<br><br><br><hr>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; color: #65676b; font-size: 0.85rem;'>
        ⚠️ <b>Descargo de responsabilidad:</b> Lexio es un asistente impulsado por Inteligencia Artificial para la autogestión de reclamos. 
        No presta asesoramiento jurídico profesional ni representación legal directa.
    </p>
""", unsafe_allow_html=True)
