import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="Simulador Avançado de Aerodinâmica & Mecânica dos Fluidos",
    page_icon="⚡",
    layout="wide"
)

# Estilização CSS Avançada
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
        background: -webkit-linear-gradient(45deg, #00D2FF, #FF2A6D, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .variable-card {
        background-color: #0E1117;
        color: #FAFAFA;
        border-left: 4px solid #00D2FF;
        padding: 8px 12px;
        margin-bottom: 6px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    
    .status-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8rem;
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

PRESETS_TERRESTRES = {
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2, "massa": 1100, "potencia_cv": 100, "crr": 0.012, "comprimento": 4.0},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9, "massa": 1400, "potencia_cv": 450, "crr": 0.015, "comprimento": 4.5},
    "Carro Elétrico (Design Aerodinâmico)": {"cd": 0.21, "area": 2.1, "massa": 1800, "potencia_cv": 300, "crr": 0.010, "comprimento": 4.7},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0, "massa": 12000, "potencia_cv": 400, "crr": 0.008, "comprimento": 12.0},
    "Ciclista em Pé (Gravel/Urbano)": {"cd": 0.90, "area": 0.6, "massa": 85, "potencia_cv": 0.4, "crr": 0.005, "comprimento": 1.5},
    "Paraquedista (Aberto)": {"cd": 1.20, "area": 1.5, "massa": 80, "potencia_cv": 0, "crr": 0.0, "comprimento": 1.8}
}

PRESETS_AQUATICOS = {
    "Lancha Esportiva / Jet Ski": {"cd": 0.25, "area": 1.8, "massa": 900, "potencia_cv": 250, "crr": 0.0, "comprimento": 5.0},
    "Barco de Carga / Navio": {"cd": 0.45, "area": 25.0, "massa": 45000, "potencia_cv": 1200, "crr": 0.0, "comprimento": 20.0},
    "Submarino Hidrodinâmico": {"cd": 0.12, "area": 6.0, "massa": 25000, "potencia_cv": 800, "crr": 0.0, "comprimento": 15.0},
    "Caiaque de Corrida": {"cd": 0.30, "area": 0.4, "massa": 95, "potencia_cv": 0.6, "crr": 0.0, "comprimento": 4.5}
}

CIDADES_ALTITUDE = {
    "Personalizado": None,
    "Nível do Mar (0 m)": 0,
    "São Paulo / Curitiba (~800 m)": 800,
    "Cidade do México (~2240 m)": 2240,
    "La Paz - Bolívia (~3640 m)": 3640
}

# Funções para sincronização de presets no session_state
def carregar_preset_a():
    preset_nome = st.session_state.get("select_preset_a")
    if preset_nome and preset_nome in presets_atuais:
        p = presets_atuais[preset_nome]
        st.session_state.cd_a = float(p["cd"])
        st.session_state.area_a = float(p["area"])
        st.session_state.m_a = float(p["massa"])
        st.session_state.p_a = float(p["potencia_cv"])
        st.session_state.comp_a = float(p["comprimento"])

def carregar_preset_b():
    preset_nome = st.session_state.get("select_preset_b")
    if preset_nome and preset_nome in presets_atuais:
        p = presets_atuais[preset_nome]
        st.session_state.cd_b = float(p["cd"])
        st.session_state.area_b = float(p["area"])
        st.session_state.m_b = float(p["massa"])
        st.session_state.p_b = float(p["potencia_cv"])
        st.session_state.comp_b = float(p["comprimento"])

# Initialização de estado para Objeto A e B
if "cd_a" not in st.session_state:
    p_default = PRESETS_TERRESTRES["Carro Popular (Hatch/Sedan)"]
    st.session_state.cd_a = float(p_default["cd"])
    st.session_state.area_a = float(p_default["area"])
    st.session_state.m_a = float(p_default["massa"])
    st.session_state.p_a = float(p_default["potencia_cv"])
    st.session_state.comp_a = float(p_default["comprimento"])

