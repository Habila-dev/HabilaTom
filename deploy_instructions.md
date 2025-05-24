# 🚀 Instructions de Déploiement - Habila Ghost

## 📋 Structure de l'Application Optimisée

Votre application est maintenant prête pour le déploiement gratuit avec :
- ✅ Python 3.13
- ✅ Dépendances minimales (requirements.txt)
- ✅ Configuration Streamlit optimisée
- ✅ Fichiers de déploiement complets

## 🗂️ Fichiers Essentiels

```
habila-ghost-finance/
├── app.py                    # Application principale
├── requirements.txt          # Dépendances Python 3.13
├── runtime.txt              # Version Python
├── Procfile                 # Configuration Heroku
├── README.md                # Documentation
├── .gitignore              # Fichiers à ignorer
├── .streamlit/
│   └── config.toml         # Configuration Streamlit
├── pages/                   # Pages de l'application
├── models/                  # Modèles de données
├── utils/                   # Utilitaires
├── data/                    # Stockage local
└── config/                  # Configuration utilisateurs
```

## ☁️ Options de Déploiement Gratuit

### 1. **Streamlit Cloud** (Recommandé - 100% Gratuit)
- Connexion directe avec GitHub
- Déploiement automatique
- SSL gratuit
- Domaine personnalisé disponible

### 2. **Railway** (Généreux plan gratuit)
- Déploiement simple
- Base de données incluse si nécessaire
- SSL automatique

### 3. **Render** (Plan gratuit permanent)
- Déploiement depuis GitHub
- SSL automatique
- Veille automatique après inactivité

### 4. **Heroku** (Plan gratuit limité)
- Utilise le Procfile inclus
- Veille après 30 min d'inactivité

## 🎯 Étapes de Déploiement

### Pour Streamlit Cloud :
1. Créer un repository GitHub public
2. Uploader tous les fichiers
3. Aller sur share.streamlit.io
4. Connecter GitHub et sélectionner le repo
5. Déployer automatiquement !

### Identifiants par défaut :
- **Utilisateur** : `admin`
- **Mot de passe** : `habila2025`

## 🔧 Personnalisation Post-Déploiement

Après déploiement, vous pourrez :
- Changer le mot de passe admin
- Créer de nouveaux utilisateurs
- Ajouter des données de production
- Personnaliser les rapports

## 📞 Support

L'application est entièrement autonome et ne nécessite aucune configuration supplémentaire.