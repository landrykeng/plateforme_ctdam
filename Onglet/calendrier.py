import streamlit as st
import pandas as pd
from data.loader import get_calendrier, PAYS_CEMAC

def show():
    if not st.session_state.get("authenticated", False):
        st.warning(":material/lock: Cette section est réservée aux utilisateurs enregistrés.")
        if st.button(":material/login: Se connecter"):
            st.session_state["page"] = "Connexion"; st.rerun()
        return

    st.title("Calendrier des émissions")
    st.caption("Adjudications prévisionnelles et confirmées — mis à jour par l'administrateur BEAC.")

    df_cal = get_calendrier()

    if df_cal.empty:
        st.info("Aucune émission programmée — alimentez la feuille **CALENDRIER_EMISSIONS** de l'Excel.")
        return

    pays_list = ["Tous"] + sorted(df_cal["pays_nom"].dropna().unique().tolist()) if "pays_nom" in df_cal.columns else ["Tous"]
    c1, c2, c3 = st.columns(3)
    with c1:
        pays_f = st.multiselect("Pays", options=pays_list[1:], default=pays_list[1:], key="cal_pays")
    with c2:
        inst_f = st.selectbox("Instrument", ["Tous","BTA","OTA"], key="cal_inst")
    with c3:
        statuts = ["Tous"] + sorted(df_cal["statut"].dropna().unique().tolist()) if "statut" in df_cal.columns else ["Tous"]
        statut_f = st.selectbox("Statut", statuts, key="cal_statut")

    df_f = df_cal.copy()
    if pays_f and "pays_nom" in df_f.columns:
        df_f = df_f[df_f["pays_nom"].isin(pays_f)]
    if inst_f != "Tous" and "instrument" in df_f.columns:
        df_f = df_f[df_f["instrument"] == inst_f]
    if statut_f != "Tous" and "statut" in df_f.columns:
        df_f = df_f[df_f["statut"] == statut_f]

    st.markdown(f"**{len(df_f)} adjudication(s) à venir**")

    for _, row in df_f.iterrows():
        statut = str(row.get("statut",""))
        badge_color = "#003366" if "confirm" in statut.lower() else "#C8A84B"
        inst = str(row.get("instrument",""))
        inst_color = "#004080" if inst == "OTA" else "#9E7B28"
        montant = row.get("montant_indicatif", 0)
        pays_nom = row.get("pays_nom", row.get("pays",""))
        date = str(row.get("date_adjudication",""))[:10]
        heure = str(row.get("heure_limite","11h00"))
        maturite = str(row.get("maturite",""))

        st.markdown(f"""
        <div class="app-card" style="margin-bottom:0.7rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
            <div style="display:flex; align-items:center; gap:1rem;">
                <div>
                    <div style="font-size:1.1rem; font-weight:700; color:#003366;">{date}</div>
                    <div style="font-size:0.8rem; color:#8C8C8C;">Heure limite : {heure}</div>
                </div>
                <div>
                    <div style="font-weight:600; color:#1A1A2E;">{pays_nom}</div>
                    <div style="font-size:0.85rem; color:#4A4A4A;">{maturite}</div>
                </div>
            </div>
            <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap;">
                <span style="background:{inst_color};color:white;padding:3px 10px;border-radius:3px;font-size:0.75rem;font-weight:700">{inst}</span>
                <span style="background:{badge_color};color:white;padding:3px 10px;border-radius:3px;font-size:0.75rem;font-weight:700">{statut}</span>
                <span style="font-size:0.88rem; color:#003366; font-weight:600;">{montant:,.0f} M XAF</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info(":material/info: Les montants sont indicatifs. Les résultats sont publiés le jour même de l'adjudication.")

    csv = df_f.to_csv(index=False).encode("utf-8")
    st.download_button(":material/download: Exporter le calendrier CSV", csv, "calendrier.csv")
