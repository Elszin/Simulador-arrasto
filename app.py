import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(
    page_title="Simulador MONSTRO & Túnel de Vento Aerodinâmico",
    page_icon="🏎️",
    layout="wide"
)

# Estilização CSS Avançada
st.markdown("""
    <style>
    div[data-testid="stColumn"]:nth-child(1) {
        position: sticky;
        top: 1rem;
        align-self: flex-start;
        z-index: 99;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00D2FF, #FF2A6D, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    </style>
""", unsafe_allow_html=True)

# Dicionários de Dados
PRESETS_VEICULOS = {
    "Carro Popular (Hatch/Sedan)": {"cd": 0.32, "area": 2.2, "massa": 1100, "potencia_cv": 100, "tipo": "carro"},
    "Carro Esportivo (Supercarro)": {"cd": 0.28, "area": 1.9, "massa": 1400, "potencia_cv": 450, "tipo": "carro_esportivo"},
    "Caminhão / Ônibus": {"cd": 0.80, "area": 8.0, "massa": 12000, "potencia_cv": 400, "tipo": "caixa"},
    "Asa de Avião / Aerofólio": {"cd": 0.05, "area": 1.2, "massa": 500, "potencia_cv": 200, "tipo": "asa"}
}

# ==========================================
# BARRA LATERAL
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Parâmetros do Túnel de Vento")
    st.write("---")
    
    preset_sel = st.selectbox("Selecione o Modelo no Túnel:", list(PRESETS_VEICULOS.keys()), index=0)
    p_d = PRESETS_VEICULOS[preset_sel]
    
    v_kmh = st.slider("Velocidade do Vento (km/h)", 10.0, 300.0, 120.0, 5.0)
    cd = st.slider("Coeficiente de Arrasto (Cd)", 0.01, 1.20, p_d["cd"], 0.01)
    area = st.slider("Área Frontal (m²)", 0.5, 10.0, p_d["area"], 0.1)
    rho = st.slider("Densidade do Ar ρ (kg/m³)", 0.5, 1.5, 1.225, 0.05)

# Cálculos Básicos
v_ms = v_kmh / 3.6
fd = 0.5 * rho * (v_ms**2) * cd * area
pot_cv = (fd * v_ms) / 735.5

