import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import time

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Simulador de Aerodinâmica & Consumo",
    page_icon="🏎️",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00D2FF, #FF2A6D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Presets de Veículos Terrestres
PRESETS_VEICULOS = {
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2, "massa": 1100.0, "potencia_cv": 100.0, "comprimento": 4.0, "tipo": "hatch"},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9, "massa": 1400.0, "potencia_cv": 450.0, "comprimento": 4.5, "tipo": "esportivo"},
    "SUV / Caminhonete": {"cd": 0.40, "area": 2.8, "massa": 1900.0, "potencia_cv": 180.0, "comprimento": 4.8, "tipo": "suv"},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0, "massa": 12000.0, "potencia_cv": 400.0, "comprimento": 12.0, "tipo": "caminhao"},
    "Ciclista em Pé": {"cd": 0.90, "area": 0.6, "massa": 85.0, "potencia_cv": 0.4, "comprimento": 1.5, "tipo": "ciclista"}
}

CIDADES_ALTITUDE = {
    "Personalizado": None,
    "Nível do Mar (0 m)": 0,
    "São Paulo / Curitiba (~800 m)": 800,
    "Cidade do México (~2240 m)": 2240,
    "La Paz - Bolívia (~3640 m)": 3640
}

# FUNÇÃO PARA GERAR A SILHUETA MÁTRICA DE CADA MODELO DE VEÍCULO
def gerar_silhueta_veiculo(tipo, comprimento, altura):
    L = comprimento
    H = altura
    
    if tipo == "esportivo":
        x = np.array([-0.50, -0.48, -0.35, -0.10,  0.15,  0.40,  0.48,  0.50,  0.50, -0.50]) * L
        y = np.array([ 0.15,  0.30,  0.40,  0.95,  0.85,  0.50,  0.35,  0.15,  0.00,  0.00]) * H
    elif tipo == "suv":
        x = np.array([-0.50, -0.48, -0.38, -0.18,  0.25,  0.45,  0.48,  0.50,  0.50, -0.50]) * L
        y = np.array([ 0.15,  0.55,  0.60,  0.98,  0.98,  0.90,  0.35,  0.15,  0.00,  0.00]) * H
    elif tipo == "caminhao":
        x = np.array([-0.50, -0.49, -0.48,  0.48,  0.49,  0.50,  0.50, -0.50]) * L
        y = np.array([ 0.10,  0.95,  0.98,  0.98,  0.95,  0.10,  0.00,  0.00]) * H
    elif tipo == "ciclista":
        x = np.array([-0.40, -0.30, -0.15,  0.05,  0.25,  0.35,  0.25,  0.00, -0.25, -0.40]) * L
        y = np.array([ 0.30,  0.70,  0.95,  0.85,  0.60,  0.25,  0.05,  0.05,  0.05,  0.30]) * H
    else:  # Hatch / Sedan
        x = np.array([-0.50, -0.47, -0.32, -0.12,  0.20,  0.38,  0.47,  0.50,  0.50, -0.50]) * L
        y = np.array([ 0.15,  0.45,  0.52,  0.96,  0.94,  0.60,  0.30,  0.15,  0.00,  0.00]) * H
        
    return x, y

def carregar_preset_a():
    sel = st.session_state.preset_select_a
    if sel in PRESETS_VEICULOS:
        p = PRESETS_VEICULOS[sel]
        st.session_state.cd_a = float(p["cd"])
        st.session_state.area_a = float(p["area"])
        st.session_state.m_a = float(p["massa"])
        st.session_state.p_a = float(p["potencia_cv"])
        st.session_state.comp_a = float(p["comprimento"])

def carregar_preset_b():
    sel = st.session_state.preset_select_b
    if sel in PRESETS_VEICULOS:
        p = PRESETS_VEICULOS[sel]
        st.session_state.cd_b = float(p["cd"])
        st.session_state.area_b = float(p["area"])
        st.session_state.m_b = float(p["massa"])
        st.session_state.p_b = float(p["potencia_cv"])
        st.session_state.comp_b = float(p["comprimento"])

# Initializer do Estado de Animação
if "animando" not in st.session_state:
    st.session_state.animando = False
if "fase_anim" not in st.session_state:
    st.session_state.fase_anim = 0.0

