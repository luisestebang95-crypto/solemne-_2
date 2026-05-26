import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard API Gobierno", layout="wide")
st.title("📊 Dashboard Analítico - Datos Gobierno de Chile")
st.markdown("Proyecto Solemne II - Análisis de datos a través de API REST.")

# 2. Extracción de datos de la API
@st.cache_data
def fetch_data():
    url = "https://datos.gob.cl/api/3/action/datastore_search"
    # Usando un ID garantizado para asegurar la conexión exitosa
    params = {
        "resource_id": "d9631921-ebb9-4268-80d9-9a904e8cdcda", 
        "limit": 100
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data["result"]["records"])

try:
    df = fetch_data()
    
    # Limpieza básica
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    # 3. Interfaz y Filtros Dinámicos
    st.sidebar.header("Filtros del Sistema")
    
    columnas_texto = df.columns.tolist()
    columna_filtro = columnas_texto[0] 
    
    opciones = df[columna_filtro].unique().tolist()
    seleccion = st.sidebar.multiselect(f"Selecciona {columna_filtro}", opciones, default=opciones[:5])
    
    df_filtrado = df[df[columna_filtro].isin(seleccion)]
    
    # 4. KPIs
    st.subheader("Resumen General")
    st.metric("Total de Registros Analizados", len(df_filtrado))
    st.divider()
    
    # 5. Gráfico interactivo
    st.subheader(f"Distribución según {columna_filtro}")
    
    df_agrupado = df_filtrado[columna_filtro].value_counts().reset_index()
    df_agrupado.columns = [columna_filtro, 'Cantidad']
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df_agrupado[columna_filtro].astype(str), df_agrupado['Cantidad'], color='#3498db')
    plt.xticks(rotation=45, ha='right')
    ax.set_ylabel('Frecuencia')
    
    st.pyplot(fig)
    
    # 6. Tabla de datos
    st.divider()
    st.subheader("Base de Datos Cruda")
    st.dataframe(df_filtrado)

except Exception as e:
    st.error(f"Error de conexión: {e}")
