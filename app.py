#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application Habila Ghosts
Compatible avec HuggingFace Spaces, Railway, Render, etc.
"""

import os
import sys

# Ajouter le répertoire courant au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import de l'application Gradio
from gradio_app import create_interface

def main():
    """Fonction principale pour lancer l'application"""
    
    # Créer l'interface Gradio
    interface = create_interface()
    
    # Configuration pour différents environnements de déploiement
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Lancer l'application
    interface.launch(
        server_name=host,
        server_port=port,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()