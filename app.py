import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import traceback

# ==========================
# CONFIGURACIÓN DE PÁGINA
# ==========================
st.set_page_config(
    page_title="Análisis del Comportamiento del Ruido en el Ambiente Universitario",
    layout="wide"
)

# ==========================
# NAVEGACIÓN PRINCIPAL
# ==========================
menu = st.sidebar.radio(
    "Navegación",
    ["Introducción", "Objetivo", "Desarrollo", "Resultados"]
)

# ==========================
# SECCIÓN: INTRODUCCIÓN
# ==========================
if menu == "Introducción":
    st.title("Análisis del Comportamiento del Ruido en el Ambiente Universitario")
    st.markdown("""
    Este proyecto analiza los niveles de ruido registrados en diferentes puntos del entorno universitario,
    utilizando una red de sensores conectados mediante tecnología **LoRa32** y micrófonos **INMP441**.
    """)

# ==========================
# SECCIÓN: OBJETIVO
# ==========================
elif menu == "Objetivo":
    st.header("Objetivo General")
    st.markdown("""
    Analizar el comportamiento del ruido ambiental en un entorno universitario,
    identificando patrones horarios y zonas con niveles potencialmente dañinos para la salud auditiva.
    """)

# ==========================
# SECCIÓN: DESARROLLO TEÓRICO
# ==========================
elif menu == "Desarrollo":
    st.header("Desarrollo Teórico")
    st.markdown("""
    Los niveles de ruido son medidos en decibelios (dB) y se expresan comúnmente mediante el nivel **Leq**,
    que representa el nivel equivalente de sonido continuo durante un intervalo de tiempo determinado.
    """)

# ==========================
# SECCIÓN: RESULTADOS
# ==========================
elif menu == "Resultados":
    st.header("Resultados del Monitoreo")

    # -----------------------------------
    # PANEL LATERAL DE PARÁMETROS
    # -----------------------------------
    with st.sidebar:
        st.header("Parámetros de entrada")

        try:
            # ✅ URL pública de tu hoja de Google Sheets
            sheet_url = "https://docs.google.com/spreadsheets/d/1-9FdzIdIz-F7UYuK8DFdBjzPwS9-J3FLV05S_yTaOGE/export?format=csv&gid=0"

            # ✅ Leer el CSV directamente desde Google Sheets
            df = pd.read_csv(sheet_url, encoding='utf-8', on_bad_lines='skip')

            # ✅ Renombrar columnas clave según su posición
            if len(df.columns) > 8:
                df = df.rename(columns={
                    df.columns[4]: '_time',    # Columna 5
                    df.columns[5]: '_value',   # Columna 6
                    df.columns[8]: 'nodo'      # Columna 9
                })[['_time', '_value', 'nodo']]
            else:
                st.error("❌ La hoja de cálculo no contiene las columnas necesarias.")
                st.stop()

            # ✅ Conversión de tipos de datos
            df['_time'] = pd.to_datetime(df['_time'], errors='coerce', utc=True)
            df['_value'] = pd.to_numeric(df['_value'], errors='coerce')
            df['nodo'] = df['nodo'].astype(str)

            # ✅ Limpieza de datos nulos
            df = df.dropna(subset=['_time', '_value', 'nodo'])
            df = df.sort_values('_time')

            # ✅ Mostrar vista previa
            st.success(f"Datos cargados correctamente: {len(df)} registros")
            st.dataframe(df.head())

            # --- FILTROS DE FECHA / HORA / NODOS ---
            tiempo_min, tiempo_max = df['_time'].min(), df['_time'].max()

            fecha = st.date_input(
                "Selecciona fecha:",
                value=tiempo_min.date(),
                min_value=tiempo_min.date(),
                max_value=tiempo_max.date()
            )
            hora_inicio = st.time_input("Hora de inicio", pd.to_datetime("00:00").time())
            hora_fin = st.time_input("Hora de fin", pd.to_datetime("23:59").time())

            nodos_disponibles = sorted(df["nodo"].unique())
            nodos_seleccionados = st.multiselect(
                "Selecciona nodos:",
                options=nodos_disponibles,
                default=nodos_disponibles
            )

            # --- FILTRADO DE DATOS ---
            inicio = pd.to_datetime(f"{fecha} {hora_inicio}").tz_localize('UTC')
            fin = pd.to_datetime(f"{fecha} {hora_fin}").tz_localize('UTC')

            df_filtrado = df[
                (df['_time'] >= inicio) &
                (df['_time'] <= fin) &
                (df['nodo'].isin(nodos_seleccionados))
            ]

            st.write(f"📊 Registros filtrados: {len(df_filtrado)}")

        except Exception as e:
            st.error("❌ Error al cargar o procesar los datos:")
            st.code(traceback.format_exc())
            df_filtrado = pd.DataFrame()

    # -----------------------------------
    # VISUALIZACIÓN DE RESULTADOS
    # -----------------------------------
    if not df_filtrado.empty:
        st.subheader("Evolución del Nivel de Ruido (Leq)")

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df_filtrado, x="_time", y="_value", hue="nodo", ax=ax)
        ax.set_title("Niveles de Ruido por Nodo")
        ax.set_xlabel("Tiempo")
        ax.set_ylabel("Nivel de Ruido (dB)")
        ax.legend(title="Nodo")
        st.pyplot(fig)

        # --- ESTADÍSTICAS ---
        st.subheader("Estadísticas por Nodo")
        stats = df_filtrado.groupby('nodo')['_value'].describe()[['mean', 'min', 'max']]
        st.dataframe(stats)

        # --- ANÁLISIS DE RIESGO AUDITIVO ---
        st.subheader("Distribución de Niveles de Ruido Peligrosos")
        bins = [0, 55, 70, 85, 100, 120]
        labels = ['Bajo', 'Moderado', 'Alto', 'Muy Alto', 'Peligroso']
        df_filtrado['Nivel'] = pd.cut(df_filtrado['_value'], bins=bins, labels=labels, right=False)
        nivel_counts = df_filtrado['Nivel'].value_counts().sort_index()

        fig2, ax2 = plt.subplots()
        ax2.pie(nivel_counts, labels=nivel_counts.index, autopct='%1.1f%%')
        ax2.set_title("Porcentaje de Niveles de Ruido por Categoría")
        st.pyplot(fig2)

    else:
        st.warning("⚠️ No hay datos disponibles para los filtros seleccionados.")
