import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuração da Página
st.set_page_config(
    page_title="Simulador de Arrasto",
    page_icon="⚡",
    layout="centered"
)

# Estilização CSS personalizada para títulos e caixas
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00D2FF, #FF2A6D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #666;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho Estilizado
st.markdown('<p class="main-title">⚡ Simulador de Força de Arrasto</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Análise interativa de mecânica dos fluidos em tempo real</p>', unsafe_allow_html=True)

st.latex(r"F_d = \frac{1}{2} \rho v^2 C_d A")

# Container de Controles
with st.container(border=True):
    st.markdown("**🎛️ Parâmetros da Simulação**")
    col1, col2 = st.columns(2)
    
    with col1:
        rho = st.slider("Densidade do ar ρ (kg/m³)", 0.5, 2.0, 1.225, 0.05)
        cd = st.slider("Coeficiente de arrasto (Cd)", 0.1, 1.5, 0.30, 0.05)
        
    with col2:
        area = st.slider("Área frontal A (m²)", 0.5, 5.0, 2.0, 0.1)
        v_kmh = st.slider("Velocidade atual (km/h)", 0.0, 150.0, 108.0, 1.0)

# Cálculos
v_ms = v_kmh / 3.6
fd_atual = 0.5 * rho * (v_ms ** 2) * cd * area

st.write("") # Espaçamento

# Métricas Destacadas em Colunas
m_col1, m_col2 = st.columns(2)
m_col1.metric("Força de Arrasto (Fd)", f"{fd_atual:.2f} N")
m_col2.metric("Velocidade Converter", f"{v_ms:.1f} m/s", f"{v_kmh:.0f} km/h")

st.write("")

# Vetor da Curva
v_vetor_ms = np.linspace(0, 150 / 3.6, 100)
v_vetor_kmh = v_vetor_ms * 3.6
fd_vetor = 0.5 * rho * (v_vetor_ms ** 2) * cd * area

# Gráfico
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=v_vetor_kmh, y=fd_vetor,
    mode='lines',
    name='Curva Fd',
    line=dict(color='#00D2FF', width=3),
    fill='tozeroy',
    fillcolor='rgba(0, 210, 255, 0.08)'
))

fig.add_trace(go.Scatter(
    x=[0, v_kmh, v_kmh],
    y=[fd_atual, fd_atual, 0],
    mode='lines',
    line=dict(color='#FF2A6D', width=1.5, dash='dash'),
    hoverinfo='skip'
))

fig.add_trace(go.Scatter(
    x=[v_kmh], y=[fd_atual],
    mode='markers',
    name='Ponto Atual',
    marker=dict(color='#FF2A6D', size=11, line=dict(color='#FFFFFF', width=2))
))

fig.update_layout(
    xaxis_title="Velocidade (km/h)",
    yaxis_title="Força de Arrasto (N)",
    template="plotly_white",
    margin=dict(l=20, r=20, t=20, b=20),
    height=380,
    showlegend=False,
    yaxis=dict(range=[0, 4000], gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False),
    xaxis=dict(gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False)
)

st.plotly_chart(fig, use_container_width=True)