if "cd_b" not in st.session_state:
    p_default_b = PRESETS_TERRESTRES["Carro Esportivo (Supercarro)"]
    st.session_state.cd_b = float(p_default_b["cd"])
    st.session_state.area_b = float(p_default_b["area"])
    st.session_state.m_b = float(p_default_b["massa"])
    st.session_state.p_b = float(p_default_b["potencia_cv"])
    st.session_state.comp_b = float(p_default_b["comprimento"])

with st.sidebar:
    st.markdown("### ⚙️ Configurações Gerais")
    st.write("---")
    
    st.markdown("**🌊 Fluido & Termodinâmica**")
    fluido_sel = st.selectbox("Fluido Base:", list(FLUIDOS.keys()), index=0)
    is_ar = "Ar" in fluido_sel
    is_agua = "Água" in fluido_sel
    presets_atuais = PRESETS_AQUATICOS if is_agua else PRESETS_TERRESTRES

    if is_ar:
        st.markdown("**🏔️ Simulador de Altitude & Temperatura**")
        cidade_preset = st.selectbox("Presets de Altitude:", list(CIDADES_ALTITUDE.keys()), index=1)
        val_alt = CIDADES_ALTITUDE[cidade_preset] if CIDADES_ALTITUDE[cidade_preset] is not None else 0
        altitude = st.slider("Altitude (m)", 0, 5000, val_alt, 100)
        temp_c = st.slider("Temperatura do Ar (°C)", -10, 50, 20, 1)
        
        # Correção Barométrica + Temperatura (Gases Ideais)
        temp_k = temp_c + 273.15
        p_atm = 101325 * np.exp(-altitude / 8500) # Pressão em Pa
        rho_calc = p_atm / (287.058 * temp_k)     # Densidade corrigida (kg/m³)
        
        st.caption(f"💡 Densidade do Ar ($\rho$): **{rho_calc:.3f} kg/m³**")
        rho = rho_calc
        viscosidade_din = 1.81e-5 * ((temp_k / 293.15) ** 0.7)
    else:
        rho = st.slider("Densidade ρ (kg/m³)", 0.1, 1100.0, FLUIDOS[fluido_sel]["rho"], 0.1)
        viscosidade_din = FLUIDOS[fluido_sel]["visc"]

    st.write("---")
    st.markdown("**⚡ Propulsão & Eficiência**")
    tipo_motor = st.radio("Tipo de Motorização:", ["Combustão (Gasolina/Diesel)", "Elétrico (EV)"])
    
    if tipo_motor == "Combustão (Gasolina/Diesel)":
        preco_comb = st.number_input("Preço Combustível (R$/L):", value=5.80, step=0.10)
        eficiencia_motor = st.slider("Eficiência Térmica (%)", 15, 45, 30) / 100.0
    else:
        preco_kwh = st.number_input("Preço da Energia (R$/kWh):", value=0.85, step=0.05)
        eficiencia_motor = st.slider("Eficiência Elétrica (%)", 75, 95, 90) / 100.0
        capacidade_bateria = st.number_input("Capacidade da Bateria (kWh):", value=60.0, step=5.0)

    st.write("---")
    comparar = st.toggle("🔀 Modo Comparativo de Objetos", value=False)

# DIVISÃO DA ÁREA PRINCIPAL
col_centro, col_direita = st.columns([2.2, 1], gap="medium")

