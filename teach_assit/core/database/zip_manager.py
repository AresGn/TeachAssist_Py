"""
Utilitaire pour gérer les fichiers ZIP en conjonction avec la base de données.
"""

import os
import zipfile
import hashlib
from pathlib import Path
from teach_assit.core.database.db_manager import DatabaseManager


class ZipManager:
    """Gestionnaire pour les opérations sur les fichiers ZIP avec sauvegarde dans la base de données."""
    
    def __init__(self, db_manager=None):
        """
        Initialise le gestionnaire de fichiers ZIP.
        
        Args:
            db_manager (DatabaseManager, optional): Instance de gestionnaire de base de données.
                Si None, crée une nouvelle instance.
        """
        self.db_manager = db_manager or DatabaseManager()
        
        # Crée le dossier d'extraction si nécessaire
        project_root = Path(__file__).parent.parent.parent.parent
        self.extract_base_dir = project_root / "data" / "extracted"
        if not os.path.exists(self.extract_base_dir):
            os.makedirs(self.extract_base_dir)
    
    def calculate_md5(self, filepath):
        """
        Calcule le hash MD5 d'un fichier.
        
        Args:
            filepath (str): Chemin vers le fichier
            
        Returns:
            str: Hash MD5 du fichier
        """
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def import_zip_file(self, filepath, description=None, auto_extract=False):
        """
        Importe un fichier ZIP dans la base de données.
        
        Args:
            filepath (str): Chemin vers le fichier ZIP
            description (str, optional): Description du fichier
            auto_extract (bool, optional): Si True, extrait automatiquement le fichier
            
        Returns:
            tuple: (zip_id, folder_id si extrait, sinon None)
        """
        if not os.path.exists(filepath) or not zipfile.is_zipfile(filepath):
            raise ValueError(f"Le fichier {filepath} n'existe pas ou n'est pas un fichier ZIP valide")
        
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        md5_hash = self.calculate_md5(filepath)
        
        # Sauvegarde dans la base de données
        zip_id = self.db_manager.add_zip_file(
            filename=filename,
            filepath=filepath,
            file_size=file_size,
            md5_hash=md5_hash,
            description=description
        )
        
        folder_id = None
        if auto_extract:
            folder_id = self.extract_zip(zip_id, filepath)
        
        return zip_id, folder_id
    
    def extract_zip(self, zip_id, zip_filepath=None):
        """
        Extrait un fichier ZIP et enregistre les informations dans la base de données.
        
        Args:
            zip_id (int): ID du fichier ZIP dans la base de données
            zip_filepath (str, optional): Chemin du fichier ZIP. Si None, récupère depuis la BD.
            
        Returns:
            int: ID du dossier extrait
        """
        # Si le chemin n'est pas fourni, récupère-le depuis la base de données
        if zip_filepath is None:
            zip_files = self.db_manager.get_all_zip_files()
            for zip_file in zip_files:
                if zip_file[0] == zip_id:
                    zip_filepath = zip_file[2]
                    break
            
            if zip_filepath is None:
                raise ValueError(f"Fichier ZIP avec ID {zip_id} non trouvé dans la base de données")
        
        # Crée un dossier unique pour cette extraction
        extract_dir = self.extract_base_dir / f"zip_{zip_id}_{os.path.basename(zip_filepath).split('.')[0]}"
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)
        
        # Extrait le ZIP
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Enregistre le dossier extrait dans la base de données
        folder_id = self.db_manager.add_extracted_folder(zip_id, str(extract_dir))
        
        # Parcours tous les fichiers extraits et les ajoute à la base de données
        for root, _, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                file_type = os.path.splitext(file)[1].lstrip('.')
                
                self.db_manager.add_extracted_file(
                    folder_id=folder_id,
                    filepath=file_path,
                    file_size=file_size,
                    file_type=file_type
                )
        
        return folder_id
    
    def get_all_zip_files(self):
        """
        Récupère tous les fichiers ZIP.
        
        Returns:
            list: Liste de tuples avec les informations des fichiers ZIP
        """
        return self.db_manager.get_all_zip_files()
    
    def get_extracted_folders(self, zip_id):
        """
        Récupère tous les dossiers extraits pour un ZIP.
        
        Args:
            zip_id (int): ID du fichier ZIP
            
        Returns:
            list: Liste de tuples avec les informations des dossiers
        """
        return self.db_manager.get_extracted_folders_by_zip(zip_id)
    
    def get_extracted_files(self, folder_id):
        """
        Récupère tous les fichiers d'un dossier extrait.
        
        Args:
            folder_id (int): ID du dossier
            
        Returns:
            list: Liste de tuples avec les informations des fichiers
        """
        return self.db_manager.get_files_by_folder(folder_id)
    
    def delete_zip_with_extracts(self, zip_id):
        """
        Supprime un fichier ZIP et tous ses dossiers extraits de la base de données.
        Optionnellement, supprime aussi les fichiers physiques.
        
        Args:
            zip_id (int): ID du fichier ZIP
            
        Returns:
            bool: True si la suppression a réussi
        """
        # Récupère les informations du ZIP et des dossiers avant de les supprimer
        zip_files = self.db_manager.get_all_zip_files()
        zip_filepath = None
        for zip_file in zip_files:
            if zip_file[0] == zip_id:
                zip_filepath = zip_file[2]
                break
        
        extracted_folders = self.db_manager.get_extracted_folders_by_zip(zip_id)
        folder_paths = [folder[1] for folder in extracted_folders]
        
        # Supprime de la base de données
        db_success = self.db_manager.delete_zip_file(zip_id)
        
        return db_success 