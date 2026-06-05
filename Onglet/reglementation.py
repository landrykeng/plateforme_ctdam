import streamlit as st
import os
from data.loader import get_reglementation, get_publications, get_faq, PAYS_CEMAC

# ── Réglementation ────────────────────────────────────────────────────────────
def show_reglementation():
    st.title("Réglementation applicable")
    st.markdown("Bibliothèque des textes réglementaires du marché des valeurs du Trésor CEMAC.")

    docs = get_reglementation()

    # Fallback si Excel vide
    if not docs:
        docs = [
            {"titre":"Règlement n°01/24/CEMAC/UMAC — Émission des valeurs du Trésor",
             "categorie":"Règlement","ref":"CEMAC/01/2024","date":"2024-01-15","acces":"Public","chemin":""},
            {"titre":"Instruction n°03/23 — Procédures d'adjudication sur le marché primaire",
             "categorie":"Instruction","ref":"BEAC/CRCT/003/2023","date":"2023-07-10","acces":"Public","chemin":""},
            {"titre":"Circulaire n°12/23 — Accréditation des SVT",
             "categorie":"Circulaire","ref":"BEAC/CRCT/012/2023","date":"2023-09-01","acces":"Public","chemin":""},
        ]

    cat_options = ["Tous"] + sorted(list({d.get("categorie","") for d in docs if d.get("categorie")}))
    cat_filter = st.selectbox(":material/filter_list: Filtrer par catégorie", cat_options)
    docs_f = docs if cat_filter == "Tous" else [d for d in docs if d.get("categorie","") == cat_filter]

    badge_colors = {"Règlement":"#003366","Instruction":"#C8A84B",
                    "Circulaire":"#004080","Règle de cotation":"#9E7B28"}

    for doc in docs_f:
        color = badge_colors.get(doc.get("categorie",""), "#8C8C8C")
        with st.expander(f"**{doc['titre']}**"):
            col1, col2, col3 = st.columns([2,1,1])
            with col1:
                st.markdown(f"<span style='background:{color};color:white;padding:3px 10px;"
                    f"border-radius:3px;font-size:0.75rem;font-weight:700'>{doc.get('categorie','')}</span>",
                    unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Référence :** {doc.get('ref','')}")
            with col3:
                st.markdown(f"**Date :** {doc.get('date','')}")

            chemin = doc.get("chemin","")
            if chemin and os.path.exists(chemin):
                with open(chemin, "rb") as f:
                    st.download_button(":material/download: Télécharger (PDF)",
                        f.read(), file_name=os.path.basename(chemin),
                        mime="application/pdf",
                        key=f"dl_{doc.get('ref','').replace('/','_')}")
            else:
                st.markdown("*Document disponible en téléchargement pour les utilisateurs enregistrés.*")
                st.button(":material/download: Télécharger (PDF)",
                    key=f"dl_{doc.get('ref','').replace('/','_')}",
                    disabled=not st.session_state.get("authenticated", False))


# ── Guide de l'investisseur ───────────────────────────────────────────────────
def show_guide():
    st.title("Guide de l'investisseur")
    st.markdown("*Section pédagogique à destination des investisseurs souhaitant participer au marché des valeurs du Trésor de la CEMAC.*")

    tabs = st.tabs([
        ":material/info: Présentation du marché",
        ":material/assignment: Procédures",
        ":material/description: Instruments",
        ":material/person_add: Critères d'éligibilité",
        ":material/glossary: Glossaire",
    ])

    with tabs[0]:
        st.markdown("### Le marché des valeurs du Trésor CEMAC")
        st.markdown("""
Le marché des valeurs du Trésor de la CEMAC est le cadre dans lequel les États membres émettent des 
titres de créance pour financer leurs besoins de trésorerie et leurs investissements. Il est organisé 
et supervisé par la **BEAC** via le **CRCT**.

**Les acteurs principaux :**
- **BEAC/CRCT** : Organisateur des adjudications et garant de la transparence du marché
- **SVT** : Institutions financières agréées, intermédiaires obligatoires sur le marché primaire
- **SGP** : Gestionnaires d'actifs intervenant sur le marché secondaire
- **SDB** : Intermédiaires agréés sur les bourses régionales
- **Investisseurs** : Institutionnels, banques, entreprises, personnes physiques qualifiées
        """)

    with tabs[1]:
        st.markdown("### Comment participer aux adjudications")
        steps = [
            (":material/how_to_reg:", "1. Créer un compte","Remplissez le formulaire d'inscription et joignez vos pièces justificatives."),
            (":material/verified:", "2. Validation BEAC","L'administrateur examine votre dossier et valide sous 5 jours ouvrés."),
            (":material/contacts:", "3. Choisir un SVT","Identifiez un SVT accrédité dans le Bottin et ouvrez un compte."),
            (":material/gavel:", "4. Soumettre une offre","Transmettez votre offre (montant, taux) à votre SVT avant l'heure limite."),
            (":material/receipt:", "5. Résultats","Les résultats sont publiés le jour même."),
        ]
        for icon, titre, desc in steps:
            st.markdown(f"""
            <div class="app-card" style="margin-bottom:0.8rem; display:flex; align-items:flex-start; gap:1rem;">
                <div><div style="font-weight:700; color:#003366;">{titre}</div>
                <div style="font-size:0.9rem; color:#4A4A4A;">{desc}</div></div>
            </div>""", unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("### Les instruments disponibles")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class="app-card">
                <div style="font-weight:700;color:#003366;font-size:1rem;margin-bottom:0.5rem;">
                 Bons du Trésor Assimilables (BTA)</div>
                <div style="font-size:0.88rem;color:#4A4A4A;line-height:1.6;">
                <b>Maturités :</b> 13, 26 ou 52 semaines<br>
                <b>Usage :</b> Financement de la trésorerie à court terme<br>
                <b>Taux :</b> Déterminé par adjudication<br>
                <b>Minimum :</b> 1 000 000 XAF</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class="app-card">
                <div style="font-weight:700;color:#003366;font-size:1rem;margin-bottom:0.5rem;">
                 Obligations du Trésor Assimilables (OTA)</div>
                <div style="font-size:0.88rem;color:#4A4A4A;line-height:1.6;">
                <b>Maturités :</b> 2, 3, 5, 7, 10 ou 15 ans<br>
                <b>Usage :</b> Financement des investissements publics<br>
                <b>Coupon :</b> Annuel, taux fixe<br>
                <b>Minimum :</b> 10 000 XAF</div></div>""", unsafe_allow_html=True)

    with tabs[3]:
        profils = [
            ("Investisseurs institutionnels","Compagnies d'assurance, caisses de prévoyance, OPCVMs. Accès direct via SVT.","Actif"),
            ("Banques commerciales","Établissements de crédit agréés dans la zone CEMAC.","Actif"),
            ("Entreprises","Sociétés souhaitant placer leur trésorerie. Accès via SVT ou SDB.","Actif"),
            ("Personnes physiques qualifiées","Investisseurs individuels avec patrimoine financier significatif.","Restreint"),
            ("Investisseurs non-résidents","Tout investisseur hors CEMAC. Processus de validation renforcé.","Restreint"),
        ]
        for nom, desc, acc in profils:
            badge = (f"<span style='background:{'#003366' if acc=='Actif' else '#C8A84B'};"
                     f"color:white;padding:2px 8px;border-radius:3px;font-size:0.72rem;'>{acc}</span>")
            with st.expander(f"**{nom}**", expanded=False):
                st.markdown(desc)

    with tabs[4]:
        termes = [
            ("Adjudication","Processus par lequel le Trésor émet des valeurs du Trésor sur la base d'offres et de prix offerts par les différents Spécialistes des Valeurs du Trésor soumissionnaires"),
            ("Taux marginal","Taux limite à partir duquel les offres sont retenues."),
            ("TRMP","Taux de Rendement Moyen Pondéré — moyenne pondérée par les montants retenus."),
            ("Taux de couverture","Ratio montant total des offres / montant mis en adjudication."),
            ("Code ISIN","Identifiant international unique à 12 caractères attribué à chaque émission."),
            ("Marché primaire","Marché sur lequel les nouvelles émissions sont vendues pour la première fois."),
            ("Marché secondaire","Marché sur lequel les titres déjà émis sont négociés entre investisseurs."),
            ("SVT","Spécialiste en Valeurs du Trésor — intermédiaire obligatoire sur le marché primaire."),
            ("Encours","Montant total des titres en circulation non encore remboursés."),
            ("Duration","Mesure de la sensibilité du prix d'un titre aux variations de taux, en années."),
            ("Convexité","Mesure de la courbure de la relation prix/rendement d'une obligation."),
            ("Spread","Écart de taux entre un titre et un taux de référence, exprimé en points de base."),
        ]
        for terme, definition in termes:
            with st.expander(f"**{terme}**"):
                st.markdown(definition)


# ── Publications ──────────────────────────────────────────────────────────────
def show_publications():
    st.title("Publications officielles")
    st.caption("Bulletins trimestriels, rapports annuels et notes de marché.")

    df_pubs = get_publications()
    if df_pubs.empty:
        st.info("Aucune publication — alimentez la feuille **DOCUMENTS_META** de l'Excel.")
        return

    cat_dispo = df_pubs["categorie"].dropna().unique().tolist() if "categorie" in df_pubs.columns else []
    col1, col2 = st.columns([1,2])
    with col1:
        cat_sel = st.multiselect(":material/filter_list: Catégorie", options=cat_dispo, default=cat_dispo)
    with col2:
        search = st.text_input(":material/search: Rechercher", placeholder="Mot-clé...")

    df_f = df_pubs.copy()
    if cat_sel and "categorie" in df_f.columns:
        df_f = df_f[df_f["categorie"].isin(cat_sel)]
    if search and "titre" in df_f.columns:
        df_f = df_f[df_f["titre"].str.contains(search, case=False, na=False)]

    for _, row in df_f.iterrows():
        col_i, col_t, col_d = st.columns([1,4,1])
        with col_i:
            st.markdown(f"<span class='badge-nouveau'>{row.get('categorie','')}</span>", unsafe_allow_html=True)
        with col_t:
            titre = row.get("titre","")
            date = str(row.get("date",""))[:10]
            taille = row.get("taille","")
            st.markdown(f"**{titre}** — {date} · {taille}")
        with col_d:
            chemin = row.get("chemin_fichier","")
            if chemin and os.path.exists(str(chemin)):
                with open(chemin, "rb") as f:
                    st.download_button(":material/download: PDF", f.read(),
                        file_name=os.path.basename(chemin),
                        key=f"pub_{row.get('reference','').replace('/','_')}")
            else:
                st.button(":material/download: PDF", disabled=True,
                    key=f"pub_{row.get('titre','')[:20].replace(' ','_')}")
        st.markdown("<hr style='margin:0.4rem 0; border:none; border-top:1px solid #EAE8E2;'>",
                    unsafe_allow_html=True)


# ── FAQ ───────────────────────────────────────────────────────────────────────
def show_faq():
    st.title("Foire Aux Questions")
    st.markdown("*Réponses aux questions fréquentes sur le marché des valeurs du Trésor de la CEMAC.*")

    faqs = get_faq()
    search = st.text_input(":material/search: Rechercher dans la FAQ",
                           placeholder="Ex : BTA, adjudication, investisseur...")
    faqs_f = faqs if not search else [
        f for f in faqs if search.lower() in f["question"].lower() or search.lower() in f["reponse"].lower()
    ]
    for faq in faqs_f:
        with st.expander(f":material/help: **{faq['question']}**"):
            st.markdown(faq["reponse"])

    st.markdown("---")
    st.info(":material/mail: Vous ne trouvez pas votre réponse ? Contactez-nous à **crct@beac.int**")
