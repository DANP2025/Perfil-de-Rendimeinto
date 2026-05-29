import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y CSS
# ==========================================
st.set_page_config(page_title="Pro Athlete Profiling", layout="wide", page_icon="⚡")

# Inyección de CSS para ocultar el menú de Streamlit y dar estilo al header
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stMetric {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #1f77b4;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CARGA Y PROCESAMIENTO DE DATOS
# ==========================================
@st.cache_data
def load_data():
    np.random.seed(42)
    data = {
        'Atleta': ['Mateo Silva', 'Lucas Rossi', 'Tomás Costa', 'Joaquín Gómez', 'Thiago López', 'Martín Romano', 'Nicolás Fernández', 'Facundo Herrera', 'Santiago Díaz', 'Diego Navarro', 'Alejandro Castro', 'Valentino Ruiz', 'Bautista Giménez', 'Emiliano Torres', 'Julián Ortiz', 'Benjamín Morales', 'Enzo Peralta', 'Marcos Domínguez', 'Ignacio Vargas', 'Rodrigo Medina'],
        'CMJ_cm': np.random.normal(42, 5, 20),           
        'Sprint_10m_s': np.random.normal(1.65, 0.08, 20),
        'Sentadilla_1RM_kg': np.random.normal(130, 20, 20),
        'VIFT_kmh': np.random.normal(19.5, 1.2, 20)   
    }
    return pd.DataFrame(data)

def calculate_z_scores(df):
    df_z = df.copy()
    metrics = ['CMJ_cm', 'Sprint_10m_s', 'Sentadilla_1RM_kg', 'VIFT_kmh']
    
    for col in metrics:
        mean = df[col].mean()
        std = df[col].std()
        
        # Inversión para métricas de tiempo (menor es mejor)
        if 'Sprint' in col:
            df_z[col + '_Z'] = (mean - df[col]) / std
        else:
            df_z[col + '_Z'] = (df[col] - mean) / std
            
    return df_z

df = load_data()
df_z = calculate_z_scores(df)

# ==========================================
# 3. ENCABEZADO Y CONTROLES (HEADER LAYOUT)
# ==========================================
header_cols = st.columns([1, 3, 2], gap="large", vertical_alignment="center")

with header_cols[0]:
    # Foto del profe (RPE)
    st.image("coach.jpg", use_container_width=True)

with header_cols[1]:
    # Títulos principales
    st.markdown("## ⚡ Perfil de Rendimiento Físico")
    st.markdown("Comparativa individual frente a la media de la plantilla.")
    st.info("💡 **Tip:** Z-Scores > 1.0 indican nivel Élite.")

with header_cols[2]:
    # Dropdown de selección integrado
    athlete_list = df['Atleta'].tolist()
    selected_athlete = st.selectbox(
        "👤 Seleccionar Atleta a evaluar:", 
        athlete_list,
        index=0
    )
    st.markdown(f"<h3 style='text-align: center; color: #1f77b4;'>{selected_athlete}</h3>", unsafe_allow_html=True)

# Filtrar datos del atleta seleccionado
athlete_data = df_z[df_z['Atleta'] == selected_athlete].iloc[0]

# ==========================================
# 4. TARJETAS DE MÉTRICAS (KPIs)
# ==========================================
st.write("") # Espaciador

# Calcular medias del equipo para los Deltas
mean_cmj = df['CMJ_cm'].mean()
mean_sprint = df['Sprint_10m_s'].mean()
mean_squat = df['Sentadilla_1RM_kg'].mean()
mean_vift = df['VIFT_kmh'].mean()

# Tarjetas de Métricas (KPIs)
cols = st.columns(4)

# st.metric tiene un parámetro "delta_color" que es mágico para el deporte.
with cols[0]:
    delta_cmj = athlete_data['CMJ_cm'] - mean_cmj
    st.metric("⬆️ Salto CMJ", f"{athlete_data['CMJ_cm']:.1f} cm", f"{delta_cmj:.1f} cm vs media")

with cols[1]:
    delta_sprint = athlete_data['Sprint_10m_s'] - mean_sprint
    # Para el sprint, un delta negativo (menos tiempo) es BUENO, así que usamos delta_color="inverse"
    st.metric("⏱️ Sprint 10m", f"{athlete_data['Sprint_10m_s']:.2f} s", f"{delta_sprint:.2f} s vs media", delta_color="inverse")

with cols[2]:
    delta_squat = athlete_data['Sentadilla_1RM_kg'] - mean_squat
    st.metric("🏋️ Fuerza 1RM", f"{athlete_data['Sentadilla_1RM_kg']:.1f} kg", f"{delta_squat:.1f} kg vs media")

with cols[3]:
    delta_vift = athlete_data['VIFT_kmh'] - mean_vift
    st.metric("🫁 30-15 IFT", f"{athlete_data['VIFT_kmh']:.1f} km/h", f"{delta_vift:.1f} km/h vs media")

st.divider()

# ==========================================
# 5. GRÁFICO PLOTLY DE ALTO RENDIMIENTO
# ==========================================
st.markdown("### 📊 Z-Score Profiling (Radar Lineal)")

z_metrics = ['VIFT_kmh_Z', 'Sentadilla_1RM_kg_Z', 'Sprint_10m_s_Z', 'CMJ_cm_Z']
z_values = [athlete_data[m] for m in z_metrics]
metric_names = ['30-15 IFT', '1RM Sentadilla', 'Sprint 10m', 'Salto CMJ']

# Colores premium: Verde esmeralda y Rojo coral
colors = ['#10B981' if val >= 0 else '#EF4444' for val in z_values]

fig = go.Figure()

# Añadir las barras
fig.add_trace(go.Bar(
    x=z_values,
    y=metric_names,
    orientation='h',
    marker=dict(
        color=colors,
        line=dict(color='rgba(0,0,0,0)', width=0), # Bordes limpios
        cornerradius=4 # Bordes redondeados (en versiones recientes de Plotly)
    ),
    text=[f"<b>{val:+.2f} SD</b>" for val in z_values],
    textposition='auto',
    textfont=dict(color='white', size=14),
    hoverinfo='none'
))

# Diseño del gráfico (Layout)
fig.update_layout(
    height=400,
    margin=dict(l=0, r=0, t=20, b=0),
    plot_bgcolor='rgba(0,0,0,0)', # Fondo transparente
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        title="← Déficit  |  Z-Score (Desviaciones Estándar)  |  Élite →",
        range=[-3.5, 3.5],
        tickmode='linear',
        tick0=-3, dtick=1,
        showgrid=True,
        gridcolor='rgba(128,128,128,0.2)',
        zeroline=True,
        zerolinecolor='rgba(255,255,255,0.5)', # Línea 0 (Media) bien visible
        zerolinewidth=3
    ),
    yaxis=dict(
        showgrid=False,
        tickfont=dict(size=14, family="Arial", color="gray")
    ),
    showlegend=False
)

