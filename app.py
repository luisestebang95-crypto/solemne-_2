import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt

# 1. Configuración Pro de la interfaz
st.set_page_config(page_title="Minería Chile - Solemne II", page_icon="⛏️", layout="wide")

# 2. Inyección de CSS (Encabezado azul con texto blanco y pestañas modernas)
st.markdown("""
    <style>
    .header-banner {
        background: linear-gradient(135deg, #0f172a 0%, #0284c7 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .header-title {
        color: #ffffff !important; /* Texto en blanco puro */
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    .header-subtitle {
        color: #e0f2fe;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    button[data-baseweb="tab"] {
        font-size: 1.1rem;
        padding: 1rem 2rem;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #f0f9ff;
        border-bottom: 4px solid #0284c7;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">📊 Sistema de Inteligencia y Visualización de Datos</h1>
        <p class="header-subtitle">Minería en Chile: Análisis Predictivo y Desempeño Histórico (API datos.gob.cl)</p>
    </div>
""", unsafe_allow_html=True)

# 3. Motor de Datos (Extracción y Limpieza)
@st.cache_data
def load_and_clean_data():
    url = "https://datos.gob.cl/api/3/action/datastore_search"
    params = {"resource_id": "d9631921-ebb9-4268-80d9-9a904e8cdcda", "limit": 1000}
    res = requests.get(url, params=params)
    data = json.loads(res.text)
    df_raw = pd.DataFrame(data["result"]["records"])
    
    # Identificar columnas de años (formato Chile: 1.997)
    cols_years = [c for c in df_raw.columns if any(i.isdigit() for i in c) and '.' in c]
    
    # Derretir (Melt) para análisis temporal
    df_long = df_raw.melt(
        id_vars=['Grupo de minerales', 'Sector', 'Mineral', 'Unidad'], 
        value_vars=cols_years, 
        var_name='Año', 
        value_name='Produccion'
    )
    
    # Limpieza numérica profunda
    df_long['Año'] = df_long['Año'].str.replace('.', '').astype(int)
    df_long['Produccion'] = df_long['Produccion'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df_long['Produccion'] = pd.to_numeric(df_long['Produccion'], errors='coerce').fillna(0)
    
    return df_long

try:
    df = load_and_clean_data()
    
    # Separación de universos de datos
    df_met = df[df['Sector'].str.contains('METÁLICA', case=False, na=False) & ~df['Sector'].str.contains('NO METÁLICA', case=False)]
    df_nomet = df[df['Sector'].str.contains('NO METÁLICA', case=False, na=False)]

    # 4. Estructura de Pestañas
    t1, t2, t3, t4 = st.tabs(["🏭 Minería Metálica", "💎 Minería No Metálica", "🗄️ Explorador", "📄 Memoria"])

    def render_mining_tab(data_subset, accent_color):
        # Filtros específicos
        opciones = data_subset['Mineral'].unique().tolist()
        seleccion = st.multiselect("Seleccionar Minerales:", opciones, default=opciones[:3], key=f"sel_{accent_color}")
        df_f = data_subset[data_subset['Mineral'].isin(seleccion)]
        
        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("Registros Históricos", len(df_f))
        c2.metric("Punto Máximo Producción", f"{df_f['Produccion'].max():,.0f}")
        c3.metric("Promedio Anual", f"{df_f['Produccion'].mean():,.2f}")
        
        st.divider()
        
        # Gráficos Vivos (Streamlit Nativo)
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### Frecuencia por Mineral (Interactivo)")
            st.bar_chart(df_f.groupby('Mineral')['Produccion'].sum(), color=accent_color)
        with g2:
            st.markdown("#### Composición del Sector (Matplotlib)")
            fig, ax = plt.subplots()
            pie_data = df_f.groupby('Mineral')['Produccion'].sum()
            ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', colors=plt.cm.Blues(range(100, 255, 30)), startangle=90)
            fig.patch.set_alpha(0.0)
            st.pyplot(fig)
            
        st.markdown("#### 📈 Evolución Temporal Comparativa")
        # Gráfico de líneas "Vivo"
        chart_data = df_f.pivot_table(index='Año', columns='Mineral', values='Produccion', aggfunc='sum')
        st.line_chart(chart_data)

    with t1:
        render_mining_tab(df_met, "#0369a1")
        
    with t2:
        render_mining_tab(df_nomet, "#0891b2")

    with t3:
        st.dataframe(df, use_container_width=True)

    with t4:
        st.info("Especificaciones: Python 3.10+ | Framework: Streamlit | Data: API CKAN Gobierno de Chile")

except Exception as e:
    st.error(f"Error en el sistema: {e}")
