import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
import uuid
from typing import Optional, Tuple, List

# Import existing models and utilities
from utils.data_manager import DataManager
from models.transaction import Transaction
from models.employee import Employee
from models.shareholder import Shareholder

class HabilaGhostsApp:
    """Application Gradio pour la gestion financière de Habila Ghosts"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.current_user = None
        self.user_role = None
        self.authenticated = False
        
    def load_users(self):
        """Charger les utilisateurs depuis le fichier"""
        users_file = "config/users.json"
        if not os.path.exists("config"):
            os.makedirs("config")
        
        if not os.path.exists(users_file):
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

    def authenticate(self, username: str, password: str) -> Tuple[str, bool]:
        """Authentifier un utilisateur"""
        users = self.load_users()
        
        if username in users and users[username].get('active', True):
            if users[username]['password'] == password:
                self.authenticated = True
                self.current_user = username
                self.user_role = users[username].get('role', 'Utilisateur')
                
                # Mettre à jour la dernière connexion
                try:
                    users[username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open("config/users.json", 'w', encoding='utf-8') as f:
                        json.dump(users, f, indent=2, ensure_ascii=False)
                except:
                    pass
                
                return f"✅ Connexion réussie! Bienvenue {username}", True
            else:
                return "❌ Mot de passe incorrect", False
        else:
            return "❌ Utilisateur inexistant ou compte désactivé", False

    def logout(self):
        """Déconnecter l'utilisateur"""
        self.authenticated = False
        self.current_user = None
        self.user_role = None
        return "🚪 Déconnexion réussie"

    def get_dashboard_data(self):
        """Récupérer les données pour le tableau de bord"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour accéder au tableau de bord", None, None, None
        
        try:
            # Charger les données
            transactions_df = self.data_manager.load_transactions()
            employees_df = self.data_manager.load_employees()
            shareholders_df = self.data_manager.load_shareholders()
            
            # Calculer les métriques principales
            if not transactions_df.empty:
                transactions_df['date'] = pd.to_datetime(transactions_df['date'])
                
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
            
            nb_employees = len(employees_df[employees_df['actif'] == True]) if not employees_df.empty else 0
            
            # Créer le texte des métriques
            metrics_text = f"""
            ## 📊 Tableau de Bord - Habila Ghosts
            
            **💵 Solde Actuel:** {solde_actuel:,.2f} $ (Δ {entrees_mois - sorties_mois:,.2f} $ ce mois)
            
            **📈 Total Entrées:** {total_entrees:,.2f} $ (Δ {entrees_mois:,.2f} $ ce mois)
            
            **📉 Total Sorties:** {total_sorties:,.2f} $ (Δ {sorties_mois:,.2f} $ ce mois)
            
            **👥 Employés Actifs:** {nb_employees}
            
            **💾 Données:** {len(transactions_df)} transactions, {len(employees_df[employees_df['actif'] == True]) if not employees_df.empty else 0} employés, {len(shareholders_df[shareholders_df['actif'] == True]) if not shareholders_df.empty else 0} actionnaires
            """
            
            # Créer les graphiques
            charts = self.create_dashboard_charts(transactions_df, shareholders_df)
            
            # Dernières transactions
            recent_transactions = self.get_recent_transactions(transactions_df)
            
            return metrics_text, charts, recent_transactions, "✅ Données chargées avec succès"
            
        except Exception as e:
            return f"❌ Erreur lors du chargement des données: {str(e)}", None, None, None

    def create_dashboard_charts(self, transactions_df, shareholders_df):
        """Créer les graphiques du tableau de bord"""
        charts = {}
        
        if not transactions_df.empty:
            # Graphique d'évolution du solde
            transactions_sorted = transactions_df.sort_values('date')
            transactions_sorted['solde_cumule'] = transactions_sorted.apply(
                lambda row: row['montant'] if row['type'] == 'Entrée' else -row['montant'], axis=1
            ).cumsum()
            
            fig_solde = px.line(
                transactions_sorted, 
                x='date', 
                y='solde_cumule',
                title="📈 Évolution du Solde dans le Temps"
            )
            fig_solde.update_layout(
                xaxis_title="Date",
                yaxis_title="Solde ($)",
                yaxis_tickformat=",.0f"
            )
            charts['evolution_solde'] = fig_solde
            
            # Graphique camembert entrées vs sorties
            total_entrees = transactions_df[transactions_df['type'] == 'Entrée']['montant'].sum()
            total_sorties = transactions_df[transactions_df['type'] == 'Sortie']['montant'].sum()
            
            if total_entrees > 0 or total_sorties > 0:
                fig_pie = px.pie(
                    values=[total_entrees, total_sorties],
                    names=['Entrées', 'Sorties'],
                    title="💰 Répartition Entrées vs Sorties"
                )
                charts['repartition_flux'] = fig_pie
        
        # Graphique de répartition du capital
        if not shareholders_df.empty:
            active_shareholders = shareholders_df[shareholders_df['actif'] == True]
            if not active_shareholders.empty:
                total_parts = active_shareholders['parts_sociales'].sum()
                if total_parts > 0:
                    fig_capital = px.pie(
                        active_shareholders,
                        values='parts_sociales',
                        names=active_shareholders['nom'] + ' ' + active_shareholders['prenom'],
                        title=f"🏛️ Répartition du Capital ({total_parts} parts sur 100)"
                    )
                    charts['repartition_capital'] = fig_capital
        
        return charts

    def get_recent_transactions(self, transactions_df):
        """Obtenir les dernières transactions formatées"""
        if transactions_df.empty:
            return "Aucune transaction enregistrée."
        
        recent = transactions_df.head(10).copy()
        recent['date'] = pd.to_datetime(recent['date']).dt.strftime('%Y-%m-%d')
        
        # Formater pour l'affichage
        display_data = []
        for _, row in recent.iterrows():
            display_data.append([
                row['date'],
                row['type'],
                f"{row['montant']:,.2f} $",
                row['description'],
                row.get('categorie', '')
            ])
        
        return display_data

    def add_transaction(self, date_str: str, type_transaction: str, montant: float, 
                       description: str, categorie: str) -> str:
        """Ajouter une nouvelle transaction"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour ajouter une transaction"
        
        try:
            # Validation des données
            if not description.strip():
                return "❌ La description est obligatoire"
            
            if montant <= 0:
                return "❌ Le montant doit être positif"
            
            if type_transaction not in ['Entrée', 'Sortie']:
                return "❌ Type de transaction invalide"
            
            # Créer la transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                type=type_transaction,
                montant=montant,
                description=description.strip(),
                categorie=categorie.strip() if categorie else None
            )
            
            # Valider et sauvegarder
            if transaction.validate():
                self.data_manager.add_transaction(transaction)
                return f"✅ Transaction ajoutée avec succès: {montant:,.2f} $ ({type_transaction})"
            else:
                return "❌ Données de transaction invalides"
                
        except Exception as e:
            return f"❌ Erreur lors de l'ajout de la transaction: {str(e)}"

    def get_transactions_list(self):
        """Obtenir la liste de toutes les transactions"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour voir les transactions", []
        
        try:
            transactions_df = self.data_manager.load_transactions()
            if transactions_df.empty:
                return "Aucune transaction enregistrée.", []
            
            # Formater pour l'affichage
            transactions_df['date'] = pd.to_datetime(transactions_df['date']).dt.strftime('%Y-%m-%d')
            display_data = []
            
            for _, row in transactions_df.iterrows():
                display_data.append([
                    row['id'],
                    row['date'],
                    row['type'],
                    f"{row['montant']:,.2f} $",
                    row['description'],
                    row.get('categorie', '')
                ])
            
            return f"📋 {len(transactions_df)} transactions trouvées", display_data
            
        except Exception as e:
            return f"❌ Erreur lors du chargement des transactions: {str(e)}", []

    def add_employee(self, prenom: str, nom: str, poste: str, salaire: float, date_embauche_str: str) -> str:
        """Ajouter un nouvel employé"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour ajouter un employé"
        
        try:
            # Validation des données
            if not all([prenom.strip(), nom.strip(), poste.strip()]):
                return "❌ Tous les champs sont obligatoires"
            
            if salaire <= 0:
                return "❌ Le salaire doit être positif"
            
            # Créer l'employé
            employee = Employee(
                id=str(uuid.uuid4()),
                nom=nom.strip(),
                prenom=prenom.strip(),
                poste=poste.strip(),
                salaire_mensuel=salaire,
                date_embauche=datetime.strptime(date_embauche_str, '%Y-%m-%d').date(),
                actif=True
            )
            
            # Sauvegarder
            if self.data_manager.save_employee(employee):
                return f"✅ Employé {prenom} {nom} ajouté avec succès!"
            else:
                return "❌ Erreur lors de l'ajout de l'employé"
                
        except Exception as e:
            return f"❌ Erreur lors de l'ajout de l'employé: {str(e)}"

    def get_employees_list(self):
        """Obtenir la liste des employés"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour voir les employés", []
        
        try:
            employees_df = self.data_manager.load_employees()
            if employees_df.empty:
                return "Aucun employé enregistré.", []
            
            # Filtrer les employés actifs
            active_employees = employees_df[employees_df['actif'] == True]
            if active_employees.empty:
                return "Aucun employé actif.", []
            
            # Formater pour l'affichage
            display_data = []
            for _, row in active_employees.iterrows():
                date_embauche = pd.to_datetime(row['date_embauche']).strftime('%Y-%m-%d')
                display_data.append([
                    f"{row['prenom']} {row['nom']}",
                    row['poste'],
                    f"{row['salaire_mensuel']:,.2f} $",
                    date_embauche
                ])
            
            return f"👥 {len(active_employees)} employés actifs", display_data
            
        except Exception as e:
            return f"❌ Erreur lors du chargement des employés: {str(e)}", []

    def add_shareholder(self, prenom: str, nom: str, parts_sociales: int, email: str, telephone: str) -> str:
        """Ajouter un nouvel actionnaire"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour ajouter un actionnaire"
        
        try:
            # Validation des données
            if not all([prenom.strip(), nom.strip()]):
                return "❌ Le prénom et le nom sont obligatoires"
            
            if parts_sociales <= 0 or parts_sociales > 100:
                return "❌ Le nombre de parts doit être entre 1 et 100"
            
            # Vérifier que le total des parts ne dépasse pas 100
            shareholders_df = self.data_manager.load_shareholders()
            if not shareholders_df.empty:
                current_total = 0
                for _, row in shareholders_df[shareholders_df['actif'] == True].iterrows():
                    if 'parts_sociales' in row and pd.notna(row['parts_sociales']):
                        current_total += int(row['parts_sociales'])
                    elif 'pourcentage_actions' in row and pd.notna(row['pourcentage_actions']):
                        current_total += int(row['pourcentage_actions'])
                
                if current_total + parts_sociales > 100:
                    return f"❌ Le total des parts ne peut pas dépasser 100. Actuellement: {current_total} parts"
            
            # Créer l'actionnaire
            shareholder = Shareholder(
                id=str(uuid.uuid4()),
                nom=nom.strip(),
                prenom=prenom.strip(),
                parts_sociales=parts_sociales,
                email=email.strip() if email.strip() else None,
                telephone=telephone.strip() if telephone.strip() else None,
                actif=True
            )
            
            # Sauvegarder
            if self.data_manager.save_shareholder(shareholder):
                valeur = shareholder.valeur_parts
                return f"✅ Actionnaire {prenom} {nom} ajouté avec succès! Valeur: ${valeur:,.2f}"
            else:
                return "❌ Erreur lors de l'ajout de l'actionnaire"
                
        except Exception as e:
            return f"❌ Erreur lors de l'ajout de l'actionnaire: {str(e)}"

    def get_shareholders_list(self):
        """Obtenir la liste des actionnaires"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour voir les actionnaires", []
        
        try:
            shareholders_df = self.data_manager.load_shareholders()
            if shareholders_df.empty:
                return "Aucun actionnaire enregistré.", []
            
            # Filtrer les actionnaires actifs
            active_shareholders = shareholders_df[shareholders_df['actif'] == True]
            if active_shareholders.empty:
                return "Aucun actionnaire actif.", []
            
            # Calculer le total des parts
            total_parts = active_shareholders['parts_sociales'].sum()
            
            # Formater pour l'affichage
            display_data = []
            for _, row in active_shareholders.iterrows():
                parts = row['parts_sociales']
                pourcentage = (parts / total_parts * 100) if total_parts > 0 else 0
                valeur = parts * 1500  # 150,000 / 100 parts
                
                display_data.append([
                    f"{row['prenom']} {row['nom']}",
                    f"{parts} parts",
                    f"{pourcentage:.1f}%",
                    f"{valeur:,.2f} $",
                    row.get('email', ''),
                    row.get('telephone', '')
                ])
            
            return f"🏛️ {len(active_shareholders)} actionnaires actifs ({total_parts}/100 parts)", display_data
            
        except Exception as e:
            return f"❌ Erreur lors du chargement des actionnaires: {str(e)}", []

    def pay_salaries(self, mois_str: str) -> str:
        """Payer les salaires du mois"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour payer les salaires"
        
        try:
            employees_df = self.data_manager.load_employees()
            active_employees = employees_df[employees_df['actif'] == True]
            
            if active_employees.empty:
                return "❌ Aucun employé actif à payer"
            
            total_salaires = 0
            transactions_added = 0
            
            for _, employee in active_employees.iterrows():
                # Créer une transaction pour chaque salaire
                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    date=datetime.strptime(mois_str + "-01", '%Y-%m-%d').date(),
                    type='Sortie',
                    montant=employee['salaire_mensuel'],
                    description=f"Salaire {mois_str} - {employee['prenom']} {employee['nom']}",
                    categorie='Salaires'
                )
                
                if transaction.validate() and self.data_manager.add_transaction(transaction):
                    total_salaires += employee['salaire_mensuel']
                    transactions_added += 1
            
            if transactions_added > 0:
                return f"✅ Salaires payés: {transactions_added} employés, total: {total_salaires:,.2f} $"
            else:
                return "❌ Erreur lors du paiement des salaires"
                
        except Exception as e:
            return f"❌ Erreur lors du paiement des salaires: {str(e)}"

    def generate_reports(self):
        """Générer les rapports financiers"""
        if not self.authenticated:
            return "❌ Veuillez vous connecter pour voir les rapports", "", None, None, ""
        
        try:
            transactions_df = self.data_manager.load_transactions()
            employees_df = self.data_manager.load_employees()
            shareholders_df = self.data_manager.load_shareholders()
            
            if transactions_df.empty:
                return "Aucune donnée disponible pour les rapports", "", None, None, ""
            
            # Conversion des dates
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            
            # Calculs financiers
            total_entrees = transactions_df[transactions_df['type'] == 'Entrée']['montant'].sum()
            total_sorties = transactions_df[transactions_df['type'] == 'Sortie']['montant'].sum()
            solde_actuel = total_entrees - total_sorties
            
            # Résumé financier
            financial_summary = f"""
            **💰 Résumé Financier Global**
            
            - **Solde Actuel:** {solde_actuel:,.2f} $
            - **Total Entrées:** {total_entrees:,.2f} $
            - **Total Sorties:** {total_sorties:,.2f} $
            - **Ratio Entrées/Sorties:** {(total_entrees/total_sorties*100):.1f}% si sorties > 0
            
            **📊 Répartition du Capital**
            - **Capital Total:** 150,000 $
            - **Parts Distribuées:** {shareholders_df[shareholders_df['actif'] == True]['parts_sociales'].sum() if not shareholders_df.empty else 0}/100
            """
            
            # Statistiques
            nb_transactions = len(transactions_df)
            nb_employees = len(employees_df[employees_df['actif'] == True]) if not employees_df.empty else 0
            nb_shareholders = len(shareholders_df[shareholders_df['actif'] == True]) if not shareholders_df.empty else 0
            
            # Calcul de la masse salariale
            masse_salariale = employees_df[employees_df['actif'] == True]['salaire_mensuel'].sum() if not employees_df.empty else 0
            
            stats_summary = f"""
            **📈 Statistiques Générales**
            
            - **Transactions:** {nb_transactions}
            - **Employés Actifs:** {nb_employees}
            - **Actionnaires:** {nb_shareholders}
            - **Masse Salariale Mensuelle:** {masse_salariale:,.2f} $
            
            **📅 Période d'Analyse**
            - **Première Transaction:** {transactions_df['date'].min().strftime('%Y-%m-%d') if not transactions_df.empty else 'N/A'}
            - **Dernière Transaction:** {transactions_df['date'].max().strftime('%Y-%m-%d') if not transactions_df.empty else 'N/A'}
            """
            
            # Graphique évolution mensuelle
            transactions_df['mois'] = transactions_df['date'].dt.to_period('M')
            monthly_data = transactions_df.groupby(['mois', 'type'])['montant'].sum().reset_index()
            monthly_data['mois_str'] = monthly_data['mois'].astype(str)
            
            if not monthly_data.empty:
                fig_monthly = px.bar(
                    monthly_data,
                    x='mois_str',
                    y='montant',
                    color='type',
                    title="📈 Évolution Mensuelle des Flux Financiers",
                    labels={'mois_str': 'Mois', 'montant': 'Montant ($)', 'type': 'Type'}
                )
                fig_monthly.update_layout(xaxis_title="Mois", yaxis_title="Montant ($)")
            else:
                fig_monthly = None
            
            # Graphique par catégorie
            if 'categorie' in transactions_df.columns:
                category_data = transactions_df.groupby('categorie')['montant'].sum().reset_index()
                category_data = category_data[category_data['montant'] > 0]
                
                if not category_data.empty:
                    fig_category = px.pie(
                        category_data,
                        values='montant',
                        names='categorie',
                        title="💼 Répartition par Catégorie"
                    )
                else:
                    fig_category = None
            else:
                fig_category = None
            
            return (
                financial_summary,
                stats_summary,
                fig_monthly,
                fig_category,
                "✅ Rapports générés avec succès"
            )
            
        except Exception as e:
            return f"❌ Erreur lors de la génération des rapports: {str(e)}", "", None, None, ""