# ==========================================
# BARRA LATERAL: PARÂMETROS AMBIENTAIS & OPERAÇÃO
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configurações do Teste")
    st.write("---")
    
    st.markdown("**🏔️ Altitude & Atmosfera**")
    cidade_preset = st.selectbox("Presets de Altitude:", list(CIDADES_ALTITUDE.keys()), index=0, key="select_cidade_alt")
    
    is_custom = (cidade_preset == "Personalizado")
    if not is_custom:
        val_alt = CIDADES_ALTITUDE[cidade_preset]
        altitude = st.slider("Altitude (m)", 0, 5000, val_alt, 100, disabled=True, key="slider_altitude_preset")
    else:
        altitude = st.slider("Altitude Personalizada (m)", 0, 5000, 0, 100, disabled=False, key="slider_altitude_custom")
    
    temp_c = st.slider("Temperatura do Ar (°C)", -10, 50, 20, 1, key="slider_temp")
    
    # Cálculo da densidade do ar
    temp_k = temp_c + 273.15
    p_atm = 101325 * np.exp(-altitude / 8500)
    rho = p_atm / (287.058 * temp_k)
    st.caption(f"💡 Densidade do Ar ($\rho$): **{rho:.3f} kg/m³**")

    st.write("---")
    st.markdown("**⛽ Combustível & Motor**")
    preco_comb = st.number_input("Preço do Combustível (R$/L):", value=5.80, step=0.10, key="input_preco_comb")
    eficiencia_motor = st.slider("Eficiência Térmica do Motor (%)", 15, 45, 30, key="slider_efic_comb") / 100.0

    st.write("---")
    v_kmh = st.slider("Velocidade do Veículo (km/h)", 10.0, 220.0, 110.0, 5.0, key="slider_v_kmh")
    v_vento_kmh = st.slider("Vento Frontal (+Contra / -Favor) (km/h)", -40.0, 40.0, 0.0, 5.0, key="slider_v_vento")

    st.write("---")
    comparar = st.toggle("🔀 Modo Comparativo (Objeto B)", value=False, key="toggle_comparar")

# ==========================================
# COLUNAS DA INTERFACE PRINCIPAL
# ==========================================
col_centro, col_direita = st.columns([2.2, 1], gap="medium")

# Session State Initializer
if "cd_a" not in st.session_state:
    p_init = list(PRESETS_VEICULOS.values())[0]
    st.session_state.cd_a = float(p_init["cd"])
    st.session_state.area_a = float(p_init["area"])
    st.session_state.m_a = float(p_init["massa"])
    st.session_state.p_a = float(p_init["potencia_cv"])
    st.session_state.comp_a = float(p_init["comprimento"])

if "cd_b" not in st.session_state:
    p_init_b = list(PRESETS_VEICULOS.values())[1]
    st.session_state.cd_b = float(p_init_b["cd"])
    st.session_state.area_b = float(p_init_b["area"])
    st.session_state.m_b = float(p_init_b["massa"])
    st.session_state.p_b = float(p_init_b["potencia_cv"])
    st.session_state.comp_b = float(p_init_b["comprimento"])

