import streamlit as st
import openai
from datetime import datetime
import os
import json

# Cargar API Key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
st.write("Tu asistente inteligente para organizar tareas diarias.")

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
        with st.spinner("Analizando tareas..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=700
            )
            resultado = response.choices[0].message["content"]
            guardar_en_historial(tareas_input, resultado)
            st.success("✅ Resultado:")
            st.markdown(resultado)
    else:
        st.warning("Ingresá al menos una tarea.")

with st.expander("🕘 Historial de consultas"):
    if os.path.exists("historial.json"):
        with open("historial.json", "r") as f:
            historial = json.load(f)
            for item in reversed(historial[-5:]):  # mostrar últimos 5
                st.write(f"📅 {item['fecha']}")
                st.markdown(f"**Tareas:**\n{item['tareas']}")
                st.markdown(f"**Resultado:**\n{item['resultado']}")
                st.markdown("---")
    else:
        st.info("Todavía no hay historial.")

with st.expander("ℹ️ ¿Cómo funciona TaskMaster IA?"):
    st.markdown("""
    Esta app analiza tus tareas usando inteligencia artificial (GPT-3.5) y te sugiere un orden óptimo de ejecución.
    También guarda tu historial para que puedas revisar tus últimos análisis.
    """)
