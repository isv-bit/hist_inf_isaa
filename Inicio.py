import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title='Tablero Inteligente', layout="wide")

# =========================
# ESTILO VISUAL
# =========================
st.markdown("""
<style>

/* =========================
   FONDO VIVO NEÓN
========================= */
.main {
    background: linear-gradient(135deg, #ff0080, #7928ca, #00c6ff, #00ff87);
    background-size: 400% 400%;
    animation: fondoAnimado 8s ease infinite;
}

@keyframes fondoAnimado {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* =========================
   TÍTULO
========================= */
h1 {
    text-align: center;
    color: #ffffff;
    font-size: 48px;
    font-weight: 900;
    text-shadow: 0 0 25px #00fff7;
}

/* =========================
   SUBTÍTULOS
========================= */
h2, h3 {
    color: #00fff7 !important;
    text-shadow: 0 0 10px rgba(0,0,0,0.6);
}

/* =========================
   TEXTO GENERAL
========================= */
p, label, span, div {
    color: #ffffff !important;
    font-weight: 500;
}

/* =========================
   SIDEBAR
========================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0f2a, #1a0b3d);
}

/* =========================
   BOTONES
========================= */
.stButton>button {
    background: linear-gradient(90deg, #ff00cc, #00fff7);
    color: white;
    font-weight: bold;
    border-radius: 0px;
    height: 50px;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.05);
    filter: brightness(1.3);
}

/* =========================
   INPUTS
========================= */
input {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
}

/* =========================
   CANVAS
========================= */
canvas {
    border: 2px solid #00fff7;
}

</style>
""", unsafe_allow_html=True)

# =========================
# APP
# =========================
st.title('🎨 Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Esta app interpreta bocetos y los analiza con IA.")

st.subheader("✏️ Dibuja tu boceto en el panel")

# =========================
# CANVAS
# =========================
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Ancho de línea', 1, 30, 5)
stroke_color = "#000000"
bg_color = '#FFFFFF'

canvas_result = st_canvas(
    fill_color="rgba(255, 0, 200, 0.2)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# =========================
# API KEY
# =========================
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=api_key)

analyze_button = st.button("🚀 Analizar imagen", type="secondary")

# =========================
# CODIFICACIÓN
# =========================
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# =========================
# ANÁLISIS IA
# =========================
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):

        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")

        prompt_text = "Describe in spanish briefly the image"

        try:
            message_placeholder = st.empty()

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                            },
                        },
                    ],
                }],
                max_tokens=500,
            )

            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)

            st.session_state.full_response = full_response
            st.session_state.analysis_done = True

        except Exception as e:
            st.error(f"Error: {e}")

# =========================
# HISTORIA
# =========================
if st.session_state.get("analysis_done"):
    st.divider()
    st.subheader("📚 Crear historia infantil")

    if st.button("✨ Generar historia"):
        with st.spinner("Creando historia..."):

            story_prompt = f"Crea una historia infantil basada en: {st.session_state.full_response}"

            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=500,
            )

            st.markdown("### 📖 Historia generada")
            st.write(story_response.choices[0].message.content)

# =========================
# ALERTA
# =========================
if not api_key:
    st.warning("Por favor ingresa tu API key.")
