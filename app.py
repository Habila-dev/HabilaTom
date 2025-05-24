import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from utils.data_manager import DataManager

# Configuration de la page
st.set_page_config(
    page_title="Habila Ghosts - Gestion Financière",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Système d'authentification multi-utilisateurs
import json
import os

def load_users():
    """Charger les utilisateurs depuis le fichier"""
    users_file = "config/users.json"
    if not os.path.exists("config"):
        os.makedirs("config")
    
    if not os.path.exists(users_file):
        # Créer le fichier avec l'admin par défaut
        from datetime import datetime
        default_users = {
            "admin": {
                "password": "habila2025",
                "role": "Administrateur",
                "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": None,
                "active": True
            }
        }
        try:
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)
        except:
            pass
        return default_users
    
    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"admin": {"password": "habila2025", "role": "Administrateur", "active": True}}

def update_last_login(username):
    """Mettre à jour la dernière connexion"""
    users_file = "config/users.json"
    try:
        users = load_users()
        from datetime import datetime
        users[username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except:
        pass

# Vérifier si l'utilisateur est connecté (sessions persistantes)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_role = None
    
# Maintenir la session tant que l'utilisateur ne se déconnecte pas manuellement
if 'session_initialized' not in st.session_state:
    st.session_state.session_initialized = True

if not st.session_state.authenticated:
    st.title("🔐 Connexion - Habila Ghost")
    st.markdown("---")
    
    # Charger les utilisateurs
    users = load_users()
    
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")
        submit = st.form_submit_button("Se connecter")
        
        if submit:
            if username in users and users[username].get('active', True):
                if users[username]['password'] == password:
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.user_role = users[username].get('role', 'Utilisateur')
                    update_last_login(username)
                    st.success("✅ Connexion réussie!")
                    st.rerun()
                else:
                    st.error("❌ Mot de passe incorrect")
            else:
                st.error("❌ Utilisateur inexistant ou compte désactivé")
    
    st.info("**Compte administrateur par défaut:**\n- Utilisateur: `admin`\n- Mot de passe: `habila2025`")
    st.stop()

# Interface de déconnexion
with st.sidebar:
    role_emoji = {"Administrateur": "👑", "Gestionnaire": "👤", "Consultant": "👁️", "Utilisateur": "👤"}
    current_emoji = role_emoji.get(st.session_state.user_role, "👤")
    st.success(f"✅ Connecté: {st.session_state.current_user}")
    st.caption(f"{current_emoji} {st.session_state.user_role}")
    
    if st.button("🚪 Déconnexion"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.rerun()

# Initialisation du gestionnaire de données (version déployable)
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager

# En-tête avec logo
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("attached_assets/habila_ghosts_logo_final.png", width=150)
    except:
        st.write("👻 **HABILA GHOSTS**")

with col2:
    st.title("💰 Système de Gestion Financière")
    st.caption("Capital: 150 000 $ divisé en 100 parts sociales")

st.markdown("---")

# Sidebar pour navigation
st.sidebar.title("📊 Navigation")
st.sidebar.markdown("Utilisez les pages ci-dessous pour naviguer dans l'application")

# Indicateur de statut des données
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Données")
try:
    transactions_df = data_manager.load_transactions()
    employees_df = data_manager.load_employees()
    shareholders_df = data_manager.load_shareholders()
    
    st.sidebar.success("✅ Données locales")
    st.sidebar.caption(f"Transactions: {len(transactions_df)}")
    st.sidebar.caption(f"Employés: {len(employees_df[employees_df['actif'] == True]) if not employees_df.empty else 0}")
    st.sidebar.caption(f"Actionnaires: {len(shareholders_df[shareholders_df['actif'] == True]) if not shareholders_df.empty else 0}")
except Exception:
    st.sidebar.error("❌ Erreur de chargement")

# Tableau de bord principal
st.header("📈 Tableau de Bord")

# Charger les données
transactions_df = data_manager.load_transactions()
employees_df = data_manager.load_employees()
shareholders_df = data_manager.load_shareholders()

# Calculer les métriques principales
if not transactions_df.empty:
    # Conversion des colonnes de date
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])
    
    # Calculs financiers
    total_entrees = transactions_df[transactions_df['type'] == 'Entrée']['montant'].sum()
    total_sorties = transactions_df[transactions_df['type'] == 'Sortie']['montant'].sum()
    solde_actuel = total_entrees - total_sorties
    
    # Métriques du mois en cours
    mois_actuel = datetime.now().replace(day=1)
    transactions_mois = transactions_df[transactions_df['date'] >= mois_actuel]
    entrees_mois = transactions_mois[transactions_mois['type'] == 'Entrée']['montant'].sum()
    sorties_mois = transactions_mois[transactions_mois['type'] == 'Sortie']['montant'].sum()
