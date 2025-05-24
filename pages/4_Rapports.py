import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from utils.excel_exporter import ExcelExporter

st.set_page_config(
    page_title="Rapports - Habila Ghost",
    page_icon="📊",
    layout="wide"
)

# Initialisation du gestionnaire de données
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager
excel_exporter = ExcelExporter(data_manager)

st.title("📊 Rapports et Analyses")
st.markdown("---")

# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["📈 Tableau de Bord", "📋 Rapports Mensuels", "📊 Analyses", "📥 Exports"])

with tab1:
    st.header("Tableau de bord analytique")
    
    # Charger les données
    transactions_df = data_manager.load_transactions()
    employees_df = data_manager.load_employees()
    shareholders_df = data_manager.load_shareholders()
    
    if not transactions_df.empty:
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        
        # Période d'analyse
        col1, col2 = st.columns(2)
        
        with col1:
            period_options = {
                "7 derniers jours": 7,
                "30 derniers jours": 30,
                "90 derniers jours": 90,
                "6 derniers mois": 180,
                "1 an": 365
            }
            selected_period = st.selectbox("Période d'analyse", list(period_options.keys()), index=2)
            days_back = period_options[selected_period]
        
        with col2:
            end_date = st.date_input("Jusqu'au", value=date.today(), max_value=date.today())
        
        # Filtrer les données
        start_date = end_date - timedelta(days=days_back)
        period_transactions = transactions_df[
            (transactions_df['date'].dt.date >= start_date) &
            (transactions_df['date'].dt.date <= end_date)
        ]
        
        if not period_transactions.empty:
            # KPIs principaux
            total_income = period_transactions[period_transactions['type'] == 'Entrée']['montant'].sum()
            total_expenses = period_transactions[period_transactions['type'] == 'Sortie']['montant'].sum()
            net_result = total_income - total_expenses
            num_transactions = len(period_transactions)
            avg_transaction = period_transactions['montant'].mean()
            
            # Affichage des KPIs
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💵 Entrées", f"{total_income:,.2f} €")
            
            with col2:
                st.metric("💸 Sorties", f"{total_expenses:,.2f} €")
            
            with col3:
                st.metric("💰 Résultat Net", f"{net_result:,.2f} €", 
                         delta=f"{net_result:+,.2f} €" if net_result != 0 else None)
            
            with col4:
                st.metric("📊 Nb Transactions", num_transactions)
            
            with col5:
                st.metric("📈 Moyenne/Transaction", f"{avg_transaction:,.2f} €")
            
            st.markdown("---")
            
            # Graphiques analytiques
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Évolution des Flux Financiers")
                
                # Regrouper par jour
                daily_data = period_transactions.groupby([
                    period_transactions['date'].dt.date, 'type'
                ])['montant'].sum().reset_index()
                
                fig = px.line(daily_data, 
                            x='date', 
                            y='montant', 
                            color='type',
                            title='Évolution Quotidienne des Entrées et Sorties')
                fig.update_layout(xaxis_title="Date", yaxis_title="Montant (€)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🥧 Répartition par Catégorie")
                
                # Catégories pour les sorties
                expenses_by_category = period_transactions[
                    (period_transactions['type'] == 'Sortie') & 
                    (period_transactions['categorie'].notna())
                ].groupby('categorie')['montant'].sum().reset_index()
                
                if not expenses_by_category.empty:
                    fig = px.pie(expenses_by_category, 
                               values='montant', 
                               names='categorie',
                               title='Répartition des Dépenses par Catégorie')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données de catégories pour cette période")
            
            # Analyse des tendances
            st.subheader("📊 Analyse des Tendances")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution mensuelle
                if days_back >= 60:  # Si période assez longue pour analyse mensuelle
                    monthly_data = period_transactions.groupby([
                        period_transactions['date'].dt.to_period('M'), 'type'
                    ])['montant'].sum().reset_index()
                    monthly_data['date'] = monthly_data['date'].astype(str)
                    
                    fig = px.bar(monthly_data, 
                               x='date', 
                               y='montant', 
                               color='type',
                               title='Évolution Mensuelle',
                               barmode='group')
                    fig.update_layout(xaxis_title="Mois", yaxis_title="Montant (€)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Évolution hebdomadaire pour périodes courtes
                    weekly_data = period_transactions.groupby([
                        period_transactions['date'].dt.to_period('W'), 'type'
                    ])['montant'].sum().reset_index()
                    weekly_data['date'] = weekly_data['date'].astype(str)
                    
                    fig = px.bar(weekly_data, 
                               x='date', 
                               y='montant', 
                               color='type',
                               title='Évolution Hebdomadaire',
                               barmode='group')
                    fig.update_layout(xaxis_title="Semaine", yaxis_title="Montant (€)")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top des transactions
                st.subheader("🔝 Top 10 des Transactions")
                
                top_transactions = period_transactions.nlargest(10, 'montant')
                display_df = top_transactions[['date', 'type', 'description', 'montant']].copy()
                display_df['date'] = display_df['date'].dt.strftime('%d/%m/%Y')
                display_df['montant'] = display_df['montant'].apply(lambda x: f"{x:,.2f} €")
                
                st.dataframe(
                    display_df,
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
            st.info(f"🔍 Aucune transaction trouvée pour la période du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}")
    else:
        st.info("📝 Aucune transaction disponible pour l'analyse.")

with tab2:
    st.header("Rapports mensuels détaillés")
    
    # Sélection du mois
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.selectbox(
            "Année",
            [datetime.now().year - 2, datetime.now().year - 1, datetime.now().year, datetime.now().year + 1],
            index=2
        )
    
    with col2:
        months = [
            (1, "Janvier"), (2, "Février"), (3, "Mars"), (4, "Avril"),
            (5, "Mai"), (6, "Juin"), (7, "Juillet"), (8, "Août"),
            (9, "Septembre"), (10, "Octobre"), (11, "Novembre"), (12, "Décembre")
        ]
        selected_month = st.selectbox(
            "Mois",
            months,
            format_func=lambda x: x[1],
            index=datetime.now().month - 1
        )[0]
    
    # Charger les données pour le mois sélectionné
    transactions_df = data_manager.load_transactions()
    employees_df = data_manager.load_employees()
    shareholders_df = data_manager.load_shareholders()
    
    if not transactions_df.empty:
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        monthly_transactions = transactions_df[
            (transactions_df['date'].dt.year == selected_year) & 
            (transactions_df['date'].dt.month == selected_month)
        ]
        
        st.subheader(f"📊 Rapport pour {months[selected_month-1][1]} {selected_year}")
        
        if not monthly_transactions.empty:
            # Résumé financier
            total_income = monthly_transactions[monthly_transactions['type'] == 'Entrée']['montant'].sum()
            total_expenses = monthly_transactions[monthly_transactions['type'] == 'Sortie']['montant'].sum()
            net_result = total_income - total_expenses
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💵 Total Entrées", f"{total_income:,.2f} €")
            
            with col2:
                st.metric("💸 Total Sorties", f"{total_expenses:,.2f} €")
            
            with col3:
                st.metric("💰 Résultat Net", f"{net_result:,.2f} €", 
                         delta=f"{net_result:+,.2f} €")
            
            # Détail des transactions par catégorie
            st.subheader("📋 Détail par Catégorie")
            
            # Grouper par catégorie et type
            category_summary = monthly_transactions.groupby(['type', 'categorie'])['montant'].agg(['sum', 'count']).reset_index()
            category_summary.columns = ['Type', 'Catégorie', 'Total', 'Nombre']
            
            # Séparer entrées et sorties
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**💵 Entrées par Catégorie**")
                income_categories = category_summary[category_summary['Type'] == 'Entrée']
                if not income_categories.empty:
                    income_categories['Total'] = income_categories['Total'].apply(lambda x: f"{x:,.2f} €")
                    st.dataframe(
                        income_categories[['Catégorie', 'Total', 'Nombre']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Aucune entrée catégorisée")
            
            with col2:
                st.write("**💸 Sorties par Catégorie**")
                expense_categories = category_summary[category_summary['Type'] == 'Sortie']
                if not expense_categories.empty:
                    expense_categories['Total'] = expense_categories['Total'].apply(lambda x: f"{x:,.2f} €")
                    st.dataframe(
                        expense_categories[['Catégorie', 'Total', 'Nombre']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Aucune sortie catégorisée")
            
            # Analyse des salaires
            if not employees_df.empty:
                st.subheader("👥 Analyse des Salaires")
                
                active_employees = employees_df[employees_df['actif'] == True]
                salary_data = []
                
                for _, employee in active_employees.iterrows():
                    # Calculer les paiements effectués ce mois
                    employee_payments = monthly_transactions[
                        monthly_transactions['description'].str.contains(f"Salaire - {employee['nom']}", na=False)
                    ]['montant'].sum()
                    
                    remaining = employee['salaire_mensuel'] - employee_payments
                    
                    salary_data.append({
                        'Employé': f"{employee['prenom']} {employee['nom']}",
                        'Salaire Dû': employee['salaire_mensuel'],
                        'Payé': employee_payments,
                        'Reste': max(0, remaining),
                        'Statut': '✅ Payé' if remaining <= 0 else '⏰ En attente'
                    })
                
                salary_df = pd.DataFrame(salary_data)
                
                # Formatage pour l'affichage
                display_salary_df = salary_df.copy()
                for col in ['Salaire Dû', 'Payé', 'Reste']:
                    display_salary_df[col] = display_salary_df[col].apply(lambda x: f"{x:,.2f} €")
                
                st.dataframe(display_salary_df, use_container_width=True, hide_index=True)
                
                # Statistiques salaires
                total_due = salary_df['Salaire Dû'].sum()
                total_paid = salary_df['Payé'].sum()
                total_remaining = salary_df['Reste'].sum()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("💰 Total Salaires Dus", f"{total_due:,.2f} €")
                with col2:
                    st.metric("✅ Total Payé", f"{total_paid:,.2f} €")
                with col3:
                    st.metric("⏰ Reste à Payer", f"{total_remaining:,.2f} €")
            
            # Graphique des transactions quotidiennes
            st.subheader("📈 Évolution Quotidienne")
            
            daily_summary = monthly_transactions.groupby([
                monthly_transactions['date'].dt.date, 'type'
            ])['montant'].sum().reset_index()
            
            fig = px.bar(daily_summary, 
                        x='date', 
                        y='montant', 
                        color='type',
                        title=f'Transactions Quotidiennes - {months[selected_month-1][1]} {selected_year}',
                        barmode='group')
            fig.update_layout(xaxis_title="Date", yaxis_title="Montant (€)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Bouton de téléchargement du rapport
            st.markdown("---")
            if st.button("📥 Télécharger le Rapport Mensuel Excel", use_container_width=True):
                try:
                    excel_data = excel_exporter.generate_monthly_report(selected_year, selected_month)
                    
                    st.download_button(
                        label="💾 Télécharger le fichier Excel",
                        data=excel_data,
                        file_name=f"rapport_mensuel_{selected_month:02d}_{selected_year}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("✅ Rapport généré avec succès!")
                
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération du rapport: {str(e)}")
        else:
            st.info(f"🔍 Aucune transaction pour {months[selected_month-1][1]} {selected_year}")
    else:
        st.info("📝 Aucune transaction disponible.")

with tab3:
    st.header("Analyses avancées")
    
    transactions_df = data_manager.load_transactions()
    
    if not transactions_df.empty:
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        
        # Sélection de la période d'analyse
        col1, col2 = st.columns(2)
        
        with col1:
            start_analysis_date = st.date_input(
                "Date de début",
                value=date.today() - timedelta(days=365),
                max_value=date.today()
            )
        
        with col2:
            end_analysis_date = st.date_input(
                "Date de fin",
                value=date.today(),
                max_value=date.today()
            )
        
        # Filtrer les données
        analysis_transactions = transactions_df[
            (transactions_df['date'].dt.date >= start_analysis_date) &
            (transactions_df['date'].dt.date <= end_analysis_date)
        ]
        
        if not analysis_transactions.empty:
            st.subheader("📊 Analyses Comparatives")
            
            # Analyse par mois
            monthly_analysis = analysis_transactions.groupby([
                analysis_transactions['date'].dt.to_period('M'), 'type'
            ])['montant'].sum().unstack(fill_value=0)
            
            monthly_analysis['Net'] = monthly_analysis.get('Entrée', 0) - monthly_analysis.get('Sortie', 0)
            monthly_analysis.index = monthly_analysis.index.astype(str)
            
            # Graphique de comparaison mensuelle
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=['Entrées vs Sorties par Mois', 'Résultat Net par Mois'],
                vertical_spacing=0.1
            )
            
            if 'Entrée' in monthly_analysis.columns:
                fig.add_trace(
                    go.Bar(name='Entrées', x=monthly_analysis.index, y=monthly_analysis['Entrée']),
                    row=1, col=1
                )
            
            if 'Sortie' in monthly_analysis.columns:
                fig.add_trace(
                    go.Bar(name='Sorties', x=monthly_analysis.index, y=monthly_analysis['Sortie']),
                    row=1, col=1
                )
            
            fig.add_trace(
                go.Scatter(name='Net', x=monthly_analysis.index, y=monthly_analysis['Net'], 
                          mode='lines+markers', line=dict(color='green')),
                row=2, col=1
            )
            
            fig.update_layout(height=600, title_text="Analyse Financière Comparative")
            fig.update_xaxes(title_text="Mois", row=2, col=1)
            fig.update_yaxes(title_text="Montant (€)", row=1, col=1)
            fig.update_yaxes(title_text="Résultat Net (€)", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistiques détaillées
            st.subheader("📈 Statistiques Détaillées")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_income = analysis_transactions[analysis_transactions['type'] == 'Entrée']['montant'].sum()
            total_expenses = analysis_transactions[analysis_transactions['type'] == 'Sortie']['montant'].sum()
            avg_monthly_income = monthly_analysis.get('Entrée', pd.Series([0])).mean()
            avg_monthly_expenses = monthly_analysis.get('Sortie', pd.Series([0])).mean()
            
            with col1:
                st.metric("💵 Total Entrées", f"{total_income:,.2f} €")
            
            with col2:
                st.metric("💸 Total Sorties", f"{total_expenses:,.2f} €")
            
            with col3:
                st.metric("📈 Moy. Entrées/Mois", f"{avg_monthly_income:,.2f} €")
            
            with col4:
                st.metric("📉 Moy. Sorties/Mois", f"{avg_monthly_expenses:,.2f} €")
            
            # Analyse des catégories
            st.subheader("🏷️ Analyse par Catégorie")
            
            category_analysis = analysis_transactions[
                analysis_transactions['categorie'].notna()
            ].groupby(['categorie', 'type'])['montant'].sum().unstack(fill_value=0)
            
            if not category_analysis.empty:
                # Graphique des catégories
                fig = px.bar(
                    category_analysis.reset_index(), 
                    x='categorie', 
                    y=['Entrée', 'Sortie'] if 'Sortie' in category_analysis.columns else ['Entrée'],
                    title='Montants par Catégorie',
                    barmode='group'
                )
                fig.update_layout(xaxis_title="Catégorie", yaxis_title="Montant (€)")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Tableau détaillé des catégories
                display_category_df = category_analysis.copy()
                if 'Entrée' in display_category_df.columns:
                    display_category_df['Entrée'] = display_category_df['Entrée'].apply(lambda x: f"{x:,.2f} €")
                if 'Sortie' in display_category_df.columns:
                    display_category_df['Sortie'] = display_category_df['Sortie'].apply(lambda x: f"{x:,.2f} €")
                
                st.dataframe(display_category_df, use_container_width=True)
            
            # Analyse des tendances
            st.subheader("📊 Indicateurs de Performance")
            
            # Calculer les tendances
            recent_months = monthly_analysis.tail(3)
            older_months = monthly_analysis.head(-3).tail(3) if len(monthly_analysis) > 3 else monthly_analysis.head(3)
            
            if len(recent_months) > 0 and len(older_months) > 0:
                recent_avg_income = recent_months.get('Entrée', pd.Series([0])).mean()
                older_avg_income = older_months.get('Entrée', pd.Series([0])).mean()
                income_trend = ((recent_avg_income - older_avg_income) / older_avg_income * 100) if older_avg_income > 0 else 0
                
                recent_avg_expenses = recent_months.get('Sortie', pd.Series([0])).mean()
                older_avg_expenses = older_months.get('Sortie', pd.Series([0])).mean()
                expense_trend = ((recent_avg_expenses - older_avg_expenses) / older_avg_expenses * 100) if older_avg_expenses > 0 else 0
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "📈 Tendance Entrées (3 derniers mois)",
                        f"{recent_avg_income:,.2f} €",
                        delta=f"{income_trend:+.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "📉 Tendance Sorties (3 derniers mois)",
                        f"{recent_avg_expenses:,.2f} €",
                        delta=f"{expense_trend:+.1f}%",
                        delta_color="inverse"
                    )
        else:
            st.info("🔍 Aucune transaction pour la période sélectionnée.")
    else:
        st.info("📝 Aucune donnée disponible pour l'analyse.")

with tab4:
    st.header("Exports et téléchargements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Export Données Complètes")
        
        st.write("Téléchargez toutes vos données dans un fichier Excel complet avec plusieurs feuilles:")
        st.write("• Toutes les transactions")
        st.write("• Tous les employés")
        st.write("• Tous les actionnaires")
        
        if st.button("📊 Générer Export Complet", use_container_width=True):
            try:
                excel_data = excel_exporter.export_all_data()
                
                st.download_button(
                    label="💾 Télécharger Export Complet",
                    data=excel_data,
                    file_name=f"habila_ghost_export_complet_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("✅ Export complet généré avec succès!")
            
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
    
    with col2:
        st.subheader("📋 Export Rapports Mensuels")
        
        # Sélection du mois pour export
        col_year, col_month = st.columns(2)
        
        with col_year:
            export_year = st.selectbox(
                "Année",
                [datetime.now().year - 1, datetime.now().year, datetime.now().year + 1],
                index=1,
                key="export_year"
            )
        
        with col_month:
            export_month = st.selectbox(
                "Mois",
                [(i, f"{i:02d} - {['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'][i-1]}") for i in range(1, 13)],
                format_func=lambda x: x[1],
                index=datetime.now().month - 1,
                key="export_month"
            )[0]
        
        if st.button("📊 Générer Rapport Mensuel", use_container_width=True):
            try:
                excel_data = excel_exporter.generate_monthly_report(export_year, export_month)
                
                month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                              'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
                
                st.download_button(
                    label=f"💾 Télécharger Rapport {month_names[export_month-1]} {export_year}",
                    data=excel_data,
                    file_name=f"rapport_mensuel_{export_month:02d}_{export_year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("✅ Rapport mensuel généré avec succès!")
            
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
    
    # Section d'exports par format
    st.markdown("---")
    st.subheader("📄 Exports par Format")
    
    # Charger les données pour les exports
    transactions_df = data_manager.load_transactions()
    employees_df = data_manager.load_employees()
    shareholders_df = data_manager.load_shareholders()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**💳 Transactions CSV**")
        if not transactions_df.empty:
            csv_transactions = transactions_df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Télécharger Transactions.csv",
                data=csv_transactions,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucune transaction à exporter")
    
    with col2:
        st.write("**👥 Employés CSV**")
        if not employees_df.empty:
            csv_employees = employees_df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Télécharger Employés.csv",
                data=csv_employees,
                file_name=f"employes_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucun employé à exporter")
    
    with col3:
        st.write("**📈 Actionnaires CSV**")
        if not shareholders_df.empty:
            csv_shareholders = shareholders_df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Télécharger Actionnaires.csv",
                data=csv_shareholders,
                file_name=f"actionnaires_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucun actionnaire à exporter")
    
    # Informations sur les exports
    st.markdown("---")
    st.subheader("ℹ️ Informations sur les Exports")
    
    st.info("""
    **Formats disponibles:**
    
    📊 **Excel (.xlsx)** - Recommandé pour les rapports complets avec formatage et graphiques
    
    📄 **CSV (.csv)** - Compatible avec tous les tableurs, idéal pour l'import/export de données
    
    **Contenu des rapports mensuels:**
    - Résumé financier du mois
    - Liste détaillée des transactions
    - État des salaires et paiements
    - Calculs de partage des bénéfices
    - Graphiques et analyses visuelles
    """)
    
    # Statistiques sur les données
    st.markdown("---")
    st.subheader("📊 Aperçu des Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💳 Transactions", len(transactions_df) if not transactions_df.empty else 0)
    
    with col2:
        st.metric("👥 Employés", len(employees_df) if not employees_df.empty else 0)
    
    with col3:
        st.metric("📈 Actionnaires", len(shareholders_df) if not shareholders_df.empty else 0)
    
    # Dernière mise à jour
    if not transactions_df.empty:
        last_transaction_date = pd.to_datetime(transactions_df['date']).max()
        st.write(f"**Dernière transaction:** {last_transaction_date.strftime('%d/%m/%Y')}")
    else:
        st.write("**Dernière transaction:** Aucune transaction enregistrée")

