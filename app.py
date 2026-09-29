import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. Configuração da Página
st.set_page_config(page_title="Simulador de Arrasto Aerodinâmico", page_icon="🚗", layout="wide")

st.title("🚗 Simulador de Força de Arrasto Aerodinâmico")
st.write("Cálculo baseado na equação fundamental: $F_d = \\frac{1}{2} \\cdot \\rho \\cdot v^2 \\cdot C_d \\cdot A$")

# 2. Sidebar - Seleção e Controles
st.sidebar.header("⚙️ Configurações do Veículo")

veiculo = st.sidebar.selectbox(
    "Selecione um perfil de veículo:", 
    ["Carro Popular", "Esportivo", "Caminhão", "Personalizado"]
)

# Valores padrão de Cd e Área
perfis = {
    "Carro Popular": (0.32, 2.2),
    "Esportivo": (0.28, 1.9),
    "Caminhão": (0.70, 8.0),
    "Personalizado": (0.30, 2.0)
}

cd_def, a_def = perfis[veiculo]

# Sliders
v_kmh = st.sidebar.slider("Velocidade (km/h)", 0, 200, 110, step=5)
rho = st.sidebar.slider("Densidade do Ar ρ (kg/m³)", 1.00, 1.30, 1.225, step=0.01)

if veiculo == "Personalizado":
    cd = st.sidebar.slider("Coeficiente de Arrasto (Cd)", 0.10, 1.20, cd_def, step=0.01)
    area = st.sidebar.slider("Área Frontal A (m²)", 0.5, 10.0, a_def, step=0.1)
else:
    cd, area = cd_def, a_def
    st.sidebar.info(f"**{veiculo}**\n- $C_d$: {cd}\n- Área Frontal: {area} m²")

# 3. Cálculos Físicos
v_ms = v_kmh / 3.6
fd = 0.5 * rho * (v_ms ** 2) * cd * area
potencia_kw = (fd * v_ms) / 1000
potencia_cv = potencia_kw * 1.35962

# 4. Exibição de Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Velocidade", f"{v_kmh} km/h")
col2.metric("Força de Arrasto (Fd)", f"{fd:.1f} N")
col3.metric("Potência (kW)", f"{potencia_kw:.1f} kW")
col4.metric("Potência (CV)", f"{potencia_cv:.1f} cv")

st.markdown("---")

# 5. Gráfico Bonito com Eixo Fixo no Matplotlib
st.subheader("📈 Comparativo de Curvas de Arrasto (Escala Fixa)")

# Vetor de velocidades de 0 a 200 km/h
v_vetor_kmh = np.linspace(0, 200, 200)
v_vetor_ms = v_vetor_kmh / 3.6

# Estilo visual moderno do gráfico (Dark Mode)
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

color_map = {
    "Carro Popular": "#00d2ff", # Azul Neon
    "Esportivo": "#00ff87",    # Verde Neon
    "Caminhão": "#ff4b4b"      # Vermelho Neon
}

# Desenha as curvas dos 3 veículos principais para comparação
for nome, (c_d_p, a_p) in perfis.items():
    if nome == "Personalizado":
        continue
    fd_curva = 0.5 * rho * (v_vetor_ms ** 2) * c_d_p * a_p
    is_selected = (nome == veiculo)
    
    alpha = 1.0 if is_selected else 0.25
    linewidth = 3.2 if is_selected else 1.5
    linestyle = '-' if is_selected else '--'
    
    ax.plot(
        v_vetor_kmh, fd_curva, 
        label=nome, 
        color=color_map[nome], 
        alpha=alpha, 
        linewidth=linewidth, 
        linestyle=linestyle
    )

# Se for personalizado, desenha a curva personalizada
if veiculo == "Personalizado":
    fd_curva_custom = 0.5 * rho * (v_vetor_ms ** 2) * cd * area
    ax.plot(v_vetor_kmh, fd_curva_custom, label="Personalizado", color="#ffaa00", linewidth=3.2)
    cor_ponto = "#ffaa00"
else:
    cor_ponto = color_map[veiculo]

# Ponto Atual (Velocidade Selecionada)
ax.scatter([v_kmh], [fd], color=cor_ponto, s=120, zorder=5, edgecolor='white', linewidth=1.5)
ax.annotate(
    f"  {v_kmh} km/h\n  {fd:.0f} N", 
    (v_kmh, fd), 
    textcoords="offset points", 
    xytext=(10, -10), 
    color='white', 
    fontsize=10, 
    weight='bold',
    bbox=dict(boxstyle="round,pad=0.3", fc="#1e1e1e", ec=cor_ponto, lw=1.5)
)

# Linhas auxiliares tracejadas
ax.axvline(x=v_kmh, color='gray', linestyle=':', alpha=0.5)
ax.axhline(y=fd, color='gray', linestyle=':', alpha=0.5)

# ESCALA FIXA DOS EIXOS (Não muda quando você mexe no slider!)
ax.set_xlim(0, 200)
ax.set_ylim(0, 4500)

# Estilização de Títulos e Grade
ax.set_title("Comportamento Quadrático da Força de Arrasto (Fd vs V)", fontsize=13, pad=15, color='white', weight='bold')
ax.set_xlabel("Velocidade (km/h)", fontsize=11, color='white')
ax.set_ylabel("Força de Arrasto Fd (N)", fontsize=11, color='white')
ax.grid(True, linestyle='--', alpha=0.2)
ax.legend(loc="upper left", frameon=True, facecolor="#1e1e1e", edgecolor="gray")

# Exibir no Streamlit
st.pyplot(fig)
