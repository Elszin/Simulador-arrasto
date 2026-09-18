import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador Aerodinâmico", layout="wide")

# --- BANCO DE DADOS E DADOS DE PRESET ---
PRESETS_VEICULOS = {
    "Sedan Médio": {"cd": 0.28, "area": 2.2, "comprimento": 4.5, "tipo": "sedan"},
    "SUV Compacto": {"cd": 0.35, "area": 2.6, "comprimento": 4.3, "tipo": "suv"},
    "Hatch Compacto": {"cd": 0.32, "area": 2.1, "comprimento": 3.9, "tipo": "hatch"},
    "Esportivo": {"cd": 0.29, "area": 1.9, "comprimento": 4.4, "tipo": "esportivo"},
    "Caminhonete": {"cd": 0.42, "area": 3.1, "comprimento": 5.3, "tipo": "caminhonete"}
}

def calcular_densidade_ar(temp_c, altitude_m=0):
    T_kelvin = temp_c + 273.15
    P0 = 101325  # Pa
    L = 0.0065   # K/m
    R = 8.31447
    M = 0.0289644
    g = 9.80665
    P = P0 * (1 - (L * altitude_m) / 288.15) ** ((g * M) / (R * L))
    R_especifico = 287.058
    rho = P / (R_especifico * T_kelvin)
    return rho

def gerar_silhueta_veiculo(tipo, comp, alt):
    if tipo == "sedan":
        x = [-comp*0.5, -comp*0.48, -comp*0.35, -comp*0.15, comp*0.1, comp*0.35, comp*0.48, comp*0.5, comp*0.5, -comp*0.5]
        y = [alt*0.2, alt*0.45, alt*0.52, alt*1.0, alt*1.0, alt*0.6, alt*0.5, alt*0.2, 0, 0]
    elif tipo == "suv":
        x = [-comp*0.5, -comp*0.48, -comp*0.38, -comp*0.2, comp*0.3, comp*0.45, comp*0.5, comp*0.5, -comp*0.5]
        y = [alt*0.25, alt*0.5, alt*0.55, alt*1.0, alt*0.98, alt*0.7, alt*0.25, 0, 0]
    elif tipo == "esportivo":
        x = [-comp*0.5, -comp*0.48, -comp*0.25, comp*0.0, comp*0.25, comp*0.45, comp*0.5, comp*0.5, -comp*0.5]
        y = [alt*0.15, alt*0.35, alt*0.45, alt*0.95, alt*0.9, alt*0.55, alt*0.18, 0, 0]
    else:
        x = [-comp*0.5, -comp*0.45, -comp*0.2, comp*0.2, comp*0.45, comp*0.5, comp*0.5, -comp*0.5]
        y = [alt*0.2, alt*0.48, alt*0.95, alt*0.95, alt*0.55, alt*0.2, 0, 0]
    return np.array(x), np.array(y)


# --- BARRA LATERAL (PARÂMETROS DE ENTRADA) ---
st.sidebar.title("🛠️ Configurações & Parâmetros")

# 1. Combustível e Motor
st.sidebar.markdown("### ⛽ Combustível & Motor")
preco_combustivel = st.sidebar.number_input("Preço do Combustível (R$/L):", value=6.00, step=0.10)
eficiencia_motor = st.sidebar.slider("Eficiência Térmica do Motor (%)", 10, 50, 30) / 100.0

# 2. Condições Ambientais & Velocidade
st.sidebar.markdown("### 🌡️ Ambiente & Velocidade")
temp_c = st.sidebar.slider("Temperatura do Ar (°C)", -10, 50, 25)
v_veiculo_kmh = st.sidebar.slider("Velocidade do Veículo (km/h)", 10.0, 300.0, 220.0)
v_vento_kmh = st.sidebar.slider("Vento Frontal (+Contra / -Favor) (km/h)", -100.0, 100.0, -40.0)

# Cálculos de Densidade e Velocidades
rho = calcular_densidade_ar(temp_c)
v_efetiva_kmh = v_veiculo_kmh + v_vento_kmh
v_efetiva_ms = max(0.0, v_efetiva_kmh / 3.6)