# ==========================================
# COLUNA DIREITA: AJUSTES DOS OBJETOS
# ==========================================
with col_direita:
    st.markdown("### 📐 Geometria do Veículo")
    
    with st.expander("🔵 **Objeto A (Referência)**", expanded=True):
        modelo_a = st.selectbox("Modelo Base:", list(PRESETS_VEICULOS.keys()), key="preset_select_a", on_change=carregar_preset_a)
        
        cd_a = st.slider("C_d (Coef. de Arrasto):", 0.15, 1.20, st.session_state.cd_a, 0.01, key="cd_a")
        area_a = st.slider("Área Frontal (m²):", 0.5, 10.0, st.session_state.area_a, 0.1, key="area_a")
        massa_a = st.number_input("Massa (kg):", value=st.session_state.m_a, step=50.0, key="m_a")
        potencia_cv_a = st.number_input("Potência Motor (CV):", value=st.session_state.p_a, step=10.0, key="p_a")
        comprimento_a = st.number_input("Comprimento (m):", value=st.session_state.comp_a, step=0.5, key="comp_a")
        
        usar_aerofolio = st.checkbox("➕ Adicionar Aerofólio", key="check_asa_a")
        if usar_aerofolio:
            cl_a = st.slider("C_L (Downforce):", 0.1, 2.0, 0.8, 0.1, key="cl_asa_a")
            area_asa_a = st.slider("Área da Asa (m²):", 0.1, 2.0, 0.4, 0.1, key="area_asa_a")
            cd_induzido_asa_a = (cl_a ** 2) / (np.pi * 3.5)
        else:
            cl_a, area_asa_a, cd_induzido_asa_a = 0.0, 0.0, 0.0

    if comparar:
        with st.expander("🔴 **Objeto B (Comparativo)**", expanded=False):
            modelo_b = st.selectbox("Modelo Base:", list(PRESETS_VEICULOS.keys()), key="preset_select_b", on_change=carregar_preset_b)
            
            cd_b = st.slider("C_d (Coef. de Arrasto):", 0.15, 1.20, st.session_state.cd_b, 0.01, key="cd_b")
            area_b = st.slider("Área Frontal (m²):", 0.5, 10.0, st.session_state.area_b, 0.1, key="area_b")
            massa_b = st.number_input("Massa (kg):", value=st.session_state.m_b, step=50.0, key="m_b")
            potencia_cv_b = st.number_input("Potência Motor (CV):", value=st.session_state.p_b, step=10.0, key="p_b")
            comprimento_b = st.number_input("Comprimento (m):", value=st.session_state.comp_b, step=0.5, key="comp_b")
            cl_b, area_asa_b, cd_induzido_asa_b = 0.0, 0.0, 0.0

# ==========================================
# CÁLCULOS FÍSICOS
# ==========================================
v_efetiva_ms = max(0.0, v_kmh + v_vento_kmh) / 3.6
v_propria_ms = v_kmh / 3.6
crr = 0.012

# Objeto A
fd_corpo_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_a * area_a
fd_asa_a = 0.5 * rho * (v_efetiva_ms ** 2) * cd_induzido_asa_a * area_asa_a if usar_aerofolio else 0.0
fd_a = fd_corpo_a + fd_asa_a

f_rol_a = crr * massa_a * 9.81
f_total_a = fd_a + f_rol_a

pot_watts_a = f_total_a * v_propria_ms
pot_cv_a = pot_watts_a / 735.5

downforce_a = 0.5 * rho * (v_efetiva_ms ** 2) * cl_a * area_asa_a

