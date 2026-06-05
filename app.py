"""
CTDAM-CEMAC — Plateforme du marché des valeurs du Trésor CEMAC
BEAC / CRCT — v2.0
Données alimentées depuis CTDAM_CEMAC_Base_Donnees.xlsx
"""

import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

# ── Configuration ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CTDAM-CEMAC | Marché des Valeurs du Trésor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS BEAC ──────────────────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────────────────────────
from Authentification import authentication_system, admin_panel

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-header">
    <span><b>BEAC · CRCT</b> &nbsp;|&nbsp; Comité de Trésorerie et Développement des Marchés de la CEMAC</span>
    <div class="header-right">
        <span style="font-size:0.8rem; opacity:0.8">Marché des Valeurs du Trésor CEMAC</span>
        <a class="lang-btn" href="#">FR</a>
        <a class="lang-btn" href="#">EN</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Initialisation session ────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

page = st.session_state.get("page", "Accueil")
is_auth = st.session_state.get("authenticated", False)
user_status = st.session_state.get("status", None)
is_admin = is_auth and user_status in ["Administrateur", "Admin BEAC"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 0.5rem 0;">
        <div style="font-family:'Libre Baskerville',serif; font-size:1.1rem; color:#C8A84B;
             font-weight:700; letter-spacing:1px;">CTDAM-CEMAC</div>
        <div style="font-size:0.72rem; color:rgba(255,255,255,0.6); letter-spacing:2px;
             text-transform:uppercase; margin-top:3px;">Bottin des Investisseurs</div>
    </div>
    <hr style="border:none; border-top:1px solid rgba(200,168,75,0.3); margin:0.5rem 0 1rem 0;">
    """, unsafe_allow_html=True)

    if not is_auth:
        if st.button(":material/login: Se connecter", use_container_width=True, type="primary"):
            st.session_state["page"] = "Connexion"
            st.rerun()
    else:
        st.markdown(
            f"<div style='font-size:0.78rem;color:rgba(255,255,255,0.7);text-align:center;"
            f"margin-bottom:0.3rem;'>Connecté : <b style='color:#C8A84B'>"
            f"{st.session_state.get('username','')}</b></div>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:0.72rem;color:rgba(200,168,75,0.6);text-align:center;"
            f"margin-bottom:0.5rem;'>{user_status}</div>",
            unsafe_allow_html=True)
        if st.button(":material/logout: Déconnexion", use_container_width=True):
            for k in ["authenticated","username","status","login_time"]:
                st.session_state[k] = None if k != "authenticated" else False
            st.session_state["page"] = "Accueil"
            st.rerun()

    if is_admin:
        st.markdown("<hr style='border:none;border-top:1px solid rgba(200,168,75,0.15);margin:0.8rem 0;'>",
                    unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.72rem;color:rgba(200,168,75,0.7);letter-spacing:1.5px;"
                    "text-transform:uppercase;margin-bottom:0.5rem;'>Administration</div>",
                    unsafe_allow_html=True)
        pages_admin = [
            (":material/manage_accounts:", "Gestion des utilisateurs"),
            (":material/upload_file:",     "Import données marché"),
            (":material/edit_document:",   "Gestion du Bottin"),
            (":material/event_available:", "Gestion émissions"),
            (":material/analytics:",       "Tableau de bord admin"),
            (":material/history:",         "Journal d'activité"),
        ]
        for icon, label in pages_admin:
            if st.button(f"{icon} {label}", key=f"adm_{label}", use_container_width=True):
                st.session_state["page"] = label
                st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(200,168,75,0.2);margin:1rem 0 0.5rem 0;'>",
                unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.68rem;color:rgba(255,255,255,0.3);text-align:center;"
                "margin-top:1rem;'>BEAC/CRCT · v2.0 · 2026</div>", unsafe_allow_html=True)

# ── Définition des pages ──────────────────────────────────────────────────────

# Pages publiques (espace public)
public_pages = [
    (":material/home:",        "Accueil"),
    (":material/bar_chart:",   "Statistiques publiques"),
    (":material/menu_book:",   "Réglementation"),
    (":material/school:",      "Guide de l'investisseur"),
    (":material/article:",     "Publications officielles"),
    (":material/help:",        "FAQ"),
    (":material/how_to_reg:",  "Inscription"),
]

# Pages restreintes investisseur validé
private_pages_investor = [
    (":material/contacts:",        "Bottin des investisseurs"),
    (":material/monitoring:",      "Données historiques"),
    (":material/calendar_month:",  "Calendrier des émissions"),
    (":material/public:",          "Macroéconomie"),
    (":material/account_balance:", "Tombée des échéances"),
    (":material/calculate:",       "Outils de simulation"),
    (":material/folder_open:",     "Espace documentaire"),
    (":material/notifications:",   "Alertes personnalisées"),
]

# Pages réservées opérateurs SVT/SGP/SDB (statuts Superviseur ou Admin)
OPERATOR_STATUTS = ["Superviseur", "Administrateur", "Admin BEAC"]

# ── Navigation par onglets ────────────────────────────────────────────────────
section_tabs = st.tabs(["Espace public", "Espace restreint"])

# ────────────────────────────────────────────────────────────────────────────
# ESPACE PUBLIC
# ────────────────────────────────────────────────────────────────────────────
with section_tabs[0]:
    public_subtabs = st.tabs([label for _, label in public_pages])

    for subtab, (_, label) in zip(public_subtabs, public_pages):
        with subtab:
            if label == "Accueil":
                from Onglet.accueil import show; show()
            elif label == "Statistiques publiques":
                from Onglet.statistiques_publiques import show; show()
            elif label == "Réglementation":
                from Onglet.reglementation import show_reglementation; show_reglementation()
            elif label == "Guide de l'investisseur":
                from Onglet.guide_investisseur import show; show()
            elif label == "Publications officielles":
                from Onglet.publications import show; show()
            elif label == "FAQ":
                from Onglet.faq import show; show()
            elif label == "Inscription":
                from Onglet.inscription import show; show()

# ────────────────────────────────────────────────────────────────────────────
# ESPACE RESTREINT
# ────────────────────────────────────────────────────────────────────────────
with section_tabs[1]:
    if not is_auth:
        st.info(":material/lock: **Espace restreint** — Le Bottin, les données historiques, "
                "les indicateurs macroéconomiques et les outils de simulation sont accessibles "
                "après création et validation de votre compte.")
        st.info("Connectez-vous pour accéder aux pages restreintes.")
        col_btn1, col_btn2, _ = st.columns([1,1,3])
        with col_btn1:
            if st.button(":material/login: Se connecter", use_container_width=True):
                st.session_state["page"] = "Connexion"; st.rerun()
        with col_btn2:
            pass
    else:
        # Détecter si opérateur pour affichage de répartition SVT
        is_operator = user_status in OPERATOR_STATUTS

        private_subtabs = st.tabs([label for _, label in private_pages_investor])

        for subtab, (_, label) in zip(private_subtabs, private_pages_investor):
            with subtab:
                if label == "Bottin des investisseurs":
                    from Onglet.bottin import show; show()

                elif label == "Données historiques":
                    from Onglet.donnees_historiques import show; show()

                elif label == "Calendrier des émissions":
                    from Onglet.calendrier import show; show()

                elif label == "Macroéconomie":
                    from Onglet.macroeconomie import show; show()

                elif label == "Tombée des échéances":
                    from Onglet.echeances import show; show()

                elif label == "Outils de simulation":
                    from Onglet.simulation import show; show()

                elif label == "Espace documentaire":
                    from Onglet.documents import show; show()

                elif label == "Alertes personnalisées":
                    from Onglet.alertes import show; show()


    if st.button(":material/how_to_reg: Créer un compte", use_container_width=True, type="primary"):
        st.session_state["page"] = "Inscription"; st.rerun()
# ── Routage hors-onglets (Connexion, Admin) ───────────────────────────────────
if page == "Connexion":
    from Onglet.connexion import show; show()
elif page in [label for _, label in [
    ("","Gestion des utilisateurs"),("","Import données marché"),
    ("","Gestion du Bottin"),("","Gestion émissions"),
    ("","Tableau de bord admin"),("","Journal d'activité"),("","Inscription")]]:
    from Onglet.admin import show; show(page)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <span>© 2026 BEAC — Banque des États de l'Afrique Centrale &nbsp;|&nbsp;
    CRCT — Comité de Trésorerie et Développement des Marchés de la CEMAC &nbsp;|&nbsp;
    <a href="#">Mentions légales</a> &nbsp;|&nbsp; <a href="#">Contact</a> &nbsp;|&nbsp;
    Données alimentées depuis CTDAM_CEMAC_Base_Donnees.xlsx</span>
</div>
""", unsafe_allow_html=True)
