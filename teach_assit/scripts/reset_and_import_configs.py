"""
Script pour réinitialiser la base de données et importer toutes les configurations
des fichiers JSON vers la base de données SQLite.
"""

import os
import sys
import shutil
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from teach_assit.core.analysis.config_loader import ConfigLoader

def reset_database():
    """Supprime et réinitialise la base de données."""
    # Chemin du dossier data contenant la base de données
    data_dir = os.path.join(project_root, "data")
    db_file = os.path.join(data_dir, "teachassist.db")
    
    # Supprimer le fichier de base de données s'il existe
    if os.path.exists(db_file):
        print(f"Suppression de la base de données existante: {db_file}")
        try:
            os.remove(db_file)
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
    
    # S'assurer que le dossier data existe
    os.makedirs(data_dir, exist_ok=True)
    
    return True

def main():
    """
    Réinitialise la base de données et importe toutes les configurations depuis les fichiers JSON.
    """
    # Réinitialiser la base de données
    if not reset_database():
        print("Impossible de réinitialiser la base de données. Abandon.")
        return
    
    # Initialiser le chargeur de configuration avec le répertoire racine du projet
    config_loader = ConfigLoader(str(project_root))
    
    print("Importation des configurations vers la base de données...")
    
    # Importer toutes les configurations
    exercises_count, assessments_count = config_loader.import_configs_to_database()
    
    print(f"Importation terminée : {exercises_count} exercices et {assessments_count} évaluations importés.")
    
    # Charger les configurations pour vérifier
    exercises, assessments = config_loader.load_all_configs()
    
    print(f"La base de données contient maintenant {exercises} exercices et {assessments} évaluations.")

if __name__ == "__main__":
    main() 