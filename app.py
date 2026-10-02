import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Configuração da Página (DEVE SER SEMPRE A PRIMEIRA CHAMADA DO STREAMLIT)
st.set_page_config(
    page_title="Simulador de Força de Arrasto Linear",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS customizada
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">Simulador de Força de Arrasto (Velocidade Linear)</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Análise de resistência em regime linear proporcional ($F_d \\propto v$)</div>',
    unsafe_allow_html=True,
)

# --- PRESETS DE OBJETOS ---
PRESETS_AR = {
    "Carro Esportivo": {"k": 0.45, "desc": "Perfil aerodinâmico otimizado"},
    "Caminhão / Ônibus": {
        "k": 1.20,
        "desc": "Grande seção frontal e formato romptivo",
    },
}

PRESETS_AGUA = {
    "Lancha Rápida": {"k": 3.50, "desc": "Hidrodinâmica de superfície"},
    "Submarino": {"k": 0.80, "desc": "Corpo esguio de imersão"},
}

# --- BARRA LATERAL (AMPLITUDE E AMBIENTE) ---
st.sidebar.header("🌍 Parâmetros Ambientais")
fluido = st.sidebar.selectbox("Escolha o Meio (Fluido):", ["Ar", "Água"])

if fluido == "Ar":
    altitude = st.sidebar.slider(
        "Altitude (m):", 0, 10000, 0, 500, help="Afeta a densidade do ar."
    )
    temperatura = st.sidebar.slider("Temperatura do Ar (°C):", -20, 40, 20, 1)
    # Cálculo aproximado da densidade do ar
    pressao = 101325 * np.exp(-altitude / 8500)
    temp_k = temperatura + 273.15
    rho = pressao / (287.05 * temp_k)
    presets_atuais = PRESETS_AR
else:
    temperatura = st.sidebar.slider("Temperatura da Água (°C):", 0, 30, 20, 1)
    rho = 1000 - 0.02 * (
        temperatura - 4
    ) ** 2  # Variação térmica aproximada da água
    presets_atuais = PRESETS_AGUA

st.sidebar.markdown(f"**Densidade do Fluido ($\\rho$):** `{rho:.3f} kg/m³`")

# --- PAINEL PRINCIPAL DE PARÂMETROS ---
col_config1, col_config2 = st.columns(2)

with col_config1:
    st.subheader("🚗 Configuração do Objeto A")
    preset_a = st.selectbox(
        "Modelo Base (Objeto A):", list(presets_atuais.keys()), key="preset_a"
    )

    k_default = presets_atuais[preset_a]["k"]

    k_a = st.slider(
        "Coeficiente de Arrasto Linear ($k$):",
        0.01,
        10.0,
        float(k_default),
        0.05,
        help="Fator de proporcionalidade linear da força de resistência.",
    )

    vel_a = st.slider(
        "Velocidade do Objeto A (km/h):", 0.0, 200.0, 50.0, 1.0, key="vel_a"
    )

with col_config2:
    st.subheader("📊 Modo Comparativo (Objeto B)")
    comparar = st.checkbox("Ativar Comparação com Objeto B")

    if comparar:
        preset_b = st.selectbox(
            "Modelo Base (Objeto B):",
            list(presets_atuais.keys()),
            key="preset_b",
        )
        k_b_default = presets_atuais[preset_b]["k"] * 1.5
        k_b = st.slider(
            "Coeficiente Linear Objeto B ($k$):", 0.01, 10.0, float(k_b_default)
        )
        vel_b = st.slider(
            "Velocidade do Objeto B (km/h):", 0.0, 200.0, 50.0, 1.0, key="vel_b"
        )

# --- MOTOR DE CÁLCULO FÍSICO (VELOCIDADE LINEAR) ---
v_a_ms = vel_a / 3.6
f_d_a = k_a * rho * v_a_ms

# Exibição de Métricas
st.markdown("---")
col_met1, col_met2 = st.columns(2)
with col_met1:
    st.metric(
        label=f"Força de Arrasto (Objeto A - {preset_a})",
        value=f"{f_d_a:.2f} N",
    )

if comparar:
    v_b_ms = vel_b / 3.6
    f_d_b = k_b * rho * v_b_ms
    with col_met2:
        st.metric(
            label=f"Força de Arrasto (Objeto B - {preset_b})",
            value=f"{f_d_b:.2f} N",
        )

# --- GRÁFICO DINÂMICO (LINHA RETA / PROPORCIONALIDADE) ---
st.markdown("### 📈 Curva de Comportamento Linear da Força de Arrasto")

velocidades_range = np.linspace(0, 200, 100)
velocidades_ms = velocidades_range / 3.6
forcas_range_a = k_a * rho * velocidades_ms

fig = go.Figure()

# Curva do Objeto A
fig.add_trace(
    go.Scatter(
        x=velocidades_range,
        y=forcas_range_a,
        mode="lines",
        name=f"Objeto A ({preset_a})",
        line=dict(color="#2563EB", width=3),
    )
)

# Ponto atual do Objeto A
fig.add_trace(
    go.Scatter(
        x=[vel_a],
        y=[f_d_a],
        mode="markers",
        name=f"Operação Atual A ({vel_a} km/h)",
        marker=dict(color="#1E3A8A", size=12, symbol="circle"),
    )
)

if comparar:
    forcas_range_b = k_b * rho * velocidades_ms
    fig.add_trace(
        go.Scatter(
            x=velocidades_range,
            y=forcas_range_b,
            mode="lines",
            name=f"Objeto B ({preset_b})",
            line=dict(color="#DC2626", width=3, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[vel_b],
            y=[f_d_b],
            mode="markers",
            name=f"Operação Atual B ({vel_b} km/h)",
            marker=dict(color="#991B1B", size=12, symbol="diamond"),
        )
    )

fig.update_layout(
    title="Relação Linear entre Velocidade e Força de Resistência ($F_d = k \\cdot \\rho \\cdot v$)",
    xaxis_title="Velocidade (km/h)",
    yaxis_title="Força de Arrasto (N)",
    template="plotly_white",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)
