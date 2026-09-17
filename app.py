import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Simulador de Arrasto", layout="centered")

st.title("⚡ Simulador: Força de Arrasto")
st.latex(r"F_d = \frac{1}{2} \rho v^2 C_d A")

# Controles organizados em colunas
st.subheader("⚙️ Parâmetros do Sistema")
col_ctrl1, col_ctrl2 = st.columns(2)

with col_ctrl1:
    rho = st.slider("Densidade do ar ρ (kg/m³)", 0.5, 2.0, 1.225, 0.05)
    cd = st.slider("Coeficiente de arrasto (Cd)", 0.1, 1.5, 0.3, 0.05)

with col_ctrl2:
    area = st.slider("Área frontal A (m²)", 0.5, 5.0, 2.0, 0.1)
    v_kmh = st.slider("Velocidade atual (km/h)", 0.0, 150.0, 108.0, 1.0)

# Cálculos
v_ms = v_kmh / 3.6
fd_atual = 0.5 * rho * (v_ms ** 2) * cd * area

# Exibição de Métricas em Destaque
col_m1, col_m2 = st.columns(2)
col_m1.metric("Força de Arrasto (Fd)", f"{fd_atual:.2f} N")
col_m2.metric("Velocidade (v)", f"{v_ms:.1f} m/s", f"{v_kmh:.0f} km/h")

# Vetor da curva
v_vetor_ms = np.linspace(0, 150 / 3.6, 100)
v_vetor_kmh = v_vetor_ms * 3.6
fd_vetor = 0.5 * rho * (v_vetor_ms ** 2) * cd * area

# Gráfico Avançado com Plotly
fig = go.Figure()

# Curva com preenchimento sombreado
fig.add_trace(go.Scatter(
    x=v_vetor_kmh, y=fd_vetor,
    mode='lines',
    name='Curva Fd',
    line=dict(color='#00D2FF', width=3),
    fill='tozeroy',
    fillcolor='rgba(0, 210, 255, 0.1)',
    hovertemplate='Velocidade: %{x:.1f} km/h<br>Força: %{y:.2f} N<extra></extra>'
))

# Linha projetada no Eixo Y (Força)
fig.add_trace(go.Scatter(
    x=[0, v_kmh], y=[fd_atual, fd_atual],
    mode='lines',
    line=dict(color='rgba(255, 42, 109, 0.5)', width=1.5, dash='dash'),
    hoverinfo='skip'
))

# Linha projetada no Eixo X (Velocidade)
fig.add_trace(go.Scatter(
    x=[v_kmh, v_kmh], y=[0, fd_atual],
    mode='lines',
    line=dict(color='rgba(255, 42, 109, 0.5)', width=1.5, dash='dash'),
    hoverinfo='skip'
))

# Ponto atual destacado
fig.add_trace(go.Scatter(
    x=[v_kmh], y=[fd_atual],
    mode='markers',
    name='Ponto Atual',
    marker=dict(color='#FF2A6D', size=12, line=dict(color='#FFFFFF', width=2)),
    hovertemplate='<b>Ponto Atual</b><br>v: %{x:.1f} km/h<br>Fd: %{y:.2f} N<extra></extra>'
))

fig.update_layout(
    xaxis_title="Velocidade (km/h)",
    yaxis_title="Força de Arrasto (N)",
    template="plotly_dark",
    margin=dict(l=20, r=20, t=20, b=20),
    height=400,
    showlegend=False,
    yaxis=dict(range=[0, 4000], gridcolor='#333333'),
    xaxis=dict(gridcolor='#333333')
)

st.plotly_chart(fig, use_container_width=True)
