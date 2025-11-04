if seccion_activa == "Resultados":
        st.markdown("### Resultados")
    
        with st.sidebar:
            st.header("Parámetros de entrada")
        
            # --- CARGA AUTOMÁTICA DESDE GOOGLE SHEETS ---
            sheet_url = "https://docs.google.com/spreadsheets/d/1-9FdzIdIz-F7UYuK8DFdBjzPwS9-J3FLV05S_yTaOGE/gviz/tq?tqx=out:csv&sheet=consulta29-30"
        
            try:
                # --- MODIFICACIÓN CLAVE: USAR 'df' EN LUGAR DE 'f' ---
                df = pd.read_csv(sheet_url, skiprows=6, header=None) 
                
                # Renombrar columnas manualmente según su posición 
                # Ahora 'df' está definido y se puede usar en el .rename()
                df = df.rename(columns={ 
                    4: '_time', # Columna E → tiempo 
                    5: '_value', # Columna F → nivel de sonido (Leq) 
                    8: 'nodo' # Columna I → número de nodo 
                }) 
                # Conservar solo las columnas que interesan 
                df = df[['_time', '_value', 'nodo']] 
                # Convertir tipos de datos 
                df['_time'] = pd.to_datetime(df['_time'], utc=True, errors='coerce') 
                df['_value'] = pd.to_numeric(df['_value'], errors='coerce') 
                df['nodo'] = df['nodo'].astype(str)
    
        
                # ... (resto de tu código de validación y filtrado)
                # ...
                
            except Exception as e:
                st.error(f"Error al cargar el archivo desde Google Sheets: {e}")
                df_filtrado = pd.DataFrame()
