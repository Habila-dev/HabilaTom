import pandas as pd
import os
from typing import List, Optional
import uuid
from datetime import date
from models.transaction import Transaction
from models.employee import Employee
from models.shareholder import Shareholder

class DataManager:
    """Gestionnaire de données pour l'application financière"""
    
    def __init__(self):
        self.data_dir = "data"
        self.transactions_file = os.path.join(self.data_dir, "transactions.csv")
        self.employees_file = os.path.join(self.data_dir, "employees.csv")
        self.shareholders_file = os.path.join(self.data_dir, "shareholders.csv")
        
        # Créer le répertoire data s'il n'existe pas
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Initialiser les fichiers CSV s'ils n'existent pas
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialise les fichiers CSV avec les en-têtes appropriés"""
        
        # Transactions
        if not os.path.exists(self.transactions_file):
            df = pd.DataFrame(columns=['id', 'date', 'type', 'montant', 'description', 'categorie'])
            df.to_csv(self.transactions_file, index=False)
        
        # Employés
        if not os.path.exists(self.employees_file):
            df = pd.DataFrame(columns=['id', 'nom', 'prenom', 'poste', 'salaire_mensuel', 'date_embauche', 'actif'])
            df.to_csv(self.employees_file, index=False)
        
        # Actionnaires
        if not os.path.exists(self.shareholders_file):
            df = pd.DataFrame(columns=['id', 'nom', 'prenom', 'parts_sociales', 'pourcentage_actions', 'email', 'telephone', 'actif'])
            df.to_csv(self.shareholders_file, index=False)
    
    # Gestion des transactions
    def load_transactions(self) -> pd.DataFrame:
        """Charge toutes les transactions"""
        try:
            return pd.read_csv(self.transactions_file)
        except Exception:
            return pd.DataFrame(columns=['id', 'date', 'type', 'montant', 'description', 'categorie'])
    
    def save_transaction(self, transaction: Transaction) -> bool:
        """Sauvegarde une nouvelle transaction"""
        try:
            df = self.load_transactions()
            new_row = pd.DataFrame([transaction.to_dict()])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(self.transactions_file, index=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la transaction: {e}")
            return False
    
    def update_transaction(self, transaction_id: str, updated_transaction: Transaction) -> bool:
        """Met à jour une transaction existante"""
        try:
            df = self.load_transactions()
            idx = df[df['id'] == transaction_id].index
            if len(idx) > 0:
                df.loc[idx[0]] = updated_transaction.to_dict()
                df.to_csv(self.transactions_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la transaction: {e}")
            return False
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Supprime une transaction"""
        try:
            df = self.load_transactions()
            df = df[df['id'] != transaction_id]
            df.to_csv(self.transactions_file, index=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de la transaction: {e}")
            return False
    
    # Gestion des employés
    def load_employees(self) -> pd.DataFrame:
        """Charge tous les employés"""
        try:
            return pd.read_csv(self.employees_file)
        except Exception:
            return pd.DataFrame(columns=['id', 'nom', 'prenom', 'poste', 'salaire_mensuel', 'date_embauche', 'actif'])
    
    def save_employee(self, employee: Employee) -> bool:
        """Sauvegarde un nouveau employé"""
        try:
            df = self.load_employees()
            new_row = pd.DataFrame([employee.to_dict()])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(self.employees_file, index=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'employé: {e}")
            return False
    
    def update_employee(self, employee_id: str, updated_employee: Employee) -> bool:
        """Met à jour un employé existant"""
        try:
            df = self.load_employees()
            idx = df[df['id'] == employee_id].index
            if len(idx) > 0:
                df.loc[idx[0]] = updated_employee.to_dict()
                df.to_csv(self.employees_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'employé: {e}")
            return False
    
    def delete_employee(self, employee_id: str) -> bool:
        """Supprime un employé"""
        try:
            df = self.load_employees()
            df = df[df['id'] != employee_id]
            df.to_csv(self.employees_file, index=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de l'employé: {e}")
            return False
    
    # Gestion des actionnaires
    def load_shareholders(self) -> pd.DataFrame:
        """Charge tous les actionnaires"""
        try:
            return pd.read_csv(self.shareholders_file)
        except Exception:
            return pd.DataFrame(columns=['id', 'nom', 'prenom', 'parts_sociales', 'pourcentage_actions', 'email', 'telephone', 'actif'])
    
    def save_shareholder(self, shareholder: Shareholder) -> bool:
        """Sauvegarde un nouveau actionnaire"""
        try:
            df = self.load_shareholders()
            new_row = pd.DataFrame([shareholder.to_dict()])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(self.shareholders_file, index=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'actionnaire: {e}")
            return False
    
    def update_shareholder(self, shareholder_id: str, updated_shareholder: Shareholder) -> bool:
        """Met à jour un actionnaire existant"""
        try:
            df = self.load_shareholders()
            idx = df[df['id'] == shareholder_id].index
            if len(idx) > 0:
                df.loc[idx[0]] = updated_shareholder.to_dict()
                df.to_csv(self.shareholders_file, index=False)
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'actionnaire: {e}")
            return False
    
    def delete_shareholder(self, shareholder_id: str) -> bool:
        """Supprime un actionnaire"""
        try:
            df = self.load_shareholders()
            df = df[df['id'] != shareholder_id]
            df.to_csv(self.shareholders_file, index=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de l'actionnaire: {e}")
            return False
    
    def generate_id(self) -> str:
        """Génère un ID unique"""
        return str(uuid.uuid4())
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Récupère une transaction par son ID"""
        df = self.load_transactions()
        transaction_data = df[df['id'] == transaction_id]
        if not transaction_data.empty:
            return Transaction.from_dict(transaction_data.iloc[0].to_dict())
        return None
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Récupère un employé par son ID"""
        df = self.load_employees()
        employee_data = df[df['id'] == employee_id]
        if not employee_data.empty:
            return Employee.from_dict(employee_data.iloc[0].to_dict())
        return None
    
    def get_shareholder_by_id(self, shareholder_id: str) -> Optional[Shareholder]:
        """Récupère un actionnaire par son ID"""
        df = self.load_shareholders()
        shareholder_data = df[df['id'] == shareholder_id]
        if not shareholder_data.empty:
            return Shareholder.from_dict(shareholder_data.iloc[0].to_dict())
        return None
