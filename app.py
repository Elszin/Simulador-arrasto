import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Simulador de Aerodinâmica & Consumo",
    page_icon="🏎️",
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
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Presets de Veículos Terrestres
PRESETS_VEICULOS = {
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2, "massa": 1100.0, "potencia_cv": 100.0, "comprimento": 4.0},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9, "massa": 1400.0, "potencia_cv": 450.0, "comprimento": 4.5},
    "SUV / Caminhonete": {"cd": 0.40, "area": 2.8, "massa": 1900.0, "potencia_cv": 180.0, "comprimento": 4.8},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0, "massa": 12000.0, "potencia_cv": 400.0, "comprimento": 12.0},
    "Ciclista em Pé": {"cd": 0.90, "area": 0.6, "massa": 85.0, "potencia_cv": 0.4, "comprimento": 1.5}
}

CIDADES_ALTITUDE = {
    "Personalizado": None,
    "Nível do Mar (0 m)": 0,
    "São Paulo / Curitiba (~800 m)": 800,
    "Cidade do México (~2240 m)": 2240,
    "La Paz - Bolívia (~3640 m)": 3640
}

# Callbacks para carregar dados dos presets de veículos
def carregar_preset_a():
    sel = st.session_state.preset_select_a
    if sel in PRESETS_VEICULOS:
        p = PRESETS_VEICULOS[sel]
        st.session_state.cd_a = float(p["cd"])
        st.session_state.area_a = float(p["area"])
        st.session_state.m_a = float(p["massa"])
        st.session_state.p_a = float(p["potencia_cv"])
        st.session_state.comp_a = float(p["comprimento"])

def carregar_preset_b():
    sel = st.session_state.preset_select_b
    if sel in PRESETS_VEICULOS:
        p = PRESETS_VEICULOS[sel]
        st.session_state.cd_b = float(p["cd"])
        st.session_state.area_b = float(p["area"])
        st.session_state.m_b = float(p["massa"])
        st.session_state.p_b = float(p["potencia_cv"])
        st.session_state.comp_b = float(p["comprimento"])

# ==========================================
# BARRA LATERAL: PARÂMETROS AMBIENTAIS & OPERAÇÃO
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configurações do Teste")
    st.write("---")
    
    st.markdown("**🏔️ Altitude & Atmosfera**")
    cidade_preset = st.selectbox("Presets de Altitude:", list(CIDADES_ALTITUDE.keys()), index=0, key="select_cidade_alt")
    
    # Lógica do modo personalizado vs preset fixo
    is_custom = (cidade_preset == "Personalizado")
    
    if not is_custom:
        val_alt = CIDADES_ALTITUDE[cidade_preset]
        altitude = st.slider("Altitude (m)", 0, 5000, val_alt, 100, disabled=True, key="slider_altitude_preset")
    else:
        altitude = st.slider("Altitude Personalizada (m)", 0, 5000, 0, 100, disabled=False, key="slider_altitude_custom")
    
    temp_c = st.slider("Temperatura do Ar (°C)", -10, 50, 20, 1, key="slider_temp")
    
    # Cálculo físico da densidade do ar em função da altitude e temperatura
    temp_k = temp_c + 273.15
    p_atm = 101325 * np.exp(-altitude / 8500)
    rho = p_atm / (287.058 * temp_k)
    st.caption(f"💡 Densidade do Ar ($\rho$): **{rho:.3f} kg/m³**")

    st.write("---")
    st.markdown("**⛽ Combustível & Motor**")
    preco_comb = st.number_input("Preço do Combustível (R$/L):", value=5.80, step=0.10, key="input_preco_comb")
    eficiencia_motor = st.slider("Eficiência Térmica do Motor (%)", 15, 45, 30, key="slider_efic_comb") / 100.0

    st.write("---")
    v_kmh = st.slider("Velocidade do Veículo (km/h)", 10.0, 220.0, 110.0, 5.0, key="slider_v_kmh")
    v_vento_kmh = st.slider("Vento Frontal (+Contra / -Favor) (km/h)", -40.0, 40.0, 0.0, 5.0, key="slider_v_vento")

    st.write("---")
    comparar = st.toggle("🔀 Modo Comparativo (Objeto B)", value=False, key="toggle_comparar")

