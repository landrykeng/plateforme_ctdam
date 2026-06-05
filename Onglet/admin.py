import streamlit as st
import pandas as pd
import os
from datetime import datetime
from Authentification import admin_panel
from data.loader import (get_emissions, get_encours_mensuels, get_svt,
                          get_calendrier, EXCEL_PATH, PAYS_CEMAC)

EXCEL_FILE = EXCEL_PATH

def show(sous_page="Gestion des utilisateurs"):
    if not st.session_state.get("authenticated", False):
        st.error(":material/block: Accès refusé."); return

    user_status = st.session_state.get("status", "")
    if user_status not in ["Administrateur", "Admin BEAC"]:
        st.error(f":material/block: Accès réservé aux administrateurs BEAC. Votre profil : **{user_status}**")
        return

    st.markdown(f"""
    <div style="background:linear-gradient(90deg,#003366,#004080);color:white;padding:0.6rem 1.2rem;
    border-radius:6px;border-left:4px solid #C8A84B;margin-bottom:1.5rem;">
        <span style="font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;color:#C8A84B;">
        Espace d'administration</span> &nbsp;|&nbsp; <span style="font-weight:600;">{sous_page}</span>
    </div>""", unsafe_allow_html=True)

    # ── Gestion des utilisateurs ─────────────────────────────────────────────
    if sous_page == "Gestion des utilisateurs":
        st.title("Gestion des utilisateurs")
        admin_panel()

    # ── Import données marché ─────────────────────────────────────────────────
    elif sous_page == "Import données marché":
        st.title("Import des données de marché")
        st.markdown(f"""
        <div class="app-card">
        Toutes les données de la plateforme proviennent du fichier Excel :
        <code>{EXCEL_FILE}</code><br>
        Mettez à jour les feuilles correspondantes puis rechargez la page.
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        tab_enc, tab_adj, tab_remb, tab_cal = st.tabs([
            ":material/upload_file: Import Excel direct",
            ":material/table: Aperçu EMISSIONS",
            ":material/table: Aperçu REMBOURSEMENTS",
            ":material/calendar_month: Aperçu CALENDRIER",
        ])

        with tab_enc:
            st.markdown("#### Remplacer le fichier Excel de la base de données")
            st.info("""**Procédure :**
1. Téléchargez le fichier Excel ci-dessous
2. Ouvrez-le et mettez à jour les feuilles souhaitées
3. Téléversez le fichier modifié ci-dessous
4. Rechargez la page pour que les changements prennent effet""")

            if os.path.exists(EXCEL_FILE):
                with open(EXCEL_FILE, "rb") as f:
                    st.download_button(":material/download: Télécharger la base de données Excel",
                        f.read(), "CTDAM_CEMAC_Base_Donnees.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            fichier = st.file_uploader("Téléverser le fichier Excel mis à jour",
                                        type=["xlsx"], key="excel_upload")
            if fichier:
                try:
                    # Valider qu'il s'agit bien d'un Excel avec les bonnes feuilles
                    xl = pd.ExcelFile(fichier)
                    feuilles_attendues = ["EMISSIONS","REMBOURSEMENTS","SVT","SGP","SDB",
                                          "PAYS_MACRO","ENCOURS_MENSUEL","CALENDRIER_EMISSIONS",
                                          "COURBE_TAUX","DETENTEURS","DOCUMENTS_META"]
                    feuilles_presentes = xl.sheet_names
                    manquantes = [f for f in feuilles_attendues if f not in feuilles_presentes]

                    if manquantes:
                        st.warning(f"Feuilles manquantes dans le fichier : {manquantes}")
                    else:
                        # Sauvegarder
                        with open(EXCEL_FILE, "wb") as out:
                            out.write(fichier.getvalue())
                        st.success(f":material/check_circle: Base de données mise à jour avec succès — {len(feuilles_presentes)} feuilles chargées.")
                        st.info("Rechargez la page (F5) pour voir les données actualisées.")
                except Exception as e:
                    st.error(f":material/error: Erreur : {e}")

            st.markdown("---")
            st.markdown("#### Import partiel par feuille (CSV/Excel)")
            feuille_cible = st.selectbox("Feuille cible", [
                "EMISSIONS","REMBOURSEMENTS","ENCOURS_MENSUEL","CALENDRIER_EMISSIONS",
                "COURBE_TAUX","DETENTEURS","PAYS_MACRO","SVT","SGP","SDB",
                "INVESTISSEURS_INST","CALCULS_MARCHE","DOCUMENTS_META"])
            fichier2 = st.file_uploader("Fichier à importer (CSV ou Excel)", type=["csv","xlsx"], key="partial_upload")
            if fichier2:
                try:
                    df_import = pd.read_csv(fichier2) if fichier2.name.endswith(".csv") else pd.read_excel(fichier2)
                    st.success(f":material/check_circle: Aperçu — {len(df_import)} lignes, {len(df_import.columns)} colonnes")
                    st.dataframe(df_import.head(10), use_container_width=True, hide_index=True)
                    if st.button(":material/save: Valider l'import dans l'Excel", type="primary"):
                        # Écrire dans la feuille cible
                        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a",
                                            if_sheet_exists="replace") as writer:
                            df_import.to_excel(writer, sheet_name=feuille_cible, index=False)
                        st.success(f"Feuille **{feuille_cible}** mise à jour.")
                except Exception as e:
                    st.error(f":material/error: Erreur : {e}")

        with tab_adj:
            df_adj = get_emissions()
            if not df_adj.empty:
                st.markdown(f"**{len(df_adj)} émissions dans la base**")
                st.dataframe(df_adj.head(20), use_container_width=True, hide_index=True)
            else:
                st.info("Feuille EMISSIONS vide.")

        with tab_remb:
            try:
                df_remb = pd.read_excel(EXCEL_FILE, sheet_name="REMBOURSEMENTS", header=2)
                df_remb = df_remb.dropna(how="all")
                st.markdown(f"**{len(df_remb)} remboursements dans la base**")
                st.dataframe(df_remb.head(20), use_container_width=True, hide_index=True)
            except Exception:
                st.info("Feuille REMBOURSEMENTS vide.")

        with tab_cal:
            df_cal = get_calendrier()
            if not df_cal.empty:
                st.dataframe(df_cal, use_container_width=True, hide_index=True)
            else:
                st.info("Feuille CALENDRIER_EMISSIONS vide.")

    # ── Gestion du Bottin ─────────────────────────────────────────────────────
    elif sous_page == "Gestion du Bottin":
        st.title("Gestion du Bottin des investisseurs")
        st.markdown("""Gérez les fiches SVT, SGP, SDB directement dans l'Excel
        (feuilles **SVT**, **SGP**, **SDB**, **INVESTISSEURS_INST**) puis rechargez la page.""")

        df_svt = get_svt()
        st.markdown("### Fiches SVT actuelles")
        if not df_svt.empty:
            st.dataframe(df_svt, use_container_width=True, hide_index=True)

        # Demandes de mise à jour (statique pour illustration)
        st.markdown("### Demandes de mise à jour en attente")
        demandes = [
            {"institution":"BGFI Bank Tchad","type":"SVT","modification":"Mise à jour email Front Office","date":"2026-04-10"},
        ]
        for d in demandes:
            col1, col2, col3 = st.columns([4,1,1])
            with col1:
                st.markdown(f"**{d['institution']}** ({d['type']}) — {d['modification']} · {d['date']}")
            with col2:
                if st.button(":material/check: Valider", key=f"val_{d['institution']}"):
                    st.success("Validé — modifiez l'Excel en conséquence.")
            with col3:
                if st.button(":material/close: Rejeter", key=f"rej_{d['institution']}"):
                    st.warning("Rejeté.")

    # ── Gestion émissions ─────────────────────────────────────────────────────
    elif sous_page == "Gestion émissions":
        st.title("Gestion du calendrier des émissions")
        st.markdown("""Les émissions sont gérées dans les feuilles **EMISSIONS** et **CALENDRIER_EMISSIONS** de l'Excel.""")

        tab_cal, tab_new = st.tabs([
            ":material/calendar_month: Calendrier actuel",
            ":material/add_circle: Ajouter une adjudication",
        ])

        with tab_cal:
            df_cal = get_calendrier()
            if not df_cal.empty:
                st.dataframe(df_cal, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune émission programmée.")

        with tab_new:
            st.info("Pour ajouter une adjudication, ajoutez une ligne dans la feuille **CALENDRIER_EMISSIONS** de l'Excel puis rechargez.")
            with st.form("new_adj"):
                c1, c2 = st.columns(2)
                with c1:
                    pays_n = st.selectbox("Pays émetteur", [v["nom"] for v in PAYS_CEMAC.values()])
                    instrument_n = st.selectbox("Instrument", ["BTA","OTA"])
                    maturite_n = st.selectbox("Maturité", ["13 semaines","26 semaines","52 semaines","2 ans","3 ans","5 ans","7 ans","10 ans","15 ans"])
                with c2:
                    date_n = st.date_input("Date d'adjudication")
                    montant_n = st.number_input("Montant indicatif (M XAF)", value=10000, step=1000)
                    statut_n = st.selectbox("Statut", ["Prévisionnel","Confirmé"])
                if st.form_submit_button(":material/add: Ajouter au calendrier", type="primary"):
                    st.success(f"Ajoutez manuellement cette ligne dans l'Excel : {pays_n} — {instrument_n} {maturite_n} — {date_n} — {montant_n} M XAF — {statut_n}")

    # ── Tableau de bord admin ─────────────────────────────────────────────────
    elif sous_page == "Tableau de bord admin":
        st.title("Tableau de bord d'utilisation")
        from Authentification import load_users
        users = load_users()
        nb_total = len(users.get("users",{}))
        nb_actifs = sum(1 for u in users.get("users",{}).values() if u.get("active", True))
        nb_attente = sum(1 for u in users.get("users",{}).values()
                        if str(u.get("status","")).lower() in ["en attente","pending"])

        df_adj = get_emissions()
        nb_adj = len(df_adj)

        c1, c2, c3, c4 = st.columns(4)
        for col, val, label in [
            (c1, nb_total, "Comptes total"),
            (c2, nb_actifs, "Comptes actifs"),
            (c3, nb_attente, "En attente validation"),
            (c4, nb_adj, "Émissions en base"),
        ]:
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value">{val}</div>
                    <div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

        st.markdown("---")
        # Répartition utilisateurs par statut
        if users.get("users"):
            status_count = {}
            for u in users["users"].values():
                s = u.get("status","Utilisateur")
                status_count[s] = status_count.get(s,0) + 1
            import plotly.express as px
            df_status = pd.DataFrame(list(status_count.items()), columns=["Statut","Nombre"])
            fig = px.bar(df_status, x="Nombre", y="Statut", orientation="h",
                color_discrete_sequence=["#003366"])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                height=250, margin=dict(l=0,r=0,t=10,b=0))
            st.markdown("### Répartition des utilisateurs par statut")
            st.plotly_chart(fig, use_container_width=True)

    # ── Journal d'activité ────────────────────────────────────────────────────
    elif sous_page == "Journal d'activité":
        st.title("Journal d'activité")
        st.caption("Historique des actions sur la plateforme.")
        journal = [
            {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "utilisateur": "admin_beac",
             "action": "Connexion", "détail": "Session ouverte"},
            {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "utilisateur": "admin_beac",
             "action": "Import Excel", "détail": "Base de données mise à jour"},
        ]
        df_j = pd.DataFrame(journal)
        search_j = st.text_input(":material/search: Filtrer le journal")
        if search_j:
            df_j = df_j[df_j.apply(lambda r: search_j.lower() in r.to_string().lower(), axis=1)]
        st.dataframe(df_j, use_container_width=True, hide_index=True)
        csv = df_j.to_csv(index=False).encode("utf-8")
        st.download_button(":material/download: Exporter", csv, "journal.csv")
