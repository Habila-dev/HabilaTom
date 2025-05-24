import streamlit as st
import pandas as pd
from datetime import date, datetime
import uuid
from models.transaction import Transaction

st.set_page_config(
    page_title="Transactions - Habila Ghost",
    page_icon="💳",
    layout="wide"
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

st.title("💳 Gestion des Transactions")
st.markdown("---")

# Onglets pour organiser les fonctionnalités
tab1, tab2, tab3 = st.tabs(["➕ Nouvelle Transaction", "📋 Liste des Transactions", "✏️ Modifier/Supprimer"])

with tab1:
    st.header("Ajouter une nouvelle transaction")
    
    with st.form("nouvelle_transaction"):
        col1, col2 = st.columns(2)
        
        with col1:
            date_transaction = st.date_input(
                "Date de la transaction",
                value=date.today(),
                max_value=date.today()
            )
            
            type_transaction = st.selectbox(
                "Type de transaction",
                ["Entrée", "Sortie"],
                help="Sélectionnez si c'est une entrée d'argent ou une sortie"
            )
            
            montant = st.number_input(
                "Montant ($)",
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )
        
        with col2:
            description = st.text_area(
                "Description",
                placeholder="Décrivez la transaction...",
                height=100
            )
            
            categories_predefinies = [
                "Vente", "Service", "Investissement", "Subvention",  # Entrées
                "Salaire", "Fournitures", "Marketing", "Transport", "Loyer", "Autre"  # Sorties
            ]
            
            categorie = st.selectbox(
                "Catégorie",
                [""] + categories_predefinies,
                help="Choisissez une catégorie pour mieux organiser vos transactions"
            )
        
        submitted = st.form_submit_button("💾 Enregistrer la Transaction", use_container_width=True)
        
        if submitted:
            if montant > 0 and description.strip():
                try:
                    transaction = Transaction(
                        id=str(uuid.uuid4()),
                        date=date_transaction,
                        type=type_transaction,
                        montant=montant,
                        description=description.strip(),
                        categorie=categorie if categorie else None
                    )
                    
                    if data_manager.save_transaction(transaction):
                        st.success(f"✅ Transaction de ${montant:.2f} enregistrée avec succès!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de l'enregistrement de la transaction.")
                
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires avec des valeurs valides.")

with tab2:
    st.header("Liste de toutes les transactions")
    
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    
    transactions_df = data_manager.load_transactions()
    
    if not transactions_df.empty:
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        
        with col1:
            # Filtre par type
            type_filter = st.selectbox(
                "Filtrer par type",
                ["Tous", "Entrée", "Sortie"]
            )
        
        with col2:
            # Filtre par mois
            months = ["Tous"] + [f"{i:02d}/{datetime.now().year}" for i in range(1, 13)]
            month_filter = st.selectbox("Filtrer par mois", months)
        
        with col3:
            # Filtre par catégorie
            categories = ["Toutes"] + sorted(transactions_df['categorie'].dropna().unique().tolist())
            category_filter = st.selectbox("Filtrer par catégorie", categories)
        
        with col4:
            # Tri
            sort_options = {
                "Date (récent)": ("date", False),
                "Date (ancien)": ("date", True),
                "Montant (↑)": ("montant", True),
                "Montant (↓)": ("montant", False)
            }
            sort_choice = st.selectbox("Trier par", list(sort_options.keys()))
            sort_col, sort_asc = sort_options[sort_choice]
        
        # Appliquer les filtres
        filtered_df = transactions_df.copy()
        
        if type_filter != "Tous":
            filtered_df = filtered_df[filtered_df['type'] == type_filter]
        
        if month_filter != "Tous":
            month_num = int(month_filter.split('/')[0])
            year_num = int(month_filter.split('/')[1])
            filtered_df = filtered_df[
                (filtered_df['date'].dt.month == month_num) & 
                (filtered_df['date'].dt.year == year_num)
            ]
        
        if category_filter != "Toutes":
            filtered_df = filtered_df[filtered_df['categorie'] == category_filter]
        
        # Trier
        filtered_df = filtered_df.sort_values(sort_col, ascending=sort_asc)
        
        # Affichage des résultats
        st.write(f"**{len(filtered_df)} transaction(s) trouvée(s)**")
        
        if not filtered_df.empty:
            # Calculs pour les transactions filtrées
            total_entrees = filtered_df[filtered_df['type'] == 'Entrée']['montant'].sum()
            total_sorties = filtered_df[filtered_df['type'] == 'Sortie']['montant'].sum()
            solde_filtre = total_entrees - total_sorties
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Entrées", f"${total_entrees:,.2f}")
            with col2:
                st.metric("Total Sorties", f"${total_sorties:,.2f}")
            with col3:
                st.metric("Solde", f"${solde_filtre:,.2f}", delta=f"${solde_filtre:+,.2f}")
            
            # Préparer l'affichage
            display_df = filtered_df.copy()
            display_df['date'] = display_df['date'].dt.strftime('%d/%m/%Y')
            display_df['montant_formatted'] = display_df.apply(
                lambda row: f"{'+'if row['type']=='Entrée' else '-'}${row['montant']:,.2f}", 
                axis=1
            )
            
            # Tableau des transactions
            st.dataframe(
                display_df[['date', 'type', 'description', 'montant_formatted', 'categorie']],
                column_config={
                    "date": "Date",
                    "type": "Type",
                    "description": "Description",
                    "montant_formatted": "Montant",
                    "categorie": "Catégorie"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("🔍 Aucune transaction trouvée avec ces filtres.")
    else:
        st.info("📝 Aucune transaction enregistrée. Commencez par ajouter votre première transaction!")

with tab3:
    st.header("Modifier ou supprimer une transaction")
    
    transactions_df = data_manager.load_transactions()
    
    if not transactions_df.empty:
        # Sélection de la transaction à modifier
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        transactions_df['display'] = transactions_df.apply(
            lambda row: f"{row['date'].strftime('%d/%m/%Y')} - {row['type']} - {row['description'][:50]} - {row['montant']:.2f}€",
            axis=1
        )
        
        selected_transaction = st.selectbox(
            "Sélectionnez une transaction à modifier",
            options=transactions_df['id'].tolist(),
            format_func=lambda x: transactions_df[transactions_df['id'] == x]['display'].iloc[0]
        )
        
        if selected_transaction:
            transaction_data = transactions_df[transactions_df['id'] == selected_transaction].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✏️ Modifier")
                
                with st.form("modifier_transaction"):
                    new_date = st.date_input(
                        "Date",
                        value=transaction_data['date'].date()
                    )
                    
                    new_type = st.selectbox(
                        "Type",
                        ["Entrée", "Sortie"],
                        index=0 if transaction_data['type'] == 'Entrée' else 1
                    )
                    
                    new_montant = st.number_input(
                        "Montant (€)",
                        value=float(transaction_data['montant']),
                        min_value=0.01,
                        step=0.01
                    )
                    
                    new_description = st.text_area(
                        "Description",
                        value=transaction_data['description']
                    )
                    
                    categories_predefinies = [
                        "Vente", "Service", "Investissement", "Subvention",
                        "Salaire", "Fournitures", "Marketing", "Transport", "Loyer", "Autre"
                    ]
                    
                    current_category = transaction_data.get('categorie', '')
                    if current_category and current_category not in categories_predefinies:
                        categories_predefinies.append(current_category)
                    
                    new_categorie = st.selectbox(
                        "Catégorie",
                        [""] + categories_predefinies,
                        index=categories_predefinies.index(current_category) + 1 if current_category in categories_predefinies else 0
                    )
                    
                    if st.form_submit_button("💾 Mettre à jour", use_container_width=True):
                        try:
                            updated_transaction = Transaction(
                                id=selected_transaction,
                                date=new_date,
                                type=new_type,
                                montant=new_montant,
                                description=new_description.strip(),
                                categorie=new_categorie if new_categorie else None
                            )
                            
                            if data_manager.update_transaction(selected_transaction, updated_transaction):
                                st.success("✅ Transaction mise à jour avec succès!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la mise à jour.")
                        
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")
            
            with col2:
                st.subheader("🗑️ Supprimer")
                
                # Affichage des détails de la transaction
                st.write("**Détails de la transaction:**")
                st.write(f"**Date:** {transaction_data['date'].strftime('%d/%m/%Y')}")
                st.write(f"**Type:** {transaction_data['type']}")
                st.write(f"**Montant:** {transaction_data['montant']:.2f} €")
                st.write(f"**Description:** {transaction_data['description']}")
                if transaction_data.get('categorie'):
                    st.write(f"**Catégorie:** {transaction_data['categorie']}")
                
                st.warning("⚠️ Cette action est irréversible!")
                
                if st.button("🗑️ Supprimer cette transaction", 
                           type="primary", 
                           use_container_width=True):
                    if data_manager.delete_transaction(selected_transaction):
                        st.success("✅ Transaction supprimée avec succès!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la suppression.")
    else:
        st.info("📝 Aucune transaction disponible pour modification.")

# Statistiques rapides en bas de page
if not transactions_df.empty:
    st.markdown("---")
    st.subheader("📊 Statistiques Rapides")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_transactions = len(transactions_df)
    avg_transaction = transactions_df['montant'].mean()
    max_transaction = transactions_df['montant'].max()
    
    # Transactions ce mois
    current_month_transactions = transactions_df[
        (transactions_df['date'].dt.month == datetime.now().month) &
        (transactions_df['date'].dt.year == datetime.now().year)
    ]
    
    with col1:
        st.metric("Total Transactions", total_transactions)
    
    with col2:
        st.metric("Montant Moyen", f"{avg_transaction:.2f} €")
    
    with col3:
        st.metric("Transaction Max", f"{max_transaction:.2f} €")
    
    with col4:
        st.metric("Transactions ce Mois", len(current_month_transactions))