# ==========================================
# COLUNAS DA INTERFACE PRINCIPAL
# ==========================================
col_centro, col_direita = st.columns([2.2, 1], gap="medium")

# Inicialização de Session State
if "cd_a" not in st.session_state:
    p_init = list(PRESETS_VEICULOS.values())[0]
    st.session_state.cd_a = float(p_init["cd"])
    st.session_state.area_a = float(p_init["area"])
    st.session_state.m_a = float(p_init["massa"])
    st.session_state.p_a = float(p_init["potencia_cv"])
    st.session_state.comp_a = float(p_init["comprimento"])

if "cd_b" not in st.session_state:
    p_init_b = list(PRESETS_VEICULOS.values())[1]
    st.session_state.cd_b = float(p_init_b["cd"])
    st.session_state.area_b = float(p_init_b["area"])
    st.session_state.m_b = float(p_init_b["massa"])
    st.session_state.p_b = float(p_init_b["potencia_cv"])
    st.session_state.comp_b = float(p_init_b["comprimento"])

# ==========================================
# COLUNA DIREITA: AJUSTES DOS OBJETOS (CAIXAS RETRÁTEIS)
# ==========================================
with col_direita:
    st.markdown("### 📐 Geometria do Veículo")
    
    with st.expander("🔵 **Objeto A (Referência)**", expanded=True):
        st.selectbox("Modelo Base:", list(PRESETS_VEICULOS.keys()), key="preset_select_a", on_change=carregar_preset_a)
        
        cd_a = st.slider("C_d (Coef. de Arrasto):", 0.15, 1.20, st.session_state.cd_a, 0.01, key="cd_a")
        area_a = st.slider("Área Frontal (m²):", 0.5, 10.0, st.session_state.area_a, 0.1, key="area_a")
        massa_a = st.number_input("Massa (kg):", value=st.session_state.m_a, step=50.0, key="m_a")
        potencia_cv_a = st.number_input("Potência Motor (CV):", value=st.session_state.p_a, step=10.0, key="p_a")
        comprimento_a = st.number_input("Comprimento (m):", value=st.session_state.comp_a, step=0.5, key="comp_a")
        
        usar_aerofolio = st.checkbox("➕ Adicionar Aerofólio", key="check_asa_a")
        if usar_aerofolio:
            cl_a = st.slider("C_L (Downforce):", 0.1, 2.0, 0.8, 0.1, key="cl_asa_a")
            area_asa_a = st.slider("Área da Asa (m²):", 0.1, 2.0, 0.4, 0.1, key="area_asa_a")
            # Arrasto induzido gerado pela asa
            cd_induzido_asa_a = (cl_a ** 2) / (np.pi * 3.5)
        else:
            cl_a = 0.0
            area_asa_a = 0.0
            cd_induzido_asa_a = 0.0

    if comparar:
        with st.expander("🔴 **Objeto B (Comparativo)**", expanded=False):
            st.selectbox("Modelo Base:", list(PRESETS_VEICULOS.keys()), key="preset_select_b", on_change=carregar_preset_b)
            
            cd_b = st.slider("C_d (Coef. de Arrasto):", 0.15, 1.20, st.session_state.cd_b, 0.01, key="cd_b")
            area_b = st.slider("Área Frontal (m²):", 0.5, 10.0, st.session_state.area_b, 0.1, key="area_b")
            massa_b = st.number_input("Massa (kg):", value=st.session_state.m_b, step=50.0, key="m_b")
            potencia_cv_b = st.number_input("Potência Motor (CV):", value=st.session_state.p_b, step=10.0, key="p_b")
            comprimento_b = st.number_input("Comprimento (m):", value=st.session_state.comp_b, step=0.5, key="comp_b")
            cl_b, area_asa_b, cd_induzido_asa_b = 0.0, 0.0, 0.0

# ==========================================
# CÁLCULOS FÍSICOS
# ==========================================
v_efetiva_ms = max(0.0, v_kmh + v_vento_kmh) / 3.6
v_propria_ms = v_kmh / 3.6
crr = 0.012  # Coeficiente de resistência ao rolamento dos pneus

