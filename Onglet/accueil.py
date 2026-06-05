import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data.loader import stats_marche_public, encours_par_pays, get_dernières_emissions, PAYS_CEMAC

def show():
    stats = stats_marche_public()

    st.title("Marché des Valeurs du Trésor de la CEMAC")
    st.markdown("""
    <p style="font-size:1.05rem; color:#4A4A4A; line-height:1.7; max-width:800px;">
    Bienvenue sur le portail officiel d'information et de répertoire du marché des valeurs 
    du Trésor de la Communauté Économique et Monétaire de l'Afrique Centrale (CEMAC), 
    géré par la <strong>BEAC</strong> et le <strong>CRCT</strong>.
    </p>
    """, unsafe_allow_html=True)

    # ── Chiffres clés ──────────────────────────────────────────────────────────
    st.markdown("## Chiffres clés du marché")
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, stats["encours_global"],        "Encours global",         ":material/account:"),
        (c2, str(stats["nb_svt_actifs"]),    "SVT accrédités actifs",  ":material/groups:"),
        (c3, stats["volumes_annuels"],        "Volumes émis (12 mois)", ":material/trending_up:"),
        (c4, stats["taux_couverture_moyen"], "Taux de couverture moy.", ":material/ chart:"),
    ]
    for col, val, label, icon in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    cards2 = [
        (c5, str(stats["nb_pays"]),              "États membres CEMAC",       ":material/public:"),
        (c6, stats["dernier_taux_bta_13s"],      "Dernier taux BTA 13 sem.",  ":material/percent:"),
        (c7, str(stats["nb_adjudications_annee"]),"Adjudications (12 mois)",  ":material/gavel:"),
        (c8, str(stats["instruments_codes"]),     "Codes ISIN actifs",         ":material/description:"),
    ]
    for col, val, label, icon in cards2:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Graphique encours par pays ─────────────────────────────────────────────
    col_g, col_t = st.columns([3, 2])
    with col_g:
        st.markdown("## Encours par État membre (Mds XAF)")
        df_pays = encours_par_pays()
        if not df_pays.empty:
            fig = go.Figure()
            fig.add_bar(x=df_pays["pays"], y=df_pays["BTA"]/1000, name="BTA", marker_color="#003366")
            fig.add_bar(x=df_pays["pays"], y=df_pays["OTA"]/1000, name="OTA", marker_color="#C8A84B")
            fig.update_layout(
                barmode="stack", plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Source Sans 3", size=12),
                legend=dict(orientation="h", y=1.1),
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(title="Mds XAF", gridcolor="#EAE8E2"),
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données d'encours non disponibles — alimentez la feuille ENCOURS_MENSUEL.")

    with col_t:
        st.markdown("## Tableau récapitulatif")
        if not df_pays.empty:
            disp = df_pays.copy()
            disp["BTA"] = (disp["BTA"]/1000).round(1).astype(str) + " Mds"
            disp["OTA"] = (disp["OTA"]/1000).round(1).astype(str) + " Mds"
            disp["total"] = (disp["total"]/1000).round(1).astype(str) + " Mds"
            disp.columns = ["Pays","BTA","OTA","Total (XAF)"]
            st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée.")

    # ── Dernières émissions ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## Dernières émissions publiées")
    df_em = get_dernières_emissions(8)
    if not df_em.empty:
        cols_show = [c for c in ["pays_nom","instrument","maturite","date_souscription",
                                  "montant_leve","trmp","taux_couverture","statut"] if c in df_em.columns]
        rename = {"pays_nom":"Pays","instrument":"Instrument","maturite":"Maturité",
                  "date_souscription":"Date","montant_leve":"Montant levé (M)","trmp":"TRMP (%)",
                  "taux_couverture":"Couverture","statut":"Statut"}
        st.dataframe(df_em[cols_show].rename(columns=rename),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Aucune émission enregistrée — alimentez la feuille EMISSIONS.")

    st.markdown("---")
    # ── Modules ───────────────────────────────────────────────────────────────
    st.markdown("## Accès aux modules")
    modules = [
        (":material/gavel:", "Résultats des adjudications","Consultez les derniers résultats par pays et instrument."),
        (":material/menu_book:", "Réglementation","Accédez aux textes réglementaires, circulaires et règles de cotation."),
        (":material/school:", "Guide de l'investisseur","Comprenez les procédures, instruments et critères d'éligibilité."),
        (":material/bar_chart:", "Statistiques publiques","Encours, courbe de taux, répartition détenteurs."),
        (":material/article:", "Publications officielles","Bulletins trimestriels et rapports annuels."),
        (":material/help:", "FAQ","Réponses aux questions fréquentes."),
    ]
    cols = st.columns(3)
    for i, (icon, titre, desc) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="app-card" style="margin-bottom:1rem;">
                <div style="font-weight:700; color:#003366; font-size:1rem; margin-bottom:0.3rem;">{titre}</div>
                <div style="font-size:0.87rem; color:#4A4A4A; line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
