import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from scipy.interpolate import griddata

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Visualización de Niveles de Sonido", layout="wide")

# --- ESTILO PERSONALIZADO ---
# Se mantiene el estilo original para respetar el diseño solicitado
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
        .stButton>button {
            background-color: #004080;
            color: white;
            padding: 10px 25px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            border: none;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #0059b3;
        }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO GENERAL ---
# 
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.title("📢 **Investigación del comportamiento del ruido en un ambiente universitario**")

# --- IMAGEN PRINCIPAL (Asegúrate de tener este archivo) ---
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.image("UAMAZC.jpg", use_container_width=True, caption="UAM Azcapotzalco: Lugar de la investigación (Imagen de referencia)")

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
# -----------------------------------------------------------------------------
if seccion_activa == "Introducción":
    st.markdown("---")
    st.markdown("### 📚 Introducción")
    st.markdown("""
    <div style='text-align: justify;'>
    El presente proyecto tiene como objetivo investigar cómo afecta el **ruido ambiental** en una zona específica de la universidad mediante la instalación y uso de **sonómetros** para medir los niveles sonoros.
    El ruido es un factor ambiental que puede influir negativamente en la calidad de vida, el rendimiento académico y la salud de estudiantes y personal universitario.
    <br><br>
    El **sonómetro** es un instrumento de lectura directa del nivel global de presión sonora, expresada en **decibeles (dB)**. Su importancia radica en que permite **cuantificar el ruido ambiental**, evaluar el cumplimiento de normativas acústicas y proteger la salud pública y el bienestar social.
    Los niveles elevados de ruido pueden interferir en actividades cotidianas, como el estudio o el descanso, y tienen un impacto directo en la salud pública.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚠️ Riesgos contra la salud humana por exposición al ruido")
    st.markdown("""
    * **Pérdida auditiva inducida por ruido:** Daño a las células sensoriales del oído interno.
    * **Estrés, irritabilidad y fatiga mental:** Interferencia con la concentración y el descanso.
    * **Aumento del riesgo cardiovascular:** Elevación de la presión arterial y trastornos circulatorios.
    """)

    st.markdown("### ⚖️ Marco Legal y Normatividad")
    st.markdown("""
    * La **Ley Ambiental de Protección a la Tierra** establece límites máximos de emisiones sonoras.
    * La norma **NADF-005-AMBT-2013** en la Ciudad de México regula el ruido en el exterior, estableciendo los Límites Máximos Permisibles.
    * La **Procuraduría Ambiental y del Ordenamiento Territorial (PAOT)** se encarga de inspeccionar y responder a las denuncias ciudadanas sobre contaminación acústica.
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Niveles_de_ruido.jpg", use_container_width=True, caption="Tabla de referencia de niveles de ruido comunes.")
    
    st.markdown("---")
    st.markdown("### 1.1 Principio de funcionamiento del Sonómetro")
    st.markdown("""
    <div style='text-align: justify;'>
    1. **Captación del sonido:** Un micrófono de condensador capta las ondas y las convierte en señal eléctrica.
    2. **Conversión y Cálculo:** La señal se amplifica, se filtra (ponderaciones A, C, Z) y se convierte a un valor logarítmico para obtener el nivel de presión sonora.
    </div>
    """, unsafe_allow_html=True)

    st.latex(r'''
        \text{Nivel de presión sonora (dB)} = 20 \cdot \log_{10} \left(\frac{P}{P_0}\right)
    ''')

    st.markdown(r"""
        Donde: 
        * $P$: presión sonora medida 
        * $P_0 = 20\,\mu\text{Pa}$: presión sonora de referencia (umbral de audición humana)
    """)

    st.markdown("### 1.2 Diagrama del dispositivo.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Diagrama.png", use_container_width=True, caption="Diagrama de bloques funcional de un sonómetro.")

# -----------------------------------------------------------------------------
elif seccion_activa == "Objetivo":
    st.markdown("---")
    st.markdown("### 🎯 Objetivo General y Específicos")
    
    st.markdown("#### 2.1 Objetivo General")
    st.markdown("Diseñar y construir un sonómetro digital que permita medir niveles de presión sonora en tiempo real, facilitando el monitoreo del ruido ambiental con precisión y la posterior visualización de datos.")
    
    st.markdown("#### 2.2 Objetivos Específicos")
    st.markdown("* Seleccionar y calibrar un sensor de sonido compatible con microcontroladores.")
    st.markdown("* Programar el microcontrolador para interpretar los datos de decibeles (dB) y mostrarlos en una interfaz digital.")
    st.markdown("* Integrar un sistema de visualización en pantalla (OLED o similar).")
    st.markdown("* **Medir** los niveles de ruido en diferentes puntos del área de estudio usando un sonómetro de clase adecuada.")
    st.markdown("* **Registrar y analizar** los datos obtenidos para identificar zonas y periodos con niveles de ruido excesivo.")
    st.markdown("* **Comparar** los resultados con los límites establecidos en las normas oficiales mexicanas.")
    st.markdown("* Fomentar la concientización sobre la importancia del control del ruido.")

# -----------------------------------------------------------------------------
elif seccion_activa == "Desarrollo":
    st.markdown("---")
    st.markdown("### 🛠️ Desarrollo y Construcción del Prototipo")
    st.header("Construcción del Sonómetro con ESP32")

    st.markdown("""
    <div style='text-align: justify;'>
    La construcción del sonómetro implica la integración de componentes electrónicos clave:
    * **Micrófono:** Capta ondas sonoras y las convierte en señal eléctrica.
    * **Amplificador/Pre-amplificador:** Fortalece la señal débil del micrófono.
    * **Filtros de frecuencia:** Simulan la respuesta del oído humano.
    * **Microcontrolador (ESP32):** Convierte la señal analógica a digital y realiza el cálculo de dB.
    * **Pantalla de visualización (OLED):** Muestra los resultados en tiempo real.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 3.1 Diseño del modelo ESP32")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("ESP32.jpg", use_container_width=True, caption="Módulo ESP32 T3 V1.6.1 utilizado como microcontrolador principal.")
        
    st.markdown("### 3.2 Construcción del sonómetro")
    
    st.markdown("#### 3.2.1 Materiales necesarios")
    st.table(pd.DataFrame({
        'Componente': ['ESP32 T3 V1.6.1', 'Sensor de sonido (micrófono)', 'Pantalla OLED', 'Jumpers', 'Pulsador (botón de control)', 'Caja impresa en 3D', 'Fuente de alimentación'],
        'Descripción': ['Microcontrolador con Wi-Fi/Bluetooth', 'Detecta presión sonora para convertirla a señal analógica', 'Muestra el nivel de decibeles en tiempo real (I2C)', 'Para las conexiones entre módulos', 'Encendido, reinicio o cambio de modo', 'Para encapsular el dispositivo y protegerlo', 'Batería o alimentación USB']
    }))

    st.markdown("#### 3.2.2 Procedimiento de armado")
    st.markdown("##### Conexión del sensor de sonido")
    st.table(pd.DataFrame({
        'Sensor': ['VCC', 'GND', 'A0 (salida analógica)'],
        'ESP32 T3 V1.6.1': ['3.3V', 'GND', 'GPIO 34 (u otro pin analógico)']
    }))
    
    st.markdown("##### Conexión de la pantalla OLED (Protocolo I2C)")
    st.table(pd.DataFrame({
        'OLED SSD1306': ['VCC', 'GND', 'SDA', 'SCL'],
        'ESP32 T3 V1.6.1': ['3.3V', 'GND', 'GPIO 21', 'GPIO 22']
    }))
    
    st.markdown("""
    * **Botón de control:** Conectar un botón entre un pin digital y GND para funciones de control.
    * **Código en Arduino:** Carga el *firmware* al ESP32 para leer el sensor y mostrar los datos.
    * **Montaje físico y carcasa:** Utilizar una caja impresa en 3D para un ensamblaje robusto y seguro.
    """)

# -----------------------------------------------------------------------------
elif seccion_activa == "Resultados":
    st.markdown("---")
    st.markdown("### 📈 Resultados y Análisis de Datos")
    
    # --- PROCESAMIENTO DE DATOS ---
    with st.sidebar:
        st.header("⚙️ Parámetros de entrada")
        # Asumiendo la ruta fija para el archivo de datos
        uploaded_file = "40nodos.csv" 
        df_filtrado = pd.DataFrame()

        try:
            # La función 'skiprows=3' es crucial para leer el archivo InfluxDB CSV
            df = pd.read_csv(uploaded_file, skiprows=3)
            columnas_requeridas = ['_time', 'nodo', '_value']

            if not all(col in df.columns for col in columnas_requeridas):
                st.error("El archivo no contiene las columnas necesarias (_time, nodo, _value).")
            else:
                df['_time'] = pd.to_datetime(df['_time'], utc=True, errors='coerce')
                df = df.dropna(subset=['_time']) # Eliminar filas con fechas no interpretables

                if df.empty:
                    st.error("No se pudieron interpretar las fechas o el DataFrame está vacío.")
                else:
                    tiempo_min = df['_time'].min()
                    tiempo_max = df['_time'].max()

                    # Controles de filtrado
                    fecha = st.date_input("Fecha", value=tiempo_min.date(), min_value=tiempo_min.date(), max_value=tiempo_max.date())
                    hora_inicio = st.time_input("Hora de inicio", value=pd.to_datetime('00:00').time())
                    hora_fin = st.time_input("Hora de fin", value=pd.to_datetime('23:59').time())

                    nodos_disponibles = sorted(df["nodo"].unique())
                    nodos_seleccionados = st.multiselect(
                        "Selecciona los nodos:",
                        options=nodos_disponibles,
                        default=nodos_disponibles
                    )

                    # Aplicar filtros
                    fecha_inicio = pd.to_datetime(f"{fecha} {hora_inicio}").tz_localize('UTC')
                    fecha_fin = pd.to_datetime(f"{fecha} {hora_fin}").tz_localize('UTC')

                    df_filtrado = df[
                        (df['_time'] >= fecha_inicio) &
                        (df['_time'] <= fecha_fin) &
                        (df['nodo'].isin(nodos_seleccionados))
                    ].copy()
                    
        except FileNotFoundError:
             st.error(f"Error: El archivo de datos '{uploaded_file}' no fue encontrado. Asegúrate de que esté en el mismo directorio.")
        except Exception as e:
            st.error(f"Error al cargar/procesar el archivo: {e}")

    # --- VISUALIZACIONES ---
    if not df_filtrado.empty:
        
        # Funciones de utilidad para el análisis
        def clasificar_riesgo(db):
            if db < 85:
                return "Seguro"
            elif db < 100:
                return "Riesgo moderado"
            else:
                return "Peligroso"

        df_filtrado["riesgo"] = df_filtrado["_value"].apply(clasificar_riesgo)
        df_filtrado["hora"] = df_filtrado["_time"].dt.hour

        # Pestañas de visualización
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🌡️ Mapa de Calor", 
            "📈 Gráficos por Nodo", 
            "🧩 Comparación General", 
            "📊 Análisis Estadístico",
            "🚨 Riesgo por Hora"
        ])

        # --- TAB 1: Mapa de Sonido (Heatmap) ---
        with tab1:
            st.markdown("### Mapa de niveles de sonido (Heatmap)")
            st.markdown("""
            Este mapa de calor representa la intensidad del ruido registrado por cada nodo a lo largo del tiempo.
            * **Eje Horizontal:** Nodos (Sensores)
            * **Eje Vertical:** Hora del día
            * **Colores:** Nivel de sonido en decibeles (dB). Colores cálidos (rojos) indican niveles más altos.
            """)
            
            # Selector de paleta de colores
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                palette = st.selectbox(
                    "Seleccione la paleta de colores:",
                    options=['jet', 'viridis', 'plasma', 'inferno', 'magma', 'coolwarm', 'YlOrRd', 'RdYlBu_r'],
                    index=0,
                    key="palette_selector"
                )
            
            # Procesamiento de datos para la interpolación 
            X = df_filtrado['nodo'].astype(int).values
            fecha_base = pd.Timestamp(fecha).tz_localize('UTC')
            tiempos_segundos = (df_filtrado['_time'] - fecha_base).dt.total_seconds().values
            Z = df_filtrado['_value'].astype(float).values
            
            x_unique = np.unique(X)
            y_unique = np.unique(tiempos_segundos)
            
            # Crear una malla para la interpolación
            if len(x_unique) > 1 and len(y_unique) > 1:
                X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
                Z_grid = griddata((X, tiempos_segundos), Z, (X_grid, Y_grid), method='linear')
                Z_grid = np.nan_to_num(Z_grid, nan=np.nanmin(Z_grid) if np.nanmin(Z) is not np.nan else 0)
            else:
                # Caso de datos insuficientes para interpolación 2D
                Z_grid = Z.reshape(-1, 1) if Z.ndim == 1 else Z
                x_unique = X[:Z_grid.shape[1]]
                y_unique = tiempos_segundos[:Z_grid.shape[0]]

            # Configuración del gráfico
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Ajuste de etiquetas del eje Y para mostrar horas
            num_ticks = min(10, len(y_unique))
            yticks = np.linspace(0, len(y_unique) - 1, num=num_ticks, dtype=int)
            # Asegurar que el índice no exceda el tamaño de y_unique
            ytick_seconds = [y_unique[i] for i in yticks if i < len(y_unique)]
            yticklabels = [pd.to_datetime(sec, unit='s').strftime('%H:%M') for sec in ytick_seconds]

            # Heatmap con paleta seleccionada
            sb.heatmap(
                Z_grid, 
                cmap=palette, 
                xticklabels=x_unique, 
                yticklabels=False, 
                ax=ax,
                cbar_kws={'label': 'Nivel de sonido (dB)'}
            )
            
            ax.invert_yaxis()
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticklabels, rotation=0)
            ax.set_xlabel("Nodos")
            ax.set_ylabel("Hora (HH:MM)")
            
            st.pyplot(fig)
                        
        # --- TAB 2: Gráficos por nodo (Línea) ---
        with tab2:
            st.markdown("### Evolución Temporal del Ruido por Nodo")
            st.markdown("Gráficos de línea individuales para observar tendencias, picos o patrones específicos de ruido en cada sensor.")
            
            nodos_en_data = sorted(df_filtrado["nodo"].unique())
            for nodo in nodos_en_data:
                st.subheader(f"Nodo {nodo}")
                datos_nodo = df_filtrado[df_filtrado["nodo"] == nodo]
                st.line_chart(datos_nodo.set_index("_time")["_value"], height=200, use_container_width=True)

        # --- TAB 3: Comparación General (Línea) ---
        with tab3:
            st.markdown("### Comparación general de nodos en un solo gráfico")
            st.markdown("Visualización conjunta para detectar diferencias o similitudes en el comportamiento acústico entre distintas áreas.")
            df_pivot = df_filtrado.pivot(index='_time', columns='nodo', values='_value').sort_index()
            st.line_chart(df_pivot, height=400, use_container_width=True)

        # --- TAB 4: Análisis Estadístico ---
        with tab4:
            st.markdown("### Análisis Estadístico Básico por Nodo")
            resumen_estadistico = df_filtrado.groupby("nodo")["_value"].agg(
                Minimo="min",
                Maximo="max",
                Media="mean",
                Mediana="median",
                Conteo="count"
            ).round(2)
            st.dataframe(resumen_estadistico.T, use_container_width=True)
            
            st.markdown("### Gráfico de valores máximos por nodo")
            # Usar Matplotlib/Seaborn para un gráfico de barras más controlado
            fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
            sb.barplot(x=resumen_estadistico.index, y=resumen_estadistico["Maximo"], ax=ax_bar, palette="Blues_d")
            ax_bar.set_title("Nivel de Ruido Máximo por Nodo (dB)")
            ax_bar.set_xlabel("Nodo")
            ax_bar.set_ylabel("Decibeles (dB)")
            st.pyplot(fig_bar)
            
        # --- TAB 5: Riesgo por Hora ---
        with tab5:
            st.markdown("### 👂 Efectos del Ruido en la Audición y Niveles de Riesgo")
            st.markdown("""
            La sensibilidad al ruido varía, pero una exposición prolongada a altos niveles puede causar pérdida auditiva permanente. Proteger los oídos es crucial.
            """)
            
            st.markdown("#### 🔊 Rangos de niveles de sonido (dB) y Efectos")
            # Tabla de rangos de sonido
            st.table(pd.DataFrame({
                'Nivel (dB)': ['0–30 dB', '30–60 dB', '60–85 dB', '85–100 dB', '100–120+ dB'],
                'Ejemplo': ['Biblioteca, susurros', 'Conversación normal', 'Tráfico denso, aspiradora', 'Moto, concierto', 'Sirena ambulancia, martillo neumático'],
                'Efecto sobre la salud': ['Sin riesgo', 'Sin riesgo', 'Riesgo leve (si exposición prolongada)', 'Puede causar daño (exposición > 8h)', 'Daño auditivo posible en minutos']
            }))
            
            # Clasificación personalizada para el gráfico de pastel
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
            
            df_filtrado["rango"] = df_filtrado["_value"].apply(clasificar_rango)
            
            st.markdown("### Distribución de niveles de sonido por hora (clasificados por riesgo)")
            
            horas_disponibles = sorted(df_filtrado["hora"].unique())
            if horas_disponibles:
                hora_seleccionada = st.selectbox(
                    "Selecciona la hora que deseas visualizar (formato 24h):",
                    options=horas_disponibles,
                    index=min(len(horas_disponibles) - 1, 13), # Intentar seleccionar la 13:00 por defecto si existe
                    key="hora_selector"
                )
                
                df_hora = df_filtrado[df_filtrado["hora"] == hora_seleccionada]
                conteo = df_hora["rango"].value_counts().sort_index()
                
                colores = {
                    "0–30 dB: Sin riesgo": "#b3d9ff",
                    "30–60 dB: Sin riesgo": "#80bfff",
                    "60–85 dB: Riesgo leve": "#ffcc80",
                    "85–100 dB: Riesgo moderado": "#ff9966",
                    "100–120+ dB: Peligroso": "#ff4d4d"
                }
                
                # Crear gráfico de pastel
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(
                    conteo,
                    labels=conteo.index,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=[colores.get(cat, "#cccccc") for cat in conteo.index]
                )
                ax.set_title(f"Distribución de niveles de ruido a las {hora_seleccionada:02d}:00 hrs")
                ax.axis('equal') # Para que el pastel sea un círculo
                st.pyplot(fig)
            else:
                 st.warning("No hay datos para las horas disponibles en el rango seleccionado.")

    else:
        st.warning("No hay datos para visualizar. Por favor, verifica el archivo de datos o ajusta los parámetros de filtro en la barra lateral.")

# -----------------------------------------------------------------------------