# ==========================================
# COLUNA DIREITA: PARÂMETROS DO OBJETO
# ==========================================
with col_direita:
    st.markdown("### 📐 Geometria & Dinâmica")
    
    with st.container(border=True):
        st.markdown("**🔵 Objeto A (Referência)**")
        
        # Sincronizador de Presets com Callback
        st.selectbox(
            "Preset do Veículo:",
            list(presets_atuais.keys()),
            key="select_preset_a",
            on_change=carregar_preset_a
        )
        
        cd_a = st.slider("C_d (Arrasto):", 0.01, 1.5, key="cd_a", step=0.01)
        area_a = st.slider("Área Frontal A (m²):", 0.1, 25.0, key="area_a", step=0.1)
        massa_a = st.number_input("Massa do Veículo (kg):", key="m_a", step=50.0)
        potencia_cv_a = st.number_input("Potência do Motor (CV):", key="p_a", step=10.0)
        comprimento_a = st.number_input("Comprimento do Corpo (m):", key="comp_a", step=0.5)
        
        # Módulo Asa / Downforce opcional
        usar_aerofolio = st.checkbox("➕ Adicionar Aerofólio / Asas")
        if usar_aerofolio:
            cl_a = st.slider("C_L (Sustentação/Downforce):", 0.0, 2.5, 0.8, 0.1)
            area_asa = st.slider("Área da Asa (m²):", 0.1, 3.0, 0.5, 0.1)
        else:
            cl_a = 0.0
            area_asa = 0.0

    if comparar:
        with st.container(border=True):
            st.markdown("**🔴 Objeto B (Comparativo)**")
            st.selectbox(
                "Preset do Veículo B:",
                list(presets_atuais.keys()),
                key="select_preset_b",
                on_change=carregar_preset_b
            )
            
            cd_b = st.slider("C_d (Arrasto):", 0.01, 1.5, key="cd_b", step=0.01)
            area_b = st.slider("Área Frontal B (m²):", 0.1, 25.0, key="area_b", step=0.1)
            massa_b = st.number_input("Massa do Veículo (kg):", key="m_b", step=50.0)
            potencia_cv_b = st.number_input("Potência do Motor (CV):", key="p_b", step=10.0)
            comprimento_b = st.number_input("Comprimento do Corpo (m):", key="comp_b", step=0.5)

# BARRA LATERAL: CONFIGURAÇÕES AMBIENTAIS E MOTOR
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configurações Gerais")
    st.write("---")
    
    st.markdown("**🌊 Fluido & Termodinâmica**")
    fluido_sel = st.selectbox("Fluido Base:", list(FLUIDOS.keys()), index=0)
    is_ar = "Ar" in fluido_sel
    is_agua = "Água" in fluido_sel
    presets_atuais = PRESETS_AQUATICOS if is_agua else PRESETS_TERRESTRES

    if is_ar:
        st.markdown("**🏔️ Simulador de Altitude & Temperatura**")
        cidade_preset = st.selectbox("Presets de Altitude:", list(CIDADES_ALTITUDE.keys()), index=1)
        val_alt = CIDADES_ALTITUDE[cidade_preset] if CIDADES_ALTITUDE[cidade_preset] is not None else 0
        altitude = st.slider("Altitude (m)", 0, 5000, val_alt, 100)
        temp_c = st.slider("Temperatura do Ar (°C)", -10, 50, 20, 1)
        
        # Correção Barométrica + Temperatura (Gases Ideais)
        temp_k = temp_c + 273.15
        p_atm = 101325 * np.exp(-altitude / 8500) # Pressão em Pa
        rho_calc = p_atm / (287.058 * temp_k)     # Densidade corrigida (kg/m³)
        
        st.caption(f"💡 Densidade do Ar ($\rho$): **{rho_calc:.3f} kg/m³**")
        rho = rho_calc
        viscosidade_din = 1.81e-5 * ((temp_k / 293.15) ** 0.7) # Correção Sutherland simplificada
    else:
        rho = st.slider("Densidade ρ (kg/m³)", 0.1, 1100.0, FLUIDOS[fluido_sel]["rho"], 0.1)
        viscosidade_din = FLUIDOS[fluido_sel]["visc"]

    st.write("---")
    st.markdown("**⚡ Propulsão & Eficiência**")
    tipo_motor = st.radio("Tipo de Motorização:", ["Combustão (Gasolina/Diesel)", "Elétrico (EV)"])
    
    if tipo_motor == "Combustão (Gasolina/Diesel)":
        preco_comb = st.number_input("Preço Combustível (R$/L):", value=5.80, step=0.10)
        eficiencia_motor = st.slider("Eficiência Térmica (%)", 15, 45, 30) / 100.0
    else:
        preco_kwh = st.number_input("Preço da Energia (R$/kWh):", value=0.85, step=0.05)
        eficiencia_motor = st.slider("Eficiência Elétrica (%)", 75, 95, 90) / 100.0
        capacidade_bateria = st.number_input("Capacidade da Bateria (kWh):", value=60.0, step=5.0)

    st.write("---")
    comparar = st.toggle("🔀 Modo Comparativo de Objetos", value=False)

