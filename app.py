import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from scipy.interpolate import griddata
from influxdb_client import InfluxDBClient
from datetime import timedelta
from streamlit_autorefresh import st_autorefresh  # Opcional para refrescar auto

# Refrescar cada 30s
st_autorefresh(interval=30000, key="refresh")

# --- CONFIGURACIÓN DE INFLUXDB ---
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "_L9PKanXCuigARoWixm3SWBkl5nv6hngIM9-PBAh_btyklusppM80kDB-wER1quiTeSZXZLeWZwJxp4NNz_t9g=="
INFLUXDB_ORG = "CADI"
INFLUXDB_BUCKET = "Ruido"

# --- FUNCIÓN DE CONSULTA A INFLUXDB ---
@st.cache_data(ttl=10)
def obtener_datos_realtime(nodos, minutos=10):
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        query_api = client.query_api()
        dfs = []

        for nodo in nodos:
            query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                    |> range(start: -{minutos}m)
                    |> filter(fn: (r) => r["_measurement"] == "leq")
                    |> filter(fn: (r) => r["nodo"] == "{nodo}")
                    |> aggregateWindow(every: 1s, fn: last, createEmpty: false)
                    |> yield(name: "last")
            '''
            result = query_api.query(org=INFLUXDB_ORG, query=query)

            data = []
            for table in result:
                for record in table.records:
                    data.append({
                        "time": record.get_time(),
                        "nodo": nodo,
                        "value": record.get_value()
                    })

            df_nodo = pd.DataFrame(data)
            dfs.append(df_nodo)

        df_total = pd.concat(dfs, ignore_index=True)
        df_total["time"] = pd.to_datetime(df_total["time"]) - pd.Timedelta(hours=6)
        return df_total

    except Exception as e:
        st.error(f"Error al consultar InfluxDB: {e}")
        return pd.DataFrame()

# --- CONFIGURACIÓN DE STREAMLIT ---
st.set_page_config(page_title="Visualización de Niveles de Sonido", layout="wide")

st.markdown("""
    <style>
        header {visibility: hidden;}
        .block-container {padding-top: 1rem;}
        h2 { font-size: 16px !important; color: red !important; }
        .subheader { color: #333; }
        .menu-button {
            background-color: #004080;
            color: white;
            padding: 10px 25px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO E IMAGEN ---
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.title("**Investigación del comportamiento del ruido en un ambiente universitario**")
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

# --- RESULTADOS CON DATOS EN TIEMPO REAL ---
if seccion_activa == "Resultados":
    st.markdown("### Resultados")

    with st.sidebar:
        st.header("Datos en tiempo real desde InfluxDB")
        nodos_disponibles = [1, 2, 3, 4]
        nodos_seleccionados = st.multiselect("Selecciona los nodos:", nodos_disponibles, default=nodos_disponibles)
        minutos = st.slider("Últimos minutos a consultar", 1, 60, 10)
        df_filtrado = obtener_datos_realtime(nodos_seleccionados, minutos)

    if not df_filtrado.empty:
        def clasificar_riesgo(db):
            if db < 85:
                return "Seguro"
            elif db < 100:
                return "Riesgo moderado"
            else:
                return "Peligroso"

        df_filtrado["riesgo"] = df_filtrado["value"].apply(clasificar_riesgo)
        df_filtrado["hora"] = df_filtrado["time"].dt.hour

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Mapa de Sonido",
            "📈 Gráficos por nodo",
            "🧩 Comparación general",
            "📊 Análisis estadístico",
            "🧨 Riesgo por hora"
        ])

        with tab1:
            st.markdown("### 💥 Mapa de niveles de sonido")

            X = df_filtrado['nodo'].astype(int).values
            fecha_base = df_filtrado["time"].dt.normalize().min()
            tiempos_segundos = (df_filtrado['time'] - fecha_base).dt.total_seconds().values
            Z = df_filtrado['value'].astype(float).values

            x_unique = np.unique(X)
            y_unique = np.unique(tiempos_segundos)
            X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
            Z_grid = griddata((X, tiempos_segundos), Z, (X_grid, Y_grid), method='linear')
            Z_grid = np.nan_to_num(Z_grid, nan=np.nanmin(Z_grid))

            fig, ax = plt.subplots(figsize=(10, 6))
            yticks = np.linspace(0, len(y_unique) - 1, num=10, dtype=int)
            yticklabels = [pd.to_datetime(y_unique[i], unit='s').strftime('%H:%M') for i in yticks]

            sb.heatmap(Z_grid, cmap='jet', xticklabels=x_unique, yticklabels=False, ax=ax)
            ax.invert_yaxis()
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticklabels)
            ax.set_xlabel("Nodos")
            ax.set_ylabel("Hora (HH:MM)")
            st.pyplot(fig)

        with tab2:
            st.markdown("#### Evolución temporal por nodo")
            for nodo in sorted(df_filtrado["nodo"].unique()):
                st.subheader(f"Nodo {nodo}")
                datos_nodo = df_filtrado[df_filtrado["nodo"] == nodo]
                st.line_chart(datos_nodo.set_index("time")["value"], height=200)

        with tab3:
            st.markdown("### Comparación general de nodos")
            df_pivot = df_filtrado.pivot(index='time', columns='nodo', values='value').sort_index()
            st.line_chart(df_pivot, height=300)

        with tab4:
            st.markdown("### Análisis estadístico por nodo")
            resumen = df_filtrado.groupby("nodo")["value"].agg(["min", "max", "mean", "median", "count"]).round(2)
            st.dataframe(resumen)
            st.bar_chart(resumen["max"])

        with tab5:
            st.markdown("### Distribución por riesgo auditivo")
            def clasificar_rango(db):
                if db < 30:
                    return "0–30 dB: Sin riesgo"
                elif db < 60:
                    return "30–60 dB: Sin riesgo"
                elif db < 85:
                    return "60–85 dB: Riesgo leve"
                elif db < 100:
                    return "85–100 dB: Riesgo moderado"
                else:
                    return "100–120+ dB: Peligroso"

            df_filtrado["rango"] = df_filtrado["value"].apply(clasificar_rango)
            hora_sel = st.selectbox("Selecciona la hora (0–23):", sorted(df_filtrado["hora"].unique()))
            df_hora = df_filtrado[df_filtrado["hora"] == hora_sel]
            conteo = df_hora["rango"].value_counts().sort_index()

            colores = {
                "0–30 dB: Sin riesgo": "#b3d9ff",
                "30–60 dB: Sin riesgo": "#80bfff",
                "60–85 dB: Riesgo leve": "#ffcc80",
                "85–100 dB: Riesgo moderado": "#ff9966",
                "100–120+ dB: Peligroso": "#ff4d4d"
            }

            fig, ax = plt.subplots()
            ax.pie(
                conteo,
                labels=conteo.index,
                autopct="%1.1f%%",
                colors=[colores.get(k, "#ccc") for k in conteo.index]
            )
            ax.set_title(f"{hora_sel}:00 hrs — Niveles de sonido")
            st.pyplot(fig)

    else:
        st.warning("No hay datos disponibles en este momento.")
