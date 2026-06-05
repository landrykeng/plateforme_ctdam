import streamlit as st
import pandas as pd
import numpy as np
import json
import hashlib
import os
from datetime import datetime, timedelta
from PIL import Image


def hash_password(password):
    """Hash un mot de passe pour un stockage sécurisé"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Charge la base de données des utilisateurs depuis un fichier JSON"""
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {"users": {}}

def save_users(users):
    """Sauvegarde la base de données des utilisateurs dans un fichier JSON"""
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def import_users_from_excel(excel_path="Data/Connexion.xlsx"):
    """Importe les utilisateurs depuis un fichier Excel vers la base de données JSON"""
    try:
        df = pd.read_excel(excel_path, sheet_name="Identifiant")
        users = load_users()
        
        imported_count = 0
        for _, row in df.iterrows():
            username = row['User'].strip() if isinstance(row['User'], str) else str(row['User'])
            status = row['Statut'].strip() if isinstance(row['Statut'], str) else str(row['Statut'])
            password = row['Password'].strip() if isinstance(row['Password'], str) else str(row['Password'])
            
            if username not in users["users"]:
                users["users"][username] = {
                    "password": hash_password(password),
                    "status": status,
                    "email": f"{username}@example.com",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "active": True
                }
                imported_count += 1
        
        save_users(users)
        return True, f"{imported_count} utilisateurs importés avec succès"
    except Exception as e:
        return False, f"Erreur lors de l'importation: {str(e)}"

def check_credentials(username, password):
    """Vérifie si les identifiants sont corrects et renvoie également le statut"""
    users = load_users()
    if username in users["users"]:
        user = users["users"][username]
        if not user.get("active", True):
            return False, None
        if user["password"] == hash_password(password):
            return True, user.get("status", "Utilisateur")
    return False, None

def register_user(username, password, email, status="Utilisateur"):
    """Enregistre un nouvel utilisateur avec un statut"""
    users = load_users()
    if username in users["users"]:
        return False, "Ce nom d'utilisateur existe déjà"
    
    users["users"][username] = {
        "password": hash_password(password),
        "email": email,
        "status": status,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active": True
    }
    save_users(users)
    return True, "Compte créé avec succès"

def update_user(username, new_data):
    """Met à jour les données d'un utilisateur"""
    users = load_users()
    if username not in users["users"]:
        return False, "Utilisateur introuvable"
    
    users["users"][username].update(new_data)
    save_users(users)
    return True, "Utilisateur mis à jour avec succès"

def delete_user(username):
    """Supprime un utilisateur"""
    users = load_users()
    if username not in users["users"]:
        return False, "Utilisateur introuvable"
    
    del users["users"][username]
    save_users(users)
    return True, "Utilisateur supprimé avec succès"

def toggle_user_status(username):
    """Active ou désactive un utilisateur"""
    users = load_users()
    if username not in users["users"]:
        return False, "Utilisateur introuvable"
    
    current_status = users["users"][username].get("active", True)
    users["users"][username]["active"] = not current_status
    save_users(users)
    return True, f"Utilisateur {'désactivé' if current_status else 'activé'} avec succès"

