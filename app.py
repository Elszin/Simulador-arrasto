import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="Dashboard de Arrasto Aerodinâmico & Hidrodinâmico",
    page_icon="⚡",
    layout="wide"
)

# Estilização CSS com Coluna Fixa (Sticky)
st.markdown("""
    <style>
    div[data-testid="stColumn"]:nth-child(1) {
        position: sticky;
        top: 1rem;
        align-self: flex-start;
        z-index: 99;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00D2FF, #FF2A6D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .variable-card {
        background-color: #F8FAFC;
        border-left: 4px solid #00D2FF;
        padding: 8px 12px;
        margin-bottom: 6px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# Dicionário de Fluidos (Mecânica dos Fluidos)
FLUIDOS = {
    "Ar (Nível do Mar - 15°C)": 1.225,
    "Ar (Altitude 2000m)": 1.006,
    "Água Doce (20°C)": 998.2,
    "Água do Mar (15°C)": 1025.0,
    "Customizado": 1.225
}

# Banco de dados de Presets
PRESETS = {
    "Customizado": {"cd": 0.30, "area": 2.2},
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0},
    "Ciclista em Pé (Gravel/Urbano)": {"cd": 0.90, "area": 0.6},
    "Paraquedista (Aberto)": {"cd": 1.20, "area": 1.5}
}

# ==========================================
# COLUNA 1 (ESQUERDA): BARRA LATERAL
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configurações Gerais")
    st.write("---")
    
    st.markdown("**🌊 Meio Fluido & Ambiente**")
    fluido_selecionado = st.selectbox("Selecione o Fluido:", list(FLUIDOS.keys()), index=0)
    rho_padrao = FLUIDOS[fluido_selecionado]
    
    rho = st.slider("Densidade do meio ρ (kg/m³)", 0.1, 1100.0, float(rho_padrao), 0.1)
    v_kmh = st.slider("Velocidade do Veículo (km/h)", 0.0, 180.0, 108.0, 1.0)
    v_vento_kmh = st.slider("Vento / Correnteza (-Favor / +Contra km/h)", -50.0, 50.0, 0.0, 1.0)
    
    v_efetiva_kmh = max(0.0, v_kmh + v_vento_kmh)
    v_efetiva_ms = v_efetiva_kmh / 3.6

    st.write("---")
    comparar = st.toggle("🔀 Ativar Modo Comparativo", value=False)
    st.write("---")

# DIVISÃO DA ÁREA PRINCIPAL
col_centro, col_direita = st.columns([2.2, 1], gap="medium")

# ==========================================
# COLUNA 3 (DIREITA): PARÂMETROS
# ==========================================
with col_direita:
    st.markdown("### 📐 Parâmetros do Objeto")
    
    # Objeto A
    with st.container(border=True):
        st.markdown("**🔵 Objeto A (Referência)**")
        preset_a = st.selectbox("Preset:", list(PRESETS.keys()), index=1, key="select_preset_a")
        
        cd_a = st.slider("Cd (Objeto A)", 0.1, 1.5, PRESETS[preset_a]["cd"], 0.01, key=f"cd_a_{preset_a}")
        area_a = st.slider("Área Frontal A (m²)", 0.1, 10.0, PRESETS[preset_a]["area"], 0.1, key=f"area_a_{preset_a}")

    fd_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a

    # Objeto B
    if comparar:
        with st.container(border=True):
            st.markdown("**🔴 Objeto B (Comparativo)**")
            preset_b = st.selectbox("Preset:", list(PRESETS.keys()), index=3, key="select_preset_b")
            
            cd_b = st.slider("Cd (Objeto B)", 0.1, 1.5, PRESETS[preset_b]["cd"], 0.01, key=f"cd_b_{preset_b}")
            area_b = st.slider("Área Frontal B (m²)", 0.1, 10.0, PRESETS[preset_b]["area"], 0.1, key=f"area_b_{preset_b}")

        fd_b = 0.5 * rho * (v_efetiva_ms ** 2) * cd_b * area_b

    with st.expander("📖 Teoria das Variáveis", expanded=False):
        st.markdown("""
        <div class="variable-card"><b>ρ:</b> Densidade do meio (Ar ≈ 1.22 kg/m³ | Água ≈ 1000 kg/m³).</div>
        <div class="variable-card"><b>v<sub>efetiva</sub>:</b> Velocidade do corpo + fluxo do fluido.</div>
        <div class="variable-card"><b>C<sub>d</sub>:</b> Eficiência do formato geométrico.</div>
        <div class="variable-card"><b>A:</b> Área frontal projetada.</div>
        """, unsafe_allow_html=True)

# ==========================================
# COLUNA 2 (MEIO): GRÁFICO E RESULTADOS
# ==========================================
with col_centro:
    st.markdown('<p class="main-title">⚡ Simulador de Força de Arrasto</p>', unsafe_allow_html=True)
    st.latex(r"F_d = \frac{1}{2} \rho (v_{veículo} + v_{vento})^2 C_d A")
    
    if comparar:
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Força (Objeto A)", f"{fd_a:.1f} N")
        m_col2.metric("Força (Objeto B)", f"{fd_b:.1f} N")
        diferenca = fd_b - fd_a
        m_col3.metric("Diferença (B - A)", f"{abs(diferenca):.1f} N", delta=f"{diferenca:.1f} N", delta_color="inverse")
    else:
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("Força de Arrasto (Fd)", f"{fd_a:.2f} N")
        m_col2.metric("Velocidade Efetiva", f"{v_efetiva_kmh:.0f} km/h", f"{v_efetiva_ms:.1f} m/s")

    # Vetor de Dados
    v_vetor_kmh = np.linspace(0, 180, 100)
    v_vetor_efetiva_kmh = np.maximum(0.0, v_vetor_kmh + v_vento_kmh)
    v_vetor_efetiva_ms = v_vetor_efetiva_kmh / 3.6
    fd_vetor_a = 0.5 * rho * (v_vetor_efetiva_ms ** 2) * cd_a * area_a

    fig = go.Figure()
    
    # Curva A
    fig.add_trace(go.Scatter(
        x=v_vetor_kmh, y=fd_vetor_a, mode='lines', name='Objeto A',
        line=dict(color='#00D2FF', width=3),
        fill='tozeroy', fillcolor='rgba(0, 210, 255, 0.08)',
        hovertemplate='<b>Objeto A</b><br>v: %{x:.1f} km/h<br>Fd: %{y:.2f} N<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=[v_kmh], y=[fd_a], mode='markers', name='Ponto A',
        marker=dict(color='#00D2FF', size=10, line=dict(color='#FFFFFF', width=2))
    ))
    fig.add_trace(go.Scatter(
        x=[0, v_kmh, v_kmh], y=[fd_a, fd_a, 0], mode='lines',
        line=dict(color='#00D2FF', width=1, dash='dash'), hoverinfo='skip'
    ))

    # Curva B
    if comparar:
        fd_vetor_b = 0.5 * rho * (v_vetor_efetiva_ms ** 2) * cd_b * area_b
        fig.add_trace(go.Scatter(
            x=v_vetor_kmh, y=fd_vetor_b, mode='lines', name='Objeto B',
            line=dict(color='#FF2A6D', width=3),
            fill='tozeroy', fillcolor='rgba(255, 42, 109, 0.05)',
            hovertemplate='<b>Objeto B</b><br>v: %{x:.1f} km/h<br>Fd: %{y:.2f} N<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=[v_kmh], y=[fd_b], mode='markers', name='Ponto B',
            marker=dict(color='#FF2A6D', size=10, line=dict(color='#FFFFFF', width=2))
        ))
        fig.add_trace(go.Scatter(
            x=[0, v_kmh, v_kmh], y=[fd_b, fd_b, 0], mode='lines',
            line=dict(color='#FF2A6D', width=1, dash='dash'), hoverinfo='skip'
        ))

    max_y = max(5000 if rho < 10 else 1000000, fd_a * 1.2 if not comparar else max(fd_a, fd_b) * 1.2)
    
    fig.update_layout(
        xaxis_title="Velocidade do Corpo (km/h)",
        yaxis_title="Força de Arrasto (N)",
        template="plotly_white",
        height=430,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=comparar,
        legend=dict(x=0.02, y=0.98),
        yaxis=dict(range=[0, max_y], gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False),
        xaxis=dict(gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False)
    )

    st.plotly_chart(fig, use_container_width=True)

# Exportador na Sidebar
with st.sidebar:
    st.markdown("**📂 Exportação de Dados**")
    data_dict = {
        "Fluido": [fluido_selecionado] * 100,
        "Velocidade_Corpo_kmh": v_vetor_kmh,
        "Velocidade_Efetiva_kmh": v_vetor_efetiva_kmh,
        "Forca_Objeto_A_N": fd_vetor_a
    }
    if comparar:
        data_dict["Forca_Objeto_B_N"] = fd_vetor_b
        
    df_export = pd.DataFrame(data_dict)
    csv_data = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Baixar Simulação (CSV)",
        data=csv_data,
        file_name="simulacao_arrasto.csv",
        mime="text/csv",
        use_container_width=True
    )
