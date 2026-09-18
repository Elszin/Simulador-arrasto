import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Simulador Avançado de Aerodinâmica & Mecânica dos Fluidos",
    page_icon="⚡",
    layout="wide"
)

# Estilização CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00D2FF, #FF2A6D, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    </style>
""", unsafe_allow_html=True)

# Dicionários de Dados
FLUIDOS = {
    "Ar Atmosférico (Variável com Alt./Temp.)": {"rho": 1.225, "visc": 1.81e-5},
    "Água Doce (20°C)": {"rho": 998.2, "visc": 1.002e-3},
    "Água do Mar (15°C)": {"rho": 1025.0, "visc": 1.08e-3},
    "Customizado": {"rho": 1.225, "visc": 1.81e-5}
}

PRESETS_VEICULOS = {
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2, "massa": 1100.0, "potencia_cv": 100.0, "crr": 0.012, "comprimento": 4.0},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9, "massa": 1400.0, "potencia_cv": 450.0, "crr": 0.015, "comprimento": 4.5},
    "Carro Elétrico (Design Aerodinâmico)": {"cd": 0.21, "area": 2.1, "massa": 1800.0, "potencia_cv": 300.0, "crr": 0.010, "comprimento": 4.7},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0, "massa": 12000.0, "potencia_cv": 400.0, "crr": 0.008, "comprimento": 12.0},
    "Ciclista em Pé (Gravel/Urbano)": {"cd": 0.90, "area": 0.6, "massa": 85.0, "potencia_cv": 0.4, "crr": 0.005, "comprimento": 1.5},
    "Paraquedista (Aberto)": {"cd": 1.20, "area": 1.5, "massa": 80.0, "potencia_cv": 0.0, "crr": 0.0, "comprimento": 1.8}
}

PRESETS_AQUATICOS = {
    "Lancha Esportiva / Jet Ski": {"cd": 0.35, "area": 1.8, "massa": 900.0, "potencia_cv": 250.0, "crr": 0.0, "comprimento": 5.5},
    "Navio de Carga / Petroleiro": {"cd": 0.85, "area": 45.0, "massa": 500000.0, "potencia_cv": 15000.0, "crr": 0.0, "comprimento": 180.0},
    "Submarino Hidrodinâmico": {"cd": 0.15, "area": 12.0, "massa": 80000.0, "potencia_cv": 4000.0, "crr": 0.0, "comprimento": 35.0},
    "Caiaque / Remo": {"cd": 0.25, "area": 0.5, "massa": 95.0, "potencia_cv": 0.5, "crr": 0.0, "comprimento": 3.2}
}

CIDADES_ALTITUDE = {
    "Nível do Mar (0 m)": 0,
    "São Paulo / Curitiba (~800 m)": 800,
    "Cidade do México (~2240 m)": 2240,
    "La Paz - Bolívia (~3640 m)": 3640
}

# Callbacks para carregar dados dos presets
def carregar_preset_a():
    sel = st.session_state.preset_select_a
    base = PRESETS_AQUATICOS if st.session_state.get('is_aquatico', False) else PRESETS_VEICULOS
    if sel in base:
        p = base[sel]
        st.session_state.cd_a = float(p["cd"])
        st.session_state.area_a = float(p["area"])
        st.session_state.m_a = float(p["massa"])
        st.session_state.p_a = float(p["potencia_cv"])
        st.session_state.comp_a = float(p["comprimento"])

def carregar_preset_b():
    sel = st.session_state.preset_select_b
    base = PRESETS_AQUATICOS if st.session_state.get('is_aquatico', False) else PRESETS_VEICULOS
    if sel in base:
        p = base[sel]
        st.session_state.cd_b = float(p["cd"])
        st.session_state.area_b = float(p["area"])
        st.session_state.m_b = float(p["massa"])
        st.session_state.p_b = float(p["potencia_cv"])
        st.session_state.comp_b = float(p["comprimento"])

# ==========================================
# BARRA LATERAL: CONFIGURAÇÕES AMBIENTAIS E MOTOR
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configurações Gerais")
    st.write("---")
    
    st.markdown("**🌊 Fluido & Termodinâmica**")
    fluido_sel = st.selectbox("Fluido Base:", list(FLUIDOS.keys()), index=0, key="select_fluido_base")
    
    is_ar = "Ar" in fluido_sel
    is_aquatico = "Água" in fluido_sel
    st.session_state.is_aquatico = is_aquatico

    if is_ar:
        st.markdown("**🏔️ Altitude & Temperatura**")
        cidade_preset = st.selectbox("Presets de Altitude:", list(CIDADES_ALTITUDE.keys()), index=0, key="select_cidade_alt")
        val_alt = CIDADES_ALTITUDE[cidade_preset]
        altitude = st.slider("Altitude (m)", 0, 5000, val_alt, 100, key="slider_altitude")
        temp_c = st.slider("Temperatura do Ar (°C)", -10, 50, 20, 1, key="slider_temp")
        
        temp_k = temp_c + 273.15
        p_atm = 101325 * np.exp(-altitude / 8500)
        rho_calc = p_atm / (287.058 * temp_k)
        
        st.caption(f"💡 Densidade do Ar ($\rho$): **{rho_calc:.3f} kg/m³**")
        rho = rho_calc
        viscosidade_din = 1.81e-5 * ((temp_k / 293.15) ** 0.7)
    else:
        rho = st.slider("Densidade ρ (kg/m³)", 0.1, 1100.0, float(FLUIDOS[fluido_sel]["rho"]), 0.1, key="slider_rho_custom")
        viscosidade_din = FLUIDOS[fluido_sel]["visc"]

    st.write("---")
    st.markdown("**⚡ Propulsão & Eficiência**")
    tipo_motor = st.radio("Tipo de Motorização:", ["Combustão (Gasolina/Diesel)", "Elétrico (EV)"], key="radio_tipo_motor")
    
    if tipo_motor == "Combustão (Gasolina/Diesel)":
        preco_comb = st.number_input("Preço Combustível (R$/L):", value=5.80, step=0.10, key="input_preco_comb")
        eficiencia_motor = st.slider("Eficiência Térmica (%)", 15, 45, 30, key="slider_efic_comb") / 100.0
    else:
        preco_kwh = st.number_input("Preço da Energia (R$/kWh):", value=0.85, step=0.05, key="input_preco_kwh")
        eficiencia_motor = st.slider("Eficiência Elétrica (%)", 75, 95, 90, key="slider_efic_eletrica") / 100.0
        capacidade_bateria = st.number_input("Capacidade da Bateria (kWh):", value=60.0, step=5.0, key="input_bateria_kwh")

    st.write("---")
    v_kmh = st.slider("Velocidade do Corpo (km/h)", 0.0, 250.0, 110.0, 1.0, key="slider_v_kmh")
    v_vento_kmh = st.slider("Vento / Correnteza (-Favor / +Contra km/h)", -50.0, 50.0, 0.0, 1.0, key="slider_v_vento")

    st.write("---")
    comparar = st.toggle("🔀 Modo Comparativo de Objetos", value=False, key="toggle_comparar")

# ==========================================
# DEFINIÇÃO DAS COLUNAS (CORRIGIDO)
# ==========================================
col_centro, col_direita = st.columns([2.2, 1], gap="medium")

presets_atuais = PRESETS_AQUATICOS if is_aquatico else PRESETS_VEICULOS

# Inicialização de variáveis no session_state para Objeto A
if "cd_a" not in st.session_state:
    p_init = list(presets_atuais.values())[0]
    st.session_state.cd_a = float(p_init["cd"])
    st.session_state.area_a = float(p_init["area"])
    st.session_state.m_a = float(p_init["massa"])
    st.session_state.p_a = float(p_init["potencia_cv"])
    st.session_state.comp_a = float(p_init["comprimento"])

# Inicialização para Objeto B
if "cd_b" not in st.session_state:
    p_init_b = list(presets_atuais.values())[1 if len(presets_atuais) > 1 else 0]
    st.session_state.cd_b = float(p_init_b["cd"])
    st.session_state.area_b = float(p_init_b["area"])
    st.session_state.m_b = float(p_init_b["massa"])
    st.session_state.p_b = float(p_init_b["potencia_cv"])
    st.session_state.comp_b = float(p_init_b["comprimento"])

# ==========================================
# COLUNA DIREITA: PARÂMETROS DO OBJETO (COM EXPANDER)
# ==========================================
with col_direita:
    st.markdown("### 📐 Geometria & Dinâmica")
    
    # Caixa retrátil para o Objeto A
    with st.expander("🔵 **Objeto A (Referência)**", expanded=True):
        st.selectbox("Preset do Veículo:", list(presets_atuais.keys()), key="preset_select_a", on_change=carregar_preset_a)
        
        cd_a = st.slider("C_d (Arrasto do Corpo):", 0.01, 1.5, st.session_state.cd_a, 0.01, key="cd_a")
        area_a = st.slider("Área Frontal A (m²):", 0.1, 50.0, st.session_state.area_a, 0.1, key="area_a")
        massa_a = st.number_input("Massa do Veículo (kg):", value=st.session_state.m_a, step=50.0, key="m_a")
        potencia_cv_a = st.number_input("Potência do Motor (CV):", value=st.session_state.p_a, step=10.0, key="p_a")
        comprimento_a = st.number_input("Comprimento do Corpo (m):", value=st.session_state.comp_a, step=0.5, key="comp_a")
        
        usar_aerofolio = st.checkbox("➕ Adicionar Aerofólio / Asas", key="check_asa_a")
        if usar_aerofolio:
            cl_a = st.slider("C_L (Downforce):", 0.0, 2.5, 0.8, 0.1, key="cl_asa_a")
            area_asa_a = st.slider("Área da Asa (m²):", 0.1, 3.0, 0.5, 0.1, key="area_asa_a")
            aspect_ratio = 3.5
            cd_induzido_asa_a = (cl_a ** 2) / (np.pi * aspect_ratio)
        else:
            cl_a = 0.0
            area_asa_a = 0.0
            cd_induzido_asa_a = 0.0

    # Caixa retrátil para o Objeto B (Inicia fechada por padrão)
    if comparar:
        with st.expander("🔴 **Objeto B (Comparativo)**", expanded=False):
            st.selectbox("Preset do Veículo:", list(presets_atuais.keys()), key="preset_select_b", on_change=carregar_preset_b)
            
            cd_b = st.slider("C_d (Arrasto do Corpo):", 0.01, 1.5, st.session_state.cd_b, 0.01, key="cd_b")
            area_b = st.slider("Área Frontal B (m²):", 0.1, 50.0, st.session_state.area_b, 0.1, key="area_b")
            massa_b = st.number_input("Massa do Veículo (kg):", value=st.session_state.m_b, step=50.0, key="m_b")
            potencia_cv_b = st.number_input("Potência do Motor (CV):", value=st.session_state.p_b, step=10.0, key="p_b")
            comprimento_b = st.number_input("Comprimento do Corpo (m):", value=st.session_state.comp_b, step=0.5, key="comp_b")
            cl_b = 0.0
            area_asa_b = 0.0
            cd_induzido_asa_b = 0.0

# ==========================================
# CÁLCULOS FÍSICOS
# ==========================================
v_efetiva_kmh = max(0.0, v_kmh + v_vento_kmh)
v_efetiva_ms = v_efetiva_kmh / 3.6
v_propria_ms = v_kmh / 3.6

crr_a = 0.0 if is_aquatico else 0.012

# Arrasto do corpo + Arrasto induzido da asa
fd_corpo_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a
fd_asa_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_induzido_asa_a * area_asa_a if usar_aerofolio else 0.0
fd_a = fd_corpo_a + fd_asa_a

f_rol_a = crr_a * massa_a * 9.81
f_total_a = fd_a + f_rol_a

pot_watts_a = f_total_a * v_propria_ms
pot_cv_a = pot_watts_a / 735.5

downforce_a = 0.5 * rho * (v_efetiva_ms ** 2) * cl_a * area_asa_a
reynolds_a = (rho * v_efetiva_ms * comprimento_a) / viscosidade_din if viscosidade_din > 0 else 0

if tipo_motor == "Combustão (Gasolina/Diesel)":
    consumo_l_h_a = (pot_watts_a / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
    consumo_100km_a = (consumo_l_h_a / v_kmh) * 100 if v_kmh > 0 else 0
    custo_100km_a = consumo_100km_a * preco_comb
    autonomia_a = 0
else:
    consumo_kwh_h_a = (pot_watts_a / eficiencia_motor) / 1000.0 if v_kmh > 0 else 0
    consumo_100km_a = (consumo_kwh_h_a / v_kmh) * 100 if v_kmh > 0 else 0
    custo_100km_a = consumo_100km_a * preco_kwh
    autonomia_a = (capacidade_bateria / consumo_100km_a) * 100 if consumo_100km_a > 0 else 0

if comparar:
    crr_b = 0.0 if is_aquatico else 0.012
    fd_b = 0.5 * rho * (v_efetiva_ms ** 2) * cd_b * area_b
    f_rol_b = crr_b * massa_b * 9.81
    f_total_b = fd_b + f_rol_b
    pot_watts_b = f_total_b * v_propria_ms
    pot_cv_b = pot_watts_b / 735.5
    
    if tipo_motor == "Combustão (Gasolina/Diesel)":
        consumo_l_h_b = (pot_watts_b / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
        consumo_100km_b = (consumo_l_h_b / v_kmh) * 100 if v_kmh > 0 else 0
        custo_100km_b = consumo_100km_b * preco_comb
    else:
        consumo_kwh_h_b = (pot_watts_b / eficiencia_motor) / 1000.0 if v_kmh > 0 else 0
        consumo_100km_b = (consumo_kwh_h_b / v_kmh) * 100 if v_kmh > 0 else 0
        custo_100km_b = consumo_100km_b * preco_kwh

# ==========================================
# COLUNA CENTRAL: DASHBOARD & ABAS
# ==========================================
with col_centro:
    st.markdown('<p class="main-title">⚡ Simulador Avançado de Mecânica dos Fluidos</p>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Força de Arrasto (Fd)", f"{fd_a:.1f} N")
    m2.metric("Potência Exigida", f"{pot_cv_a:.1f} CV")
    
    if tipo_motor == "Combustão (Gasolina/Diesel)":
        m3.metric("Consumo Estimado", f"{consumo_100km_a:.2f} L/100km")
        m4.metric("Custo p/ 100 km", f"R$ {custo_100km_a:.2f}")
    else:
        m3.metric("Consumo de Bateria", f"{consumo_100km_a:.2f} kWh/100km")
        m4.metric("Autonomia Estimada", f"{autonomia_a:.0f} km")

    st.write("---")
    
    tab_grafico, tab_desenho, tab_fisica, tab_ranking = st.tabs([
        "📊 Curvas & Desempenho", 
        "🎨 Perfil & Desenho 2D", 
        "🔬 Análise Física Avançada", 
        "🏆 Comparador de Frota"
    ])

    # TAB 1: CURVAS & DESEMPENHO
    with tab_grafico:
        opcao_grafico = st.radio("Selecione o Eixo Y:", ["Força de Arrasto (N)", "Potência Necessária (CV)", "Custo Financeiro (R$/100km)"], horizontal=True, key="radio_grafico_y")
        
        v_vec = np.linspace(1, 250, 120)
        v_vec_ef = np.maximum(0.1, v_vec + v_vento_kmh) / 3.6
        v_vec_ms = v_vec / 3.6
        
        fd_vec_corpo_a = 0.5 * rho * (v_vec_ef ** 2) * cd_a * area_a
        fd_vec_asa_a = 0.5 * rho * (v_vec_ef ** 2) * cd_induzido_asa_a * area_asa_a if usar_aerofolio else 0.0
        fd_vec_a = fd_vec_corpo_a + fd_vec_asa_a
        
        f_tot_vec_a = fd_vec_a + f_rol_a
        pot_vec_cv_a = (f_tot_vec_a * v_vec_ms) / 735.5
        
        if tipo_motor == "Combustão (Gasolina/Diesel)":
            cons_vec_a = (((f_tot_vec_a * v_vec_ms) / eficiencia_motor) / (32e6 / 3600) / np.maximum(1.0, v_vec)) * 100 * preco_comb
        else:
            cons_vec_a = (((f_tot_vec_a * v_vec_ms) / eficiencia_motor) / 1000.0 / np.maximum(1.0, v_vec)) * 100 * preco_kwh

        if opcao_grafico == "Força de Arrasto (N)":
            y_a = fd_vec_a; y_p_a = fd_a; title_y = "Força de Arrasto (N)"
        elif opcao_grafico == "Potência Necessária (CV)":
            y_a = pot_vec_cv_a; y_p_a = pot_cv_a; title_y = "Potência Requerida (CV)"
        else:
            y_a = cons_vec_a; y_p_a = custo_100km_a; title_y = "Custo R$ / 100km"

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=v_vec, y=y_a, mode='lines', name='Objeto A', line=dict(color='#00D2FF', width=3)))
        fig.add_trace(go.Scatter(x=[v_kmh], y=[y_p_a], mode='markers', name='Ponto Atual A', marker=dict(color='#00D2FF', size=10)))

        if opcao_grafico == "Potência Necessária (CV)":
            fig.add_hline(y=potencia_cv_a, line_dash="dash", line_color="#FFD700", annotation_text=f"Potência Máx Motor ({potencia_cv_a} CV)")

        if comparar:
            fd_vec_b = 0.5 * rho * (v_vec_ef ** 2) * cd_b * area_b
            f_tot_vec_b = fd_vec_b + f_rol_b
            pot_vec_cv_b = (f_tot_vec_b * v_vec_ms) / 735.5
            
            if tipo_motor == "Combustão (Gasolina/Diesel)":
                cons_vec_b = (((f_tot_vec_b * v_vec_ms) / eficiencia_motor) / (32e6 / 3600) / np.maximum(1.0, v_vec)) * 100 * preco_comb
            else:
                cons_vec_b = (((f_tot_vec_b * v_vec_ms) / eficiencia_motor) / 1000.0 / np.maximum(1.0, v_vec)) * 100 * preco_kwh

            y_b = fd_vec_b if opcao_grafico == "Força de Arrasto (N)" else (pot_vec_cv_b if opcao_grafico == "Potência Necessária (CV)" else cons_vec_b)
            y_p_b = fd_b if opcao_grafico == "Força de Arrasto (N)" else (pot_cv_b if opcao_grafico == "Potência Necessária (CV)" else custo_100km_b)
            
            fig.add_trace(go.Scatter(x=v_vec, y=y_b, mode='lines', name='Objeto B', line=dict(color='#FF2A6D', width=3)))
            fig.add_trace(go.Scatter(x=[v_kmh], y=[y_p_b], mode='markers', name='Ponto Atual B', marker=dict(color='#FF2A6D', size=10)))

        fig.update_layout(xaxis_title="Velocidade (km/h)", yaxis_title=title_y, template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: PERFIL & DESENHO 2D DINÂMICO
    with tab_desenho:
        st.markdown("#### 🎨 Túnel de Vento 2D & Vetores de Força")
        fig_draw = go.Figure()
        
        sharpness = max(0.05, 1.0 - (cd_a * 0.8))
        height_geom = np.sqrt(area_a) / 2.0
        
        x_body = np.linspace(-comprimento_a/2, comprimento_a/2, 100)
        y_top = height_geom * (1 - (2 * x_body / comprimento_a)**2) ** sharpness
        y_bottom = -y_top
        
        # Desenho do Corpo
        fig_draw.add_trace(go.Scatter(
            x=np.concatenate([x_body, x_body[::-1]]),
            y=np.concatenate([y_top, y_bottom[::-1]]),
            fill='toself', fillcolor='rgba(0, 210, 255, 0.3)',
            line=dict(color='#00D2FF', width=3), name='Geometria A'
        ))

        # Desenho da Asa/Aerofólio
        if usar_aerofolio:
            x_asa = comprimento_a/2.5
            y_asa = height_geom + 0.3
            fig_draw.add_trace(go.Scatter(
                x=[x_asa - 0.3, x_asa + 0.3], y=[y_asa, y_asa + 0.1],
                mode='lines', line=dict(color='#FFD700', width=6), name='Aerofólio'
            ))
            # Vetor Downforce (Verde)
            fig_draw.add_annotation(
                x=x_asa, y=y_asa - min(2.0, downforce_a * 0.001),
                ax=x_asa, ay=y_asa,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3, arrowcolor="#00FF66",
                text=f"Downforce = {downforce_a:.0f} N"
            )

        # Vetor Arrasto Total (Vermelho)
        vec_scale = 0.002
        fig_draw.add_annotation(
            x=comprimento_a/2 + (fd_a * vec_scale), y=0,
            ax=comprimento_a/2, ay=0,
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

    # TAB 3: ANÁLISE FÍSICA
    with tab_fisica:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("#### 🌀 Número de Reynolds ($Re$)")
            st.write(f"**$Re$ Calculado:** `{reynolds_a:.2e}`")
            
            if reynolds_a < 2e3:
                st.success("Regime: **Laminar**")
            elif 2e3 <= reynolds_a <= 4e3:
                st.warning("Regime: **Transição**")
            else:
                st.error("Regime: **Turbulento**")

            st.markdown("#### 🏎️ Downforce")
            st.write(f"**Peso Extra no Solo:** `{downforce_a:.1f} N` (~`{downforce_a/9.81:.1f} kg`)")
            if usar_aerofolio:
                st.write(f"**Arrasto Extra da Asa:** `{fd_asa_a:.1f} N` (Aumenta o consumo)")

        with col_f2:
            st.markdown("#### ⚖️ Divisão das Forças")
            pct_arrasto = (fd_a / f_total_a) * 100 if f_total_a > 0 else 100
            pct_rolamento = (f_rol_a / f_total_a) * 100 if f_total_a > 0 else 0
            
            fig_pie = px.pie(
                values=[pct_arrasto, pct_rolamento],
                names=['Arrasto Aerodinâmico Total', 'Resistência de Pneu / Rolamento'],
                color_discrete_sequence=['#00D2FF', '#FF2A6D'],
                height=250
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # TAB 4: RANKING DE FROTA
    with tab_ranking:
        st.markdown("#### 🏆 Comparação da Força de Arrasto a 120 km/h")
        nomes_veic, forcas_veic = [], []
        
        for nome, dados in presets_atuais.items():
            fd_temp = 0.5 * rho * ((120/3.6)**2) * dados["cd"] * dados["area"]
            nomes_veic.append(nome)
            forcas_veic.append(fd_temp)
            
        df_rank = pd.DataFrame({"Veículo": nomes_veic, "Arrasto (N)": forcas_veic}).sort_values("Arrasto (N)")
        fig_bar = px.bar(df_rank, x="Arrasto (N)", y="Veículo", orientation='h', color="Arrasto (N)", color_continuous_scale="Viridis", height=350)
        st.plotly_chart(fig_bar, use_container_width=True)
