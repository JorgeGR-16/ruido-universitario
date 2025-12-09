import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from scipy.interpolate import griddata
import os # Importar os para manejo de rutas de archivos

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
        st.image("UAMAZC.jpg", use_container_width=True)
    except FileNotFoundError:
        st.warning("Archivo UAMAZC.jpg no encontrado. Asegúrate de que esté en el directorio correcto.")
        
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
    El presente proyecto tiene como objetivo investigar cómo afecta el ruido ambiental en una zona específica de la universidad mediante la instalación y uso de sonómetros para medir los niveles sonoros. El ruido es un factor ambiental que puede influir negativamente en la calidad de vida, el rendimiento académico y la salud de estudiantes y personal universitario...
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    El **sonómetro** es un instrumento de lectura directa del nivel global de presión sonora. Sirve para medir la intensidad del sonido, expresada en **decibeles (dB)** y se utiliza para cuantificar el nivel de ruido en un lugar determinado, ya sea en control de ruido ambiental o laboral, o para evaluar la exposición sonora a la que están sometidas las personas. Su importancia radica en que permite cuantificar el ruido ambiental, evaluar el cumplimiento de normativas acústicas, diseñar políticas de control y mitigación del ruido, y proteger la salud pública y el bienestar social. Los niveles elevados de ruido pueden interferir en actividades cotidianas, como el trabajo o el descanso, y tienen un impacto directo en la salud pública. El ruido no controlado no solo afecta la calidad de vida de las personas, sino que también puede tener efectos negativos sobre la salud, como estrés, alteraciones del sueño y problemas auditivos.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    El ruido excesivo es una forma de contaminación ambiental que puede tener efectos perjudiciales sobre la salud humana, tanto a corto como a largo plazo. Los sonómetros son instrumentos clave para medir, controlar y prevenir estos riesgos. A continuación, se explican diferentes riesgos contra la salud humana:
    * **Pérdida auditiva inducida por ruido**
    * **Estrés, irritabilidad y fatiga mental**
    * **Aumento del riesgo cardiovascular**
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    Los sonómetros tienen aplicaciones en diversas áreas, como:
    * **Salud pública:** se utilizan para medir los niveles de ruido en hospitales, escuelas y vecindarios.
    * **Industria y construcción:** para monitorear el ruido en fábricas y sitios de construcción, asegurando la seguridad de los trabajadores y el cumplimiento de las regulaciones.
    * **Transporte:** se emplean en la medición del ruido de tráfico, ferroviario y aéreo, con el fin de minimizar su impacto en las comunidades cercanas.
    * **Investigación acústica:** en estudios científicos y de ingeniería, se utilizan para evaluar la propagación del sonido y el diseño de soluciones para reducir el ruido.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    En el ruido hay diferentes objetos y lugares que causan volumen excesivo con 2 fuentes que pueden proporcionar el sonido: **fuentes fijas** y **móviles**. Las fuentes fijas se encuentran en espacios públicos en sitios de construcción, manufactura industrial y empresa de servicios. Las fuentes móviles se encuentran por medios de transporte. La norma ambiental tiene límites máximos en decibeles que debemos seguir en las fuentes fijas por niveles de emisiones sonoras. El punto de emisión nos permite calibrar el ruido para supervisar la vibración, pero se excluyen las normas móviles. La Organización Mundial de la salud dicen que modifican la intensidad del sonido al oír ruidos excesivos subiéndolos. La afectación por el ruido se divide en **primarios** y **secundarios**. Los primarios se pueden percibir al revelar el ruido alterando al ser humano por 8 horas y los secundarios tienen gran alcance que pueden ocasionar en enfermedades psicosomáticas. <br><br>
    La exposición constante al ruido puede tener serias consecuencias tanto físicas como psicológicas. A nivel emocional, puede generar inensibilidad que sucede a nuestro alrededor, promover el aislamiento social e incrementar el estrés, lo que deriva en conductas agresivas o intolerantes. En el plano físico, el ruido interfiere con el descanso adecuado, afectando la recuperación del cuerpo, incluso cuando es de baja intensidad. También puede provocar transtornos relacionados con la tensión nerviosa como problemas circulatorios, presión arterial alta y alteraciones digestivas.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: justify;'><br>
    Las siguientes leyes se deben cumplir y seguir para los ciudadanos:
    * El **artículo 4°** establece varios derechos fundamentales para todos los mexicanos.
    * La **Ley Ambiental de Protección a la Tierra** permite que todos los ciudadanos deben concluir el límite máximo de emisiones sonoras.
    * Los límites se deben continuar de acuerdo a la norma ambiental para que los sonómetros guarden los sonidos producidos. En la Ciudad de México, la **Ley de Establecimientos Mercantiles** obliga a los negocios a evitar la emisión de ruido al exterior e instalar aislamiento acústico, además de cumplir con límites de sonido en su interior. La norma **NADF-005-AMBT-2013** regula el ruido en el exterior. También se prohibe el uso de bocinas o música en zonas de enseres. Por su parte, la **Ley de Cultura Cívica** considera infracción generar ruidos que afecten la tranquilidad o salud. Las sanciones por incumplimiento van desde multas, clausuras, arrestos administrativos y otras medidas legales. También deben escuchar y responder las denuncias de los ciudadanos sobre las emisiones sonoras que generan en sus domicilios si sobrepasan los Límites Máximos Permisibles por la norma ambiental NADF-005-AMBT-2013 porque si omiten las quejas de los ciudadanos están desobedeciendo las precauciones que pueden suspender sus actividades y recibir informes por la Secretaría de Medio Ambiente de la Ciudad de México (**SEDEMA**). <br><br>
    Tienen campañas de difusión para la denuncia del ruido que deben decir los responsables para inspeccionar la contaminación acústica. En 2019, PAOT realizó más de 50 precauciones en los comerciales que cada acción se resuelve los encargados en reformar las emisiones sonoras y que sigan el límite mínimos por la norma ambiental NADF-005. En la guía del PAOT brinda propietarios, administradores y responsables de comercios especialmente restaurantes y bares, una herramienta práctica para controlar y mitigar las emisiones sonoras, facilitando el cumplimiento de la normativa ambiental vigente en la Ciudad de México (NADF‑005‑AMBT‑2013). Hay diferentes contenidos que se deben solucionar para el ruido:
    * Vías de transmisión
    * Mejora de aislamiento en los edificios
    * Instalación y ubicación en máquinas ruidosas, sistemas de audio y ruidos de impacto
    La **Procuraduría Ambiental y del Ordenamiento Territorial de la Ciudad de México (PAOT)** examina de que todo sea legal y que podemos denunciar por internet, teléfono y hablar de forma presencial en la dirección indicada y horario.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("Niveles_de_ruido.jpg", use_container_width=True)
        except FileNotFoundError:
            st.warning("Archivo Niveles_de_ruido.jpg no encontrado.")

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
    * $P_0 = 20\,\mu\text{Pa}$: presión sonora de referencia
    """, unsafe_allow_html=True)

    st.markdown("### 1.2 Diagrama del dispositivo.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("Diagrama.png", use_container_width=True)
        except FileNotFoundError:
            st.warning("Archivo Diagrama.png no encontrado.")


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
    La construcción de un sonómetro es un proceso complejo que involucra varias partes, tanto electrónicas como mecánicas, que trabajan juntas para medir el sonido de manera precisa. A continuación, se explican en detalle los elementos que componen un sonómetro:
    * **Micrófono:** se encarga de captar las ondas sonoras del ambiente y convertirlas en una señal eléctrica.
    * **Amplificador:** La señal eléctrica generada por el micrófono es extremadamente débil, por lo que debe ser amplificada para que sea procesada correctamente. Este proceso lo lleva a cabo el pre-amplificador, que amplifica la señal de manera lineal sin distorsionarla.
    * **Filtros de frecuencia:** simula la percepción del oído humano o adaptarse a diferentes tipos de medición.
    * **Circuito de procesamiento de señales:** cuando la señal ha sido amplificada y filtrada, pasa al circuito de procesamiento que se encarga de convertir la señal analógica en digital y realizar los cálculos necesarios para determinar el nivel de presión sonora.
    * **Pantalla de visualización:** es el componente que permite visualizar los resultados de las mediciones. Dependiendo del modelo del sonómetro, puede ser una pantalla LCD o LED.
    * **Controladores y botones:** tiene una serie de botones o controles para que el usuario ajuste las opciones según sus necesidades.
    * **Fuente de alimentación:** funcionan con baterías recargables o pilas de 9V. Algunos modelos más grandes pueden tener una fuente de alimentación externa. La duración de la batería es crucial para la portabilidad del sonómetro, especialmente en mediciones de campo.
    Lo siguiente es mostrar un manual para construir un sonómetro y su diseño.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 3.1 Diseño del modelo ESP32")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("ESP32.jpg", use_container_width=True)
        except FileNotFoundError:
            st.warning("Archivo ESP32.jpg no encontrado.")

    st.markdown("### 3.2 Construcción del sonómetro")

    st.markdown("### 3.2.1 Materiales necesarios")
    st.markdown("""
