# 🔧 Guide de Dépannage - Déploiement Streamlit Cloud

## 🚨 Problèmes Courants et Solutions

### 1. Erreur d'Installation des Dépendances

#### Symptômes
```
ModuleNotFoundError: No module named 'xxx'
ERROR: Could not install packages due to an EnvironmentError
```

#### Solutions
1. **Vérifiez la version Python** dans `runtime.txt`
   - ✅ Utilisez `python-3.11.9` (version stable et supportée)
   - ❌ Évitez `python-3.13.x` (trop récent, peut causer des incompatibilités)

2. **Vérifiez requirements.txt**
   ```txt
   # ✅ Bon format avec plages de versions
   streamlit>=1.28.0,<2.0.0
   pandas>=2.0.0,<3.0.0
   
   # ❌ Évitez les versions trop spécifiques
   streamlit==1.35.0  # Peut causer des conflits
   ```

3. **Ajoutez les dépendances système** dans `packages.txt`
   ```txt
   build-essential
   pkg-config
   ```

### 2. Erreur de Démarrage de l'Application

#### Symptômes
```
FileNotFoundError: [Errno 2] No such file or directory
PermissionError: [Errno 13] Permission denied
```

#### Solutions
1. **Vérifiez la structure des fichiers**
   ```
   ├── app.py                    ✅ Point d'entrée
   ├── requirements.txt          ✅ Dépendances
   ├── runtime.txt              ✅ Version Python
   ├── packages.txt             ✅ Dépendances système
   ├── .streamlit/
   │   ├── config.toml          ✅ Configuration
   │   └── secrets.toml.template ✅ Template secrets
   ```

2. **Configurez les secrets** dans l'interface Streamlit Cloud
   ```toml
   [auth]
   default_admin_password = "votre_mot_de_passe"
   ```

### 3. Erreur de Chargement des Données

#### Symptômes
```
FileNotFoundError: data/transactions.csv
pandas.errors.EmptyDataError
```

#### Solutions
1. **Vérifiez l'initialisation des données de démonstration**
   - Le fichier `utils/demo_data.py` doit être présent
   - La fonction `create_demo_data()` doit s'exécuter au démarrage

2. **Vérifiez les permissions d'écriture**
   - Streamlit Cloud a des restrictions sur l'écriture de fichiers
   - Les données sont créées en mémoire au démarrage

### 4. Erreur de Configuration

#### Symptômes
```
KeyError: 'auth'
streamlit.errors.StreamlitAPIException
```

#### Solutions
1. **Configurez les secrets** correctement
2. **Vérifiez la syntaxe TOML** des secrets
3. **Redémarrez l'application** après modification des secrets

## 🛠️ Étapes de Dépannage

### Étape 1: Vérification Locale
```bash
# Testez localement avec la même version Python
python3.11 -m pip install -r requirements.txt
python3.11 app.py
```

### Étape 2: Vérification des Logs
1. Allez dans l'interface Streamlit Cloud
2. Consultez les logs de déploiement
3. Identifiez l'erreur spécifique

### Étape 3: Solutions Progressives

#### Solution 1: Redéploiement Simple
1. Modifiez un fichier (ajoutez un commentaire)
2. Commitez et pushez
3. Attendez le redéploiement automatique

#### Solution 2: Nettoyage du Cache
1. Dans l'interface Streamlit Cloud
2. Cliquez sur "Reboot app"
3. Attendez le redémarrage complet

#### Solution 3: Recréation de l'App
1. Supprimez l'application dans Streamlit Cloud
2. Recréez-la avec les mêmes paramètres
3. Reconfigurez les secrets

## 📋 Checklist de Déploiement

### Avant le Déploiement
- [ ] `runtime.txt` contient `python-3.11.9`
- [ ] `requirements.txt` utilise des plages de versions
- [ ] `packages.txt` contient les dépendances système
- [ ] `.streamlit/config.toml` est optimisé pour le cloud
- [ ] Tous les fichiers sont commitées et pushées

### Pendant le Déploiement
- [ ] Sélection du bon repository et branche
- [ ] Configuration du fichier principal (`app.py`)
- [ ] Configuration des secrets dans "Advanced settings"
- [ ] Attente complète du déploiement (2-5 minutes)

### Après le Déploiement
- [ ] Test de l'authentification
- [ ] Vérification des données de démonstration
- [ ] Test de toutes les pages
- [ ] Changement du mot de passe admin par défaut

## 🆘 Support d'Urgence

### Si Rien ne Fonctionne

1. **Utilisez une configuration minimale**
   ```txt
   # requirements.txt minimal
   streamlit
   pandas
   plotly
   openpyxl
   ```

2. **Simplifiez runtime.txt**
   ```txt
   python-3.11
   ```

3. **Videz packages.txt**
   ```txt
   # Commentez tout temporairement
   ```

4. **Contactez le support**
   - GitHub Issues du projet
   - Documentation Streamlit Cloud
   - Forums Streamlit Community

## 📞 Ressources Utiles

- **Documentation Streamlit Cloud**: [docs.streamlit.io](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- **Forum Communauté**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Status Streamlit**: [status.streamlit.io](https://status.streamlit.io)
- **GitHub Issues**: Repository du projet

---

**💡 Conseil**: Gardez toujours une version de sauvegarde qui fonctionne localement avant de déployer sur le cloud.