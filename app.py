import streamlit as st
import requests
import json
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="TaskMaster IA", page_icon="🧠")

# --- Función para consultar a Gemini ---
def consultar_gemini(prompt_usuario):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
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

# --- Inicializar sesión ---
if "tareas" not in st.session_state:
    st.session_state.tareas = []
if "analisis_ejecutado" not in st.session_state:
    st.session_state.analisis_ejecutado = False
if "resultado_prioridad" not in st.session_state:
    st.session_state.resultado_prioridad = None

# --- Agregar nueva tarea ---
st.title("🧠 TaskMaster IA")
st.write("Organizá tu día con inteligencia artificial. Podés ingresar tareas con o sin horario, y la IA completará lo que falta.")

if st.button("➕ Agregar nueva tarea"):
    st.session_state.tareas.append({"descripcion": "", "inicio": "", "fin": ""})

# --- Mostrar tareas cargadas dinámicamente ---
st.subheader("📋 Lista de tareas")

for i, tarea in enumerate(st.session_state.tareas):
    col1, col2, col3 = st.columns([3, 1.5, 1.5])
    tarea["descripcion"] = col1.text_input(f"Tarea #{i+1}", tarea["descripcion"], key=f"desc_{i}")
    tarea["inicio"] = col2.text_input(f"Inicio", tarea["inicio"], key=f"ini_{i}", placeholder="hh:mm")
    tarea["fin"] = col3.text_input(f"Fin", tarea["fin"], key=f"fin_{i}", placeholder="hh:mm")

# --- Botón de análisis ---
if st.button("🧠 Organizar cronograma"):
    tareas_con_horario = []
    tareas_sin_horario = []

    for t in st.session_state.tareas:
        if t["descripcion"].strip() == "":
            continue
        if t["inicio"].strip() and t["fin"].strip():
            tareas_con_horario.append(t)
        else:
            tareas_sin_horario.append(t)

    prompt_horarios = "Tengo las siguientes tareas con horario definido:\n"
    for t in tareas_con_horario:
        prompt_horarios += f"- {t['descripcion']} de {t['inicio']} a {t['fin']}\n"

    if tareas_sin_horario:
        prompt_horarios += "\nY estas tareas sin horario:\n"
        for t in tareas_sin_horario:
            prompt_horarios += f"- {t['descripcion']}\n"
        prompt_horarios += """
        Por favor, asignales un horario a las tareas sin superponerlas con las ya definidas. 
        Devolvé el resultado solo como una lista con el siguiente formato:
        - Nombre de la tarea: HH:MM - HH:MM
        """

        resultado_cronograma = consultar_gemini(prompt_horarios)
    else:
        resultado_cronograma = "Todas las tareas tienen horario asignado."

    # --- Mostrar cronograma final ---
    st.subheader("🗓️ Cronograma sugerido")

    # Parsear las líneas tipo: - Tarea: hh:mm - hh:mm
    patron = r"-\s*(.+?):\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})"
    eventos = re.findall(patron, resultado_cronograma)

    # Crear DataFrame con tareas cargadas manualmente (con horario)
    manual_df = pd.DataFrame(tareas_con_horario)

    # Crear DataFrame con tareas sugeridas por la IA
    if eventos:
        ai_df = pd.DataFrame(eventos, columns=["descripcion", "inicio", "fin"])
    else:
        ai_df = pd.DataFrame(columns=["descripcion", "inicio", "fin"])

    # Combinar ambos
    df_cronograma = pd.concat([manual_df, ai_df], ignore_index=True)

    # Ordenar por horario de inicio
    df_cronograma = df_cronograma.sort_values("inicio")

    # Renombrar columnas para visualización
    df_cronograma.columns = ["Tarea", "Inicio", "Fin"]

    # Mostrar tabla
    st.dataframe(df_cronograma, hide_index=True, use_container_width=True)


    # --- También pedir análisis y prioridad ---
    todas_las_tareas = "\n".join([f"- {t['descripcion']}" for t in st.session_state.tareas])
    prompt_prioridad = f"""
    Sos un asistente de productividad. Para cada tarea listada, devolvé una prioridad (Alta, Media o Baja) y una breve justificación. 
    Formato de salida estricto por tarea:

    Tarea: <nombre>
    Prioridad: <Alta/Media/Baja>
    Justificación: <explicación>

    Tareas a analizar:
    {todas_las_tareas}
    """
    st.session_state.resultado_prioridad = consultar_gemini(prompt_prioridad)
    st.session_state.analisis_ejecutado = True

# --- Mostrar prioridades coloreadas SOLO si se ejecutó el análisis ---
if st.session_state.analisis_ejecutado:
    st.subheader("📌 Análisis y prioridades con colores")

    def colorear_bloques_por_tarea(texto):
        bloques = texto.strip().split("\n\n")
        for bloque in bloques:
            bloque_lower = bloque.lower()
            if "prioridad: alta" in bloque_lower:
                color = "#FFCCCC"
            elif "prioridad: media" in bloque_lower:
                color = "#FFF2CC"
            elif "prioridad: baja" in bloque_lower:
                color = "#CCFFCC"
            else:
                continue  # ignorar bloques que no contienen tareas válidas

            st.markdown(
                f"<div style='background-color: {color}; color: black; padding: 10px; border-radius: 8px; margin-bottom: 8px;'>{bloque}</div>",
                unsafe_allow_html=True
            )

    if st.session_state.resultado_prioridad:
        colorear_bloques_por_tarea(st.session_state.resultado_prioridad)
    else:
        st.info("No se pudo generar el análisis de prioridades.")
