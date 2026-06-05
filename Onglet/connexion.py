import streamlit as st
from Authentification import authentication_system

def show():
    st.title("Connexion à l'espace restreint")
    st.markdown("Accédez au Bottin des investisseurs, aux données historiques détaillées et aux outils de simulation.")

    result = authentication_system(required_status=None, key="main_login")
    if result:
        st.success(":material/check_circle: Vous êtes connecté. Utilisez la navigation dans le menu.")
        if st.button(":material/contacts: Accéder au Bottin des investisseurs", type="primary"):
            st.session_state["page"] = "Bottin des investisseurs"
            st.rerun()
