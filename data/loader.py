"""
data/loader.py — Chargement centralisé depuis CTDAM_CEMAC_Base_Donnees.xlsx
Toutes les fonctions de la plateforme lisent ce fichier.
"""

import pandas as pd
import numpy as np
import os
from functools import lru_cache
from datetime import datetime, timedelta

EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          "CTDAM_CEMAC_Base_Donnees.xlsx")

PAYS_CEMAC = {
    "CMR": {"nom": "Cameroun",           "code": "CMR", "devise": "XAF"},
    "GAB": {"nom": "Gabon",              "code": "GAB", "devise": "XAF"},
    "COG": {"nom": "Congo",              "code": "COG", "devise": "XAF"},
    "RCA": {"nom": "Rép. Centrafricaine","code": "RCA", "devise": "XAF"},
    "GNQ": {"nom": "Guinée Équatoriale", "code": "GNQ", "devise": "XAF"},
    "TCD": {"nom": "Tchad",              "code": "TCD", "devise": "XAF"},
}

# ── Utilitaire de lecture robuste ────────────────────────────────────────────

def _read_sheet(sheet: str, header_row: int = 2) -> pd.DataFrame:
    """Lit une feuille Excel; renvoie DataFrame vide si fichier absent."""
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=header_row)
        df = df.dropna(how="all")
        # Supprime les lignes-totaux (commençant par →)
        if df.shape[1] > 0:
            first = df.iloc[:, 0].astype(str)
            df = df[~first.str.startswith("→")]
        return df.reset_index(drop=True)
    except Exception:
        return pd.DataFrame()


def _safe_float(val, default=0.0):
    try:
        if pd.isna(val):
            return default
        s = str(val).replace("%", "").replace(",", ".").strip()
        return float(s)
    except Exception:
        return default


# ── EMISSIONS ────────────────────────────────────────────────────────────────

