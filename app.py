import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuração da Página
st.set_page_config(
    page_title="Simulador de Arrasto Comparativo",
    page_icon="⚡",
    layout="centered"
)

# Estilização CSS personalizada
st.markdown("""
    <style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00D2FF, #FF2A6D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    .sub-title {
        color: #4A5568;
        font-size: 1.15rem;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .variable-card {
        background-color: #F8FAFC;
        border-left: 4px solid #00D2FF;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.92rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<p class="main-title">⚡ Simulador de Força de Arrasto</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">'
    'Ferramenta interativa desenvolvida para modelagem, análise e comparação da resistência aerodinâmica '
    'em meios fluidos entre diferentes geometrias e objetos reais.'
    '</p>',
    unsafe_allow_html=True
)

st.latex(r"F_d = \frac{1}{2} \rho v^2 C_d A")

# Explicação Detalhada das Variáveis
with st.expander("📖 Entenda as Variáveis da Fórmula", expanded=False):
    st.markdown("""
    <div class="variable-card"><b>ρ (Densidade do Fluido):</b> Mede a massa específica do meio (ex: ar = 1.225 kg/m³). Quanto mais denso o fluido, maior a quantidade de matéria a ser deslocada.</div>
    <div class="variable-card"><b>v (Velocidade):</b> Parâmetro de maior impacto devido à relação quadrática (v²). Dobrar a velocidade multiplica a força de arrasto por quatro.</div>
    <div class="variable-card"><b>C<sub>d</sub> (Coeficiente de Arrasto):</b> Adimensional que quantifica a eficiência aerodinâmica. Depende estritamente do formato e geometria do corpo.</div>
    <div class="variable-card"><b>A (Área Frontal):</b> Projeção da área do objeto perpendicular à direção do fluxo. Quanto maior a área exposta, maior a resistência sofrida.</div>
    """, unsafe_allow_html=True)

st.write("")

# Banco de dados de Presets
PRESETS = {
    "Customizado": {"cd": 0.30, "area": 2.2},
    "Carro Popular (Hatch/Sede)": {"cd": 0.32, "area": 2.2},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0},
    "Ciclista em Pé (Gravel/Urbano)": {"cd": 0.90, "area": 0.6},
    "Paraquedista (Aberto)": {"cd": 1.20, "area": 1.5}
}

# Controle Geral de Ambiente
col_env1, col_env2 = st.columns(2)
with col_env1:
    rho = st.slider("Densidade do ar ρ (kg/m³)", 0.5, 2.0, 1.225, 0.05)
with col_env2:
    v_kmh = st.slider("Velocidade de Teste (km/h)", 0.0, 180.0, 108.0, 1.0)

v_ms = v_kmh / 3.6

# Toggle do Modo Comparativo
comparar = st.toggle("🔀 Ativar Modo Comparativo (Objeto A vs. Objeto B)", value=False)

st.write("")

# --- OBJETO A ---
with st.container(border=True):
    st.markdown("**🔵 Objeto A (Referência)**")
    preset_a = st.selectbox("Selecione um Preset para o Objeto A:", list(PRESETS.keys()), index=1)
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        cd_a = st.slider("Cd (Objeto A)", 0.1, 1.5, PRESETS[preset_a]["cd"], 0.01, key="cd_a")
    with col_a2:
        area_a = st.slider("Área Frontal A (m²)", 0.1, 10.0, PRESETS[preset_a]["area"], 0.1, key="area_a")

fd_a = 0.5 * rho * (v_ms ** 2) * cd_a * area_a

# --- OBJETO B (SE ATIVADO) ---
if comparar:
    with st.container(border=True):
        st.markdown("**🔴 Objeto B (Comparativo)**")
        preset_b = st.selectbox("Selecione um Preset para o Objeto B:", list(PRESETS.keys()), index=3)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            cd_b = st.slider("Cd (Objeto B)", 0.1, 1.5, PRESETS[preset_b]["cd"], 0.01, key="cd_b")
        with col_b2:
            area_b = st.slider("Área Frontal A (m²)", 0.1, 10.0, PRESETS[preset_b]["area"], 0.1, key="area_b")

    fd_b = 0.5 * rho * (v_ms ** 2) * cd_b * area_b

st.write("")

# Exibição de Métricas
if comparar:
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Força Fd (Objeto A)", f"{fd_a:.1f} N")
    m_col2.metric("Força Fd (Objeto B)", f"{fd_b:.1f} N")
    
    diferenca = fd_b - fd_a
    m_col3.metric("Diferença (B - A)", f"{abs(diferenca):.1f} N", delta=f"{diferenca:.1f} N", delta_color="inverse")
else:
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Força de Arrasto (Fd)", f"{fd_a:.2f} N")
    m_col2.metric("Velocidade (v)", f"{v_ms:.1f} m/s", f"{v_kmh:.0f} km/h")

st.write("")

# Vetor da Curva
v_vetor_ms = np.linspace(0, 180 / 3.6, 100)
v_vetor_kmh = v_vetor_ms * 3.6
fd_vetor_a = 0.5 * rho * (v_vetor_ms ** 2) * cd_a * area_a

# Gráfico
fig = go.Figure()

# Curva A
fig.add_trace(go.Scatter(
    x=v_vetor_kmh, y=fd_vetor_a,
    mode='lines',
    name='Objeto A',
    line=dict(color='#00D2FF', width=3),
    fill='tozeroy' if not comparar else None,
    fillcolor='rgba(0, 210, 255, 0.08)',
    hovertemplate='<b>Objeto A</b><br>Velocidade: %{x:.1f} km/h<br>Força: %{y:.2f} N<extra></extra>'
))

# Ponto A
fig.add_trace(go.Scatter(
    x=[v_kmh], y=[fd_a],
    mode='markers',
    name='Ponto A',
    marker=dict(color='#00D2FF', size=11, line=dict(color='#FFFFFF', width=2)),
    hovertemplate='<b>Atual Objeto A</b><br>v: %{x:.1f} km/h<br>Fd: %{y:.2f} N<extra></extra>'
))

# Linha de Projeção A
fig.add_trace(go.Scatter(
    x=[0, v_kmh, v_kmh],
    y=[fd_a, fd_a, 0],
    mode='lines',
    line=dict(color='#00D2FF', width=1, dash='dash'),
    hoverinfo='skip'
))

# Adiciona Objeto B se a comparação estiver ativa
if comparar:
    fd_vetor_b = 0.5 * rho * (v_vetor_ms ** 2) * cd_b * area_b
    
    fig.add_trace(go.Scatter(
        x=v_vetor_kmh, y=fd_vetor_b,
        mode='lines',
        name='Objeto B',
        line=dict(color='#FF2A6D', width=3),
        hovertemplate='<b>Objeto B</b><br>Velocidade: %{x:.1f} km/h<br>Força: %{y:.2f} N<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[v_kmh], y=[fd_b],
        mode='markers',
        name='Ponto B',
        marker=dict(color='#FF2A6D', size=11, line=dict(color='#FFFFFF', width=2)),
        hovertemplate='<b>Atual Objeto B</b><br>v: %{x:.1f} km/h<br>Fd: %{y:.2f} N<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[0, v_kmh, v_kmh],
        y=[fd_b, fd_b, 0],
        mode='lines',
        line=dict(color='#FF2A6D', width=1, dash='dash'),
        hoverinfo='skip'
    ))

fig.update_layout(
    xaxis_title="Velocidade (km/h)",
    yaxis_title="Força de Arrasto (N)",
    template="plotly_white",
    margin=dict(l=20, r=20, t=20, b=20),
    height=400,
    showlegend=comparar,  # Exibe legenda apenas no modo comparativo
    legend=dict(x=0.02, y=0.98),
    yaxis=dict(range=[0, max(5000, fd_a * 1.2 if not comparar else max(fd_a, fd_b) * 1.2)], gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False),
    xaxis=dict(gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False)
)

st.plotly_chart(fig, use_container_width=True)
