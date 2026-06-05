import streamlit as st
import pandas as pd
from data.loader import get_bottin_complet, get_svt, PAYS_CEMAC

def show():
    if not st.session_state.get("authenticated", False):
        st.warning(":material/lock: Cette section est réservée aux utilisateurs enregistrés et validés.")
        if st.button(":material/login: Se connecter"):
            st.session_state["page"] = "Connexion"; st.rerun()
        return

    st.title("Bottin des investisseurs")
    st.caption("Répertoire central de tous les acteurs du marché des valeurs du Trésor de la CEMAC.")

    bottin = get_bottin_complet()

    tab_svt, tab_sgp, tab_sdb, tab_inv = st.tabs([
        ":material/account_balance: SVT",
        ":material/trending_up: SGP",
        ":material/store: SDB",
        ":material/groups: Investisseurs institutionnels",
    ])

    pays_list = ["Tous"] + [v["nom"] for v in PAYS_CEMAC.values()]

    def filtres_et_affichage(df, prefix):
        if df.empty:
            st.info("Aucune donnée — alimentez la feuille correspondante de l'Excel.")
            return
        c1, c2, c3 = st.columns([2,1,2])
        with c1:
            pays = st.selectbox(":material/public: Pays", pays_list, key=f"{prefix}_pays")
        with c2:
            statuts = ["Tous"] + sorted(df["Statut"].dropna().unique().tolist()) if "Statut" in df.columns else ["Tous"]
            statut = st.selectbox(":material/toggle_on: Statut", statuts, key=f"{prefix}_statut")
        with c3:
            search = st.text_input(":material/search: Rechercher", placeholder="Nom, contact...", key=f"{prefix}_search")

        df_f = df.copy()
        if pays != "Tous" and "Pays" in df_f.columns:
            df_f = df_f[df_f["Pays"] == pays]
        if statut != "Tous" and "Statut" in df_f.columns:
            df_f = df_f[df_f["Statut"] == statut]
        if search:
            mask = df_f.apply(lambda r: search.lower() in r.to_string().lower(), axis=1)
            df_f = df_f[mask]

        st.markdown(f"<div style='font-size:0.82rem;color:#8C8C8C;margin-bottom:0.5rem;'>{len(df_f)} entrée(s)</div>",
                    unsafe_allow_html=True)
        st.dataframe(df_f, use_container_width=True, hide_index=True)

        col_dl, _ = st.columns([1,4])
        with col_dl:
            csv = df_f.to_csv(index=False).encode("utf-8")
            st.download_button(":material/download: Exporter CSV", csv,
                               f"bottin_{prefix}.csv", "text/csv", key=f"{prefix}_dl")

    with tab_svt:
        st.markdown("### Spécialistes en Valeurs du Trésor (SVT)")
        st.markdown("Les SVT sont les intermédiaires obligatoires sur le marché primaire.")
        filtres_et_affichage(bottin["SVT"], "svt")

        # Résumé par pays
        st.markdown("---")
        st.markdown("#### SVT actifs par pays")
        svt_full = get_svt()
        if not svt_full.empty and "statut" in svt_full.columns and "pays_nom" in svt_full.columns:
            actifs = svt_full[svt_full["statut"].astype(str).str.lower() == "actif"]
            cols = st.columns(3)
            for i, (code, info) in enumerate(PAYS_CEMAC.items()):
                nb = len(actifs[actifs["pays_nom"] == info["nom"]]) if "pays_nom" in actifs.columns else 0
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:0.8rem;">
                        <div class="metric-value">{nb}</div>
                        <div class="metric-label">{info['nom']}</div>
                    </div>""", unsafe_allow_html=True)

    with tab_sgp:
        st.markdown("### Sociétés de Gestion et de Portefeuille (SGP)")
        filtres_et_affichage(bottin["SGP"], "sgp")

    with tab_sdb:
        st.markdown("### Sociétés de Bourse (SDB)")
        filtres_et_affichage(bottin["SDB"], "sdb")

    with tab_inv:
        st.markdown("### Investisseurs institutionnels")
        st.caption("Liste des investisseurs institutionnels enregistrés et validés sur le marché CEMAC.")
        filtres_et_affichage(bottin["Investisseurs"], "inv")