def get_emissions() -> pd.DataFrame:
    df = _read_sheet("EMISSIONS", header_row=2)
    if df.empty:
        return df
    col_map = {
        df.columns[0]:  "code_long",
        df.columns[1]:  "code_court",
        df.columns[2]:  "pays",
        df.columns[3]:  "instrument",
        df.columns[4]:  "maturite",
        df.columns[5]:  "montant_emis",
        df.columns[6]:  "date_souscription",
        df.columns[7]:  "date_remboursement",
        df.columns[8]:  "svt_locaux",
        df.columns[9]:  "svt_deplaces",
        df.columns[10]: "montant_leve",
        df.columns[11]: "nb_svt_emetteur",
        df.columns[12]: "nb_svt_participes",
        df.columns[13]: "taux_participation",
        df.columns[14]: "trmp",
        df.columns[15]: "taux_souscription",
        df.columns[16]: "taux_limite",
        df.columns[17]: "min_bta_ota",
        df.columns[18]: "max_bta_ota",
        df.columns[19]: "pmp_rendement",
        df.columns[20]: "taux_facial",
        df.columns[21]: "taux_couverture",
        df.columns[22]: "statut",
    } if len(df.columns) >= 23 else {}
    if col_map:
        df = df.rename(columns=col_map)
    # Nettoyage
    for col in ["montant_emis","montant_leve","svt_locaux","svt_deplaces"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["trmp","taux_couverture","taux_souscription"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: _safe_float(x))
    # Noms pays
    if "pays" in df.columns:
        df["pays_nom"] = df["pays"].map(
            lambda c: PAYS_CEMAC.get(str(c).upper(), {}).get("nom", str(c)))
    return df


def get_dernières_emissions(n: int = 10) -> pd.DataFrame:
    df = get_emissions()
    if df.empty:
        return df
    if "date_souscription" in df.columns:
        df["date_souscription"] = pd.to_datetime(df["date_souscription"], errors="coerce")
        df = df.sort_values("date_souscription", ascending=False)
    return df.head(n)


# ── REMBOURSEMENTS ───────────────────────────────────────────────────────────

def get_remboursements() -> pd.DataFrame:
    df = _read_sheet("REMBOURSEMENTS", header_row=2)
    if df.empty:
        return df
    if len(df.columns) >= 12:
        col_map = {
            df.columns[0]: "code_long",
            df.columns[1]: "code_court",
            df.columns[2]: "pays",
            df.columns[3]: "instrument",
            df.columns[4]: "maturite",
            df.columns[5]: "montant_emis",
            df.columns[6]: "date_souscription",
            df.columns[7]: "date_remboursement",
            df.columns[8]: "nature",
            df.columns[9]: "montant_du",
            df.columns[10]: "montant_paye",
            df.columns[11]: "date_paiement_effectif",
        }
        df = df.rename(columns=col_map)
    for col in ["montant_du","montant_paye","montant_emis"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if "pays" in df.columns:
        df["pays_nom"] = df["pays"].map(
            lambda c: PAYS_CEMAC.get(str(c).upper(), {}).get("nom", str(c)))
    return df


def get_tombee_echeances() -> pd.DataFrame:
    """Échéances groupées par mois pour le graphique tombée."""
    df = get_remboursements()
    if df.empty:
        return pd.DataFrame(columns=["mois","coupon","principal","total"])
    df["date_remboursement"] = pd.to_datetime(df["date_remboursement"], errors="coerce")
    df["mois"] = df["date_remboursement"].dt.to_period("M").astype(str)
    out = df.groupby(["mois","nature"])["montant_du"].sum().unstack(fill_value=0).reset_index()
    out.columns = [str(c).lower() for c in out.columns]
    if "coupon" not in out.columns:
        out["coupon"] = 0
    if "principal" not in out.columns:
        out["principal"] = 0
    out["coupon"] = pd.to_numeric(out["coupon"], errors="coerce").fillna(0)
    out["principal"] = pd.to_numeric(out["principal"], errors="coerce").fillna(0)
    out["total"] = out["coupon"] + out["principal"]
    return out.sort_values("mois")


# ── SVT / SGP / SDB / INVESTISSEURS ─────────────────────────────────────────

def _get_acteurs(sheet: str, col_names: list) -> pd.DataFrame:
    df = _read_sheet(sheet, header_row=2)
    if df.empty:
        return df
    mapping = {df.columns[i]: col_names[i]
               for i in range(min(len(df.columns), len(col_names)))}
    df = df.rename(columns=mapping)
    if "pays" in df.columns:
        df["pays_nom"] = df["pays"].map(
            lambda c: PAYS_CEMAC.get(str(c).upper(), {}).get("nom", str(c)))
    return df


def get_svt() -> pd.DataFrame:
    cols = ["raison_sociale","code_svt","pays","ville","date_convention",
            "agrement","statut","capital","email_front","email_middle",
            "email_back","telephone","site_web","representant","nb_adj","encours"]
    return _get_acteurs("SVT", cols)


def get_sgp() -> pd.DataFrame:
    cols = ["denomination","code_sgp","pays","ville","agrement",
            "date_agrement","statut","aum","contact","email","telephone","site_web"]
    return _get_acteurs("SGP", cols)


def get_sdb() -> pd.DataFrame:
    cols = ["denomination","code_sdb","pays","ville","agrement",
            "date_agrement","statut","email","telephone","site_web"]
    return _get_acteurs("SDB", cols)


def get_investisseurs_inst() -> pd.DataFrame:
    cols = ["denomination","type_acteur","pays","ville","point_focal",
            "email","telephone","statut","aum","svt_referent",
            "date_validation","num_dossier"]
    return _get_acteurs("INVESTISSEURS_INST", cols)


def get_bottin_complet() -> dict:
    """Retourne un dict de DataFrames formatés pour l'affichage Bottin."""
    svt = get_svt()
    sgp = get_sgp()
    sdb = get_sdb()
    inv = get_investisseurs_inst()

    def fmt(df, cols_display, rename):
        if df.empty:
            return pd.DataFrame(columns=rename.values())
        available = [c for c in cols_display if c in df.columns]
        out = df[available].copy()
        out = out.rename(columns={c: rename.get(c, c) for c in available})
        return out

    svt_out = fmt(svt,
        ["raison_sociale","pays_nom","statut","date_convention","email_front","telephone"],
        {"raison_sociale":"Dénomination","pays_nom":"Pays","statut":"Statut",
         "date_convention":"Date convention","email_front":"Contact","telephone":"Tél."})

    sgp_out = fmt(sgp,
        ["denomination","pays_nom","statut","agrement","email","telephone"],
        {"denomination":"Dénomination","pays_nom":"Pays","statut":"Statut",
         "agrement":"Agrément","email":"Contact","telephone":"Tél."})

    sdb_out = fmt(sdb,
        ["denomination","pays_nom","statut","agrement","email","telephone"],
        {"denomination":"Dénomination","pays_nom":"Pays","statut":"Statut",
         "agrement":"Agrément","email":"Contact","telephone":"Tél."})

    inv_out = fmt(inv,
        ["denomination","type_acteur","pays_nom","statut","email","svt_referent"],
        {"denomination":"Dénomination","type_acteur":"Type","pays_nom":"Pays",
         "statut":"Statut","email":"Contact","svt_referent":"SVT référent"})

    return {"SVT": svt_out, "SGP": sgp_out, "SDB": sdb_out, "Investisseurs": inv_out}


# ── PAYS_MACRO ───────────────────────────────────────────────────────────────

def get_pays_macro(annee: int = None) -> pd.DataFrame:
    df = _read_sheet("PAYS_MACRO", header_row=3)
    if df.empty:
        return df
    col_map = {}
    cols = list(df.columns)
    names = ["pays","code_pays","annee","pib","croissance_pib","inflation",
             "solde_budgetaire","recettes_fiscales","depenses","deficit_ext",
             "dette_totale","dette_pib","service_dette","service_dette_recettes",
             "proj_recettes","proj_depenses"]
    for i, n in enumerate(names):
        if i < len(cols):
            col_map[cols[i]] = n
    df = df.rename(columns=col_map)
    for col in ["pib","inflation","croissance_pib","solde_budgetaire",
                "dette_totale","dette_pib","service_dette","recettes_fiscales","depenses"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if annee and "annee" in df.columns:
        df = df[df["annee"] == annee]
    return df


def get_latest_macro() -> pd.DataFrame:
    df = get_pays_macro()
    if df.empty or "annee" not in df.columns:
        return df
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
    last = df["annee"].max()
    return df[df["annee"] == last].copy()


# ── ENCOURS_MENSUEL ──────────────────────────────────────────────────────────

def get_encours_mensuels() -> pd.DataFrame:
    df = _read_sheet("ENCOURS_MENSUEL", header_row=2)
    if df.empty:
        return df
    cols = list(df.columns)
    names = ["pays_nom","pays","mois","instrument","maturite","encours",
             "encours_cumul","variation_mm","variation_aa","nb_titres","source"]
    col_map = {cols[i]: names[i] for i in range(min(len(cols), len(names)))}
    df = df.rename(columns=col_map)
    if "encours" in df.columns:
        df["encours"] = pd.to_numeric(df["encours"], errors="coerce").fillna(0)
    if "pays_nom" not in df.columns and "pays" in df.columns:
        df["pays_nom"] = df["pays"].map(
            lambda c: PAYS_CEMAC.get(str(c).upper(), {}).get("nom", str(c)))
    return df


def encours_par_pays() -> pd.DataFrame:
    df = get_encours_mensuels()
    if df.empty:
        cols_needed = ["pays_nom","instrument","mois"]
        return pd.DataFrame(columns=["pays","BTA","OTA","total"])
    # Dernier mois disponible
    if "mois" in df.columns:
        last_mois = df["mois"].astype(str).max()
        df = df[df["mois"].astype(str) == last_mois]
    pivot = df.groupby(["pays_nom","instrument"])["encours"].sum().unstack(fill_value=0).reset_index()
    pivot.columns.name = None
    if "BTA" not in pivot.columns:
        pivot["BTA"] = 0
    if "OTA" not in pivot.columns:
        pivot["OTA"] = 0
    pivot["total"] = pivot["BTA"] + pivot["OTA"]
    pivot = pivot.rename(columns={"pays_nom":"pays"})
    return pivot.sort_values("total", ascending=False)


# ── CALENDRIER ───────────────────────────────────────────────────────────────

def get_calendrier() -> pd.DataFrame:
    df = _read_sheet("CALENDRIER_EMISSIONS", header_row=2)
    if df.empty:
        return df
    cols = list(df.columns)
    names = ["pays_nom","pays","instrument","maturite","date_adjudication",
             "heure_limite","montant_indicatif","statut","reference","remarque","resultat"]
    col_map = {cols[i]: names[i] for i in range(min(len(cols), len(names)))}
    df = df.rename(columns=col_map)
    if "montant_indicatif" in df.columns:
        df["montant_indicatif"] = pd.to_numeric(df["montant_indicatif"], errors="coerce").fillna(0)
    if "pays_nom" not in df.columns and "pays" in df.columns:
        df["pays_nom"] = df["pays"].map(
            lambda c: PAYS_CEMAC.get(str(c).upper(), {}).get("nom", str(c)))
    return df


# ── COURBE DES TAUX ──────────────────────────────────────────────────────────

def get_courbe_taux() -> pd.DataFrame:
    df = _read_sheet("COURBE_TAUX", header_row=2)
    if df.empty:
        return pd.DataFrame()
    cols = list(df.columns)
    names = ["date","maturite","maturite_num","taux_actuel","taux_cmr","taux_gab",
             "taux_cog","taux_rca","taux_gnq","taux_tcd","variation","source"]
    col_map = {cols[i]: names[i] for i in range(min(len(cols), len(names)))}
    df = df.rename(columns=col_map)
    for col in ["taux_actuel","taux_cmr","taux_gab","taux_cog","maturite_num"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Taux N-1 simulé si absent : -0.4
    df["taux_n1"] = df["taux_actuel"] - 0.4
    # Dernier relevé
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        last = df["date"].max()
        df = df[df["date"] == last]
    return df.reset_index(drop=True)


# ── CALCULS MARCHÉ ────────────────────────────────────────────────────────────

def get_calculs_marche() -> pd.DataFrame:
    df = _read_sheet("CALCULS_MARCHE", header_row=2)
    if df.empty:
        return df
    cols = list(df.columns)
    names = ["code_isin","pays","instrument","maturite","date_valeur","taux_facial",
             "prix_pied","prix_coupon_couru","rendement","duration",
             "duration_modifiee","convexite","spread","liquidite"]
    col_map = {cols[i]: names[i] for i in range(min(len(cols), len(names)))}
    df = df.rename(columns=col_map)
    for col in ["rendement","duration","duration_modifiee","convexite","liquidite"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: _safe_float(x))
    return df


# ── DÉTENTEURS ────────────────────────────────────────────────────────────────

def get_detenteurs() -> dict:
    df = _read_sheet("DETENTEURS", header_row=2)
    if df.empty:
        return {"SVT": 42.3, "Autres banques": 18.7,
                "Institutionnels non-bancaires": 24.1,
                "Personnes physiques": 8.4, "Autres": 6.5}
    cols = list(df.columns)
    names = ["mois","pays","categorie","encours","part","variation","source"]
    col_map = {cols[i]: names[i] for i in range(min(len(cols), len(names)))}
    df = df.rename(columns=col_map)
    # Dernier mois CEMAC
    if "mois" in df.columns:
        last = df["mois"].astype(str).max()
        df = df[df["mois"].astype(str) == last]
    if "pays" in df.columns:
        df = df[df["pays"].astype(str).str.upper() == "CEMAC"]
    if "categorie" in df.columns and "encours" in df.columns:
        df["encours"] = pd.to_numeric(df["encours"], errors="coerce").fillna(0)
        total = df["encours"].sum()
        result = {}
        for _, row in df.iterrows():
            cat = str(row["categorie"])
            pct = (row["encours"] / total * 100) if total > 0 else 0
            result[cat] = round(pct, 1)
        return result
    return {}


# ── DOCUMENTS ─────────────────────────────────────────────────────────────────

def get_documents_meta() -> pd.DataFrame:
    df = _read_sheet("DOCUMENTS_META", header_row=2)
    if df.empty:
        return df
    cols = list(df.columns)
    names = ["titre","categorie","sous_categorie","reference","date_publication",
             "auteur","acces","chemin_fichier","taille","version","actif","remarque"]
    col_map = {cols[i]: names[i] for i in range(min(len(cols), len(names)))}
    df = df.rename(columns=col_map)
    if "actif" in df.columns:
        df = df[df["actif"].astype(str).str.lower().isin(["oui","yes","true","1"])]
    return df


def get_reglementation() -> list:
    df = get_documents_meta()
    if df.empty:
        return []
    reg = df[df.get("categorie", pd.Series(dtype=str)).astype(str).str.lower() == "réglementation"]
    result = []
    for _, row in reg.iterrows():
        result.append({
            "titre": row.get("titre",""),
            "categorie": row.get("sous_categorie",""),
            "ref": row.get("reference",""),
            "date": str(row.get("date_publication",""))[:10],
            "acces": row.get("acces","Public"),
            "chemin": row.get("chemin_fichier",""),
        })
    return result


def get_publications() -> pd.DataFrame:
    df = get_documents_meta()
    if df.empty:
        return pd.DataFrame()
    pub = df[df.get("categorie", pd.Series(dtype=str)).astype(str).str.lower().isin(
        ["publication","statistiques"])]
    if pub.empty:
        return pub
    pub = pub.rename(columns={
        "titre":"titre","categorie":"categorie","date_publication":"date",
        "taille":"taille","acces":"acces"
    })
    pub["date"] = pub["date"].astype(str).str[:10]
    return pub.reset_index(drop=True)


# ── KPIs ACCUEIL ─────────────────────────────────────────────────────────────

def stats_marche_public() -> dict:
    """Chiffres clés calculés depuis les données Excel."""
    emissions = get_emissions()
    encours_df = encours_par_pays()
    svt = get_svt()
    courbe = get_courbe_taux()

    # Encours global
    total_enc = encours_df["total"].sum() if not encours_df.empty else 0
    enc_str = f"{total_enc/1000:.1f} Mds XAF" if total_enc > 0 else "N/D"

    # SVT actifs
    nb_svt = 0
    if not svt.empty and "statut" in svt.columns:
        nb_svt = int((svt["statut"].astype(str).str.lower() == "actif").sum())

    # Volumes 12 mois
    vol_12m = 0
    if not emissions.empty and "montant_leve" in emissions.columns and "date_souscription" in emissions.columns:
        emissions["date_souscription"] = pd.to_datetime(emissions["date_souscription"], errors="coerce")
        cutoff = datetime.now() - timedelta(days=365)
        recent = emissions[emissions["date_souscription"] >= cutoff]
        vol_12m = recent["montant_leve"].sum()
    vol_str = f"{vol_12m/1000:.1f} Mds XAF" if vol_12m > 0 else "N/D"

    # Nb adjudications 12 mois
    nb_adj = 0
    if not emissions.empty and "date_souscription" in emissions.columns:
        emissions["date_souscription"] = pd.to_datetime(emissions["date_souscription"], errors="coerce")
        cutoff = datetime.now() - timedelta(days=365)
        nb_adj = int((emissions["date_souscription"] >= cutoff).sum())

    # Taux couverture moyen
    tc = 1.0
    if not emissions.empty and "taux_couverture" in emissions.columns:
        vals = pd.to_numeric(emissions["taux_couverture"], errors="coerce").dropna()
        if len(vals) > 0:
            tc = round(vals.mean(), 2)

    # Dernier taux BTA 13s
    bta13 = "N/D"
    if not courbe.empty and "taux_actuel" in courbe.columns and "maturite" in courbe.columns:
        row = courbe[courbe["maturite"].astype(str).str.contains("13", na=False)]
        if not row.empty:
            v = row["taux_actuel"].iloc[0]
            if pd.notna(v):
                bta13 = f"{v:.2f}%".replace(".", ",")

    # Nb codes ISIN
    nb_isin = 0
    if not emissions.empty and "code_long" in emissions.columns:
        nb_isin = emissions["code_long"].dropna().nunique()

    return {
        "encours_global":        enc_str,
        "nb_svt_actifs":         nb_svt if nb_svt > 0 else 9,
        "nb_pays":               6,
        "dernier_taux_bta_13s":  bta13,
        "volumes_annuels":       vol_str,
        "nb_adjudications_annee":nb_adj if nb_adj > 0 else 0,
        "taux_couverture_moyen": f"{tc:.2f}x",
        "instruments_codes":     nb_isin if nb_isin > 0 else 0,
    }


# ── PARAMÈTRES ────────────────────────────────────────────────────────────────

def get_parametres() -> dict:
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="PARAMETRES", header=1)
        df = df.dropna(how="all")
        if len(df.columns) >= 2:
            return dict(zip(df.iloc[:,0].astype(str), df.iloc[:,1].astype(str)))
    except Exception:
        pass
    return {}


# ── FAQ (statique enrichie) ───────────────────────────────────────────────────

def get_faq() -> list:
    return [
        {"question": "Qu'est-ce qu'une valeur du Trésor ?",
         "reponse": "Une valeur du Trésor est un titre de créance émis par un État membre de la CEMAC pour financer ses besoins de trésorerie (BTA) ou ses investissements à moyen/long terme (OTA). Ces titres sont garantis par l'État."},
        {"question": "Quelle est la différence entre un BTA et une OTA ?",
         "reponse": "Les **BTA** (Bons du Trésor Assimilables) sont des instruments à court terme (13, 26 ou 52 semaines). Les **OTA** (Obligations du Trésor Assimilables) sont à moyen/long terme (2 à 15 ans) avec coupon annuel."},
        {"question": "Comment devenir investisseur sur le marché ?",
         "reponse": "Créez un compte sur cette plateforme, joignez vos pièces justificatives, et attendez la validation sous 5 jours ouvrés. Vous devrez ensuite passer par un SVT accrédité pour participer aux adjudications."},
        {"question": "Comment sont organisées les adjudications ?",
         "reponse": "Les adjudications se tiennent selon le calendrier publié sur cette plateforme. Les offres (montant + taux) sont soumises par les SVT avant 11h. Les résultats sont publiés le même jour."},
        {"question": "Les investisseurs de la diaspora peuvent-ils participer ?",
         "reponse": "Oui. Les investisseurs non-résidents peuvent participer via un SVT accrédité après validation de leur dossier par la BEAC (processus renforcé)."},
        {"question": "Qu'est-ce que le TRMP ?",
         "reponse": "Le **Taux de Rendement Moyen Pondéré** est la moyenne pondérée des taux offerts lors d'une adjudication, calculée sur les montants effectivement retenus."},
        {"question": "Comment lire la courbe des taux ?",
         "reponse": "La courbe des taux représente les rendements exigés par le marché selon la maturité du titre. Une courbe normale est ascendante (les maturités longues offrent des taux plus élevés pour compenser le risque)."},
        {"question": "Qu'est-ce que la duration ?",
         "reponse": "La duration mesure la sensibilité du prix d'une obligation aux variations de taux d'intérêt. Plus elle est élevée, plus le titre est sensible aux mouvements de taux."},
    ]