else:
    total_entrees = total_sorties = solde_actuel = 0
    entrees_mois = sorties_mois = 0

# Affichage des métriques principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💵 Solde Actuel",
        value=f"{solde_actuel:,.2f} $",
        delta=f"{entrees_mois - sorties_mois:,.2f} $ ce mois"
    )

with col2:
    st.metric(
        label="📈 Total Entrées",
        value=f"{total_entrees:,.2f} $",
        delta=f"{entrees_mois:,.2f} $ ce mois"
    )

with col3:
    st.metric(
        label="📉 Total Sorties",
        value=f"{total_sorties:,.2f} $",
        delta=f"{sorties_mois:,.2f} $ ce mois"
    )

with col4:
    nb_employees = len(employees_df[employees_df['actif'] == True]) if not employees_df.empty else 0
    st.metric(
        label="👥 Employés Actifs",
        value=nb_employees
    )

st.markdown("---")

# Graphiques
if not transactions_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Évolution du Solde")
        
        # Calculer le solde cumulé
        transactions_sorted = transactions_df.sort_values('date')
        transactions_sorted['solde_cumule'] = transactions_sorted.apply(
            lambda row: row['montant'] if row['type'] == 'Entrée' else -row['montant'], axis=1
        ).cumsum()
        
        fig_solde = px.line(
            transactions_sorted, 
            x='date', 
            y='solde_cumule',
            title="Évolution du Solde dans le Temps"
        )
        fig_solde.update_layout(
            xaxis_title="Date",
            yaxis_title="Solde ($)",
            yaxis_tickformat=",.0f"
        )
        st.plotly_chart(fig_solde, use_container_width=True)
    
    with col2:
        st.subheader("💰 Répartition Entrées vs Sorties")
        
        # Graphique camembert
        fig_pie = px.pie(
            values=[total_entrees, total_sorties],
            names=['Entrées', 'Sorties'],
            title="Répartition des Flux Financiers"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# Dernières transactions
st.subheader("📋 Dernières Transactions")
if not transactions_df.empty:
    dernières_transactions = transactions_df.head(10)
    dernières_transactions['date'] = dernières_transactions['date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        dernières_transactions[['date', 'type', 'montant', 'description', 'categorie']],
        use_container_width=True,
        column_config={
            'date': 'Date',
            'type': 'Type',
            'montant': st.column_config.NumberColumn('Montant', format="%.2f $"),
            'description': 'Description',
            'categorie': 'Catégorie'
        }
    )
else:
    st.info("Aucune transaction enregistrée. Rendez-vous sur la page 'Transactions' pour en ajouter.")

# Informations sur les actionnaires
if not shareholders_df.empty:
    st.subheader("🏛️ Répartition du Capital")
    
    # Calculer les pourcentages
    total_parts = shareholders_df[shareholders_df['actif'] == True]['parts_sociales'].sum()
    
    if total_parts > 0:
        active_shareholders = shareholders_df[shareholders_df['actif'] == True].copy()
        active_shareholders['pourcentage'] = (active_shareholders['parts_sociales'] / total_parts) * 100
        
        fig_capital = px.pie(
            active_shareholders,
            values='parts_sociales',
            names=active_shareholders['nom'] + ' ' + active_shareholders['prenom'],
            title=f"Répartition du Capital ({total_parts} parts sur 100)"
        )
        st.plotly_chart(fig_capital, use_container_width=True)
    else:
        st.info("Aucun actionnaire actif. Rendez-vous sur la page 'Actionnaires' pour en ajouter.")
else:
    st.info("Aucun actionnaire enregistré. Rendez-vous sur la page 'Actionnaires' pour en ajouter.")