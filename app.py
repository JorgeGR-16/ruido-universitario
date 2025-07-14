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
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
        header { 
            visibility: hidden;
        }
        .block-container {
            padding-top: 1rem;
        }
        h1 {
            margin-top: -2rem;
        }
        h2 {
            font-size: 16px !important;
            color: red !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        h3, h4, h5, h6 {
            color: black;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
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
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.title("**Investigación del comportamiento del ruido en un ambiente universitario**")

# --- IMAGEN PRINCIPAL ---
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.image("UAMAZC.jpg", use_container_width=True)

# --- MENÚ DE NAVEGACIÓN ---
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

# --- SECCIONES ---
if seccion_activa == "Introducción":
    st.markdown("### Introducción")
    st.markdown("""
    <div style='text-align: justify;'>
     El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros para medir los niveles sonoros.
     El ruido es un factor ambiental que puede influir negativamente en la calidad de vida, el rendimiento académico y la salud de estudiantes y personal universitario...
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1.1 Principio de funcionamiento")
    st.markdown("""
    <div style='text-align: justify;'>
    **1. Captación del sonido:**  
    El sonido ambiente es captado por un micrófono de condensador...
    </div>
    """, unsafe_allow_html=True)

    st.latex(r'''
        \text{Nivel de presión sonora (dB)} = 20 \cdot \log_{10} \left(\frac{P}{P_0}\right)
    ''')

    st.markdown("""
        Donde:  
        - \( P \): presión sonora medida  
        - \( P_0 = 20\,\mu\text{Pa} \): presión sonora de referencia
    """, unsafe_allow_html=True)

    st.markdown("### 1.2 Diagrama del dispositivo.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Diagrama.png", use_container_width=True)

elif seccion_activa == "Objetivo":
    st.markdown("### Objetivo")
    st.markdown("* Visualizar el comportamiento del sonido en una área específica...")

elif seccion_activa == "Desarrollo":
    st.markdown("### Desarrollo del prototipo")
    st.header("*En esta parte veremos el desarrollo del prototipo y su construcción.*")

elif seccion_activa == "Resultados":
    st.markdown("### Resultados")

    with st.sidebar:
        st.header("Parámetros de entrada")
        uploaded_file = "40nodos1.csv"  # Ruta fija

        try:
            df = pd.read_csv(uploaded_file, skiprows=3)
            columnas_requeridas = ['_time', 'nodo', '_value']

            if not all(col in df.columns for col in columnas_requeridas):
                st.error("El archivo no contiene las columnas necesarias.")
                df_filtrado = pd.DataFrame()
            else:
                df['_time'] = pd.to_datetime(df['_time'], utc=True, errors='coerce')

                if df['_time'].isna().all():
                    st.error("No se pudieron interpretar las fechas.")
                    df_filtrado = pd.DataFrame()
                else:
                    tiempo_min = df['_time'].min()
                    tiempo_max = df['_time'].max()

                    fecha = st.date_input("Fecha", value=tiempo_min.date(), min_value=tiempo_min.date(), max_value=tiempo_max.date())
                    hora_inicio = st.time_input("Hora de inicio", value=pd.to_datetime('00:00').time())
                    hora_fin = st.time_input("Hora de fin", value=pd.to_datetime('23:59').time())

                    nodos_disponibles = sorted(df["nodo"].unique())
                    nodos_seleccionados = st.multiselect(
                        "Selecciona los nodos:",
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
        df_filtrado = df_filtrado.copy()

        # Clasificar riesgo
        def clasificar_riesgo(db):
            if db < 85:
                return "Seguro"
            elif db < 100:
                return "Riesgo moderado"
            else:
                return "Peligroso"

        df_filtrado["riesgo"] = df_filtrado["_value"].apply(clasificar_riesgo)
        df_filtrado["hora"] = df_filtrado["_time"].dt.hour

        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Mapa de Sonido", 
            "📈 Gráficos por nodo", 
            "🧩 Comparación general", 
            "📊 Análisis estadístico",
            "🧨 Riesgo por hora"
        ])

        with tab1:
            st.markdown("### 💥 Mapa de niveles de sonido ")
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

            sb.heatmap(Z_grid, cmap='jet', xticklabels=x_unique, yticklabels=False, ax=ax, linewidths=0.3, linecolor='gray')
            ax.invert_yaxis()
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticklabels, rotation=0)
            ax.set_xlabel("Nodos")
            ax.set_ylabel("Hora (HH:MM)")
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
                Conteo="count"
            ).round(2)
            st.dataframe(resumen_estadistico, use_container_width=True)
            st.markdown("### Gráfico de valores máximos por nodo")
            st.bar_chart(resumen_estadistico["Maximo"])

        with tab5:
            st.markdown("### 🔊 **Rangos de niveles de sonido (dB SPL)**")

            st.markdown("""
            | Nivel (dB)     | Ejemplo                            | Efecto sobre la salud                                  |
            |----------------|-------------------------------------|--------------------------------------------------------|
            | 0–30 dB        | Biblioteca, susurros                | Sin riesgo                                             |
            | 30–60 dB       | Conversación normal                 | Sin riesgo                                             |
            | 60–85 dB       | Tráfico denso, aspiradora          | Riesgo leve si exposición prolongada                   |
            | **85–100 dB**  | Moto, concierto                     | **Puede causar daño si hay exposición prolongada (>8h)** |
            | **100–120 dB** | Sirena ambulancia, martillo neumático | **Daño auditivo posible en minutos**                  |
            """)

            st.markdown("### Distribución de niveles de riesgo por hora")
        
            horas_disponibles = sorted(df_filtrado["hora"].unique())
            horas_seleccionadas = st.multiselect(
                "Selecciona las horas que deseas visualizar (en formato 24h):",
                options=horas_disponibles,
                default=horas_disponibles
            )
        
            if horas_seleccionadas:
                for h in horas_seleccionadas:
                    df_hora = df_filtrado[df_filtrado["hora"] == h]
                    conteo = df_hora["riesgo"].value_counts()
        
                    fig, ax = plt.subplots()
                    ax.pie(
                        conteo,
                        labels=conteo.index,
                        autopct="%1.1f%%",
                        startangle=90,
                        colors=["#2ca02c", "#ff7f0e", "#d62728"]
                    )
                    ax.set_title(f"{h}:00 hrs — Niveles de Riesgo")
                    st.pyplot(fig)
            else:
                st.info("Selecciona al menos una hora para visualizar los diagramas.")

    else:
        st.warning("No hay datos para los parámetros seleccionados.")
