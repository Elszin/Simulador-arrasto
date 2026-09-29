import streamlit as st
import numpy as np
import pandas as pd

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

# 5. Gráfico Comparativo Nativo
st.subheader("📈 Comparativo de Curvas de Arrasto (Escala Fixa ate 4500 N)")

v_vetor_kmh = np.linspace(0, 200, 101)
v_vetor_ms = v_vetor_kmh / 3.6

dados_grafico = {
    "Velocidade (km/h)": v_vetor_kmh,
}

# Adiciona a curva de cada veículo ao mesmo gráfico
for nome, (c_d_p, a_p) in perfis.items():
    if nome == "Personalizado":
        continue
    dados_grafico[nome] = 0.5 * rho * (v_vetor_ms ** 2) * c_d_p * a_p

if veiculo == "Personalizado":
    dados_grafico["Personalizado"] = 0.5 * rho * (v_vetor_ms ** 2) * cd * area

# Linha teto fixo em 4500 N para travar o eixo Y
dados_grafico["Teto Escala (4500 N)"] = 4500.0

df_grafico = pd.DataFrame(dados_grafico)

colunas_linhas = [c for c in df_grafico.columns if c not in ["Velocidade (km/h)", "Teto Escala (4500 N)"]]

st.line_chart(
    df_grafico, 
    x="Velocidade (km/h)", 
    y=colunas_linhas,
    height=450
)

st.success(f"📍 **Ponto Atual ({veiculo}):** Na velocidade de **{v_kmh} km/h**, a Força de Arrasto e de **{fd:.1f} N** e consome **{potencia_cv:.1f} CV** do motor.")
