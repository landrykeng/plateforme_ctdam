import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data.loader import (get_emissions, get_encours_mensuels,
                          get_courbe_taux, PAYS_CEMAC)

def show():
    if not st.session_state.get("authenticated", False):
        st.warning(":material/lock: Cette section est réservée aux utilisateurs enregistrés et validés.")
        if st.button(":material/login: Se connecter"):
            st.session_state["page"] = "Connexion"; st.rerun()
        return

    st.title("Données historiques du marché")
    st.caption("Historique complet — encours, adjudications, taux.")

    tab1, tab2, tab3 = st.tabs([
        ":material/storage: Encours par État et instrument",
        ":material/gavel: Résultats des adjudications",
        ":material/show_chart: Taux et rendements",
    ])

    df_enc = get_encours_mensuels()
    df_adj = get_emissions()

    # ── Tab 1 : Encours ────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Évolution des encours mensuels")
        if df_enc.empty:
            st.info("Alimentez la feuille **ENCOURS_MENSUEL** de l'Excel.")
        else:
            pays_dispo = sorted(df_enc["pays_nom"].dropna().unique().tolist()) if "pays_nom" in df_enc.columns else []
            c1, c2, c3 = st.columns(3)
            with c1:
                pays_sel = st.multiselect("Pays", options=pays_dispo, default=pays_dispo, key="enc_pays")
            with c2:
                inst_sel = st.selectbox("Instrument", ["Tous","BTA","OTA"], key="enc_inst")
            with c3:
                mois_dispo = sorted(df_enc["mois"].astype(str).unique().tolist(), reverse=True) if "mois" in df_enc.columns else []
                vmin=min(24, len(mois_dispo)) if mois_dispo else 12
                vmax=max(12, len(mois_dispo)) if mois_dispo else 12
                vmin
                vmax
                periode = st.slider("Derniers N mois", 3, vmin,vmax)

            df_f = df_enc.copy()
            if pays_sel and "pays_nom" in df_f.columns:
                df_f = df_f[df_f["pays_nom"].isin(pays_sel)]
            if inst_sel != "Tous" and "instrument" in df_f.columns:
                df_f = df_f[df_f["instrument"] == inst_sel]
            if "mois" in df_f.columns and mois_dispo:
                dates_keep = mois_dispo[:periode]
                df_f = df_f[df_f["mois"].astype(str).isin(dates_keep)]

            if not df_f.empty and "mois" in df_f.columns and "pays_nom" in df_f.columns:
                df_pivot = df_f.groupby(["mois","pays_nom"])["encours"].sum().reset_index()
                fig = px.area(df_pivot, x="mois", y="encours", color="pays_nom",
                    color_discrete_sequence=["#003366","#C8A84B","#004080","#9E7B28","#0055a5","#E2C97A"],
                    labels={"mois":"Mois","encours":"Encours (M XAF)","pays_nom":"Pays"})
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Source Sans 3", size=12),
                    xaxis=dict(tickangle=-30, gridcolor="#EAE8E2"),
                    yaxis=dict(gridcolor="#EAE8E2"), height=380,
                    legend=dict(title=""), margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Tableau détaillé")
            if "pays_nom" in df_f.columns and "instrument" in df_f.columns:
                df_table = df_f.groupby(["mois","pays_nom","instrument"])["encours"].sum().reset_index()
                df_table.columns = ["Mois","Pays","Instrument","Encours (M XAF)"]
                df_table["Encours (M XAF)"] = df_table["Encours (M XAF)"].apply(lambda x: f"{x:,.0f}")
                st.dataframe(df_table, use_container_width=True, hide_index=True)
                csv = df_f.to_csv(index=False).encode("utf-8")
                st.download_button(":material/download: Exporter CSV", csv, "encours_historique.csv", key="dl_enc")

    # ── Tab 2 : Adjudications ─────────────────────────────────────────────────
    with tab2:
        st.markdown("### Résultats des adjudications")
        if df_adj.empty:
            st.info("Alimentez la feuille **EMISSIONS** de l'Excel.")
        else:
            pays_dispo2 = sorted(df_adj["pays_nom"].dropna().unique().tolist()) if "pays_nom" in df_adj.columns else []
            c1, c2, c3 = st.columns(3)
            with c1:
                pays_a = st.multiselect("Pays", options=pays_dispo2, default=pays_dispo2, key="adj_pays")
            with c2:
                inst_a = st.selectbox("Instrument", ["Tous","BTA","OTA"], key="adj_inst")
            with c3:
                statuts = sorted(df_adj["statut"].dropna().unique().tolist()) if "statut" in df_adj.columns else []
                statut_a = st.selectbox("Statut", ["Tous"] + statuts, key="adj_statut")

            df_af = df_adj.copy()
            if pays_a and "pays_nom" in df_af.columns:
                df_af = df_af[df_af["pays_nom"].isin(pays_a)]
            if inst_a != "Tous" and "instrument" in df_af.columns:
                df_af = df_af[df_af["instrument"] == inst_a]
            if statut_a != "Tous" and "statut" in df_af.columns:
                df_af = df_af[df_af["statut"] == statut_a]

            cols_show = [c for c in ["date_souscription","pays_nom","instrument","maturite",
                                      "montant_emis","montant_leve","trmp","taux_couverture",
                                      "code_long","statut"] if c in df_af.columns]
            rename = {"date_souscription":"Date","pays_nom":"Pays","instrument":"Instrument",
                      "maturite":"Maturité","montant_emis":"Émis (M)","montant_leve":"Levé (M)",
                      "trmp":"TRMP (%)","taux_couverture":"Couverture","code_long":"Code ISIN","statut":"Statut"}
            st.dataframe(df_af[cols_show].rename(columns=rename),
                         use_container_width=True, hide_index=True)
            csv2 = df_af.to_csv(index=False).encode("utf-8")
            st.download_button(":material/download: Exporter CSV", csv2, "adjudications.csv", key="dl_adj")

    # ── Tab 3 : Taux ──────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Courbe de taux interactive")
        df_taux = get_courbe_taux()
        if df_taux.empty:
            st.info("Alimentez la feuille **COURBE_TAUX** de l'Excel.")
        else:
            fig2 = go.Figure()
            fig2.add_scatter(x=df_taux.get("maturite",[]), y=df_taux.get("taux_actuel",[]),
                mode="lines+markers", name="Taux actuel",
                line=dict(color="#003366", width=2.5),
                marker=dict(size=8, color="#C8A84B", line=dict(color="#003366",width=1.5)))
            if "taux_n1" in df_taux.columns:
                fig2.add_scatter(x=df_taux["maturite"], y=df_taux["taux_n1"],
                    mode="lines+markers", name="N-1",
                    line=dict(color="#8C8C8C", width=1.5, dash="dot"),
                    marker=dict(size=5))
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Source Sans 3", size=12),
                xaxis=dict(title="Maturité", gridcolor="#EAE8E2"),
                yaxis=dict(title="Taux (%)", gridcolor="#EAE8E2"),
                height=350, margin=dict(l=0,r=0,t=20,b=0),
                legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Évolution des TRMP par adjudication")
        if not df_adj.empty and "trmp" in df_adj.columns and "date_souscription" in df_adj.columns:
            df_rp = df_adj.dropna(subset=["trmp"]).copy()
            df_rp["trmp"] = pd.to_numeric(df_rp["trmp"], errors="coerce")
            df_rp = df_rp[df_rp["trmp"] > 0]
            if not df_rp.empty:
                size_col = "montant_leve" if "montant_leve" in df_rp.columns else None
                hover = [c for c in ["pays_nom","maturite","taux_couverture"] if c in df_rp.columns]
                fig3 = px.scatter(df_rp, x="date_souscription", y="trmp",
                    color="instrument" if "instrument" in df_rp.columns else None,
                    size=size_col if size_col else None,
                    hover_data=hover,
                    color_discrete_map={"BTA":"#003366","OTA":"#C8A84B"},
                    labels={"date_souscription":"Date","trmp":"TRMP (%)","instrument":"Instrument"})
                fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Source Sans 3"), height=340,
                    xaxis=dict(gridcolor="#EAE8E2", tickangle=-30),
                    yaxis=dict(gridcolor="#EAE8E2"), margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig3, use_container_width=True)
