# 🚀 Guide de Déploiement Streamlit Cloud

Ce guide vous accompagne dans le déploiement de l'application **Habila Ghosts - Gestion Financière** sur Streamlit Cloud.

## 📋 Prérequis

- Compte GitHub avec le repository de l'application
- Compte Streamlit Cloud (gratuit) : [share.streamlit.io](https://share.streamlit.io)
- Repository public ou accès privé configuré

## 🔧 Configuration Pré-Déploiement

### 1. Vérification des Fichiers

Assurez-vous que ces fichiers sont présents dans votre repository :

```
├── .streamlit/
│   ├── config.toml                 ✅ Configuration Streamlit
│   └── secrets.toml.template       ✅ Template des secrets
├── requirements.txt                ✅ Dépendances Python
├── app.py                         ✅ Application principale
├── pages/                         ✅ Pages de l'application
├── utils/                         ✅ Utilitaires
├── data/                          ✅ Données de démonstration
└── STREAMLIT_DEPLOYMENT.md        ✅ Ce guide
```

### 2. Configuration des Secrets

1. **Connectez-vous à Streamlit Cloud**
2. **Sélectionnez votre application déployée**
3. **Allez dans "Settings" > "Secrets"**
4. **Copiez le contenu du template** `.streamlit/secrets.toml.template`
5. **Personnalisez les valeurs** selon vos besoins :

```toml
[auth]
# Changez ce mot de passe pour la production !
default_admin_password = "votre_mot_de_passe_securise"

cookie_secret_key = "votre_cle_secrete_unique"

[app]
app_name = "Habila Ghosts - Gestion Financière"
company_capital = 150000
total_shares = 100

[demo]
enable_demo_data = true
```

## 🚀 Déploiement sur Streamlit Cloud

### Méthode 1 : Déploiement Direct

1. **Connectez-vous** à [share.streamlit.io](https://share.streamlit.io)
2. **Cliquez sur "New app"**
3. **Sélectionnez votre repository GitHub**
4. **Configurez** :
   - **Repository** : `votre-username/habila-ghosts`
   - **Branch** : `main` (ou votre branche principale)
   - **Main file path** : `app.py`
   - **App URL** : `habila-ghosts` (ou votre choix)

### Méthode 2 : Déploiement via URL

Utilisez cette URL en remplaçant les valeurs :
```
https://share.streamlit.io/deploy?repository=github.com/VOTRE-USERNAME/VOTRE-REPO&branch=main&mainModule=app.py
```

## ⚙️ Configuration Post-Déploiement

### 1. Vérification du Déploiement

✅ **L'application se charge sans erreur**  
✅ **Les données de démonstration sont créées automatiquement**  
✅ **L'authentification fonctionne**  
✅ **Toutes les pages sont accessibles**  

### 2. Première Connexion

- **Utilisateur** : `admin`
- **Mot de passe** : Celui configuré dans les secrets (par défaut : `habila2025`)

### 3. Configuration Initiale

1. **Connectez-vous** avec le compte admin
2. **Allez dans "Administration"** pour :
   - Changer le mot de passe administrateur
   - Créer d'autres utilisateurs si nécessaire
   - Configurer les paramètres de l'application

## 🔒 Sécurité

### Recommandations de Sécurité

1. **Changez immédiatement** le mot de passe administrateur par défaut
2. **Utilisez une clé secrète unique** pour les cookies
3. **Limitez l'accès** aux secrets Streamlit Cloud
4. **Surveillez** les logs d'accès régulièrement

### Gestion des Secrets

- ❌ **Ne jamais** commiter `.streamlit/secrets.toml`
- ✅ **Utilisez** uniquement l'interface Streamlit Cloud pour les secrets
- ✅ **Documentez** les secrets nécessaires pour l'équipe
- ✅ **Rotez** régulièrement les clés secrètes

## 📊 Données et Sauvegarde

### Données de Démonstration

L'application crée automatiquement des données de démonstration au premier démarrage :
- **Transactions** : 6 exemples de transactions
- **Employés** : 3 employés fictifs
- **Actionnaires** : 3 actionnaires avec répartition du capital

### Sauvegarde des Données

⚠️ **Important** : Streamlit Cloud utilise un stockage éphémère. Les données peuvent être perdues lors des redémarrages.

**Solutions recommandées** :
1. **Export régulier** via la fonction d'export Excel
2. **Intégration future** avec une base de données externe
3. **Sauvegarde manuelle** des fichiers CSV importants

## 🔧 Dépannage

### Problèmes Courants

#### 1. Erreur de Démarrage / Dépendances
```
ModuleNotFoundError: No module named 'xxx'
ERROR: Could not install packages due to an EnvironmentError
```
**Solutions** : 
- Vérifiez que `runtime.txt` utilise `python-3.11.9` (version stable)
- Utilisez des plages de versions dans `requirements.txt` au lieu de versions fixes
- Consultez `DEPLOYMENT_TROUBLESHOOTING.md` pour un guide détaillé

#### 2. Erreur d'Authentification
```
KeyError: 'auth'
```
**Solution** : Configurez les secrets dans l'interface Streamlit Cloud

#### 3. Données Non Créées
```
FileNotFoundError: data/transactions.csv
```
**Solution** : Vérifiez que `utils/demo_data.py` est présent et fonctionnel

#### 4. Erreur de Permissions
```
PermissionError: [Errno 13] Permission denied
```
**Solution** : Problème de permissions sur Streamlit Cloud, redéployez l'application

### Logs et Debugging

1. **Consultez les logs** dans l'interface Streamlit Cloud
2. **Activez le mode debug** temporairement si nécessaire
3. **Vérifiez la console** du navigateur pour les erreurs JavaScript

## 🔄 Mise à Jour de l'Application

### Déploiement Automatique

Streamlit Cloud redéploie automatiquement à chaque push sur la branche configurée.

### Mise à Jour Manuelle

1. **Allez dans l'interface Streamlit Cloud**
2. **Cliquez sur "Reboot"** pour redémarrer l'application
3. **Ou cliquez sur "Rerun"** pour une mise à jour légère

## 📞 Support

### Ressources Utiles

- **Documentation Streamlit** : [docs.streamlit.io](https://docs.streamlit.io)
- **Communauté Streamlit** : [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues** : Pour les problèmes spécifiques à l'application

### Contact

Pour toute question spécifique à cette application, créez une issue sur le repository GitHub.

---

## ✅ Checklist de Déploiement

- [ ] Repository GitHub configuré
- [ ] Compte Streamlit Cloud créé
- [ ] Application déployée
- [ ] Secrets configurés
- [ ] Première connexion réussie
- [ ] Mot de passe admin changé
- [ ] Données de démonstration vérifiées
- [ ] Toutes les fonctionnalités testées
- [ ] Documentation équipe mise à jour

**🎉 Félicitations ! Votre application Habila Ghosts est maintenant déployée sur Streamlit Cloud !**
