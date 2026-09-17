import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="Simulador MONSTRO de Arrasto & Potência Aerodinâmica",
    page_icon="🚀",
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
        font-size: 2.3rem;
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
    
    .highlight-box {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Dicionários e Constantes Físicas
FLUIDOS = {
    "Ar Atmosférico (Variável com Altitude)": 1.225,
    "Água Doce (20°C)": 998.2,
    "Água do Mar (15°C)": 1025.0,
    "Customizado": 1.225
}

PRESETS_AR = {
    "Customizado": {"cd": 0.30, "area": 2.2},
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0},
    "Ciclista em Pé (Gravel/Urbano)": {"cd": 0.90, "area": 0.6},
    "Paraquedista (Aberto)": {"cd": 1.20, "area": 1.5}
}

PRESETS_AGUA = {
    "Customizado": {"cd": 0.10, "area": 1.0},
    "Submarino / Torpedo": {"cd": 0.04, "area": 1.5},
    "Casco de Lancha / Barco": {"cd": 0.25, "area": 2.5},
    "Nadador / Mergulhador": {"cd": 0.70, "area": 0.5},
    "Esfera Perfeita debaixo d'água": {"cd": 0.47, "area": 1.0}
}

CIDADES_ALTITUDE = {
    "Personalizado": None,
    "Nível do Mar (0 m)": 0,
    "São Paulo / Curitiba (~800 m)": 800,
    "Cidade do México (~2240 m)": 2240,
    "La Paz - Bolívia (~3640 m)": 3640
}

# ==========================================
# COLUNA 1 (ESQUERDA): BARRA LATERAL
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configurações Gerais")
    st.write("---")
    
    st.markdown("**🌊 Meio Fluido & Ambiente**")
    fluido_selecionado = st.selectbox("Selecione o Fluido:", list(FLUIDOS.keys()), index=0)
    
    is_ar = "Ar" in fluido_selecionado
    is_agua = "Água" in fluido_selecionado

    if is_ar:
        st.markdown("**🏔️ Simulador de Altitude**")
        cidade_preset = st.selectbox("Presets de Altitude:", list(CIDADES_ALTITUDE.keys()), index=1)
        val_altitude = CIDADES_ALTITUDE[cidade_preset] if CIDADES_ALTITUDE[cidade_preset] is not None else 0
        altitude = st.slider("Altitude em relação ao nível do mar (m)", 0, 5000, val_altitude, 100)
        
        # Fórmula Barométrica
        rho_calculado = 1.225 * np.exp(-altitude / 8500)
        st.caption(f"💡 Densidade do ar: **{rho_calculado:.3f} kg/m³**")
        rho_padrao = rho_calculado
    else:
        rho_padrao = FLUIDOS[fluido_selecionado]

    rho = st.slider("Densidade do meio ρ (kg/m³)", 0.1, 1100.0, float(rho_padrao), 0.1)
    
    st.write("---")
    st.markdown("**🚗 Dinâmica de Movimento**")
    v_kmh = st.slider("Velocidade do Corpo (km/h)", 0.0, 250.0, 110.0, 1.0)
    v_vento_kmh = st.slider("Vento / Correnteza (-Favor / +Contra km/h)", -50.0, 50.0, 0.0, 1.0)
    
    v_efetiva_kmh = max(0.0, v_kmh + v_vento_kmh)
    v_efetiva_ms = v_efetiva_kmh / 3.6

    st.write("---")
    st.markdown("**⛽ Parâmetros de Consumo (Estimativa)**")
    preco_combustivel = st.number_input("Preço da Gasolina/Diesel (R$/L):", value=5.80, step=0.10)
    eficiencia_motor = st.slider("Eficiência Térmica do Motor (%)", 15, 45, 30) / 100.0

    st.write("---")
    comparar = st.toggle("🔀 Ativar Modo Comparativo", value=False)
    st.write("---")

