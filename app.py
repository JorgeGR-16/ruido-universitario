import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from scipy.interpolate import griddata

st.set_page_config(page_title="Visualización de Niveles de Sonido", layout="wide")

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
        .stApp {
            background-color: white;
            color: black;
        }
        h1 {
            margin-top: 0.5rem !important;  /* controla espacio arriba */
            margin-bottom: 0.5rem !important; /* controla espacio abajo */
            color: black;
        }
        h2 {
            font-size: 16px !important;
            color: red !important;
            margin-top: 0.25rem !important;
            margin-bottom: 0.25rem !important;
        }
        h3, h4, h5, h6 {
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

# --- TÍTULO GENERAL ---
#col1, col2, col3 = st.columns([1, 4, 1])
#with col2:
st.title("**Investigación del comportamiento del ruido en un ambiente universitario**")

# ----------------------------------------------------- IMAGEN PRINCIPAL----------------------------------------------------------------#
##col1, col2, col3 = st.columns([1, 4, 1])
##with col2:
##    st.image("UAMAZC.jpg", use_container_width=True)

# ----------------------------------------------------- MENÚ DE NAVEGACIÓN -------------------------------------------------------------#
if "seccion" not in st.session_state:
    st.session_state.seccion = "Introducción"
    
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Introducción", use_container_width=True):
        st.session_state.seccion = "Introducción"
with col2:
    if st.button("Objetivo", use_container_width=True):
        st.session_state.seccion = "Objetivo"
with col3:
    if st.button("Desarrollo", use_container_width=True):
        st.session_state.seccion = "Desarrollo"
with col4:
    if st.button("Resultados", use_container_width=True):
        st.session_state.seccion = "Resultados"

seccion_activa = st.session_state.seccion
st.markdown('<p class="subheader">Aplicación de análisis acústico para investigación técnica</p>', unsafe_allow_html=True)

# --------------------------------------------------------SECCIONES ------------------------------------------------------------------#
#_________________________________________________________Introduccion________________________________________________________________#
if seccion_activa == "Introducción":
    st.markdown("### Introducción")
    st.markdown("""
    <div style='text-align: justify;'>
     El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros para medir los niveles sonoros.
     El ruido es un factor ambiental que puede influir negativamente en la calidad de vida, el rendimiento académico y la salud de estudiantes y personal universitario. Por ello, es fundamental identificar y cuantificar las fuentes y niveles de ruido presentes para poder plantear estrategias de mitigación efectivas.
     A través de esta investigación, se pretende obtener datos precisos que permitan evaluar el impacto acústico en el entorno universitario y promover un ambiente más adecuado para el estudio y desarrollo académico.
     La red está conformada por varios sonómetros basados en el microcontrolador LoRa32, un micrófono digital INMP441 y una batería recargable, todo alojado en una carcasa impresa en 3D.
     La red utiliza una topología de estrella en la que los sonómetros se comunican directamente con un gateway central, también basado en un LoRa32. Este gateway actúa como puente entre los sensores y una computadora central, permitiendo la transferencia de datos de ruido en tiempo real, mediante enlace USB o el protocolo MQTT.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1.1 Principio de funcionamiento")
    st.markdown("""
    <div style='text-align: justify;'>
    **1. Captación del sonido:**  
    El sonido ambiente es captado por un micrófono de condensador, el cual detecta las variaciones de presión del aire generadas por las ondas sonoras.

    **2. Conversión eléctrica:**  
    Estas variaciones se transforman en una señal eléctrica proporcional a la presión acústica.

    **3. Procesamiento de la señal:**  
    La señal eléctrica es amplificada y procesada mediante un circuito electrónico o un microcontrolador. Durante este proceso, se aplica una ponderación frecuencial (normalmente del tipo A), que ajusta la medición de acuerdo con la sensibilidad del oído humano.

    **4. Cálculo y visualización en decibelios (dB):**  
    Finalmente, el sistema calcula el nivel de presión sonora utilizando la fórmula logarítmica:
    </div>
    """, unsafe_allow_html=True)

    st.latex(r'''
        \text{Nivel de presión sonora (dB)} = 20 \cdot \log_{10} \left(\frac{P}{P_0}\right)
    ''')

    st.markdown("""
        Donde:  
        - \( P \): presión sonora medida  
        - \( P_0 = 20\,\mu\text{Pa} \): presión sonora de referencia en el aire
    """, unsafe_allow_html=True)

    st.markdown("### 1.2 Diagrama del dispositivo.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Diagrama.png", use_container_width=True)
# --------------------------------------------------------SECCIONES ------------------------------------------------------------------#
#_________________________________________________________Objetivo________________________________________________________________#
elif seccion_activa == "Objetivo":
    st.markdown("### Objetivo")
    st.markdown("* Visualizar el comportamiento del sonido en una área específica, utilizando sensores y gráficos...")
# --------------------------------------------------------SECCIONES ------------------------------------------------------------------#
#_________________________________________________________Desarrollo________________________________________________________________#
elif seccion_activa == "Desarrollo":
    st.markdown("### Desarrollo del prototipo")
    st.header("*En esta parte veremos el desarrollo del prototipo y su construcción.*")
# --------------------------------------------------------SECCIONES ------------------------------------------------------------------#
#_________________________________________________________Resultados________________________________________________________________#
elif seccion_activa == "Resultados":
    st.markdown("### Resultados")
    

    with st.sidebar:
        st.header("Parámetros de entrada")
        uploaded_file = "mediciones_1.csv"

        try:
            df = pd.read_csv(uploaded_file, skiprows=3)
            columnas_requeridas = ['_time', 'nodo', '_value']
            if not all(col in df.columns for col in columnas_requeridas):
                st.error("El archivo no contiene las columnas necesarias.")
                df_filtrado = pd.DataFrame()
            else:
                df['_time'] = pd.to_datetime(df['_time'], format='%Y-%m-%dT%H:%M:%S.%fZ', utc=True, errors='coerce')
                tiempo_min = df['_time'].min()
                tiempo_max = df['_time'].max()

                fecha = st.date_input("Fecha", value=tiempo_min.date(), min_value=tiempo_min.date(), max_value=tiempo_max.date())
                hora_inicio = st.time_input("Hora de inicio", value=pd.to_datetime('00:00').time())
                hora_fin = st.time_input("Hora de fin", value=pd.to_datetime('23:59').time())

                nodos_disponibles = sorted(df["nodo"].unique())
                nodos_seleccionados = st.multiselect(
                    "Selecciona los nodos que deseas visualizar:",
                    options=nodos_disponibles,
                    default=nodos_disponibles
                )

                fecha_inicio = pd.to_datetime(f"{fecha} {hora_inicio}").tz_localize('UTC')
                fecha_fin = pd.to_datetime(f"{fecha} {hora_fin}").tz_localize('UTC')

                df_filtrado = df[
                    (df['_time'] >= fecha_inicio) &
                    (df['_time'] <= fecha_fin) &
                    (df['nodo'].isin(nodos_seleccionados))
                ]

        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            df_filtrado = pd.DataFrame()

    if not df_filtrado.empty:
        st.success(f"Se encontraron {len(df_filtrado)} registros.")

        with st.expander("🔧 Parámetros de visualización (haz clic para mostrar/ocultar)", expanded=True):
            st.info("Puedes modificar la **fecha, hora y nodos** desde la **barra lateral izquierda** 📊.")
            
            # --- Análisis estadístico básico por nodo ---
        

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Mapa de Sonido", "📈 Gráficos por nodo", "🧩 Comparación general", "📊 Análisis estadístico"])

        with tab1:
            st.markdown("Mapa de niveles de sonido:")
            X = df_filtrado['nodo'].astype(int).values
            fecha_base = pd.Timestamp(fecha).tz_localize('UTC')
            tiempos_segundos = (df_filtrado['_time'] - fecha_base).dt.total_seconds().values
            Z = df_filtrado['_value'].astype(float).values

            x_unique = np.unique(X)
            y_unique = np.unique(tiempos_segundos)
            X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
            Z_grid = griddata((X, tiempos_segundos), Z, (X_grid, Y_grid), method='linear')
            Z_grid = np.nan_to_num(Z_grid, nan=np.nanmin(Z_grid))

            fig, ax = plt.subplots(figsize=(10, 6))
            yticks = np.linspace(0, len(y_unique) - 1, num=10, dtype=int)
            yticklabels = [pd.to_datetime(y_unique[i], unit='s').strftime('%H:%M') for i in yticks]

            sb.heatmap(Z_grid, xticklabels=x_unique, yticklabels=False, cmap='jet', ax=ax)
            ax.invert_yaxis()
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticklabels, rotation=0)
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

        with tab3:
            st.markdown("### Comparación general de nodos en un solo gráfico")
            df_pivot = df_filtrado.pivot(index='_time', columns='nodo', values='_value').sort_index()
            st.line_chart(df_pivot, height=300, use_container_width=True)

        with tab4:
            st.markdown("### Análisis estadístico básico por nodo")
    
            resumen_estadistico = df_filtrado.groupby("nodo")["_value"].agg(
                Minimo="min",
                Maximo="max",
                Media="mean",
                Mediana="median",
                Desviación_Estd="std",
                Conteo="count"
            ).round(2)
    
            st.dataframe(resumen_estadistico, use_container_width=True)
            st.markdown("### Gráfico de valores maximos por nodo")
            st.bar_chart(resumen_estadistico["Maximo"])
    else:
        st.warning("No hay datos para los parámetros seleccionados.")
