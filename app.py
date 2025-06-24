import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

st.set_page_config(page_title="Visualización de Niveles de Sonido", layout="wide")

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
        .menu-button {
            background-color: #004080;
            color: white;
            padding: 10px 25px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            border: none;
        }
        .menu-button:hover {
            background-color: #0059b3;
        }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO E IMAGEN PRINCIPAL ---
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.title("**Investigación del comportamiento del ruido en un ambiente universitario**")

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
    with st.container():
        st.markdown("### Introducción")
        st.markdown("""
        <div style='text-align: justify;'>
        El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros para medir los niveles sonoros.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 1.1 Principio de funcionamiento")
        st.markdown("**1. Captación del sonido:** [...]")
        st.latex(r'''
        \text{Nivel de presión sonora (dB)} = 20 \cdot \log_{10} \left(\frac{P}{P_0}\right)
        ''')
        st.markdown("- \( P \): presión sonora medida  \n- \( P_0 = 20\,\mu\text{Pa} \): presión sonora de referencia")

        st.markdown("### 1.2 Diagrama del dispositivo.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("Diagrama.png", use_container_width=True)

elif seccion_activa == "Objetivo":
    st.markdown("### Objetivo")
    st.markdown("* Visualizar el comportamiento del sonido en una área específica, utilizando sensores y gráficos.")

elif seccion_activa == "Desarrollo":
    st.markdown("### Desarrollo del prototipo")
    st.markdown("* En esta parte veremos el desarrollo del prototipo y su construcción.")

elif seccion_activa == "Resultados":
    st.markdown("### Resultados")

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("Parámetros de entrada")
        uploaded_file = "mediciones_1.csv"

    try:
        df = pd.read_csv(uploaded_file, skiprows=3)
        columnas_requeridas = ['_time', 'nodo', '_value']
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"El CSV debe contener las columnas: {columnas_requeridas}")
        else:
            df['_time'] = pd.to_datetime(df['_time'], utc=True, errors='coerce')
            df.dropna(subset=['_time'], inplace=True)

            tiempo_min = df['_time'].min()
            tiempo_max = df['_time'].max()

            with st.sidebar:
                fecha = st.date_input("Fecha", value=tiempo_min.date(), min_value=tiempo_min.date(), max_value=tiempo_max.date())
                hora_inicio = st.time_input("Hora de inicio", value=pd.to_datetime('00:00').time())
                hora_fin = st.time_input("Hora de fin", value=pd.to_datetime('23:59').time())

            fecha_inicio = pd.to_datetime(f"{fecha} {hora_inicio}").tz_localize('UTC')
            fecha_fin = pd.to_datetime(f"{fecha} {hora_fin}").tz_localize('UTC')

            df_filtrado = df[(df['_time'] >= fecha_inicio) & (df['_time'] <= fecha_fin)]

            # --- Selección de nodos ---
            nodos_disponibles = sorted(df_filtrado["nodo"].unique())
            with st.sidebar:
                nodos_seleccionados = st.multiselect(
                    "Selecciona los nodos a visualizar",
                    options=nodos_disponibles,
                    default=nodos_disponibles
                )
            df_filtrado = df_filtrado[df_filtrado["nodo"].isin(nodos_seleccionados)]

            if df_filtrado.empty:
                st.warning("No hay datos para los parámetros seleccionados.")
            else:
                st.success(f"Se encontraron {len(df_filtrado)} registros.")
                tab1, tab2 = st.tabs(["📊 Mapa de calor", "📈 Gráficos por nodo"])

                with tab1:
                    st.markdown("Mapa de calor de niveles de sonido:")
                    X = df_filtrado['nodo'].astype(float).values
                    fecha_base = pd.Timestamp(fecha).tz_localize('UTC')
                    tiempos_segundos = (df_filtrado['_time'] - fecha_base).dt.total_seconds().values
                    Z = df_filtrado['_value'].astype(float).values

                    x_unique = np.unique(X)
                    y_unique = np.unique(tiempos_segundos)
                    X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
                    Z_grid = griddata((X, tiempos_segundos), Z, (X_grid, Y_grid), method='linear')

                    fig, ax = plt.subplots(figsize=(10, 6))
                    c = ax.pcolormesh(X_grid, Y_grid, Z_grid, shading='auto', cmap='jet')
                    plt.colorbar(c, ax=ax, label='Nivel de sonido (dB)')

                    yticks = ax.get_yticks()
                    ylabels = [(fecha_base + pd.Timedelta(seconds=sec)).strftime('%H:%M') for sec in yticks]
                    ax.set_yticks(yticks)
                    ax.set_yticklabels(ylabels)

                    ax.set_xlabel("Nodos")
                    ax.set_ylabel("Hora (HH:MM)")
                    ax.set_title("Mapa de niveles de sonido", fontsize=14)
                    st.pyplot(fig)

                with tab2:
                    st.markdown("#### Evolución temporal por nodo")
                    for nodo in sorted(df_filtrado["nodo"].unique()):
                        st.subheader(f"Nodo {nodo}")
                        datos_nodo = df_filtrado[df_filtrado["nodo"] == nodo]
                        st.line_chart(datos_nodo.set_index("_time")["_value"], height=200, use_container_width=True)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")

