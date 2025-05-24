import streamlit as st
import pandas as pd
from datetime import date, datetime
import uuid
import plotly.express as px
import plotly.graph_objects as go
from models.shareholder import Shareholder
from models.transaction import Transaction

st.set_page_config(
    page_title="Actionnaires - Habila Ghost",
    page_icon="📈",
    layout="wide"
)

# Vérifier l'authentification
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Accès non autorisé. Veuillez vous connecter d'abord.")
    st.stop()

# Vérifier si l'utilisateur est administrateur
if st.session_state.get('user_role') != 'Administrateur':
    st.error("❌ Accès restreint aux administrateurs uniquement.")
    st.info("Cette section contient des informations sensibles sur la répartition du capital et les actionnaires de l'entreprise.")
    st.stop()

# Initialisation du gestionnaire de données
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager

st.title("📈 Gestion des Actionnaires")
st.markdown("---")

# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["👥 Actionnaires", "💰 Calcul des Bénéfices", "📊 Distribution", "✏️ Modifier/Supprimer"])

with tab1:
    st.header("Gestion des actionnaires")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Ajouter un actionnaire")
        
        with st.form("nouvel_actionnaire"):
            prenom = st.text_input("Prénom", placeholder="Marie")
            nom = st.text_input("Nom", placeholder="Dubois")
            parts_sociales = st.number_input(
                "Nombre de parts sociales (sur 100 total)",
                min_value=1,
                max_value=100,
                step=1,
                help="Chaque part représente 1% du capital de 150 000 $"
            )
            email = st.text_input("Email (optionnel)", placeholder="marie.dubois@email.com")
            telephone = st.text_input("Téléphone (optionnel)", placeholder="+33 1 23 45 67 89")
            
            if st.form_submit_button("💾 Ajouter l'actionnaire", use_container_width=True):
                if prenom.strip() and nom.strip() and parts_sociales > 0:
                    # Vérifier que le total des parts ne dépasse pas 100
                    shareholders_df = data_manager.load_shareholders()
                    if not shareholders_df.empty:
                        # Gestion de la rétrocompatibilité
                        current_total = 0
                        for _, row in shareholders_df[shareholders_df['actif'] == True].iterrows():
                            if 'parts_sociales' in row and pd.notna(row['parts_sociales']):
                                current_total += int(row['parts_sociales'])
                            elif 'pourcentage_actions' in row and pd.notna(row['pourcentage_actions']):
                                current_total += int(row['pourcentage_actions'])
                        
                        if current_total + parts_sociales > 100:
                            st.error(f"❌ Le total des parts ne peut pas dépasser 100. Actuellement: {current_total} parts")
                        else:
                            try:
                                shareholder = Shareholder(
                                    id=str(uuid.uuid4()),
                                    nom=nom.strip(),
                                    prenom=prenom.strip(),
                                    parts_sociales=parts_sociales,
                                    email=email.strip() if email.strip() else None,
                                    telephone=telephone.strip() if telephone.strip() else None,
                                    actif=True
                                )
                                
                                if data_manager.save_shareholder(shareholder):
                                    valeur = shareholder.valeur_parts
                                    st.success(f"✅ Actionnaire {prenom} {nom} ajouté avec succès! Valeur: ${valeur:,.2f}")
                                    st.rerun()
                                else:
                                    st.error("❌ Erreur lors de l'ajout de l'actionnaire.")
                            
                            except Exception as e:
                                st.error(f"❌ Erreur: {str(e)}")
                    else:
                        # Premier actionnaire
                        try:
                            shareholder = Shareholder(
                                id=str(uuid.uuid4()),
                                nom=nom.strip(),
                                prenom=prenom.strip(),
                                parts_sociales=parts_sociales,
                                email=email.strip() if email.strip() else None,
                                telephone=telephone.strip() if telephone.strip() else None,
                                actif=True
                            )
                            
                            if data_manager.save_shareholder(shareholder):
                                valeur = shareholder.valeur_parts
                                st.success(f"✅ Actionnaire {prenom} {nom} ajouté avec succès! Valeur: ${valeur:,.2f}")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de l'ajout de l'actionnaire.")
                        
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires.")
    
    with col2:
        st.subheader("📋 Liste des actionnaires")
        
        shareholders_df = data_manager.load_shareholders()
        
        if not shareholders_df.empty:
            active_shareholders = shareholders_df[shareholders_df['actif'] == True]
            
            if not active_shareholders.empty:
                display_df = active_shareholders.copy()
                display_df['nom_complet'] = display_df['prenom'] + ' ' + display_df['nom']
                display_df['pourcentage_formatted'] = display_df['pourcentage_actions'].apply(lambda x: f"{x:.2f}%")
                
                st.dataframe(
                    display_df[['nom_complet', 'pourcentage_formatted', 'email', 'telephone']],
                    column_config={
                        "nom_complet": "Nom Complet",
                        "pourcentage_formatted": "% Actions",
                        "email": "Email",
                        "telephone": "Téléphone"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistiques
                total_percentage = active_shareholders['pourcentage_actions'].sum()
                num_shareholders = len(active_shareholders)
                avg_percentage = active_shareholders['pourcentage_actions'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Actionnaires Actifs", num_shareholders)
                with col2:
                    st.metric("Total Actions", f"{total_percentage:.2f}%", 
                             delta=f"{100 - total_percentage:.2f}% disponible" if total_percentage < 100 else "Complet")
                with col3:
                    st.metric("Moyenne par Actionnaire", f"{avg_percentage:.2f}%")
                
                # Graphique de répartition
                if len(active_shareholders) > 1:
                    st.subheader("🥧 Répartition des Actions")
                    
                    fig = px.pie(
                        active_shareholders, 
                        values='pourcentage_actions', 
                        names=active_shareholders['prenom'] + ' ' + active_shareholders['nom'],
                        title="Répartition des Actions par Actionnaire"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tous les actionnaires sont inactifs.")
        else:
            st.info("📈 Aucun actionnaire enregistré.")

with tab2:
    st.header("Calcul des bénéfices à distribuer")
    
    # Charger les données
    transactions_df = data_manager.load_transactions()
    employees_df = data_manager.load_employees()
    shareholders_df = data_manager.load_shareholders()
    
    if not shareholders_df.empty:
        active_shareholders = shareholders_df[shareholders_df['actif'] == True]
        
        if not active_shareholders.empty:
            # Sélection de la période
            col1, col2 = st.columns(2)
            
            with col1:
                period_type = st.selectbox(
                    "Type de période",
                    ["Mensuel", "Trimestriel", "Annuel", "Personnalisé"]
                )
            
            with col2:
                if period_type == "Mensuel":
                    selected_date = st.date_input("Sélectionnez le mois", value=date.today())
                    start_date = date(selected_date.year, selected_date.month, 1)
                    # Dernier jour du mois
                    if selected_date.month == 12:
                        end_date = date(selected_date.year + 1, 1, 1) - pd.Timedelta(days=1)
                    else:
                        end_date = date(selected_date.year, selected_date.month + 1, 1) - pd.Timedelta(days=1)
                    
                elif period_type == "Trimestriel":
                    quarter = st.selectbox("Trimestre", [1, 2, 3, 4])
                    year = st.number_input("Année", value=datetime.now().year, min_value=2020, max_value=2030)
                    start_month = (quarter - 1) * 3 + 1
                    start_date = date(year, start_month, 1)
                    end_month = quarter * 3
                    if end_month == 12:
                        end_date = date(year + 1, 1, 1) - pd.Timedelta(days=1)
                    else:
                        end_date = date(year, end_month + 1, 1) - pd.Timedelta(days=1)
                
                elif period_type == "Annuel":
                    year = st.number_input("Année", value=datetime.now().year, min_value=2020, max_value=2030)
                    start_date = date(year, 1, 1)
                    end_date = date(year, 12, 31)
                
                else:  # Personnalisé
                    col_start, col_end = st.columns(2)
                    with col_start:
                        start_date = st.date_input("Date de début")
                    with col_end:
                        end_date = st.date_input("Date de fin", value=date.today())
            
            st.markdown("---")
            
            # Calculs financiers
            if not transactions_df.empty:
                transactions_df['date'] = pd.to_datetime(transactions_df['date'])
                period_transactions = transactions_df[
                    (transactions_df['date'].dt.date >= start_date) &
                    (transactions_df['date'].dt.date <= end_date)
                ]
                
                if not period_transactions.empty:
                    total_income = period_transactions[period_transactions['type'] == 'Entrée']['montant'].sum()
                    total_expenses = period_transactions[period_transactions['type'] == 'Sortie']['montant'].sum()
                else:
                    total_income = 0
                    total_expenses = 0
            else:
                total_income = 0
                total_expenses = 0
            
            # Calcul des salaires pour la période
            if not employees_df.empty:
                active_employees = employees_df[employees_df['actif'] == True]
                # Calculer le nombre de mois dans la période
                months_in_period = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
                theoretical_salaries = active_employees['salaire_mensuel'].sum() * months_in_period
            else:
                theoretical_salaries = 0
            
            # Calcul du bénéfice net
            gross_profit = total_income - total_expenses
            net_profit_after_salaries = gross_profit - theoretical_salaries
            distributable_profit = max(0, net_profit_after_salaries)
            
            # Affichage des résultats
            st.subheader(f"📊 Résultats pour la période du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💵 Total Entrées", f"{total_income:,.2f} €")
            
            with col2:
                st.metric("💸 Total Sorties", f"{total_expenses:,.2f} €")
            
            with col3:
                st.metric("💰 Bénéfice Brut", f"{gross_profit:,.2f} €", 
                         delta=f"{gross_profit:+,.2f} €")
            
            with col4:
                st.metric("🎯 Bénéfice Distribuable", f"{distributable_profit:,.2f} €",
                         delta=f"Après salaires théoriques: {theoretical_salaries:,.2f} €")
            
            if distributable_profit > 0:
                st.success(f"✅ Bénéfices disponibles pour distribution: {distributable_profit:,.2f} €")
                
                # Calcul des parts par actionnaire
                st.subheader("💰 Répartition par actionnaire")
                
                distribution_data = []
                for _, shareholder in active_shareholders.iterrows():
                    share_amount = (shareholder['pourcentage_actions'] / 100) * distributable_profit
                    distribution_data.append({
                        'actionnaire': f"{shareholder['prenom']} {shareholder['nom']}",
                        'pourcentage': shareholder['pourcentage_actions'],
                        'montant': share_amount
                    })
                
                distribution_df = pd.DataFrame(distribution_data)
                
                st.dataframe(
                    distribution_df,
                    column_config={
                        "actionnaire": "Actionnaire",
                        "pourcentage": st.column_config.NumberColumn("% Actions", format="%.2f%%"),
                        "montant": st.column_config.NumberColumn("Montant à Recevoir", format="%.2f €")
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Bouton pour enregistrer les distributions
                st.markdown("---")
                if st.button("💳 Enregistrer les distributions comme transactions", 
                           type="primary", 
                           use_container_width=True):
                    
                    success_count = 0
                    for _, row in distribution_df.iterrows():
                        transaction = Transaction(
                            id=str(uuid.uuid4()),
                            date=date.today(),
                            type="Sortie",
                            montant=row['montant'],
                            description=f"Distribution bénéfices - {row['actionnaire']} ({period_type.lower()} {start_date.strftime('%m/%Y')} à {end_date.strftime('%m/%Y')})",
                            categorie="Distribution Bénéfices"
                        )
                        
                        if data_manager.save_transaction(transaction):
                            success_count += 1
                    
                    if success_count == len(distribution_df):
                        st.success(f"✅ {success_count} distributions enregistrées avec succès!")
                        st.rerun()
                    else:
                        st.error(f"❌ Erreur: seulement {success_count}/{len(distribution_df)} distributions enregistrées.")
            
            elif gross_profit > 0:
                st.warning(f"⚠️ Bénéfice brut de {gross_profit:,.2f} € disponible, mais {theoretical_salaries:,.2f} € nécessaires pour les salaires.")
            else:
                st.error(f"❌ Aucun bénéfice à distribuer. Résultat: {gross_profit:,.2f} €")
        else:
            st.info("📈 Aucun actionnaire actif pour calculer les bénéfices.")
    else:
        st.info("📈 Aucun actionnaire enregistré.")

with tab3:
    st.header("Historique des distributions")
    
    transactions_df = data_manager.load_transactions()
    
    if not transactions_df.empty:
        # Filtrer les transactions de distribution
        distribution_transactions = transactions_df[
            transactions_df['description'].str.contains('Distribution bénéfices', na=False)
        ].copy()
        
        if not distribution_transactions.empty:
            # Filtres
            col1, col2 = st.columns(2)
            
            with col1:
                years = sorted(pd.to_datetime(distribution_transactions['date']).dt.year.unique(), reverse=True)
                selected_year = st.selectbox(
                    "Filtrer par année",
                    ["Toutes"] + [str(year) for year in years]
                )
            
            with col2:
                # Extraire les noms des actionnaires des descriptions
                shareholder_names = set()
                for desc in distribution_transactions['description']:
                    if ' - ' in desc and 'Distribution bénéfices - ' in desc:
                        name_part = desc.split('Distribution bénéfices - ')[1]
                        if ' (' in name_part:
                            name = name_part.split(' (')[0]
                            shareholder_names.add(name)
                
                selected_shareholder = st.selectbox(
                    "Filtrer par actionnaire",
                    ["Tous"] + sorted(list(shareholder_names))
                )
            
            # Appliquer les filtres
            filtered_distributions = distribution_transactions.copy()
            
            if selected_year != "Toutes":
                filtered_distributions['date'] = pd.to_datetime(filtered_distributions['date'])
                filtered_distributions = filtered_distributions[
                    filtered_distributions['date'].dt.year == int(selected_year)
                ]
            
            if selected_shareholder != "Tous":
                filtered_distributions = filtered_distributions[
                    filtered_distributions['description'].str.contains(selected_shareholder, na=False)
                ]
            
            # Affichage
            if not filtered_distributions.empty:
                st.write(f"**{len(filtered_distributions)} distribution(s) trouvée(s)**")
                
                # Préparer l'affichage
                display_df = filtered_distributions.copy()
                display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%d/%m/%Y')
                display_df = display_df.sort_values('date', ascending=False)
                
                st.dataframe(
                    display_df[['date', 'description', 'montant']],
                    column_config={
                        "date": "Date",
                        "description": "Description",
                        "montant": st.column_config.NumberColumn("Montant", format="%.2f €")
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistiques
                total_distributed = filtered_distributions['montant'].sum()
                avg_distribution = filtered_distributions['montant'].mean()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Distribué", f"{total_distributed:,.2f} €")
                with col2:
                    st.metric("Distribution Moyenne", f"{avg_distribution:,.2f} €")
                
                # Graphique des distributions par actionnaire
                if len(filtered_distributions) > 1:
                    st.subheader("📊 Distributions par Actionnaire")
                    
                    # Extraire les noms des actionnaires et grouper
                    distribution_by_shareholder = {}
                    for _, row in filtered_distributions.iterrows():
                        desc = row['description']
                        if 'Distribution bénéfices - ' in desc:
                            name_part = desc.split('Distribution bénéfices - ')[1]
                            if ' (' in name_part:
                                name = name_part.split(' (')[0]
                                if name in distribution_by_shareholder:
                                    distribution_by_shareholder[name] += row['montant']
                                else:
                                    distribution_by_shareholder[name] = row['montant']
                    
                    if distribution_by_shareholder:
                        fig = px.bar(
                            x=list(distribution_by_shareholder.keys()),
                            y=list(distribution_by_shareholder.values()),
                            title="Distributions par Actionnaire",
                            labels={'x': 'Actionnaire', 'y': 'Montant Total (€)'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🔍 Aucune distribution trouvée avec ces filtres.")
        else:
            st.info("💰 Aucune distribution de bénéfices enregistrée.")
    else:
        st.info("📝 Aucune transaction disponible.")

with tab4:
    st.header("Modifier ou supprimer un actionnaire")
    
    shareholders_df = data_manager.load_shareholders()
    
    if not shareholders_df.empty:
        # Sélection de l'actionnaire
        shareholders_df['display'] = shareholders_df.apply(
            lambda row: f"{row['prenom']} {row['nom']} - {row['pourcentage_actions']:.2f}% ({'Actif' if row['actif'] else 'Inactif'})",
            axis=1
        )
        
        selected_shareholder_id = st.selectbox(
            "Sélectionnez un actionnaire",
            shareholders_df['id'].tolist(),
            format_func=lambda x: shareholders_df[shareholders_df['id'] == x]['display'].iloc[0]
        )
        
        if selected_shareholder_id:
            shareholder_data = shareholders_df[shareholders_df['id'] == selected_shareholder_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✏️ Modifier")
                
                with st.form("modifier_actionnaire"):
                    new_prenom = st.text_input("Prénom", value=shareholder_data['prenom'])
                    new_nom = st.text_input("Nom", value=shareholder_data['nom'])
                    
                    # Vérifier les pourcentages pour la validation
                    other_shareholders_total = shareholders_df[
                        (shareholders_df['id'] != selected_shareholder_id) & 
                        (shareholders_df['actif'] == True)
                    ]['pourcentage_actions'].sum()
                    
                    max_percentage = 100 - other_shareholders_total
                    
                    new_pourcentage = st.number_input(
                        f"Pourcentage d'actions (%) - Max: {max_percentage:.2f}%",
                        value=float(shareholder_data['pourcentage_actions']),
                        min_value=0.01,
                        max_value=max_percentage,
                        step=0.01
                    )
                    
                    new_email = st.text_input(
                        "Email",
                        value=shareholder_data.get('email', '') or ''
                    )
                    new_telephone = st.text_input(
                        "Téléphone",
                        value=shareholder_data.get('telephone', '') or ''
                    )
                    new_actif = st.checkbox(
                        "Actionnaire actif",
                        value=bool(shareholder_data['actif'])
                    )
                    
                    if st.form_submit_button("💾 Mettre à jour", use_container_width=True):
                        try:
                            updated_shareholder = Shareholder(
                                id=selected_shareholder_id,
                                nom=new_nom.strip(),
                                prenom=new_prenom.strip(),
                                pourcentage_actions=new_pourcentage,
                                email=new_email.strip() if new_email.strip() else None,
                                telephone=new_telephone.strip() if new_telephone.strip() else None,
                                actif=new_actif
                            )
                            
                            if data_manager.update_shareholder(selected_shareholder_id, updated_shareholder):
                                st.success("✅ Actionnaire mis à jour avec succès!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la mise à jour.")
                        
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")
            
            with col2:
                st.subheader("🗑️ Supprimer")
                
                # Affichage des détails
                st.write("**Détails de l'actionnaire:**")
                st.write(f"**Nom:** {shareholder_data['prenom']} {shareholder_data['nom']}")
                st.write(f"**Pourcentage:** {shareholder_data['pourcentage_actions']:.2f}%")
                if shareholder_data.get('email'):
                    st.write(f"**Email:** {shareholder_data['email']}")
                if shareholder_data.get('telephone'):
                    st.write(f"**Téléphone:** {shareholder_data['telephone']}")
                st.write(f"**Statut:** {'Actif' if shareholder_data['actif'] else 'Inactif'}")
                
                st.warning("⚠️ Cette action supprimera définitivement l'actionnaire!")
                st.info("💡 Conseil: Désactivez plutôt l'actionnaire pour conserver l'historique.")
                
                if st.button("🗑️ Supprimer cet actionnaire", 
                           type="primary", 
                           use_container_width=True):
                    if data_manager.delete_shareholder(selected_shareholder_id):
                        st.success("✅ Actionnaire supprimé avec succès!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la suppression.")
    else:
        st.info("📈 Aucun actionnaire disponible pour modification.")
