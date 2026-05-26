import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt

# 1. Configuración inicial de la página
st.set_page_config(page_title="Dashboard Energético", layout="wide")
st.title("⚡ Dashboard de Generación Eléctrica - Chile")
st.markdown("Proyecto Solemne II - Análisis de datos a través de la API del Gobierno de Chile.")

# 2. Función para extraer datos de la API
@st.cache_data # Mantiene los datos en caché para no saturar la API
def fetch_data():
    # URL estándar de la API de datos.gob.cl (basada en CKAN)
    url = "https://datos.gob.cl/api/3/action/datastore_search"
    
    # IMPORTANTE: Aquí debes poner el resource_id exacto del dataset que elijas en el portal
    params = {
        "resource_id": "TU_RESOURCE_ID_AQUI", 
        "limit": 100
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Verifica si la conexión fue exitosa
        data = response.json()
        
        # Convertimos el JSON a un DataFrame de Pandas
        records = data["result"]["records"]
        return pd.DataFrame(records)
        
    except Exception as e:
        st.error(f"Error de conexión con la API: Reemplaza TU_RESOURCE_ID_AQUI por un ID válido. Detalle: {e}")
        
        # Datos de prueba (Mock) para que veas cómo funciona la interfaz mientras configuras la API
        st.warning("Mostrando datos de prueba generados localmente:")
        data_mock = {
            "Region": ["Antofagasta", "Antofagasta", "Atacama", "Coquimbo", "Metropolitana", "Biobío"],
            "Tipo_Tecnologia": ["Solar", "Eólica", "Solar", "Eólica", "Térmica", "Hidráulica"],
            "Capacidad_MW": [500, 300, 450, 200, 800, 600]
        }
        return pd.DataFrame(data_mock)

# Cargar los datos
df = fetch_data()

# 3. Interfaz y Filtros
if not df.empty:
    st.sidebar.header("Filtros del Sistema")
    
    # Filtro por Región
    regiones = df['Region'].unique().tolist()
    region_seleccionada = st.sidebar.multiselect("Selecciona Región(es)", regiones, default=regiones)
    
    # Aplicar el filtro al DataFrame
    df_filtrado = df[df['Region'].isin(region_seleccionada)]
    
    # 4. Presentación de KPIs (Tarjetas de resumen)
    st.subheader("Resumen General")
    col1, col2 = st.columns(2)
    col1.metric("Centrales Registradas", len(df_filtrado))
    col2.metric("Capacidad Total (MW)", f"{df_filtrado['Capacidad_MW'].sum():.1f}")
    
    st.divider()
    
    # 5. Gráficos interactivos
    st.subheader("Capacidad Instalada por Tecnología")
    
    # Agrupamos los datos
    df_agrupado = df_filtrado.groupby('Tipo_Tecnologia')['Capacidad_MW'].sum().reset_index()
    
    # Creamos el gráfico con Matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df_agrupado['Tipo_Tecnologia'], df_agrupado['Capacidad_MW'], color=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    ax.set_ylabel('Capacidad (MW)')
    ax.set_title('Distribución Energética')
    
    # Renderizamos el gráfico en Streamlit
    st.pyplot(fig)
    
    # 6. Mostrar la base de datos cruda
    st.divider()
    st.subheader("Base de Datos Detallada")
    st.dataframe(df_filtrado)