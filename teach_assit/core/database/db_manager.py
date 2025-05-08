"""
Gestionnaire de base de données SQLite pour TeachAssist.
Permet de stocker les informations sur les fichiers ZIP et les dossiers extraits.
"""

import os
from pathlib import Path

from teach_assit.core.database.managers import (
    ConnectionProvider,
    SchemaManager,
    ZipManager,
    ExerciseManager,
    AssessmentManager,
    SettingsManager,
    FeedbackManager
)

class DatabaseManager:
    """Gestionnaire de base de données SQLite pour l'application TeachAssist."""
    
    def __init__(self, db_path=None):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            db_path (str, optional): Chemin vers le fichier de base de données.
                Si None, utilise le dossier data à la racine du projet.
        """
        if db_path is None:
            # Utilise le dossier data à la racine du projet
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = project_root / "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            self.db_path = str(data_dir / "teachassist.db")
        else:
            self.db_path = db_path
        
        # Initialise le fournisseur de connexion
        self.connection_provider = ConnectionProvider(self.db_path)
        
        # Initialise les gestionnaires spécialisés
        self.schema_manager = SchemaManager(self.connection_provider)
        self.zip_manager = ZipManager(self.connection_provider)
        self.exercise_manager = ExerciseManager(self.connection_provider)
        self.assessment_manager = AssessmentManager(self.connection_provider)
        self.settings_manager = SettingsManager(self.connection_provider)
        self.feedback_manager = FeedbackManager(self.connection_provider)
        
        # Initialisation de la structure de la base de données
        self.schema_manager.initialize_database()
    
    # Méthodes déléguées au ZipManager
    
    def add_zip_file(self, filename, filepath, file_size, md5_hash=None, description=None):
        """
        Ajoute un fichier ZIP à la base de données.
        
        Args:
            filename (str): Nom du fichier ZIP
            filepath (str): Chemin complet vers le fichier
            file_size (int): Taille du fichier en octets
            md5_hash (str, optional): Hash MD5 du fichier pour vérification
            description (str, optional): Description du contenu du ZIP
            
        Returns:
            int: ID du fichier ZIP dans la base de données
        """
        return self.zip_manager.add_zip_file(filename, filepath, file_size, md5_hash, description)
    
    def add_extracted_folder(self, zip_id, folder_path):
        """
        Ajoute un dossier extrait à la base de données.
        
        Args:
            zip_id (int): ID du fichier ZIP d'origine
            folder_path (str): Chemin vers le dossier extrait
            
        Returns:
            int: ID du dossier extrait
        """
        return self.zip_manager.add_extracted_folder(zip_id, folder_path)
    
    def add_extracted_file(self, folder_id, filepath, file_size, file_type=None):
        """
        Ajoute un fichier extrait à la base de données.
        
        Args:
            folder_id (int): ID du dossier contenant le fichier
            filepath (str): Chemin vers le fichier
            file_size (int): Taille du fichier en octets
            file_type (str, optional): Type du fichier (extension)
            
        Returns:
            int: ID du fichier extrait
        """
        return self.zip_manager.add_extracted_file(folder_id, filepath, file_size, file_type)
    
    def get_all_zip_files(self):
        """
        Récupère tous les fichiers ZIP stockés dans la base de données.
        
        Returns:
            list: Liste de tuples contenant les informations des fichiers ZIP
        """
        return self.zip_manager.get_all_zip_files()
    
    def get_extracted_folders_by_zip(self, zip_id):
        """
        Récupère tous les dossiers extraits pour un fichier ZIP donné.
        
        Args:
            zip_id (int): ID du fichier ZIP
            
        Returns:
            list: Liste de tuples contenant les informations des dossiers
        """
        return self.zip_manager.get_extracted_folders_by_zip(zip_id)
    
    def get_files_by_folder(self, folder_id):
        """
        Récupère tous les fichiers d'un dossier extrait.
        
        Args:
            folder_id (int): ID du dossier
            
        Returns:
            list: Liste de tuples contenant les informations des fichiers
        """
        return self.zip_manager.get_files_by_folder(folder_id)
    
    def delete_zip_file(self, zip_id):
        """
        Supprime un fichier ZIP et tous ses dossiers/fichiers associés.
        
        Args:
            zip_id (int): ID du fichier ZIP à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        return self.zip_manager.delete_zip_file(zip_id)
    
    def update_extracted_folder_status(self, folder_id, status):
        """
        Met à jour le statut d'un dossier extrait.
        
        Args:
            folder_id (int): ID du dossier
            status (str): Nouveau statut ('active', 'archived', etc.)
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        return self.zip_manager.update_extracted_folder_status(folder_id, status)
    
    # Méthodes déléguées au ExerciseManager
    
    def add_exercise_config(self, config_dict):
        """
        Ajoute ou met à jour une configuration d'exercice dans la base de données.
        
        Args:
            config_dict (dict): Dictionnaire de configuration de l'exercice
            
        Returns:
            bool: True si l'opération a réussi
        """
        return self.exercise_manager.add_exercise_config(config_dict)
    
    def get_exercise_config(self, exercise_id):
        """
        Récupère une configuration d'exercice par son ID.
        
        Args:
            exercise_id (str): ID de l'exercice
            
        Returns:
            dict: Configuration de l'exercice, None si non trouvé
        """
        return self.exercise_manager.get_exercise_config(exercise_id)
    
    def get_all_exercise_configs(self):
        """
        Récupère toutes les configurations d'exercices.
        
        Returns:
            dict: Dictionnaire de configurations {id: config_dict}
        """
        return self.exercise_manager.get_all_exercise_configs()
    
    def delete_exercise_config(self, exercise_id):
        """
        Supprime une configuration d'exercice.
        
        Args:
            exercise_id (str): ID de l'exercice à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        return self.exercise_manager.delete_exercise_config(exercise_id)
    
    # Méthodes déléguées au AssessmentManager
    
    def add_assessment_config(self, config_dict):
        """
        Ajoute ou met à jour une configuration d'évaluation dans la base de données.
        
        Args:
            config_dict (dict): Dictionnaire de configuration de l'évaluation
            
        Returns:
            bool: True si l'opération a réussi
        """
        return self.assessment_manager.add_assessment_config(config_dict)
    
    def get_assessment_config(self, assessment_id):
        """
        Récupère une configuration d'évaluation par son ID.
        
        Args:
            assessment_id (str): ID de l'évaluation
            
        Returns:
            dict: Configuration de l'évaluation, None si non trouvée
        """
        return self.assessment_manager.get_assessment_config(assessment_id)
    
    def get_all_assessment_configs(self):
        """
        Récupère toutes les configurations d'évaluations.
        
        Returns:
            dict: Dictionnaire de configurations {id: config_dict}
        """
        return self.assessment_manager.get_all_assessment_configs()
    
    def delete_assessment_config(self, assessment_id):
        """
        Supprime une configuration d'évaluation.
        
        Args:
            assessment_id (str): ID de l'évaluation à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        return self.assessment_manager.delete_assessment_config(assessment_id)
    
    # Méthodes déléguées au SettingsManager
    
    def save_setting(self, key, value, description=None):
        """
        Sauvegarde un paramètre dans la base de données.
        
        Args:
            key (str): Clé du paramètre
            value (str): Valeur du paramètre
            description (str, optional): Description du paramètre
            
        Returns:
            bool: True si l'opération a réussi
        """
        return self.settings_manager.save_setting(key, value, description)
    
    def get_setting(self, key, default_value=None):
        """
        Récupère la valeur d'un paramètre.
        
        Args:
            key (str): Clé du paramètre
            default_value: Valeur par défaut si le paramètre n'existe pas
            
        Returns:
            str: Valeur du paramètre ou default_value si non trouvé
        """
        return self.settings_manager.get_setting(key, default_value)
    
    def delete_setting(self, key):
        """
        Supprime un paramètre.
        
        Args:
            key (str): Clé du paramètre
            
        Returns:
            bool: True si l'opération a réussi
        """
        return self.settings_manager.delete_setting(key)
    
    def get_all_settings(self):
        """
        Récupère tous les paramètres.
        
        Returns:
            dict: Dictionnaire {clé: valeur} de tous les paramètres
        """
        return self.settings_manager.get_all_settings()
    
    # Méthodes déléguées au FeedbackManager
    
    def add_feedback(self, student_name, assessment_id, feedback_content, global_grade=None):
        """
        Ajoute un feedback dans la base de données.
        
        Args:
            student_name (str): Nom de l'étudiant
            assessment_id (str): ID de l'évaluation (peut être None)
            feedback_content (str): Contenu du feedback
            global_grade (str, optional): Note globale
            
        Returns:
            int: ID du feedback dans la base de données, ou -1 en cas d'erreur
        """
        return self.feedback_manager.add_feedback(student_name, assessment_id, feedback_content, global_grade)
    
    def get_feedback(self, feedback_id):
        """
        Récupère un feedback par son ID.
        
        Args:
            feedback_id (int): ID du feedback
            
        Returns:
            dict: Données du feedback, None si non trouvé
        """
        return self.feedback_manager.get_feedback(feedback_id)
    
    def get_student_feedbacks(self, student_name):
        """
        Récupère tous les feedbacks d'un étudiant.
        
        Args:
            student_name (str): Nom de l'étudiant
            
        Returns:
            list: Liste des feedbacks de l'étudiant
        """
        return self.feedback_manager.get_student_feedbacks(student_name)
    
    def get_assessment_feedbacks(self, assessment_id):
        """
        Récupère tous les feedbacks d'une évaluation.
        
        Args:
            assessment_id (str): ID de l'évaluation
            
        Returns:
            list: Liste des feedbacks de l'évaluation
        """
        return self.feedback_manager.get_assessment_feedbacks(assessment_id)
    
    def get_all_feedbacks(self):
        """
        Récupère tous les feedbacks de la base de données.
        
        Returns:
            list: Liste de tous les feedbacks
        """
        return self.feedback_manager.get_all_feedbacks()
    
    def delete_feedback(self, feedback_id):
        """
        Supprime un feedback.
        
        Args:
            feedback_id (int): ID du feedback à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        return self.feedback_manager.delete_feedback(feedback_id) 