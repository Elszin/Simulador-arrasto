import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA & THEMA SPACE
# ==========================================
st.set_page_config(
    page_title="Rocket Dynamics & Max Q Simulator | Aerospace Engineering",
    page_icon="🚀",
    layout="wide"
)

# Estilização CSS Avançada (UI Dark/Space High-Tech)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Título Futurista */
    .rocket-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 50%, #00C6FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .rocket-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-bottom: 20px;
    }

    /* Cards Personalizados */
    .metric-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(8px);
    }
    
    .maxq-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(185, 28, 28, 0.05) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 16px;
    }

    /* Sidebar Fixa e Estilizada */
    div[data-testid="stSidebar"] {
        background-color: #07090E;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MODELO DA ATMOSFERA PADRÃO (ISA) & AERODINÂMICA
# ==========================================

def get_isa_atmosphere(altitude_m):
    """
    Modelo Estendido da Atmosfera Padrão Internacional (ISA)
    Retorna: Temperatura (K), Pressão (Pa), Densidade (kg/m³), Velocidade do Som (m/s)
    """
    h = np.clip(altitude_m, 0, 100000) # Até 100 km (Linha de Kármán)
    
    # Constantes físicas
    R = 287.058 # Constante dos gases para o ar J/(kg·K)
    g = 9.80665 # Gravidade m/s²
    gamma = 1.4 # Razão de calores específicos
    
    # Camadas atmosféricas (Altitude, Gradiente T, T_base, P_base)
    if h <= 11000: # Troposfera
        T = 288.15 - 0.0065 * h
        P = 101325 * (T / 288.15) ** (5.25588)
    elif h <= 20000: # Tropopausa
        T = 216.65
        P = 22632.1 * np.exp(-g * (h - 11000) / (R * T))
    elif h <= 32000: # Estratosfera Inferior
        T = 216.65 + 0.0010 * (h - 20000)
        P = 5474.89 * (T / 216.65) ** (-34.1632)
    elif h <= 47000: # Estratosfera Superior
        T = 228.65 + 0.0028 * (h - 32000)
        P = 868.02 * (T / 228.65) ** (-12.2011)
    elif h <= 51000: # Estratopausa
        T = 270.65
        P = 110.91 * np.exp(-g * (h - 47000) / (R * T))
    else: # Mesosfera
        T = max(180.0, 270.65 - 0.0028 * (h - 51000))
        P = max(0.001, 66.94 * (T / 270.65) ** (12.2011))
        
    rho = P / (R * T)
    speed_of_sound = np.sqrt(gamma * R * T)
    
    return T, P, rho, speed_of_sound

def get_mach_corrected_cd(cd_base, mach):
    """
    Calcula a variação do Cd com a Singularidade Prandtl-Glauert / Barreira do Som.
    O Cd dispara na região Transônica (Mach 0.8 a 1.2) e decai suavemente no Hipersônico.
    """
    if mach < 0.8:
        # Subsônico
        return cd_base * (1.0 + 0.1 * (mach ** 2))
    elif 0.8 <= mach <= 1.2:
        # Transônico (Onda de choque / Peak Drag)
        transonic_factor = 1.0 + 1.8 * np.sin(np.pi * (mach - 0.8) / 0.4)
        return cd_base * transonic_factor
    elif 1.2 < mach <= 5.0:
        # Supersônico
        return cd_base * (1.8 / (mach ** 0.4))
    else:
        # Hipersônico (Mach > 5)
        return cd_base * 0.95

# ==========================================
# 3. BANCO DE DADOS DE FOGUETES & PRESETS
# ==========================================
ROCKET_PRESETS = {
    "Falcon 9 (SpaceX)": {
        "cd_base": 0.28,
        "diameter": 3.7, # metros
        "stage1_thrust_kn": 7607,
        "mass_tons": 549,
        "max_speed_kmh": 8000,
        "desc": "Vetor de lançamento médio reutilizável orbital."
    },
    "Saturn V (Apollo Program)": {
        "cd_base": 0.35,
        "diameter": 10.1,
        "stage1_thrust_kn": 35100,
        "mass_tons": 2970,
        "max_speed_kmh": 9800,
        "desc": "O mais poderoso super heavy-lift rocket operado pela NASA."
    },
    "Electron (Rocket Lab)": {
        "cd_base": 0.25,
        "diameter": 1.2,
        "stage1_thrust_kn": 224,
        "mass_tons": 13,
        "max_speed_kmh": 7200,
        "desc": "Foguete ultraleve dedicado a microssatélites."
    },
    "Minifoguete Universitário / Experimental": {
        "cd_base": 0.45,
        "diameter": 0.15,
        "stage1_thrust_kn": 8.5,
        "mass_tons": 0.045,
        "max_speed_kmh": 1800,
        "desc": "Projetos de alta altitude acadêmicos (Competições de Foguetes)."
    },
    "Customizado": {
        "cd_base": 0.30,
        "diameter": 2.0,
        "stage1_thrust_kn": 1000,
        "mass_tons": 50,
        "max_speed_kmh": 6000,
        "desc": "Parâmetros configuráveis manualmente."
    }
}

# ==========================================
# 4. SIDEBAR - CONTROLES & CONFIGURAÇÕES
# ==========================================
with st.sidebar:
    st.markdown("## 🚀 Missão & Veículo")
    st.write("---")
    
    preset_selected = st.selectbox("Selecione o Veículo de Lançamento:", list(ROCKET_PRESETS.keys()), index=0)
    preset_data = ROCKET_PRESETS[preset_selected]
    
    st.caption(f"ℹ️ {preset_data['desc']}")
    st.write("---")
    
    st.markdown("### 🛠️ Geometria & Aerodinâmica")
    cd_input = st.slider("C_d Base (Zero Mach):", 0.10, 0.80, float(preset_data["cd_base"]), 0.01)
    diametro_input = st.slider("Diâmetro do Veículo (m):", 0.10, 12.00, float(preset_data["diameter"]), 0.05)
    
    # Área Frontal Projetada A = π * (d/2)²
    area_projetada = np.pi * ((diametro_input / 2.0) ** 2)
    st.caption(f"📐 Área Frontal ($A$): **{area_projetada:.2f} m²**")
    
    st.write("---")
    st.markdown("### 📈 Perfil da Trajetória")
    max_alt_km = st.slider("Teto da Simulação (km):", 10, 100, 80, 5)
    v_max_sim = st.slider("Velocidade Máxima do Estágio 1 (km/h):", 1000, 12000, int(preset_data["max_speed_kmh"]), 200)

    st.write("---")
    comparar_segundo_foguete = st.toggle("🔀 Modo Comparativo de Veículos", value=False)

# ==========================================
# 5. MOTOR DE SIMULAÇÃO ATMOSFÉRICA & VOO
# ==========================================

def run_rocket_simulation(cd_base, area, v_max_kmh, max_altitude_km):
    altitudes_m = np.linspace(0, max_altitude_km * 1000, 500)
    
    # Curva de velocidade simplificada de subida orbital (Aceleração típica de lançamento)
    # A velocidade cresce exponencialmente/parabolicamente com a altitude
    v_ms_vetor = (v_max_kmh / 3.6) * (altitudes_m / (max_altitude_km * 1000)) ** 0.65
    
    rhos = []
    pressures = []
    temps = []
    machs = []
    cds_mach = []
    drag_forces_n = []
    dynamic_pressures_pa = [] # Pressão Dinâmica q = 0.5 * rho * v²
    
    for h, v_ms in zip(altitudes_m, v_ms_vetor):
        T, P, rho, a = get_isa_atmosphere(h)
        mach = v_ms / a if a > 0 else 0
        cd_corr = get_mach_corrected_cd(cd_base, mach)
        
        q = 0.5 * rho * (v_ms ** 2) # Pressão dinâmica
        fd = q * cd_corr * area    # Força de arrasto
        
        rhos.append(rho)
        pressures.append(P)
        temps.append(T)
        machs.append(mach)
        cds_mach.append(cd_corr)
        drag_forces_n.append(fd)
        dynamic_pressures_pa.append(q)
        
    df = pd.DataFrame({
        "Altitude_km": altitudes_m / 1000,
        "Altitude_m": altitudes_m,
        "Velocidade_kmh": v_ms_vetor * 3.6,
        "Velocidade_ms": v_ms_vetor,
        "Densidade_rho": rhos,
        "Pressao_Pa": pressures,
        "Temperatura_K": temps,
        "Mach": machs,
        "Cd_Efetivo": cds_mach,
        "Forca_Arrasto_N": drag_forces_n,
        "Forca_Arrasto_kN": np.array(drag_forces_n) / 1000,
        "Pressao_Dinamica_kPa": np.array(dynamic_pressures_pa) / 1000
    })
    
    # Localização do MAX Q (Pressão Dinâmica Máxima)
    idx_max_q = df["Pressao_Dinamica_kPa"].idxmax()
    row_max_q = df.iloc[idx_max_q]
    
    # Integração Numérica do Trabalho do Arrasto (Energia Perdida em Gigajoules)
    # W = ∫ F_d dh
    trabalho_joules = np.trapz(df["Forca_Arrasto_N"], df["Altitude_m"])
    trabalho_gj = trabalho_joules / 1e9
    
    return df, row_max_q, trabalho_gj

# Executar Simulação Principal
df_sim, max_q, energia_perdida_gj = run_rocket_simulation(cd_input, area_projetada, v_max_sim, max_alt_km)

# ==========================================
# 6. DASHBOARD PRINCIPAL DE RESULTADOS
# ==========================================

st.markdown('<p class="rocket-title">🚀 ROCKET AERODYNAMICS & MAX Q DASHBOARD</p>', unsafe_allow_html=True)
st.markdown('<p class="rocket-subtitle">Análise Espacial de Trajetória Atmosférica, Barreira de Som e Pressão Estrutural Dinâmica</p>', unsafe_allow_html=True)

# METRIC CARDS SUPERIORES
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.markdown(f"""
    <div class="maxq-card">
        <small style="color:#EF4444; font-weight:700;">🔥 PONTO CRÍTICO MAX Q</small>
        <h2 style="margin:4px 0; color:#FFFFFF;">{max_q['Pressao_Dinamica_kPa']:.1f} kPa</h2>
        <small style="color:#CBD5E1;">Altitude: <b>{max_q['Altitude_km']:.2f} km</b></small>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card">
        <small style="color:#38BDF8; font-weight:700;">⚡ ARRASTO MÁXIMO (F_d Peak)</small>
        <h2 style="margin:4px 0; color:#FFFFFF;">{max_q['Forca_Arrasto_kN']:.1f} kN</h2>
        <small style="color:#CBD5E1;">Velocidade: <b>{max_q['Velocidade_kmh']:.0f} km/h</b></small>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card">
        <small style="color:#34D399; font-weight:700;">🌐 VELOCIDADE EM MACH (No Max Q)</small>
        <h2 style="margin:4px 0; color:#FFFFFF;">Mach {max_q['Mach']:.2f}</h2>
        <small style="color:#CBD5E1;">Cd Transônico: <b>{max_q['Cd_Efetivo']:.3f}</b></small>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    st.markdown(f"""
    <div class="metric-card">
        <small style="color:#FBBF24; font-weight:700;">🔋 PERDA DE ENERGIA ATMOSFÉRICA</small>
        <h2 style="margin:4px 0; color:#FFFFFF;">{energia_perdida_gj:.2f} GJ</h2>
        <small style="color:#CBD5E1;">Trabalho do Arrasto (0-{max_alt_km}km)</small>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# ==========================================
# 7. GRÁFICOS INTERATIVOS PLOTLY (3 SEÇÕES)
# ==========================================

tab1, tab2, tab3 = st.tabs(["📊 Análise de Arrasto & Max Q", "🌡️ Perfil Atmosférico ISA", "🔀 Onda de Choque Transônica (Mach vs Cd)"])

# ------------------------------------------
# TAB 1: ARRASTO & PRESSÃO DINÂMICA
# ------------------------------------------
with tab1:
    fig_flight = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Evolução da Força de Arrasto (kN) vs Altitude", "Pressão Dinâmica q (kPa) e Região de Max Q"),
        horizontal_spacing=0.1
    )
    
    # Gráfico 1: Força de Arrasto
    fig_flight.add_trace(
        go.Scatter(
            x=df_sim["Altitude_km"], y=df_sim["Forca_Arrasto_kN"],
            mode='lines', name='Força de Arrasto (kN)',
            line=dict(color='#00F2FE', width=3),
            fill='tozeroy', fillcolor='rgba(0, 242, 254, 0.08)'
        ),
        row=1, col=1
    )
    # Marcar Max Q no Gráfico 1
    fig_flight.add_trace(
        go.Scatter(
            x=[max_q["Altitude_km"]], y=[max_q["Forca_Arrasto_kN"]],
            mode='markers+text', name='Ponto Estresse Máximo',
            marker=dict(color='#EF4444', size=12, symbol='diamond'),
            text=[f" Max Q ({max_q['Forca_Arrasto_kN']:.0f} kN)"],
            textposition="top right"
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Pressão Dinâmica q
    fig_flight.add_trace(
        go.Scatter(
            x=df_sim["Altitude_km"], y=df_sim["Pressao_Dinamica_kPa"],
            mode='lines', name='Pressão Dinâmica q (kPa)',
            line=dict(color='#FF2A6D', width=3),
            fill='tozeroy', fillcolor='rgba(255, 42, 109, 0.08)'
        ),
        row=1, col=2
    )
    
    fig_flight.update_layout(
        template="plotly_dark",
        height=480,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)'
    )
    
    fig_flight.update_xaxes(title_text="Altitude (km)", gridcolor='rgba(255,255,255,0.1)')
    fig_flight.update_yaxes(title_text="Força (kN)", gridcolor='rgba(255,255,255,0.1)', row=1, col=1)
    fig_flight.update_yaxes(title_text="Pressão Dinâmica (kPa)", gridcolor='rgba(255,255,255,0.1)', row=1, col=2)
    
    st.plotly_chart(fig_flight, use_container_width=True)

# ------------------------------------------
# TAB 2: ATMOSFERA E DENSIDADE
# ------------------------------------------
with tab2:
    fig_atmo = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Queda Exponencial da Densidade do Ar ρ (kg/m³)", "Gradiente de Temperatura Atmosférica (K)"),
        horizontal_spacing=0.1
    )
    
    fig_atmo.add_trace(
        go.Scatter(
            x=df_sim["Altitude_km"], y=df_sim["Densidade_rho"],
            mode='lines', name='Densidade ρ',
            line=dict(color='#38BDF8', width=3)
        ),
        row=1, col=1
    )
    
    fig_atmo.add_trace(
        go.Scatter(
            x=df_sim["Altitude_km"], y=df_sim["Temperatura_K"],
            mode='lines', name='Temperatura (K)',
            line=dict(color='#FBBF24', width=3)
        ),
        row=1, col=2
    )
    
    fig_atmo.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)'
    )
    
    fig_atmo.update_xaxes(title_text="Altitude (km)", gridcolor='rgba(255,255,255,0.1)')
    fig_atmo.update_yaxes(title_text="Densidade ρ (kg/m³)", type="log", gridcolor='rgba(255,255,255,0.1)', row=1, col=1)
    fig_atmo.update_yaxes(title_text="Temperatura (K)", gridcolor='rgba(255,255,255,0.1)', row=1, col=2)
    
    st.plotly_chart(fig_atmo, use_container_width=True)

