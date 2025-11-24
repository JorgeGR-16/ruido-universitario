import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import altair as alt # Necesario para el gráfico de análisis por hora
import plotly.express as px # Necesario para el gráfico de Distribución Lineal
from scipy.interpolate import griddata
import traceback

# --- CONFIGURACIÓN DE PÁGINA ---
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

# ---------------------------------------------------------------------
# BLOQUE GLOBAL: CARGA DE DATOS Y BARRA LATERAL 
# ---------------------------------------------------------------------

# 💡 INICIALIZACIÓN GLOBAL: df y df_filtrado siempre existen para evitar NameError
df_filtrado = pd.DataFrame() 
df = pd.DataFrame()
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQTQKOrkLvhvYM8wSl5TUCDSB-RioUR28159Cb0qqJzEoTOEJCoQC_xuy8-vdW_Yw/pub?output=csv"

# --- 1. FUNCIÓN DE CARGA DE DATOS ---
@st.cache_data(ttl=600)
def load_data(url):
    try:
        # Tu lógica para leer y limpiar el CSV
        df_raw = pd.read_csv(url, header=None, on_bad_lines='skip')
        required_cols = [4, 5, 8]
        if not all(col in df_raw.columns for col in required_cols):
            df_raw = pd.read_csv(url, header=None, on_bad_lines='skip', skiprows=6)
            if not all(col in df_raw.columns for col in [0, 1, 4]):
                return pd.DataFrame()
            df = df_raw.rename(columns={
                0: '_time', 1: '_value', 4: 'nodo'
            })[['_time', '_value', 'nodo']]
        else:
            df = df_raw.rename(columns={
                4: '_time', 5: '_value', 8: 'nodo'
            })[['_time', '_value', 'nodo']]
        
        df = df.dropna(subset=['_time', '_value', 'nodo'], how='any')
        df['_time'] = pd.to_datetime(df['_time'], utc=True, errors='coerce')
        df['_value'] = pd.to_numeric(df['_value'], errors='coerce')
        df['nodo'] = df['nodo'].astype(str)
        df = df.dropna(subset=['_time', '_value'])
        return df
    except Exception as e:
        # st.error(f"Error en load_data: {e}") # Descomentar para depuración
        return pd.DataFrame()

df = load_data(sheet_url)

# -------------------------------------------------------------
# 🟢 DEFINICIÓN DE LA FUNCIÓN DE POSICIÓN LINEAL (SOLUCIÓN DEL ERROR)
# -------------------------------------------------------------
def asignar_posicion_lineal(df):
    """
    Asigna una posición numérica (Posicion_X) a cada nodo basada en su ID, 
    asumiendo que están colocados linealmente del 1 al 39.
    """
    if df.empty:
        return df
        
    try:
        # Extraer solo dígitos del 'nodo' y convertir a entero (ej: 'nodo 1' -> 1)
        df['Posicion_X'] = df['nodo'].astype(str).str.replace(r'[^\d]', '', regex=True).astype(int)
    except Exception as e:
        # Fallback si los IDs no son numéricos
        st.error(f"Error al asignar Posicion_X. Asegúrate que los IDs de nodo sean números. Error: {e}")
        df['Posicion_X'] = 0
        
    return df
# -------------------------------------------------------------

# --- 2. BARRA LATERAL CON FILTROS ---
if not df.empty:
    with st.sidebar:
        st.header("Parámetros de entrada")
        
        # Manejo de fechas mínimas/máximas con seguridad
        tiempo_min = df['_time'].min().normalize()
        tiempo_max = df['_time'].max().normalize()
        
        if pd.isna(tiempo_min) or pd.isna(tiempo_max):
             st.warning("No se pudieron determinar las fechas mínima y máxima de los datos.")
             # Usar fecha actual como fallback si los datos están vacíos o corruptos
             tiempo_min = pd.Timestamp.now().normalize()
             tiempo_max = pd.Timestamp.now().normalize()
        
        fecha = st.date_input(
            "Fecha",
            value=tiempo_min.date(),
            min_value=tiempo_min.date(),
            max_value=tiempo_max.date()
        )
        # Filtros de HORA
        hora_inicio = st.time_input("Hora de inicio", value=pd.to_datetime('00:00').time())
        hora_fin = st.time_input("Hora de fin", value=pd.to_datetime('23:59').time())

        nodos_disponibles = sorted(df["nodo"].unique())
        nodos_seleccionados = st.multiselect(
            "Selecciona los nodos:",
            options=nodos_disponibles,
            default=nodos_disponibles
        )

        # 🔹 Filtrado por fecha, hora y nodo
        fecha_inicio_ts = pd.to_datetime(f"{fecha} {hora_inicio}").tz_localize('UTC')
        fecha_fin_ts = pd.to_datetime(f"{fecha} {hora_fin}").tz_localize('UTC')

        df_filtrado = df[
            (df['_time'] >= fecha_inicio_ts) &
            (df['_time'] <= fecha_fin_ts) &
            (df['nodo'].isin(nodos_seleccionados))
        ].copy() 
        
        # Verificación del filtro (Ayuda a diagnosticar el problema de los 20 nodos)
        nodos_en_filtro = df_filtrado["nodo"].nunique()
        st.write(f"📈 **{len(df_filtrado)}** registros después del filtrado.")
        st.info(f"Nodos únicos en el filtro: **{nodos_en_filtro}**.")