# DIVISÃO DA ÁREA PRINCIPAL
col_centro, col_direita = st.columns([2.2, 1], gap="medium")

# ==========================================
# COLUNA DIREITA: PARÂMETROS DO OBJETO
# ==========================================
with col_direita:
    st.markdown("### 📐 Geometria & Dinâmica")
    
    with st.container(border=True):
        st.markdown("**🔵 Objeto A (Referência)**")
        preset_a = st.selectbox("Preset do Veículo:", list(presets_atuais.keys()), index=0)
        p_a = presets_atuais[preset_a]
        
        cd_a = st.slider("C_d (Arrasto):", 0.01, 1.5, p_a["cd"], 0.01, key="cd_a")
        area_a = st.slider("Área Frontal A (m²):", 0.1, 25.0, p_a["area"], 0.1, key="area_a")
        massa_a = st.number_input("Massa do Veículo (kg):", value=float(p_a["massa"]), step=50.0, key="m_a")
        potencia_cv_a = st.number_input("Potência do Motor (CV):", value=float(p_a["potencia_cv"]), step=10.0, key="p_a")
        comprimento_a = st.number_input("Comprimento do Corpo (m):", value=float(p_a["comprimento"]), step=0.5, key="comp_a")
        
        # Módulo Asa / Downforce opcional
        usar_aerofolio = st.checkbox("➕ Adicionar Aerofólio / Asas")
        if usar_aerofolio:
            cl_a = st.slider("C_L (Coeficiente de Sustentação/Downforce):", 0.0, 2.5, 0.8, 0.1)
            area_asa = st.slider("Área da Asa (m²):", 0.1, 3.0, 0.5, 0.1)
        else:
            cl_a = 0.0
            area_asa = 0.0

    if comparar:
        with st.container(border=True):
            st.markdown("**🔴 Objeto B (Comparativo)**")
            preset_b = st.selectbox("Preset do Veículo:", list(presets_atuais.keys()), index=min(1, len(presets_atuais)-1))
            p_b = presets_atuais[preset_b]
            
            cd_b = st.slider("C_d (Arrasto):", 0.01, 1.5, p_b["cd"], 0.01, key="cd_b")
            area_b = st.slider("Área Frontal B (m²):", 0.1, 25.0, p_b["area"], 0.1, key="area_b")
            massa_b = st.number_input("Massa do Veículo (kg):", value=float(p_b["massa"]), step=50.0, key="m_b")
            potencia_cv_b = st.number_input("Potência do Motor (CV):", value=float(p_b["potencia_cv"]), step=10.0, key="p_b")
            comprimento_b = st.number_input("Comprimento do Corpo (m):", value=float(p_b["comprimento"]), step=0.5, key="comp_b")

# ==========================================
# CÁLCULOS FÍSICOS PRINCIPAIS
# ==========================================
# Velocidade e Vento
v_kmh = st.sidebar.slider("Velocidade do Corpo (km/h)", 0.0, 250.0, 110.0, 1.0)
v_vento_kmh = st.sidebar.slider("Vento / Correnteza (-Favor / +Contra km/h)", -50.0, 50.0, 0.0, 1.0)

v_efetiva_kmh = max(0.0, v_kmh + v_vento_kmh)
v_efetiva_ms = v_efetiva_kmh / 3.6
v_propria_ms = v_kmh / 3.6

# Objeto A
fd_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a
f_rol_a = p_a["crr"] * massa_a * 9.81
f_total_a = fd_a + f_rol_a