def admin_panel():
    """Panneau d'administration pour gérer les utilisateurs"""
    st.markdown("### 👤 Gestion des Utilisateurs")
    
    users = load_users()
    
    # Onglets pour différentes actions d'administration
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["📋 Liste des utilisateurs", "➕ Ajouter un utilisateur", "📊 Statistiques"])
    
    with admin_tab1:
        if users["users"]:
            # Créer un DataFrame pour l'affichage
            user_data = []
            for username, info in users["users"].items():
                user_data.append({
                    "Nom d'utilisateur": username,
                    "Email": info.get("email", "N/A"),
                    "Statut": info.get("status", "Utilisateur"),
                    "Actif": "✅" if info.get("active", True) else "❌",
                    "Date de création": info.get("created_at", "N/A")
                })
            
            df_users = pd.DataFrame(user_data)
            st.dataframe(df_users, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("#### Actions sur les utilisateurs")
            
            col1, col2 = st.columns(2)
            
            with col1:
                user_to_modify = st.selectbox("Sélectionner un utilisateur", list(users["users"].keys()))
                
                if user_to_modify:
                    st.markdown(f"**Utilisateur sélectionné:** {user_to_modify}")
                    st.markdown(f"**Statut actuel:** {users['users'][user_to_modify].get('status', 'N/A')}")
                    st.markdown(f"**Actif:** {'Oui' if users['users'][user_to_modify].get('active', True) else 'Non'}")
            
            with col2:
                st.markdown("**Actions disponibles:**")
                
                # Modifier le statut
                new_status = st.selectbox("Modifier le statut", 
                                         ["Administrateur", "Utilisateur", "Superviseur", "Invité"])
                if st.button("💾 Mettre à jour le statut"):
                    success, msg = update_user(user_to_modify, {"status": new_status})
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                
                # Activer/Désactiver
                if st.button("🔄 Activer/Désactiver"):
                    success, msg = toggle_user_status(user_to_modify)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                
                # Supprimer
                if st.button("🗑️ Supprimer l'utilisateur", type="secondary"):
                    if user_to_modify != st.session_state["username"]:
                        success, msg = delete_user(user_to_modify)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("Vous ne pouvez pas supprimer votre propre compte!")
        else:
            st.info("Aucun utilisateur dans la base de données")
    
    with admin_tab2:
        st.markdown("#### Créer un nouvel utilisateur")
        
        with st.form("add_user_form"):
            new_username = st.text_input("Nom d'utilisateur")
            new_email = st.text_input("Email")
            new_password = st.text_input("Mot de passe", type="password")
            new_password_confirm = st.text_input("Confirmer le mot de passe", type="password")
            new_user_status = st.selectbox("Statut", ["Utilisateur", "Administrateur", "Superviseur", "Invité"])
            
            submit_button = st.form_submit_button("➕ Créer l'utilisateur")
            
            if submit_button:
                if not new_username or not new_password or not new_email:
                    st.error("Tous les champs sont obligatoires")
                elif new_password != new_password_confirm:
                    st.error("Les mots de passe ne correspondent pas")
                else:
                    success, msg = register_user(new_username, new_password, new_email, new_user_status)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        
        st.markdown("---")
        st.markdown("#### Importer depuis Excel")
        
        if st.button("📥 Importer les utilisateurs depuis Connexion.xlsx"):
            success, msg = import_users_from_excel()
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    with admin_tab3:
        st.markdown("#### Statistiques de la plateforme")
        
        total_users = len(users["users"])
        active_users = sum(1 for u in users["users"].values() if u.get("active", True))
        inactive_users = total_users - active_users
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total utilisateurs", total_users)
        with col2:
            st.metric("Utilisateurs actifs", active_users)
        with col3:
            st.metric("Utilisateurs inactifs", inactive_users)
        
        # Répartition par statut
        st.markdown("#### Répartition par statut")
        status_count = {}
        for user in users["users"].values():
            status = user.get("status", "Utilisateur")
            status_count[status] = status_count.get(status, 0) + 1
        
        if status_count:
            df_status = pd.DataFrame(list(status_count.items()), columns=["Statut", "Nombre"])
            st.bar_chart(df_status.set_index("Statut"))

def authentication_system(required_status=None, key="auth_system"):
    """
    Système d'authentification complet pour Streamlit
    
    Args:
        required_status (list, optional): Liste des statuts autorisés à accéder à l'application
                                         Si None, tous les utilisateurs peuvent accéder
    """
    # Initialisation des variables de session
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "status" not in st.session_state:
        st.session_state["status"] = None
    if "login_time" not in st.session_state:
        st.session_state["login_time"] = None
        
    # Si l'utilisateur est déjà authentifié
    if st.session_state["authenticated"]:
        # Vérifier si la session n'a pas expiré (8 heures)
        if st.session_state["login_time"] and datetime.now() - st.session_state["login_time"] > timedelta(hours=8):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.session_state["status"] = None
            st.session_state["login_time"] = None
            st.warning("⏰ Votre session a expiré. Veuillez vous reconnecter.")
        else:
            # Vérifier si l'utilisateur a le statut requis
            if required_status and st.session_state["status"] not in required_status:
                st.error(f"🚫 Accès refusé. Vous avez besoin d'un des statuts suivants : {', '.join(required_status)}")
                if st.sidebar.button("🚪 Déconnexion", key=f"logout_{key}"):
                    st.session_state["authenticated"] = False
                    st.session_state["username"] = None
                    st.session_state["status"] = None
                    st.session_state["login_time"] = None
                    st.rerun()
                return False
            
            # Afficher un message de bienvenue et un bouton de déconnexion
            st.sidebar.success(f"✅ Connecté : **{st.session_state['username']}**")
            if st.sidebar.button("🚪 Déconnexion", key=f"logout_{key}"):
                st.session_state["authenticated"] = False
                st.session_state["username"] = None
                st.session_state["status"] = None
                st.session_state["login_time"] = None
                st.rerun()
            return True
    
    # Style CSS personnalisé pour le thème INS
    st.markdown("""
        <style>
        .main {
            background-color: #f5f5f5;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #ffffff;
            border-radius: 5px 5px 0px 0px;
            padding: 10px 20px;
            font-weight: 600;
            color: #2c5f2d;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2c5f2d;
            color: white;
        }
        .login-header {
            background: linear-gradient(135deg, #2c5f2d 0%, #4a8c4f 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton > button {
            background-color: #2c5f2d;
            color: white;
            border-radius: 5px;
            padding: 10px 24px;
            font-weight: 600;
            border: none;
            width: 100%;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            background-color: #4a8c4f;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .stTextInput > div > div > input {
            border-radius: 5px;
            border: 2px solid #e0e0e0;
        }
        .stTextInput > div > div > input:focus {
            border-color: #2c5f2d;
        }
        </style>
    """, unsafe_allow_html=True)
    
    
        
    st.write(" ")
    col_panel = st.columns(2)
        
    with col_panel[0]:
            
        with st.form("login_form"):
            st.markdown("<h2 style='text-align: center; color: #2c5f2d;'>Connexion</h2>", unsafe_allow_html=True)
            username = st.text_input("👤 Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur", key=f"user_{key}")
            password = st.text_input("🔒 Mot de passe", type="password", placeholder="Entrez votre mot de passe", key=f"password_{key}")
                
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submit_button = st.form_submit_button("Se connecter", use_container_width=True)
                
            if submit_button:
                if not username or not password:
                    st.error("❌ Veuillez remplir tous les champs")
                else:
                    success, status = check_credentials(username, password)
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.session_state["status"] = status
                        st.session_state["login_time"] = datetime.now()
                            
                            # Vérifier si l'utilisateur a le statut requis
                        if required_status and status not in required_status:
                            st.error(f"🚫 Accès refusé. Statuts autorisés : {', '.join(required_status)}")
                            st.session_state["authenticated"] = False
                            st.session_state["username"] = None
                            st.session_state["status"] = None
                            st.session_state["login_time"] = None
                        else:
                            st.success("✅ Connexion réussie!")
                            st.rerun()
                    else:
                        st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
            
            st.markdown("---")
            st.info("💡 **Besoin d'aide ?** Contactez l'administrateur système pour obtenir vos identifiants.")
    
    with col_panel[1]:
        logo2 = Image.open("Picture/images_beac.jpg")
        st.image(logo2  , width=500)
    return False