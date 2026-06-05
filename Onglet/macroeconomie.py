"""
Onglet Macroéconomie — dette, PIB, inflation, ratios CEMAC
Accessible : Investisseur validé + Opérateur
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data.loader import get_pays_macro, PAYS_CEMAC

def show():
    if not st.session_state.get("authenticated", False):
        st.warning(":material/lock: Cette section est réservée aux utilisateurs enregistrés.")
        if st.button(":material/login: Se connecter"):
            st.session_state["page"] = "Connexion"; st.rerun()
        return

    st.title("Environnement macroéconomique")
    st.caption("Indicateurs macroéconomiques des États membres de la CEMAC.")

    df = get_pays_macro()
    if df.empty:
        st.info("Aucune donnée — alimentez la feuille **PAYS_MACRO** de l'Excel.")
        return

    # Filtres
    annees = sorted(df["annee"].dropna().unique().tolist(), reverse=True) if "annee" in df.columns else []
    c1, c2 = st.columns([1, 3])
    with c1:
        annee_sel = st.selectbox("Année", annees) if annees else None
    with c2:
        pays_dispo = sorted(df["pays"].dropna().unique().tolist()) if "pays" in df.columns else []
        pays_sel = st.multiselect("Pays", options=pays_dispo, default=pays_dispo)

    df_f = df.copy()
    if annee_sel and "annee" in df_f.columns:
        df_f = df_f[df_f["annee"] == annee_sel]
    if pays_sel and "pays" in df_f.columns:
        df_f = df_f[df_f["pays"].isin(pays_sel)]

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/account_balance: Dette publique",
        ":material/trending_up: Croissance & Inflation",
        ":material/receipt: Finances publiques",
        ":material/table_view: Tableau complet",
    ])

    color_seq = ["#003366","#C8A84B","#004080","#9E7B28","#0055a5","#E2C97A"]

    with tab1:
        st.markdown("### Dette publique et service de la dette")
        if "dette_pib" in df_f.columns and "pays" in df_f.columns:
            c_a, c_b = st.columns(2)
            with c_a:
                fig = px.bar(df_f, x="pays", y="dette_pib",
                    color="pays", color_discrete_sequence=color_seq,
                    labels={"pays":"Pays","dette_pib":"Dette / PIB (%)"},
                    title="Ratio Dette / PIB (%)")
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    showlegend=False, height=320, margin=dict(l=0,r=0,t=40,b=0))
                fig.add_hline(y=70, line_dash="dot", line_color="red",
                              annotation_text="Seuil CEMAC 70%", annotation_position="top right")
                st.plotly_chart(fig, use_container_width=True)
            with c_b:
                if "service_dette_recettes" in df_f.columns:
                    fig2 = px.bar(df_f, x="pays", y="service_dette_recettes",
                        color="pays", color_discrete_sequence=color_seq,
                        labels={"pays":"Pays","service_dette_recettes":"Service dette / Recettes (%)"},
                        title="Service de la dette / Recettes fiscales (%)")
                    fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                        showlegend=False, height=320, margin=dict(l=0,r=0,t=40,b=0))
                    st.plotly_chart(fig2, use_container_width=True)

        if "dette_totale" in df_f.columns:
            # Évolution multi-années
            df_all = get_pays_macro()
            if pays_sel and "pays" in df_all.columns:
                df_all = df_all[df_all["pays"].isin(pays_sel)]
            if not df_all.empty and "annee" in df_all.columns and "dette_totale" in df_all.columns:
                fig3 = px.line(df_all, x="annee", y="dette_totale", color="pays",
                    color_discrete_sequence=color_seq,
                    labels={"annee":"Année","dette_totale":"Dette (Mds XAF)","pays":"Pays"},
                    title="Évolution de la dette totale (Mds XAF)")
                fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    height=320, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.markdown("### Croissance du PIB et inflation")
        c_a, c_b = st.columns(2)
        with c_a:
            if "croissance_pib" in df_f.columns:
                fig = px.bar(df_f, x="pays", y="croissance_pib",
                    color="pays", color_discrete_sequence=color_seq,
                    labels={"pays":"Pays","croissance_pib":"Croissance (%)"},
                    title="Croissance du PIB (%)")
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    showlegend=False, height=320, margin=dict(l=0,r=0,t=40,b=0))
                fig.add_hline(y=0, line_color="gray", line_dash="dash")
                st.plotly_chart(fig, use_container_width=True)
        with c_b:
            if "inflation" in df_f.columns:
                fig2 = px.bar(df_f, x="pays", y="inflation",
                    color="pays", color_discrete_sequence=color_seq,
                    labels={"pays":"Pays","inflation":"Inflation (%)"},
                    title="Taux d'inflation (%)")
                fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    showlegend=False, height=320, margin=dict(l=0,r=0,t=40,b=0))
                fig2.add_hline(y=3, line_dash="dot", line_color="orange",
                               annotation_text="Cible 3%", annotation_position="top right")
                st.plotly_chart(fig2, use_container_width=True)

        # Comparaison PIB
        if "pib" in df_f.columns:
            fig3 = px.pie(df_f, names="pays", values="pib",
                color_discrete_sequence=color_seq,
                title="Répartition du PIB CEMAC")
            fig3.update_layout(height=320, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.markdown("### Finances publiques")
        c_a, c_b = st.columns(2)
        with c_a:
            if "solde_budgetaire" in df_f.columns:
                colors_bar = ["#003366" if v >= 0 else "#C8A84B" for v in df_f["solde_budgetaire"]]
                fig = go.Figure(go.Bar(x=df_f["pays"], y=df_f["solde_budgetaire"],
                    marker_color=colors_bar))
                fig.update_layout(title="Solde budgétaire (% PIB)",
                    plot_bgcolor="white", paper_bgcolor="white",
                    height=320, margin=dict(l=0,r=0,t=40,b=0))
                fig.add_hline(y=0, line_color="gray")
                st.plotly_chart(fig, use_container_width=True)
        with c_b:
            if "recettes_fiscales" in df_f.columns and "depenses" in df_f.columns:
                fig2 = go.Figure()
                fig2.add_bar(name="Recettes fiscales", x=df_f["pays"], y=df_f["recettes_fiscales"],
                    marker_color="#003366")
                fig2.add_bar(name="Dépenses totales", x=df_f["pays"], y=df_f["depenses"],
                    marker_color="#C8A84B")
                fig2.update_layout(title="Recettes vs Dépenses (Mds XAF)",
                    barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                    height=320, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig2, use_container_width=True)

        # Projections
        proj_cols = [c for c in ["pays","proj_recettes","proj_depenses"] if c in df_f.columns]
        if len(proj_cols) == 3:
            st.markdown("#### Projections N+1")
            proj = df_f[proj_cols].rename(columns={"pays":"Pays",
                "proj_recettes":"Recettes projetées (Mds XAF)",
                "proj_depenses":"Dépenses projetées (Mds XAF)"})
            st.dataframe(proj, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("### Tableau complet des indicateurs")
        cols_show = [c for c in ["pays","annee","pib","croissance_pib","inflation",
                                  "dette_totale","dette_pib","service_dette",
                                  "recettes_fiscales","depenses","solde_budgetaire",
                                  "deficit_ext"] if c in df_f.columns]
        rename = {"pays":"Pays","annee":"Année","pib":"PIB (Mds XAF)",
                  "croissance_pib":"Croissance (%)","inflation":"Inflation (%)",
                  "dette_totale":"Dette (Mds XAF)","dette_pib":"Dette/PIB (%)",
                  "service_dette":"Service dette (Mds)","recettes_fiscales":"Recettes (Mds)",
                  "depenses":"Dépenses (Mds)","solde_budgetaire":"Solde budg. (% PIB)",
                  "deficit_ext":"Déficit ext. (% PIB)"}
        st.dataframe(df_f[cols_show].rename(columns=rename),
                     use_container_width=True, hide_index=True)
        csv = df_f.to_csv(index=False).encode("utf-8")
        st.download_button(":material/download: Exporter CSV", csv, "macroeconomie.csv")
