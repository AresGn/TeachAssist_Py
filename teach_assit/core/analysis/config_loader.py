import os
import json
from teach_assit.core.analysis.models import ExerciseConfig, AssessmentConfig


class ConfigLoader:
    """Chargeur de configurations JSON pour les exercices et les évaluations."""
    
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
    
    def load_all_configs(self):
        """
        Charge toutes les configurations disponibles.
        
        Returns:
            tuple: (nombre d'exercices chargés, nombre d'évaluations chargées)
        """
        exercise_count = self.load_exercise_configs()
        assessment_count = self.load_assessment_configs()
        return exercise_count, assessment_count
    
    def load_exercise_configs(self):
        """
        Charge toutes les configurations d'exercices.
        
        Returns:
            int: Nombre de configurations chargées.
        """
        self.exercise_configs = {}
        count = 0
        
        if not os.path.exists(self.configs_dir):
            return 0
        
        for filename in os.listdir(self.configs_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.configs_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config_dict = json.load(f)
                        if 'id' in config_dict:
                            config = ExerciseConfig(config_dict)
                            self.exercise_configs[config.id] = config
                            count += 1
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Erreur lors du chargement de {filename}: {str(e)}")
        
        return count
    
    def load_assessment_configs(self):
        """
        Charge toutes les configurations d'évaluations.
        
        Returns:
            int: Nombre de configurations chargées.
        """
        self.assessment_configs = {}
        count = 0
        
        if not os.path.exists(self.assessments_dir):
            return 0
        
        for filename in os.listdir(self.assessments_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.assessments_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config_dict = json.load(f)
                        if 'assessmentId' in config_dict:
                            config = AssessmentConfig(config_dict)
                            self.assessment_configs[config.id] = config
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
        return self.exercise_configs.get(exercise_id)
    
    def get_assessment_config(self, assessment_id):
        """
        Récupère une configuration d'évaluation par son identifiant.
        
        Args:
            assessment_id (str): Identifiant de l'évaluation.
            
        Returns:
            AssessmentConfig: Configuration de l'évaluation, None si non trouvée.
        """
        return self.assessment_configs.get(assessment_id)
    
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
        Sauvegarde une configuration d'exercice.
        
        Args:
            config (ExerciseConfig): Configuration à sauvegarder.
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon.
        """
        if not config.id:
            return False
        
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
            return False
    
    def save_assessment_config(self, config):
        """
        Sauvegarde une configuration d'évaluation.
        
        Args:
            config (AssessmentConfig): Configuration à sauvegarder.
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon.
        """
        if not config.id:
            return False
        
        filename = f"{config.id}.json"
        filepath = os.path.join(self.assessments_dir, filename)
        
        try:
            # Mise à jour du total des points avant sauvegarde
            config.update_max_points()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Mettre à jour le cache
            self.assessment_configs[config.id] = config
            return True
        except IOError as e:
            print(f"Erreur lors de la sauvegarde de {filename}: {str(e)}")
            return False
    
    def delete_exercise_config(self, exercise_id):
        """
        Supprime une configuration d'exercice.
        
        Args:
            exercise_id (str): Identifiant de l'exercice à supprimer.
            
        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        if exercise_id not in self.exercise_configs:
            return False
        
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
            return False
    
    def delete_assessment_config(self, assessment_id):
        """
        Supprime une configuration d'évaluation.
        
        Args:
            assessment_id (str): Identifiant de l'évaluation à supprimer.
            
        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        if assessment_id not in self.assessment_configs:
            return False
        
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
            return False
    
    def create_empty_exercise_config(self, exercise_id):
        """
        Crée une configuration d'exercice vide avec l'ID spécifié.
        
        Args:
            exercise_id (str): Identifiant de l'exercice.
            
        Returns:
            ExerciseConfig: Configuration vide de l'exercice.
        """
        # Création d'un dictionnaire avec les valeurs par défaut
        config_dict = {
            'id': exercise_id,
            'name': f'Exercice {exercise_id}',
            'description': '',
            'rules': {
                'requiredMethods': [],
                'allowedOperators': [],
                'requiredControlStructures': [],
                'customPatterns': [],
                'checkVariableScope': False,
                'checkNamingConventions': []
            }
        }
        
        # Création de l'objet de configuration
        config = ExerciseConfig(config_dict)
        
        # Ajout au cache
        self.exercise_configs[exercise_id] = config
        
        # Sauvegarde de la configuration
        self.save_exercise_config(config)
        
        return config
    
    def create_empty_assessment_config(self, assessment_id):
        """
        Crée une configuration d'évaluation vide avec l'ID spécifié.
        
        Args:
            assessment_id (str): Identifiant de l'évaluation.
            
        Returns:
            AssessmentConfig: Configuration vide de l'évaluation.
        """
        # Création d'un dictionnaire avec les valeurs par défaut
        config_dict = {
            'assessmentId': assessment_id,
            'name': f'Évaluation {assessment_id}',
            'exercises': [],
            'totalMaxPoints': 0
        }
        
        # Création de l'objet de configuration
        config = AssessmentConfig(config_dict)
        
        # Ajout au cacheE
        self.assessment_configs[assessment_id] = config
        
        # Sauvegarde de la configuration
        self.save_assessment_config(config)
        
        return config 