# 3. Parâmetros do Veículo A
st.sidebar.markdown("### 🚗 Veículo A")
modelo_a = st.sidebar.selectbox("Preset Veículo A", list(PRESETS_VEICULOS.keys()), index=0)
massa_a = st.sidebar.number_input("Massa (kg):", value=1100.0, step=50.0)
potencia_a = st.sidebar.number_input("Potência Motor (CV):", value=100.0, step=10.0)
comprimento_a = st.sidebar.number_input("Comprimento (m):", value=PRESETS_VEICULOS[modelo_a]["comprimento"], step=0.1)

# Aerofólio / Downforce
usar_aerofolio = st.sidebar.checkbox("➕ Adicionar Aerofólio", value=True)
if usar_aerofolio:
    cl_a = st.sidebar.slider("C_L (Downforce):", 0.05, 2.5, 2.0, step=0.05)
    area_asa_a = st.sidebar.slider("Área da Asa (m²):", 0.1, 1.5, 0.40, step=0.05)
    cd_extra_asa = cl_a * 0.12
else:
    cl_a = 0.0
    area_asa_a = 0.0
    cd_extra_asa = 0.0

cd_a = PRESETS_VEICULOS[modelo_a]["cd"] + cd_extra_asa
area_a = PRESETS_VEICULOS[modelo_a]["area"]

# Cálculos de Forças Veículo A
fd_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a
downforce_a = 0.5 * rho * (v_efetiva_ms ** 2) * cl_a * area_asa_a


# --- CORPO PRINCIPAL DO APP ---
st.title("🚀 Simulador de Aerodinâmica & Arrasto")

tab_resumo, tab_desenho = st.tabs(["📊 Resumo & Desempenho", "🌀 Túnel de Vento Interativo"])

with tab_resumo:
    col1, col2, col3 = st.columns(3)
    col1.metric("Força de Arrasto (Fd)", f"{fd_a:.1f} N")
    col2.metric("Downforce Gerado", f"{downforce_a:.1f} N")
    col3.metric("Densidade do Ar (ρ)", f"{rho:.3f} kg/m³")


