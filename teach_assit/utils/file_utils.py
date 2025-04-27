import os
import zipfile
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from teach_assit.core.database.db_manager import DatabaseManager
from teach_assit.core.database.zip_manager import ZipManager


class SubmissionManager:
    """Gestionnaire des soumissions d'étudiants (fichiers ZIP)."""
    
    def __init__(self):
        """Initialise le gestionnaire de soumissions."""
        self.base_dir = ""
        self.extraction_dir = ""
        self.student_folders = {}  # {nom_etudiant: {path: chemin, java_files: [liste_fichiers]}}
        
        # Initialisation de la base de données SQLite
        self.db_manager = DatabaseManager()
        self.zip_manager = ZipManager(self.db_manager)
    
    def set_base_directory(self, directory):
        """Définit le répertoire de base contenant les fichiers ZIP."""
        self.base_dir = directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.extraction_dir = os.path.join(directory, f"extracted_{timestamp}")
        self.student_folders = {}
        return self.extraction_dir
    
    def list_zip_files(self):
        """Liste tous les fichiers ZIP dans le répertoire de base."""
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return []
        
        return [f for f in os.listdir(self.base_dir) if f.lower().endswith('.zip')]
    
    def extract_zip_file(self, zip_filename):
        """
        Extrait un fichier ZIP dans un dossier dédié à l'étudiant et stocke dans la base de données.
        """
        if not self.extraction_dir:
            raise ValueError("Le répertoire d'extraction n'a pas été défini")
            
        # Création du répertoire d'extraction s'il n'existe pas
        os.makedirs(self.extraction_dir, exist_ok=True)
        
        zip_path = os.path.join(self.base_dir, zip_filename)
        
        # Extraction du nom de l'étudiant depuis le nom du fichier ZIP
        student_name = os.path.splitext(zip_filename)[0]
        student_dir = os.path.join(self.extraction_dir, student_name)
        
        # Création du répertoire de l'étudiant
        os.makedirs(student_dir, exist_ok=True)
        
        # Extraction du contenu du ZIP
        try:
            # Stockage dans la base de données SQLite
            description = f"Soumission de {student_name}"
            zip_id, _ = self.zip_manager.import_zip_file(
                filepath=zip_path,
                description=description,
                auto_extract=False
            )
            
            # Extraction traditionnelle du ZIP pour maintenir la compatibilité
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(student_dir)
            
            # Liste des fichiers Java extraits
            java_files = self._find_java_files(student_dir)
            
            # Stockage des informations (pour la compatibilité avec l'existant)
            self.student_folders[student_name] = {
                'path': student_dir,
                'java_files': java_files,
                'zip_id': zip_id  # Stocke l'ID de la BD pour référence future
            }
            
            # Extraction dans la base de données et stockage des informations
            folder_id = self.zip_manager.extract_zip(zip_id, zip_path)
            
            # Mise à jour des métadonnées dans la base de données
            self._store_java_files_info(folder_id, java_files, student_dir)
            
            return True, f"Extraction réussie : {len(java_files)} fichier(s) Java trouvé(s)"
            
        except zipfile.BadZipFile:
            return False, "Fichier ZIP corrompu ou invalide"
        except Exception as e:
            return False, f"Erreur lors de l'extraction : {str(e)}"
    
    def _store_java_files_info(self, folder_id, java_files, student_dir):
        """
        Met à jour les métadonnées des fichiers Java dans la base de données.
        """
        # Cette fonction pourrait être utilisée pour stocker des informations 
        # spécifiques sur les fichiers Java dans la base de données
        pass
    
    def extract_all_zip_files(self):
        """Extrait tous les fichiers ZIP du répertoire de base."""
        results = {}
        zip_files = self.list_zip_files()
        
        for zip_file in zip_files:
            results[zip_file] = self.extract_zip_file(zip_file)
            
        return results
    
    def _find_java_files(self, directory):
        """Trouve récursivement tous les fichiers Java dans un répertoire."""
        java_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.java'):
                    # Chemin relatif par rapport au répertoire de l'étudiant
                    rel_path = os.path.relpath(os.path.join(root, file), directory)
                    java_files.append(rel_path)
        
        return java_files
    
    def get_student_folders(self):
        """
        Renvoie les informations sur les dossiers d'étudiants.
        Si des dossiers ont été extraits en utilisant la base de données,
        les récupère également.
        """
        # Synchroniser avec la base de données si pas de dossiers en mémoire
        if not self.student_folders and hasattr(self, 'zip_manager'):
            # Récupérer tous les fichiers ZIP de la base de données
            zip_files = self.get_all_zip_files_from_db()
            
            for zip_file in zip_files:
                zip_id = zip_file[0]
                zip_filename = zip_file[1]
                
                # Récupérer les dossiers extraits pour ce ZIP
                extracted_folders = self.get_extracted_folders_from_db(zip_id)
                
                if extracted_folders:
                    # Extraire le nom de l'étudiant depuis le nom du fichier ZIP
                    student_name = os.path.splitext(zip_filename)[0]
                    
                    for folder in extracted_folders:
                        folder_id = folder[0]
                        folder_path = folder[1]
                        
                        # Récupérer les fichiers java dans ce dossier
                        extracted_files = self.get_extracted_files_from_db(folder_id)
                        java_files = []
                        
                        for file in extracted_files:
                            file_path = file[1]
                            file_type = file[3]
                            if file_type and file_type.lower() == 'java':
                                # Chemin relatif par rapport au dossier de l'étudiant
                                try:
                                    rel_path = os.path.relpath(file_path, folder_path)
                                    java_files.append(rel_path)
                                except:
                                    # Fallback si le chemin relatif ne peut pas être déterminé
                                    java_files.append(os.path.basename(file_path))
                        
                        # Ajouter à la liste des dossiers d'étudiants
                        if student_name not in self.student_folders:
                            self.student_folders[student_name] = {
                                'path': folder_path,
                                'java_files': java_files,
                                'zip_id': zip_id,
                                'folder_id': folder_id
                            }
        
        return self.student_folders
    
    def get_all_zip_files_from_db(self):
        """
        Récupère tous les fichiers ZIP stockés dans la base de données.
        
        Returns:
            list: Liste de tuples avec les informations des fichiers ZIP
        """
        return self.zip_manager.get_all_zip_files()
    
    def get_extracted_folders_from_db(self, zip_id):
        """
        Récupère tous les dossiers extraits pour un ZIP depuis la base de données.
        
        Args:
            zip_id (int): ID du fichier ZIP
            
        Returns:
            list: Liste de tuples avec les informations des dossiers
        """
        return self.zip_manager.get_extracted_folders(zip_id)
    
    def get_extracted_files_from_db(self, folder_id):
        """
        Récupère tous les fichiers d'un dossier extrait depuis la base de données.
        
        Args:
            folder_id (int): ID du dossier
            
        Returns:
            list: Liste de tuples avec les informations des fichiers
        """
        return self.zip_manager.get_extracted_files(folder_id)
    
    def clean_extraction_directory(self):
        """Supprime le répertoire d'extraction."""
        if self.extraction_dir and os.path.exists(self.extraction_dir):
            try:
                shutil.rmtree(self.extraction_dir)
                return True, "Répertoire d'extraction supprimé avec succès"
            except Exception as e:
                return False, f"Erreur lors de la suppression du répertoire : {str(e)}"
        return False, "Aucun répertoire d'extraction à supprimer"
    
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