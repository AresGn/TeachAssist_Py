#!/usr/bin/env python3
"""
Démo d'utilisation de l'analyseur statique.
Ce script montre comment utiliser l'analyseur statique pour vérifier
la structure d'un code Java par rapport à une configuration d'exercice.
"""

import os
import sys
import json

# Assurez-vous que le package teach_assit est dans le path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from teach_assit.core.analysis import StaticAnalyzer, ConfigLoader, ExerciseConfig


def main():
    """Fonction principale de démonstration."""
    # Initialisation du chargeur de configuration
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_loader = ConfigLoader(base_dir)
    
    # Charger toutes les configurations
    n_exercises, n_assessments = config_loader.load_all_configs()
    print(f"Configurations chargées: {n_exercises} exercices, {n_assessments} évaluations")
    
    # Exemple: chargement de la configuration pour l'exercice de validation d'âge
    exercise_id = "06-validation-age"
    exercise_config = config_loader.get_exercise_config(exercise_id)
    
    if not exercise_config:
        print(f"Configuration d'exercice '{exercise_id}' non trouvée")
        return
    
    print(f"\nExercice: {exercise_config.name}")
    print(f"Description: {exercise_config.description}")
    print("\nMéthodes requises:")
    for method in exercise_config.get_required_methods():
        params = ", ".join(method.get('params', []))
        return_type = method.get('returnType', 'void')
        print(f"  - {return_type} {method.get('name', '')}({params})")
    
    # Exemple de code Java correct
    valid_code = """
    public class Validation {
        public boolean estMajeur(int age) {
            return age >= 18;
        }
    }
    """
    
    # Exemple de code Java avec erreur de syntaxe
    syntax_error_code = """
    public class Validation {
        public boolean estMajeur(int age) {
            return age >= 18
        }
    }
    """
    
    # Exemple de code Java sans la méthode requise
    missing_method_code = """
    public class Validation {
        public boolean verifierAge(int age) {
            return age >= 18;
        }
    }
    """
    
    # Analyse du code
    analyzer = StaticAnalyzer()
    
    print("\n=== Analyse du code correct ===")
    result = analyzer.analyze_code(valid_code, exercise_config)
    print_analysis_result(result)
    
    print("\n=== Analyse du code avec erreur de syntaxe ===")
    result = analyzer.analyze_code(syntax_error_code, exercise_config)
    print_analysis_result(result)
    
    print("\n=== Analyse du code sans la méthode requise ===")
    result = analyzer.analyze_code(missing_method_code, exercise_config)
    print_analysis_result(result)


def print_analysis_result(result):
    """Affiche les résultats de l'analyse de façon formatée."""
    print(f"Code valide: {result['is_valid']}")
    
    if result['syntax_errors']:
        print("\nErreurs de syntaxe:")
        for error in result['syntax_errors']:
            print(f"  - Ligne {error['line']}: {error['message']}")
    
    if result['missing_methods']:
        print("\nMéthodes manquantes:")
        for method in result['missing_methods']:
            params = ", ".join(method['expected_params'])
            print(f"  - {method['expected_return']} {method['name']}({params})")
    
    if not result['syntax_errors'] and not result['missing_methods']:
        print("  => Le code respecte les exigences de l'exercice!")


if __name__ == "__main__":
    main() 