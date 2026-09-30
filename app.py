import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Simulador de Aerodinâmica",
    page_icon="🏎",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00D2FF, #FF2A6D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Presets de Veículos Terrestres (Apenas Coeficiente de Arrasto e Área Frontal)
PRESETS_VEICULOS = {
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9},
    "SUV / Caminhonete": {"cd": 0.40, "area": 2.8},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0},
    "Ciclista em Pé": {"cd": 0.90, "area": 0.6}
}

def carregar_preset_a():
    sel = st.session_state.preset_select_a
    if sel in PRESETS_VEICULOS:
        p = PRESETS_VEICULOS[sel]
        st.session_state.cd_a = float(p["cd"])
        st.session_state.area_a = float(p["area"])

def carregar_preset_b():
    sel = st.session_state.preset_select_b
    if sel in PRESETS_VEICULOS:
        p = PRESETS_VEICULOS[sel]
        st.session_state.cd_b = float(p["cd"])
        st.session_state.area_b = float(p["area"])

# ==========================================
# BARRA LATERAL: PARÂMETROS AMBIENTAIS
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configurações do Teste")
    st.write("---")
    
    st.markdown("**🏔️ Altitude & Atmosfera**")
    altitude = st.slider("Altitude (m)", 0, 5000, 0, 100, key="slider_altitude_custom")
    temp_c = st.slider("Temperatura do Ar (°C)", -10, 50, 20, 1, key="slider_temp")
    
    temp_k = temp_c + 273.15
    p_atm = 101325 * np.exp(-altitude / 8500)
    rho = p_atm / (287.058 * temp_k)
    st.caption(f"💡 Densidade do Ar ($\rho$): **{rho:.3f} kg/m³**")

    st.write("---")
    v_kmh = st.slider("Velocidade do Veículo (km/h)", 10.0, 220.0, 110.0, 5.0, key="slider_v_kmh")
    v_vento_kmh = st.slider("Vento Frontal (+Contra / -Favor) (km/h)", -40.0, 40.0, 0.0, 5.0, key="slider_v_vento")

    st.write("---")
    comparar = st.toggle("🔀 Modo Comparativo (Objeto B)", value=False, key="toggle_comparar")

# ==========================================
# INICIALIZAÇÃO DE ESTADO
# ==========================================
if "cd_a" not in st.session_state:
    p_init = list(PRESETS_VEICULOS.values())[0]
    st.session_state.cd_a = float(p_init["cd"])
    st.session_state.area_a = float(p_init["area"])

if "cd_b" not in st.session_state:
    p_init_b = list(PRESETS_VEICULOS.values())[1]
    st.session_state.cd_b = float(p_init_b["cd"])
    st.session_state.area_b = float(p_init_b["area"])

# ==========================================
# COLUNA DIREITA: AJUSTES DOS OBJETOS
# ==========================================
col_centro, col_direita = st.columns([2.2, 1], gap="medium")

with col_direita:
    st.markdown("### 📐 Parâmetros do Veículo")
    
    with st.expander("🔵 **Objeto A (Referência)**", expanded=True):
        st.selectbox("Modelo Base:", list(PRESETS_VEICULOS.keys()), key="preset_select_a", on_change=carregar_preset_a)
        
        cd_a = st.slider("C_d (Coef. de Arrasto):", 0.15, 1.20, st.session_state.cd_a, 0.01, key="cd_a")
        area_a = st.slider("Área Frontal (m²):", 0.5, 10.0, st.session_state.area_a, 0.1, key="area_a")
        
        usar_aerofolio = st.checkbox("➕ Adicionar Aerofólio", key="check_asa_a")
        if usar_aerofolio:
            cl_a = st.slider("C_L (Downforce):", 0.1, 2.0, 0.8, 0.1, key="cl_asa_a")
            area_asa_a = st.slider("Área da Asa (m²):", 0.1, 2.0, 0.4, 0.1, key="area_asa_a")
            cd_induzido_asa_a = (cl_a ** 2) / (np.pi * 3.5)
        else:
            cl_a, area_asa_a, cd_induzido_asa_a = 0.0, 0.0, 0.0

    if comparar:
        with st.expander("🔴 **Objeto B (Comparativo)**", expanded=False):
            st.selectbox("Modelo Base:", list(PRESETS_VEICULOS.keys()), key="preset_select_b", on_change=carregar_preset_b)
            
            cd_b = st.slider("C_d (Coef. de Arrasto):", 0.15, 1.20, st.session_state.cd_b, 0.01, key="cd_b")
            area_b = st.slider("Área Frontal (m²):", 0.5, 10.0, st.session_state.area_b, 0.1, key="area_b")
            cl_b, area_asa_b, cd_induzido_asa_b = 0.0, 0.0, 0.0

