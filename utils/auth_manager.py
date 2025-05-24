import streamlit_authenticator as stauth
import yaml
import os
from typing import Dict, List, Optional
import bcrypt
from datetime import datetime
from sqlalchemy import text
from utils.database_manager import DatabaseManager

class AuthManager:
    """Gestionnaire d'authentification pour l'application Habila Ghost"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.config_file = "config/auth_config.yaml"
        self._initialize_auth_system()
    
    def _initialize_auth_system(self):
        """Initialise le système d'authentification"""
        # Créer le dossier config s'il n'existe pas
        os.makedirs("config", exist_ok=True)
        
        # Créer la table des utilisateurs si elle n'existe pas
        self._create_users_table()
        
        # Créer le fichier de configuration par défaut s'il n'existe pas
        if not os.path.exists(self.config_file):
            self._create_default_config()
    
    def _create_users_table(self):
        """Crée la table des utilisateurs dans la base de données"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255),
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            created_by VARCHAR(36)
        );
        
        -- Index pour améliorer les performances
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);
        """
        
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
                
                # Créer l'utilisateur administrateur par défaut s'il n'existe pas
                self._create_default_admin()
        except Exception as e:
            print(f"Erreur lors de la création de la table users: {e}")
    
    def _create_default_admin(self):
        """Crée l'utilisateur administrateur par défaut"""
        try:
            with self.db_manager.engine.connect() as conn:
                # Vérifier si l'admin existe déjà
                check_admin = """
                SELECT COUNT(*) as count FROM users WHERE username = 'admin'
                """
                result = conn.execute(text(check_admin)).fetchone()
                
                if result[0] == 0:
                    # Créer l'administrateur par défaut
                    admin_password = "habila2025!"  # Mot de passe par défaut
                    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    insert_admin = """
                    INSERT INTO users (id, username, name, email, password_hash, role, active)
                    VALUES (%(id)s, %(username)s, %(name)s, %(email)s, %(password_hash)s, %(role)s, %(active)s)
                    """
                    
                    conn.execute(text(insert_admin), {
                        'id': self.db_manager.generate_id(),
                        'username': 'admin',
                        'name': 'Administrateur Habila Ghost',
                        'email': 'admin@habilaghost.com',
                        'password_hash': hashed_password,
                        'role': 'admin',
                        'active': True
                    })
                    conn.commit()
                    print("✅ Utilisateur administrateur créé: admin / habila2025!")
        except Exception as e:
            print(f"Erreur lors de la création de l'admin: {e}")
    
    def _create_default_config(self):
        """Crée le fichier de configuration par défaut"""
        config = {
            'credentials': {
                'usernames': {}
            },
            'cookie': {
                'name': 'habila_ghost_auth',
                'key': 'habila_ghost_secret_key_2025',
                'expiry_days': 30
            },
            'preauthorized': {
                'emails': []
            }
        }
        
        with open(self.config_file, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
    
    def load_config(self) -> Dict:
        """Charge la configuration d'authentification depuis la base de données"""
        try:
            with self.db_manager.engine.connect() as conn:
                query = """
                SELECT username, name, email, password_hash, role
                FROM users 
                WHERE active = TRUE
                """
                result = conn.execute(self.db_manager.text(query)).fetchall()
                
                config = {
                    'credentials': {
                        'usernames': {}
                    },
                    'cookie': {
                        'name': 'habila_ghost_auth',
                        'key': 'habila_ghost_secret_key_2025',
                        'expiry_days': 30
                    },
                    'preauthorized': {
                        'emails': []
                    }
                }
                
                for row in result:
                    username, name, email, password_hash, role = row
                    config['credentials']['usernames'][username] = {
                        'name': name,
                        'password': password_hash,
                        'email': email,
                        'role': role
                    }
                
                return config
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict:
        """Configuration de fallback en cas d'erreur"""
        return {
            'credentials': {
                'usernames': {
                    'admin': {
                        'name': 'Administrateur Habila Ghost',
                        'password': bcrypt.hashpw('habila2025!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                        'email': 'admin@habilaghost.com',
                        'role': 'admin'
                    }
                }
            },
            'cookie': {
                'name': 'habila_ghost_auth',
                'key': 'habila_ghost_secret_key_2025',
                'expiry_days': 30
            },
            'preauthorized': {
                'emails': []
            }
        }
    
    def create_user(self, username: str, name: str, email: str, password: str, role: str = 'user', created_by: str = None) -> bool:
        """Crée un nouveau utilisateur"""
        try:
            # Hasher le mot de passe
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            with self.db_manager.engine.connect() as conn:
                insert_query = """
                INSERT INTO users (id, username, name, email, password_hash, role, active, created_by)
                VALUES (%(id)s, %(username)s, %(name)s, %(email)s, %(password_hash)s, %(role)s, %(active)s, %(created_by)s)
                """
                
                conn.execute(text(insert_query), {
                    'id': self.db_manager.generate_id(),
                    'username': username,
                    'name': name,
                    'email': email,
                    'password_hash': hashed_password,
                    'role': role,
                    'active': True,
                    'created_by': created_by
                })
                conn.commit()
                return True
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur: {e}")
            return False
    
    def update_user(self, username: str, name: str = None, email: str = None, role: str = None, active: bool = None) -> bool:
        """Met à jour un utilisateur existant"""
        try:
            with self.db_manager.engine.connect() as conn:
                updates = []
                params = {'username': username}
                
                if name is not None:
                    updates.append("name = %(name)s")
                    params['name'] = name
                
                if email is not None:
                    updates.append("email = %(email)s")
                    params['email'] = email
                
                if role is not None:
                    updates.append("role = %(role)s")
                    params['role'] = role
                
                if active is not None:
                    updates.append("active = %(active)s")
                    params['active'] = active
                
                if updates:
                    query = f"UPDATE users SET {', '.join(updates)} WHERE username = %(username)s"
                    result = conn.execute(text(query), params)
                    conn.commit()
                    return result.rowcount > 0
                
                return False
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'utilisateur: {e}")
            return False
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change le mot de passe d'un utilisateur"""
        try:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            with self.db_manager.engine.connect() as conn:
                query = "UPDATE users SET password_hash = %(password_hash)s WHERE username = %(username)s"
                result = conn.execute(self.db_manager.text(query), {
                    'password_hash': hashed_password,
                    'username': username
                })
                conn.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Erreur lors du changement de mot de passe: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Récupère tous les utilisateurs"""
        try:
            with self.db_manager.engine.connect() as conn:
                query = """
                SELECT id, username, name, email, role, active, created_at, last_login
                FROM users
                ORDER BY created_at DESC
                """
                result = conn.execute(self.db_manager.text(query)).fetchall()
                
                users = []
                for row in result:
                    users.append({
                        'id': row[0],
                        'username': row[1],
                        'name': row[2],
                        'email': row[3],
                        'role': row[4],
                        'active': row[5],
                        'created_at': row[6],
                        'last_login': row[7]
                    })
                
                return users
        except Exception as e:
            print(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []
    
    def update_last_login(self, username: str):
        """Met à jour la date de dernière connexion"""
        try:
            with self.db_manager.engine.connect() as conn:
                query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = %(username)s"
                conn.execute(self.db_manager.text(query), {'username': username})
                conn.commit()
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la dernière connexion: {e}")
    
    def get_authenticator(self):
        """Retourne l'authenticator configuré"""
        config = self.load_config()
        return stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
    
    def has_permission(self, username: str, required_role: str) -> bool:
        """Vérifie si un utilisateur a les permissions requises"""
        role_hierarchy = {'viewer': 1, 'user': 2, 'admin': 3}
        
        try:
            with self.db_manager.engine.connect() as conn:
                query = "SELECT role FROM users WHERE username = %(username)s AND active = TRUE"
                result = conn.execute(self.db_manager.text(query), {'username': username}).fetchone()
                
                if result:
                    user_role = result[0]
                    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
                
                return False
        except Exception as e:
            print(f"Erreur lors de la vérification des permissions: {e}")
            return False