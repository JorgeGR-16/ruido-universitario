import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from scipy.interpolate import griddata
import os

st.set_page_config(page_title="Visualización de Niveles de Sonido", layout="wide")

# --- CONFIGURACIÓN DE ACCESO AL ARCHIVO ---
# ✅ CORRECCIÓN: Saltamos solo la Fila 1 para que los encabezados (Fila 2) sean detectados.
NUM_SKIP_ROWS = 1 
# ------------------------------------------

# Asegúrate de que esta URL sea la correcta para tu Google Sheet (ID y GID)
SHEET_ID = "1fH5RGHo3_1u8F_SHJTVWP6TDmX8xtsha"
GID = 0 
data_source = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

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
/* Estilos para los botones de navegación */
div[data-testid="stButton"] > button {
    background-color: #004080;
    color: white;
    padding: 10px 25px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    border: none;
    transition: background-color 0.3s;
}

div[data-testid="stButton"] > button:hover {
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
    try:
        # Asegúrate de que 'UAMAZC.jpg' esté en la misma carpeta
        st.image("UAMAZC.jpg", use_container_width=True) 
    except FileNotFoundError:
        st.warning("Archivo UAMAZC.jpg no encontrado.")
        
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

# --- SECCIONES INTRODUCCIÓN, OBJETIVO, DESARROLLO (SIN CAMBIOS FUNCIONALES) ---
if seccion_activa == "Introducción":
    st.markdown("### Introducción")
    st.markdown("""
    <div style='text-align: justify;'>
    El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros para medir los niveles sonoros. El ruido es un factor ambiental que puede influir negativamente en la calidad de vida, el rendimiento académico y la salud de estudiantes y personal universitario...
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    El **sonómetro** es un instrumento de lectura directa del nivel global de presión sonora. Sirve para medir la intensidad del sonido, expresada en **decibeles (dB)**. 

[Image of schematic diagram of a sound level meter]
 Su importancia radica en que permite cuantificar el ruido ambiental, evaluar el cumplimiento de normativas acústicas, diseñar políticas de control y mitigación del ruido, y proteger la salud pública y el bienestar social. Los niveles elevados de ruido pueden interferir en actividades cotidianas, como el trabajo o el descanso, y tienen un impacto directo en la salud pública.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1.1 Principio de funcionamiento")
    st.markdown("""
    <div style='text-align: justify;'>
    1. **Captación del sonido:** El sonido ambiente es captado por un micrófono de condensador...
    </div>
    """, unsafe_allow_html=True)
    st.latex(r'''
    \text{Nivel de presión sonora (dB)} = 20 \cdot \log_{10} \left(\frac{P}{P_0}\right)
    ''')
    st.markdown("""
    Donde:
    * $P$: presión sonora medida
    * $P_0 = 20\,\mu\text{Pa}$: presión sonora de referencia (umbral de audición humana)
    """, unsafe_allow_html=True)
    
    # ... (Resto de la sección Introducción)

elif seccion_activa == "Objetivo":
    st.markdown("### Objetivo")
    st.markdown("* Visualizar el comportamiento del sonido en una área específica...")
    # ... (Resto de la sección Objetivo)

elif seccion_activa == "Desarrollo":
    st.markdown("### Desarrollo del prototipo")
    st.header("*En esta parte veremos el desarrollo del prototipo y su construcción.*")
    # ... (Resto de la sección Desarrollo)

# --- SECCIÓN RESULTADOS (CON CAMBIOS EN LA LECTURA DE DATOS) ---

elif seccion_activa == "Resultados":
    st.markdown("### Resultados")
    
    df_filtrado = pd.DataFrame()

    with st.sidebar:
        st.header("Parámetros de entrada")
        
        try:
            # 🚨 MODIFICACIÓN CLAVE: Agregamos decimal=',' para manejar el formato regional (62,41)
            # y usamos skiprows=NUM_SKIP_ROWS (que ahora es 1)
            df = pd.read_csv(data_source, skiprows=NUM_SKIP_ROWS, decimal=',')
            
            columnas_requeridas = ['_time', 'nodo', '_value']
            
            if not all(col in df.columns for col in columnas_requeridas):
                st.error("El archivo no contiene las columnas necesarias (_time, nodo, _value).")
                st.info(f"Columnas encontradas después de saltar {NUM_SKIP_ROWS} filas: {df.columns.tolist()}")
            else:
                # 🚨 MODIFICACIÓN: Conversión segura de 'nodo' a entero. Si falla, lo deja como string.
                try:
                    df['nodo'] = df['nodo'].astype(int)
                except ValueError:
                    st.warning("La columna 'nodo' contiene valores no numéricos y se usará como texto.")

                # Conversión de tiempo (maneja el formato ISO/UTC como '2025-11-12T19:13:06Z')
                df['_time'] = pd.to_datetime(df['_time'], utc=True, errors='coerce')
                
                if df['_time'].isna().all():
                    st.error("No se pudieron interpretar las fechas en la columna '_time'. Verifica el formato de tu hoja.")
                else:
                    tiempo_min = df['_time'].min().tz_convert('UTC')
                    tiempo_max = df['_time'].max().tz_convert('UTC')

                    # Manejo de la fecha y horas (Mismo código de filtros)
                    fecha_default = tiempo_min.date()
                    fecha = st.date_input("Fecha", value=fecha_default, min_value=tiempo_min.date(), max_value=tiempo_max.date())

                    hora_inicio = st.time_input("Hora de inicio", value=pd.to_datetime('00:00').time())
                    hora_fin = st.time_input("Hora de fin", value=pd.to_datetime('23:59').time())

                    nodos_disponibles = sorted(df["nodo"].astype(str).unique())
                    nodos_seleccionados = st.multiselect(
                        "Selecciona los nodos:",
                        options=nodos_disponibles,
                        default=nodos_disponibles
                    )
                    
                    # Filtrado final
                    fecha_inicio_str = f"{fecha} {hora_inicio}"
                    fecha_fin_str = f"{fecha} {hora_fin}"
                    
                    fecha_inicio = pd.to_datetime(fecha_inicio_str).tz_localize('UTC')
                    fecha_fin = pd.to_datetime(fecha_fin_str).tz_localize('UTC')
                    
                    df_filtrado = df[
                        (df['_time'] >= fecha_inicio) & 
                        (df['_time'] <= fecha_fin) & 
                        (df['nodo'].astype(str).isin(nodos_seleccionados))
                    ].copy() 
                        
        except Exception as e:
            st.error(f"Error al cargar o procesar el archivo: {e}")
            st.info(f"**Verifica:** 1. Permisos públicos de la hoja. 2. La variable `NUM_SKIP_ROWS` está en **1**.")

    
    if not df_filtrado.empty:
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
        # ... (Todo el código de las pestañas Tab1 a Tab5 es el mismo)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Mapa de Sonido", 
            "📈 Gráficos por nodo", 
            "🧩 Comparación general", 
            "📊 Análisis estadístico", 
            "🧨 Riesgo por hora"
        ])

        # Contenido de la Tab1 (Mapa de Sonido)
        with tab1:
            st.markdown("### Mapa de niveles de sonido")
            st.markdown("""
            Este mapa de calor representa la intensidad del ruido registrado por cada nodo (sensor) a lo largo del tiempo en un día específico...
            """)
            
            # Selector de paleta de colores encima del mapa
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                palette = st.selectbox(
                    "Seleccione la paleta de colores:",
                    options=['jet', 'viridis', 'plasma', 'inferno', 'magma', 'coolwarm', 'YlOrRd', 'RdYlBu_r'],
                    index=0,
                    key="palette_selector"
                )

            # --- Procesamiento de datos para el Mapa de Calor ---
            try:
                # Usar valores de 'nodo' convertidos a float (si son numéricos)
                X = df_filtrado['nodo'].astype(float).values
            except ValueError:
                # Si el nodo es texto (por la advertencia anterior), usar códigos para mapear en el eje X
                X = df_filtrado['nodo'].astype('category').cat.codes.values + 1
            
            fecha_base = pd.Timestamp(fecha).tz_localize('UTC')
            tiempos_segundos = (df_filtrado['_time'] - fecha_base).dt.total_seconds().values
            # El valor ya es float gracias a decimal=','
            Z = df_filtrado['_value'].values 

            # Preparar la rejilla de interpolación
            x_unique = np.unique(X)
            y_unique = np.unique(tiempos_segundos)
            
            if len(x_unique) > 1 and len(y_unique) > 1:
                X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
                
                # Interpolación
                Z_grid = griddata((X, tiempos_segundos), Z, (X_grid, Y_grid), method='linear')
                
                # Rellenar NaNs con el valor mínimo
                Z_grid = np.nan_to_num(Z_grid, nan=np.nanmin(Z_grid) if not np.isnan(np.nanmin(Z_grid)) else 0)

                # Configuración del gráfico
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Calcular yticks para mostrar las horas
                yticks_indices = np.linspace(0, len(y_unique) - 1, num=10, dtype=int)
                yticks_values = y_unique[yticks_indices]
                yticklabels = [pd.to_datetime(t, unit='s').strftime('%H:%M') for t in yticks_values]

                # Heatmap con paleta seleccionada
                sb.heatmap(
                    Z_grid,
                    cmap=palette, 
                    xticklabels=x_unique,
                    yticklabels=False,
                    ax=ax
                )
                
                ax.invert_yaxis()
                ax.set_yticks(yticks_indices + 0.5) 
                ax.set_yticklabels(yticklabels, rotation=0)
                
                ax.set_xlabel("Nodos")
                ax.set_ylabel("Hora (HH:MM)")

                # Añadir barra de color con etiqueta
                cbar = ax.collections[0].colorbar
                cbar.set_label('Nivel de sonido (dB)', rotation=270, labelpad=20)
                
                st.pyplot(fig)
            else:
                 st.warning("Datos insuficientes para generar el mapa de calor. Asegúrate de tener mediciones de al menos dos nodos y dos tiempos distintos.")

        # Contenido de las Tabs 2 a 5 (Se omite por brevedad, es el mismo código)
        with tab2:
            st.markdown("#### Evolución temporal por nodo")
            for nodo in sorted(df_filtrado["nodo"].astype(str).unique()):
                st.subheader(f"Nodo {nodo}")
                datos_nodo = df_filtrado[df_filtrado["nodo"].astype(str) == nodo]
                if not datos_nodo.empty:
                    st.line_chart(datos_nodo.set_index("_time")["_value"], height=200, use_container_width=True)
                else:
                    st.info(f"No hay datos para el Nodo {nodo} en el rango de tiempo seleccionado.")
        
        with tab3:
            st.markdown("### Comparación general de nodos en un solo gráfico")
            df_pivot = df_filtrado.pivot(index='_time', columns='nodo', values='_value').sort_index()
            df_pivot.columns = df_pivot.columns.astype(str) 
            st.line_chart(df_pivot, height=300, use_container_width=True)

        with tab4:
            st.markdown("### Análisis estadístico básico por nodo")
            resumen_estadistico = df_filtrado.groupby("nodo")["_value"].agg(
                Minimo="min", Maximo="max", Media="mean", Mediana="median", Conteo="count"
            ).round(2)
            st.dataframe(resumen_estadistico, use_container_width=True)
            st.markdown("### Gráfico de valores máximos por nodo")
            resumen_estadistico.index = resumen_estadistico.index.astype(str)
            st.bar_chart(resumen_estadistico["Maximo"])

        with tab5:
            st.markdown("### **Efectos del ruido en la audición**")
            # ... (omisión del texto estático de la tab 5) ...
            st.markdown("### Distribución de niveles de sonido por hora (clasificados por riesgo auditivo)")
            def clasificar_rango(db):
                if db < 30: return "0–30 dB: Sin riesgo"
                elif db < 60: return "30–60 dB: Sin riesgo"
                elif db < 85: return "60–85 dB: Riesgo leve"
                elif db < 100: return "85–100 dB: Riesgo moderado"
                else: return "100–120+ dB: Peligroso"

            df_filtrado["rango"] = df_filtrado["_value"].apply(clasificar_rango)
            horas_disponibles = sorted(df_filtrado["hora"].unique())
            if horas_disponibles:
                hora_seleccionada = st.selectbox("Selecciona la hora que deseas visualizar (formato 24h):", options=horas_disponibles, index=0)
                df_hora = df_filtrado[df_filtrado["hora"] == hora_seleccionada]
                conteo = df_hora["rango"].value_counts().sort_index()
                if not conteo.empty:
                    colores = {"0–30 dB: Sin riesgo": "#b3d9ff", "30–60 dB: Sin riesgo": "#80bfff", "60–85 dB: Riesgo leve": "#ffcc80", "85–100 dB: Riesgo moderado": "#ff9966", "100–120+ dB: Peligroso": "#ff4d4d"}
                    colores_para_grafico = [colores.get(cat, "#cccccc") for cat in conteo.index]
                    fig, ax = plt.subplots()
                    ax.pie(conteo, labels=conteo.index, autopct="%1.1f%%", startangle=90, colors=colores_para_grafico)
                    ax.set_title(f"{hora_seleccionada}:00 hrs — Niveles de sonido por rango")
                    ax.axis('equal') 
                    st.pyplot(fig)
                else: st.info(f"No hay mediciones para la hora {hora_seleccionada}:00 hrs.")
            else: st.info("No hay datos de horas disponibles para el análisis de riesgo.")
            

    else:
        st.warning("No hay datos para los parámetros seleccionados o la base de datos de Google Sheets no se cargó correctamente.")
