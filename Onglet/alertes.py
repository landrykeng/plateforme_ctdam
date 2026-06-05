import streamlit as st

def show():
    if not st.session_state.get("authenticated", False):
        st.warning(":material/lock: Cette section est réservée aux utilisateurs enregistrés.")
        if st.button(":material/login: Se connecter"):
            st.session_state["page"] = "Connexion"; st.rerun()
        return

    st.title("Alertes personnalisées")
    st.caption("Configurez des alertes pour être notifié par email des adjudications correspondant à vos critères.")

    col_form, col_actives = st.columns([2, 1])

    with col_form:
        st.markdown("### Nouvelle alerte")
        with st.form("alerte_form"):
            c1, c2 = st.columns(2)
            with c1:
                instrument_alerte = st.multiselect("Instrument(s)", ["BTA","OTA"], default=["BTA","OTA"])
                pays_alerte = st.multiselect("Pays émetteur(s)",
                    ["Cameroun","Gabon","Congo","Rép. Centrafricaine","Guinée Équatoriale","Tchad"],
                    default=["Cameroun","Gabon"])
            with c2:
                taux_min = st.number_input("Rendement minimum (%)", 0.0, 15.0, 5.0, 0.1)
                maturite_alerte = st.multiselect("Maturité(s)",
                    ["13 semaines","26 semaines","52 semaines","2 ans","3 ans","5 ans","7 ans","10 ans","15 ans"])

            email_alerte = st.text_input("Email de notification",
                value=f"{st.session_state.get('username','')}@exemple.cm")
            newsletter = st.checkbox("S'abonner à la newsletter mensuelle du marché")

            submitted = st.form_submit_button(":material/notifications_active: Activer cette alerte",
                type="primary", use_container_width=True)
            if submitted:
                st.success(":material/check_circle: Alerte configurée avec succès !")

    with col_actives:
        st.markdown("### Mes alertes actives")
        st.markdown("""
        <div class="app-card" style="margin-bottom:0.5rem;">
            <div style="font-weight:600; color:#003366; font-size:0.88rem;">BTA · Cameroun · ≥ 3,5%</div>
            <div style="font-size:0.78rem; color:#8C8C8C; margin-top:3px;">Configurée le 2026-01-10</div>
        </div>
        <div class="app-card" style="margin-bottom:0.5rem;">
            <div style="font-weight:600; color:#003366; font-size:0.88rem;">OTA 5 ans · Gabon · ≥ 7%</div>
            <div style="font-size:0.78rem; color:#8C8C8C; margin-top:3px;">Configurée le 2026-02-15</div>
        </div>
        """, unsafe_allow_html=True)
        st.info(":material/mail: **Newsletter** : vous êtes abonné.")
