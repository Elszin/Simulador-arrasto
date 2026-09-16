import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="Simulador de Força de Arrasto", layout="wide")

st.title("⚡ Simulador Interativo: Força de Arrasto")
st.markdown(
    "Ajuste os parâmetros para calcular $F_d = \\frac{1}{2} \\rho v^2 C_d A$"
)

# Sliders na lateral
st.sidebar.header("⚙️ Configurações")
rho = st.sidebar.slider("Massa específica (ρ) [kg/m³]", 0.1, 10.0, 1.225)
v = st.sidebar.slider("Velocidade (v) [m/s]", 0.0, 150.0, 30.0)
cd = st.sidebar.slider("Coeficiente de arrasto (Cd)", 0.01, 2.0, 0.47)
a = st.sidebar.slider("Área frontal (A) [m²]", 0.01, 20.0, 0.5)

# Cálculo
fd = 0.5 * rho * (v**2) * cd * a
v_kmh = v * 3.6

# Métricas
col1, col2 = st.columns(2)
col1.metric("Força de Arrasto", f"{fd:.2f} N")
col2.metric("Velocidade em km/h", f"{v_kmh:.1f} km/h")

# Gráfico
v_array = np.linspace(0, 150, 300)
fd_array = 0.5 * rho * (v_array**2) * cd * a

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(v_array, fd_array, color="#1f77b4", lw=2)
ax.scatter([v], [fd], color="red", s=70, zorder=5)
ax.set_xlabel("Velocidade (m/s)")
ax.set_ylabel("Força de Arrasto (N)")
ax.grid(True, linestyle="--", alpha=0.6)

st.pyplot(fig)
