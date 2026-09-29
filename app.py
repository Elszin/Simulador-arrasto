import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# 1. Configuração da Página
st.set_page_config(page_title="Simulador de Arrasto Aerodinâmico", page_icon="🚗", layout="wide")

st.title("🚗 Simulador de Força de Arrasto Aerodinâmico")
st.write("Cálculo baseado na equação fundamental: $F_d = \\frac{1}{2} \\cdot \\rho \\cdot v^2 \\cdot C_d \\cdot A$")

# 2. Sidebar - Seleção e Controles
st.sidebar.header("⚙️ Configurações do Veículo")

perfis = {
    "Carro Popular": (0.32, 2.2),
    "Esportivo": (0.28, 1.9),
    "Caminhão": (0.70, 8.0),
    "Personalizado": (0.30, 2.0)
}

# Opção de Comparação entre 2 veículos
comparar = st.sidebar.checkbox("🔍 Comparar 2 Veículos", value=False)

if comparar:
    col_comp1, col_comp2 = st.sidebar.columns(2)
    with col_comp1:
        v_nome1 = st.selectbox("Veículo 1:", list(perfis.keys()), index=0)
    with col_comp2:
        v_nome2 = st.selectbox("Veículo 2:", list(perfis.keys()), index=2)
    veiculo_principal = v_nome1
else:
    veiculo_principal = st.sidebar.selectbox("Selecione o veículo:", list(perfis.keys()), index=0)
    v_nome1, v_nome2 = veiculo_principal, None

# Sliders de controle
st.sidebar.markdown("---")
v_kmh = st.sidebar.slider("Velocidade (km/h)", 0, 200, 110, step=5)
rho = st.sidebar.slider("Densidade do Ar ρ (kg/m³)", 1.00, 1.30, 1.225, step=0.01)

# Leitura do Cd e Área do veículo principal
if veiculo_principal == "Personalizado":
    cd = st.sidebar.slider("Coeficiente de Arrasto (Cd) - Principal", 0.10, 1.20, perfis["Personalizado"][0], step=0.01)
    area = st.sidebar.slider("Área Frontal A (m²) - Principal", 0.5, 10.0, perfis["Personalizado"][1], step=0.1)
else:
    cd, area = perfis[veiculo_principal]
    st.sidebar.info(f"**{veiculo_principal}**\n- $C_d$: {cd}\n- Área Frontal: {area} m²")

# 3. Cálculos Físicos
v_ms = v_kmh / 3.6
fd = 0.5 * rho * (v_ms ** 2) * cd * area
potencia_kw = (fd * v_ms) / 1000
potencia_cv = potencia_kw * 1.35962

# Exibição de Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Velocidade", f"{v_kmh} km/h")
col2.metric("Força de Arrasto (Fd)", f"{fd:.1f} N")
col3.metric("Potência (kW)", f"{potencia_kw:.1f} kW")
col4.metric("Potência (CV)", f"{potencia_cv:.1f} cv")

st.markdown("---")
st.subheader("📈 Curva de Arrasto Aerodinâmico (Escala Fixa até 4500 N)")

# 4. Construção dos Dados do Gráfico
v_vetor_kmh = np.linspace(0, 200, 101)
v_vetor_ms = v_vetor_kmh / 3.6

rows = []
veiculos_para_plotar = [v_nome1, v_nome2] if (comparar and v_nome1 and v_nome2) else [veiculo_principal]

for v_nome in veiculos_para_plotar:
    c_d_v, a_v = (cd, area) if (v_nome == "Personalizado" and v_nome == veiculo_principal) else perfis[v_nome]
    for vk, vm in zip(v_vetor_kmh, v_vetor_ms):
        f_val = 0.5 * rho * (vm ** 2) * c_d_v * a_v
        rows.append({
            "Velocidade (km/h)": vk,
            "Força de Arrasto (N)": f_val,
            "Veículo": v_nome
        })

df_chart = pd.DataFrame(rows)

# 5. Renderização do Gráfico com Altair
scale_y = alt.Scale(domain=[0, 4500], clamp=True)
scale_x = alt.Scale(domain=[0, 200])

# Camada 1: Área Translúcida Sombreada
area_chart = alt.Chart(df_chart).mark_area(opacity=0.25).encode(
    x=alt.X("Velocidade (km/h):Q", scale=scale_x),
    y=alt.Y("Força de Arrasto (N):Q", scale=scale_y),
    color=alt.Color("Veículo:N")
)

# Camada 2: Linha Principal
line_chart = alt.Chart(df_chart).mark_line(size=3).encode(
    x=alt.X("Velocidade (km/h):Q", scale=scale_x),
    y=alt.Y("Força de Arrasto (N):Q", scale=scale_y),
    color=alt.Color("Veículo:N")
)

# Camada 3: Ponto Fixo
df_ponto = pd.DataFrame([{
    "Velocidade (km/h)": v_kmh,
    "Força de Arrasto (N)": fd,
    "Veículo": veiculo_principal
}])

point_chart = alt.Chart(df_ponto).mark_circle(size=140, color="red").encode(
    x=alt.X("Velocidade (km/h):Q", scale=scale_x),
    y=alt.Y("Força de Arrasto (N):Q", scale=scale_y)
)

# Camada 4: Rótulo de Texto Fixo
text_chart = alt.Chart(df_ponto).mark_text(
    align='left', dx=10, dy=-10, fontSize=13, fontWeight='bold', color='white'
).encode(
    x=alt.X("Velocidade (km/h):Q", scale=scale_x),
    y=alt.Y("Força de Arrasto (N):Q", scale=scale_y),
    text=alt.value(f"{v_kmh} km/h | {fd:.1f} N")
)

# Une todas as camadas sem zoom/interatividade excessiva
final_chart = (area_chart + line_chart + point_chart + text_chart).properties(
    height=450
).interactive(bind_y=False, bind_x=False)

st.altair_chart(final_chart, use_container_width=True)

st.success(f"📍 **Ponto Atual ({veiculo_principal}):** Na velocidade de **{v_kmh} km/h**, a Força de Arrasto é de **{fd:.1f} N** e consome **{potencia_cv:.1f} CV** do motor.")
