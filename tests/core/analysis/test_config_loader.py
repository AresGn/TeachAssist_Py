import os
import json
import pytest
import tempfile
import shutil
from teach_assit.core.analysis.config_loader import ConfigLoader
from teach_assit.core.analysis.models import ExerciseConfig, AssessmentConfig


class TestConfigLoader:
    """Tests pour le chargeur de configuration."""
    
    @pytest.fixture
    def setup_temp_directory(self):
        """Créer un répertoire temporaire pour les tests."""
        temp_dir = tempfile.mkdtemp()
        
        # Créer les sous-répertoires
        configs_dir = os.path.join(temp_dir, 'configs')
        assessments_dir = os.path.join(temp_dir, 'assessments')
        os.makedirs(configs_dir, exist_ok=True)
        os.makedirs(assessments_dir, exist_ok=True)
        
        yield temp_dir
        
        # Nettoyage
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def create_test_configs(self, setup_temp_directory):
        """Créer des fichiers de configuration de test."""
        temp_dir = setup_temp_directory
        configs_dir = os.path.join(temp_dir, 'configs')
        assessments_dir = os.path.join(temp_dir, 'assessments')
        
        # Créer un fichier de configuration d'exercice
        exercise_config = {
            'id': 'test-exercise',
            'name': 'Exercice de test',
            'description': 'Description de l\'exercice de test',
            'rules': {
                'requiredMethods': [
                    {'name': 'testMethod', 'params': ['int'], 'returnType': 'void'}
                ],
                'allowedOperators': ['+', '-'],
                'requiredControlStructures': ['if', 'for'],
                'checkVariableScope': True,
                'customPatterns': [
                    {'pattern': 'for\\s*\\(.*\\)', 'description': 'Boucle for', 'required': True}
                ]
            }
        }
        
        with open(os.path.join(configs_dir, 'test-exercise.json'), 'w', encoding='utf-8') as f:
            json.dump(exercise_config, f, indent=2)
        
        # Créer un fichier de configuration d'évaluation
        assessment_config = {
            'assessmentId': 'test-assessment',
            'name': 'Évaluation de test',
            'exercises': [
                {'exerciseId': 'test-exercise', 'maxPoints': 10}
            ],
            'totalMaxPoints': 10
        }
        
        with open(os.path.join(assessments_dir, 'test-assessment.json'), 'w', encoding='utf-8') as f:
            json.dump(assessment_config, f, indent=2)
        
        # Créer un fichier JSON invalide
        with open(os.path.join(configs_dir, 'invalid.json'), 'w', encoding='utf-8') as f:
            f.write('{This is not valid JSON')
        
        return temp_dir
    
    def test_load_exercise_configs(self, create_test_configs):
        """Tester le chargement des configurations d'exercices."""
        temp_dir = create_test_configs
        loader = ConfigLoader(temp_dir)
        
        count = loader.load_exercise_configs()
        assert count == 1  # Le fichier invalide ne doit pas être compté
        
        configs = loader.get_all_exercise_configs()
        assert 'test-exercise' in configs
        
        config = configs['test-exercise']
        assert config.id == 'test-exercise'
        assert config.name == 'Exercice de test'
        assert config.get_required_methods()[0]['name'] == 'testMethod'
        assert config.get_allowed_operators() == ['+', '-']
        assert config.get_required_control_structures() == ['if', 'for']
        assert config.should_check_variable_scope() is True
        assert config.get_custom_patterns()[0]['description'] == 'Boucle for'
    
    def test_load_assessment_configs(self, create_test_configs):
        """Tester le chargement des configurations d'évaluations."""
        temp_dir = create_test_configs
        loader = ConfigLoader(temp_dir)
        
        count = loader.load_assessment_configs()
        assert count == 1
        
        configs = loader.get_all_assessment_configs()
        assert 'test-assessment' in configs
        
        config = configs['test-assessment']
        assert config.id == 'test-assessment'
        assert config.name == 'Évaluation de test'
        assert len(config.exercises) == 1
        assert config.exercises[0]['exerciseId'] == 'test-exercise'
        assert config.exercises[0]['maxPoints'] == 10
        assert config.total_max_points == 10
    
    def test_load_all_configs(self, create_test_configs):
        """Tester le chargement de toutes les configurations."""
        temp_dir = create_test_configs
        loader = ConfigLoader(temp_dir)
        
        exercise_count, assessment_count = loader.load_all_configs()
        assert exercise_count == 1
        assert assessment_count == 1
    
    def test_save_exercise_config(self, setup_temp_directory):
        """Tester la sauvegarde d'une configuration d'exercice."""
        temp_dir = setup_temp_directory
        loader = ConfigLoader(temp_dir)
        
        # Créer une configuration
        config = ExerciseConfig()
        config.id = 'new-exercise'
        config.name = 'Nouvel exercice'
        config.description = 'Description du nouvel exercice'
        config.rules = {
            'requiredMethods': [{'name': 'newMethod', 'params': ['String'], 'returnType': 'boolean'}]
        }
        
        # Sauvegarder
        result = loader.save_exercise_config(config)
        assert result is True
        
        # Vérifier que le fichier a été créé
        file_path = os.path.join(temp_dir, 'configs', 'new-exercise.json')
        assert os.path.exists(file_path)
        
        # Vérifier le contenu du fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
            assert saved_config['id'] == 'new-exercise'
            assert saved_config['name'] == 'Nouvel exercice'
    
    def test_save_assessment_config(self, setup_temp_directory):
        """Tester la sauvegarde d'une configuration d'évaluation."""
        temp_dir = setup_temp_directory
        loader = ConfigLoader(temp_dir)
        
        # Créer une configuration
        config = AssessmentConfig()
        config.id = 'new-assessment'
        config.name = 'Nouvelle évaluation'
        config.exercises = [{'exerciseId': 'ex1', 'maxPoints': 5}, {'exerciseId': 'ex2', 'maxPoints': 5}]
        
        # Sauvegarder
        result = loader.save_assessment_config(config)
        assert result is True
        
        # Vérifier que le fichier a été créé
        file_path = os.path.join(temp_dir, 'assessments', 'new-assessment.json')
        assert os.path.exists(file_path)
        
        # Vérifier le contenu du fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
            assert saved_config['assessmentId'] == 'new-assessment'
            assert saved_config['name'] == 'Nouvelle évaluation'
            assert saved_config['totalMaxPoints'] == 10  # 5 + 5
    
    def test_delete_configs(self, create_test_configs):
        """Tester la suppression des configurations."""
        temp_dir = create_test_configs
        loader = ConfigLoader(temp_dir)
        loader.load_all_configs()
        
        # Supprimer la configuration d'exercice
        result = loader.delete_exercise_config('test-exercise')
        assert result is True
        
        # Vérifier que le fichier a été supprimé
        file_path = os.path.join(temp_dir, 'configs', 'test-exercise.json')
        assert not os.path.exists(file_path)
        
        # Supprimer la configuration d'évaluation
        result = loader.delete_assessment_config('test-assessment')
        assert result is True
        
        # Vérifier que le fichier a été supprimé
        file_path = os.path.join(temp_dir, 'assessments', 'test-assessment.json')
        assert not os.path.exists(file_path) 