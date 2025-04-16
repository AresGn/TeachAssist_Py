import os
import zipfile
import shutil
from datetime import datetime


class SubmissionManager:
    """Gestionnaire des soumissions d'étudiants (fichiers ZIP)."""
    
    def __init__(self):
        """Initialise le gestionnaire de soumissions."""
        self.base_dir = ""
        self.extraction_dir = ""
        self.student_folders = {}  # {nom_etudiant: {path: chemin, java_files: [liste_fichiers]}}
    
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
        """Extrait un fichier ZIP dans un dossier dédié à l'étudiant."""
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
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(student_dir)
                
            # Liste des fichiers Java extraits
            java_files = self._find_java_files(student_dir)
            
            # Stockage des informations
            self.student_folders[student_name] = {
                'path': student_dir,
                'java_files': java_files
            }
            
            return True, f"Extraction réussie : {len(java_files)} fichier(s) Java trouvé(s)"
            
        except zipfile.BadZipFile:
            return False, "Fichier ZIP corrompu ou invalide"
        except Exception as e:
            return False, f"Erreur lors de l'extraction : {str(e)}"
    
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
        """Renvoie les informations sur les dossiers d'étudiants."""
        return self.student_folders
    
    def clean_extraction_directory(self):
        """Supprime le répertoire d'extraction."""
        if self.extraction_dir and os.path.exists(self.extraction_dir):
            try:
                shutil.rmtree(self.extraction_dir)
                return True, "Répertoire d'extraction supprimé avec succès"
            except Exception as e:
                return False, f"Erreur lors de la suppression du répertoire : {str(e)}"
        return False, "Aucun répertoire d'extraction à supprimer" 