# ==========================================
# ÁREA PRINCIPAL
# ==========================================
st.markdown('<p class="main-title">🌬️ Túnel de Vento Aerodinâmico Interativo</p>', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.metric("Velocidade do Fluxo", f"{v_kmh:.0f} km/h", f"{v_ms:.1f} m/s")
m2.metric("Força de Arrasto (Fd)", f"{fd:.1f} N")
m3.metric("Potência para Vencer o Vento", f"{pot_cv:.1f} CV")

st.write("---")

tab_tunnel, tab_cfd = st.tabs(["🌬️ Animação de Partículas (Túnel de Vento)", "📊 Campo de Pressão & Streamlines (CFD)"])

# ----------------------------------------------------
# TAB 1: ANIMAÇÃO EM CANVAS (PARTÍCULAS DE VENTO)
# ----------------------------------------------------
with tab_tunnel:
    # Código JS/Canvas responsivo que se ajusta em tempo real com os sliders
    canvas_code = f"""
    <div style="text-align: center; background-color: #0E1117; padding: 10px; border-radius: 10px;">
        <canvas id="windTunnel" width="800" height="350" style="border: 1px solid #30363D; border-radius: 8px; background: #05070A;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('windTunnel');
        const ctx = canvas.getContext('2d');

        const speed = {v_ms} * 0.15;  // Velocidade das partículas
        const cd = {cd};              // Define turbulência
        const objectType = "{p_d['tipo']}";

        // Criar partículas de vento
        let particles = [];
        const numParticles = 120;

        for(let i = 0; i < numParticles; i++) {{
            particles.push({{
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: speed + Math.random() * 2,
                vy: 0,
                size: Math.random() * 2 + 1,
                color: '#00D2FF'
            }});
        }}

        function drawObject() {{
            ctx.fillStyle = '#FF2A6D';
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 2;

            ctx.beginPath();
            if (objectType === 'carro' || objectType === 'carro_esportivo') {{
                // Desenhar Silhueta de Carro
                ctx.moveTo(300, 220);
                ctx.lineTo(340, 220);
                ctx.lineTo(370, 180);
                ctx.lineTo(440, 180);
                ctx.lineTo(480, 220);
                ctx.lineTo(520, 220);
                ctx.lineTo(520, 240);
                ctx.lineTo(300, 240);
                ctx.closePath();
            }} else if (objectType === 'asa') {{
                // Desenhar Gota / Aerofólio
                ctx.ellipse(400, 210, 80, 25, Math.PI / 12, 0, 2 * Math.PI);
            }} else {{
                // Desenhar Bloco / Caminhão
                ctx.rect(320, 150, 160, 90);
            }}
            ctx.fill();
            ctx.stroke();
        }}

        function animate() {{
            ctx.fillStyle = 'rgba(5, 7, 10, 0.2)'; // Efeito Rastro
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            drawObject();

            particles.forEach(p => {{
                // Lógica de Desvio Aerodinâmico simples ao se aproximar do objeto
                let dx = p.x - 400;
                let dy = p.y - 200;
                let dist = Math.sqrt(dx*dx + dy*dy);

                if (dist < 100) {{
                    let angle = Math.atan2(dy, dx);
                    p.vy += Math.sin(angle) * (cd * 1.5);
                    
                    // Mudar de cor no impacto (Alta Pressão -> Amarelo/Vermelho)
                    p.color = '#FFD700';
                }} else {{
                    p.vy *= 0.95; // Retorna ao fluxo normal
                    p.color = '#00D2FF';
                }}

                p.x += p.vx;
                p.y += p.vy;

                // Reiniciar partículas que saem da tela
                if (p.x > canvas.width) {{
                    p.x = 0;
                    p.y = Math.random() * canvas.height;
                    p.vx = speed + Math.random() * 2;
                    p.vy = 0;
                }}
            }});

            particles.forEach(p => {{
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fill();
            }});

            requestAnimationFrame(animate);
        }}

        animate();
    </script>
    """
    components.html(canvas_code, height=390)

# ----------------------------------------------------
# TAB 2: CAMPO DE PRESSÃO & STREAMLINES (PLOTLY)
# ----------------------------------------------------
with tab_cfd:
    x = np.linspace(-3, 3, 40)
    y = np.linspace(-2, 2, 30)
    X, Y = np.meshgrid(x, y)

    # Potencial de escoamento ao redor de um cilindro/obstáculo aerodinâmico
    R = 0.8 * (cd ** 0.5)
    r2 = X**2 + Y**2
    r2[r2 < R**2] = R**2  # Evita divisão por zero no objeto

    # Componentes de Velocidade (u, v)
    u = v_ms * (1 - (R**2 * (X**2 - Y**2)) / (r2**2))
    v = v_ms * (-2 * R**2 * X * Y) / (r2**2)
    
    # Campo de Pressão Relativa (Bernoulli: P = 0.5 * rho * (V_inf^2 - V^2))
    vel_mag = np.sqrt(u**2 + v**2)
    pressao = 0.5 * rho * (v_ms**2 - vel_mag**2)

    # Gráfico Contour com Streamlines
    fig = go.Figure()

    # Mapa de Calor da Pressão (Vermelho = Alta Pressão na frente, Azul = Baixa Pressão atrás)
    fig.add_trace(go.Contour(
        z=pressao, x=x, y=y,
        colorscale='Turbid',
        colorbar=dict(title="Pressão (Pa)"),
        opacity=0.8
    ))

    fig.update_layout(
        title="Simulação CFD: Campo de Pressão e Escoamento",
        xaxis_title="Distância Horizontal (m)",
        yaxis_title="Altura (m)",
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)
