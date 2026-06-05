"""
Onglet Tombée des échéances — coupon + principal par mois
Accessible : Investisseur validé + Opérateur
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data.loader import get_remboursements, get_tombee_echeances, PAYS_CEMAC

def show():
    if not st.session_state.get("authenticated", False):
        st.warning(":material/lock: Cette section est réservée aux utilisateurs enregistrés.")
        if st.button(":material/login: Se connecter"):
            st.session_state["page"] = "Connexion"; st.rerun()
        return

    st.title("Tombée des échéances")
    st.caption("Répartition des remboursements (coupon + principal) par mois et par pays.")

    df_remb = get_remboursements()
    df_tombee = get_tombee_echeances()

    if df_remb.empty:
        st.info("Aucune donnée — alimentez la feuille **REMBOURSEMENTS** de l'Excel.")
        return

    # ── Filtres ───────────────────────────────────────────────────────────────
    pays_dispo = sorted(df_remb["pays_nom"].dropna().unique().tolist()) if "pays_nom" in df_remb.columns else []
    c1, c2 = st.columns(2)
    with c1:
        pays_sel = st.multiselect("Pays", options=pays_dispo, default=pays_dispo)
    with c2:
        natures = sorted(df_remb["nature"].dropna().unique().tolist()) if "nature" in df_remb.columns else []
        nature_sel = st.multiselect("Nature", options=natures, default=natures)

    df_f = df_remb.copy()
    if pays_sel and "pays_nom" in df_f.columns:
        df_f = df_f[df_f["pays_nom"].isin(pays_sel)]
    if nature_sel and "nature" in df_f.columns:
        df_f = df_f[df_f["nature"].isin(nature_sel)]

    # ── KPIs rapides ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    total_du = df_f["montant_du"].sum() if "montant_du" in df_f.columns else 0
    total_coupon = df_f[df_f["nature"].astype(str).str.lower().str.contains("coupon")]["montant_du"].sum() \
        if "nature" in df_f.columns and "montant_du" in df_f.columns else 0
    total_principal = df_f[df_f["nature"].astype(str).str.lower().str.contains("principal")]["montant_du"].sum() \
        if "nature" in df_f.columns and "montant_du" in df_f.columns else 0

    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_du/1000:.1f} Mds</div>
            <div class="metric-label">Total échéances (XAF)</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_coupon/1000:.1f} Mds</div>
            <div class="metric-label">Coupons à payer (XAF)</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_principal/1000:.1f} Mds</div>
            <div class="metric-label">Principal à rembourser (XAF)</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Graphique tombée ──────────────────────────────────────────────────────
    if not df_tombee.empty and "mois" in df_tombee.columns:
        st.markdown("### Tombée des échéances par mois (M XAF)")
        fig = go.Figure()
        if "coupon" in df_tombee.columns:
            fig.add_bar(x=df_tombee["mois"], y=df_tombee["coupon"],
                name="Coupons", marker_color="#C8A84B")
        if "principal" in df_tombee.columns:
            fig.add_bar(x=df_tombee["mois"], y=df_tombee["principal"],
                name="Principal", marker_color="#003366")
        fig.update_layout(barmode="stack", plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Source Sans 3", size=12),
            xaxis=dict(title="Mois", tickangle=-30, gridcolor="#EAE8E2"),
            yaxis=dict(title="M XAF", gridcolor="#EAE8E2"),
            legend=dict(orientation="h", y=1.1),
            height=380, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    # ── Par pays ──────────────────────────────────────────────────────────────
    if "pays_nom" in df_f.columns and "montant_du" in df_f.columns:
        st.markdown("### Répartition par pays")
        by_pays = df_f.groupby(["pays_nom","nature"])["montant_du"].sum().unstack(fill_value=0).reset_index()
        by_pays.columns.name = None
        fig2 = px.bar(by_pays.melt(id_vars="pays_nom", var_name="Nature", value_name="Montant (M XAF)"),
            x="pays_nom", y="Montant (M XAF)", color="Nature",
            color_discrete_sequence=["#C8A84B","#003366"],
            barmode="stack",
            labels={"pays_nom":"Pays"})
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
            height=320, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tableau détaillé ──────────────────────────────────────────────────────
    st.markdown("### Détail des remboursements")
    cols_show = [c for c in ["date_remboursement","pays_nom","instrument","maturite",
                               "code_long","nature","montant_du","montant_paye",
                               "date_paiement_effectif"] if c in df_f.columns]
    rename = {"date_remboursement":"Date remb.","pays_nom":"Pays","instrument":"Instrument",
               "maturite":"Maturité","code_long":"Code ISIN","nature":"Nature",
               "montant_du":"Dû (M XAF)","montant_paye":"Payé (M XAF)",
               "date_paiement_effectif":"Date paiement"}
    st.dataframe(df_f[cols_show].rename(columns=rename),
                 use_container_width=True, hide_index=True)
    csv = df_f.to_csv(index=False).encode("utf-8")
    st.download_button(":material/download: Exporter CSV", csv, "echeances.csv")