pot_watts_a = f_total_a * v_propria_ms
pot_cv_a = pot_watts_a / 735.5

# Downforce
downforce_a = 0.5 * rho * (v_efetiva_ms ** 2) * cl_a * area_asa

# Número de Reynolds (Re = (ρ * v * L) / μ)
reynolds_a = (rho * v_efetiva_ms * comprimento_a) / viscosidade_din if viscosidade_din > 0 else 0

# Consumo & Custos
if tipo_motor == "Combustão (Gasolina/Diesel)":
    # 32 MJ por Litro de Gasolina
    consumo_l_h_a = (pot_watts_a / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
    consumo_100km_a = (consumo_l_h_a / v_kmh) * 100 if v_kmh > 0 else 0
    custo_100km_a = consumo_100km_a * preco_comb
    autonomia_a = 0
else:
    # Elétrico (kWh/100km)
    consumo_kwh_h_a = (pot_watts_a / eficiencia_motor) / 1000.0 if v_kmh > 0 else 0
    consumo_100km_a = (consumo_kwh_h_a / v_kmh) * 100 if v_kmh > 0 else 0
    custo_100km_a = consumo_100km_a * preco_kwh
    autonomia_a = (capacidade_bateria / consumo_100km_a) * 100 if consumo_100km_a > 0 else 0

# Objeto B (Se comparativo)
if comparar:
    fd_b = 0.5 * rho * (v_efetiva_ms ** 2) * cd_b * area_b
    f_rol_b = p_b["crr"] * massa_b * 9.81
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
    
    # METRICAS DE CABEÇALHO
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
    
    # ABAS PRINCIPAIS INCLUINDO DESENHO INTERATIVO
    tab_desenho, tab_grafico, tab_física, tab_ranking = st.tabs([
        "🎨 Perfil & Desenho 2D", 
        "📊 Curvas & Desempenho", 
        "🔬 Análise Física Avançada", 
        "🏆 Comparador de Frota"
    ])

    # ----------------------------------------------------
    # TAB 0: DESENHO DINÂMICO 2D & VETORES DE FORÇA
    # ----------------------------------------------------
    with tab_desenho:
        st.markdown("#### 🎨 Perfil Aerodinâmico & Vetores de Força em Tempo Real")
        st.caption("O perfil visual do veículo, o escoamento do ar e os vetores de força mudam dinamicamente conforme os parâmetros.")
        
        # Função para gerar desenho dinâmico baseado em parâmetros geométricos e Cd
        def criar_desenho_aerodinamico(cd, area, comp, downforce, fd, v_kmh):
            fig_draw = go.Figure()
            
            # Cálculo proporcional de altura/largura visual
            altura_vis = np.sqrt(area)
            comp_vis = max(comp, 1.2)
            
            # Gerar perfil de corpo (Gota fluida para Cd baixo, bloco para Cd alto)
            x_body = np.linspace(0, comp_vis, 100)
            
            # Coeficiente de forma aerodinâmica
            sharpness = max(0.1, 1.2 - cd * 0.8)
            y_upper = (altura_vis / 2) * (np.sin(np.pi * (x_body / comp_vis) ** sharpness))
            y_lower = -y_upper
            
            # Desenhar corpo principal do veículo
            fig_draw.add_trace(go.Scatter(
                x=np.concatenate([x_body, x_body[::-1]]),
                y=np.concatenate([y_upper, y_lower[::-1]]),
                fill='toself',
                fillcolor='rgba(0, 210, 255, 0.25)',
                line=dict(color='#00D2FF', width=3),
                name='Geometria do Veículo'
            ))

            # Desenhar Linhas de Fluxo (Streamlines)
            for offset in np.linspace(-altura_vis * 1.5, altura_vis * 1.5, 7):
                if abs(offset) < 0.1:
                    continue
                
                # Desvio da linha de vento em volta do corpo
                x_stream = np.linspace(-comp_vis * 0.8, comp_vis * 1.8, 80)
                deflection = np.exp(-((x_stream - comp_vis*0.3)**2) / (comp_vis*0.8)**2) * (offset * (1 + cd*0.5))
                y_stream = offset + deflection * (1 if offset > 0 else -1) * 0.3
                
                # Turbulência na esteira traseira (Wake region) maior para Cd alto
                wake_mask = x_stream > comp_vis
                if cd > 0.3:
                    y_stream[wake_mask] += np.sin(x_stream[wake_mask] * 12) * (cd * 0.12 * abs(offset))

                fig_draw.add_trace(go.Scatter(
                    x=x_stream, y=y_stream,
                    mode='lines',
                    line=dict(color='rgba(255, 255, 255, 0.35)', width=1.5, dash='dash' if cd > 0.4 else 'solid'),
                    showlegend=False
                ))

            # VETORES DE FORÇA
            scale_f = max(fd, 1.0)
            
            # Vetor de Arrasto Fd (Seta para trás)
            fig_draw.add_annotation(
                x=comp_vis * 1.25, y=0,
                ax=0, ay=0,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=4, arrowcolor="#FF2A6D",
                text=f"<b>Fd = {fd:.0f} N</b>",
                font=dict(color="#FF2A6D", size=13)
            )
            
            # Vetor de Sustentação / Downforce FL (Seta para baixo se hover wing)
            if downforce > 0:
                fig_draw.add_annotation(
                    x=comp_vis * 0.7, y=-altura_vis * 0.8,
                    ax=comp_vis * 0.7, ay=0,
                    xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3, arrowcolor="#FFD700",
                    text=f"<b>Downforce = {downforce:.0f} N</b>",
                    font=dict(color="#FFD700", size=12)
                )

            fig_draw.update_layout(
                xaxis=dict(range=[-comp_vis, comp_vis * 2.2], title="Comprimento (m)", showgrid=False),
                yaxis=dict(range=[-altura_vis * 2.2, altura_vis * 2.2], title="Altura Relativa (m)", showgrid=False),
                template="plotly_dark",
                height=430,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            return fig_draw

        st.plotly_chart(
            criar_desenho_aerodinamico(cd_a, area_a, comprimento_a, downforce_a, fd_a, v_kmh),
            use_container_width=True
        )

    # ----------------------------------------------------
    # TAB 1: GRÁFICOS INTERATIVOS DE DESEMPENHO
    # ----------------------------------------------------
    with tab_grafico:
        opcao_grafico = st.radio("Selecione o Eixo Y:", ["Força de Arrasto (N)", "Potência Necessária (CV)", "Custo Financeiro (R$/100km)"], horizontal=True)
        
        v_vec = np.linspace(1, 250, 120)
        v_vec_ef = np.maximum(0.1, v_vec + v_vento_kmh) / 3.6
        v_vec_ms = v_vec / 3.6
        
        # Vetorização Objeto A
        fd_vec_a = 0.5 * rho * (v_vec_ef ** 2) * cd_a * area_a
        f_tot_vec_a = fd_vec_a + f_rol_a
        pot_vec_cv_a = (f_tot_vec_a * v_vec_ms) / 735.5
        
        if tipo_motor == "Combustão (Gasolina/Diesel)":
            cons_vec_a = (((f_tot_vec_a * v_vec_ms) / eficiencia_motor) / (32e6 / 3600) / v_vec) * 100 * preco_comb
        else:
            cons_vec_a = (((f_tot_vec_a * v_vec_ms) / eficiencia_motor) / 1000.0 / v_vec) * 100 * preco_kwh

        if opcao_grafico == "Força de Arrasto (N)":
            y_a = fd_vec_a; y_p_a = fd_a; title_y = "Força de Arrasto (N)"
        elif opcao_grafico == "Potência Necessária (CV)":
            y_a = pot_vec_cv_a; y_p_a = pot_cv_a; title_y = "Potência Requerida (CV)"
        else:
            y_a = cons_vec_a; y_p_a = custo_100km_a; title_y = "Custo R$ / 100km"

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=v_vec, y=y_a, mode='lines', name='Objeto A', line=dict(color='#00D2FF', width=3)))
        fig.add_trace(go.Scatter(x=[v_kmh], y=[y_p_a], mode='markers', name='Ponto Atual A', marker=dict(color='#00D2FF', size=10)))

        # Cruzamento de Potência Máxima do Motor
        if opcao_grafico == "Potência Necessária (CV)":
            fig.add_hline(y=potencia_cv_a, line_dash="dash", line_color="#FFD700", annotation_text=f"Potência Máx Motor ({potencia_cv_a:.0f} CV)")

        if comparar:
            fd_vec_b = 0.5 * rho * (v_vec_ef ** 2) * cd_b * area_b
            f_tot_vec_b = fd_vec_b + f_rol_b
            pot_vec_cv_b = (f_tot_vec_b * v_vec_ms) / 735.5
            
            if tipo_motor == "Combustão (Gasolina/Diesel)":
                cons_vec_b = (((f_tot_vec_b * v_vec_ms) / eficiencia_motor) / (32e6 / 3600) / v_vec) * 100 * preco_comb
            else:
                cons_vec_b = (((f_tot_vec_b * v_vec_ms) / eficiencia_motor) / 1000.0 / v_vec) * 100 * preco_kwh

            y_b = fd_vec_b if opcao_grafico == "Força de Arrasto (N)" else (pot_vec_cv_b if opcao_grafico == "Potência Necessária (CV)" else cons_vec_b)
            y_p_b = fd_b if opcao_grafico == "Força de Arrasto (N)" else (pot_cv_b if opcao_grafico == "Potência Necessária (CV)" else custo_100km_b)
            
            fig.add_trace(go.Scatter(x=v_vec, y=y_b, mode='lines', name='Objeto B', line=dict(color='#FF2A6D', width=3)))
            fig.add_trace(go.Scatter(x=[v_kmh], y=[y_p_b], mode='markers', name='Ponto Atual B', marker=dict(color='#FF2A6D', size=10)))

        fig.update_layout(xaxis_title="Velocidade (km/h)", yaxis_title=title_y, template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: ANÁLISE FÍSICA AVANÇADA (REYNOLDS & DOWNFORCE)
    # ----------------------------------------------------
    with tab_física:
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            st.markdown("#### 🌀 Número de Reynolds ($Re$)")
            st.write(f"**$Re$ Calculado:** `{reynolds_a:.2e}`")
            
            if reynolds_a < 2e3:
                st.success("Regime do Escoamento: **Laminar** (Fluidos calmos e organizados)")
            elif 2e3 <= reynolds_a <= 4e3:
                st.warning("Regime do Escoamento: **De Transição**")
            else:
                st.error("Regime do Escoamento: **Turbulento** (Vórtices e turbulência dominam)")

            st.markdown("#### 🏎️ Carga Aerodinâmica (*Downforce*)")
            st.write(f"**Peso Extra Gerado nas Rodas:** `{downforce_a:.1f} N` (~`{downforce_a/9.81:.1f} kg`)")

        with col_f2:
            st.markdown("#### ⚖️ Divisão das Forças de Resistência")
            pct_arrasto = (fd_a / f_total_a) * 100 if f_total_a > 0 else 0
            pct_rolamento = (f_rol_a / f_total_a) * 100 if f_total_a > 0 else 0
            
            fig_pie = px.pie(
                values=[pct_arrasto, pct_rolamento],
                names=['Arrasto do Ar (Fd)', 'Atrito dos Pneus (F_rol)'],
                color_discrete_sequence=['#00D2FF', '#FF2A6D'],
                height=250
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # ----------------------------------------------------
    # TAB 3: RANKING COMPARATIVO DE FROTA
    # ----------------------------------------------------
    with tab_ranking:
        st.markdown("#### 🏆 Comparação da Força de Arrasto a 120 km/h")
