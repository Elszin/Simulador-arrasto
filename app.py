# ==========================================
# COLUNA DIREITA: PARÂMETROS DO OBJETO
# ==========================================
with col_direita:
    st.markdown("### 📐 Geometria & Dinâmica")
    
    # Caixa retrátil para o Objeto A (Inicia expandida/aberta)
    with st.expander("🔵 **Objeto A (Referência)**", expanded=True):
        st.selectbox("Preset do Veículo:", list(presets_atuais.keys()), key="preset_select_a", on_change=carregar_preset_a)
        
        cd_a = st.slider("C_d (Arrasto do Corpo):", 0.01, 1.5, st.session_state.cd_a, 0.01, key="cd_a")
        area_a = st.slider("Área Frontal A (m²):", 0.1, 50.0, st.session_state.area_a, 0.1, key="area_a")
        massa_a = st.number_input("Massa do Veículo (kg):", value=st.session_state.m_a, step=50.0, key="m_a")
        potencia_cv_a = st.number_input("Potência do Motor (CV):", value=st.session_state.p_a, step=10.0, key="p_a")
        comprimento_a = st.number_input("Comprimento do Corpo (m):", value=st.session_state.comp_a, step=0.5, key="comp_a")
        
        usar_aerofolio = st.checkbox("➕ Adicionar Aerofólio / Asas", key="check_asa_a")
        if usar_aerofolio:
            cl_a = st.slider("C_L (Downforce):", 0.0, 2.5, 0.8, 0.1, key="cl_asa_a")
            area_asa_a = st.slider("Área da Asa (m²):", 0.1, 3.0, 0.5, 0.1, key="area_asa_a")
            aspect_ratio = 3.5
            cd_induzido_asa_a = (cl_a ** 2) / (np.pi * aspect_ratio)
        else:
            cl_a = 0.0
            area_asa_a = 0.0
            cd_induzido_asa_a = 0.0

    # Caixa retrátil para o Objeto B (Inicia fechada por padrão)
    if comparar:
        with st.expander("🔴 **Objeto B (Comparativo)**", expanded=False):
            st.selectbox("Preset do Veículo:", list(presets_atuais.keys()), key="preset_select_b", on_change=carregar_preset_b)
            
            cd_b = st.slider("C_d (Arrasto do Corpo):", 0.01, 1.5, st.session_state.cd_b, 0.01, key="cd_b")
            area_b = st.slider("Área Frontal B (m²):", 0.1, 50.0, st.session_state.area_b, 0.1, key="area_b")
            massa_b = st.number_input("Massa do Veículo (kg):", value=st.session_state.m_b, step=50.0, key="m_b")
            potencia_cv_b = st.number_input("Potência do Motor (CV):", value=st.session_state.p_b, step=10.0, key="p_b")
            comprimento_b = st.number_input("Comprimento do Corpo (m):", value=st.session_state.comp_b, step=0.5, key="comp_b")
            cl_b = 0.0
            area_asa_b = 0.0
            cd_induzido_asa_b = 0.0
