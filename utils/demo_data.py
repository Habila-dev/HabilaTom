"""
Utilitaire pour créer des données de démonstration
pour le déploiement sur Streamlit Cloud
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import uuid

def create_demo_data():
    """Crée des données de démonstration pour l'application"""
    
    # Créer le répertoire data s'il n'existe pas
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Données de démonstration pour les transactions
    demo_transactions = [
        {
            'id': str(uuid.uuid4()),
            'date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'type': 'Entrée',
            'montant': 50000.00,
            'description': 'Investissement initial - Capital de démarrage',
            'categorie': 'Investissement'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d'),
            'type': 'Entrée',
            'montant': 25000.00,
            'description': 'Revenus de services - Contrat client A',
            'categorie': 'Revenus'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'),
            'type': 'Sortie',
            'montant': 8000.00,
            'description': 'Salaires équipe - Mois 1',
            'categorie': 'Salaires'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
            'type': 'Sortie',
            'montant': 2500.00,
            'description': 'Frais de bureau et équipement',
            'categorie': 'Opérationnel'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'type': 'Entrée',
            'montant': 15000.00,
            'description': 'Revenus de services - Contrat client B',
            'categorie': 'Revenus'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'type': 'Sortie',
            'montant': 1200.00,
            'description': 'Marketing et publicité',
            'categorie': 'Marketing'
        }
    ]
    
    # Données de démonstration pour les employés
    demo_employees = [
        {
            'id': str(uuid.uuid4()),
            'nom': 'Habila',
            'prenom': 'Tom',
            'poste': 'Directeur Général',
            'salaire_mensuel': 4000.00,
            'date_embauche': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'actif': True
        },
        {
            'id': str(uuid.uuid4()),
            'nom': 'Dupont',
            'prenom': 'Marie',
            'poste': 'Développeuse Senior',
            'salaire_mensuel': 3500.00,
            'date_embauche': (datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d'),
            'actif': True
        },
        {
            'id': str(uuid.uuid4()),
            'nom': 'Martin',
            'prenom': 'Pierre',
            'poste': 'Designer UX/UI',
            'salaire_mensuel': 3000.00,
            'date_embauche': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'),
            'actif': True
        }
    ]
    
    # Données de démonstration pour les actionnaires
    demo_shareholders = [
        {
            'id': str(uuid.uuid4()),
            'nom': 'Habila',
            'prenom': 'Tom',
            'parts_sociales': 60,
            'pourcentage_actions': 60.0,
            'email': 'tom.habila@habilaghosts.com',
            'telephone': '+33 6 12 34 56 78',
            'actif': True
        },
        {
            'id': str(uuid.uuid4()),
            'nom': 'Investisseur',
            'prenom': 'Alpha',
            'parts_sociales': 25,
            'pourcentage_actions': 25.0,
            'email': 'alpha@investisseur.com',
            'telephone': '+33 6 98 76 54 32',
            'actif': True
        },
        {
            'id': str(uuid.uuid4()),
            'nom': 'Partenaire',
            'prenom': 'Beta',
            'parts_sociales': 15,
            'pourcentage_actions': 15.0,
            'email': 'beta@partenaire.com',
            'telephone': '+33 6 11 22 33 44',
            'actif': True
        }
    ]
    
    # Créer les fichiers CSV
    try:
        # Transactions
        df_transactions = pd.DataFrame(demo_transactions)
        df_transactions.to_csv("data/transactions.csv", index=False)
        
        # Employés
        df_employees = pd.DataFrame(demo_employees)
        df_employees.to_csv("data/employees.csv", index=False)
        
        # Actionnaires
        df_shareholders = pd.DataFrame(demo_shareholders)
        df_shareholders.to_csv("data/shareholders.csv", index=False)
        
        return True
    except Exception as e:
        print(f"Erreur lors de la création des données de démonstration: {e}")
        return False

def should_create_demo_data():
    """Vérifie si les données de démonstration doivent être créées"""
    # Vérifier si les fichiers existent et ne sont pas vides
    files_to_check = [
        "data/transactions.csv",
        "data/employees.csv", 
        "data/shareholders.csv"
    ]
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            return True
        
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return True
        except:
            return True
    
    return False