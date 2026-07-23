import os
import streamlit as st
from PIL import Image
import google.generativeai as genai

# ---------------------------------------------------------
# Configuración de la página y Estilo Premium
# ---------------------------------------------------------
st.set_page_config(
    page_title="LEXIO — Auditoría Inteligente de Facturas",
    page_icon="⚖️",
    layout="centered"
)

# Inyección de CSS para diseño personalizado (Dark Mode Premium)
st.markdown("""
    <style>
    /* Importar tipografía moderna si fuera posible, o usar sans-serif del sistema */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0e14; /* Fondo ultra oscuro profesional */
        color: #e4e6eb;
    }

    /* Estilo del título principal */
    .main-title {
        font-weight: 700;
        font-size: 3rem !important;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    /* Estilo del subtítulo */
    .sub-title {
        font-weight: 400;
        font-size: 1.1rem;
        color: #b0b3b8;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Contenedor de subida de archivos */
    [data-testid="stFileUploader"] {
        background-color: #1c1f26;
        border: 2px dashed #3a3d42;
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Botón Principal (Analizar) */
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

    /* Tarjetas de resultados */
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
        display: flex;
        align-items: center;
    }

    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Conexión con la API de Gemini (Estable)
# ---------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Error de configuración: Falta la clave API de Gemini.")
    st.stop()

# Configurar API forzando la versión v1 de producción
genai.configure(api_key=api_key, client_options={"api_version": "v1"})


# ---------------------------------------------------------
# Interfaz de Usuario - Cabecera Estilizada
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">LEXIO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Defensa Inteligente del Consumidor contra cobros indebidos y letra chica.</p>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# Sección 1: Subida de Factura
# ---------------------------------------------------------
with st.container():
    st.markdown("### 1️⃣ Subí tu factura")
    st.caption("Saca una foto clara o subí el archivo (JPG, PNG)")
    
    uploaded_file = st.file_uploader(
        "Arrastrá tu archivo aquí", 
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

# ---------------------------------------------------------
# Sección 2: Análisis y Resultados
# ---------------------------------------------------------
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Mostrar vista previa estilizada de la imagen
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image(image, caption="Vista previa del documento", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Botón de acción principal
    analyze_btn = st.button("🔍 Iniciar Auditoría Legal con Lexio")
    
    if analyze_btn:
        with st.spinner("Lexio está escaneando ítems, impuestos y letra chica..."):
            try:
                # Prompt mejorado para estructura Markdown clara
                prompt = """
                Actúa como un auditor experto en consumo y derecho del consumidor en Argentina (Ley 24.240).
                Analiza profesionalmente la imagen de la factura adjunta y genera un informe estructurado en Markdown.
                
                Usa títulos claros (##) y viñetas. Estructura la respuesta EXACTAMENTE así:

                ## 📋 Diagnóstico Rápido
                *   **Empresa / Servicio:** [Nombre]
                *   **Monto Total:** [Monto]
                *   **Puntos Críticos:** [Analiza ítems sospechosos, aumentos no notificados, cargos administrativos fijos o servicios no solicitados en viñetas claras]

                ## ⚖️ Evaluación Legal
                [Redacta aquí una evaluación legal profesional y concisa de 2 o 3 oraciones, indicando si hay fundamento para un reclamo basado en la Ley 24.240 u otras normativas argentinas aplicables]

                ## 📨 Carta de Reclamo Formal
                [Redacta una carta/email de reclamo formal completa, lista para copiar y pegar]
                [Usa variables entre corchetes como [Nombre del Cliente], [Número de Cuenta]]
                [Cita los artículos legales relevantes con firmeza y profesionalismo]
                """
                
                # Nombre de versión estable garantizada
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([prompt, image])
                
                # Mostrar resultados con éxito estilizado
                st.balloons()
                st.success("¡Auditoría completada con éxito!")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Contenedor para mostrar la respuesta estructurada de Gemini
                with st.container():
                    st.markdown(response.text)
                
                st.markdown("---")
                # Tarjeta de "Siguientes Pasos"
                st.markdown(f"""
                    <div class="result-card">
                        <div class="card-header">💡 Siguientes Pasos</div>
                        <p>Copiá la <b>Carta de Reclamo Formal</b> generada arriba y enviala por mail a la casilla de Atención al Cliente o Legales de la empresa. ¡No olvides completar los datos entre corchetes!</p>
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Ocurrió un error inesperado durante el análisis: {e}")

# ---------------------------------------------------------
# Pie de página legal (Discreto y Profesional)
# ---------------------------------------------------------
st.markdown("<br><br><br><hr>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; color: #65676b; font-size: 0.85rem;'>
        ⚠️ <b>Descargo de responsabilidad:</b> Lexio es un asistente impulsado por Inteligencia Artificial para la autogestión de reclamos. 
        No presta asesoramiento jurídico profesional ni representación legal directa.
    </p>
""", unsafe_allow_html=True)
