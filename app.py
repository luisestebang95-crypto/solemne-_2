import streamlit as st
import pandas as pd
import requests
import json # Requerido explícitamente en la rúbrica 
import matplotlib.pyplot as plt

# 1. Configuración de página nivel corporativo
st.set_page_config(page_title="DataViz API", page_icon="⚡", layout="wide")

# 2. Inyección de CSS para diseño UI moderno (sombras, bordes redondeados y ocultar marcas)
st.markdown("""
    <style>
    /* Ocultar elementos por defecto de Streamlit (hamburguesa y footer) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilizar las tarjetas de métricas (KPIs) con un toque industrial */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 5% 5% 5% 10%;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-left: 6px solid #0071CE; /* Acento azul corporativo */
    }
    
    /* Tipografía de encabezados */
    .main-header {
        font-size: 2.2rem;
        color: #0f172a;
        font-weight: 800;
        margin-bottom: 0px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado moderno
st.markdown('<p class="main-header">Centro de Inteligencia de Datos</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Monitoreo y análisis interactivo mediante API REST Gubernamental</p>', unsafe_allow_html=True)

# 3. Reconfiguración global de Matplotlib (Adiós look de los 90s)
plt.rcParams.update({
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.edgecolor": "#e2e8f0",
    "grid.color": "#f1f5f9",
    "grid.linestyle": "--",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "sans-serif",
    "font.size": 10,
    "text.color": "#334155",
    "axes.labelcolor": "#334155",
    "xtick.color": "#64748b",
    "ytick.color": "#64748b"
})

# 4. Extracción de datos de la API [cite: 44, 49]
@st.cache_data
def fetch_data():
    url = "https://datos.gob.cl/api/3/action/datastore_search"
    params = {"resource_id": "d9631921-ebb9-4268-80d9-9a904e8cdcda", "limit": 300}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    # Uso explícito de la librería json para parsear el texto 
    data = json.loads(response.text) 
    return pd.DataFrame(data["result"]["records"])

try:
    df = fetch_data()
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    num_cols = df.select_dtypes(exclude=['object']).columns.tolist()

    if cat_cols:
        columna_principal = cat_cols[0]
        
        # Panel Lateral (Sidebar) minimalista
        st.sidebar.markdown("### 🎛️ Filtros de Segmentación")
        opciones = df[columna_principal].unique().tolist()
        seleccion = st.sidebar.multiselect(f"Seleccione {columna_principal}", opciones, default=opciones[:6])
        
        df_filtrado = df[df[columna_principal].isin(seleccion)]
        
        # KPIs en tarjetas
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Registros Filtrados", f"{len(df_filtrado):,}")
        kpi2.metric("Categorías Activas", f"{len(seleccion)}")
        
        if num_cols:
            suma_total = pd.to_numeric(df_filtrado[num_cols[0]], errors='coerce').sum()
            # Formato numérico limpio y preciso
            kpi3.metric(f"Total {num_cols[0]}", f"{suma_total:,.2f}") 
        else:
            kpi3.metric("Estado de Conexión", "API Online API")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos de Alta Fidelidad en columnas
        graf_col1, graf_col2 = st.columns(2)
        
        df_agrupado = df_filtrado[columna_principal].value_counts().reset_index()
        df_agrupado.columns = [columna_principal, 'Cantidad']
        
        # Paleta de colores moderna
        colores_barras = ['#0071CE', '#1F2937', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
        
        with graf_col1:
            st.markdown("##### 📈 Distribución de Frecuencias")
            fig1, ax1 = plt.subplots(figsize=(8, 4.5))
            barras = ax1.bar(df_agrupado[columna_principal].astype(str), df_agrupado['Cantidad'], color=colores_barras[:len(df_agrupado)], zorder=3)
            ax1.grid(axis='y', zorder=0)
            plt.xticks(rotation=45, ha='right')
            ax1.set_ylabel('Cantidad de Registros')
            st.pyplot(fig1)
            
        with graf_col2:
            st.markdown("##### 🍩 Proporción Relativa")
            fig2, ax2 = plt.subplots(figsize=(8, 4.5))
            # Gráfico de dona moderno en lugar de torta plana
            wedges, texts, autotexts = ax2.pie(
                df_agrupado['Cantidad'], 
                labels=df_agrupado[columna_principal].astype(str), 
                autopct='%1.1f%%', 
                colors=colores_barras[:len(df_agrupado)],
                startangle=90, 
                wedgeprops={'width': 0.4, 'edgecolor': 'white', 'linewidth': 2}
            )
            plt.setp(autotexts, size=9, weight="bold", color="white")
            ax2.axis('equal')
            st.pyplot(fig2)

        # Tabla de Datos y Descarga
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🗄️ Explorador de Datos Crudos")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    else:
        st.warning("El conjunto de datos no posee categorías para aplicar filtros.")

except Exception as e:
    st.error(f"Error en la infraestructura API: {e}")
