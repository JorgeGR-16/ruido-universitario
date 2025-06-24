import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Visualización de Niveles de Sonido", layout="wide")

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------##
#ESTILO PERSONALIZADO
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

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------##
#TITULO GENERAL
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.title("**Investigación del comportamiento del ruido en un ambiente universitario**")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------##
#IMAGEN PRINCIPAL
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.image("UAMAZC.jpg", use_container_width=600)

##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------##

#MENÚ DE NAVEGACIÓN PERSONALIZADO 
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

##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------##

st.markdown('<p class="subheader">Aplicación de análisis acústico para investigación técnica</p>', unsafe_allow_html=True)


##---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------##
# --- SECCIONES ---
if seccion_activa == "Introducción":
    with st.container():
        st.markdown("### Introducción")
        st.markdown("""
        <div style='text-align: justify;'>
        El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros para medir los niveles sonoros.
        [...] <!-- Puedes dejar aquí tu texto completo de introducción -->
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 1.1 Principio de funcionamiento")
        st.markdown("""
        **1. Captación del sonido:**  
        [...]  
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

elif seccion_activa == "Objetivo":
    st.markdown("### Objetivo")
    st.markdown("""
    * Visualizar el comportamiento del sonido en una área específica, utilizando sensores y gráficos, para comprender con mayor claridad en qué zonas afectan más las alteraciones sonoras.
    """)
    
elif seccion_activa == "Desarrollo":
    st.markdown("### Desarrollo del prototipo")
    st.markdown("""
    *En esta parte veremos el desarrollo del prototipo y su construccion.
    """)
    
elif seccion_activa == "Resultados":
    st.markdown("### Resultados")

    with st.sidebar:
        st.header("Parámetros de entrada")
        uploaded_file = "mediciones_1.csv"

    try:
        df = pd.read_csv(uploaded_file, skiprows=3)
        columnas_requeridas = ['_time', 'nodo', '_value']
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"El CSV debe contener las columnas: {columnas_requeridas}")
        else:
            df['_time'] = pd.to_datetime(df['_time'], format='%Y-%m-%dT%H:%M:%S.%fZ', utc=True, errors='coerce')
            if df['_time'].isna().any():
                st.warning("Algunas fechas no se pudieron convertir correctamente.")

            tiempo_min = df['_time'].min()
            tiempo_max = df['_time'].max()

            with st.expander("Filtro temporal", expanded=True):
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
                tab1, tab2 = st.tabs(["📊 Mapa de calor", "📈 Gráficos por nodo"])

                with tab1:
                    st.markdown("Mapa de calor de niveles de sonido:")
                
                    df_filtrado['nodo'] = df_filtrado['nodo'].astype(int)
                    fecha_base = pd.Timestamp(fecha).tz_localize('UTC')
                
                    df_pivot = df_filtrado.pivot_table(index='_time', columns='nodo', values='_value', aggfunc='mean').sort_index()
                    nodos_completos = list(range(1, 21))
                    df_pivot = df_pivot.reindex(columns=nodos_completos)
                
                    Z_grid = df_pivot.values
                    y_unique = (df_pivot.index - fecha_base).total_seconds().values
                    x_unique = np.array(nodos_completos)
                
                    fig, ax = plt.subplots(figsize=(6, 4))
                    extent = [x_unique.min() - 0.5, x_unique.max() + 0.5, y_unique.min(), y_unique.max()]
                
                    im = ax.imshow(Z_grid, aspect='auto', origin='lower', cmap='jet', extent=extent)
                    plt.colorbar(im, ax=ax, label='Nivel de sonido (dB)')
                
                    # Configurar ticks X solo enteros sin decimales
                    ax.set_xticks(x_unique)
                    ax.set_xticklabels([str(x) for x in x_unique])
                    ax.xaxis.set_major_locator(plt.FixedLocator(x_unique))
                    ax.xaxis.set_minor_locator(plt.NullLocator())
                    ax.tick_params(axis='x', which='both', length=5)
                
                    yticks = ax.get_yticks()
                    ylabels = [(fecha_base + pd.Timedelta(seconds=sec)).strftime('%H:%M') for sec in yticks]
                    ax.set_yticks(yticks)
                    ax.set_yticklabels(ylabels)
                
                    ax.set_xlabel("Nodos")
                    ax.set_ylabel("Hora (HH:MM)")
                    ax.set_title("Mapa de niveles de sonido", fontsize=14)
                
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col2:
                        st.pyplot(fig, use_container_width=False)

                with tab2:
                   
                    st.markdown("#### Gráficos combinados por nodo")
                
                    nodos = sorted(df_filtrado["nodo"].unique())
                    
                    for i, nodo in enumerate(nodos):
                        datos_nodo = df_filtrado[df_filtrado["nodo"] == nodo].sort_values('_time')
                
                        if len(datos_nodo) < 2:
                            continue
                
                        col1, col2 = st.columns([1, 1])
                
                        with col1:
                            st.markdown(f"**Nodo {nodo} – Gráfico de Línea**")
                            st.line_chart(datos_nodo.set_index('_time')['_value'], height=200, use_container_width=True)
                
                        with col2:
                            st.markdown(f"**Nodo {nodo} – Mapa de Calor**")
                            valores = datos_nodo['_value'].values
                
                            if len(valores) < 2:
                                st.warning("No hay suficientes datos para este nodo.")
                                continue
                
                            # Convertir a matriz 2D
                            Z_matrix = np.expand_dims(valores, axis=0)
                
                            # Tiempos relativos en segundos
                            tiempos_relativos = (datos_nodo['_time'] - datos_nodo['_time'].min()).dt.total_seconds().values
                
                            if len(tiempos_relativos) != len(valores):
                                st.warning("Datos incompatibles para mapa de calor.")
                                continue
                
                            extent = [tiempos_relativos.min(), tiempos_relativos.max(), 0, 1]
                
                            fig, ax = plt.subplots(figsize=(5, 1.5))
                            im = ax.imshow(Z_matrix, aspect='auto', origin='lower', cmap='jet', extent=extent)
                
                            ax.set_yticks([])
                            ax.set_xticks([])
                            ax.set_xlabel("Tiempo")
                            plt.colorbar(im, ax=ax, orientation='vertical', fraction=0.05, pad=0.04)
                
                            st.pyplot(fig)


    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