# Initialiser l'application
app = HabilaGhostsApp()

def create_interface():
    """Créer l'interface Gradio"""
    
    # CSS personnalisé pour l'optimisation mobile
    custom_css = """
    /* Optimisation mobile */
    @media (max-width: 768px) {
        .gradio-container {
            padding: 10px !important;
        }
        
        .block {
            margin: 5px 0 !important;
        }
        
        .form {
            gap: 10px !important;
        }
        
        /* Améliorer la lisibilité sur mobile */
        .markdown {
            font-size: 14px !important;
            line-height: 1.4 !important;
        }
        
        /* Optimiser les tableaux pour mobile */
        .dataframe {
            font-size: 12px !important;
        }
        
        /* Boutons plus grands sur mobile */
        .btn {
            min-height: 44px !important;
            font-size: 16px !important;
        }
    }
    
    /* Style général */
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    
    /* En-tête personnalisé */
    .header-custom {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Métriques du tableau de bord */
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    """
    
    with gr.Blocks(
        title="Habila Ghosts - Gestion Financière", 
        theme=gr.themes.Soft(),
        css=custom_css
    ) as interface:
        
        # État de l'authentification
        auth_state = gr.State(False)
        
        # En-tête
        gr.HTML("""
        <div style="text-align: center; padding: 20px;">
            <h1>👻 Habila Ghosts - Système de Gestion Financière</h1>
            <p><em>Capital: 150 000 $ divisé en 100 parts sociales</em></p>
        </div>
        """)
        
        # Section d'authentification
        with gr.Group(visible=True) as login_section:
            gr.Markdown("## 🔐 Connexion")
            with gr.Row():
                username_input = gr.Textbox(label="Nom d'utilisateur", placeholder="admin")
                password_input = gr.Textbox(label="Mot de passe", type="password", placeholder="habila2025")
            login_btn = gr.Button("Se connecter", variant="primary")
            login_status = gr.Markdown("")
            
            gr.Markdown("""
            **Compte administrateur par défaut:**
            - Utilisateur: `admin`
            - Mot de passe: `habila2025`
            """)
        
        # Section principale (cachée initialement)
        with gr.Group(visible=False) as main_section:
            # Barre de statut utilisateur
            with gr.Row():
                user_status = gr.Markdown("")
                logout_btn = gr.Button("🚪 Déconnexion", size="sm")
            
            # Onglets principaux
            with gr.Tabs():
                # Tableau de bord
                with gr.Tab("📊 Tableau de Bord"):
                    refresh_dashboard_btn = gr.Button("🔄 Actualiser", size="sm")
                    dashboard_status = gr.Markdown("")
                    dashboard_metrics = gr.Markdown("")
                    
                    with gr.Row():
                        with gr.Column():
                            evolution_chart = gr.Plot(label="Évolution du Solde")
                        with gr.Column():
                            repartition_chart = gr.Plot(label="Répartition des Flux")
                    
                    capital_chart = gr.Plot(label="Répartition du Capital")
                    
                    gr.Markdown("### 📋 Dernières Transactions")
                    recent_transactions_table = gr.Dataframe(
                        headers=["Date", "Type", "Montant", "Description", "Catégorie"],
                        label="Transactions récentes"
                    )
                
                # Transactions
                with gr.Tab("💳 Transactions"):
                    with gr.Tabs():
                        with gr.Tab("➕ Nouvelle Transaction"):
                            with gr.Row():
                                trans_date = gr.Textbox(
                                    label="Date (YYYY-MM-DD)", 
                                    value=date.today().strftime('%Y-%m-%d')
                                )
                                trans_type = gr.Dropdown(
                                    choices=["Entrée", "Sortie"],
                                    label="Type de transaction",
                                    value="Entrée"
                                )
                            
                            with gr.Row():
                                trans_amount = gr.Number(label="Montant ($)", minimum=0.01)
                                trans_category = gr.Textbox(label="Catégorie (optionnel)")
                            
                            trans_description = gr.Textbox(label="Description", lines=2)
                            add_trans_btn = gr.Button("Ajouter Transaction", variant="primary")
                            add_trans_status = gr.Markdown("")
                        
                        with gr.Tab("📋 Liste des Transactions"):
                            refresh_trans_btn = gr.Button("🔄 Actualiser", size="sm")
                            trans_list_status = gr.Markdown("")
                            transactions_table = gr.Dataframe(
                                headers=["ID", "Date", "Type", "Montant", "Description", "Catégorie"],
                                label="Toutes les transactions"
                            )
                
                # Gestion des Salaires
                with gr.Tab("👥 Salaires"):
                    with gr.Tabs():
                        with gr.Tab("👤 Employés"):
                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### ➕ Ajouter un employé")
                                    emp_prenom = gr.Textbox(label="Prénom", placeholder="Jean")
                                    emp_nom = gr.Textbox(label="Nom", placeholder="Dupont")
                                    emp_poste = gr.Textbox(label="Poste", placeholder="Développeur")
                                    emp_salaire = gr.Number(label="Salaire mensuel ($)", minimum=0.01)
                                    emp_date_embauche = gr.Textbox(
                                        label="Date d'embauche (YYYY-MM-DD)", 
                                        value=date.today().strftime('%Y-%m-%d')
                                    )
                                    add_emp_btn = gr.Button("💾 Ajouter l'employé", variant="primary")
                                    add_emp_status = gr.Markdown("")
                                
                                with gr.Column():
                                    gr.Markdown("### 📋 Liste des employés")
                                    refresh_emp_btn = gr.Button("🔄 Actualiser", size="sm")
                                    emp_list_status = gr.Markdown("")
                                    employees_table = gr.Dataframe(
                                        headers=["Nom Complet", "Poste", "Salaire Mensuel", "Date d'Embauche"],
                                        label="Employés actifs"
                                    )
                        
                        with gr.Tab("💰 Payer Salaires"):
                            gr.Markdown("### 💰 Paiement des Salaires")
                            salary_month = gr.Textbox(
                                label="Mois (YYYY-MM)", 
                                value=datetime.now().strftime('%Y-%m'),
                                placeholder="2024-01"
                            )
                            pay_salaries_btn = gr.Button("💰 Payer tous les salaires", variant="primary")
                            pay_salaries_status = gr.Markdown("")
                
                # Gestion des Actionnaires
                with gr.Tab("🏛️ Actionnaires"):
                    with gr.Tabs():
                        with gr.Tab("👥 Actionnaires"):
                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### ➕ Ajouter un actionnaire")
                                    share_prenom = gr.Textbox(label="Prénom", placeholder="Marie")
                                    share_nom = gr.Textbox(label="Nom", placeholder="Dubois")
                                    share_parts = gr.Number(
                                        label="Nombre de parts sociales (sur 100 total)", 
                                        minimum=1, maximum=100, step=1
                                    )
                                    share_email = gr.Textbox(label="Email (optionnel)", placeholder="marie.dubois@email.com")
                                    share_telephone = gr.Textbox(label="Téléphone (optionnel)", placeholder="+33 1 23 45 67 89")
                                    add_share_btn = gr.Button("💾 Ajouter l'actionnaire", variant="primary")
                                    add_share_status = gr.Markdown("")
                                
                                with gr.Column():
                                    gr.Markdown("### 📋 Liste des actionnaires")
                                    refresh_share_btn = gr.Button("🔄 Actualiser", size="sm")
                                    share_list_status = gr.Markdown("")
                                    shareholders_table = gr.Dataframe(
                                        headers=["Nom Complet", "Parts", "Pourcentage", "Valeur", "Email", "Téléphone"],
                                        label="Actionnaires actifs"
                                    )
                        
                        with gr.Tab("💰 Calcul des Bénéfices"):
                            gr.Markdown("### 💰 Distribution des Bénéfices")
                            gr.Markdown("*Fonctionnalité en cours de développement...*")
                
                with gr.Tab("📊 Rapports"):
                    gr.Markdown("### 📊 Rapports et Analyses")
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### 💰 Résumé Financier")
                            financial_summary = gr.Markdown("")
                            
                        with gr.Column():
                            gr.Markdown("#### 📈 Statistiques")
                            stats_summary = gr.Markdown("")
                    
                    gr.Markdown("#### 📊 Graphiques Détaillés")
                    with gr.Row():
                        monthly_chart = gr.Plot(label="Évolution Mensuelle")
                        category_chart = gr.Plot(label="Répartition par Catégorie")
                    
                    refresh_reports_btn = gr.Button("🔄 Actualiser les Rapports", variant="primary")
                    reports_status = gr.Markdown("")
                
                with gr.Tab("⚙️ Administration"):
                    gr.Markdown("### ⚙️ Administration")
                    gr.Markdown("*Fonctionnalité en cours de développement...*")
        
        # Fonctions de callback
        def handle_login(username, password):
            message, success = app.authenticate(username, password)
            if success:
                user_info = f"✅ Connecté: **{app.current_user}** ({app.user_role})"
                return (
                    message,
                    gr.update(visible=False),  # Cacher login
                    gr.update(visible=True),   # Montrer main
                    user_info,
                    True  # auth_state
                )
            else:
                return (
                    message,
                    gr.update(visible=True),   # Garder login
                    gr.update(visible=False),  # Cacher main
                    "",
                    False  # auth_state
                )
        
        def handle_logout():
            message = app.logout()
            return (
                message,
                gr.update(visible=True),   # Montrer login
                gr.update(visible=False),  # Cacher main
                "",
                False  # auth_state
            )
        
        def refresh_dashboard():
            metrics, charts, recent_trans, status = app.get_dashboard_data()
            
            evolution_plot = charts.get('evolution_solde') if charts else None
            repartition_plot = charts.get('repartition_flux') if charts else None
            capital_plot = charts.get('repartition_capital') if charts else None
            
            return (
                status,
                metrics,
                evolution_plot,
                repartition_plot,
                capital_plot,
                recent_trans if recent_trans and isinstance(recent_trans, list) else []
            )
        
        def add_new_transaction(date_str, trans_type, amount, description, category):
            result = app.add_transaction(date_str, trans_type, amount, description, category)
            return result
        
        def refresh_transactions():
            status, trans_data = app.get_transactions_list()
            return status, trans_data
        
        def add_new_employee(prenom, nom, poste, salaire, date_embauche):
            result = app.add_employee(prenom, nom, poste, salaire, date_embauche)
            return result
        
        def refresh_employees():
            status, emp_data = app.get_employees_list()
            return status, emp_data
        
        def add_new_shareholder(prenom, nom, parts, email, telephone):
            result = app.add_shareholder(prenom, nom, int(parts) if parts else 0, email, telephone)
            return result
        
        def refresh_shareholders():
            status, share_data = app.get_shareholders_list()
            return status, share_data
        
        def pay_monthly_salaries(month):
            result = app.pay_salaries(month)
            return result
        
        def refresh_reports():
            financial, stats, monthly_chart, category_chart, status = app.generate_reports()
            return financial, stats, monthly_chart, category_chart, status
        
        # Connecter les événements
        login_btn.click(
            handle_login,
            inputs=[username_input, password_input],
            outputs=[login_status, login_section, main_section, user_status, auth_state]
        )
        
        logout_btn.click(
            handle_logout,
            outputs=[login_status, login_section, main_section, user_status, auth_state]
        )
        
        refresh_dashboard_btn.click(
            refresh_dashboard,
            outputs=[
                dashboard_status, dashboard_metrics, evolution_chart, 
                repartition_chart, capital_chart, recent_transactions_table
            ]
        )
        
        add_trans_btn.click(
            add_new_transaction,
            inputs=[trans_date, trans_type, trans_amount, trans_description, trans_category],
            outputs=[add_trans_status]
        )
        
        refresh_trans_btn.click(
            refresh_transactions,
            outputs=[trans_list_status, transactions_table]
        )
        
        # Événements pour les employés
        add_emp_btn.click(
            add_new_employee,
            inputs=[emp_prenom, emp_nom, emp_poste, emp_salaire, emp_date_embauche],
            outputs=[add_emp_status]
        )
        
        refresh_emp_btn.click(
            refresh_employees,
            outputs=[emp_list_status, employees_table]
        )
        
        # Événements pour les actionnaires
        add_share_btn.click(
            add_new_shareholder,
            inputs=[share_prenom, share_nom, share_parts, share_email, share_telephone],
            outputs=[add_share_status]
        )
        
        refresh_share_btn.click(
            refresh_shareholders,
            outputs=[share_list_status, shareholders_table]
        )
        
        # Événement pour le paiement des salaires
        pay_salaries_btn.click(
            pay_monthly_salaries,
            inputs=[salary_month],
            outputs=[pay_salaries_status]
        )
        
        # Événement pour les rapports
        refresh_reports_btn.click(
            refresh_reports,
            outputs=[financial_summary, stats_summary, monthly_chart, category_chart, reports_status]
        )
    
    return interface

# Créer et lancer l'interface
if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
