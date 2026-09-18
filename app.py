import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA & ESTILIZAÇÃO CSS
# ==========================================
st.set_page_config(
    page_title="Simulador MONSTRO de Aerodinâmica",
    page_icon="👹",
    layout="wide"
)

st.markdown("""
    <style>
    .title-monstro {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #FF4500, #FF8C00, #00E5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .subtitle-text {
        font-size: 1rem;
        color: #94A3B8;
        margin-bottom: 20px;
    }
    div[data-testid="stMetric"] {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        padding: 12px 16px;
        border-radius: 10px;
        color: #F8FAFC;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DADOS DE VEÍCULOS
# ==========================================
CARROS_DATABASE = {
    "Populares & Hatchbacks": {
        "Volkswagen Gol G6": {"cd": 0.34, "area": 2.10, "massa": 1020},
        "Fiat Uno Mille": {"cd": 0.38, "area": 1.95, "massa": 840},
        "Chevrolet Onix": {"cd": 0.33, "area": 2.15, "massa": 1040},
        "Hyundai HB20": {"cd": 0.34, "area": 2.12, "massa": 1030}
    },
    "Sedans & Coupés": {
        "Honda Civic G10": {"cd": 0.27, "area": 2.22, "massa": 1320},
        "Toyota Corolla": {"cd": 0.28, "area": 2.20, "massa": 1375},
        "Tesla Model S": {"cd": 0.208, "area": 2.34, "massa": 2100}
    },
    "Esportivos & Hipercarros": {
        "Porsche 911 Carrera": {"cd": 0.29, "area": 2.07, "massa": 1505},
        "Bugatti Chiron": {"cd": 0.36, "area": 2.07, "massa": 1995},
        "Nissan GT-R R35": {"cd": 0.26, "area": 2.28, "massa": 1750}
    }
}

def gerar_canvas_js(id_canvas, v_relativa_ms, cd, titulo_label, cor_veiculo="#FF4500"):
    return f"""
    <div style="text-align: center; background-color: #0B0F19; padding: 10px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #1E293B;">
        <div style="color: #FF8C00; font-weight: bold; font-family: sans-serif; font-size: 0.9rem; margin-bottom: 6px; text-align: left;">
            {titulo_label}
        </div>
        <canvas id="{id_canvas}" width="750" height="200" style="border: 1px solid #334155; border-radius: 8px; background: #020617;"></canvas>
    </div>
    <script>
        (function() {{
            const canvas = document.getElementById('{id_canvas}');
            const ctx = canvas.getContext('2d');
            const speed = Math.max(0.5, {v_relativa_ms} * 0.18);
            const cd = {cd};
            
            let particles = [];
            for(let i = 0; i < 100; i++) {{
                particles.push({{
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: speed + Math.random() * 2,
                    vy: 0,
                    size: Math.random() * 2 + 1,
                    color: '#00E5FF'
                }});
            }}

            function drawVehicle() {{
                ctx.fillStyle = '{cor_veiculo}';
                ctx.strokeStyle = '#FFFFFF';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(280, 120); ctx.lineTo(330, 120); ctx.lineTo(370, 80);
                ctx.lineTo(450, 80); ctx.lineTo(490, 120); ctx.lineTo(520, 120);
                ctx.lineTo(520, 140); ctx.lineTo(280, 140);
                ctx.fill();
                ctx.stroke();
            }}

            function render() {{
                ctx.fillStyle = 'rgba(2, 6, 23, 0.25)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                drawVehicle();
                
                particles.forEach(p => {{
                    let dx = p.x - 400;
                    let dy = p.y - 110;
                    let dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist < 85) {{
                        let angle = Math.atan2(dy, dx);
                        p.vy += Math.sin(angle) * (cd * 3.0);
                        p.color = '#FF4500';
                    }} else {{
                        p.vy *= 0.90;
                        p.color = '#00E5FF';
                    }}
                    
                    p.x += p.vx;
                    p.y += p.vy;
                    
                    if (p.x > canvas.width) {{
                        p.x = 0;
                        p.y = Math.random() * canvas.height;
                        p.vx = speed + Math.random() * 2;
                        p.vy = 0;
                    }}
                    
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                }});
                
                requestAnimationFrame(render);
            }}
            render();
        }})();
    </script>
    """

# ==========================================
# 3. LAYOUT EM TRÊS COLUNAS
# ==========================================
col_esq, col_centro, col_dir = st.columns([1, 2.2, 1], gap="medium")

# ----------------------------------------------------
# COLUNA ESQUERDA: CLIMA, VENTO RELATIVO E VELOCIDADES
# ----------------------------------------------------
with col_esq:
    st.markdown("### 🌐 Ambiente & Vento")
    st.write("---")
    
    altitude = st.slider("Altitude (m):", 0, 5000, 0, step=100)
    temp_c = st.slider("Temperatura (°C):", -10, 40, 20, step=1)
    
    temp_k = temp_c + 273.15
    p_atm = 101325 * ((1 - 2.25577e-5 * altitude) ** 5.25588)
    rho = p_atm / (287.05 * temp_k)
    
    st.caption(f"🍃 Densidade do Ar ($\rho$): **{rho:.3f} kg/m³**")
        
    st.write("---")
    st.markdown("### 💨 Velocidade Relativa")
    
    v_veiculo_kmh = st.slider("Velocidade do Veículo $V_v$ (km/h):", 0.0, 300.0, 100.0, step=5.0)
    v_vento_kmh = st.slider("Vento de Frente/Cauda $V_w$ (km/h):", -100.0, 100.0, 20.0, step=5.0)
    
    v_relativa_kmh = v_veiculo_kmh + v_vento_kmh
    v_relativa_ms = max(0.0, v_relativa_kmh / 3.6)
    v_veiculo_ms = v_veiculo_kmh / 3.6

    st.write("---")
    st.markdown("### 📐 Fórmula Modificada")
    st.latex(r"F_d = \frac{1}{2} \cdot \rho \cdot (V_v + V_w)^2 \cdot C_d \cdot A")

# ----------------------------------------------------
# COLUNA DIREITA: SELEÇÃO DE MODELOS
# ----------------------------------------------------
with col_dir:
    st.markdown("### 🏎️ Garagem MONSTRO")
    st.write("---")
    
    cat_a = st.selectbox("Categoria (Objeto A):", list(CARROS_DATABASE.keys()), index=0)
    opcoes_a = list(CARROS_DATABASE[cat_a].keys()) + ["🔧 MONSTRO Custom"]
    carro_a_nome = st.selectbox("Veículo A:", opcoes_a, index=0)
    
    if carro_a_nome == "🔧 MONSTRO Custom":
        cd_a = st.number_input("Cd (A):", value=0.320, format="%.3f", step=0.01)
        area_a = st.number_input("Área m² (A):", value=2.20, format="%.2f", step=0.05)
    else:
        dados_a = CARROS_DATABASE[cat_a][carro_a_nome]
        cd_a = dados_a["cd"]
        area_a = dados_a["area"]
        st.info(f"**Specs A:** Cd = `{cd_a}` | Área = `{area_a} m²`")

    st.write("---")
    comparar = st.toggle("🔀 Modo Comparação", value=True)
    
    if comparar:
        cat_b = st.selectbox("Categoria (Objeto B):", list(CARROS_DATABASE.keys()), index=1)
        opcoes_b = list(CARROS_DATABASE[cat_b].keys()) + ["🔧 MONSTRO Custom"]
        carro_b_nome = st.selectbox("Veículo B:", opcoes_b, index=2)
        
        if carro_b_nome == "🔧 MONSTRO Custom":
            cd_b = st.number_input("Cd (B):", value=0.220, format="%.3f", step=0.01)
            area_b = st.number_input("Área m² (B):", value=2.30, format="%.2f", step=0.05)
        else:
            dados_b = CARROS_DATABASE[cat_b][carro_b_nome]
            cd_b = dados_b["cd"]
            area_b = dados_b["area"]
            st.caption(f"**Specs B:** Cd = `{cd_b}` | Área = `{area_b} m²`")

# ----------------------------------------------------
# CÁLCULOS FÍSICOS REAIS
# ----------------------------------------------------
fd_a = 0.5 * rho * (v_relativa_ms ** 2) * cd_a * area_a
pot_w_a = fd_a * v_veiculo_ms
pot_cv_a = pot_w_a / 735.499

if comparar:
    fd_b = 0.5 * rho * (v_relativa_ms ** 2) * cd_b * area_b
    pot_w_b = fd_b * v_veiculo_ms
    pot_cv_b = pot_w_b / 735.499

# ----------------------------------------------------
# COLUNA CENTRAL: TÍTULO COLORIDO E GRÁFICOS
# ----------------------------------------------------
with col_centro:
    st.markdown('<p class="title-monstro">🔥 Simulador MONSTRO de Aerodinâmica</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Análise avançada com componente de vento relativo $V_{relativ} = (V_v + V_w)$.</p>', unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Arrasto Fd (A)", f"{fd_a:.1f} N")
    m2.metric("Potência Requerida (A)", f"{pot_cv_a:.1f} CV")
    m3.metric("Velocidade Relativa", f"{v_relativa_kmh:.0f} km/h", f"{v_relativa_ms:.1f} m/s")
    
    st.write("---")
    
    tab_fd, tab_pot, tab_anim = st.tabs([
        "📈 Arrasto com Vento Relativo", 
        "⚡ Potência do Motor",
        "💨 Túnel de Vento MONSTRO"
    ])

    v_vetor_veiculo_kmh = np.linspace(10, 260, 100)
    v_vetor_relativo_ms = np.maximum(0.0, (v_vetor_veiculo_kmh + v_vento_kmh) / 3.6)

    # ABA 1: FORÇA DE ARRASTO COM FÓRMULA (Vv + Vw)
    with tab_fd:
        fd_vetor_a = 0.5 * rho * (v_vetor_relativo_ms ** 2) * cd_a * area_a
        
        fig_fd = go.Figure()
        fig_fd.add_trace(go.Scatter(
            x=v_vetor_veiculo_kmh, y=fd_vetor_a, mode='lines', name=f'Veículo A: {carro_a_nome}',
            line=dict(color='#FF4500', width=3), fill='tozeroy', fillcolor='rgba(255, 69, 0, 0.15)'
        ))
        fig_fd.add_trace(go.Scatter(
            x=[v_veiculo_kmh], y=[fd_a], mode='markers', name='Ponto Atual (A)',
            marker=dict(color='#FF4500', size=11, symbol='diamond')
        ))

        if comparar:
            fd_vetor_b = 0.5 * rho * (v_vetor_relativo_ms ** 2) * cd_b * area_b
            fig_fd.add_trace(go.Scatter(
                x=v_vetor_veiculo_kmh, y=fd_vetor_b, mode='lines', name=f'Veículo B: {carro_b_nome}',
                line=dict(color='#00E5FF', width=3), fill='tozeroy', fillcolor='rgba(0, 229, 255, 0.12)'
            ))
            fig_fd.add_trace(go.Scatter(
                x=[v_veiculo_kmh], y=[fd_b], mode='markers', name='Ponto Atual (B)',
                marker=dict(color='#00E5FF', size=11, symbol='square')
            ))

        fig_fd.update_layout(
            title=f"Força de Arrasto x Velocidade do Veículo (Vento constante = {v_vento_kmh:.0f} km/h)",
            xaxis_title="Velocidade do Veículo V_v (km/h)", yaxis_title="Força de Arrasto Fd (N)",
            template="plotly_dark", height=420, hovermode="x unified"
        )
        st.plotly_chart(fig_fd, use_container_width=True)

    # ABA 2: POTÊNCIA
    with tab_pot:
        v_vetor_veiculo_ms = v_vetor_veiculo_kmh / 3.6
        pot_vetor_cv_a = (fd_vetor_a * v_vetor_veiculo_ms) / 735.499
        
        fig_pot = go.Figure()
        fig_pot.add_trace(go.Scatter(
            x=v_vetor_veiculo_kmh, y=pot_vetor_cv_a, mode='lines', name=f'Veículo A: {carro_a_nome}',
            line=dict(color='#FF8C00', width=3), fill='tozeroy', fillcolor='rgba(255, 140, 0, 0.15)'
        ))
        fig_pot.add_trace(go.Scatter(
            x=[v_veiculo_kmh], y=[pot_cv_a], mode='markers', name='Ponto Atual (A)',
            marker=dict(color='#FF8C00', size=11)
        ))

        if comparar:
            pot_vetor_cv_b = (fd_vetor_b * v_vetor_veiculo_ms) / 735.499
            fig_pot.add_trace(go.Scatter(
                x=v_vetor_veiculo_kmh, y=pot_vetor_cv_b, mode='lines', name=f'Veículo B: {carro_b_nome}',
                line=dict(color='#10B981', width=3), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.12)'
            ))
            fig_pot.add_trace(go.Scatter(
                x=[v_veiculo_kmh], y=[pot_cv_b], mode='markers', name='Ponto Atual (B)',
                marker=dict(color='#10B981', size=11)
            ))

        fig_pot.update_layout(
            title="Potência do Motor Requerida para Vencer o Arrasto (CV)",
            xaxis_title="Velocidade do Veículo V_v (km/h)", yaxis_title="Potência Requerida (CV)",
            template="plotly_dark", height=420, hovermode="x unified"
        )
        st.plotly_chart(fig_pot, use_container_width=True)

    # ABA 3: TÚNEL DE VENTO MONSTRO
    with tab_anim:
        st.markdown("##### Visualização Dinâmica do Vento Relativo $(V_v + V_w)$")
        html_code_a = gerar_canvas_js("canvas_a", v_relativa_ms, cd_a, f"🔥 Veículo A: {carro_a_nome}", "#FF4500")
        
        if comparar:
            html_code_b = gerar_canvas_js("canvas_b", v_relativa_ms, cd_b, f"⚡ Veículo B: {carro_b_nome}", "#00E5FF")
            components.html(html_code_a + html_code_b, height=500)
        else:
            components.html(html_code_a, height=250)