# ==========================================
# CÁLCULOS FÍSICOS (ESTRITAMENTE ARRASTO)
# ==========================================
v_efetiva_ms = max(0.0, v_kmh + v_vento_kmh) / 3.6

# Objeto A
fd_corpo_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a
fd_asa_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_induzido_asa_a * area_asa_a if usar_aerofolio else 0.0
fd_a = fd_corpo_a + fd_asa_a

# Objeto B (se ativo)
if comparar:
    fd_b = 0.5 * rho * (v_efetiva_ms ** 2) * cd_b * area_b

# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
with col_centro:
    st.markdown('<p class="main-title">🏎️ Simulador de Força de Arrasto</p>', unsafe_allow_html=True)
    
    # Exibição da Fórmula em Destaque no Topo
    st.markdown("---")
    st.markdown("📌 **Fórmula da Força de Arrasto ($F_d$):**")
    st.latex(r"F_d = \frac{1}{2} \cdot \rho \cdot v^2 \cdot C_d \cdot A")
    st.caption("Onde: $\\rho$ = Densidade do ar | $v$ = Velocidade efetiva | $C_d$ = Coeficiente de arrasto | $A$ = Área frontal")
    st.markdown("---")

    m1, m2 = st.columns(2)
    m1.metric("Força de Arrasto (Fd) - Objeto A", f"{fd_a:.1f} N")
    if comparar:
        m2.metric("Força de Arrasto (Fd) - Objeto B", f"{fd_b:.1f} N")
    else:
        m2.metric("Densidade do Ar ($\rho$)", f"{rho:.3f} kg/m³")

    st.write("---")
    st.markdown("#### 📊 Curva de Desempenho Aerodinâmico")

    # Gráfico Dinâmico Baseado na Velocidade
    v_max_grafico = max(40.0, v_kmh + 15.0)
    v_vec = np.linspace(0, v_max_grafico, 100)
    v_vec_ef = np.maximum(0.1, v_vec + v_vento_kmh) / 3.6
    
    fd_vec_a = (0.5 * rho * (v_vec_ef ** 2) * cd_a * area_a) + (0.5 * rho * (v_vec_ef ** 2) * cd_induzido_asa_a * area_asa_a if usar_aerofolio else 0.0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v_vec, y=fd_vec_a, mode='lines', name='Objeto A', line=dict(color='#00D2FF', width=3)))
    fig.add_trace(go.Scatter(x=[v_kmh], y=[fd_a], mode='markers', name='Ponto Atual A', marker=dict(color='#00D2FF', size=12)))

    # Linhas tracejadas de projeção do Objeto A
    fig.add_shape(type="line", x0=v_kmh, y0=0, x1=v_kmh, y1=fd_a,
                  line=dict(color="#00D2FF", width=1.5, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=fd_a, x1=v_kmh, y1=fd_a,
                  line=dict(color="#00D2FF", width=1.5, dash="dash"))

    if comparar:
        fd_vec_b = 0.5 * rho * (v_vec_ef ** 2) * cd_b * area_b
        fig.add_trace(go.Scatter(x=v_vec, y=fd_vec_b, mode='lines', name='Objeto B', line=dict(color='#FF2A6D', width=3)))
        fig.add_trace(go.Scatter(x=[v_kmh], y=[fd_b], mode='markers', name='Ponto Atual B', marker=dict(color='#FF2A6D', size=12)))

        # Linhas tracejadas de projeção do Objeto B
        fig.add_shape(type="line", x0=v_kmh, y0=0, x1=v_kmh, y1=fd_b,
                      line=dict(color="#FF2A6D", width=1.5, dash="dash"))
        fig.add_shape(type="line", x0=0, y0=fd_b, x1=v_kmh, y1=fd_b,
                      line=dict(color="#FF2A6D", width=1.5, dash="dash"))

    fig.update_layout(
        xaxis=dict(range=[0, v_max_grafico], title="Velocidade (km/h)"),
        yaxis=dict(title="Força de Arrasto (N)"),
        template="plotly_white", 
        height=480
    )
    st.plotly_chart(fig, use_container_width=True)
