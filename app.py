import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt

# 1. Configuración de página - Nativa y Robusta
st.set_page_config(page_title="DataViz API - Gobierno", page_icon="📊", layout="wide")

st.title("📊 Dashboard Analítico Gubernamental")
st.markdown("Proyecto Solemne II - Extracción y Análisis de Datos mediante API REST")
st.divider()

# 2. Conexión a la API y procesamiento (Uso estricto de requests y json)
@st.cache_data
def fetch_data():
    url = "https://datos.gob.cl/api/3/action/datastore_search"
    params = {"resource_id": "d9631921-ebb9-4268-80d9-9a904e8cdcda", "limit": 500}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    # Uso explícito de la librería json según instrucciones
    data = json.loads(response.text) 
    
    df = pd.DataFrame(data["result"]["records"])
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    return df

try:
    df = fetch_data()

    # Separar variables para el análisis dinámico
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    num_cols = df.select_dtypes(exclude=['object']).columns.tolist()
    col_principal = cat_cols[0] if cat_cols else None

    if col_principal:
        # 3. Interfaz Lateral (Filtros Nativos de Streamlit)
        st.sidebar.header("⚙️ Parámetros de Análisis")
        
        opciones = df[col_principal].unique().tolist()
        seleccion = st.sidebar.multiselect(
            f"Filtre por {col_principal}:", 
            options=opciones, 
            default=opciones[:7]
        )
        
        df_filtrado = df[df[col_principal].isin(seleccion)]

        # 4. Panel Principal - KPIs usando columnas nativas
        st.subheader("Indicadores de Desempeño")
        col1, col2, col3 = st.columns(3)
        col1.metric("Volumen de Datos (Registros)", len(df_filtrado))
        col2.metric("Categorías Seleccionadas", len(seleccion))
        
        if num_cols:
            suma = pd.to_numeric(df_filtrado[num_cols[0]], errors='coerce').sum()
            col3.metric(f"Total Agregado ({num_cols[0]})", f"{suma:,.2f}")
        else:
            col3.metric("Conexión API", "Estable 🟢")

        st.divider()

        # 5. Visualizaciones con Matplotlib (Con fondo transparente para respetar el tema)
        st.subheader("Análisis Gráfico")
        
        df_agrupado = df_filtrado[col_principal].value_counts().reset_index()
        df_agrupado.columns = [col_principal, 'Frecuencia']
        
        graf_col1, graf_col2 = st.columns(2)
        
        with graf_col1:
            st.markdown(f"**Frecuencia por {col_principal}**")
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            
            # Estilo minimalista puro
            ax1.bar(df_agrupado[col_principal].astype(str), df_agrupado['Frecuencia'], color='#1f77b4', alpha=0.8)
            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.yticks(fontsize=9)
            ax1.spines[['top', 'right']].set_visible(False)
            ax1.grid(axis='y', linestyle='--', alpha=0.5)
            
            # Esto es clave: Hace que el fondo del gráfico sea transparente
            fig1.patch.set_alpha(0.0) 
            ax1.patch.set_alpha(0.0)
            
            st.pyplot(fig1)

        with graf_col2:
            st.markdown("**Composición Porcentual**")
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            wedges, texts, autotexts = ax2.pie(
                df_agrupado['Frecuencia'], 
                labels=df_agrupado[col_principal].astype(str),
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 9, 'color': 'gray'}
            )
            
            # Fondo transparente
            fig2.patch.set_alpha(0.0)
            ax2.patch.set_alpha(0.0)
            
            st.pyplot(fig2)

        st.divider()

        # 6. Tabla de Datos limpia
        st.subheader("Explorador de Datos")
        st.dataframe(df_filtrado, use_container_width=True)

    else:
        st.warning("No se encontraron columnas categóricas para graficar.")

except Exception as e:
    st.error(f"Error de ejecución: {e}")