# Objeto A
fd_corpo_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a
fd_asa_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_induzido_asa_a * area_asa_a if usar_aerofolio else 0.0
fd_a = fd_corpo_a + fd_asa_a

f_rol_a = crr * massa_a * 9.81
f_total_a = fd_a + f_rol_a

pot_watts_a = f_total_a * v_propria_ms
pot_cv_a = pot_watts_a / 735.5

downforce_a = 0.5 * rho * (v_efetiva_ms ** 2) * cl_a * area_asa_a

consumo_l_h_a = (pot_watts_a / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
consumo_100km_a = (consumo_l_h_a / v_kmh) * 100 if v_kmh > 0 else 0
custo_100km_a = consumo_100km_a * preco_comb

# Objeto B (se ativo)
if comparar:
    fd_b = 0.5 * rho * (v_efetiva_ms ** 2) * cd_b * area_b
    f_rol_b = crr * massa_b * 9.81
    f_total_b = fd_b + f_rol_b
    pot_watts_b = f_total_b * v_propria_ms
    pot_cv_b = pot_watts_b / 735.5
    consumo_l_h_b = (pot_watts_b / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
    consumo_100km_b = (consumo_l_h_b / v_kmh) * 100 if v_kmh > 0 else 0
    custo_100km_b = consumo_100km_b * preco_comb

# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
with col_centro:
    st.markdown('<p class="main-title">🏎️ Simulador Aerodinâmico de Veículos</p>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Força de Arrasto (Fd)", f"{fd_a:.1f} N")
    m2.metric("Potência Exigida", f"{pot_cv_a:.1f} CV")
    m3.metric("Consumo Estimado", f"{consumo_100km_a:.2f} L/100km")
    m4.metric("Custo p/ 100 km", f"R$ {custo_100km_a:.2f}")

    st.write("---")
    
    tab_grafico, tab_desenho, tab_pie = st.tabs([
        "📊 Curvas de Desempenho", 
        "🎨 Perfil 2D & Vetores", 
        "⚖️ Divisão das Forças"
    ])

    # TAB 1: CURVAS DE DESEMPENHO
    with tab_grafico:
        opcao_grafico = st.radio("Métrica a exibir:", ["Força de Arrasto (N)", "Potência Necessária (CV)", "Custo (R$/100km)"], horizontal=True)
        
        v_vec = np.linspace(10, 220, 100)
        v_vec_ef = np.maximum(0.1, v_vec + v_vento_kmh) / 3.6
        v_vec_ms = v_vec / 3.6
        
        fd_vec_a = (0.5 * rho * (v_vec_ef ** 2) * cd_a * area_a) + (0.5 * rho * (v_vec_ef ** 2) * cd_induzido_asa_a * area_asa_a if usar_aerofolio else 0.0)
        f_tot_vec_a = fd_vec_a + f_rol_a
        pot_vec_cv_a = (f_tot_vec_a * v_vec_ms) / 735.5
        cons_vec_a = (((f_tot_vec_a * v_vec_ms) / eficiencia_motor) / (32e6 / 3600) / np.maximum(1.0, v_vec)) * 100 * preco_comb

        if opcao_grafico == "Força de Arrasto (N)":
            y_a, y_p_a, title_y = fd_vec_a, fd_a, "Força de Arrasto (N)"
        elif opcao_grafico == "Potência Necessária (CV)":
            y_a, y_p_a, title_y = pot_vec_cv_a, pot_cv_a, "Potência Requerida (CV)"
        else:
            y_a, y_p_a, title_y = cons_vec_a, custo_100km_a, "Custo R$ / 100km"

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=v_vec, y=y_a, mode='lines', name='Objeto A', line=dict(color='#00D2FF', width=3)))
        fig.add_trace(go.Scatter(x=[v_kmh], y=[y_p_a], mode='markers', name='Ponto Atual A', marker=dict(color='#00D2FF', size=10)))

        if comparar:
            fd_vec_b = 0.5 * rho * (v_vec_ef ** 2) * cd_b * area_b
            f_tot_vec_b = fd_vec_b + f_rol_b
            pot_vec_cv_b = (f_tot_vec_b * v_vec_ms) / 735.5
            cons_vec_b = (((f_tot_vec_b * v_vec_ms) / eficiencia_motor) / (32e6 / 3600) / np.maximum(1.0, v_vec)) * 100 * preco_comb

            y_b = fd_vec_b if opcao_grafico == "Força de Arrasto (N)" else (pot_vec_cv_b if opcao_grafico == "Potência Necessária (CV)" else cons_vec_b)
            y_p_b = fd_b if opcao_grafico == "Força de Arrasto (N)" else (pot_cv_b if opcao_grafico == "Potência Necessária (CV)" else custo_100km_b)

            fig.add_trace(go.Scatter(x=v_vec, y=y_b, mode='lines', name='Objeto B', line=dict(color='#FF2A6D', width=3)))
            fig.add_trace(go.Scatter(x=[v_kmh], y=[y_p_b], mode='markers', name='Ponto Atual B', marker=dict(color='#FF2A6D', size=10)))

        fig.update_layout(xaxis_title="Velocidade (km/h)", yaxis_title=title_y, template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: PERFIL 2D DINÂMICO
    with tab_desenho:
        st.markdown("#### 🎨 Túnel de Vento 2D & Vetores de Força")
        fig_draw = go.Figure()
        
        sharpness = max(0.05, 1.0 - (cd_a * 0.8))
        height_geom = np.sqrt(area_a) / 2.0
        
        x_body = np.linspace(-comprimento_a/2, comprimento_a/2, 100)
        y_top = height_geom * (1 - (2 * x_body / comprimento_a)**2) ** sharpness
        y_bottom = -y_top
        
        # Geometria do Corpo
        fig_draw.add_trace(go.Scatter(
            x=np.concatenate([x_body, x_body[::-1]]),
            y=np.concatenate([y_top, y_bottom[::-1]]),
            fill='toself', fillcolor='rgba(0, 210, 255, 0.3)',
            line=dict(color='#00D2FF', width=3), name='Objeto A'
        ))

        # Aerofólio & Downforce
        if usar_aerofolio:
            x_asa = comprimento_a/2.5
            y_asa = height_geom + 0.3
            fig_draw.add_trace(go.Scatter(
                x=[x_asa - 0.3, x_asa + 0.3], y=[y_asa, y_asa + 0.1],
                mode='lines', line=dict(color='#FFD700', width=6), name='Aerofólio'
            ))
            fig_draw.add_annotation(
                x=x_asa, y=y_asa - min(2.0, downforce_a * 0.001), ax=x_asa, ay=y_asa,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3, arrowcolor="#00FF66",
                text=f"Downforce = {downforce_a:.0f} N"
            )

        # Seta do Arrasto
        vec_scale = 0.002
        fig_draw.add_annotation(
            x=comprimento_a/2 + (fd_a * vec_scale), y=0, ax=comprimento_a/2, ay=0,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3, arrowcolor="#FF2A6D",
            text=f"Fd = {fd_a:.0f} N"
        )

        fig_draw.update_layout(
            template="plotly_dark", height=380,
            xaxis=dict(range=[-comprimento_a*1.2, comprimento_a*2.2], title="Comprimento (m)"),
            yaxis=dict(range=[-height_geom*3, height_geom*3], title="Altura (m)"),
            showlegend=False
        )
        st.plotly_chart(fig_draw, use_container_width=True)

    # TAB 3: DIVISÃO DE RESISTÊNCIAS
    with tab_pie:
        st.markdown("#### ⚖️ Arrasto Aerodinâmico vs. Pneu (Rolamento)")
        pct_arrasto = (fd_a / f_total_a) * 100 if f_total_a > 0 else 100
        pct_rolamento = (f_rol_a / f_total_a) * 100 if f_total_a > 0 else 0
        
        fig_pie = px.pie(
            values=[pct_arrasto, pct_rolamento],
            names=['Arrasto Aerodinâmico ($F_d$)', 'Resistência de Rolamento ($F_{rol}$)'],
            color_discrete_sequence=['#00D2FF', '#FF2A6D'],
            height=300
        )
        st.plotly_chart(fig_pie, use_container_width=True)