# ------------------------------------------
# TAB 3: BARREIRA DO SOM & MACH
# ------------------------------------------
with tab3:
    fig_mach = go.Figure()
    
    fig_mach.add_trace(go.Scatter(
        x=df_sim["Mach"], y=df_sim["Cd_Efetivo"],
        mode='lines+markers', name='C_d Corrigido por Mach',
        line=dict(color='#A855F7', width=3),
        hovertemplate='<b>Mach: %{x:.2f}</b><br>Cd: %{y:.3f}<extra></extra>'
    ))
    
    # Destacar zona transônica
    fig_mach.add_vrect(
        x0=0.8, x1=1.2, fillcolor="rgba(239, 68, 68, 0.2)",
        annotation_text="Zona Transônica (Picada de Cd por Onda de Choque)", annotation_position="top left"
    )
    
    fig_mach.update_layout(
        title="Variação Aerodinâmica do Coeficiente de Arrasto (C_d) com o Número de Mach",
        xaxis_title="Número de Mach (v / velocidade do som)",
        yaxis_title="Coeficiente de Arrasto Efetivo (C_d)",
        template="plotly_dark",
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)'
    )
    
    st.plotly_chart(fig_mach, use_container_width=True)

# ==========================================
# 8. EXPORTAÇÃO TELEMÉTRICA PARA CSV
# ==========================================
with st.sidebar:
    st.markdown("### 💾 Telemetria de Voo")
    csv_rocket = df_sim.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Telemétricos (CSV)",
        data=csv_rocket,
        file_name=f"telemetria_{preset_selected.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )
