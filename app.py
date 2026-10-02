import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Simulador de Arrasto Viscoso (Lei de Stokes)",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilização CSS customizada para espaçamento e visual
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- LAYOUT EM TRÊS COLUNAS PRINCIPAIS ---
col_esq, col_meio, col_dir = st.columns([1.1, 2.2, 1.1])

# --- COLUNA DA ESQUERDA: PARÂMETROS DO FLUIDO ---
with col_esq:
    st.subheader("🌍 Fluido")
    fluido = st.selectbox("Escolha o Meio:", ["Ar", "Água"])

    if fluido == "Ar":
        temperatura = st.slider("Temperatura (°C):", -20, 40, 20, 1)
        mu = 1.71e-5 + 4.8e-8 * temperatura
    else:
        temperatura = st.slider("Temperatura (°C):", 0, 30, 20, 1)
        mu = 1.002e-3 / (1.0 + 0.033 * (temperatura - 20))

    st.markdown("---")
    st.markdown(f"**Viscosidade ($\mu$):**")
    st.code(f"{mu:.2e} Pa·s")

    st.info(
        "💡 **Dica:** A água possui viscosidade muito superior ao ar, gerando forças de arrasto consideravelmente maiores para a mesma esfera."
    )

# --- COLUNA DA DIREITA: OBJETOS (CONFIGURAÇÃO) ---
with col_dir:
    st.subheader("⚙️ Objetos")

    st.markdown("##### 🔵 Esfera Principal (A)")
    raio_a_mm = st.slider(
        "Raio A (mm):",
        0.5,
        10.0,
        2.0,
        0.5,
        help="Raio físico da partícula em milímetros.",
    )
    vel_a = st.slider("Velocidade A (cm/s):", 0.1, 50.0, 10.0, 0.5, key="vel_a")
    raio_a = raio_a_mm / 1000.0

    st.markdown("---")
    st.markdown("##### 📊 Comparação (B)")
    comparar = st.checkbox("Ativar Esfera B")

    if comparar:
        raio_b_mm = st.slider(
            "Raio B (mm):", 0.5, 10.0, 3.0, 0.5, key="raio_b"
        )
        vel_b = st.slider(
            "Velocidade B (cm/s):", 0.1, 50.0, 10.0, 0.5, key="vel_b"
        )
        raio_b = raio_b_mm / 1000.0

# --- COLUNA DO MEIO: TÍTULO, MÉTRICAS E GRÁFICO ---
with col_meio:
    st.markdown(
        '<div class="main-title">Simulador de Arrasto Viscoso Linear</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtitle">Análise física baseada na Lei de Stokes</div>',
        unsafe_allow_html=True,
    )

    # Fórmula renderizada de forma limpa em LaTeX
    st.latex(r"F_d = 6 \cdot \pi \cdot \mu \cdot r \cdot v")

    # Motor de Cálculo Físico
    v_a_ms = vel_a / 100.0
    f_d_a = 6 * np.pi * mu * raio_a * v_a_ms

    # Exibição de Métricas nas colunas do meio
    if comparar:
        met_c1, met_c2 = st.columns(2)
        with met_c1:
            st.metric(
                label=f"Arrasto (A: {raio_a_mm}mm)",
                value=f"{f_d_a * 1e6:.2f} µN"
                if f_d_a < 1e-3
                else f"{f_d_a:.4f} N",
            )
        v_b_ms = vel_b / 100.0
        f_d_b = 6 * np.pi * mu * raio_b * v_b_ms
        with met_c2:
            st.metric(
                label=f"Arrasto (B: {raio_b_mm}mm)",
                value=f"{f_d_b * 1e6:.2f} µN"
                if f_d_b < 1e-3
                else f"{f_d_b:.4f} N",
            )
    else:
        st.metric(
            label=f"Força de Arrasto Calculada (Esfera A - {raio_a_mm} mm)",
            value=f"{f_d_a * 1e6:.2f} µN"
            if f_d_a < 1e-3
            else f"{f_d_a:.4f} N",
        )

    # Gráfico Dinâmico Plotly
    velocidades_range_cms = np.linspace(0, 50, 100)
    velocidades_range_ms = velocidades_range_cms / 100.0
    forcas_range_a = 6 * np.pi * mu * raio_a * velocidades_range_ms

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=velocidades_range_cms,
            y=forcas_range_a * 1000,
            mode="lines",
            name=f"Esfera A ({raio_a_mm} mm)",
            line=dict(color="#2563EB", width=3),
        )
    )

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
        title="Relação Linear Velocidade vs. Força de Resistência",
        xaxis_title="Velocidade (cm/s)",
        yaxis_title="Força de Arrasto (mN)",
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)
