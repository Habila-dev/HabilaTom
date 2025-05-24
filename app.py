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

# Initialisation du gestionnaire de données
if 'data_manager' not in st.session_state:
    try:
        from utils.database_manager import DatabaseManager
        st.session_state.data_manager = DatabaseManager()
    except Exception as e:
        st.error(f"❌ Erreur de connexion à la base de données: {str(e)}")
        from utils.data_manager import DataManager
        st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager

# Initialisation du gestionnaire d'authentification
if 'auth_manager' not in st.session_state:
    try:
        from utils.auth_manager import AuthManager
        st.session_state.auth_manager = AuthManager(data_manager)
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation de l'authentification: {str(e)}")
        st.stop()

auth_manager = st.session_state.auth_manager

# Configuration de l'authentification
authenticator = auth_manager.get_authenticator()

# Interface de connexion
name, authentication_status, username = authenticator.login('Connexion à Habila Ghost', 'main')

if authentication_status == False:
    st.error('❌ Nom d\'utilisateur ou mot de passe incorrect')
elif authentication_status == None:
    st.warning('🔐 Veuillez vous connecter pour accéder à l\'application')
    st.info("**Compte administrateur par défaut:**\n- Utilisateur: `admin`\n- Mot de passe: `habila2025!`")
elif authentication_status:
    # Mise à jour de la dernière connexion
    auth_manager.update_last_login(username)
    
    # Interface de déconnexion dans la sidebar
    with st.sidebar:
        st.write(f'👋 Bienvenue *{name}*')
        authenticator.logout('Déconnexion', 'sidebar')
        
        # Afficher le rôle de l'utilisateur
        users = auth_manager.get_all_users()
        current_user = next((user for user in users if user['username'] == username), None)
        if current_user:
            role_emoji = {'admin': '👑', 'user': '👤', 'viewer': '👁️'}
            st.caption(f"{role_emoji.get(current_user['role'], '👤')} {current_user['role'].title()}")
    
    # Vérifier les permissions pour l'accès admin
    is_admin = auth_manager.has_permission(username, 'admin')
    
    # Afficher le menu de gestion des utilisateurs pour les admins
    if is_admin:
        with st.sidebar:
            st.markdown("---")
            if st.button("👥 Gestion des Utilisateurs"):
                st.session_state.show_user_management = True

    # Gestion des utilisateurs (pour les admins uniquement)
    if is_admin and st.session_state.get('show_user_management', False):
        st.title("👥 Gestion des Utilisateurs")
        
        tab1, tab2, tab3 = st.tabs(["📋 Liste des Utilisateurs", "➕ Ajouter Utilisateur", "🔧 Modifier Utilisateur"])
        
        with tab1:
            st.subheader("Liste des Utilisateurs")
            users = auth_manager.get_all_users()
            
            if users:
                users_df = pd.DataFrame(users)
                
                # Formatage des colonnes
                users_df['created_at'] = pd.to_datetime(users_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                users_df['last_login'] = pd.to_datetime(users_df['last_login'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
                users_df['active'] = users_df['active'].map({True: '✅ Actif', False: '❌ Inactif'})
                
                # Affichage du tableau
                st.dataframe(
                    users_df[['username', 'name', 'email', 'role', 'active', 'created_at', 'last_login']],
                    use_container_width=True,
                    column_config={
                        'username': 'Nom d\'utilisateur',
                        'name': 'Nom complet',
                        'email': 'Email',
                        'role': 'Rôle',
                        'active': 'Statut',
                        'created_at': 'Créé le',
                        'last_login': 'Dernière connexion'
                    }
                )
            else:
                st.warning("Aucun utilisateur trouvé.")
        
        with tab2:
            st.subheader("Ajouter un Nouvel Utilisateur")
            
            with st.form("add_user_form"):
                new_username = st.text_input("Nom d'utilisateur")
                new_name = st.text_input("Nom complet")
                new_email = st.text_input("Email")
                new_password = st.text_input("Mot de passe", type="password")
                new_role = st.selectbox("Rôle", ["viewer", "user", "admin"])
                
                if st.form_submit_button("Créer l'utilisateur"):
                    if new_username and new_name and new_password:
                        success = auth_manager.create_user(
                            username=new_username,
                            name=new_name,
                            email=new_email,
                            password=new_password,
                            role=new_role,
                            created_by=username
                        )
                        
                        if success:
                            st.success(f"✅ Utilisateur '{new_username}' créé avec succès!")
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de la création de l'utilisateur.")
                    else:
                        st.error("⚠️ Veuillez remplir tous les champs obligatoires.")
        
        with tab3:
            st.subheader("Modifier un Utilisateur")
            
            users = auth_manager.get_all_users()
            if users:
                usernames = [user['username'] for user in users]
                selected_username = st.selectbox("Sélectionner un utilisateur", usernames)
                
                if selected_username:
                    selected_user = next((user for user in users if user['username'] == selected_username), None)
                    
                    if selected_user:
                        with st.form("edit_user_form"):
                            edit_name = st.text_input("Nom complet", value=selected_user['name'])
                            edit_email = st.text_input("Email", value=selected_user['email'] or "")
                            edit_role = st.selectbox("Rôle", ["viewer", "user", "admin"], 
                                                   index=["viewer", "user", "admin"].index(selected_user['role']))
                            edit_active = st.checkbox("Actif", value=selected_user['active'])
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.form_submit_button("Mettre à jour"):
                                    success = auth_manager.update_user(
                                        username=selected_username,
                                        name=edit_name,
                                        email=edit_email,
                                        role=edit_role,
                                        active=edit_active
                                    )
                                    
                                    if success:
                                        st.success("✅ Utilisateur mis à jour!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Erreur lors de la mise à jour.")
                            
                            with col2:
                                with st.expander("🔒 Changer le mot de passe"):
                                    new_password = st.text_input("Nouveau mot de passe", type="password", key="new_pwd")
                                    if st.button("Changer le mot de passe"):
                                        if new_password:
                                            success = auth_manager.change_password(selected_username, new_password)
                                            if success:
                                                st.success("✅ Mot de passe changé!")
                                            else:
                                                st.error("❌ Erreur lors du changement.")
                                        else:
                                            st.error("⚠️ Veuillez saisir un mot de passe.")
        
        if st.button("← Retour au tableau de bord"):
            st.session_state.show_user_management = False
            st.rerun()
        
        st.stop()  # Arrêter l'exécution pour ne pas afficher le reste

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

    # Indicateur de statut de la base de données
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗄️ Base de Données")
    try:
        if hasattr(data_manager, 'get_database_stats'):
            db_stats = data_manager.get_database_stats()
            st.sidebar.success("✅ PostgreSQL connecté")
            st.sidebar.caption(f"Transactions: {db_stats.get('transactions_count', 0)}")
            st.sidebar.caption(f"Employés: {db_stats.get('active_employees_count', 0)}")
            st.sidebar.caption(f"Actionnaires: {db_stats.get('active_shareholders_count', 0)}")
        else:
            st.sidebar.warning("⚠️ Mode fichiers CSV")
    except Exception:
        st.sidebar.error("❌ Erreur de connexion")

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