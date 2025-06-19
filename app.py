import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Visualización de Niveles de Sonido", layout="wide")

# --- ESTILO CSS PARA DISEÑO LIMPIO ---
st.markdown("""
    <style>
        .stApp {
            background-color: #f9f9f9;
        }
        h1 {
            color: #1a1a1a;
            font-size: 2.5em;
        }
        .subheader {
            font-size: 1.2em;
            color: #555;
            margin-top: -15px;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGO Y TÍTULO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo_universidad.png", use_container_width=True)

st.title(" Investigación del comportamiento del ruido en un ambiente universitario")
st.markdown('<p class="subheader">Aplicación de análisis acústico para investigación técnica</p>', unsafe_allow_html=True)

# --- MENÚ DE NAVEGACIÓN ---
seccion = st.radio(
    "Selecciona una sección",
    ["Introducción", "Objetivo", "Resultados"],
    horizontal=True
)

st.markdown("""---""")

# --- SECCIONES ---
if seccion == "Introducción":
    with st.container():
        st.markdown("### Introducción")
        st.markdown("""
        El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros para medir los niveles sonoros.
        El ruido es un factor ambiental que puede influir negativamente en la calidad de vida, el rendimiento académico y la salud de estudiantes y personal universitario. Por ello, es fundamental identificar y cuantificar las fuentes y niveles de ruido presentes para poder plantear estrategias de mitigación efectivas.
        A través de esta investigación, se pretende obtener datos precisos que permitan evaluar el impacto acústico en el entorno universitario y promover un ambiente más adecuado para el estudio y desarrollo académico.
        La red está conformada por varios sonómetros basados en el microcontrolador `LoRa32`, un micrófono digital `INMP441` y una batería recargable, todo alojado en una carcasa impresa en 3D.
        La red utiliza una topología de estrella en la que los sonómetros se comunican directamente con un gateway central, también basado en un `LoRa32`. Este gateway actúa como puente entre los sensores y una computadora central, permitiendo la transferencia de datos de ruido en tiempo real, mediante enlace USB o el protocolo MQTT.
        """)

        st.markdown("### 1.1 Principio de funcionamiento")

        st.markdown("""
        **1. Captación del sonido:**  
        El sonido ambiente es captado por un micrófono de condensador, el cual detecta las variaciones de presión del aire generadas por las ondas sonoras.

        **2. Conversión eléctrica:**  
        Estas variaciones se transforman en una señal eléctrica proporcional a la presión acústica.

        **3. Procesamiento de la señal:**  
        La señal eléctrica es amplificada y procesada mediante un circuito electrónico o un microcontrolador. Durante este proceso, se aplica una ponderación frecuencial (normalmente del tipo A), que ajusta la medición de acuerdo con la sensibilidad del oído humano.

        **4. Cálculo y visualización en decibelios (dB):**  
        Finalmente, el sistema calcula el nivel de presión sonora utilizando la fórmula logarítmica:
        """)

        st.latex(r'''
        \text{Nivel de presión sonora (dB)} = 20 \cdot \log_{10} \left(\frac{P}{P_0}\right)
        ''')

        st.markdown("""
        Donde:  
        - \( P \): presión sonora medida  
        - \( P_0 = 20\,\mu\text{Pa} \): presión sonora de referencia en el aire
        """)
        st.markdown("### 1.2 Diagrama del dispositivo.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
         st.image("Diagrama.png", use_container_width=True)
        


elif seccion == "Objetivo":
    with st.container():
        st.markdown("### Objetivo")
        st.markdown("""
        * Visualizar el comportamiento del sonido en una área específica, utilizando sensores y gráficos, para comprender con mayor claridad en qué zonas afectan más las alteraciones sonoras.
        """)

elif seccion == "Resultados":
    st.markdown("###  Resultados")

    # --- SIDEBAR DE PARÁMETROS ---
    with st.sidebar:
        st.header("Parámetros de entrada")
        uploaded_file = st.file_uploader("Sube archivo CSV", type="csv")

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, skiprows=3)

            columnas_requeridas = ['_time', 'nodo', '_value']
            if not all(col in df.columns for col in columnas_requeridas):
                st.error(f"El CSV debe contener las columnas: {columnas_requeridas}")
            else:
                df['_time'] = pd.to_datetime(df['_time'], format='%Y-%m-%dT%H:%M:%S.%fZ', utc=True, errors='coerce')

                if df['_time'].isna().any():
                    st.warning(" Algunas fechas no se pudieron convertir correctamente.")

                tiempo_min = df['_time'].min()
                tiempo_max = df['_time'].max()

                # --- FILTRO DE TIEMPO ---
                with st.expander(" Filtro temporal", expanded=True):
                    fecha = st.date_input("Fecha", value=tiempo_min.date(), min_value=tiempo_min.date(), max_value=tiempo_max.date())
                    hora_inicio = st.time_input("Hora de inicio", value=pd.to_datetime('00:00').time())
                    hora_fin = st.time_input("Hora de fin", value=pd.to_datetime('23:59').time())

                fecha_inicio = pd.to_datetime(f"{fecha} {hora_inicio}").tz_localize('UTC')
                fecha_fin = pd.to_datetime(f"{fecha} {hora_fin}").tz_localize('UTC')

                df_filtrado = df[(df['_time'] >= fecha_inicio) & (df['_time'] <= fecha_fin)]

                if df_filtrado.empty:
                    st.warning("No hay datos en el rango seleccionado.")
                else:
                    st.success(f"Se encontraron {len(df_filtrado)} registros.")

                    # --- PREPARACIÓN PARA GRÁFICO ---
                    X = df_filtrado['nodo'].astype(float).values
                    fecha_base = pd.Timestamp(fecha).tz_localize('UTC')
                    tiempos_segundos = (df_filtrado['_time'] - fecha_base).dt.total_seconds().values
                    Z = df_filtrado['_value'].astype(float).values

                    x_unique = np.unique(X)
                    y_unique = np.unique(tiempos_segundos)
                    X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
                    Z_grid = griddata((X, tiempos_segundos), Z, (X_grid, Y_grid), method='linear')

                    # --- GRÁFICO PROFESIONAL ---
                    fig, ax = plt.subplots(figsize=(10, 6))
                    cmap = plt.get_cmap('jet')
                    c = ax.pcolormesh(X_grid, Y_grid, Z_grid, shading='auto', cmap=cmap)
                    cb = plt.colorbar(c, ax=ax, label='Nivel de sonido (dB)')

                    yticks = ax.get_yticks()
                    ylabels = [(fecha_base + pd.Timedelta(seconds=sec)).strftime('%H:%M') for sec in yticks]
                    ax.set_yticks(yticks)
                    ax.set_yticklabels(ylabels)

                    ax.set_title("Mapa de niveles de sonido", fontsize=14)
                    ax.set_xlabel("Nodos")
                    ax.set_ylabel("Hora (HH:MM)")

                    st.markdown("A continuación se muestra un mapa de calor que representa los niveles de ruido captados por cada nodo a lo largo del tiempo.")
                    st.pyplot(fig)

                     # --- GRÁFICO DE LÍNEAS POR NODO ---
                    st.markdown("#### 📈 Evolución temporal por nodo")
                    for nodo in sorted(df_filtrado["nodo"].unique()):
                        st.subheader(f"Nodo {nodo}")
                        datos_nodo = df_filtrado[df_filtrado["nodo"] == nodo]
                        st.line_chart(datos_nodo.set_index("_time")["_value"], height=200, use_container_width=True)

                    # --- DESCARGA DEL GRÁFICO ---
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", dpi=300)
                    st.download_button("📥 Descargar gráfico como imagen", buf.getvalue(), "grafico_sonido.png", mime="image/png")

        except Exception as e:
            st.error(f" Error al procesar el archivo: {e}")
    else:
        st.info(" Esperando archivo CSV para comenzar.")
