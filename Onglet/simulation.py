import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from data.loader import get_calculs_marche, get_courbe_taux

def show():
    if not st.session_state.get("authenticated", False):
        st.warning(":material/lock: Cette section est réservée aux utilisateurs enregistrés.")
        if st.button(":material/login: Se connecter"):
            st.session_state["page"] = "Connexion"; st.rerun()
        return

    st.title("Outils de calcul et de simulation")
    st.caption("Calculateurs interactifs alimentés par les données de marché réelles.")

    df_marche = get_calculs_marche()
    df_courbe = get_courbe_taux()

    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/calculate: Calculateur de rendement",
        ":material/trending_up: Simulateur d'investissement",
        ":material/compare: Comparateur d'instruments",
        ":material/table_view: Données de marché",
    ])

    # ── Tab 1 : Rendement ─────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Calculateur de rendement obligataire")

        # Pré-remplissage depuis données réelles
        isin_list = ["-- Saisie manuelle --"]
        if not df_marche.empty and "code_isin" in df_marche.columns:
            isin_list += df_marche["code_isin"].dropna().tolist()

        col_sel, _ = st.columns([2,2])
        with col_sel:
            isin_sel = st.selectbox("Choisir un titre existant (optionnel)", isin_list)

        # Valeurs par défaut
        v_nominal, v_prix, v_taux, v_duree = 1_000_000, 98.5, 6.5, 5
        if isin_sel != "-- Saisie manuelle --" and not df_marche.empty:
            row = df_marche[df_marche["code_isin"] == isin_sel].iloc[0]
            v_taux  = float(str(row.get("taux_facial","6.5%")).replace("%","")) if row.get("taux_facial") else 6.5
            v_duree = int(float(str(row.get("maturite","5")).replace(" ans","").replace("a","").split()[0])) \
                if row.get("maturite") else 5

        col_i, col_r = st.columns([2, 2])
        with col_i:
            valeur_nominale = st.number_input("Valeur nominale (XAF)", value=v_nominal, step=100_000, format="%d")
            prix_achat = st.number_input("Prix d'achat (% du nominal)", value=v_prix, min_value=50.0, max_value=130.0, step=0.1)
            taux_facial = st.number_input("Taux facial (%)", value=v_taux, min_value=0.0, max_value=25.0, step=0.1)
            duree_annees = st.slider("Durée résiduelle (années)", 0, 15, v_duree)
            frequence = st.selectbox("Fréquence des coupons", ["Annuel","Semestriel"])

        with col_r:
            if duree_annees > 0:
                freq = 1 if frequence == "Annuel" else 2
                coupon = valeur_nominale * (taux_facial / 100) / freq
                prix = valeur_nominale * (prix_achat / 100)
                n = duree_annees * freq

                def prix_bond(r):
                    return sum(coupon / (1 + r/freq)**t for t in range(1, n+1)) + valeur_nominale / (1 + r/freq)**n

                r = taux_facial / 100
                for _ in range(100):
                    f_r = prix_bond(r) - prix
                    r_eps = r + 1e-6
                    deriv = (prix_bond(r_eps) - f_r) / 1e-6
                    if abs(deriv) < 1e-12: break
                    r -= f_r / deriv

                flux_act = [(t/freq) * (coupon / (1 + r/freq)**t) for t in range(1, n+1)]
                flux_act[-1] += duree_annees * (valeur_nominale / (1 + r/freq)**n)
                duration = sum(flux_act) / prix_bond(r)
                sensibilite = -duration / (1 + r/freq)

                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:1rem;">
                    <div class="metric-label">Rendement actuariel</div>
                    <div class="metric-value">{r*100:.4f} %</div>
                </div>""", unsafe_allow_html=True)

                ca, cb, cc = st.columns(3)
                for col, val, lbl in [
                    (ca, f"{duration:.2f} ans", "Duration Macaulay"),
                    (cb, f"{sensibilite:.3f}", "Sensibilité"),
                    (cc, f"{(prix_bond(r)-prix+coupon*duree_annees):,.0f} XAF", "Gain total net"),
                ]:
                    with col:
                        st.markdown(f"""<div class="metric-card">
                            <div class="metric-label">{lbl}</div>
                            <div class="metric-value" style="font-size:1.5rem;">{val}</div>
                        </div>""", unsafe_allow_html=True)

                # Spread vs courbe
                if not df_courbe.empty and "taux_actuel" in df_courbe.columns and "maturite_num" in df_courbe.columns:
                    courbe_interp = df_courbe.dropna(subset=["taux_actuel","maturite_num"])
                    taux_courbe = np.interp(duree_annees,
                        courbe_interp["maturite_num"].values,
                        courbe_interp["taux_actuel"].values)
                    spread_bp = int((r*100 - taux_courbe) * 100)
                    st.info(f":material/show_chart: Spread vs courbe CEMAC : **{spread_bp:+d} bp** (taux courbe : {taux_courbe:.2f}%)")

                # Flux
                dates_flux = [f"An {int(t/freq)}" if t%freq==0 else f"S{t}" for t in range(1, n+1)]
                flux_vals = [coupon]*n; flux_vals[-1] += valeur_nominale
                fig = go.Figure()
                fig.add_bar(x=dates_flux, y=flux_vals,
                    marker_color=["#C8A84B" if i < n-1 else "#003366" for i in range(n)])
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Source Sans 3", size=11),
                    yaxis=dict(title="XAF"), height=250,
                    margin=dict(l=0,r=0,t=10,b=0), title="Échéancier des flux")
                st.plotly_chart(fig, use_container_width=True)

    # ── Tab 2 : Simulateur ────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Simulateur d'investissement")
        c1, c2 = st.columns(2)
        with c1:
            montant_inv = st.number_input("Montant à investir (XAF)", value=10_000_000, step=1_000_000, format="%d")
            taux_sim = st.slider("Taux de rendement (%)", 3.0, 15.0, 6.5, 0.1)
        with c2:
            horizon = st.slider("Horizon (années)", 1, 15, 5)
            type_sim = st.selectbox("Type d'instrument", ["BTA","OTA coupon annuel","OTA coupon semestriel"])

        coupon_annuel = montant_inv * taux_sim / 100
        flux_list = []
        if type_sim == "BTA":
            flux_list = [("Échéance", coupon_annuel * (13/52) + montant_inv)]
        elif type_sim == "OTA coupon annuel":
            for i in range(1, horizon+1):
                flux_list.append((f"An {i}", coupon_annuel + (montant_inv if i==horizon else 0)))
        else:
            for i in range(1, horizon*2+1):
                flux_list.append((f"S{i}", coupon_annuel/2 + (montant_inv if i==horizon*2 else 0)))

        df_flux = pd.DataFrame(flux_list, columns=["Période","Flux (XAF)"])
        total = df_flux["Flux (XAF)"].sum()
        revenus = total - montant_inv

        ca, cb, cc = st.columns(3)
        for col, val, lbl in [
            (ca, f"{total/1_000_000:.2f} M XAF", "Total flux perçus"),
            (cb, f"{revenus/1_000_000:.2f} M XAF", "Revenus nets"),
            (cc, f"{(revenus/montant_inv*100):.2f} %", "Rendement total"),
        ]:
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">{lbl}</div>
                    <div class="metric-value">{val}</div>
                </div>""", unsafe_allow_html=True)

        fig2 = go.Figure()
        fig2.add_bar(x=df_flux["Période"], y=df_flux["Flux (XAF)"],
            marker_color=["#003366" if i < len(df_flux)-1 else "#C8A84B" for i in range(len(df_flux))])
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Source Sans 3", size=11),
            yaxis=dict(title="XAF"), height=280,
            margin=dict(l=0,r=0,t=10,b=0), title="Projection des flux de trésorerie")
        st.plotly_chart(fig2, use_container_width=True)

        csv = df_flux.to_csv(index=False).encode("utf-8")
        st.download_button(":material/download: Exporter la simulation", csv, "simulation.csv")

    # ── Tab 3 : Comparateur ───────────────────────────────────────────────────
    with tab3:
        st.markdown("### Comparateur d'instruments")
        nb = st.slider("Nombre d'instruments", 2, 4, 2)
        instruments = []
        cols = st.columns(nb)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"**Instrument {i+1}**")
                instruments.append({
                    "label": st.text_input("Libellé", value=f"Titre {i+1}", key=f"lbl_{i}"),
                    "nominal": st.number_input("Nominal (M XAF)", value=10, key=f"nom_{i}"),
                    "taux": st.number_input("Taux (%)", value=round(4.0+i*1.5,1), key=f"taux_{i}"),
                    "duree": st.number_input("Durée (ans)", value=i+1, min_value=1, max_value=15, key=f"dur_{i}"),
                    "risque": st.select_slider("Risque", ["Faible","Modéré","Élevé"], key=f"rsk_{i}"),
                })

        if st.button(":material/compare_arrows: Comparer", type="primary"):
            df_comp = pd.DataFrame([{
                "Instrument": x["label"], "Nominal (M)": x["nominal"],
                "Taux (%)": x["taux"], "Durée (ans)": x["duree"],
                "Revenu total (M)": round(x["nominal"]*x["taux"]/100*x["duree"],2),
                "Risque": x["risque"],
            } for x in instruments])
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

            fig3 = go.Figure()
            for x in instruments:
                revenu = x["nominal"]*x["taux"]/100*x["duree"]
                fig3.add_bar(x=["Rendement (%)", "Revenu total (M)", "Durée (ans)"],
                    y=[x["taux"], revenu, x["duree"]], name=x["label"])
            fig3.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                height=300, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig3, use_container_width=True)

    # ── Tab 4 : Données réelles ───────────────────────────────────────────────
    with tab4:
        st.markdown("### Données de marché — Duration, Convexité, Spread")
        if df_marche.empty:
            st.info("Aucune donnée — alimentez la feuille **CALCULS_MARCHE** de l'Excel.")
        else:
            cols_show = [c for c in ["code_isin","pays","instrument","maturite","date_valeur",
                                      "rendement","duration","duration_modifiee","convexite",
                                      "spread","liquidite"] if c in df_marche.columns]
            rename = {"code_isin":"Code ISIN","pays":"Pays","instrument":"Instrument",
                      "maturite":"Maturité","date_valeur":"Date valeur","rendement":"YTM (%)",
                      "duration":"Duration","duration_modifiee":"Dur. Mod.",
                      "convexite":"Convexité","spread":"Spread","liquidite":"Liquidité"}
            st.dataframe(df_marche[cols_show].rename(columns=rename),
                         use_container_width=True, hide_index=True)
