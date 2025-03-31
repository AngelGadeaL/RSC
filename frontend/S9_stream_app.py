import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

#--------------
#Animación
#--------------
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Si no deseas usar la animación, comenta o elimina estas líneas
# lottie_ai = load_lottiefile("anim.json")

# Interfaz de Streamlit
st.set_page_config(
    page_title="FuturaTech | Buscador Inteligente",
    layout="centered"
)

# Elimina o comenta estas líneas para no mostrar el título ni la animación
# st.title("🔍Futuratech - Buscador Inteligente de Documentos Internos")
# st_lottie(lottie_ai, height=200)
# st.markdown("Consulta libremente documentos internos para apoyar tus decisiones estratégicas.")

# --- NUEVA SECCIÓN ---
# Agregamos el combo para seleccionar el proyecto
proyecto = st.selectbox("Naturtech Indique la Opcion a seleccionar", options=["Sugerencias", "Ideas", "Reclamos", ""])

# Se modifica el label del text_input usando el contenido de la variable 'proyecto'
consulta = st.text_input(
    f"Escribe una Consulta de un Recurso asociado con {proyecto}:",
    placeholder="Firewall del Area Perimetral para FrontEnd"
)
# ---------------------

k = st.slider("Número de resultados", min_value=1, max_value=5, value=3)

if st.button("Buscar"):
    if not consulta.strip():
        st.warning("Por favor, ingresa una consulta válida.")
    else:
        # Despliega el proyecto seleccionado
        st.write(f"Opcion seleccionada: {proyecto}")
        with st.spinner(f"Buscando los items asociados: {proyecto}..."):
            try:
                # Concatenar el contenido de 'consulta' con el de 'proyecto'
                consulta = consulta + " " + proyecto
                # Imprimir el contenido final de 'consulta'
                st.write("Consulta final:", consulta)
                
                url = f"http://127.0.0.1:8000/buscar/?query={consulta}&k={k}"
                response = requests.get(url)
                data = response.json()

                st.subheader("📄Resultados encontrados:")
                for i, r in enumerate(data["resultados"]):
                    st.markdown(f"""
                        **{i+1}.** *{r['documento']}*
                        _Similitud:_ **{r['similitud']:.2f}**
                    """)
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")