import unittest
import os
import sys
import json

# Ajout du répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from teach_assit.core.analysis.static_analyzer import StaticAnalyzer
from teach_assit.core.analysis.models import ExerciseConfig


class TestStaticAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur statique de code Java."""

    def setUp(self):
        """Initialisation avant chaque test."""
        self.analyzer = StaticAnalyzer()
        
        # Exemple de configuration pour le test de validation d'âge
        self.config_dict = {
            "id": "test-validation-age",
            "name": "Test Validation d'Âge",
            "description": "Test pour l'analyseur statique",
            "rules": {
                "requiredMethods": [
                    {
                        "name": "estMajeur",
                        "params": ["int"],
                        "returnType": "boolean"
                    }
                ]
            }
        }
        self.config = ExerciseConfig(self.config_dict)
        
        # Code Java valide avec la méthode requise
        self.valid_code = """
        public class Validation {
            public boolean estMajeur(int age) {
                return age >= 18;
            }
        }
        """
        
        # Code Java avec erreur de syntaxe
        self.syntax_error_code = """
        public class Validation {
            public boolean estMajeur(int age) {
                return age >= 18
            }
        }
        """
        
        # Code Java sans la méthode requise
        self.missing_method_code = """
        public class Validation {
            public boolean verifierAge(int age) {
                return age >= 18;
            }
        }
        """
        
        # Code Java avec signature incorrecte
        self.wrong_signature_code = """
        public class Validation {
            public void estMajeur(int age) {
                System.out.println(age >= 18);
            }
        }
        """

    def test_valid_code(self):
        """Test avec code Java valide."""
        result = self.analyzer.analyze_code(self.valid_code, self.config)
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['syntax_errors']), 0)
        self.assertEqual(len(result['missing_methods']), 0)
        self.assertIn('found_methods', result['analysis_details'])
        self.assertIn('estMajeur', result['analysis_details']['found_methods'])

    def test_syntax_error(self):
        """Test avec code Java contenant une erreur de syntaxe."""
        result = self.analyzer.analyze_code(self.syntax_error_code, self.config)
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['syntax_errors']), 0)

    def test_missing_method(self):
        """Test avec code Java sans la méthode requise."""
        result = self.analyzer.analyze_code(self.missing_method_code, self.config)
        self.assertTrue(result['is_valid'])
        self.assertGreater(len(result['missing_methods']), 0)
        self.assertEqual(result['missing_methods'][0]['name'], 'estMajeur')

    def test_wrong_signature(self):
        """Test avec code Java avec signature incorrecte."""
        result = self.analyzer.analyze_code(self.wrong_signature_code, self.config)
        self.assertTrue(result['is_valid'])
        self.assertGreater(len(result['missing_methods']), 0)
        self.assertEqual(result['missing_methods'][0]['name'], 'estMajeur')
        self.assertEqual(result['missing_methods'][0]['expected_return'], 'boolean')


if __name__ == '__main__':
    unittest.main() 