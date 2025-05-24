import streamlit as st
import pandas as pd
from datetime import date, datetime
import uuid
from models.employee import Employee
from models.transaction import Transaction

st.set_page_config(
    page_title="Salaires - Habila Ghost",
    page_icon="👥",
    layout="wide"
)

# Initialisation du gestionnaire de données
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager

st.title("👥 Gestion des Salaires")
st.markdown("---")

# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["👤 Employés", "💰 Payer Salaires", "📊 Historique", "✏️ Modifier/Supprimer"])

with tab1:
    st.header("Gestion des employés")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Ajouter un employé")
        
        with st.form("nouvel_employe"):
            prenom = st.text_input("Prénom", placeholder="Jean")
            nom = st.text_input("Nom", placeholder="Dupont")
            poste = st.text_input("Poste", placeholder="Développeur")
            salaire_mensuel = st.number_input(
                "Salaire mensuel (€)",
                min_value=0.01,
                step=100.00,
                format="%.2f"
            )
            date_embauche = st.date_input(
                "Date d'embauche",
                value=date.today(),
                max_value=date.today()
            )
            
            if st.form_submit_button("💾 Ajouter l'employé", use_container_width=True):
                if prenom.strip() and nom.strip() and poste.strip() and salaire_mensuel > 0:
                    try:
                        employee = Employee(
                            id=str(uuid.uuid4()),
                            nom=nom.strip(),
                            prenom=prenom.strip(),
                            poste=poste.strip(),
                            salaire_mensuel=salaire_mensuel,
                            date_embauche=date_embauche,
                            actif=True
                        )
                        
                        if data_manager.save_employee(employee):
                            st.success(f"✅ Employé {prenom} {nom} ajouté avec succès!")
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de l'ajout de l'employé.")
                    
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires.")
    
    with col2:
        st.subheader("📋 Liste des employés")
        
        employees_df = data_manager.load_employees()
        
        if not employees_df.empty:
            # Filtrer les employés actifs
            active_employees = employees_df[employees_df['actif'] == True]
            
            if not active_employees.empty:
                display_df = active_employees.copy()
                display_df['date_embauche'] = pd.to_datetime(display_df['date_embauche']).dt.strftime('%d/%m/%Y')
                display_df['nom_complet'] = display_df['prenom'] + ' ' + display_df['nom']
                display_df['salaire_formatted'] = display_df['salaire_mensuel'].apply(lambda x: f"{x:,.2f} €")
                
                st.dataframe(
                    display_df[['nom_complet', 'poste', 'salaire_formatted', 'date_embauche']],
                    column_config={
                        "nom_complet": "Nom Complet",
                        "poste": "Poste",
                        "salaire_formatted": "Salaire Mensuel",
                        "date_embauche": "Date d'Embauche"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistiques
                total_employees = len(active_employees)
                total_monthly_salaries = active_employees['salaire_mensuel'].sum()
                avg_salary = active_employees['salaire_mensuel'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Employés Actifs", total_employees)
                with col2:
                    st.metric("Total Salaires/Mois", f"{total_monthly_salaries:,.2f} €")
                with col3:
                    st.metric("Salaire Moyen", f"{avg_salary:,.2f} €")
            else:
                st.info("Tous les employés sont inactifs.")
        else:
            st.info("👥 Aucun employé enregistré.")

with tab2:
    st.header("Paiement des salaires")
    
    employees_df = data_manager.load_employees()
    transactions_df = data_manager.load_transactions()
    
    if not employees_df.empty:
        active_employees = employees_df[employees_df['actif'] == True]
        
        if not active_employees.empty:
            # Sélection du mois pour les paiements
            col1, col2 = st.columns(2)
            
            with col1:
                selected_year = st.selectbox(
                    "Année",
                    [datetime.now().year - 1, datetime.now().year, datetime.now().year + 1],
                    index=1
                )
            
            with col2:
                selected_month = st.selectbox(
                    "Mois",
                    [(i, f"{i:02d} - {['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i-1]}") for i in range(1, 13)],
                    format_func=lambda x: x[1],
                    index=datetime.now().month - 1
                )[0]
            
            st.markdown("---")
            
            # Tableau des paiements pour le mois sélectionné
            st.subheader(f"État des salaires pour {selected_month:02d}/{selected_year}")
            
            payment_data = []
            
            for _, employee in active_employees.iterrows():
                # Calculer les paiements déjà effectués pour ce mois
                if not transactions_df.empty:
                    transactions_df['date'] = pd.to_datetime(transactions_df['date'])
                    employee_payments = transactions_df[
                        (transactions_df['description'].str.contains(f"Salaire - {employee['nom']}", na=False)) &
                        (transactions_df['date'].dt.month == selected_month) &
                        (transactions_df['date'].dt.year == selected_year)
                    ]['montant'].sum()
                else:
                    employee_payments = 0
                
                remaining = employee['salaire_mensuel'] - employee_payments
                status = "✅ Payé" if remaining <= 0 else "⏰ En attente"
                
                payment_data.append({
                    'id': employee['id'],
                    'nom_complet': f"{employee['prenom']} {employee['nom']}",
                    'poste': employee['poste'],
                    'salaire_du': employee['salaire_mensuel'],
                    'deja_paye': employee_payments,
                    'reste_a_payer': max(0, remaining),
                    'statut': status
                })
            
            payment_df = pd.DataFrame(payment_data)
            
            # Affichage du tableau
            st.dataframe(
                payment_df[['nom_complet', 'poste', 'salaire_du', 'deja_paye', 'reste_a_payer', 'statut']],
                column_config={
                    "nom_complet": "Employé",
                    "poste": "Poste",
                    "salaire_du": st.column_config.NumberColumn("Salaire Dû", format="%.2f €"),
                    "deja_paye": st.column_config.NumberColumn("Déjà Payé", format="%.2f €"),
                    "reste_a_payer": st.column_config.NumberColumn("Reste à Payer", format="%.2f €"),
                    "statut": "Statut"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Section de paiement
            st.markdown("---")
            st.subheader("💰 Effectuer un paiement")
            
            # Sélection de l'employé à payer
            unpaid_employees = payment_df[payment_df['reste_a_payer'] > 0]
            
            if not unpaid_employees.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_employee_id = st.selectbox(
                        "Sélectionnez un employé",
                        unpaid_employees['id'].tolist(),
                        format_func=lambda x: unpaid_employees[unpaid_employees['id'] == x]['nom_complet'].iloc[0]
                    )
                    
                    if selected_employee_id:
                        employee_info = unpaid_employees[unpaid_employees['id'] == selected_employee_id].iloc[0]
                        max_amount = employee_info['reste_a_payer']
                        
                        st.info(f"Reste à payer: {max_amount:.2f} €")
                
                with col2:
                    with st.form("paiement_salaire"):
                        montant_paiement = st.number_input(
                            "Montant du paiement (€)",
                            min_value=0.01,
                            max_value=max_amount,
                            value=max_amount,
                            step=0.01
                        )
                        
                        date_paiement = st.date_input(
                            "Date du paiement",
                            value=date.today(),
                            max_value=date.today()
                        )
                        
                        note_paiement = st.text_area(
                            "Note (optionnel)",
                            placeholder="Remarques sur le paiement..."
                        )
                        
                        if st.form_submit_button("💳 Effectuer le paiement", use_container_width=True):
                            if selected_employee_id and montant_paiement > 0:
                                try:
                                    employee_name = employee_info['nom_complet']
                                    description = f"Salaire - {employee_name} ({selected_month:02d}/{selected_year})"
                                    if note_paiement.strip():
                                        description += f" - {note_paiement.strip()}"
                                    
                                    transaction = Transaction(
                                        id=str(uuid.uuid4()),
                                        date=date_paiement,
                                        type="Sortie",
                                        montant=montant_paiement,
                                        description=description,
                                        categorie="Salaire"
                                    )
                                    
                                    if data_manager.save_transaction(transaction):
                                        st.success(f"✅ Paiement de {montant_paiement:.2f}€ effectué pour {employee_name}!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Erreur lors de l'enregistrement du paiement.")
                                
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
            else:
                st.success("✅ Tous les salaires pour ce mois ont été payés!")
        else:
            st.info("👥 Aucun employé actif pour effectuer des paiements.")
    else:
        st.info("👥 Aucun employé enregistré.")

with tab3:
    st.header("Historique des paiements")
    
    transactions_df = data_manager.load_transactions()
    employees_df = data_manager.load_employees()
    
    if not transactions_df.empty and not employees_df.empty:
        # Filtrer les transactions de salaires
        salary_transactions = transactions_df[
            transactions_df['description'].str.contains('Salaire -', na=False)
        ].copy()
        
        if not salary_transactions.empty:
            # Filtres
            col1, col2 = st.columns(2)
            
            with col1:
                # Filtre par employé
                employee_names = []
                for _, emp in employees_df.iterrows():
                    employee_names.append(f"{emp['prenom']} {emp['nom']}")
                
                selected_employee_filter = st.selectbox(
                    "Filtrer par employé",
                    ["Tous"] + employee_names
                )
            
            with col2:
                # Filtre par période
                years = sorted(pd.to_datetime(salary_transactions['date']).dt.year.unique(), reverse=True)
                selected_year_filter = st.selectbox(
                    "Filtrer par année",
                    ["Toutes"] + [str(year) for year in years]
                )
            
            # Appliquer les filtres
            filtered_transactions = salary_transactions.copy()
            
            if selected_employee_filter != "Tous":
                filtered_transactions = filtered_transactions[
                    filtered_transactions['description'].str.contains(selected_employee_filter, na=False)
                ]
            
            if selected_year_filter != "Toutes":
                filtered_transactions['date'] = pd.to_datetime(filtered_transactions['date'])
                filtered_transactions = filtered_transactions[
                    filtered_transactions['date'].dt.year == int(selected_year_filter)
                ]
            
            # Affichage
            if not filtered_transactions.empty:
                st.write(f"**{len(filtered_transactions)} paiement(s) trouvé(s)**")
                
                # Préparer l'affichage
                display_df = filtered_transactions.copy()
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
                total_paid = filtered_transactions['montant'].sum()
                avg_payment = filtered_transactions['montant'].mean()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Payé", f"{total_paid:,.2f} €")
                with col2:
                    st.metric("Paiement Moyen", f"{avg_payment:,.2f} €")
            else:
                st.info("🔍 Aucun paiement trouvé avec ces filtres.")
        else:
            st.info("💳 Aucun paiement de salaire enregistré.")
    else:
        st.info("📝 Aucune donnée disponible pour l'historique.")

with tab4:
    st.header("Modifier ou supprimer un employé")
    
    employees_df = data_manager.load_employees()
    
    if not employees_df.empty:
        # Sélection de l'employé
        employees_df['display'] = employees_df.apply(
            lambda row: f"{row['prenom']} {row['nom']} - {row['poste']} ({'Actif' if row['actif'] else 'Inactif'})",
            axis=1
        )
        
        selected_employee_id = st.selectbox(
            "Sélectionnez un employé",
            employees_df['id'].tolist(),
            format_func=lambda x: employees_df[employees_df['id'] == x]['display'].iloc[0]
        )
        
        if selected_employee_id:
            employee_data = employees_df[employees_df['id'] == selected_employee_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✏️ Modifier")
                
                with st.form("modifier_employe"):
                    new_prenom = st.text_input("Prénom", value=employee_data['prenom'])
                    new_nom = st.text_input("Nom", value=employee_data['nom'])
                    new_poste = st.text_input("Poste", value=employee_data['poste'])
                    new_salaire = st.number_input(
                        "Salaire mensuel (€)",
                        value=float(employee_data['salaire_mensuel']),
                        min_value=0.01,
                        step=100.00
                    )
                    new_date_embauche = st.date_input(
                        "Date d'embauche",
                        value=pd.to_datetime(employee_data['date_embauche']).date()
                    )
                    new_actif = st.checkbox(
                        "Employé actif",
                        value=bool(employee_data['actif'])
                    )
                    
                    if st.form_submit_button("💾 Mettre à jour", use_container_width=True):
                        try:
                            updated_employee = Employee(
                                id=selected_employee_id,
                                nom=new_nom.strip(),
                                prenom=new_prenom.strip(),
                                poste=new_poste.strip(),
                                salaire_mensuel=new_salaire,
                                date_embauche=new_date_embauche,
                                actif=new_actif
                            )
                            
                            if data_manager.update_employee(selected_employee_id, updated_employee):
                                st.success("✅ Employé mis à jour avec succès!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la mise à jour.")
                        
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")
            
            with col2:
                st.subheader("🗑️ Supprimer")
                
                # Affichage des détails
                st.write("**Détails de l'employé:**")
                st.write(f"**Nom:** {employee_data['prenom']} {employee_data['nom']}")
                st.write(f"**Poste:** {employee_data['poste']}")
                st.write(f"**Salaire:** {employee_data['salaire_mensuel']:.2f} €")
                st.write(f"**Date d'embauche:** {pd.to_datetime(employee_data['date_embauche']).strftime('%d/%m/%Y')}")
                st.write(f"**Statut:** {'Actif' if employee_data['actif'] else 'Inactif'}")
                
                st.warning("⚠️ Cette action supprimera définitivement l'employé!")
                st.info("💡 Conseil: Désactivez plutôt l'employé pour conserver l'historique.")
                
                if st.button("🗑️ Supprimer cet employé", 
                           type="primary", 
                           use_container_width=True):
                    if data_manager.delete_employee(selected_employee_id):
                        st.success("✅ Employé supprimé avec succès!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la suppression.")
    else:
        st.info("👥 Aucun employé disponible pour modification.")
