import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Visualización de Niveles de Sonido",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
        .stApp {
            background-color: white;
            color: black;
        }
        h1, h2, h3, h4, h5, h6, p {
            color: black;
        }
        .subheader {
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.title("**Investigación del comportamiento del ruido en un ambiente universitario**")

# --- IMAGEN PRINCIPAL ---
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.image("UAMAZC.jpg", use_container_width=True)

# --- MENÚ DE NAVEGACIÓN ---
seccion_activa = st.query_params.get("seccion", "Introducción")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Introducción", use_container_width=True):
        st.query_params["seccion"] = "Introducción"
        seccion_activa = "Introducción"
with col2:
    if st.button("Objetivo", use_container_width=True):
        st.query_params["seccion"] = "Objetivo"
        seccion_activa = "Objetivo"
with col3:
    if st.button("Desarrollo", use_container_width=True):
        st.query_params["seccion"] = "Desarrollo"
        seccion_activa = "Desarrollo"
with col4:
    if st.button("Resultados", use_container_width=True):
        st.query_params["seccion"] = "Resultados"
        seccion_activa = "Resultados"

st.markdown('<p class="subheader">Aplicación de análisis acústico para investigación técnica</p>', unsafe_allow_html=True)

# --- SECCIONES ---
if seccion_activa == "Introducción":
    st.markdown("### Introducción")
    st.write("""
    El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros.
    """)

elif seccion_activa == "Objetivo":
    st.markdown("### Objetivo")
    st.write("""
    Visualizar el comportamiento del sonido en una área específica, utilizando sensores y gráficos.
    """)

elif seccion_activa == "Desarrollo":
    st.markdown("### Desarrollo del prototipo")
    st.write("*En esta parte veremos el desarrollo del prototipo y su construcción.*")

elif seccion_activa == "Resultados":
    st.markdown("### Resultados")

    uploaded_file = "mediciones_1.csv"
    try:
        df = pd.read_csv(uploaded_file, skiprows=3)
        df['_time'] = pd.to_datetime(df['_time'], utc=True, errors='coerce')
        tiempo_min, tiempo_max = df['_time'].min(), df['_time'].max()

        # Filtros
        fecha = st.sidebar.date_input("Fecha", value=tiempo_min.date(),
                                      min_value=tiempo_min.date(), max_value=tiempo_max.date())
        hora_inicio = st.sidebar.time_input("Hora de inicio", value=pd.to_datetime('00:00').time())
        hora_fin = st.sidebar.time_input("Hora de fin", value=pd.to_datetime('23:59').time())

        fecha_inicio = pd.to_datetime(f"{fecha} {hora_inicio}").tz_localize('UTC')
        fecha_fin = pd.to_datetime(f"{fecha} {hora_fin}").tz_localize('UTC')
        df_filtrado = df[(df['_time'] >= fecha_inicio) & (df['_time'] <= fecha_fin)]

        # Nodo
        nodos_disponibles = sorted(df_filtrado["nodo"].unique())
        if nodos_disponibles:
            nodo_seleccionado = st.sidebar.radio("Selecciona el nodo:", options=nodos_disponibles, horizontal=True)
            df_filtrado = df_filtrado[df_filtrado["nodo"] == nodo_seleccionado]
        else:
            st.sidebar.info("No hay nodos disponibles en el rango seleccionado.")
            df_filtrado = pd.DataFrame()

        # Mostrar gráfico si hay datos
        if not df_filtrado.empty:
            st.success(f"Se encontraron {len(df_filtrado)} registros para el nodo {nodo_seleccionado}.")
            # Aquí colocas el mapa y el gráfico por nodo...
        else:
            st.warning("No hay datos para el nodo seleccionado.")
    except Exception as e:
        st.error(f"Error al procesar: {e}")
