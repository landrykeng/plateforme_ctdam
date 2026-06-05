import streamlit as st
from Authentification import register_user

def show():
    st.title("Formulaire d'inscription")
    st.markdown("Complétez ce formulaire pour demander la création d'un compte. Votre demande sera examinée et validée manuellement par l'administrateur BEAC.")
    st.warning(":material/info: Aucun accès aux données détaillées n'est accordé sans validation préalable de votre dossier.")

    col_form, col_info = st.columns([3, 2])

    with col_form:
        with st.form("inscription_form"):
            st.markdown("#### Informations personnelles / institutionnelles")
            c1, c2 = st.columns(2)
            with c1:
                denomination = st.text_input("Dénomination ou nom complet *", placeholder="Ex : Activa Assurances SA")
            with c2:
                type_acteur = st.selectbox("Type d'acteur *", [
                    "SVT (Spécialiste en Valeurs du Trésor)",
                    "SGP (Société de Gestion et de Portefeuille)",
                    "SDB (Société de Bourse)",
                    "Compagnie d'assurance",
                    "Caisse de prévoyance",
                    "Investisseur institutionnel",
                    "Investisseur individuel qualifié",
                    "Investisseur non-résident / diaspora",
                    "Autre",
                ])

            c3, c4 = st.columns(2)
            with c3:
                pays = st.selectbox("Pays *", [
                    "Cameroun","Gabon","Congo","République Centrafricaine",
                    "Guinée Équatoriale","Tchad","Autre (hors CEMAC)"])
            with c4:
                agrement = st.text_input("N° d'agrément régulateur", placeholder="Ex : CMF-SGP-001")

            st.markdown("#### Contacts")
            c5, c6 = st.columns(2)
            with c5:
                email = st.text_input("Email professionnel *", placeholder="vous@institution.cm")
            with c6:
                telephone = st.text_input("Téléphone", placeholder="+237 6XX XXX XXX")
            nom_contact = st.text_input("Nom du point focal / responsable *", placeholder="Prénom NOM")

            st.markdown("#### Identifiants d'accès")
            c7, c8 = st.columns(2)
            with c7:
                username = st.text_input("Nom d'utilisateur *", placeholder="Min. 4 caractères")
            with c8:
                password = st.text_input("Mot de passe *", type="password", placeholder="Min. 8 caractères")
            password2 = st.text_input("Confirmer le mot de passe *", type="password")

            st.markdown("#### Pièce justificative")
            piece = st.file_uploader("Joindre une pièce justificative (PDF)", type=["pdf"])
            st.caption("Document d'agrément, statuts de la société, ou pièce d'identité selon le type d'acteur.")

            accept = st.checkbox("J'accepte que mes données soient traitées par la BEAC aux fins de validation de mon compte.")

            submitted = st.form_submit_button(":material/send: Soumettre la demande",
                use_container_width=True, type="primary")

            if submitted:
                errors = []
                if not denomination: errors.append("Dénomination requise")
                if not email: errors.append("Email requis")
                if not username or len(username) < 4: errors.append("Nom d'utilisateur trop court (min. 4 caractères)")
                if not password or len(password) < 8: errors.append("Mot de passe trop court (min. 8 caractères)")
                if password != password2: errors.append("Les mots de passe ne correspondent pas")
                if not accept: errors.append("Vous devez accepter les conditions")

                if errors:
                    for e in errors:
                        st.error(f":material/error: {e}")
                else:
                    success, msg = register_user(username, password, email, status="En attente")
                    if success:
                        st.success(f":material/check_circle: Demande enregistrée ! Votre dossier est en attente de validation. Vous serez notifié à **{email}**.")
                    else:
                        st.error(f":material/error: {msg}")

    with col_info:
        st.markdown("#### À propos du processus")
        st.markdown("""
        <div class="app-card"><div style="font-weight:700;color:#003366;margin-bottom:0.5rem;">
         Délai de traitement</div>
        <div style="font-size:0.88rem;color:#4A4A4A;">Votre dossier sera examiné sous <strong>5 jours ouvrés</strong>.</div></div>
        <br>
        <div class="app-card"><div style="font-weight:700;color:#003366;margin-bottom:0.5rem;">
         Validation manuelle</div>
        <div style="font-size:0.88rem;color:#4A4A4A;">Aucun accès automatique — chaque demande est vérifiée individuellement.</div></div>
        <br>
        <div class="app-card"><div style="font-weight:700;color:#003366;margin-bottom:0.5rem;">
         Données sécurisées</div>
        <div style="font-size:0.88rem;color:#4A4A4A;">Vos informations sont protégées conformément aux standards BEAC.</div></div>
        """, unsafe_allow_html=True)

        st.markdown("#### Contacts")
        st.markdown("""
        **BEAC — CRCT**
        :material/mail: crct@beac.int
        :material/phone: +237 222 23 40 30
        :material/location_on: Avenue Monseigneur Vogt, Yaoundé
        """)
