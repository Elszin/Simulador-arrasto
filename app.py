import streamlit as st
import numpy as np
import pandas as pd

# 1. Configuração da Página e Título
st.set_page_config(page_title="Simulador de Arrasto Aerodinâmico", page_icon="🚗")
st.title("🚗 Simulador de Força de Arrasto Aerodinâmico")
st.write("Cálculo baseado na equação fundamental: $F_d = \\frac{1}{2} \\cdot \\rho \\cdot v^2 \\cdot C_d \\cdot A$")

# 2. Perfis de Veículos Pré-configurados
veiculo = st.selectbox("Selecione um perfil de veículo para testar:", 
                       ["Personalizado", "Carro Popular", "Esportivo", "Caminhão"])

if veiculo == "Carro Popular":
    cd_padrao, a_padrao = 0.32, 2.2
elif veiculo == "Esportivo":
    cd_padrao, a_padrao = 0.28, 1.9
elif veiculo == "Caminhão":
    cd_padrao, a_padrao = 0.70, 8.0
else:
    cd_padrao, a_padrao = 0.30, 2.0

# 3. Controles Interativos (Barra Lateral)
st.sidebar.header("Parâmetros da Simulação")
v_kmh = st.sidebar.slider("Velocidade (km/h)", 0, 200, 100)
rho = st.sidebar.slider("Densidade do Ar ρ (kg/m³)", 1.00, 1.30, 1.225)
cd = st.sidebar.slider("Coeficiente de Arrasto (Cd)", 0.10, 1.00, cd_padrao)
area = st.sidebar.slider("Área Frontal A (m²)", 0.5, 10.0, a_padrao)

# 4. Cálculo Físico da Força de Arrasto
v_ms = v_kmh / 3.6  # Converte velocidade para m/s
fd = 0.5 * rho * (v_ms ** 2) * cd * area  # Fd em Newtons (N)

# 5. Destaque dos Resultados (Cartões de Métricas)
col1, col2, col3 = st.columns(3)
col1.metric("Velocidade Selecionada", f"{v_kmh} km/h")
col2.metric("Força de Arrasto (Fd)", f"{fd:.2f} N")
col3.metric("Potência Necessária", f"{(fd * v_ms / 1000):.2f} kW")

# 6. Gráfico Nativo do Streamlit (Sem dependências externas)
st.subheader("Gráfico: Comportamento da Força de Arrasto com a Velocidade")

vel_curva_kmh = np.linspace(0, 200, 100)
vel_curva_ms = vel_curva_kmh / 3.6
forcas_curva = 0.5 * rho * (vel_curva_ms ** 2) * cd * area

df_grafico = pd.DataFrame({
    "Velocidade (km/h)": vel_curva_kmh,
    "Força de Arrasto (N)": forcas_curva
})

st.line_chart(df_grafico, x="Velocidade (km/h)", y="Força de Arrasto (N)")