else:
    # Si la carga inicial falla, la barra lateral se muestra con una advertencia
    with st.sidebar:
        st.error("⚠️ No se pudieron cargar los datos iniciales desde Google Sheets. Verifique el enlace.")
        
# ---------------------------------------------------------------------
# FIN DEL BLOQUE GLOBAL
# ---------------------------------------------------------------------


# --- SECCIONES ---
if seccion_activa == "Introducción":
    st.markdown("### Introducción")
    st.markdown("""
    <div style='text-align: justify;'>
    El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros para medir los niveles sonoros.
    El ruido es un factor ambiental que puede influir negativamente en la calidad de vida, el rendimiento académico y la salud de estudiantes y personal universitario...
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    El **sonómetro** es un instrumento de lectura directa del nivel global de presión sonora. Sirve para medir la intensidad del sonido, expresada en **decibeles (dB)** y se utiliza para cuantificar el nivel de ruido en un lugar determinado, ya sea en control de ruido ambiental o laboral, o para evaluar la exposición sonora a la que están sometidas las personas.
    Su importancia radica en que permite cuantificar el ruido ambiental, evaluar el cumplimiento de normativas acústicas, diseñar políticas de control y mitigación del ruido, y proteger la salud pública y el bienestar social.
    Los niveles elevados de ruido pueden interferir en actividades cotidianas, como el trabajo o el descanso, y tienen un impacto directo en la salud pública.
    El ruido no controlado no solo afecta la calidad de vida de las personas, sino que también puede tener efectos negativos sobre la salud, como estrés, alteraciones del sueño y problemas auditivos.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    El ruido excesivo es una forma de contaminación ambiental que puede tener efectos perjudiciales sobre la salud humana, tanto a corto como a largo plazo. Los sonómetros son instrumentos clave para medir, controlar y prevenir estos riesgos.
    A continuación, se explican diferentes riesgos contra la salud humana:

    - **Pérdida auditiva inducida por ruido**
    - **Estrés, irritabilidad y fatiga mental**
    - **Aumento del riesgo cardiovascular**
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: justify;'><br>
    Los sonómetros tienen aplicaciones en diversas áreas, como:
    
    - **Salud pública:** se utilizan para medir los niveles de ruido en hospitales, escuelas y vecindarios.
    - **Industria y construcción:** para monitorear el ruido en fábricas y sitios de construcción, asegurando la seguridad de los trabajadores y el cumplimiento de las regulaciones.
    - **Transporte:** se emplean en la medición del ruido de tráfico, ferroviario y aéreo, con el fin de minimizar su impacto en las comunidades cercanas.
    - **Investigación acústica:** en estudios científicos y de ingeniería, se utilizan para evaluar la propagación del sonido y el diseño de soluciones para reducir el ruido.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    En el ruido hay diferentes objetos y lugares que causan volumen excesivo con 2 fuentes que pueden proporcionar el sonido: fuentes fijas y móviles.
    Las fuentes fijas se encuentran en espacios públicos en sitios de construcción, manufactura industrial y empresa de servicios. Las fuentes móviles se ecuentran por medios de transporte.
    La norma ambiental tiene límites máximos en decibeles que debemos seguir en las fuentes fijas por niveles de emisiones sonoras.
    El punto de emisión nos permite calibrar el ruido para supervisar la vibración, pero se excluyen las normas móviles. La Organización Mundial de la salud dicen que modifican la intensidad del sonido al oír ruidos excesivos subiéndolos.
    La afectación por el ruido se divide en primarios y secundarios. Los primarios se pueden percibir al revelar el ruido alterando al ser humano por 8 horas
    y los secundarios tienen gran alcance que pueden ocasionar en enfermedades psicosomáticas.
    <br><br>
    La exposición constante al ruido puede tener serias consecuencias tanto físicas como psicológicas. A nivel emocional, puede generar inensibilidad que sucede a nuestro alrededor,
    promover el aislamiento social e incrementar el estrés, lo que deriva en conductas agresivas o intolerantes. En el plano físico, el ruido interfiere con el descanso adecuado,
    afectando la recuperación del cuerpo, incluso cuando es de baja intensidad. También puede provocar transtornos relacionados con la tensión nerviosa como
    problemas circulatorios, presión arterial alta y alteraciones digestivas.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: justify;'><br>
    Las siguientes leyes se deben cumplir y seguir para los ciudadanos:

    - El artículo 4° establece varios derechos fundamentales para todos los mexicanos.
    - La Ley Ambiental de Protección a la Tierra permite que todos los ciudadanos deben concluir el límite máximo de emisiones sonoras.
    - Los límites se deben continuar de acuerdo a la norma ambiental para que los sonómetros guarden los sonidos producidos.

    En la Ciudad de México, la Ley de Establecimientos Mercantiles obliga a los negocios a evitar la emisión de ruido al exterior e instalar aislamiento acústico, además de
    cumplir con límites de sonido en su interior. La norma NADF-005-AMBT-2013 regula el ruido en el exterior. También se prohibe el uso de bocinas o música en zonas de enseres.
    Por su parte, la Ley de Cultura Cívica considera infracción generar ruidos que afecten la tranquilidad o salud.
    Las sanciones por incumplimiento van desde multas, clausuras, arrestos administrativos y otras medidas legales.
    También deben escuchar y responder las denuncias de los ciudadanos sobre las emisiones sonoras que generan en sus domicilios si sobrepasan los Límites Máximos Permisibles
    por la norma ambiental NADF-005-AMBT-2013 porque si omiten las quejas de los ciudadanos están desobedeciendo las precauciones que pueden suspender sus actividades
    y recibir informes por la Secretaría de Medio Ambiente de la Ciudad de México (SEDEMA).
    <br><br>
    Tienen campañas de difusión para la denuncia del ruido que deben decir los ressponables para inspeccionar la contaminación acústica.
    En 2019, PAOT realizó más de 50 precauciones en los comerciales que cada acción se resuelve los encargados en reformar las emisiones sonoras y que sigan el límite mínimos por la norma ambiental NADF-005.
    En la guía del PAOT brinda propietarios, administradores y responsables de comercios especialmente restaurantes y bares, una herramienta práctica para controlar y mitigar las emisiones sonoras, 
    facilitando el cumplimiento de la normativa ambiental vigente en la Ciudad de México (NADF‑005‑AMBT‑2013).
    Hay diferentes contenidos que se deben solucionar para el ruido:

    - Vías de transmisión
    - Mejora de aislamiento en los edificios
    - Instalación y ubicación en máquinas ruidosas, sistemas de audio y ruidos de impacto

    La Procuraduría Ambiental y del Ordenamiento Territorial de la Ciudad de México (PAOT) examina de que todo sea legal y que podemos denunciar por
    internet, teléfono y hablar de forma presencial en la dirección indicada y horario.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Niveles_de_ruido.jpg", use_container_width=True)

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

    st.markdown("### 2.1 Objetivo General")
    st.markdown("Diseñar y construir un sonómetro digital que permita medir niveles de presión sonora en tiempo real, facilitando el monitoreo del ruido ambiental con precisión.")
    
    st.markdown("### 2.2 Objetivos específicos")
    st.markdown("* Seleccionar y calibrar un sensor de sonido compatible con microcontroladores.")
    st.markdown("* Programar el microcontrolador para interpretar los datos de decibeles(dB) y mostrarlos en una interfaz digital.")
    st.markdown("* Integrar un sistema de visualización en pantalla.")
    st.markdown("* Evaluar el desempeño del prototipo frente a un sonómetro comercial.")
    st.markdown("* Medir los niveles de ruido en diferentes puntos del área usando un sonómetro de clase adecuada.")
    st.markdown("* Registrar y analizar los datos obtenidos para identificar zonas con niveles de ruido.")
    st.markdown("* Comparar los resultados con los límites establecidos en las normas oficiales.")
    st.markdown("* Fomentar la concientización sobre la importancia del control del ruido en espacios públicos, escolares o laborales.")

elif seccion_activa == "Desarrollo":
    st.markdown("### Desarrollo del prototipo")
    st.header("*En esta parte veremos el desarrollo del prototipo y su construcción.*")

    st.markdown("""
    <div style='text-align: justify;'>
    La construcción de un sonómetro es un proceso complejo que involucra varias partes, tanto electrónicas como mecánicas, que trabajan juntas para medir el sonido de manera precisa.
    A continuación, se explican en detalle los elementos que componen un sonómetro:
    
    - **Micrófono:** se encarga de captar las ondas sonoras del ambiente y convertirlas en una señal eléctrica.
    - **Amplificador:** La señal eléctrica generada por el micrófono es extremadamente débil, por lo que debe ser amplificada para que sea procesada correctamente. Este proceso lo lleva a cabo el pre-amplificador, que amplifica la señal de manera lineal sin distorsionarla.
    - **Filtros de frecuencia:** simula la percepción del oído humano o adaptarse a diferentes tipos de medición.
    - **Circuito de procesamiento de señales:** cuando la señal ha sido amplificada y filtrada, pasa al circuito de procesamiento que se encarga de convertir la señal analógica en digital y realizar los cálculos necesarios para determinar el nivel de presión sonora.
    - **Pantalla de visualización:** es el componente que permite visualizar los resultados de las mediciones. Dependiendo del modelo del sonómetro, puede ser una pantalla LCD o LED.
    - **Controladores y botones:** tiene una serie de botones o controles para que el usuario ajuste las opciones según sus necesidades.
    - **Fuente de alimentación:** funcionan con baterías recargables o pilas de 9V. Algunos modelos más grandes pueden tener una fuente de alimentación externa. La duración de la batería es crucial para la portabilidad del sonómetro, especialmente en mediciones de campo.

    Lo siguiente es mostrar un manual para construir un sonómetro y su diseño.
    </div>
    """, unsafe_allow_html=True)
    
    
    st.markdown("### 3.1 Diseño del modelo ESP32")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("ESP32.jpg", use_container_width=True)
        
    st.markdown("### 3.2 Construcción del sonómetro")
    st.markdown("### 3.2.1 Materiales necesarios")
    st.markdown("""
            | Componente      | Descripción                                     |
            |----------------|-------------------------------------|
            | ESP32 T3 V1.6.1 | Microcontrolador                    | 
            | Sensor de sonido (micrófono)      | Detecta presión sonora para convertirla a señal analógica      | 
            | Pantalla OLED  | Muestra el nivel de decibeles en tiempo real    | 
            | Jumpers hembra-hembra/ macho-hembra | Para las conexiones entre módulos                       | 
            | Pulsador (botón de control) | Encendido, reinicio o cambio de modo |
            | Caja impresa en 3D | Para encapsular el dispositivo |
            | Fuente de alimentación (batería o alimentación USB) | Para darle energía al ESP32 | 
    """)
    st.markdown("### 3.2.2 Procedimiento de armado")
    st.markdown("""
    <div style='text-align: justify;'>
    
    1. **Conexión del sensor de sonido**
        | Sensor     | ESP32 T3 V1.6.1                                 |
        |----------------|-------------------------------------|
        | VCC      | 3.3V                | 
        | GND      | GND                 | 
        | A0 (salida analógica)        | GPIO 34 (u otro pin analógico)      |
        
    2. **Conexión de la pantalla OLED**
        | OLED SSD1306     | ESP32 T3 V1.6.1                                 |
        |----------------|-------------------------------------|
        | VCC      | 3.3V                | 
        | GND      | GND                 | 
        | SDA     | GPIO 21           |
        | SCL     | GPIO 22           |
        
    3. **Botón de control**
    - Conectar un botón entre un pin digital y GND. Actúa como encendido o reinicio de mediciones
    
    4. **Código en Arduino**
    
    5. **Montaje físico y carcasa**
    - Usa una impresora 3D para crear la carcasa
    - Inserta los módulos asegurándolos con presión
    - Dejar espacio para los conectores, pantalla visible y ventilación del micrófono
    - Cerrar el circuito y conectar la alimentación
    </div>
    """, unsafe_allow_html=True)
    
    

elif seccion_activa == "Resultados":
    st.markdown("### Resultados")
    
    if not df_filtrado.empty:
        # ⚠️ PASO CRUCIAL: Asignar la posición lineal a cada nodo
        df_filtrado = asignar_posicion_lineal(df_filtrado)
        
        # --- 1. PREPARACIÓN DE DATOS ---
        
        # 1.1 Función de clasificación de riesgo
        def clasificar_riesgo(db):
            if db < 85:
                return "Seguro"
            elif db < 100:
                return "Riesgo moderado"
            else:
                return "Peligroso"

        df_filtrado["riesgo"] = df_filtrado["_value"].apply(clasificar_riesgo)
        
        # 1.2 Agregamos la columna 'hora' para análisis
        df_filtrado["hora"] = df_filtrado["_time"].dt.hour 

        # --- 2. DEFINICIÓN DE PESTAÑAS (TABS) ---
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Distribución Lineal",  # Nombre cambiado
            "📈 Análisis Temporal (Nodos)", 
            "📈 Análisis Temporal (Horas)",
            "📊 Histograma de Amplitudes", 
            "📋 Descripción de Datos"
        ])

        # --- 3. CONTENIDO DE LAS PESTAÑAS ---

        with tab1:
            st.markdown("#### Nivel de sonido promedio a lo largo de la pared")
            
            # Agrupamos los datos para obtener el promedio por posición
            df_lineal = df_filtrado.groupby('Posicion_X')['_value'].mean().reset_index()
            df_lineal.rename(columns={'_value': 'Nivel Promedio (dB)'}, inplace=True)
            
            # Creamos un gráfico de dispersión simple para la distribución lineal
            # El color y tamaño varían según el nivel de ruido, mostrando el "calor" lineal.
            fig = px.scatter(
                df_lineal,
                x='Posicion_X',
                y='Nivel Promedio (dB)',
                size='Nivel Promedio (dB)', 
                color='Nivel Promedio (dB)', 
                color_continuous_scale=px.colors.sequential.Inferno,
                labels={
                    "Posicion_X": "Posición del Sensor (1 = inicio, 39 = final)",
                    "Nivel Promedio (dB)": "Nivel Promedio (dB)"
                },
                title="Distribución del Nivel de Sonido a lo Largo de la Pared"
            )
            
            # Ajuste de ejes para claridad
            fig.update_xaxes(tick0=1, dtick=1)
            st.plotly_chart(fig, use_container_width=True)


        with tab2:
            st.markdown("#### Evolución temporal del sonido por nodo")
            # 💡 Puedes agregar aquí un gráfico de línea (ej: Plotly o Altair) mostrando _value vs _time, coloreado por 'nodo'
            st.warning("⚠️ Aquí va tu código del gráfico de nodos vs tiempo usando `df_filtrado`")

        with tab3:
            st.markdown("#### Niveles de sonido promedio por hora del día")
            
            df_hora = df_filtrado.groupby("hora")["_value"].mean().reset_index()
            df_hora.columns = ["Hora del Día", "Nivel Promedio (dB)"]
            
            chart_hora = alt.Chart(df_hora).mark_line(point=True).encode(
                x=alt.X("Hora del Día", bin=True, title="Hora del Día"),
                y=alt.Y("Nivel Promedio (dB)", title="Nivel Promedio (dB)"),
                tooltip=["Hora del Día", "Nivel Promedio (dB)"]
            ).properties(
                title="Nivel de Sonido Promedio por Hora"
            )
            st.altair_chart(chart_hora, use_container_width=True)

        with tab4:
            st.markdown("#### Distribución de Amplitudes")
            # 💡 Puedes agregar aquí un histograma simple (ej: Plotly o Matplotlib) de la columna '_value'
            st.warning("⚠️ Aquí va tu código del histograma usando `df_filtrado`")

        with tab5:
            st.markdown("#### Resumen Estadístico de los Datos Filtrados")
            st.dataframe(df_filtrado.describe())
            
    else:
        st.error("No hay datos para los parámetros seleccionados. Por favor, ajusta la **Fecha** o el **rango de Horas** en la barra lateral izquierda.")
