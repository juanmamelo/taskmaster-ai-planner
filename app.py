import streamlit as st
import requests
import os
import json
from datetime import datetime

# Configuración
st.set_page_config(page_title="TaskMaster IA", page_icon="🧠")

# Función para consultar a Gemini
def consultar_gemini(prompt_usuario):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": st.secrets["GEMINI_API_KEY"]}
    data = {
        "contents": [{
            "parts": [{"text": prompt_usuario}]
        }]
    }

    response = requests.post(url, headers=headers, params=params, json=data)

    if response.status_code == 200:
        respuesta = response.json()
        return respuesta["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"

# Función para guardar historial
def guardar_en_historial(tareas, resultado):
    historial = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tareas": tareas,
        "resultado": resultado
    }
    if not os.path.exists("historial.json"):
        with open("historial.json", "w") as f:
            json.dump([historial], f, indent=4)
    else:
        with open("historial.json", "r+") as f:
            data = json.load(f)
            data.append(historial)
            f.seek(0)
            json.dump(data, f, indent=4)

# Interfaz principal
st.title("🧠 TaskMaster IA")
st.write("Tu asistente inteligente para organizar tareas diarias con inteligencia artificial.")

st.subheader("📝 Ingresá tus tareas")
tareas_input = st.text_area("Escribí tus tareas, una por línea")

if st.button("🔍 Analizar y Priorizar"):
    if tareas_input.strip():
        prompt = f"""
        Actuá como un organizador inteligente de tareas. A partir de la siguiente lista, priorizá cada tarea considerando urgencia, importancia y contexto general. 
        Además, sugerí un horario ideal para realizar cada una.

        Lista de tareas:
        {tareas_input}
        """
        with st.spinner("Consultando IA..."):
            resultado = consultar_gemini(prompt)
            guardar_en_historial(tareas_input, resultado)
            st.success("✅ Resultado:")
            st.markdown(resultado)
    else:
        st.warning("Por favor, ingresá al menos una tarea.")

# Historial
with st.expander("🕘 Historial de consultas"):
    if os.path.exists("historial.json"):
        with open("historial.json", "r") as f:
            historial = json.load(f)
            for item in reversed(historial[-5:]):
                st.write(f"📅 {item['fecha']}")
                st.markdown(f"**Tareas:**\n{item['tareas']}")
                st.markdown(f"**Resultado:**\n{item['resultado']}")
                st.markdown("---")
    else:
        st.info("Todavía no hay historial guardado.")

# Cómo funciona
with st.expander("ℹ️ ¿Cómo funciona TaskMaster IA?"):
    st.markdown("""
    Esta aplicación utiliza inteligencia artificial (modelo Gemini de Google) para analizar tus tareas diarias, priorizarlas y sugerirte horarios ideales. 
    Solo ingresá tus tareas, hacé clic en *Analizar y Priorizar*, y recibí recomendaciones inteligentes.
    """)
