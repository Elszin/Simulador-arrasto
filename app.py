import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Simulador de Arrasto Viscoso (Lei de Stokes)",
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
    '<div class="main-title">Simulador de Arrasto Viscoso Linear (Lei de Stokes)</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Análise física baseada em dimensões reais e viscosidade do fluido ($F_d = 6 \\pi \\mu r v$)</div>',
    unsafe_allow_html=True,
)

# --- BARRA LATERAL (PARÂMETROS AMBIENTAIS E VISCOSIDADE) ---
st.sidebar.header("🌍 Parâmetros do Fluido")
fluido = st.sidebar.selectbox("Escolha o Meio:", ["Ar", "Água"])

if fluido == "Ar":
    temperatura = st.sidebar.slider("Temperatura do Ar (°C):", -20, 40, 20, 1)
    # Viscosidade dinâmica aproximada do ar em Pa·s (Pascal-segundo)
    mu = (
        1.71e-5 + 4.8e-8 * temperatura
    )  # Variação com a temperatura em escala laboratorial
    unidade_raio = "mm"
else:
    temperatura = st.sidebar.slider("Temperatura da Água (°C):", 0, 30, 20, 1)
    # Viscosidade dinâmica da água diminui com o aumento da temperatura (aproximação)
    mu = 1.002e-3 / (1.0 + 0.033 * (temperatura - 20))
    unidade_raio = "mm"

st.sidebar.markdown(f"**Viscosidade Dinâmica ($\mu$):** `{mu:.2e} Pa·s`")

# --- PAINEL PRINCIPAL DE PARÂMETROS REAIS ---
col_config1, col_config2 = st.columns(2)

with col_config1:
    st.subheader("🔵 Esfera A (Objeto Principal)")
    raio_a_mm = st.slider(
        "Raio da Esfera A (mm):",
        0.5,
        10.0,
        2.0,
        0.5,
        help="Raio físico da partícula/esfera em milímetros.",
    )
    vel_a = st.slider(
        "Velocidade da Esfera A (cm/s):",
        0.1,
        50.0,
        10.0,
        0.5,
        key="vel_a",
        help="Velocidade em centímetros por segundo (regime laminar/baixo).",
    )
    raio_a = raio_a_mm / 1000.0  # Convertendo para metros

with col_config2:
    st.subheader("📊 Esfera B (Modo Comparativo)")
    comparar = st.checkbox("Ativar Comparação de Raios")

    if comparar:
        raio_b_mm = st.slider(
            "Raio da Esfera B (mm):", 0.5, 10.0, 3.0, 0.5, key="raio_b"
        )
        vel_b = st.slider(
            "Velocidade da Esfera B (cm/s):",
            0.1,
            50.0,
            10.0,
            0.5,
            key="vel_b",
        )
        raio_b = raio_b_mm / 1000.0

# --- MOTOR DE CÁLCULO FÍSICO (LEI DE STOKES) ---
# F_d = 6 * pi * mu * r * v (v em m/s)
v_a_ms = vel_a / 100.0  # Convertendo cm/s para m/s
f_d_a = 6 * np.pi * mu * raio_a * v_a_ms

# Exibição de Métricas
st.markdown("---")
col_met1, col_met2 = st.columns(2)
with col_met1:
    st.metric(
        label=f"Força de Arrasto (Esfera A: {raio_a_mm} mm)",
        value=f"{f_d_a * 1e6:.2f} µN"
        if f_d_a < 1e-3
        else f"{f_d_a:.4f} N",
    )

if comparar:
    v_b_ms = vel_b / 100.0
    f_d_b = 6 * np.pi * mu * raio_b * v_b_ms
    with col_met2:
        st.metric(
            label=f"Força de Arrasto (Esfera B: {raio_b_mm} mm)",
            value=f"{f_d_b * 1e6:.2f} µN"
            if f_d_b < 1e-3
            else f"{f_d_b:.4f} N",
        )

# --- GRÁFICO DINÂMICO (LEI DE STOKES) ---
st.markdown("### 📈 Curva de Arrasto Viscoso Linear (Lei de Stokes)")

velocidades_range_cms = np.linspace(0, 50, 100)
velocidades_range_ms = velocidades_range_cms / 100.0
forcas_range_a = 6 * np.pi * mu * raio_a * velocidades_range_ms

fig = go.Figure()

# Curva da Esfera A
fig.add_trace(
    go.Scatter(
        x=velocidades_range_cms,
        y=forcas_range_a * 1000,  # Convertendo para miliNewtons para melhor leitura
        mode="lines",
        name=f"Esfera A ({raio_a_mm} mm)",
        line=dict(color="#2563EB", width=3),
    )
)

# Ponto atual Esfera A
fig.add_trace(
    go.Scatter(
        x=[vel_a],
        y=[f_d_a * 1000],
        mode="markers",
        name=f"Atual A ({vel_a} cm/s)",
        marker=dict(color="#1E3A8A", size=12, symbol="circle"),
    )
)

if comparar:
    forcas_range_b = 6 * np.pi * mu * raio_b * velocidades_range_ms
    fig.add_trace(
        go.Scatter(
            x=velocidades_range_cms,
            y=forcas_range_b * 1000,
            mode="lines",
            name=f"Esfera B ({raio_b_mm} mm)",
            line=dict(color="#DC2626", width=3, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[vel_b],
            y=[f_d_b * 1000],
            mode="markers",
            name=f"Atual B ({vel_b} cm/s)",
            marker=dict(color="#991B1B", size=12, symbol="diamond"),
        )
    )

fig.update_layout(
    title="Força de Resistência Viscosa ($F_d = 6\\pi\\mu r v$)",
    xaxis_title="Velocidade (cm/s)",
    yaxis_title="Força de Arrasto (mN)",
    template="plotly_white",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)
