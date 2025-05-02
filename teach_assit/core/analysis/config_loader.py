import os
import json
from teach_assit.core.analysis.models import ExerciseConfig, AssessmentConfig
from teach_assit.core.database.db_manager import DatabaseManager


class ConfigLoader:
    """Chargeur de configurations pour les exercices et les évaluations, avec support de base de données."""
    
    def __init__(self, base_dir=''):
        """
        Initialise le chargeur de configurations.
        
        Args:
            base_dir (str): Répertoire de base de l'application.
        """
        self.base_dir = base_dir
        self.configs_dir = os.path.join(base_dir, 'configs')
        self.assessments_dir = os.path.join(base_dir, 'assessments')
        
        # Dictionnaires de configurations chargées
        self.exercise_configs = {}  # {id: ExerciseConfig}
        self.assessment_configs = {}  # {id: AssessmentConfig}
        
        # Créer les répertoires s'ils n'existent pas
        os.makedirs(self.configs_dir, exist_ok=True)
        os.makedirs(self.assessments_dir, exist_ok=True)
        
        # Initialisation du gestionnaire de base de données
        self.db_manager = DatabaseManager()
    
    def load_all_configs(self):
        """
        Charge toutes les configurations disponibles depuis la base de données et les fichiers.
        Si une configuration existe dans les deux, la version de la base de données est utilisée.
        
        Returns:
            tuple: (nombre d'exercices chargés, nombre d'évaluations chargées)
        """
        exercise_count = self.load_exercise_configs()
        assessment_count = self.load_assessment_configs()
        return exercise_count, assessment_count
    
    def load_exercise_configs(self):
        """
        Charge toutes les configurations d'exercices depuis la base de données et les fichiers.
        
        Returns:
            int: Nombre de configurations chargées.
        """
        self.exercise_configs = {}
        count = 0
        
        # 1. Charger depuis la base de données
        db_configs = self.db_manager.get_all_exercise_configs()
        for config_id, config_dict in db_configs.items():
            self.exercise_configs[config_id] = ExerciseConfig(config_dict)
            count += 1
        
        # 2. Charger depuis les fichiers (pour ceux qui ne sont pas encore dans la base)
        self._load_exercise_configs_from_files()
        
        return len(self.exercise_configs)
    
    def _load_exercise_configs_from_files(self):
        """Charge les configurations d'exercices depuis les fichiers JSON."""
        if not os.path.exists(self.configs_dir):
            return 0
        
        count = 0
        for filename in os.listdir(self.configs_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.configs_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config_dict = json.load(f)
                        if 'id' in config_dict:
                            # Si cette configuration n'est pas déjà chargée depuis la BD
                            if config_dict['id'] not in self.exercise_configs:
                                config = ExerciseConfig(config_dict)
                                self.exercise_configs[config.id] = config
                                
                                # Ajouter à la base de données
                                self.db_manager.add_exercise_config(config_dict)
                                count += 1
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Erreur lors du chargement de {filename}: {str(e)}")
        
        return count
    
    def load_assessment_configs(self):
        """
        Charge toutes les configurations d'évaluations depuis la base de données et les fichiers.
        
        Returns:
            int: Nombre de configurations chargées.
        """
        self.assessment_configs = {}
        count = 0
        
        # 1. Charger depuis la base de données
        db_configs = self.db_manager.get_all_assessment_configs()
        for config_id, config_dict in db_configs.items():
            self.assessment_configs[config_id] = AssessmentConfig(config_dict)
            count += 1
        
        # 2. Charger depuis les fichiers (pour ceux qui ne sont pas encore dans la base)
        self._load_assessment_configs_from_files()
        
        return len(self.assessment_configs)
    
    def _load_assessment_configs_from_files(self):
        """Charge les configurations d'évaluations depuis les fichiers JSON."""
        if not os.path.exists(self.assessments_dir):
            return 0
        
        count = 0
        for filename in os.listdir(self.assessments_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.assessments_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config_dict = json.load(f)
                        if 'assessmentId' in config_dict:
                            # Si cette configuration n'est pas déjà chargée depuis la BD
                            if config_dict['assessmentId'] not in self.assessment_configs:
                                config = AssessmentConfig(config_dict)
                                self.assessment_configs[config.id] = config
                                
                                # Ajouter à la base de données
                                self.db_manager.add_assessment_config(config_dict)
                                count += 1
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Erreur lors du chargement de {filename}: {str(e)}")
        
        return count
    
    def get_exercise_config(self, exercise_id):
        """
        Récupère une configuration d'exercice par son identifiant.
        
        Args:
            exercise_id (str): Identifiant de l'exercice.
            
        Returns:
            ExerciseConfig: Configuration de l'exercice, None si non trouvée.
        """
        # Essayer d'abord dans notre cache
        if exercise_id in self.exercise_configs:
            return self.exercise_configs[exercise_id]
        
        # Essayer de charger depuis la base de données
        config_dict = self.db_manager.get_exercise_config(exercise_id)
        if config_dict:
            config = ExerciseConfig(config_dict)
            self.exercise_configs[exercise_id] = config
            return config
            
        return None
    
    def get_assessment_config(self, assessment_id):
        """
        Récupère une configuration d'évaluation par son identifiant.
        
        Args:
            assessment_id (str): Identifiant de l'évaluation.
            
        Returns:
            AssessmentConfig: Configuration de l'évaluation, None si non trouvée.
        """
        # Essayer d'abord dans notre cache
        if assessment_id in self.assessment_configs:
            return self.assessment_configs[assessment_id]
        
        # Essayer de charger depuis la base de données
        config_dict = self.db_manager.get_assessment_config(assessment_id)
        if config_dict:
            config = AssessmentConfig(config_dict)
            self.assessment_configs[assessment_id] = config
            return config
            
        return None
    
    def get_all_exercise_configs(self):
        """
        Récupère toutes les configurations d'exercices.
        
        Returns:
            dict: Dictionnaire {id: ExerciseConfig}.
        """
        return self.exercise_configs
    
    def get_all_assessment_configs(self):
        """
        Récupère toutes les configurations d'évaluations.
        
        Returns:
            dict: Dictionnaire {id: AssessmentConfig}.
        """
        return self.assessment_configs
    
    def save_exercise_config(self, config):
        """
        Sauvegarde une configuration d'exercice dans la base de données et dans un fichier.
        
        Args:
            config (ExerciseConfig): Configuration à sauvegarder.
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon.
        """
        if not config.id:
            return False
        
        # Sauvegarder dans la base de données
        db_success = self.db_manager.add_exercise_config(config.to_dict())
        
        # Sauvegarder dans un fichier JSON (pour compatibilité)
        filename = f"{config.id}.json"
        filepath = os.path.join(self.configs_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Mettre à jour le cache
            self.exercise_configs[config.id] = config
            return True
        except IOError as e:
            print(f"Erreur lors de la sauvegarde de {filename}: {str(e)}")
            return db_success  # Au moins retourner vrai si la BD a été mise à jour
    
    def save_assessment_config(self, config):
        """
        Sauvegarde une configuration d'évaluation dans la base de données et dans un fichier.
        
        Args:
            config (AssessmentConfig): Configuration à sauvegarder.
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon.
        """
        if not config.id:
            return False
        
        # Mise à jour du total des points avant sauvegarde
        config.update_max_points()
        
        # Sauvegarder dans la base de données
        db_success = self.db_manager.add_assessment_config(config.to_dict())
        
        # Sauvegarder dans un fichier JSON (pour compatibilité)
        filename = f"{config.id}.json"
        filepath = os.path.join(self.assessments_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Mettre à jour le cache
            self.assessment_configs[config.id] = config
            return True
        except IOError as e:
            print(f"Erreur lors de la sauvegarde de {filename}: {str(e)}")
            return db_success  # Au moins retourner vrai si la BD a été mise à jour
    
    def delete_exercise_config(self, exercise_id):
        """
        Supprime une configuration d'exercice de la base de données et du système de fichiers.
        
        Args:
            exercise_id (str): Identifiant de l'exercice à supprimer.
            
        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        if exercise_id not in self.exercise_configs:
            return False
        
        # Supprimer de la base de données
        db_success = self.db_manager.delete_exercise_config(exercise_id)
        
        # Supprimer du système de fichiers
        filename = f"{exercise_id}.json"
        filepath = os.path.join(self.configs_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Supprimer du cache
            del self.exercise_configs[exercise_id]
            return True
        except IOError as e:
            print(f"Erreur lors de la suppression de {filename}: {str(e)}")
            return db_success  # Au moins retourner vrai si la BD a été mise à jour
    
    def delete_assessment_config(self, assessment_id):
        """
        Supprime une configuration d'évaluation de la base de données et du système de fichiers.
        
        Args:
            assessment_id (str): Identifiant de l'évaluation à supprimer.
            
        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        if assessment_id not in self.assessment_configs:
            return False
        
        # Supprimer de la base de données
        db_success = self.db_manager.delete_assessment_config(assessment_id)
        
        # Supprimer du système de fichiers
        filename = f"{assessment_id}.json"
        filepath = os.path.join(self.assessments_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Supprimer du cache
            del self.assessment_configs[assessment_id]
            return True
        except IOError as e:
            print(f"Erreur lors de la suppression de {filename}: {str(e)}")
            return db_success  # Au moins retourner vrai si la BD a été mise à jour
    
    def create_empty_exercise_config(self, exercise_id):
        """
        Crée une configuration d'exercice vide avec l'ID spécifié.
        
        Args:
            exercise_id (str): Identifiant de l'exercice.
            
        Returns:
            ExerciseConfig: Configuration d'exercice vide.
        """
        config_dict = {
            'id': exercise_id,
            'name': f'Nouvel exercice {exercise_id}',
            'description': '',
            'testInputs': [],
            'rules': {
                'requiredMethods': [],
                'allowedOperators': [],
                'requiredControlStructures': [],
                'customPatterns': []
            },
            'grading_criteria': []
        }
        
        config = ExerciseConfig(config_dict)
        self.exercise_configs[exercise_id] = config
        
        # Sauvegarder la nouvelle configuration
        self.save_exercise_config(config)
        
        return config
    
    def create_empty_assessment_config(self, assessment_id):
        """
        Crée une configuration d'évaluation vide avec l'ID spécifié.
        
        Args:
            assessment_id (str): Identifiant de l'évaluation.
            
        Returns:
            AssessmentConfig: Configuration d'évaluation vide.
        """
        config_dict = {
            'assessmentId': assessment_id,
            'name': f'Nouvelle évaluation {assessment_id}',
            'exercises': [],
            'totalMaxPoints': 0
        }
        
        config = AssessmentConfig(config_dict)
        self.assessment_configs[assessment_id] = config
        
        # Sauvegarder la nouvelle configuration
        self.save_assessment_config(config)
        
        return config
        
    def import_configs_to_database(self):
        """
        Importe toutes les configurations depuis les fichiers JSON vers la base de données.
        
        Returns:
            tuple: (nombre d'exercices importés, nombre d'évaluations importées)
        """
        exercise_count = 0
        assessment_count = 0
        
        # Importer les configurations d'exercices
        if os.path.exists(self.configs_dir):
            for filename in os.listdir(self.configs_dir):
                if filename.endswith('.json'):
                    try:
                        filepath = os.path.join(self.configs_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            config_dict = json.load(f)
                            if 'id' in config_dict:
                                if self.db_manager.add_exercise_config(config_dict):
                                    exercise_count += 1
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Erreur lors de l'importation de {filename}: {str(e)}")
        
        # Importer les configurations d'évaluations
        if os.path.exists(self.assessments_dir):
            for filename in os.listdir(self.assessments_dir):
                if filename.endswith('.json'):
                    try:
                        filepath = os.path.join(self.assessments_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            config_dict = json.load(f)
                            if 'assessmentId' in config_dict:
                                if self.db_manager.add_assessment_config(config_dict):
                                    assessment_count += 1
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Erreur lors de l'importation de {filename}: {str(e)}")
        
        # Recharger les configurations
        self.load_all_configs()
        
        return exercise_count, assessment_count 