import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# 1. Configuración de página nivel profesional (ancho completo)
st.set_page_config(page_title="DataViz Gobierno", page_icon="📈", layout="wide")

# Encabezado corporativo
st.title("📊 Plataforma de Análisis de Datos - Gobierno de Chile")
st.markdown("---")
st.markdown("**Proyecto Solemne II:** Sistema interactivo de extracción, análisis y visualización de datos mediante API REST pública.")

# 2. Extracción de datos de la API (Caché activado para velocidad)
@st.cache_data
def fetch_data():
    url = "https://datos.gob.cl/api/3/action/datastore_search"
    params = {
        "resource_id": "d9631921-ebb9-4268-80d9-9a904e8cdcda", 
        "limit": 300 # Aumentamos el límite para tener más volumen de datos
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data["result"]["records"])

try:
    df = fetch_data()
    
    # Limpieza de datos
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    # Separación dinámica de columnas matemáticas y de texto
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    num_cols = df.select_dtypes(exclude=['object']).columns.tolist()

    if cat_cols:
        columna_principal = cat_cols[0]
        
        # 3. Panel Lateral (Sidebar) mejorado
        st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Gobierno_de_Chile_logo.svg/800px-Gobierno_de_Chile_logo.svg.png", width=150)
        st.sidebar.header("⚙️ Panel de Control")
        st.sidebar.markdown("Utilice los filtros para segmentar la base de datos de origen.")
        
        opciones = df[columna_principal].unique().tolist()
        seleccion = st.sidebar.multiselect(f"Filtro: {columna_principal}", opciones, default=opciones[:6])
        
        df_filtrado = df[df[columna_principal].isin(seleccion)]
        
        # 4. Organización por Pestañas (Tabs)
        tab1, tab2, tab3 = st.tabs(["📈 Panel de Análisis", "🗄️ Base de Datos", "ℹ️ Metodología"])
        
        with tab1:
            # Tarjetas de KPIs en columnas
            st.subheader("Indicadores Clave de Rendimiento (KPIs)")
            kpi1, kpi2, kpi3 = st.columns(3)
            
            kpi1.metric("Volumen de Registros", f"{len(df_filtrado)} datos")
            kpi2.metric("Categorías Analizadas", f"{len(seleccion)} ítems")
            if num_cols:
                # Si hay datos numéricos, sumamos el primero
                suma_total = pd.to_numeric(df_filtrado[num_cols[0]], errors='coerce').sum()
                kpi3.metric(f"Suma de {num_cols[0]}", f"{suma_total:,.1f}")
            else:
                kpi3.metric("Estado del Sistema", "Óptimo 🟢")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráficos dinámicos en dos columnas
            st.subheader("Visualizaciones Estadísticas")
            graf_col1, graf_col2 = st.columns(2)
            
            df_agrupado = df_filtrado[columna_principal].value_counts().reset_index()
            df_agrupado.columns = [columna_principal, 'Cantidad']
            
            with graf_col1:
                st.markdown("**Frecuencia por Categoría**")
                fig1, ax1 = plt.subplots(figsize=(8, 5))
                # Un gráfico de barras más limpio, sin bordes feos
                ax1.bar(df_agrupado[columna_principal].astype(str), df_agrupado['Cantidad'], color='#2E86C1', edgecolor='black')
                plt.xticks(rotation=45, ha='right')
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
                ax1.grid(axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig1)
                
            with graf_col2:
                st.markdown("**Proporción del Mercado**")
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                # Agregamos un gráfico de torta para darle peso analítico
                ax2.pie(df_agrupado['Cantidad'], labels=df_agrupado[columna_principal].astype(str), autopct='%1.1f%%', 
                        colors=plt.cm.Paired.colors, startangle=140, wedgeprops={'edgecolor': 'white'})
                ax2.axis('equal')
                st.pyplot(fig2)

        with tab2:
            st.subheader("Base de Datos Estructurada")
            st.markdown("Vista detallada de los registros extraídos desde la API, aplicando los filtros seleccionados.")
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Botón pro para descargar los datos filtrados
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Reporte CSV",
                data=csv,
                file_name='reporte_api_gobierno.csv',
                mime='text/csv',
            )
            
        with tab3:
            st.subheader("Arquitectura del Proyecto")
            st.markdown("""
            * **Origen de datos:** Portal de Datos Abiertos del Gobierno de Chile (`datos.gob.cl`).
            * **Método de extracción:** Protocolo RESTful API vía requests (Método GET).
            * **Procesamiento:** Transformación de formato JSON a DataFrames estructurados mediante Pandas.
            * **Visualización:** Renderizado dinámico de KPIs y gráficos utilizando Matplotlib y Streamlit.
            """)

    else:
        st.warning("El dataset extraído no contiene columnas categóricas para filtrar.")

except Exception as e:
    st.error(f"Falla crítica en la comunicación con el servidor gubernamental. Detalle técnico: {e}")