consumo_l_h_a = (pot_watts_a / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
consumo_1km_a = (consumo_l_h_a / v_kmh) if v_kmh > 0 else 0
custo_1km_a = consumo_1km_a * preco_comb

# Objeto B (se ativo)
if comparar:
    fd_b = 0.5 * rho * (v_efetiva_ms ** 2) * cd_b * area_b
    f_rol_b = crr * massa_b * 9.81
    f_total_b = fd_b + f_rol_b
    pot_watts_b = f_total_b * v_propria_ms
    pot_cv_b = pot_watts_b / 735.5
    consumo_l_h_b = (pot_watts_b / eficiencia_motor) / (32e6 / 3600) if v_kmh > 0 else 0
    consumo_1km_b = (consumo_l_h_b / v_kmh) if v_kmh > 0 else 0
    custo_1km_b = consumo_1km_b * preco_comb

# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
with col_centro:
    st.markdown('<p class="main-title">🏎️ Simulador Aerodinâmico de Veículos</p>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Força de Arrasto (Fd)", f"{fd_a:.1f} N")
    m2.metric("Potência Exigida", f"{pot_cv_a:.1f} CV")
    m3.metric("Consumo Estimado", f"{consumo_1km_a * 100:.2f} L/100km")
    m4.metric("Custo p/ 1 km", f"R$ {custo_1km_a:.2f}")

    st.write("---")
    
    tab_grafico, tab_desenho, tab_pie = st.tabs([
        "📊 Curvas de Desempenho", 
        "🌀 Túnel de Vento & Termodinâmica", 
        "⚖️ Divisão das Forças"
    ])

    # TAB 1: CURVAS DE DESEMPENHO
    with tab_grafico:
        opcao_grafico = st.radio("Métrica a exibir:", ["Força de Arrasto (N)", "Potência Necessária (CV)", "Custo (R$/km)"], horizontal=True)
        
        v_vec = np.linspace(10, 220, 100)
        v_vec_ef = np.maximum(0.1, v_vec + v_vento_kmh) / 3.6
        v_vec_ms = v_vec / 3.6
        
        fd_vec_a = (0.5 * rho * (v_vec_ef ** 2) * cd_a * area_a) + (0.5 * rho * (v_vec_ef ** 2) * cd_induzido_asa_a * area_asa_a if usar_aerofolio else 0.0)
        f_tot_vec_a = fd_vec_a + f_rol_a
        pot_vec_cv_a = (f_tot_vec_a * v_vec_ms) / 735.5
        cons_vec_a = (((f_tot_vec_a * v_vec_ms) / eficiencia_motor) / (32e6 / 3600) / np.maximum(1.0, v_vec)) * preco_comb

        if opcao_grafico == "Força de Arrasto (N)":
            y_a, y_p_a, title_y = fd_vec_a, fd_a, "Força de Arrasto (N)"
        elif opcao_grafico == "Potência Necessária (CV)":
            y_a, y_p_a, title_y = pot_vec_cv_a, pot_cv_a, "Potência Requerida (CV)"
        else:
            y_a, y_p_a, title_y = cons_vec_a, custo_1km_a, "Custo (R$ / km)"

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=v_vec, y=y_a, mode='lines', name='Objeto A', line=dict(color='#00D2FF', width=3)))
        fig.add_trace(go.Scatter(x=[v_kmh], y=[y_p_a], mode='markers', name='Ponto Atual A', marker=dict(color='#00D2FF', size=10)))

        if comparar:
            fd_vec_b = 0.5 * rho * (v_vec_ef ** 2) * cd_b * area_b
            f_tot_vec_b = fd_vec_b + f_rol_b
            pot_vec_cv_b = (f_tot_vec_b * v_vec_ms) / 735.5
            cons_vec_b = (((f_tot_vec_b * v_vec_ms) / eficiencia_motor) / (32e6 / 3600) / np.maximum(1.0, v_vec)) * preco_comb

            y_b = fd_vec_b if opcao_grafico == "Força de Arrasto (N)" else (pot_vec_cv_b if opcao_grafico == "Potência Necessária (CV)" else cons_vec_b)
            y_p_b = fd_b if opcao_grafico == "Força de Arrasto (N)" else (pot_cv_b if opcao_grafico == "Potência Necessária (CV)" else custo_1km_b)

            fig.add_trace(go.Scatter(x=v_vec, y=y_b, mode='lines', name='Objeto B', line=dict(color='#FF2A6D', width=3)))
            fig.add_trace(go.Scatter(x=[v_kmh], y=[y_p_b], mode='markers', name='Ponto Atual B', marker=dict(color='#FF2A6D', size=10)))

        fig.update_layout(xaxis_title="Velocidade (km/h)", yaxis_title=title_y, template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: TÚNEL DE VENTO COM ANIMAÇÃO DE FLUXO E AEROFOIL INTERATIVO
    with tab_desenho:
        col_head, col_btn = st.columns([3, 1])
        with col_head:
            st.markdown("#### 🌀 Fluxo Contínuo de Moléculas no Túnel de Vento")
            st.caption(f"🌡️ **{temp_c}°C** ($\rho$: **{rho:.3f} kg/m³**) | 💨 Fluxo: **{v_efetiva_ms*3.6:.1f} km/h**")
        with col_btn:
            if st.button("▶️ Alternar Animação" if not st.session_state.animando else "⏸️ Pausar Animação"):
                st.session_state.animando = not st.session_state.animando
        
        container_grafico = st.empty()

        def desenhar_tunel(offset_x=0.0):
            fig_draw = go.Figure()
            
            tipo_veiculo_a = PRESETS_VEICULOS[modelo_a]["tipo"]
            altura_a = np.sqrt(area_a) * 0.95
            x_carro, y_carro = gerar_silhueta_veiculo(tipo_veiculo_a, comprimento_a, altura_a)
            
            x_asa_pos = comprimento_a * 0.38
            y_asa_pos = altura_a * 0.82
            
            num_linhas = int(np.clip(14 + (rho - 0.8) * 20, 10, 30))
            pts_por_linha = 48
            
            # Grid que se move para a direita (efeito contínuo)
            x_min, x_max = -comprimento_a * 1.2, comprimento_a * 2.0
            largura_grid = x_max - x_min
            
            x_grid_base = np.linspace(x_min, x_max, pts_por_linha)
            y_iniciais = np.linspace(-altura_a * 0.3, altura_a * 2.6, num_linhas)
            
            px_list, py_list, vel_list, size_list = [], [], [], []
            R_eff = altura_a * (0.8 + cd_a * 0.4)
            
            for y0 in y_iniciais:
                for x_raw in x_grid_base:
                    # Deslocamento animado com módulo para repetir o fluxo
                    x = x_min + ((x_raw - x_min + offset_x) % largura_grid)
                    
                    r2_carro = x**2 + (y0 - altura_a*0.5)**2
                    dy_carro = (R_eff**2 * max(0.1, y0)) / max(r2_carro, R_eff**1.8) * np.exp(-((x + comprimento_a*0.1) / (comprimento_a*0.7))**2)
                    
                    dy_asa = 0.0
                    v_boost_asa = 0.0
                    
                    if usar_aerofolio:
                        dist_asa_sq = (x - x_asa_pos)**2 + (y0 - y_asa_pos)**2
                        fator_alcance = np.exp(-dist_asa_sq / (0.35 * comprimento_a))
                        dy_asa = (cl_a * 0.45) * fator_alcance
                        v_boost_asa = (cl_a * 35.0) * fator_alcance

                    y_part = max(0.02, y0 + dy_carro + dy_asa)
                    
                    v_relativa = v_efetiva_ms * (1.0 - (R_eff**2 * (x**2 - (y0-altura_a*0.5)**2)) / max(r2_carro**2, R_eff**3.5))
                    v_local_total = abs(v_relativa) * 3.6 + v_boost_asa
                    
                    px_list.append(x)
                    py_list.append(y_part)
                    vel_list.append(v_local_total)
                    size_list.append(4 + (v_local_total / 12.0))

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

            # Aerofólio (se ativado)
            if usar_aerofolio:
                fig_draw.add_trace(go.Scatter(
                    x=[x_asa_pos, x_asa_pos], y=[y_asa_pos - 0.15*altura_a, y_asa_pos],
                    mode='lines', line=dict(color='#888', width=3), showlegend=False
                ))
                ang = 0.15 + (cl_a * 0.08)
                x_asa_line = [x_asa_pos - 0.2*comprimento_a*0.2, x_asa_pos + 0.2*comprimento_a*0.2]
                y_asa_line = [y_asa_pos - 0.1*altura_a*ang, y_asa_pos + 0.1*altura_a*ang]
                fig_draw.add_trace(go.Scatter(
                    x=x_asa_line, y=y_asa_line,
                    mode='lines', line=dict(color='#FFD700', width=6), name='Aerofólio'
                ))

            # Vetor de Arrasto
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
            return fig_draw

        # Renderização com Animação Continuada
        if st.session_state.animando:
            # Passo proporcional à velocidade configurada
            passo = max(0.1, v_efetiva_ms * 0.02)
            st.session_state.fase_anim += passo
            fig_frame = desenhar_tunel(st.session_state.fase_anim)
            container_grafico.plotly_chart(fig_frame, use_container_width=True)
            time.sleep(0.04)
            st.rerun()
        else:
            fig_estatico = desenhar_tunel(st.session_state.fase_anim)
            container_grafico.plotly_chart(fig_estatico, use_container_width=True)

    # TAB 3: DIVISÃO DE RESISTÊNCIAS
    with tab_pie:
        st.markdown("#### ⚖️ Arrasto Aerodinâmico vs. Pneu (Rolamento)")
        pct_arrasto = (fd_a / f_total_a) * 100 if f_total_a > 0 else 100
        pct_rolamento = (f_rol_a / f_total_a) * 100 if f_total_a > 0 else 0
        
        fig_pie = px.pie(
            values=[pct_arrasto, pct_rolamento],
            names=['Arrasto Aerodinâmico ($F_d$)', 'Resistência de Rolamento ($F_{rol}$)'],
            color_discrete_sequence=['#00D2FF', '#FF2A6D'],
            height=300
        )
        st.plotly_chart(fig_pie, use_container_width=True)