presets_ativos = PRESETS_AGUA if is_agua else PRESETS_AR

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
        preset_a = st.selectbox("Preset:", list(presets_ativos.keys()), index=0 if is_agua else 1, key=f"select_preset_a_{is_agua}")
        
        cd_a = st.slider("Cd (Objeto A)", 0.01, 1.5, presets_ativos[preset_a]["cd"], 0.01, key=f"cd_a_{preset_a}_{is_agua}")
        area_a = st.slider("Área Frontal A (m²)", 0.1, 10.0, presets_ativos[preset_a]["area"], 0.1, key=f"area_a_{preset_a}_{is_agua}")

    # Cálculos Objeto A
    fd_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a
    potencia_watts_a = fd_a * (v_kmh / 3.6) # Potência mecânica requerida para a velocidade do veículo
    potencia_cv_a = potencia_watts_a / 735.5
    potencia_kw_a = potencia_watts_a / 1000.0
    
    # Estimativa de Consumo de Combustível por hora / por 100km (P_total / (eficiência * PCI_gasolina))
    # PCI Gasolina ~ 32 MJ/L = 8888 Wh/L
    consumo_l_h_a = (potencia_watts_a / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
    consumo_l_100km_a = (consumo_l_h_a / v_kmh) * 100 if v_kmh > 0 else 0
    custo_100km_a = consumo_l_100km_a * preco_combustivel

    # Objeto B
    if comparar:
        with st.container(border=True):
            st.markdown("**🔴 Objeto B (Comparativo)**")
            preset_b = st.selectbox("Preset:", list(presets_ativos.keys()), index=1 if is_agua else 3, key=f"select_preset_b_{is_agua}")
            
            cd_b = st.slider("Cd (Objeto B)", 0.01, 1.5, presets_ativos[preset_b]["cd"], 0.01, key=f"cd_b_{preset_b}_{is_agua}")
            area_b = st.slider("Área Frontal B (m²)", 0.1, 10.0, presets_ativos[preset_b]["area"], 0.1, key=f"area_b_{preset_b}_{is_agua}")

        fd_b = 0.5 * rho * (v_efetiva_ms ** 2) * cd_b * area_b
        potencia_watts_b = fd_b * (v_kmh / 3.6)
        potencia_cv_b = potencia_watts_b / 735.5
        potencia_kw_b = potencia_watts_b / 1000.0
        
        consumo_l_h_b = (potencia_watts_b / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
        consumo_l_100km_b = (consumo_l_h_b / v_kmh) * 100 if v_kmh > 0 else 0
        custo_100km_b = consumo_l_100km_b * preco_combustivel

    with st.expander("📖 Fórmulas & Física Aplicada", expanded=False):
        st.markdown("""
        <div class="variable-card"><b>Força de Arrasto:</b> Fd = ½ · ρ · v² · Cd · A</div>
        <div class="variable-card"><b>Potência Requerida:</b> P = Fd · v = ½ · ρ · v³ · Cd · A</div>
        <div class="variable-card"><b>Pressão Dinâmica:</b> q = ½ · ρ · v²</div>
        """, unsafe_allow_html=True)

# ==========================================
# COLUNA 2 (MEIO): GRÁFICO E RESULTADOS MONSTROS
# ==========================================
with col_centro:
    st.markdown('<p class="main-title">🚀 Simulador MONSTRO de Aerodinâmica</p>', unsafe_allow_html=True)
    st.latex(r"P_{arrasto} = F_d \cdot v = \frac{1}{2} \rho v^3 C_d A")
    
    # METRICAS DE IMPACTO
    if comparar:
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Força (Obj A vs B)", f"{fd_a:.1f} N", delta=f"{fd_b - fd_a:.1f} N B", delta_color="inverse")
        m_col2.metric("Potência Exigida", f"{potencia_cv_a:.1f} CV", delta=f"{potencia_cv_b - potencia_cv_a:.1f} CV B", delta_color="inverse")
        dif_custo = custo_100km_b - custo_100km_a
        m_col3.metric("Custo Arrasto / 100km", f"R$ {custo_100km_a:.2f}", delta=f"R$ {dif_custo:.2f} B", delta_color="inverse")
    else:
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Força de Arrasto (Fd)", f"{fd_a:.2f} N")
        m_col2.metric("Potência Exigida do Motor", f"{potencia_cv_a:.1f} CV", f"{potencia_kw_a:.1f} kW")
        m_col3.metric("Custo de Gasolina em Arrasto", f"R$ {custo_100km_a:.2f} /100km", f"{consumo_l_100km_a:.2f} L/100km")

    # Módulo Selector de Métrica do Gráfico
    st.write("")
    opcao_grafico = st.radio("📊 Selecione a métrica da curva:", ["Força de Arrasto (N)", "Potência Necessária (CV)"], horizontal=True)

    # Vetor de Dados
    v_vetor_kmh = np.linspace(0, 250, 120)
    v_vetor_efetiva_kmh = np.maximum(0.0, v_vetor_kmh + v_vento_kmh)
    v_vetor_efetiva_ms = v_vetor_efetiva_kmh / 3.6
    
    # Vetores Objeto A
    fd_vetor_a = 0.5 * rho * (v_vetor_efetiva_ms ** 2) * cd_a * area_a
    pot_vetor_watts_a = fd_vetor_a * (v_vetor_kmh / 3.6)
    pot_vetor_cv_a = pot_vetor_watts_a / 735.5

    # Escolha das variáveis de plot
    if opcao_grafico == "Força de Arrasto (N)":
        y_vetor_a = fd_vetor_a
        y_ponto_a = fd_a
        eixo_y_titulo = "Força de Arrasto (N)"
    else:
        y_vetor_a = pot_vetor_cv_a
        y_ponto_a = potencia_cv_a
        eixo_y_titulo = "Potência Necessária (CV)"

    fig = go.Figure()
    
    # Curva Objeto A
    fig.add_trace(go.Scatter(
        x=v_vetor_kmh, y=y_vetor_a, mode='lines', name='Objeto A',
        line=dict(color='#00D2FF', width=3.5),
        fill='tozeroy', fillcolor='rgba(0, 210, 255, 0.08)',
        hovertemplate='<b>Objeto A</b><br>v: %{x:.1f} km/h<br>Valor: %{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=[v_kmh], y=[y_ponto_a], mode='markers', name='Ponto A',
        marker=dict(color='#00D2FF', size=11, line=dict(color='#FFFFFF', width=2))
    ))
    fig.add_trace(go.Scatter(
        x=[0, v_kmh, v_kmh], y=[y_ponto_a, y_ponto_a, 0], mode='lines',
        line=dict(color='#00D2FF', width=1, dash='dash'), hoverinfo='skip'
    ))

    # Curva Objeto B
    if comparar:
        fd_vetor_b = 0.5 * rho * (v_vetor_efetiva_ms ** 2) * cd_b * area_b
        pot_vetor_watts_b = fd_vetor_b * (v_vetor_kmh / 3.6)
        pot_vetor_cv_b = pot_vetor_watts_b / 735.5

        if opcao_grafico == "Força de Arrasto (N)":
            y_vetor_b = fd_vetor_b
            y_ponto_b = fd_b
        else:
            y_vetor_b = pot_vetor_cv_b
            y_ponto_b = potencia_cv_b

        fig.add_trace(go.Scatter(
            x=v_vetor_kmh, y=y_vetor_b, mode='lines', name='Objeto B',
            line=dict(color='#FF2A6D', width=3.5),
            fill='tozeroy', fillcolor='rgba(255, 42, 109, 0.05)',
            hovertemplate='<b>Objeto B</b><br>v: %{x:.1f} km/h<br>Valor: %{y:.2f}<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=[v_kmh], y=[y_ponto_b], mode='markers', name='Ponto B',
            marker=dict(color='#FF2A6D', size=11, line=dict(color='#FFFFFF', width=2))
        ))
        fig.add_trace(go.Scatter(
            x=[0, v_kmh, v_kmh], y=[y_ponto_b, y_ponto_b, 0], mode='lines',
            line=dict(color='#FF2A6D', width=1, dash='dash'), hoverinfo='skip'
        ))

    fig.update_layout(
        xaxis_title="Velocidade do Veículo (km/h)",
        yaxis_title=eixo_y_titulo,
        template="plotly_white",
        height=450,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=comparar,
        legend=dict(x=0.02, y=0.98),
        yaxis=dict(gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False),
        xaxis=dict(gridcolor='#E5E5E5', showline=True, linewidth=1.5, linecolor='#444444', zeroline=False)
    )

    st.plotly_chart(fig, use_container_width=True)

# Exportador e Download
with st.sidebar:
    st.markdown("**📂 Exportação Completa**")
    data_dict = {
        "Fluido": [fluido_selecionado] * len(v_vetor_kmh),
        "Velocidade_kmh": v_vetor_kmh,
        "Forca_Obj_A_N": fd_vetor_a,
        "Potencia_Obj_A_CV": pot_vetor_cv_a
    }
    if comparar:
        data_dict["Forca_Obj_B_N"] = fd_vetor_b
        data_dict["Potencia_Obj_B_CV"] = pot_vetor_cv_b
        
    df_export = pd.DataFrame(data_dict)
    csv_data = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Baixar Simulação Completa (CSV)",
        data=csv_data,
        file_name="simulacao_monstro_arrasto.csv",
        mime="text/csv",
        use_container_width=True
    )
