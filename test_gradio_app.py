#!/usr/bin/env python3
"""
Script de test pour vérifier que l'application Gradio fonctionne correctement
"""

import sys
import os

def test_imports():
    """Tester les imports nécessaires"""
    print("🔍 Test des imports...")
    
    try:
        import gradio as gr
        print("✅ Gradio importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import Gradio: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import Pandas: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import Plotly: {e}")
        return False
    
    return True

def test_data_files():
    """Tester la présence des fichiers de données"""
    print("\n📁 Test des fichiers de données...")
    
    required_files = [
        "data/transactions.csv",
        "data/employees.csv", 
        "data/shareholders.csv"
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} présent")
        else:
            print(f"❌ {file_path} manquant")
            all_present = False
    
    return all_present

def test_models():
    """Tester les modèles de données"""
    print("\n🏗️ Test des modèles...")
    
    try:
        from models.transaction import Transaction
        from models.employee import Employee
        from models.shareholder import Shareholder
        print("✅ Modèles importés avec succès")
        return True
    except ImportError as e:
        print(f"❌ Erreur import modèles: {e}")
        return False

def test_utils():
    """Tester les utilitaires"""
    print("\n🛠️ Test des utilitaires...")
    
    try:
        from utils.data_manager import DataManager
        print("✅ DataManager importé avec succès")
        
        # Test d'initialisation
        dm = DataManager()
        print("✅ DataManager initialisé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur utilitaires: {e}")
        return False

def test_gradio_app():
    """Tester l'application Gradio"""
    print("\n🎯 Test de l'application Gradio...")
    
    try:
        # Import de l'application sans la lancer
        sys.path.append('.')
        from gradio_app import HabilaGhostsApp
        
        # Test d'initialisation
        app = HabilaGhostsApp()
        print("✅ Application Gradio initialisée avec succès")
        
        # Test d'authentification
        message, success = app.authenticate("admin", "habila2025")
        if success:
            print("✅ Authentification testée avec succès")
        else:
            print(f"❌ Erreur authentification: {message}")
            return False
        
        # Test de chargement des données
        metrics, charts, recent_trans, status = app.get_dashboard_data()
        if "✅" in status:
            print("✅ Chargement des données testé avec succès")
        else:
            print(f"❌ Erreur chargement données: {status}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur application Gradio: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Tests de l'Application Habila Ghosts - Gradio")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Fichiers de données", test_data_files),
        ("Modèles", test_models),
        ("Utilitaires", test_utils),
        ("Application Gradio", test_gradio_app)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Résultats des Tests:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Tous les tests sont passés! L'application est prête pour le déploiement.")
        print("\n🚀 Pour lancer l'application:")
        print("   python gradio_app.py")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())