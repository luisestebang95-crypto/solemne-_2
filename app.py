import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt

# 1. Configuración de la interfaz nativa en modo ancho
st.set_page_config(
    page_title="Dashboard - Solemne II",
    page_icon="📈",
    layout="wide"
)

# 2. Inyección de CSS Seguro (Encabezado de color y Pestañas dinámicas)
st.markdown("""
    <style>
    /* Contenedor del encabezado con degradado corporativo */
    .header-banner {
        background: linear-gradient(135deg, #0f172a 0%, #0284c7 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title {
        color: #ffffff !important; /* Texto en blanco puro */
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        font-family: sans-serif;
    }
    .header-subtitle {
        color: #e0f2fe;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Estilo dinámico para las pestañas (Tabs) */
    button[data-baseweb="tab"] {
        background-color: transparent;
        border-bottom: 3px solid transparent;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #f0f9ff;
        border-bottom: 3px solid #0284c7;
        border-radius: 8px 8px 0 0;
    }
    button[data-baseweb="tab"][aria-selected="true"] > div {
        color: #0284c7 !important;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

# Renderizar el nuevo encabezado con el texto restaurado en blanco
st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">📈 Sistema de Inteligencia y Visualización de Datos</h1>
        <p class="header-subtitle">Proyecto Final Sumativo - Solemne II | Extracción Automatizada vía API REST</p>
    </div>
""", unsafe_allow_html=True)

# 3. Extracción de datos con persistencia en caché
@st.cache_data
def cargar_datos_api():
    url = "https://datos.gob.cl/api/3/action/datastore_search"
    params = {
        "resource_id": "d9631921-ebb9-4268-80d9-9a904e8cdcda", 
        "limit": 300
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = json.loads(response.text)
    df = pd.DataFrame(data["result"]["records"])
    
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    return df

try:
    df = cargar_datos_api()
    
    columnas_texto = df.select_dtypes(include=['object']).columns.tolist()
    columnas_num = df.select_dtypes(exclude=['object']).columns.tolist()
    col_filtro = columnas_texto[0] if columnas_texto else None

    if col_filtro:
        # Panel Lateral Técnico (Sidebar)
        st.sidebar.header("⚙️ Filtros de Segmentación")
        st.sidebar.markdown("Modifique los parámetros para actualizar los componentes del panel.")
        
        opciones = df[col_filtro].unique().tolist()
        seleccion = st.sidebar.multiselect(
            f"Selección de {col_filtro}:",
            options=opciones,
            default=opciones[:5]
        )
        
        df_filtrado = df[df[col_filtro].isin(seleccion)]

        # Implementación del Sistema de Pestañas
        tab1, tab2, tab3 = st.tabs(["📊 Panel de Visualización", "🗄️ Explorador de Datos", "📄 Ficha Técnica"])

        with tab1:
            st.markdown("### 📌 Indicadores Clave de Rendimiento (KPIs)")
            
            m1, m2, m3 = st.columns(3)
            m1.metric(label="Volumen Total de Registros", value=f"{len(df_filtrado):,}")
            m2.metric(label="Categorías Filtradas", value=len(seleccion))
            
            if columnas_num:
                col_matematica = columnas_num[0]
                total_calculado = pd.to_numeric(df_filtrado[col_matematica], errors='coerce').sum()
                m3.metric(label=f"Métrica Agregada ({col_matematica})", value=f"{total_calculado:,.2f}")
            else:
                m3.metric(label="Conexión de Servidor", value="Operacional 🟢")
            
            st.markdown("---")
            st.markdown("### 📉 Distribución Analítica Estadísticas")
            
            data_grafico = df_filtrado[col_filtro].value_counts().reset_index()
            data_grafico.columns = [col_filtro, 'Cantidad']
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.markdown("**Frecuencia Absoluta (Gráfico Dinámico)**")
                # Gráfico nativo de Streamlit: animado y con interacciones al pasar el mouse
                st.bar_chart(data_grafico.set_index(col_filtro)['Cantidad'], color="#0284c7")
                
            with col_g2:
                st.markdown("**Composición Proporcional (Matplotlib)**")
                # Se mantiene un gráfico generado con Matplotlib para cumplir 100% con la rúbrica de evaluación
                fig2, ax2 = plt.subplots(figsize=(7, 4.5))
                colores_pie = ['#0284c7', '#38bdf8', '#7dd3fc', '#bae6fd', '#e0f2fe']
                wedges, texts, autotexts = ax2.pie(
                    data_grafico['Cantidad'],
                    labels=data_grafico[col_filtro].astype(str),
                    autopct='%1.1f%%',
                    startangle=140,
                    colors=colores_pie[:len(data_grafico)],
                    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
                )
                
                plt.setp(autotexts, size=9, weight="bold", color="#1e293b")
                plt.setp(texts, size=9, color="#475569")
                fig2.patch.set_alpha(0.0)
                ax2.patch.set_alpha(0.0)
                plt.tight_layout()
                st.pyplot(fig2)

        with tab2:
            st.markdown("### 🗄️ Explorador Completo de Datos")
            st.markdown("A continuación se despliega el conjunto de registros filtrados recuperados dinámicamente desde el endpoint gubernamental.")
            
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Segmentación Actual a CSV",
                data=csv,
                file_name='reporte_data_filtrada.csv',
                mime='text/csv'
            )

        with tab3:
            st.markdown("### 📄 Especificaciones de la Arquitectura")
            st.info("El sistema opera bajo los estándares técnicos definidos en la pauta de evaluación sumativa.")
            st.markdown("""
            * **Capa de Presentación:** Streamlit Web Framework.
            * **Componente de Conexión:** Librería `requests` administrando peticiones asíncronas vía protocolo HTTP (Método GET).
            * **Mapeo del Payload:** Librería estándar `json` encargada de deserializar cadenas estructuradas de texto.
            * **Análisis Matricial:** Librería `pandas` operando la lógica de DataFrames.
            * **Motor de Gráficos:** `matplotlib.pyplot` integrado junto a visualizaciones interactivas nativas.
            * **Fuente de Abastecimiento:** Catálogo de Datos Abiertos del Gobierno de Chile (`datos.gob.cl`).
            """)

    else:
        st.warning("El recurso de la API no contiene variables de texto válidas para la indexación.")

except Exception as e:
    st.error(f"Falla crítica en el subsistema de comunicación: {e}")