| Componente | Descripción |
|---|---|
| ESP32 T3 V1.6.1 | Microcontrolador |
| Sensor de sonido (micrófono) | Detecta presión sonora para convertirla a señal analógica |
| Pantalla OLED | Muestra el nivel de decibeles en tiempo real |
| Jumpers hembra-hembra/ macho-hembra | Para las conexiones entre módulos |
| Pulsador (botón de control) | Encendido, reinicio o cambio de modo |
| Caja impresa en 3D | Para encapsular el dispositivo |
| Fuente de alimentación (batería o alimentación USB) | Para darle energía al ESP32 |
""")

    st.markdown("### 3.2.2 Procedimiento de armado")
    st.markdown("""
    <div style='text-align: justify;'>
    1. **Conexión del sensor de sonido**

| Sensor | ESP32 T3 V1.6.1 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| A0 (salida analógica) | GPIO 34 (u otro pin analógico) |

    2. **Conexión de la pantalla OLED**

| OLED SSD1306 | ESP32 T3 V1.6.1 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

    3. **Botón de control** - Conectar un botón entre un pin digital y GND. Actúa como encendido o reinicio de mediciones
    4. **Código en Arduino**
    5. **Montaje físico y carcasa** - Usa una impresora 3D para crear la carcasa - Inserta los módulos asegurándolos con presión - Dejar espacio para los conectores, pantalla visible y ventilación del micrófono - Cerrar el circuito y conectar la alimentación
    </div>
    """, unsafe_allow_html=True)


elif seccion_activa == "Resultados":
    st.markdown("### Resultados")

    # Ruta fija al archivo CSV
    uploaded_file = "consultaprueba2.csv"

    # Inicializar df_filtrado como DataFrame vacío para el scope general
    df_filtrado = pd.DataFrame()

    try:
        # Verificar si el archivo existe
        if not os.path.exists(uploaded_file):
            st.error(f"El archivo de datos '{uploaded_file}' no fue encontrado.")
        else:
            def clean_cols(cols):
                return [str(c).strip().replace('\ufeff', '') for c in cols]

            df_try = pd.read_csv(uploaded_file, dtype=str)
            df_try.columns = clean_cols(df_try.columns)
            
            columnas_requeridas = ['_time', 'nodo', '_value']
            if not all(any(req == c.lower() for c in df_try.columns) for req in columnas_requeridas):
                df_try = pd.read_csv(uploaded_file, skiprows=3)
                df_try.columns = clean_cols(df_try.columns)
            
            cols_lower = {c.lower().strip().replace('\ufeff',''): c for c in df_try.columns}
            mapping = {}
            if '_time' in cols_lower: mapping[cols_lower['_time']] = '_time'
            if 'time' in cols_lower and '_time' not in cols_lower: mapping[cols_lower['time']] = '_time'
            if '_value' in cols_lower: mapping[cols_lower['_value']] = '_value'
            elif 'value' in cols_lower: mapping[cols_lower['value']] = '_value'
            if 'nodo' in cols_lower: mapping[cols_lower['nodo']] = 'nodo'
            elif 'node' in cols_lower: mapping[cols_lower['node']] = 'nodo'

            df = df_try.rename(columns=mapping)

            if not all(col in df.columns for col in columnas_requeridas):
                st.error("El archivo no contiene las columnas necesarias (_time, nodo, _value).")
            else:
                df['_value'] = pd.to_numeric(df['_value'], errors='coerce')
                df = df.dropna(subset=['_time', '_value', 'nodo']).copy()

                # --- CORRECCIÓN COMPLETA DE ZONA HORARIA ---
                df['_time'] = pd.to_datetime(df['_time'], errors='coerce')

                # Si viene sin tz, asumir UTC
                if df['_time'].dt.tz is None:
                    df['_time'] = df['_time'].dt.tz_localize('UTC', ambiguous='NaT', nonexistent='shift_forward')
                else:
                    try:
                        df['_time'] = df['_time'].dt.tz_convert('UTC')
                    except:
                        pass

                # Convertir a México UNA SOLA VEZ
                df['_time'] = df['_time'].dt.tz_convert('America/Mexico_City')

                if df['_time'].isna().all():
                    st.error("No se pudieron interpretar las fechas en la columna '_time'.")
                else:
                    # --- SIDEBAR DE FILTROS ---
                    with st.sidebar:
                        st.header("Parámetros de entrada")

                        tiempo_min = df['_time'].min()
                        tiempo_max = df['_time'].max()

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

                        # --- FILTRADO AHORA 100% EN MÉXICO ---
                        fecha_inicio = pd.to_datetime(f"{fecha} {hora_inicio}").tz_localize('America/Mexico_City')
                        fecha_fin = pd.to_datetime(f"{fecha} {hora_fin}").tz_localize('America/Mexico_City')

                        df_filtrado = df[
                            (df['_time'] >= fecha_inicio) &
                            (df['_time'] <= fecha_fin) &
                            (df['nodo'].astype(str).isin(nodos_seleccionados))
                        ].copy()
                    # --- FIN SIDEBAR ---
    except Exception as e:
        st.error(f"Error al cargar o procesar el archivo: {e}")

    if not df_filtrado.empty:

        # Clasificación riesgo auditivo
        def clasificar_riesgo(db):
            if db < 85: return "Seguro"
            elif db < 100: return "Riesgo moderado"
            else: return "Peligroso"

        df_filtrado["riesgo"] = df_filtrado["_value"].apply(clasificar_riesgo)
        df_filtrado["hora"] = df_filtrado["_time"].dt.hour

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Mapa de Sonido", 
            "📈 Gráficos por nodo", 
            "🧩 Comparación general", 
            "📊 Análisis estadístico", 
            "🧨 Riesgo por hora"
        ])

        # :::::::::::::::::::::::::::::::::::::::::::::::::::
        #                   TAB 1: HEATMAP
        # :::::::::::::::::::::::::::::::::::::::::::::::::::
        with tab1:
            st.markdown("### Mapa de niveles de sonido")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                palette = st.selectbox(
                    "Seleccione la paleta de colores:",
                    options=['jet', 'viridis', 'plasma', 'inferno', 'magma', 'coolwarm', 'YlOrRd', 'RdYlBu_r'],
                    index=0,
                )

            try:
                X = df_filtrado['nodo'].astype(int).values
            except ValueError:
                X = df_filtrado['nodo'].astype('category').cat.codes.values + 1

            # --- AHORA CALCULAMOS EL TIEMPO EN SEGUNDOS EN MÉXICO ---
            fecha_inicio_dia = pd.to_datetime(f"{fecha} 00:00").tz_localize('America/Mexico_City')
            tiempos_segundos = (df_filtrado['_time'] - fecha_inicio_dia).dt.total_seconds().values

            Z = df_filtrado['_value'].astype(int).values

            x_unique = np.unique(X)
            y_unique = np.unique(tiempos_segundos)

            if len(x_unique) > 1 and len(y_unique) > 1:

                X_grid, Y_grid = np.meshgrid(x_unique, y_unique)
                Z_grid = griddata((X, tiempos_segundos), Z, (X_grid, Y_grid), method='linear')
                Z_grid = np.nan_to_num(Z_grid, nan=np.nanmin(Z_grid))

                fig, ax = plt.subplots(figsize=(10, 6))

                yticks_indices = np.linspace(0, len(y_unique)-1, num=10, dtype=int)
                yticks_values = y_unique[yticks_indices]
                yticklabels = [pd.to_datetime(t, unit='s').strftime('%H:%M') for t in yticks_values]

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

                cbar = ax.collections[0].colorbar
                cbar.set_label('Nivel de sonido (dB)', rotation=270, labelpad=20)

                st.pyplot(fig)

            else:
                st.warning("Datos insuficientes para generar el mapa de calor.")


        # :::::::::::::::::::::::::::::::::::::::::::::::::::
        #          LAS OTRAS TABS NO NECESITAN CAMBIOS
        # :::::::::::::::::::::::::::::::::::::::::::::::::::

        # TAB2
        with tab2:
            st.markdown("#### Evolución temporal por nodo")
            for nodo in sorted(df_filtrado["nodo"].astype(str).unique()):
                st.subheader(f"Nodo {nodo}")
                datos_nodo = df_filtrado[df_filtrado["nodo"].astype(str) == nodo]
                st.line_chart(datos_nodo.set_index("_time")["_value"], height=200, use_container_width=True)

        # TAB3
        with tab3:
            st.markdown("### Comparación general de nodos en un solo gráfico")
            df_pivot = df_filtrado.pivot(index='_time', columns='nodo', values='_value').sort_index()
            df_pivot.columns = df_pivot.columns.astype(str)
            st.line_chart(df_pivot, height=300, use_container_width=True)

        # TAB4
        with tab4:
            st.markdown("### Análisis estadístico básico por nodo")
            resumen_estadistico = df_filtrado.groupby("nodo")["_value"].agg(
                Minimo="min", Maximo="max", Media="mean", Mediana="median", Conteo="count"
            ).round(2)
            st.dataframe(resumen_estadistico)

        # TAB5
        with tab5:
            st.markdown("### Distribución de niveles de sonido por hora")
            def clasificar_rango(db):
                if db < 30: return "0–30 dB: Sin riesgo"
                elif db < 60: return "30–60 dB: Sin riesgo"
                elif db < 85: return "60–85 dB: Riesgo leve"
                elif db < 100: return "85–100 dB: Riesgo moderado"
                else: return "100–120+ dB: Peligroso"

            df_filtrado["rango"] = df_filtrado["_value"].apply(clasificar_rango)

            horas_disponibles = sorted(df_filtrado["hora"].unique())
            if horas_disponibles:
                hora_seleccionada = st.selectbox("Selecciona hora:", options=horas_disponibles)
                df_hora = df_filtrado[df_filtrado["hora"] == hora_seleccionada]
                conteo = df_hora["rango"].value_counts().sort_index()

                if not conteo.empty:
                    colores = {
                        "0–30 dB: Sin riesgo": "#b3d9ff",
                        "30–60 dB: Sin riesgo": "#80bfff",
                        "60–85 dB: Riesgo leve": "#ffcc80",
                        "85–100 dB: Riesgo moderado": "#ff9966",
                        "100–120+ dB: Peligroso": "#ff4d4d"
                    }
                    colores_graf = [colores[c] for c in conteo.index]

                    fig, ax = plt.subplots()
                    ax.pie(conteo, labels=conteo.index, autopct="%1.1f%%",
                           startangle=90, colors=colores_graf)
                    ax.axis("equal")
                    st.pyplot(fig)

    else:
        st.warning("No hay datos para los parámetros seleccionados.")