# Añadir ZONAS DE RENDIMIENTO (Bajo, Promedio, Élite)
fig.add_vrect(x0=-3.5, x1=-1, fillcolor="#EF4444", opacity=0.05, layer="below", line_width=0)
fig.add_vrect(x0=-1, x1=1, fillcolor="gray", opacity=0.05, layer="below", line_width=0)
fig.add_vrect(x0=1, x1=3.5, fillcolor="#10B981", opacity=0.05, layer="below", line_width=0)

# Anotaciones de las zonas en la parte superior
fig.add_annotation(x=-2.25, y=3.5, text="Área de Mejora", showarrow=False, font=dict(color="#EF4444", size=12))
fig.add_annotation(x=0, y=3.5, text="Zona Promedio", showarrow=False, font=dict(color="gray", size=12))
fig.add_annotation(x=2.25, y=3.5, text="Zona Élite", showarrow=False, font=dict(color="#10B981", size=12))

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}) # Oculta la barra flotante de Plotly para mayor limpieza

# ==========================================
# 6. TABLA EXPANDIBLE CON MAPA DE CALOR
# ==========================================
with st.expander("📂 Ver Base de Datos Completa (Heatmap)"):
    # Aplicar un mapa de calor solo a las columnas Z para ver rápidamente quién destaca
    z_columns = [m + '_Z' for m in ['CMJ_cm', 'Sprint_10m_s', 'Sentadilla_1RM_kg', 'VIFT_kmh']]
    st.dataframe(
        df_z[['Atleta'] + z_columns].style.background_gradient(
            cmap='RdYlGn', vmin=-2.5, vmax=2.5, subset=z_columns
        ).format({col: "{:.2f}" for col in z_columns}),
        use_container_width=True,
        hide_index=True
    )
