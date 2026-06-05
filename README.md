# CTDAM-CEMAC — v2.0
## Plateforme digitale du marché des valeurs du Trésor CEMAC
**BEAC / CRCT — v2.0 — 2026**

---

## Nouveauté v2.0 — Données Excel centralisées

**Toutes les données dynamiques** de la plateforme proviennent d'un seul fichier :

```
CTDAM_CEMAC_Base_Donnees.xlsx
```

Plus aucune donnée simulée hardcodée. Chaque feuille Excel alimente directement un ou plusieurs onglets.

---

## Structure du projet

```
ctdam_cemac/
├── app.py                          # Point d'entrée principal
├── Authentification.py             # Module d'authentification
├── requirements.txt
├── CTDAM_CEMAC_Base_Donnees.xlsx   # ← BASE DE DONNÉES CENTRALE
├── users.json                      # Créé automatiquement au 1er lancement
├── assets/
│   └── style.css                   # Thème BEAC
├── data/
│   ├── __init__.py
│   └── loader.py                   # ← Toutes les fonctions de lecture Excel
├── Onglet/
│   ├── accueil.py
│   ├── statistiques_publiques.py
│   ├── reglementation.py           # + guide + publications + FAQ
│   ├── guide_investisseur.py
│   ├── publications.py
│   ├── faq.py
│   ├── inscription.py
│   ├── connexion.py
│   ├── bottin.py
│   ├── donnees_historiques.py
│   ├── calendrier.py
│   ├── macroeconomie.py            # ← NOUVEAU
│   ├── echeances.py                # ← NOUVEAU (tombée des échéances)
│   ├── simulation.py
│   ├── documents.py
│   ├── alertes.py
│   └── admin.py
└── Documentation/
    ├── reglementation/             # Fichiers PDF règlements
    └── publication/                # Fichiers PDF publications
```

---

## Feuilles Excel et ce qu'elles alimentent

| Feuille Excel            | Onglet(s) alimenté(s)                        |
|--------------------------|----------------------------------------------|
| `EMISSIONS`              | Accueil (chiffres clés), Données historiques |
| `REMBOURSEMENTS`         | Tombée des échéances                         |
| `SVT`                    | Bottin, Accueil (nb SVT actifs)              |
| `SGP`                    | Bottin                                       |
| `SDB`                    | Bottin                                       |
| `INVESTISSEURS_INST`     | Bottin                                       |
| `PAYS_MACRO`             | Macroéconomie                                |
| `ENCOURS_MENSUEL`        | Accueil (graphique pays), Statistiques       |
| `CALENDRIER_EMISSIONS`   | Calendrier des émissions                     |
| `COURBE_TAUX`            | Statistiques, Données historiques, Simulation|
| `CALCULS_MARCHE`         | Outils de simulation (tab Données marché)    |
| `DETENTEURS`             | Statistiques (répartition)                   |
| `DOCUMENTS_META`         | Espace documentaire, Réglementation, Publications |
| `UTILISATEURS`           | Admin (référence pour import)                |
| `ALERTES_ABONNEMENTS`    | Alertes (référence)                          |
| `KPIs_ACCUEIL`           | Accueil (formules auto)                      |
| `PARAMETRES`             | Configuration globale                        |
| `README`                 | Documentation interne                        |

---

## Mise à jour des données

### Méthode 1 — Directement dans l'Excel
1. Ouvrez `CTDAM_CEMAC_Base_Donnees.xlsx`
2. Mettez à jour la/les feuille(s) souhaitée(s)
3. Sauvegardez et rechargez la plateforme (F5)

### Méthode 2 — Via l'interface Admin
1. Connectez-vous avec un compte **Administrateur**
2. Menu **Import données marché** dans la sidebar
3. Téléversez le fichier Excel mis à jour **ou** importez une feuille partielle (CSV/Excel)

### Méthode 3 — Import partiel par feuille
Dans l'interface Admin → Import → sélectionnez la feuille cible → téléversez un CSV/Excel.

---

## Documents (Réglementation & Publications)

Placez vos fichiers PDF dans :
```
Documentation/reglementation/   ← Règlements, Instructions, Circulaires
Documentation/publication/      ← Bulletins, Rapports annuels, Notes
```

Puis renseignez le **chemin relatif** dans la colonne `Chemin Fichier` de la feuille `DOCUMENTS_META`.

Exemple :
```
Documentation/reglementation/reglement_01_2024.pdf
```

---

## Indicateurs disponibles par profil

| Indicateur                               | Public | Investisseur | Opérateur |
|------------------------------------------|:------:|:------------:|:---------:|
| Encours par État (OTA, BTA, évolutif)    | ✅     | ✅           | ✅        |
| Répartition volumes / émissions          | ✅     | ✅           | ✅        |
| N dernières émissions                    | ✅     | ✅           | ✅        |
| Calendrier des futures émissions         | ✅     | ✅           | ✅        |
| Courbe des taux / Rendement à l'échéance | ✅     | ✅           | ✅        |
| Inflation                                | ✅     | ✅           | ✅        |
| Ratio Dette/PIB                          | ✅     | ✅           | ✅        |
| Service de la dette / Recettes fiscales  | ✅     | ✅           | ✅        |
| Coût d'émission (TRMP)                   | ✅     | ✅           | ✅        |
| Répertoire SVT                           | ❌     | ✅           | ✅        |
| Tombée des échéances (coupon + principal)| ❌     | ✅           | ✅        |
| Poids titres publics / dette globale     | ❌     | ✅           | ✅        |
| Poids titres publics / PIB               | ❌     | ✅           | ✅        |
| Indice de concentration                  | ❌     | ✅           | ✅        |
| Duration / Convexité / Spread            | ❌     | ✅           | ✅        |
| Prix actuel d'un titre                   | ❌     | ✅           | ✅        |
| Répartition volumes par SVT              | ❌     | ❌           | ✅        |

---

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

**Premier lancement :** `users.json` est vide. Inscrivez un compte via le formulaire,
puis modifiez manuellement le fichier pour passer son statut à `"Administrateur"`.

---

## Support
BEAC / CRCT — crct@beac.int
