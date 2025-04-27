"""
Exemple d'utilisation de la base de données SQLite et du gestionnaire de fichiers ZIP.
"""

import os
from pathlib import Path
from teach_assit.core.database.db_manager import DatabaseManager
from teach_assit.core.database.zip_manager import ZipManager


def demo_database():
    """
    Démontre l'utilisation de la base de données et du gestionnaire de ZIP.
    """
    # Initialise les gestionnaires
    db_manager = DatabaseManager()
    zip_manager = ZipManager(db_manager)
    
    # Chemin d'exemple vers un fichier ZIP (à remplacer par un vrai fichier)
    project_root = Path(__file__).parent.parent.parent.parent
    example_zip_path = project_root / "data" / "example.zip"
    
    # Vérifie si le fichier exemple existe
    if not os.path.exists(example_zip_path):
        print(f"Le fichier exemple {example_zip_path} n'existe pas.")
        print("Veuillez créer un fichier ZIP d'exemple pour tester cette fonctionnalité.")
        return
    
    print("=== Démonstration de la base de données SQLite ===")
    
    # Importer un fichier ZIP
    print("\n1. Import d'un fichier ZIP")
    zip_id, _ = zip_manager.import_zip_file(
        filepath=str(example_zip_path),
        description="Fichier ZIP d'exemple pour démonstration",
        auto_extract=False
    )
    print(f"Fichier ZIP importé avec ID: {zip_id}")
    
    # Extraire le fichier ZIP
    print("\n2. Extraction du fichier ZIP")
    folder_id = zip_manager.extract_zip(zip_id)
    print(f"Fichier extrait dans le dossier avec ID: {folder_id}")
    
    # Lister tous les fichiers ZIP
    print("\n3. Liste de tous les fichiers ZIP")
    all_zips = zip_manager.get_all_zip_files()
    for zip_file in all_zips:
        print(f"ID: {zip_file[0]}, Nom: {zip_file[1]}, Taille: {zip_file[3]} octets, Date: {zip_file[4]}")
    
    # Lister les dossiers extraits
    print("\n4. Liste des dossiers extraits pour le ZIP")
    folders = zip_manager.get_extracted_folders(zip_id)
    for folder in folders:
        print(f"ID: {folder[0]}, Chemin: {folder[1]}, Date: {folder[2]}, Statut: {folder[3]}")
        
        # Lister les fichiers dans ce dossier
        print("\n  Fichiers dans ce dossier:")
        files = zip_manager.get_extracted_files(folder[0])
        for file in files:
            print(f"  - ID: {file[0]}, Chemin: {file[1]}, Taille: {file[2]} octets, Type: {file[3]}")
    
    print("\n=== Fin de la démonstration ===")


if __name__ == "__main__":
    demo_database() 