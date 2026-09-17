import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Simulador de Arrasto", layout="centered")

st.title("⚡ Simulador: Força de Arrasto")
st.latex(r"F_d = \frac{1}{2} \rho v^2 C_d A")

# Controles diretos na tela principal
st.subheader("Controles")
v_kmh = st.slider("Velocidade (km/h)", 0.0, 150.0, 108.0, 1.0)
rho = st.slider("Densidade do ar ρ (kg/m³)", 0.5, 2.0, 1.225, 0.05)
cd = st.slider("Coeficiente de arrasto (Cd)", 0.1, 1.5, 0.3, 0.05)
area = st.slider("Área frontal A (m²)", 0.5, 5.0, 2.0, 0.1)

# Cálculo da força
v_ms = v_kmh / 3.6
fd_atual = 0.5 * rho * (v_ms ** 2) * cd * area

st.metric("Força de Arrasto", f"{fd_atual:.2f} N")

# Vetor para desenhar a curva contínua
v_vetor_ms = np.linspace(0, 150 / 3.6, 100)
v_vetor_kmh = v_vetor_ms * 3.6
fd_vetor = 0.5 * rho * (v_vetor_ms ** 2) * cd * area

# Gráfico interativo fluído
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=v_vetor_kmh, y=fd_vetor,
    mode='lines',
    name='Curva Fd',
    line=dict(color='#00D2FF', width=3)
))

fig.add_trace(go.Scatter(
    x=[v_kmh], y=[fd_atual],
    mode='markers',
    name='Ponto Atual',
    marker=dict(color='#FF2A6D', size=12)
))

fig.update_layout(
    xaxis_title="Velocidade (km/h)",
    yaxis_title="Força de Arrasto (N)",
    template="plotly_dark",
    margin=dict(l=20, r=20, t=20, b=20),
    height=350,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
