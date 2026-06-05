import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data.loader import (get_encours_mensuels, get_courbe_taux,
                          get_detenteurs, encours_par_pays, PAYS_CEMAC)

def show():
    st.title("Statistiques agrégées du marché")
    st.caption("Données consolidées de la zone CEMAC — mise à jour mensuelle par l'administrateur BEAC")

    tab1, tab2, tab3 = st.tabs([
        ":material/timeline: Évolution des encours",
        ":material/show_chart: Courbe de taux",
        ":material/donut_large: Répartition des détenteurs",
    ])

    df_enc = get_encours_mensuels()

    # ── Tab 1 : Encours ────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Évolution mensuelle des encours par pays (M XAF)")
        if df_enc.empty:
            st.info("Aucune donnée — alimentez la feuille ENCOURS_MENSUEL de l'Excel.")
        else:
            pays_dispo = df_enc["pays_nom"].dropna().unique().tolist() if "pays_nom" in df_enc.columns else []
            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                pays_choix = st.multiselect("Filtrer par pays", options=pays_dispo,
                                            default=pays_dispo[:3] if len(pays_dispo) >= 3 else pays_dispo)
            with col_f2:
                inst_choix = st.selectbox("Instrument", ["Tous", "BTA", "OTA"])

            df_f = df_enc.copy()
            if pays_choix and "pays_nom" in df_f.columns:
                df_f = df_f[df_f["pays_nom"].isin(pays_choix)]
            if inst_choix != "Tous" and "instrument" in df_f.columns:
                df_f = df_f[df_f["instrument"] == inst_choix]

            if "mois" in df_f.columns and "pays_nom" in df_f.columns and "encours" in df_f.columns:
                df_pivot = df_f.groupby(["mois", "pays_nom"])["encours"].sum().reset_index()
                fig = px.line(df_pivot, x="mois", y="encours", color="pays_nom",
                    color_discrete_sequence=["#003366","#C8A84B","#004080","#9E7B28","#0055a5","#E2C97A"],
                    labels={"mois":"Mois","encours":"Encours (M XAF)","pays_nom":"Pays"})
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Source Sans 3", size=12),
                    xaxis=dict(tickangle=-30, gridcolor="#EAE8E2"),
                    yaxis=dict(gridcolor="#EAE8E2", title="Millions XAF"),
                    legend=dict(title=""), margin=dict(l=0,r=0,t=10,b=0), height=380)
                st.plotly_chart(fig, use_container_width=True)

            # Graphique dernier mois
            df_last = df_enc.copy()
            if "mois" in df_last.columns:
                last = df_last["mois"].astype(str).max()
                df_last = df_last[df_last["mois"].astype(str) == last]
            if "pays_nom" in df_last.columns and "instrument" in df_last.columns:
                df_bar = df_last.groupby(["pays_nom","instrument"])["encours"].sum().reset_index()
                fig2 = px.bar(df_bar, x="pays_nom", y="encours", color="instrument",
                    barmode="group",
                    color_discrete_map={"BTA":"#003366","OTA":"#C8A84B"},
                    labels={"pays_nom":"Pays","encours":"Encours (M XAF)","instrument":"Instrument"})
                fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Source Sans 3"),
                    margin=dict(l=0,r=0,t=10,b=0), height=320)
                st.markdown("### Encours par pays et instrument — dernier mois disponible")
                st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 2 : Courbe de taux ─────────────────────────────────────────────────
    with tab2:
        st.markdown("### Courbe de taux du marché CEMAC")
        df_taux = get_courbe_taux()
        if df_taux.empty:
            st.info("Aucune donnée — alimentez la feuille COURBE_TAUX de l'Excel.")
        else:
            fig3 = go.Figure()
            fig3.add_scatter(x=df_taux.get("maturite", []), y=df_taux.get("taux_actuel", []),
                mode="lines+markers", name="Taux actuel",
                line=dict(color="#003366", width=2.5),
                marker=dict(size=7, color="#C8A84B", line=dict(color="#003366", width=1.5)))
            if "taux_n1" in df_taux.columns:
                fig3.add_scatter(x=df_taux["maturite"], y=df_taux["taux_n1"],
                    mode="lines+markers", name="N-1",
                    line=dict(color="#8C8C8C", width=1.5, dash="dot"),
                    marker=dict(size=5, color="#8C8C8C"))
            fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Source Sans 3", size=12),
                xaxis=dict(title="Maturité", gridcolor="#EAE8E2"),
                yaxis=dict(title="Taux (%)", gridcolor="#EAE8E2"),
                legend=dict(orientation="h", y=1.1),
                margin=dict(l=0,r=0,t=20,b=0), height=380)
            st.plotly_chart(fig3, use_container_width=True)

            cols_display = [c for c in ["maturite","taux_actuel","taux_cmr","taux_gab",
                                         "taux_cog","taux_n1"] if c in df_taux.columns]
            rename = {"maturite":"Maturité","taux_actuel":"Taux CEMAC (%)","taux_cmr":"CMR",
                      "taux_gab":"GAB","taux_cog":"COG","taux_n1":"N-1 (%)"}
            st.dataframe(df_taux[cols_display].rename(columns=rename),
                         use_container_width=True, hide_index=True)

    # ── Tab 3 : Détenteurs ─────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Ventilation des encours par catégorie de détenteurs")
        repartition = get_detenteurs()
        if not repartition:
            st.info("Aucune donnée — alimentez la feuille DETENTEURS de l'Excel.")
        else:
            labels = list(repartition.keys())
            values = list(repartition.values())
            fig4 = go.Figure(go.Pie(
                labels=labels, values=values, hole=.45,
                marker=dict(colors=["#003366","#C8A84B","#004080","#9E7B28","#EAE8E2"],
                            line=dict(color="white", width=2)),
                textinfo="label+percent",
                textfont=dict(family="Source Sans 3", size=12)))
            fig4.update_layout(paper_bgcolor="white",
                font=dict(family="Source Sans 3"),
                legend=dict(orientation="v"),
                margin=dict(l=0,r=0,t=10,b=0), height=380,
                annotations=[dict(text="Détenteurs", x=0.5, y=0.5,
                    font_size=13, showarrow=False, font_color="#003366")])
            st.plotly_chart(fig4, use_container_width=True)
            df_rep = pd.DataFrame({"Catégorie": labels, "Part (%)": values})
            st.dataframe(df_rep, use_container_width=True, hide_index=True)

    st.caption(":material/info: Les statistiques agrégées sont calculées depuis la base de données Excel. L'espace restreint donne accès aux données détaillées.")
