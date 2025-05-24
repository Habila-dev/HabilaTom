import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.transaction import Transaction
from models.employee import Employee
from models.shareholder import Shareholder
import uuid
from datetime import date

class DatabaseManager:
    """Gestionnaire de base de données PostgreSQL pour l'application financière"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not found")
        
        self.engine = create_engine(self.database_url)
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Crée les tables nécessaires si elles n'existent pas"""
        
        create_tables_sql = """
        -- Table des transactions
        CREATE TABLE IF NOT EXISTS transactions (
            id VARCHAR(36) PRIMARY KEY,
            date DATE NOT NULL,
            type VARCHAR(10) NOT NULL CHECK (type IN ('Entrée', 'Sortie')),
            montant DECIMAL(12, 2) NOT NULL CHECK (montant > 0),
            description TEXT NOT NULL,
            categorie VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Table des employés
        CREATE TABLE IF NOT EXISTS employees (
            id VARCHAR(36) PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            prenom VARCHAR(100) NOT NULL,
            poste VARCHAR(100) NOT NULL,
            salaire_mensuel DECIMAL(10, 2) NOT NULL CHECK (salaire_mensuel > 0),
            date_embauche DATE NOT NULL,
            actif BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Table des actionnaires
        CREATE TABLE IF NOT EXISTS shareholders (
            id VARCHAR(36) PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            prenom VARCHAR(100) NOT NULL,
            parts_sociales INTEGER NOT NULL CHECK (parts_sociales > 0 AND parts_sociales <= 100),
            email VARCHAR(255),
            telephone VARCHAR(50),
            actif BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Index pour améliorer les performances
        CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
        CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
        CREATE INDEX IF NOT EXISTS idx_employees_actif ON employees(actif);
        CREATE INDEX IF NOT EXISTS idx_shareholders_actif ON shareholders(actif);
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_tables_sql))
                conn.commit()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la création des tables: {e}")
            raise
    
    # Gestion des transactions
    def load_transactions(self) -> pd.DataFrame:
        """Charge toutes les transactions depuis la base de données"""
        try:
            query = """
            SELECT id, date, type, montant, description, categorie
            FROM transactions
            ORDER BY date DESC
            """
            return pd.read_sql(query, self.engine)
        except SQLAlchemyError as e:
            print(f"Erreur lors du chargement des transactions: {e}")
            return pd.DataFrame(columns=['id', 'date', 'type', 'montant', 'description', 'categorie'])
    
    def save_transaction(self, transaction: Transaction) -> bool:
        """Sauvegarde une nouvelle transaction dans la base de données"""
        try:
            query = """
            INSERT INTO transactions (id, date, type, montant, description, categorie)
            VALUES (%(id)s, %(date)s, %(type)s, %(montant)s, %(description)s, %(categorie)s)
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(query), {
                    'id': transaction.id,
                    'date': transaction.date,
                    'type': transaction.type,
                    'montant': transaction.montant,
                    'description': transaction.description,
                    'categorie': transaction.categorie
                })
                conn.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Erreur lors de la sauvegarde de la transaction: {e}")
            return False
    
    def update_transaction(self, transaction_id: str, updated_transaction: Transaction) -> bool:
        """Met à jour une transaction existante"""
        try:
            query = """
            UPDATE transactions 
            SET date = %(date)s, type = %(type)s, montant = %(montant)s, 
                description = %(description)s, categorie = %(categorie)s
            WHERE id = %(id)s
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {
                    'id': transaction_id,
                    'date': updated_transaction.date,
                    'type': updated_transaction.type,
                    'montant': updated_transaction.montant,
                    'description': updated_transaction.description,
                    'categorie': updated_transaction.categorie
                })
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Erreur lors de la mise à jour de la transaction: {e}")
            return False
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Supprime une transaction"""
        try:
            query = "DELETE FROM transactions WHERE id = %(id)s"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'id': transaction_id})
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Erreur lors de la suppression de la transaction: {e}")
            return False
    
    # Gestion des employés
    def load_employees(self) -> pd.DataFrame:
        """Charge tous les employés depuis la base de données"""
        try:
            query = """
            SELECT id, nom, prenom, poste, salaire_mensuel, date_embauche, actif
            FROM employees
            ORDER BY nom, prenom
            """
            return pd.read_sql(query, self.engine)
        except SQLAlchemyError as e:
            print(f"Erreur lors du chargement des employés: {e}")
            return pd.DataFrame(columns=['id', 'nom', 'prenom', 'poste', 'salaire_mensuel', 'date_embauche', 'actif'])
    
    def save_employee(self, employee: Employee) -> bool:
        """Sauvegarde un nouvel employé dans la base de données"""
        try:
            query = """
            INSERT INTO employees (id, nom, prenom, poste, salaire_mensuel, date_embauche, actif)
            VALUES (%(id)s, %(nom)s, %(prenom)s, %(poste)s, %(salaire_mensuel)s, %(date_embauche)s, %(actif)s)
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(query), {
                    'id': employee.id,
                    'nom': employee.nom,
                    'prenom': employee.prenom,
                    'poste': employee.poste,
                    'salaire_mensuel': employee.salaire_mensuel,
                    'date_embauche': employee.date_embauche,
                    'actif': employee.actif
                })
                conn.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Erreur lors de la sauvegarde de l'employé: {e}")
            return False
    
    def update_employee(self, employee_id: str, updated_employee: Employee) -> bool:
        """Met à jour un employé existant"""
        try:
            query = """
            UPDATE employees 
            SET nom = %(nom)s, prenom = %(prenom)s, poste = %(poste)s, 
                salaire_mensuel = %(salaire_mensuel)s, date_embauche = %(date_embauche)s, actif = %(actif)s
            WHERE id = %(id)s
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {
                    'id': employee_id,
                    'nom': updated_employee.nom,
                    'prenom': updated_employee.prenom,
                    'poste': updated_employee.poste,
                    'salaire_mensuel': updated_employee.salaire_mensuel,
                    'date_embauche': updated_employee.date_embauche,
                    'actif': updated_employee.actif
                })
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Erreur lors de la mise à jour de l'employé: {e}")
            return False
    
    def delete_employee(self, employee_id: str) -> bool:
        """Supprime un employé (le marque comme inactif)"""
        try:
            query = "UPDATE employees SET actif = FALSE WHERE id = %(id)s"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'id': employee_id})
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Erreur lors de la suppression de l'employé: {e}")
            return False
    
    # Gestion des actionnaires
    def load_shareholders(self) -> pd.DataFrame:
        """Charge tous les actionnaires depuis la base de données"""
        try:
            query = """
            SELECT id, nom, prenom, parts_sociales, email, telephone, actif,
                   parts_sociales as pourcentage_actions
            FROM shareholders
            ORDER BY nom, prenom
            """
            return pd.read_sql(query, self.engine)
        except SQLAlchemyError as e:
            print(f"Erreur lors du chargement des actionnaires: {e}")
            return pd.DataFrame(columns=['id', 'nom', 'prenom', 'parts_sociales', 'pourcentage_actions', 'email', 'telephone', 'actif'])
    
    def save_shareholder(self, shareholder: Shareholder) -> bool:
        """Sauvegarde un nouvel actionnaire dans la base de données"""
        try:
            query = """
            INSERT INTO shareholders (id, nom, prenom, parts_sociales, email, telephone, actif)
            VALUES (%(id)s, %(nom)s, %(prenom)s, %(parts_sociales)s, %(email)s, %(telephone)s, %(actif)s)
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(query), {
                    'id': shareholder.id,
                    'nom': shareholder.nom,
                    'prenom': shareholder.prenom,
                    'parts_sociales': shareholder.parts_sociales,
                    'email': shareholder.email,
                    'telephone': shareholder.telephone,
                    'actif': shareholder.actif
                })
                conn.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Erreur lors de la sauvegarde de l'actionnaire: {e}")
            return False
    
    def update_shareholder(self, shareholder_id: str, updated_shareholder: Shareholder) -> bool:
        """Met à jour un actionnaire existant"""
        try:
            query = """
            UPDATE shareholders 
            SET nom = %(nom)s, prenom = %(prenom)s, parts_sociales = %(parts_sociales)s,
                email = %(email)s, telephone = %(telephone)s, actif = %(actif)s
            WHERE id = %(id)s
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {
                    'id': shareholder_id,
                    'nom': updated_shareholder.nom,
                    'prenom': updated_shareholder.prenom,
                    'parts_sociales': updated_shareholder.parts_sociales,
                    'email': updated_shareholder.email,
                    'telephone': updated_shareholder.telephone,
                    'actif': updated_shareholder.actif
                })
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Erreur lors de la mise à jour de l'actionnaire: {e}")
            return False
    
    def delete_shareholder(self, shareholder_id: str) -> bool:
        """Supprime un actionnaire (le marque comme inactif)"""
        try:
            query = "UPDATE shareholders SET actif = FALSE WHERE id = %(id)s"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'id': shareholder_id})
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Erreur lors de la suppression de l'actionnaire: {e}")
            return False
    
    # Méthodes utilitaires
    def generate_id(self) -> str:
        """Génère un ID unique"""
        return str(uuid.uuid4())
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Récupère une transaction par son ID"""
        try:
            query = "SELECT * FROM transactions WHERE id = %(id)s"
            df = pd.read_sql(query, self.engine, params={'id': transaction_id})
            
            if not df.empty:
                row = df.iloc[0]
                return Transaction.from_dict(row.to_dict())
            return None
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération de la transaction: {e}")
            return None
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Récupère un employé par son ID"""
        try:
            query = "SELECT * FROM employees WHERE id = %(id)s"
            df = pd.read_sql(query, self.engine, params={'id': employee_id})
            
            if not df.empty:
                row = df.iloc[0]
                return Employee.from_dict(row.to_dict())
            return None
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération de l'employé: {e}")
            return None
    
    def get_shareholder_by_id(self, shareholder_id: str) -> Optional[Shareholder]:
        """Récupère un actionnaire par son ID"""
        try:
            query = "SELECT * FROM shareholders WHERE id = %(id)s"
            df = pd.read_sql(query, self.engine, params={'id': shareholder_id})
            
            if not df.empty:
                row = df.iloc[0]
                return Shareholder.from_dict(row.to_dict())
            return None
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération de l'actionnaire: {e}")
            return None
    
    def get_database_stats(self) -> dict:
        """Retourne des statistiques sur la base de données"""
        try:
            stats = {}
            
            with self.engine.connect() as conn:
                # Nombre de transactions
                result = conn.execute(text("SELECT COUNT(*) as count FROM transactions"))
                stats['transactions_count'] = result.fetchone()[0]
                
                # Nombre d'employés actifs
                result = conn.execute(text("SELECT COUNT(*) as count FROM employees WHERE actif = TRUE"))
                stats['active_employees_count'] = result.fetchone()[0]
                
                # Nombre d'actionnaires actifs
                result = conn.execute(text("SELECT COUNT(*) as count FROM shareholders WHERE actif = TRUE"))
                stats['active_shareholders_count'] = result.fetchone()[0]
                
                # Solde total
                result = conn.execute(text("""
                    SELECT 
                        COALESCE(SUM(CASE WHEN type = 'Entrée' THEN montant ELSE -montant END), 0) as solde
                    FROM transactions
                """))
                stats['total_balance'] = float(result.fetchone()[0])
            
            return stats
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return {}