# TAB 2: TÚNEL DE VENTO COM DENSIDADE, ENERGIA E AEROFOIL INTERATIVO
with tab_desenho:
    st.markdown("#### 🌀 Densidade de Moléculas (Temperatura) e Energia de Impacto (Velocidade)")
    st.caption(f"🌡️ **{temp_c}°C** → Densidade de Moléculas: **{rho:.3f} kg/m³** | 💨 Velocidade do Fluxo: **{v_efetiva_ms*3.6:.1f} km/h**")
    
    fig_draw = go.Figure()
    
    # 1. Silhueta do Veículo
    tipo_veiculo_a = PRESETS_VEICULOS[modelo_a]["tipo"]
    altura_a = np.sqrt(area_a) * 0.95
    x_carro, y_carro = gerar_silhueta_veiculo(tipo_veiculo_a, comprimento_a, altura_a)
    
    # Posição Exata da Asa na Traseira (Alinhada com a silhueta do veículo)
    x_asa_pos = comprimento_a * 0.38
    y_asa_pos = altura_a * 0.72
    
    # 2. Densidade de Moléculas
    num_linhas = int(np.clip(14 + (rho - 0.8) * 20, 10, 30))
    pts_por_linha = 50
    
    x_grid = np.linspace(-comprimento_a * 1.2, comprimento_a * 2.0, pts_por_linha)
    y_iniciais = np.linspace(-altura_a * 0.3, altura_a * 2.6, num_linhas)
    
    px_list, py_list, vel_list, size_list = [], [], [], []
    
    R_eff = altura_a * (0.8 + cd_a * 0.4)
    
    for y0 in y_iniciais:
        for x in x_grid:
            # Distância ao centro do carro
            r2_carro = x**2 + (y0 - altura_a*0.5)**2
            
            # Desvio normal do corpo do veículo
            dy_carro = (R_eff**2 * max(0.1, y0)) / max(r2_carro, R_eff**1.8) * np.exp(-((x + comprimento_a*0.1) / (comprimento_a*0.7))**2)
            
            # Deformação Visual do Aerofólio
            dy_asa = 0.0
            v_boost_asa = 0.0
            
            if usar_aerofolio:
                # Distância da partícula até a asa
                dist_asa = np.sqrt((x - x_asa_pos)**2 + (y0 - y_asa_pos)**2)
                
                # Deflexão para cima (Downforce empurra o ar pra cima na saída)
                fator_campo = np.exp(-(dist_asa**2) / (0.8 * comprimento_a))
                dy_asa = (cl_a * 0.45) * fator_campo
                
                # Aceleração e turbulência local
                v_boost_asa = (cl_a * 35.0) * fator_campo

            y_part = max(0.02, y0 + dy_carro + dy_asa)
            
            # Velocidade local + efeito da asa
            v_relativa = v_efetiva_ms * (1.0 - (R_eff**2 * (x**2 - (y0-altura_a*0.5)**2)) / max(r2_carro**2, R_eff**3.5))
            v_local_total = abs(v_relativa) * 3.6 + v_boost_asa
            
            px_list.append(x)
            py_list.append(y_part)
            vel_list.append(v_local_total)
            
            p_size = 4 + (v_local_total / 12.0)
            size_list.append(p_size)

    # Desenhar Moléculas de Ar
    fig_draw.add_trace(go.Scatter(
        x=px_list, y=py_list,
        mode='markers',
        marker=dict(
            size=size_list,
            color=vel_list,
            colorscale='Turbo',
            showscale=True,
            colorbar=dict(title="Velocidade (km/h)", len=0.8)
        ),
        name='Moléculas de Ar'
    ))

    # Desenhar Silhueta do Veículo
    fig_draw.add_trace(go.Scatter(
        x=x_carro, y=y_carro,
        fill='toself', fillcolor='rgba(25, 28, 36, 0.95)',
        line=dict(color='#00D2FF', width=3), name='Veículo A'
    ))

    # Rodas
    r_raio = altura_a * 0.22
    x_roda_front = -comprimento_a * 0.3
    x_roda_tras = comprimento_a * 0.3
    theta = np.linspace(0, 2*np.pi, 20)
    
    fig_draw.add_trace(go.Scatter(
        x=x_roda_tras + r_raio*np.cos(theta), y=r_raio + r_raio*np.sin(theta),
        fill='toself', fillcolor='#111', line=dict(color='#555', width=2), showlegend=False
    ))
    fig_draw.add_trace(go.Scatter(
        x=x_roda_front + r_raio*np.cos(theta), y=r_raio + r_raio*np.sin(theta),
        fill='toself', fillcolor='#111', line=dict(color='#555', width=2), showlegend=False
    ))

    # Desenhar Aerofólio (se ativo)
    if usar_aerofolio:
        # Haste de suporte
        fig_draw.add_trace(go.Scatter(
            x=[x_asa_pos, x_asa_pos], y=[y_asa_pos - 0.15*altura_a, y_asa_pos],
            mode='lines', line=dict(color='#AAA', width=3), showlegend=False
        ))
        # Perfil do Aerofólio
        ang = 0.15 + (cl_a * 0.08)
        x_asa_line = [x_asa_pos - 0.2*comprimento_a*0.2, x_asa_pos + 0.2*comprimento_a*0.2]
        y_asa_line = [y_asa_pos - 0.1*altura_a*ang, y_asa_pos + 0.1*altura_a*ang]
        
        fig_draw.add_trace(go.Scatter(
            x=x_asa_line, y=y_asa_line,
            mode='lines', line=dict(color='#FFD700', width=6), name='Aerofólio'
        ))

    # Vetor de Arrasto (Fd)
    vec_scale = 0.002
    fig_draw.add_annotation(
        x=comprimento_a/2 + (fd_a * vec_scale), y=altura_a*0.5, ax=comprimento_a/2, ay=altura_a*0.5,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3, arrowcolor="#FF2A6D",
        text=f"Fd = {fd_a:.0f} N"
    )

    fig_draw.update_layout(
        template="plotly_dark", height=450,
        xaxis=dict(range=[-comprimento_a*1.1, comprimento_a*1.8], title="Comprimento (m)"),
        yaxis=dict(range=[-0.1, altura_a*2.2], title="Altura (m)"),
        showlegend=False
    )
    st.plotly_chart(fig_draw, use_container_width=True)
