"""
Script pour importer les configurations d'exercices et d'évaluations
depuis les fichiers JSON vers la base de données SQLite.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from teach_assit.core.analysis.config_loader import ConfigLoader

def main():
    """
    Importe toutes les configurations depuis les fichiers JSON vers la base de données.
    """
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