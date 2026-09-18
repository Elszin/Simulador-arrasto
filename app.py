import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA & ESTILIZAÇÃO CSS
# ==========================================
st.set_page_config(
    page_title="Simulador de Aerodinâmica - Modelos de Carros",
    page_icon="🚗",
    layout="wide"
)

st.markdown("""
    <style>
    .title-text {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0px;
    }
    .subtitle-text {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 15px;
    }
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 10px 14px;
        border-radius: 8px;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DADOS COMPLETA DE CARROS
# ==========================================
CARROS_DATABASE = {
    "Populares & Hatchbacks": {
        "Volkswagen Gol G6": {"cd": 0.34, "area": 2.10, "massa": 1020},
        "Fiat Uno Mille": {"cd": 0.38, "area": 1.95, "massa": 840},
        "Chevrolet Onix": {"cd": 0.33, "area": 2.15, "massa": 1040},
        "Hyundai HB20": {"cd": 0.34, "area": 2.12, "massa": 1030},
        "Toyota Yaris Hatch": {"cd": 0.30, "area": 2.14, "massa": 1125}
    },
    "Sedans & Coupés": {
        "Honda Civic G10": {"cd": 0.27, "area": 2.22, "massa": 1320},
        "Toyota Corolla": {"cd": 0.28, "area": 2.20, "massa": 1375},
        "Tesla Model S": {"cd": 0.208, "area": 2.34, "massa": 2100},
        "Mercedes-Benz CLA": {"cd": 0.23, "area": 2.21, "massa": 1430},
        "BMW Série 3 (G20)": {"cd": 0.26, "area": 2.23, "massa": 1525}
    },
    "SUVs & Pickups": {
        "Jeep Renegade": {"cd": 0.37, "area": 2.50, "massa": 1448},
        "Toyota Hilux": {"cd": 0.44, "area": 2.85, "massa": 2090},
        "Ford Ranger": {"cd": 0.40, "area": 2.90, "massa": 2210},
        "Porsche Macan": {"cd": 0.35, "area": 2.45, "massa": 1845},
        "Tesla Cybertruck": {"cd": 0.34, "area": 3.10, "massa": 3000}
    },
    "Esportivos & Hipercarros": {
        "Porsche 911 Carrera (992)": {"cd": 0.29, "area": 2.07, "massa": 1505},
        "Ferrari 488 GTB": {"cd": 0.32, "area": 2.00, "massa": 1370},
        "Bugatti Chiron": {"cd": 0.36, "area": 2.07, "massa": 1995},
        "McLaren Senna (Foco em Downforce)": {"cd": 0.45, "area": 1.98, "massa": 1198},
        "Nissan GT-R R35": {"cd": 0.26, "area": 2.28, "massa": 1750}
    },
    "Clássicos & Ícones": {
        "Volkswagen Fusca": {"cd": 0.48, "area": 1.80, "massa": 800},
        "Chevrolet Opala": {"cd": 0.45, "area": 2.10, "massa": 1250},
        "Fiat 147": {"cd": 0.49, "area": 1.75, "massa": 790},
        "Ferrari F40": {"cd": 0.34, "area": 1.90, "massa": 1250}
    }
}

def gerar_canvas_js(id_canvas, v_ms, cd, titulo_label, cor_veiculo="#0284C7"):
    return f"""
    <div style="text-align: center; background-color: #0F172A; padding: 8px; border-radius: 10px; margin-bottom: 12px;">
        <div style="color: #F8FAFC; font-weight: bold; font-family: sans-serif; font-size: 0.85rem; margin-bottom: 4px; text-align: left; padding-left: 5px;">
            {titulo_label}
        </div>
        <canvas id="{id_canvas}" width="750" height="200" style="border: 1px solid #334155; border-radius: 8px; background: #020617;"></canvas>
    </div>
    <script>
        (function() {{
            const canvas = document.getElementById('{id_canvas}');
            const ctx = canvas.getContext('2d');
            const speed = {v_ms} * 0.18;
            const cd = {cd};
            
            let particles = [];
            for(let i = 0; i < 90; i++) {{
                particles.push({{
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: speed + Math.random() * 2,
                    vy: 0,
                    size: Math.random() * 2 + 1,
                    color: '#38BDF8'
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
                    
                    if (dist < 80) {{
                        let angle = Math.atan2(dy, dx);
                        p.vy += Math.sin(angle) * (cd * 2.5);
                        p.color = '#FBBF24';
                    }} else {{
                        p.vy *= 0.92;
                        p.color = '#38BDF8';
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
# COLUNA ESQUERDA: PARÂMETROS AMBIENTAIS
# ----------------------------------------------------
with col_esq:
    st.markdown("### 🌐 Ambiente & Clima")
    st.write("---")
    
    altitude = st.slider("Altitude (m):", 0, 5000, 0, step=100)
    temp_c = st.slider("Temperatura do Ar (°C):", -10, 40, 20, step=1)
    
    temp_k = temp_c + 273.15
    p_atm = 101325 * ((1 - 2.25577e-5 * altitude) ** 5.25588)
    rho = p_atm / (287.05 * temp_k)
    
    st.caption(f"🍃 Densidade do Ar ($\rho$): **{rho:.3f} kg/m³**")
    st.caption(f"🌡️ Pressão Atmosférica: **{p_atm/100:.1f} hPa**")
        
    st.write("---")
    st.markdown("### ⏱️ Teste de Velocidade")
    v_kmh = st.slider("Velocidade do Carro (km/h):", 10.0, 300.0, 110.0, step=5.0)
    v_ms = v_kmh / 3.6

# ----------------------------------------------------
# COLUNA DIREITA: SELEÇÃO DE MODELOS DE CARROS
# ----------------------------------------------------
with col_dir:
    st.markdown("### 🚗 Garagem & Modelos")
    st.write("---")
    
    cat_a = st.selectbox("Categoria (Carro A):", list(CARROS_DATABASE.keys()), index=0)
    opcoes_a = list(CARROS_DATABASE[cat_a].keys()) + ["🔧 Personalizado"]
    carro_a_nome = st.selectbox("Modelo Principal (Carro A):", opcoes_a, index=0)
    
    if carro_a_nome == "🔧 Personalizado":
        cd_a = st.number_input("Cd (Carro A):", value=0.300, format="%.3f", step=0.01)
        area_a = st.number_input("Área Frontal m² (Carro A):", value=2.10, format="%.2f", step=0.05)
        massa_a = st.number_input("Massa kg (Carro A):", value=1100, step=50)
    else:
        dados_a = CARROS_DATABASE[cat_a][carro_a_nome]
        cd_a = dados_a["cd"]
        area_a = dados_a["area"]
        massa_a = dados_a["massa"]
        st.info(f"**Specs A:** Cd = `{cd_a}` | Área = `{area_a} m²` | `{massa_a} kg`")

    st.write("---")
    comparar = st.toggle("🔀 Comparar com outro Carro", value=True)
    
    if comparar:
        cat_b = st.selectbox("Categoria (Carro B):", list(CARROS_DATABASE.keys()), index=1)
        opcoes_b = list(CARROS_DATABASE[cat_b].keys()) + ["🔧 Personalizado"]
        carro_b_nome = st.selectbox("Modelo Secundário (Carro B):", opcoes_b, index=2)
        
        if carro_b_nome == "🔧 Personalizado":
            cd_b = st.number_input("Cd (Carro B):", value=0.250, format="%.3f", step=0.01)
            area_b = st.number_input("Área Frontal m² (Carro B):", value=2.20, format="%.2f", step=0.05)
            massa_b = st.number_input("Massa kg (Carro B):", value=1500, step=50)
        else:
            dados_b = CARROS_DATABASE[cat_b][carro_b_nome]
            cd_b = dados_b["cd"]
            area_b = dados_b["area"]
            massa_b = dados_b["massa"]
            st.caption(f"**Specs B:** Cd = `{cd_b}` | Área = `{area_b} m²` | `{massa_b} kg`")

# ----------------------------------------------------
# CÁLCULOS FÍSICOS
# ----------------------------------------------------
fd_a = 0.5 * rho * (v_ms ** 2) * cd_a * area_a
pot_w_a = fd_a * v_ms
pot_cv_a = pot_w_a / 735.499

if comparar:
    fd_b = 0.5 * rho * (v_ms ** 2) * cd_b * area_b
    pot_w_b = fd_b * v_ms
    pot_cv_b = pot_w_b / 735.499

# ----------------------------------------------------
# COLUNA CENTRAL: RESULTADOS E VISUALIZAÇÃO
# ----------------------------------------------------
with col_centro:
    st.markdown('<p class="title-text">🏎️ Simulador de Aerodinâmica Automotiva</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Compare a resistência do ar e a potência consumida por diversos modelos de carros reais.</p>', unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Arrasto Carro A", f"{fd_a:.1f} N")
    m2.metric("Potência Exigida (A)", f"{pot_cv_a:.1f} CV", f"{pot_w_a/1000:.1f} kW")
    m3.metric("Velocidade", f"{v_kmh:.0f} km/h", f"{v_ms:.1f} m/s")
    
    st.write("---")
    
    tab_fd, tab_pot, tab_anim, tab_dados = st.tabs([
        "📈 Força de Arrasto (N)", 
        "⚡ Potência Necessária (CV)",
        "💨 Túnel de Vento",
        "📋 Tabela Comparativa"
    ])

    v_vetor_kmh = np.linspace(10, 260, 100)
    v_vetor_ms = v_vetor_kmh / 3.6

    # ABA 1: FORÇA DE ARRASTO
    with tab_fd:
        fd_vetor_a = 0.5 * rho * (v_vetor_ms ** 2) * cd_a * area_a
        
        fig_fd = go.Figure()
        fig_fd.add_trace(go.Scatter(
            x=v_vetor_kmh, y=fd_vetor_a, mode='lines', name=f'Carro A: {carro_a_nome}',
            line=dict(color='#0284C7', width=3), fill='tozeroy', fillcolor='rgba(2, 132, 199, 0.12)'
        ))
        fig_fd.add_trace(go.Scatter(
            x=[v_kmh], y=[fd_a], mode='markers', name='Atual (A)',
            marker=dict(color='#0284C7', size=10)
        ))

        if comparar:
            fd_vetor_b = 0.5 * rho * (v_vetor_ms ** 2) * cd_b * area_b
            fig_fd.add_trace(go.Scatter(
                x=v_vetor_kmh, y=fd_vetor_b, mode='lines', name=f'Carro B: {carro_b_nome}',
                line=dict(color='#E11D48', width=3), fill='tozeroy', fillcolor='rgba(225, 29, 72, 0.10)'
            ))
            fig_fd.add_trace(go.Scatter(
                x=[v_kmh], y=[fd_b], mode='markers', name='Atual (B)',
                marker=dict(color='#E11D48', size=10)
            ))

        fig_fd.update_layout(
            title="Força de Arrasto x Velocidade ($F_d$ em Newtons)",
            xaxis_title="Velocidade (km/h)", yaxis_title="Força de Arrasto (N)",
            template="plotly_white", height=400, hovermode="x unified"
        )
        st.plotly_chart(fig_fd, use_container_width=True)

    # ABA 2: POTÊNCIA REQUERIDA
    with tab_pot:
        pot_vetor_cv_a = (fd_vetor_a * v_vetor_ms) / 735.499
        
        fig_pot = go.Figure()
        fig_pot.add_trace(go.Scatter(
            x=v_vetor_kmh, y=pot_vetor_cv_a, mode='lines', name=f'Carro A: {carro_a_nome}',
            line=dict(color='#0D9488', width=3), fill='tozeroy', fillcolor='rgba(13, 148, 136, 0.12)'
        ))
        fig_pot.add_trace(go.Scatter(
            x=[v_kmh], y=[pot_cv_a], mode='markers', name='Atual (A)',
            marker=dict(color='#0D9488', size=10)
        ))

        if comparar:
            pot_vetor_cv_b = (fd_vetor_b * v_vetor_ms) / 735.499
            fig_pot.add_trace(go.Scatter(
                x=v_vetor_kmh, y=pot_vetor_cv_b, mode='lines', name=f'Carro B: {carro_b_nome}',
                line=dict(color='#D97706', width=3), fill='tozeroy', fillcolor='rgba(217, 119, 6, 0.10)'
            ))
            fig_pot.add_trace(go.Scatter(
                x=[v_kmh], y=[pot_cv_b], mode='markers', name='Atual (B)',
                marker=dict(color='#D97706', size=10)
            ))

        fig_pot.update_layout(
            title="Potência Requerida do Motor Apenas para Vencer o Ar (CV)",
            xaxis_title="Velocidade (km/h)", yaxis_title="Potência Necessária (CV)",
            template="plotly_white", height=400, hovermode="x unified"
        )
        st.plotly_chart(fig_pot, use_container_width=True)

    # ABA 3: TÚNEL DE VENTO
    with tab_anim:
        st.markdown("##### Simulação do Fluxo Aerodinâmico")
        html_code_a = gerar_canvas_js("canvas_a", v_ms, cd_a, f"🚘 Carro A: {carro_a_nome}", "#0284C7")
        
        if comparar:
            html_code_b = gerar_canvas_js("canvas_b", v_ms, cd_b, f"🚘 Carro B: {carro_b_nome}", "#E11D48")
            components.html(html_code_a + html_code_b, height=500)
        else:
            components.html(html_code_a, height=250)

    # ABA 4: TABELA COMPARATIVA
    with tab_dados:
        st.markdown("##### Tabela de Comparação em Diferentes Velocidades")
        
        v_pts = np.array([60, 80, 100, 120, 140, 180, 220])
        v_pts_ms = v_pts / 3.6
        
        fd_pts_a = 0.5 * rho * (v_pts_ms ** 2) * cd_a * area_a
        pot_pts_cv_a = (fd_pts_a * v_pts_ms) / 735.499
        
        df_dados = pd.DataFrame({
            "Velocidade (km/h)": v_pts,
            f"Arrasto - {carro_a_nome} (N)": np.round(fd_pts_a, 1),
            f"Potência - {carro_a_nome} (CV)": np.round(pot_pts_cv_a, 1)
        })
        
        if comparar:
            fd_pts_b = 0.5 * rho * (v_pts_ms ** 2) * cd_b * area_b
            pot_pts_cv_b = (fd_pts_b * v_pts_ms) / 735.499
            df_dados[f"Arrasto - {carro_b_nome} (N)"] = np.round(fd_pts_b, 1)
            df_dados[f"Potência - {carro_b_nome} (CV)"] = np.round(pot_pts_cv_b, 1)
            df_dados["Diferença de Arrasto (N)"] = np.round(fd_pts_a - fd_pts_b, 1)
            
        st.dataframe(df_dados, use_container_width=True, hide_index=True)
