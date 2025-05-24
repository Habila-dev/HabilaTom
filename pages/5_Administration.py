import streamlit as st
import json
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Administration - Habila Ghosts",
    page_icon="🔐",
    layout="wide"
)

# Vérifier l'authentification
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Accès non autorisé. Veuillez vous connecter d'abord.")
    st.stop()

st.title("🔐 Administration des Accès")
st.markdown("---")

# Fichier de configuration des utilisateurs
USERS_FILE = "config/users.json"

def load_users():
    """Charger les utilisateurs depuis le fichier"""
    if not os.path.exists("config"):
        os.makedirs("config")
    
    if not os.path.exists(USERS_FILE):
        # Créer le fichier avec l'admin par défaut
        default_users = {
            "admin": {
                "password": "habila2025",
                "role": "Administrateur",
                "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": None,
                "active": True
            }
        }
        save_users(default_users)
        return default_users
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"admin": {"password": "habila2025", "role": "Administrateur", "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "last_login": None, "active": True}}

def save_users(users_data):
    """Sauvegarder les utilisateurs dans le fichier"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {e}")
        return False

# Charger les utilisateurs existants
users = load_users()

# Onglets pour l'administration
tab1, tab2, tab3 = st.tabs(["👥 Utilisateurs", "🔒 Modifier Mot de Passe Admin", "➕ Nouvel Utilisateur"])

with tab1:
    st.subheader("👥 Liste des Utilisateurs")
    
    if users:
        for username, user_data in users.items():
            with st.expander(f"🏷️ {username} ({user_data.get('role', 'Utilisateur')})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Rôle:** {user_data.get('role', 'Utilisateur')}")
                    st.write(f"**Créé le:** {user_data.get('created_date', 'Inconnu')}")
                    st.write(f"**Dernière connexion:** {user_data.get('last_login', 'Jamais')}")
                
                with col2:
                    status = "✅ Actif" if user_data.get('active', True) else "❌ Inactif"
                    st.write(f"**Statut:** {status}")
                
                with col3:
                    if username != "admin":  # Ne pas permettre de supprimer l'admin
                        if st.button(f"🗑️ Supprimer {username}", key=f"delete_{username}"):
                            users.pop(username)
                            if save_users(users):
                                st.success(f"✅ Utilisateur {username} supprimé!")
                                st.rerun()
                        
                        # Toggle statut actif/inactif
                        current_status = user_data.get('active', True)
                        new_status = st.checkbox(
                            "Compte actif", 
                            value=current_status, 
                            key=f"active_{username}"
                        )
                        if new_status != current_status:
                            users[username]['active'] = new_status
                            if save_users(users):
                                status_text = "activé" if new_status else "désactivé"
                                st.success(f"✅ Compte {username} {status_text}!")
                                st.rerun()
    else:
        st.info("Aucun utilisateur trouvé.")

with tab2:
    st.subheader("🔒 Modifier le Mot de Passe Administrateur")
    
    with st.form("change_admin_password"):
        current_password = st.text_input("Mot de passe actuel", type="password")
        new_password = st.text_input("Nouveau mot de passe", type="password")
        confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password")
        
        if st.form_submit_button("🔄 Changer le mot de passe"):
            if current_password != users.get("admin", {}).get("password", ""):
                st.error("❌ Mot de passe actuel incorrect!")
            elif len(new_password) < 6:
                st.error("❌ Le nouveau mot de passe doit contenir au moins 6 caractères!")
            elif new_password != confirm_password:
                st.error("❌ Les mots de passe ne correspondent pas!")
            else:
                users["admin"]["password"] = new_password
                users["admin"]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if save_users(users):
                    st.success("✅ Mot de passe administrateur mis à jour avec succès!")
                    st.info("⚠️ Vous devrez utiliser le nouveau mot de passe lors de votre prochaine connexion.")

with tab3:
    st.subheader("➕ Créer un Nouvel Utilisateur")
    
    with st.form("create_user"):
        new_username = st.text_input("Nom d'utilisateur", placeholder="ex: john_doe")
        new_user_password = st.text_input("Mot de passe", type="password", placeholder="Minimum 6 caractères")
        new_user_role = st.selectbox("Rôle", ["Utilisateur", "Gestionnaire", "Consultant"])
        
        if st.form_submit_button("👤 Créer l'utilisateur"):
            if not new_username or not new_user_password:
                st.error("❌ Veuillez remplir tous les champs!")
            elif new_username in users:
                st.error("❌ Ce nom d'utilisateur existe déjà!")
            elif len(new_user_password) < 6:
                st.error("❌ Le mot de passe doit contenir au moins 6 caractères!")
            elif not new_username.replace("_", "").isalnum():
                st.error("❌ Le nom d'utilisateur ne doit contenir que des lettres, chiffres et underscores!")
            else:
                users[new_username] = {
                    "password": new_user_password,
                    "role": new_user_role,
                    "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "created_by": "admin",
                    "last_login": None,
                    "active": True
                }
                
                if save_users(users):
                    st.success(f"✅ Utilisateur '{new_username}' créé avec succès!")
                    st.info(f"**Identifiants de connexion:**\n- Nom d'utilisateur: `{new_username}`\n- Mot de passe: `{new_user_password}`")
                    st.balloons()

# Section d'informations
st.markdown("---")
st.subheader("ℹ️ Informations Système")

col1, col2 = st.columns(2)

with col1:
    st.info("**📝 Instructions:**\n"
            "• Seul l'administrateur peut créer/supprimer des utilisateurs\n"
            "• Les mots de passe doivent contenir au moins 6 caractères\n"
            "• Les utilisateurs inactifs ne peuvent pas se connecter")

with col2:
    total_users = len(users)
    active_users = sum(1 for user in users.values() if user.get('active', True))
    
    st.metric("👥 Total Utilisateurs", total_users)
    st.metric("✅ Utilisateurs Actifs", active_users)

# Bouton d'export des données utilisateurs
if st.button("📥 Exporter la Liste des Utilisateurs"):
    # Créer un rapport sans les mots de passe
    user_report = {}
    for username, data in users.items():
        user_report[username] = {
            "role": data.get("role", "Utilisateur"),
            "created_date": data.get("created_date", "Inconnu"),
            "last_login": data.get("last_login", "Jamais"),
            "active": data.get("active", True)
        }
    
    report_json = json.dumps(user_report, indent=2, ensure_ascii=False)
    st.download_button(
        label="💾 Télécharger le rapport",
        data=report_json,
        file_name=f"users_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )