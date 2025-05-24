import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from utils.data_manager import DataManager
from models.transaction import Transaction
from models.employee import Employee
from models.shareholder import Shareholder

# Configuration de la page
st.set_page_config(
    page_title="Habila Ghost - Gestion Financière",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation du gestionnaire de données
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager

# Titre principal
st.title("💰 Habila Ghost - Gestion Financière")
st.markdown("---")

# Sidebar pour navigation
st.sidebar.title("📊 Navigation")
st.sidebar.markdown("Utilisez les pages ci-dessous pour naviguer dans l'application")

# Tableau de bord principal
st.header("📈 Tableau de Bord")

# Métriques principales
col1, col2, col3, col4 = st.columns(4)

# Chargement des données
transactions_df = data_manager.load_transactions()
employees_df = data_manager.load_employees()
shareholders_df = data_manager.load_shareholders()

# Calculs des totaux
total_income = transactions_df[transactions_df['type'] == 'Entrée']['montant'].sum() if not transactions_df.empty else 0
total_expenses = transactions_df[transactions_df['type'] == 'Sortie']['montant'].sum() if not transactions_df.empty else 0
current_balance = total_income - total_expenses

# Calcul des salaires dus ce mois
current_month = datetime.now().month
current_year = datetime.now().year
monthly_salary_due = 0

if not employees_df.empty:
    for _, employee in employees_df.iterrows():
        # Calculer les paiements déjà effectués ce mois
        employee_payments = transactions_df[
            (transactions_df['description'].str.contains(f"Salaire - {employee['nom']}", na=False)) &
            (pd.to_datetime(transactions_df['date']).dt.month == current_month) &
            (pd.to_datetime(transactions_df['date']).dt.year == current_year)
        ]['montant'].sum()
        
        remaining = employee['salaire_mensuel'] - employee_payments
        if remaining > 0:
            monthly_salary_due += remaining

with col1:
    st.metric("💵 Total Entrées", f"{total_income:,.2f} €", delta=None)

with col2:
    st.metric("💸 Total Sorties", f"{total_expenses:,.2f} €", delta=None)

with col3:
    st.metric("💰 Solde Actuel", f"{current_balance:,.2f} €", 
              delta=f"{current_balance:+,.2f} €" if current_balance != 0 else None,
              delta_color="normal" if current_balance >= 0 else "inverse")

with col4:
    st.metric("⏰ Salaires Dus ce Mois", f"{monthly_salary_due:,.2f} €",
              delta=None if monthly_salary_due == 0 else f"-{monthly_salary_due:,.2f} €",
              delta_color="inverse" if monthly_salary_due > 0 else "normal")

st.markdown("---")

# Graphiques
if not transactions_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Évolution du Solde")
        
        # Préparer les données pour le graphique
        transactions_sorted = transactions_df.sort_values('date')
        transactions_sorted['solde_cumulé'] = 0
        
        running_balance = 0
        for idx, row in transactions_sorted.iterrows():
            if row['type'] == 'Entrée':
                running_balance += row['montant']
            else:
                running_balance -= row['montant']
            transactions_sorted.at[idx, 'solde_cumulé'] = running_balance
        
        fig = px.line(transactions_sorted, x='date', y='solde_cumulé',
                     title='Évolution du Solde dans le Temps')
        fig.update_layout(xaxis_title="Date", yaxis_title="Solde (€)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Répartition des Transactions")
        
        # Grouper les transactions par type
        summary_data = transactions_df.groupby('type')['montant'].sum().reset_index()
        
        fig = px.pie(summary_data, values='montant', names='type',
                    title='Répartition Entrées vs Sorties')
        st.plotly_chart(fig, use_container_width=True)

# Transactions récentes
st.subheader("📋 Dernières Transactions")

if not transactions_df.empty:
    recent_transactions = transactions_df.sort_values('date', ascending=False).head(10)
    
    # Formater l'affichage
    display_df = recent_transactions.copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%d/%m/%Y')
    display_df['montant'] = display_df['montant'].apply(lambda x: f"{x:,.2f} €")
    
    st.dataframe(
        display_df[['date', 'type', 'description', 'montant']],
        column_config={
            "date": "Date",
            "type": "Type",
            "description": "Description",
            "montant": "Montant"
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("🔍 Aucune transaction enregistrée. Utilisez la page 'Transactions' pour commencer.")

# Actions rapides
st.markdown("---")
st.subheader("⚡ Actions Rapides")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ Nouvelle Transaction", use_container_width=True):
        st.switch_page("pages/1_Transactions.py")

with col2:
    if st.button("👥 Gérer Employés", use_container_width=True):
        st.switch_page("pages/2_Salaires.py")

with col3:
    if st.button("📊 Générer Rapport", use_container_width=True):
        st.switch_page("pages/4_Rapports.py")

# Alertes importantes
st.markdown("---")
st.subheader("⚠️ Alertes")

alerts = []

# Vérifier les salaires dus
if monthly_salary_due > 0:
    alerts.append(f"💼 Salaires à payer ce mois : {monthly_salary_due:,.2f} €")

# Vérifier le solde négatif
if current_balance < 0:
    alerts.append(f"⚠️ Solde négatif : {current_balance:,.2f} €")

# Vérifier les bénéfices à distribuer
net_profit = current_balance - monthly_salary_due
if net_profit > 1000 and not shareholders_df.empty:
    alerts.append(f"💰 Bénéfices disponibles pour distribution : {net_profit:,.2f} €")

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("✅ Aucune alerte active")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>Habila Ghost - Système de Gestion Financière | Développé avec Streamlit</p>
    </div>
    """, 
    unsafe_allow_html=True
)
