# 👻 Habila Ghost - Système de Gestion Financière

Application web sécurisée de gestion financière développée avec Streamlit pour le suivi complet des transactions, salaires et partage des bénéfices.

## 🚀 Fonctionnalités

- **Tableau de Bord** : Vue d'ensemble des finances avec graphiques interactifs
- **Gestion des Transactions** : Suivi des entrées et sorties de fonds
- **Gestion des Salaires** : Calcul et suivi des paiements des employés
- **Gestion des Actionnaires** : Répartition du capital (150 000 $ / 100 parts)
- **Rapports** : Export Excel des données financières
- **Administration** : Gestion sécurisée des utilisateurs

## 🔐 Système d'Authentification

- Connexion multi-utilisateurs avec rôles différenciés
- Sessions persistantes
- Accès restreint aux sections sensibles (Administrateurs uniquement)

### Compte par défaut
- **Utilisateur** : `admin`
- **Mot de passe** : `habila2025`

## 📊 Architecture

- **Frontend** : Streamlit
- **Stockage** : Fichiers JSON/CSV locaux
- **Visualisation** : Plotly
- **Export** : OpenPyXL

## 🔧 Installation Locale

```bash
# Cloner le repository
git clone [votre-repo]

# Installer les dépendances
pip install streamlit pandas plotly openpyxl streamlit-authenticator

# Lancer l'application
streamlit run app.py
```

## ☁️ Déploiement

Cette application est optimisée pour le déploiement gratuit sur :
- **Streamlit Cloud** (recommandé)
- **Heroku**
- **Railway**
- **Render**

### Déploiement sur Streamlit Cloud

1. Fork ce repository sur GitHub
2. Connectez-vous sur [share.streamlit.io](https://share.streamlit.io)
3. Déployez directement depuis votre repository

## 📁 Structure du Projet

```
├── app.py                 # Application principale
├── pages/                 # Pages Streamlit
│   ├── 1_Transactions.py
│   ├── 2_Salaires.py
│   ├── 3_Actionnaires.py
│   ├── 4_Rapports.py
│   └── 5_Administration.py
├── models/                # Modèles de données
├── utils/                 # Utilitaires
├── data/                  # Stockage des données
├── config/                # Configuration utilisateurs
└── .streamlit/           # Configuration Streamlit
```

## 💰 Système Financier

- **Capital Total** : 150 000 $
- **Parts Sociales** : 100 parts
- **Devise** : Dollar américain ($)
- **Calcul automatique** des pourcentages de répartition

## 🛡️ Sécurité

- Authentification obligatoire
- Contrôle d'accès par rôles
- Sessions sécurisées
- Données chiffrées localement

## 📈 Rapports

- Export Excel mensuel
- Graphiques interactifs
- Calculs automatiques de bénéfices
- Suivi des KPI financiers

## 🎨 Interface

- Design moderne et responsive
- Logo Habila Ghost intégré
- Navigation intuitive
- Visualisations interactives avec Plotly

---

**Développé pour Habila Ghost** - Système de gestion financière sécurisé et efficace