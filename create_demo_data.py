#!/usr/bin/env python3
"""
Script pour créer des données de démonstration pour l'application Habila Ghosts
"""

import pandas as pd
import os
from datetime import date, datetime, timedelta
import uuid

def create_demo_data():
    """Créer des données de démonstration"""
    
    # Créer le répertoire data s'il n'existe pas
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Données de démonstration pour les transactions
    demo_transactions = [
        {
            'id': str(uuid.uuid4()),
            'date': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'type': 'Entrée',
            'montant': 50000.00,
            'description': 'Investissement initial - Capital de démarrage',
            'categorie': 'Capital'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (date.today() - timedelta(days=25)).strftime('%Y-%m-%d'),
            'type': 'Entrée',
            'montant': 25000.00,
            'description': 'Contrat client - Développement application mobile',
            'categorie': 'Revenus'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (date.today() - timedelta(days=20)).strftime('%Y-%m-%d'),
            'type': 'Sortie',
            'montant': 8000.00,
            'description': 'Achat équipement informatique',
            'categorie': 'Équipement'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (date.today() - timedelta(days=15)).strftime('%Y-%m-%d'),
            'type': 'Sortie',
            'montant': 12000.00,
            'description': 'Salaires équipe - Mois précédent',
            'categorie': 'Salaires'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'type': 'Entrée',
            'montant': 15000.00,
            'description': 'Paiement client - Services de consultation',
            'categorie': 'Revenus'
        },
        {
            'id': str(uuid.uuid4()),
            'date': (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'type': 'Sortie',
            'montant': 2500.00,
            'description': 'Frais de bureau et marketing',
            'categorie': 'Opérations'
        }
    ]
    
    # Données de démonstration pour les employés
    demo_employees = [
        {
            'id': str(uuid.uuid4()),
            'nom': 'Habila',
            'prenom': 'Tom',
            'poste': 'CEO & Développeur Principal',
            'salaire_mensuel': 5000.00,
            'date_embauche': (date.today() - timedelta(days=60)).strftime('%Y-%m-%d'),
            'actif': True
        },
        {
            'id': str(uuid.uuid4()),
            'nom': 'Martin',
            'prenom': 'Sophie',
            'poste': 'Designer UX/UI',
            'salaire_mensuel': 3500.00,
            'date_embauche': (date.today() - timedelta(days=45)).strftime('%Y-%m-%d'),
            'actif': True
        },
        {
            'id': str(uuid.uuid4()),
            'nom': 'Dubois',
            'prenom': 'Alexandre',
            'poste': 'Développeur Backend',
            'salaire_mensuel': 4000.00,
            'date_embauche': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
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
            'nom': 'Investor',
            'prenom': 'Angel',
            'parts_sociales': 25,
            'pourcentage_actions': 25.0,
            'email': 'angel.investor@venture.com',
            'telephone': '+33 6 98 76 54 32',
            'actif': True
        },
        {
            'id': str(uuid.uuid4()),
            'nom': 'Partner',
            'prenom': 'Business',
            'parts_sociales': 15,
            'pourcentage_actions': 15.0,
            'email': 'business.partner@company.com',
            'telephone': '+33 6 11 22 33 44',
            'actif': True
        }
    ]
    
    # Créer les DataFrames et sauvegarder
    transactions_df = pd.DataFrame(demo_transactions)
    employees_df = pd.DataFrame(demo_employees)
    shareholders_df = pd.DataFrame(demo_shareholders)
    
    # Sauvegarder les fichiers CSV
    transactions_df.to_csv("data/transactions.csv", index=False)
    employees_df.to_csv("data/employees.csv", index=False)
    shareholders_df.to_csv("data/shareholders.csv", index=False)
    
    print("✅ Données de démonstration créées avec succès!")
    print(f"📊 {len(demo_transactions)} transactions")
    print(f"👥 {len(demo_employees)} employés")
    print(f"🏛️ {len(demo_shareholders)} actionnaires")
    print(f"💰 Solde calculé: {sum(t['montant'] if t['type'] == 'Entrée' else -t['montant'] for t in demo_transactions):,.2f} $")

if __name__ == "__main__":
    create_demo_data()