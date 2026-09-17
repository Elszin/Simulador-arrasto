import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

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
    'Ferramenta interativa desenvolvida para modelagem, análise de vento relativo e comparação da '
    'resistência aerodinâmica em meios fluidos.'
    '</p>',
    unsafe_allow_html=True
)

st.latex(r"F_d = \frac{1}{2} \rho (v_{veículo} + v_{vento})^2 C_d A")

# Explicação Detalhada das Variáveis
with st.expander("📖 Entenda as Variáveis da Fórmula", expanded=False):
    st.markdown("""
    <div class="variable-card"><b>ρ (Densidade do Fluido):</b> Mede a massa específica do meio (ex: ar = 1.225 kg/m³). Quanto mais denso o fluido, maior a quantidade de matéria a ser deslocada.</div>
    <div class="variable-card"><b>v<sub>efetiva</sub> (Velocidade Relativa):</b> A soma da velocidade do veículo com a do vento. Vento contra aumenta a velocidade efetiva; vento a favor a diminui.</div>
    <div class="variable-card"><b>C<sub>d</sub> (Coeficiente de Arrasto):</b> Adimensional que quantifica a eficiência aerodinâmica. Depende estritamente do formato e geometria do corpo.</div>
    <div class="variable-card"><b>A (Área Frontal):</b> Projeção da área do objeto perpendicular à direção do fluxo. Quanto maior a área exposta, maior a resistência sofrida.</div>
    """, unsafe_allow_html=True)

st.write("")

# Banco de dados de Presets
PRESETS = {
    "Customizado": {"cd": 0.30, "area": 2.2},
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0},
    "Ciclista em Pé (Gravel/Urbano)": {"cd": 0.90, "area": 0.6},
    "Paraquedista (Aberto)": {"cd": 1.20, "area": 1.5}
}

# Controle Geral de Ambiente
with st.container(border=True):
    st.markdown("**🌍 Condições do Ambiente & Velocidade**")
    col_env1, col_env2, col_env3 = st.columns(3)
    
    with col_env1:
        rho = st.slider("Densidade do ar ρ (kg/m³)", 0.5, 2.0, 1.225, 0.05)
    with col_env2:
        v_kmh = st.slider("Velocidade do Veículo (km/h)", 0.0, 180.0, 108.0, 1.0)
    with col_env3:
        v_vento_kmh = st.slider("Vento (-Favor / +Contra km/h)", -50.0, 50.0, 0.0, 1.0)

# Velocidade Relativa Efetiva
v_efetiva_kmh = max(0.0, v_kmh + v_vento_kmh)
v_efetiva_ms = v_efetiva_kmh / 3.6

# Toggle do Modo Comparativo
comparar = st.toggle("🔀 Ativar Modo Comparativo (Objeto A vs. Objeto B)", value=False)

st.write("")

# --- OBJETO A ---
with st.container(border=True):
    st.markdown("**🔵 Objeto A (Referência)**")
    preset_a = st.selectbox("Selecione um Preset para o Objeto A:", list(PRESETS.keys()), index=1, key="select_preset_a")
    
    default_cd_a = PRESETS[preset_a]["cd"]
    default_area_a = PRESETS[preset_a]["area"]
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        cd_a = st.slider("Cd (Objeto A)", 0.1, 1.5, default_cd_a, 0.01, key=f"cd_a_{preset_a}")
    with col_a2:
        area_a = st.slider("Área Frontal A (m²)", 0.1, 10.0, default_area_a, 0.1, key=f"area_a_{preset_a}")

fd_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a

# --- OBJETO B (SE ATIVADO) ---
if comparar:
    with st.container(border=True):
        st.markdown("**🔴 Objeto B (Comparativo)**")
        preset_b = st.selectbox("Selecione um Preset para o Objeto B:", list(PRESETS.keys()), index=3, key="select_preset_b")
        
        default_cd_b = PRESETS[preset_b]["cd"]
        default_area_b = PRESETS[preset_b]["area"]
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            cd_b = st.slider("Cd (Objeto B)", 0.1, 1.5, default_cd_b, 0.01, key=f"cd_b_{preset_b}")
        with col_b2:
            area_b = st.slider("Área Frontal A (m²)", 0.1, 10.0, default_area_b, 0.1, key=f"area_b_{preset_b}")

    fd_b = 0.5 * rho * (v_efetiva_ms ** 2) * cd_b * area_b

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
    m_col2.metric("Velocidade Efetiva do Ar", f"{v_efetiva_ms:.1f} m/s", f"{v_efetiva_kmh:.0f} km/h")

