import streamlit as st
import os
import pandas as pd
from data.loader import get_documents_meta

def show():
    if not st.session_state.get("authenticated", False):
        st.warning(":material/lock: Cette section est réservée aux utilisateurs enregistrés.")
        if st.button(":material/login: Se connecter"):
            st.session_state["page"] = "Connexion"; st.rerun()
        return

    st.title("Espace documentaire")
    st.caption("Bibliothèque complète de documents téléchargeables — rapports, études, guides, textes réglementaires.")

    df_docs = get_documents_meta()
    if df_docs.empty:
        st.info("Aucun document — alimentez la feuille **DOCUMENTS_META** de l'Excel.")
        return

    # Filtres
    cats = df_docs["categorie"].dropna().unique().tolist() if "categorie" in df_docs.columns else []
    acces_opts = df_docs["acces"].dropna().unique().tolist() if "acces" in df_docs.columns else []

    c1, c2, c3 = st.columns([2,1,2])
    with c1:
        cat_sel = st.multiselect(":material/filter_list: Catégorie", options=cats, default=cats)
    with c2:
        acces_sel = st.selectbox(":material/lock_open: Accès", ["Tous"] + acces_opts)
    with c3:
        search = st.text_input(":material/search: Mot-clé", placeholder="Rechercher...")

    df_f = df_docs.copy()
    if cat_sel and "categorie" in df_f.columns:
        df_f = df_f[df_f["categorie"].isin(cat_sel)]
    if acces_sel != "Tous" and "acces" in df_f.columns:
        df_f = df_f[df_f["acces"] == acces_sel]
    if search and "titre" in df_f.columns:
        df_f = df_f[df_f["titre"].str.contains(search, case=False, na=False)]

    st.markdown(f"<div style='font-size:0.82rem;color:#8C8C8C;margin-bottom:0.5rem;'>{len(df_f)} document(s)</div>",
                unsafe_allow_html=True)

    for _, row in df_f.iterrows():
        col_cat, col_ti, col_date, col_dl = st.columns([1.5, 4, 1.5, 1])
        cat = str(row.get("categorie",""))
        acces = str(row.get("acces","Public"))
        color = "#003366" if acces.lower() == "restreint" else "#9E7B28"
        with col_cat:
            st.markdown(f"<span style='background:{color};color:white;padding:2px 8px;"
                        f"border-radius:3px;font-size:0.72rem;font-weight:700'>{cat}</span>",
                        unsafe_allow_html=True)
        with col_ti:
            taille = str(row.get("taille",""))
            st.markdown(f"**{row.get('titre','')}** · {taille}")
        with col_date:
            date = str(row.get("date_publication",""))[:10]
            st.markdown(f"<span style='font-size:0.83rem;color:#8C8C8C;'>{date}</span>",
                        unsafe_allow_html=True)
        with col_dl:
            chemin = str(row.get("chemin_fichier",""))
            titre_court = str(row.get("titre","doc"))[:20].replace(" ","_")
            if chemin and os.path.exists(chemin):
                with open(chemin, "rb") as f:
                    st.download_button(":material/download:", f.read(),
                        file_name=os.path.basename(chemin),
                        key=f"doc_{titre_court}_{_}")
            else:
                st.button(":material/download:", key=f"doc_{titre_court}_{_}",
                          disabled=True, help="Fichier non disponible")
        st.markdown("<hr style='margin:0.3rem 0; border:none; border-top:1px solid #EAE8E2;'>",
                    unsafe_allow_html=True)
