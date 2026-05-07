import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title='Tablero Inteligente', layout="wide")

# =========================
# ESTILO VISUAL NUEVO
# =========================
st.markdown("""
<style>

/* Fondo animado llamativo */
.main {
    background: linear-gradient(135deg, #ff00cc, #00c6ff, #7b2ff7, #f107a3);
    background-size: 400% 400%;
    animation: bg 10s ease infinite;
}

@keyframes bg {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Título */
h1 {
    text-align: center;
    color: white;
    font-size: 48px;
    font-weight: 900;
    text-shadow: 0px 0px 20px rgba(0,0,0,0.6);
}

/* Texto general */
p, label, span, div {
    color: white !important;
    font-weight: 500;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e1b4b);
}

/* Botones */
.stButton>button {
    background: linear-gradient(90deg, #00f5ff, #ff00cc);
    color: white;
    font-weight: bold;
    border-radius: 0px;
    height: 50px;
    border: none;
    transition: 0.2s;
}

.stButton>button:hover {
    transform: scale(1.05);
    filter: brightness(1.2);
}

/* Canvas */
canvas {
    border: 2px solid white;
    border-radius: 0px;
}

/* Input */
input {
    background-color: rgba(255,255,255,0.1) !important;
    color: white !important;
}

/* Subtítulos */
h2, h3 {
    color: #ffffff !important;
    text-shadow: 0px 0px 10px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)

# =========================
# UI PRINCIPAL
# =========================
st.title('🎨 Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Esta app interpreta bocetos y genera descripciones con IA.")

st.subheader("✏️ Dibuja tu boceto y analiza la imagen")

# Canvas
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

# API KEY
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=api_key)

analyze_button = st.button("🚀 Analizar imagen", type="secondary")

# =========================
# ANÁLISIS
# =========================
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        def encode_image_to_base64(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

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
# ALERTA API KEY
# =========================
if not api_key:
    st.warning("Por favor ingresa tu API key.")
