#!/usr/bin/env python3
"""
Démo d'utilisation de l'analyseur statique avec des fichiers Java réels.
Ce script montre comment analyser des fichiers Java existants
par rapport à une configuration d'exercice.
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
    
    # Répertoire des fichiers Java d'exemple
    java_samples_dir = os.path.join(base_dir, 'tests', 'java_samples')
    
    # Vérifier que le répertoire existe
    if not os.path.exists(java_samples_dir):
        print(f"Répertoire des exemples Java non trouvé: {java_samples_dir}")
        return
    
    # Liste des fichiers Java à analyser
    java_files = [
        "ValidationCorrect.java",
        "ValidationSyntaxError.java",
        "ValidationMissingMethod.java",
        "ValidationWrongSignature.java"
    ]
    
    # Analyseur statique
    analyzer = StaticAnalyzer()
    
    # Analyse de chaque fichier
    for java_file in java_files:
        filepath = os.path.join(java_samples_dir, java_file)
        
        # Vérifier que le fichier existe
        if not os.path.exists(filepath):
            print(f"\n⚠️ Fichier non trouvé: {java_file}")
            continue
        
        print(f"\n\n{'='*50}")
        print(f"Analyse de {java_file}")
        print(f"{'='*50}")
        
        # Lecture du contenu du fichier
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
                
            # Analyse du code
            result = analyzer.analyze_code(code, exercise_config)
            print_analysis_result(result)
            
        except Exception as e:
            print(f"Erreur lors de la lecture/analyse de {java_file}: {str(e)}")


def print_analysis_result(result):
    """Affiche les résultats de l'analyse de façon formatée."""
    print(f"\nCode syntaxiquement valide: {result['is_valid']}")
    
    if result['syntax_errors']:
        print("\nErreurs de syntaxe:")
        for error in result['syntax_errors']:
            print(f"  - Ligne {error['line']}: {error['message']}")
    
    if result['missing_methods']:
        print("\nMéthodes manquantes ou incorrectes:")
        for method in result['missing_methods']:
            params = ", ".join(method['expected_params'])
            print(f"  - {method['expected_return']} {method['name']}({params})")
    
    if 'found_methods' in result['analysis_details']:
        print("\nMéthodes trouvées:")
        for method_name, method_details in result['analysis_details']['found_methods'].items():
            for i, detail in enumerate(method_details):
                params = ", ".join(detail['params'])
                return_type = detail['return']
                print(f"  - {return_type} {method_name}({params})")
    
    if not result['syntax_errors'] and not result['missing_methods']:
        print("\n✅ Le code respecte les exigences de l'exercice!")
    else:
        print("\n❌ Le code ne respecte pas les exigences de l'exercice!")


if __name__ == "__main__":
    main() 