import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA & ESTILIZAÇÃO CSS
# ==========================================
st.set_page_config(
    page_title="Simulador de Aerodinâmica & Arrasto Fluido",
    page_icon="⚡",
    layout="wide"
)

# Estilização CSS personalizada para um visual limpo e profissional
st.markdown("""
    <style>
    /* Estilo do título principal */
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
    /* Estilização dos cards de métricas */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 10px 14px;
        border-radius: 8px;
    }
    /* Container ajustado para o layout de 3 colunas */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DADOS REALISTA (PRESETS FIXOS)
# ==========================================
# Valores físicos reais de coeficiente de arrasto (Cd) e área frontal (m²)
VEICULOS_PRESETS = {
    "Terrestres": {
        "Volkswagen Gol G6 (Carro Popular)": {"cd": 0.34, "area": 2.10, "tipo": "terrestre", "fixo": True},
        "Tesla Model S (Sedan Aerodinâmico)": {"cd": 0.208, "area": 2.34, "tipo": "terrestre", "fixo": True}
    },
    "Aéreos": {
        "Boeing 737-800 (Aeronave Comercial)": {"cd": 0.027, "area": 12.50, "tipo": "aereo", "fixo": True},
        "Embraer Super Tucano (Militar/Ataque)": {"cd": 0.032, "area": 3.80, "tipo": "aereo", "fixo": True}
    },
    "Aquáticos": {
        "Submarino Classe Riachuelo (Submerso)": {"cd": 0.04, "area": 28.00, "tipo": "aquatico", "fixo": True},
        "Lancha Esportiva (Em Planio)": {"cd": 0.25, "area": 3.50, "tipo": "aquatico", "fixo": True}
    }
}

# ==========================================
# 3. ESTRUTURA DO LAYOUT EM TRÊS COLUNAS
# ==========================================
col_esq, col_centro, col_dir = st.columns([1, 2.2, 1], gap="medium")

# ----------------------------------------------------
# COLUNA ESQUERDA: AMBIENTE, ALTITUDE E VELOCIDADE
# ----------------------------------------------------
with col_esq:
    st.markdown("### 🌐 Ambiente & Clima")
    st.write("---")
    
    # Escolha da Altitude / Meio Fluido Dinâmico
    tipo_meio = st.radio("Meio de Escoamento:", ["Atmosférico (Ar)", "Aquático (Água Doce/Mar)"])
    
    if tipo_meio == "Atmosférico (Ar)":
        altitude = st.slider("Altitude em Relação ao Nível do Mar (m):", 0, 10000, 0, step=200)
        temp_c = st.slider("Temperatura do Ar (°C):", -10, 40, 20, step=1)
        
        # Modelo de Atmosfera Padrão (ISA) - Variação real de Densidade (rho)
        temp_k = temp_c + 273.15
        p_atm = 101325 * ((1 - 2.25577e-5 * altitude) ** 5.25588)  # Pressão barométrica em Pa
        rho = p_atm / (287.05 * temp_k)                          # Densidade corrigida (kg/m³)
        st.caption(f"🍃 Densidade Dinâmica do Ar ($\rho$): **{rho:.3f} kg/m³**")
    else:
        altitude = 0
        rho = 998.2  # Densidade da água (kg/m³)
        st.caption(f"💧 Densidade da Água ($\rho$): **{rho:.1f} kg/m³**")
        
    st.write("---")
    st.markdown("### ⏱️ Velocidade de Ensaio")
    v_kmh = st.slider("Velocidade do Fluxo (km/h):", 10.0, 300.0, 110.0, step=5.0)
    v_ms = v_kmh / 3.6  # Conversão para m/s

# ----------------------------------------------------
# COLUNA DIREITA: SELEÇÃO DE VEÍCULOS E PRESET CUSTOM
# ----------------------------------------------------
with col_dir:
    st.markdown("### 🚘 Seleção de Veículos")
    st.write("---")
    
    categoria_sel = st.selectbox("Categoria:", ["Terrestres", "Aéreos", "Aquáticos"])
    opcoes_categoria = list(VEICULOS_PRESETS[categoria_sel].keys()) + ["🔧 Preset Customizável (Modificável)"]
    
    veiculo_a = st.selectbox("Veículo Principal (Objeto A):", opcoes_categoria, index=0)
    
    # Lógica do Preset Customizável vs Presets Fixos e Inalteráveis
    if veiculo_a == "🔧 Preset Customizável (Modificável)":
        st.info("Ajuste os parâmetros abaixo para seu veículo customizado:")
        cd_a = st.number_input("Coeficiente de Arrasto (Cd):", value=0.300, format="%.3f", step=0.01)
        area_a = st.number_input("Área Frontal (m²):", value=2.00, format="%.2f", step=0.1)
        tipo_anim_a = "terrestre"
    else:
        dados_a = VEICULOS_PRESETS[categoria_sel][veiculo_a]
        cd_a = dados_a["cd"]
        area_a = dados_a["area"]
        tipo_anim_a = dados_a["tipo"]
        st.success(f"**Presets Fixos:** Cd = `{cd_a}` | Área = `{area_a} m²`")

    st.write("---")
    # Botão de Comparação de Veículos
    comparar = st.toggle("🔀 Modo Comparação (Linha Dupla)", value=False)
    
    if comparar:
        st.markdown("**Veículo Secundário (Objeto B):**")
        veiculo_b = st.selectbox("Selecione o Veículo B:", opcoes_categoria, index=1 if len(opcoes_categoria) > 1 else 0)
        
        if veiculo_b == "🔧 Preset Customizável (Modificável)":
            cd_b = st.number_input("Cd (Objeto B):", value=0.250, format="%.3f", step=0.01)
            area_b = st.number_input("Área m² (Objeto B):", value=1.80, format="%.2f", step=0.1)
        else:
            dados_b = VEICULOS_PRESETS[categoria_sel][veiculo_b]
            cd_b = dados_b["cd"]
            area_b = dados_b["area"]
            st.caption(f"**Objeto B Fixos:** Cd = `{cd_b}` | Área = `{area_b} m²`")

# ----------------------------------------------------
# CÁLCULOS FÍSICOS REAIS
# ----------------------------------------------------
# Fd = 0.5 * rho * v^2 * Cd * A
fd_a = 0.5 * rho * (v_ms ** 2) * cd_a * area_a
pot_w_a = fd_a * v_ms
pot_cv_a = pot_w_a / 735.499  # Conversão de Watts para Cavalo-Vapor (CV)

if comparar:
    fd_b = 0.5 * rho * (v_ms ** 2) * cd_b * area_b
    pot_w_b = fd_b * v_ms
    pot_cv_b = pot_w_b / 735.499

# ----------------------------------------------------
# COLUNA CENTRAL: GRÁFICOS, ANIMAÇÃO E RESULTADOS
# ----------------------------------------------------
with col_centro:
    st.markdown('<p class="title-text">⚡ Simulador de Aerodinâmica & Arrasto Fluido</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Análise telemétrica de forças dinâmicas com base em modelos reais e condições atmosféricas.</p>', unsafe_allow_html=True)
    
    # Exibição de Métricas em Destaque
    m1, m2, m3 = st.columns(3)
    m1.metric("Força de Arrasto (Fd)", f"{fd_a:.1f} N")
    m2.metric("Potência Exigida", f"{pot_cv_a:.1f} CV", f"{pot_w_a/1000:.1f} kW")
    m3.metric("Velocidade do Fluxo", f"{v_kmh:.0f} km/h", f"{v_ms:.1f} m/s")
    
    st.write("---")
    
    # Abas para Organização dos Gráficos e da Animação
    tab_anim, tab_fd, tab_pot = st.tabs([
        "💨 Animação do Fluxo (Partículas)", 
        "📈 Força de Arrasto (Fd vs V)", 
        "⚡ Potência Requerida (CV vs V)"
    ])

    # ----------------------------------------------------
    # ABA 1: ANIMAÇÃO DE PARTÍCULAS BATING NO VEÍCULO
    # ----------------------------------------------------
    with tab_anim:
        st.markdown("##### Visualização das Partículas de Vento no Túnel de Aerodinâmica")
        
        # Injeção de Canvas HTML/JS para Animação de Partículas em Tempo Real
        canvas_html = f"""
        <div style="text-align: center; background-color: #0F172A; padding: 8px; border-radius: 10px;">
            <canvas id="particleCanvas" width="750" height="320" style="border: 1px solid #334155; border-radius: 8px; background: #020617;"></canvas>
        </div>
        <script>
            const canvas = document.getElementById('particleCanvas');
            const ctx = canvas.getContext('2d');
            
            const speed = {v_ms} * 0.18;
            const cd = {cd_a};
            const shapeType = "{tipo_anim_a}";
            
            let particles = [];
            for(let i = 0; i < 110; i++) {{
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
                ctx.fillStyle = '#F43F5E';
                ctx.strokeStyle = '#FFFFFF';
                ctx.lineWidth = 2;
                ctx.beginPath();
                
                if (shapeType === 'terrestre') {{
                    // Silhueta de Veículo Terrestre
                    ctx.moveTo(280, 200); ctx.lineTo(330, 200); ctx.lineTo(370, 150);
                    ctx.lineTo(450, 150); ctx.lineTo(490, 200); ctx.lineTo(520, 200);
                    ctx.lineTo(520, 220); ctx.lineTo(280, 220);
                }} else if (shapeType === 'aereo') {{
                    // Silhueta Aerodinâmica de Avião
                    ctx.ellipse(400, 185, 110, 22, 0, 0, 2 * Math.PI);
                }} else {{
                    // Silhueta Hidrodinâmica de Casco/Submarino
                    ctx.ellipse(400, 185, 95, 38, 0, 0, 2 * Math.PI);
                }}
                ctx.fill();
                ctx.stroke();
            }}

            function render() {{
                ctx.fillStyle = 'rgba(2, 6, 23, 0.25)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                drawVehicle();
                
                particles.forEach(p => {{
                    let dx = p.x - 400;
                    let dy = p.y - 185;
                    let dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist < 90) {{
                        let angle = Math.atan2(dy, dx);
                        p.vy += Math.sin(angle) * (cd * 2.2);
                        p.color = '#FBBF24'; // Mudança de cor na zona de alta pressão
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
        </script>
        """
        components.html(canvas_html, height=350)

    # Vetorização do Eixo X (Velocidades para os gráficos)
    v_vetor_kmh = np.linspace(1, 250, 100)
    v_vetor_ms = v_vetor_kmh / 3.6

    # ----------------------------------------------------
    # ABA 2: GRÁFICO DA FORÇA DE ARRASTO (COM SOMBREAMENTO)
    # ----------------------------------------------------
    with tab_fd:
        fd_vetor_a = 0.5 * rho * (v_vetor_ms ** 2) * cd_a * area_a
        
        fig_fd = go.Figure()
        
        # Curva do Veículo A com Sombreamento (fill='tozeroy')
        fig_fd.add_trace(go.Scatter(
            x=v_vetor_kmh, y=fd_vetor_a,
            mode='lines',
            name=f'A: {veiculo_a}',
            line=dict(color='#0284C7', width=3),
            fill='tozeroy',
            fillcolor='rgba(2, 132, 199, 0.15)',
            hovertemplate="Velocidade: %{x:.1f} km/h<br>Força de Arrasto: %{y:.1f} N<extra></extra>"
        ))
        
        # Destaque do Ponto Selecionado
        fig_fd.add_trace(go.Scatter(
            x=[v_kmh], y=[fd_a],
            mode='markers',
            name='Ponto Atual (A)',
            marker=dict(color='#0284C7', size=11, symbol='circle'),
            hovertemplate="Ponto Atual A<br>V: %{x:.1f} km/h<br>Fd: %{y:.1f} N<extra></extra>"
        ))

        # Se o Modo Comparação estiver ativo -> Adiciona a Segunda Linha
        if comparar:
            fd_vetor_b = 0.5 * rho * (v_vetor_ms ** 2) * cd_b * area_b
            fig_fd.add_trace(go.Scatter(
                x=v_vetor_kmh, y=fd_vetor_b,
                mode='lines',
                name=f'B: {veiculo_b}',
                line=dict(color='#E11D48', width=3),
                fill='tozeroy',
                fillcolor='rgba(225, 29, 72, 0.12)',
                hovertemplate="Velocidade: %{x:.1f} km/h<br>Força de Arrasto: %{y:.1f} N<extra></extra>"
            ))
            fig_fd.add_trace(go.Scatter(
                x=[v_kmh], y=[fd_b],
                mode='markers',
                name='Ponto Atual (B)',
                marker=dict(color='#E11D48', size=11, symbol='square'),
                hovertemplate="Ponto Atual B<br>V: %{x:.1f} km/h<br>Fd: %{y:.1f} N<extra></extra>"
            ))

        # Estilização do Gráfico com Destaque nos Eixos X e Y
        fig_fd.update_layout(
            title="Curva de Força de Arrasto ($F_d = \\frac{1}{2} \\rho v^2 C_d A$)",
            xaxis=dict(
                title="<b>Velocidade (km/h)</b>",
                showgrid=True, gridcolor='#E2E8F0',
                showline=True, linewidth=2, linecolor='#0F172A', mirror=True
            ),
            yaxis=dict(
                title="<b>Força de Arrasto Fd (N)</b>",
                showgrid=True, gridcolor='#E2E8F0',
                showline=True, linewidth=2, linecolor='#0F172A', mirror=True
            ),
            hovermode="x unified",
            template="plotly_white",
            height=400,
            margin=dict(l=40, r=20, t=40, b=40)
        )
        st.plotly_chart(fig_fd, use_container_width=True)

    # ----------------------------------------------------
    # ABA 3: GRÁFICO DA POTÊNCIA NECESSÁRIA (MOTOR)
    # ----------------------------------------------------
    with tab_pot:
        pot_vetor_cv_a = (fd_vetor_a * v_vetor_ms) / 735.499
        
        fig_pot = go.Figure()
        
        # Curva de Potência A com Sombreamento
        fig_pot.add_trace(go.Scatter(
            x=v_vetor_kmh, y=pot_vetor_cv_a,
            mode='lines',
            name=f'A: {veiculo_a}',
            line=dict(color='#0D9488', width=3),
            fill='tozeroy',
            fillcolor='rgba(13, 148, 136, 0.15)',
            hovertemplate="Velocidade: %{x:.1f} km/h<br>Potência Requerida: %{y:.1f} CV<extra></extra>"
        ))
        
        fig_pot.add_trace(go.Scatter(
            x=[v_kmh], y=[pot_cv_a],
            mode='markers',
            name='Ponto Atual (A)',
            marker=dict(color='#0D9488', size=11),
            hovertemplate="Ponto Atual A<br>V: %{x:.1f} km/h<br>Potência: %{y:.1f} CV<extra></extra>"
        ))

        if comparar:
            pot_vetor_cv_b = (fd_vetor_b * v_vetor_ms) / 735.499
            fig_pot.add_trace(go.Scatter(
                x=v_vetor_kmh, y=pot_vetor_cv_b,
                mode='lines',
                name=f'B: {veiculo_b}',
                line=dict(color='#D97706', width=3),
                fill='tozeroy',
                fillcolor='rgba(217, 119, 6, 0.12)',
                hovertemplate="Velocidade: %{x:.1f} km/h<br>Potência Requerida: %{y:.1f} CV<extra></extra>"
            ))
            fig_pot.add_trace(go.Scatter(
                x=[v_kmh], y=[pot_cv_b],
                mode='markers',
                name='Ponto Atual (B)',
                marker=dict(color='#D97706', size=11),
                hovertemplate="Ponto Atual B<br>V: %{x:.1f} km/h<br>Potência: %{y:.1f} CV<extra></extra>"
            ))

        fig_pot.update_layout(
            title="Potência Requerida do Motor para Vencer o Arrasto ($P = F_d \\cdot v$)",
            xaxis=dict(
                title="<b>Velocidade (km/h)</b>",
                showgrid=True, gridcolor='#E2E8F0',
                showline=True, linewidth=2, linecolor='#0F172A', mirror=True
            ),
            yaxis=dict(
                title="<b>Potência Necessária (CV)</b>",
                showgrid=True, gridcolor='#E2E8F0',
                showline=True, linewidth=2, linecolor='#0F172A', mirror=True
            ),
            hovermode="x unified",
            template="plotly_white",
            height=400,
            margin=dict(l=40, r=20, t=40, b=40)
        )
        st.plotly_chart(fig_pot, use_container_width=True)