st.write("")

# Vetor da Curva
v_vetor_kmh = np.linspace(0, 180, 100)
v_vetor_efetiva_kmh = np.maximum(0.0, v_vetor_kmh + v_vento_kmh)
v_vetor_efetiva_ms = v_vetor_efetiva_kmh / 3.6

fd_vetor_a = 0.5 * rho * (v_vetor_efetiva_ms ** 2) * cd_a * area_a

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
    hovertemplate='<b>Objeto A</b><br>Velocidade Veículo: %{x:.1f} km/h<br>Força: %{y:.2f} N<extra></extra>'
))

# Ponto A
fig.add_trace(go.Scatter(
    x=[v_kmh], y=[fd_a],
    mode='markers',
    name='Ponto A',
    marker=dict(color='#00D2FF', size=11, line=dict(color='#FFFFFF', width=2)),
    hovertemplate='<b>Atual Objeto A</b><br>v_veículo: %{x:.1f} km/h<br>Fd: %{y:.2f} N<extra></extra>'
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
    fd_vetor_b = 0.5 * rho * (v_vetor_efetiva_ms ** 2) * cd_b * area_b
    
    fig.add_trace(go.Scatter(
        x=v_vetor_kmh, y=fd_vetor_b,
        mode='lines',
        name='Objeto B',
        line=dict(color='#FF2A6D', width=3),
        hovertemplate='<b>Objeto B</b><br>Velocidade Veículo: %{x:.1f} km/h<br>Força: %{y:.2f} N<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[v_kmh], y=[fd_b],
        mode='markers',
        name='Ponto B',
        marker=dict(color='#FF2A6D', size=11, line=dict(color='#FFFFFF', width=2)),
        hovertemplate='<b>Atual Objeto B</b><br>v_veículo: %{x:.1f} km/h<br>Fd: %{y:.2f} N<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[0, v_kmh, v_kmh],
        y=[fd_b, fd_b, 0],
        mode='lines',
        line=dict(color='#FF2A6D', width=1, dash='dash'),
        hoverinfo='skip'
    ))

# Define limite dinâmico do eixo Y
max_y = max(5000, fd_a * 1.2 if not comparar else max(fd_a, fd_b) * 1.2)

fig.update_layout(
    xaxis_title="Velocidade do Veículo (km/h)",
    yaxis_title="Força de Arrasto (N)",
    template="plotly_white",
    margin=dict(l=20, r=20, t=20, b=20),
    height=400,
    showlegend=comparar,
    legend=dict(x=0.02, y=0.98),
    yaxis=dict(range=[0, max_y], gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False),
    xaxis=dict(gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False)
)

st.plotly_chart(fig, use_container_width=True)

# --- EXPORTAÇÃO DE DADOS ---
st.write("")
with st.expander("📥 Exportar Dados da Simulação (CSV)", expanded=False):
    data_dict = {
        "Velocidade_Veiculo_kmh": v_vetor_kmh,
        "Vento_kmh": [v_vento_kmh] * 100,
        "Velocidade_Efetiva_kmh": v_vetor_efetiva_kmh,
        "Forca_Arrasto_Objeto_A_N": fd_vetor_a
    }
    if comparar:
        data_dict["Forca_Arrasto_Objeto_B_N"] = fd_vetor_b
        
    df_export = pd.DataFrame(data_dict)
    
    st.dataframe(df_export.head(10), use_container_width=True)
    
    csv_data = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Baixar Tabela Completa em CSV",
        data=csv_data,
        file_name="simulacao_forca_arrasto.csv",
        mime="text/csv",
        use_container_width=True
    )
