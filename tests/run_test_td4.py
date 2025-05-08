import os
import sys
import unittest
import glob
import json
import codecs
import re

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the TestStaticAnalyzer class
from tests.test_static_analyzer import TestStaticAnalyzer
from teach_assit.core.analysis.static_analyzer import StaticAnalyzer
from teach_assit.core.analysis.models import ExerciseConfig
from teach_assit.core.analysis.config_loader import ConfigLoader

# Symboles pour le rapport
SYMBOL_OK = "✅"
SYMBOL_FAIL = "❌"
SYMBOL_WARNING = "⚠️"

def fix_encoding(text):
    """Corriger l'encodage des caractères accentués"""
    if not text:
        return text
    
    # Tentatives de correction d'encodage
    try:
        # Si déjà en UTF-8 mais mal interprété
        return text.encode('latin1').decode('utf-8')
    except:
        try:
            # Si encodé en latin1
            return text.encode('latin1').decode('latin1')
        except:
            pass
    return text

def analyze_td4_files():
    """Analyze the Java files in TD4 directory using the TD4.json configuration"""
    print("\nAnalyzing TD4 Java files...")
    
    # Ouvrir un fichier pour écrire les résultats
    with open('analysis_results_td4.txt', 'w', encoding='utf-8') as out_file:
        # Initialiser le chargeur de configuration
        config_loader = ConfigLoader(os.getcwd())
        
        # S'assurer que toutes les configurations sont chargées depuis la base de données
        config_loader.load_all_configs()
        
        # Récupérer la configuration TD4 depuis la base de données
        td4_config = config_loader.get_assessment_config('TD4')
        
        if not td4_config:
            msg = "Configuration TD4 non trouvée dans la base de données"
            print(msg)
            out_file.write(msg + '\n')
            return
        
        # Obtenir les IDs des exercices à partir de la configuration TD4
        exercise_ids = [ex['exerciseId'] for ex in td4_config.exercises]
        
        if not exercise_ids:
            msg = "Aucun exercice trouvé dans la configuration TD4"
            print(msg)
            out_file.write(msg + '\n')
            return
        
        # Charger les configurations d'exercices depuis la base de données
        exercise_configs = {}
        for ex_id in exercise_ids:
            config = config_loader.get_exercise_config(ex_id)
            if config:
                exercise_configs[ex_id] = config
            else:
                msg = f"Configuration de l'exercice {ex_id} non trouvée dans la base de données"
                print(msg)
                out_file.write(msg + '\n')
        
        # Initialize analyzer
        analyzer = StaticAnalyzer()
        
        # Get all Java files in TD4 directory
        java_files = glob.glob('tests/java_samples/TD4/**/*.java', recursive=True)
        
        if not java_files:
            msg = "No Java files found in tests/java_samples/TD4/ directory"
            print(msg)
            out_file.write(msg + '\n')
            return
        
        msg = f"Found {len(java_files)} Java files to analyze:"
        print(msg)
        out_file.write(msg + '\n')
        
        # Analyze each file
        for file in java_files:
            student_name = os.path.basename(os.path.dirname(file))
            file_name = os.path.basename(file)
            
            # Déterminer l'exercice correspondant au fichier
            matching_exercise = None
            for ex_id in exercise_ids:
                if ex_id.lower() in file_name.lower() or ex_id.split('-')[-1].lower() in file_name.lower():
                    matching_exercise = ex_id
                    break
            
            if not matching_exercise:
                msg = f"\n{'='*50}\n{SYMBOL_WARNING} FICHIER IGNORÉ: {file} (Exercice non identifiable)\n{'='*50}"
                print(msg)
                out_file.write(msg + '\n')
                continue
                
            msg = f"\n{'='*50}\n{SYMBOL_OK} RAPPORT D'ANALYSE: {file} (Étudiant: {student_name}, Exercice: {matching_exercise})\n{'='*50}"
            print(msg)
            out_file.write(msg + '\n')
            
            # Read the Java code
            with open(file, 'r', encoding='utf-8') as f:
                java_code = f.read()
            
            # Get the corresponding exercise config
            config = exercise_configs[matching_exercise]
            
            # Analyze the code
            result = analyzer.analyze_code(java_code, config)
            
            # --- Rapport de syntaxe ---
            syntax_status = SYMBOL_OK if result['is_valid'] else SYMBOL_FAIL
            msg = f"\n{syntax_status} SYNTAXE: " + ("Code valide" if result['is_valid'] else "Code invalide")
            print(msg)
            out_file.write(msg + '\n')
            
            if result['syntax_errors']:
                for error in result['syntax_errors']:
                    error_msg = fix_encoding(error.get('message', 'Erreur inconnue'))
                    msg = f"  {SYMBOL_FAIL} Ligne {error.get('line', 'inconnue')}: {error_msg}"
                    print(msg)
                    out_file.write(msg + '\n')
            
            # --- Vérifier s'il y a des méthodes avec noms incorrects ---
            has_wrong_method_names = False
            if 'analysis_details' in result and 'wrong_method_names' in result['analysis_details']:
                has_wrong_method_names = len(result['analysis_details']['wrong_method_names']) > 0
            
            # --- Rapport des méthodes requises ---
            required_methods = config.get_required_methods()
            methods_status = SYMBOL_OK
            if not result['is_valid'] and has_wrong_method_names:
                methods_status = SYMBOL_FAIL
            elif result['missing_methods']:
                methods_status = SYMBOL_WARNING
                
            msg = f"\n{methods_status} MÉTHODES REQUISES:"
            print(msg)
            out_file.write(msg + '\n')
            
            # Parcourir les méthodes requises
            for req_method in required_methods:
                method_name = req_method.get('name', '')
                method_params = req_method.get('params', [])
                method_return = req_method.get('returnType', 'void')
                
                # Vérifier si la méthode est manquante
                is_missing = False
                for missing in result['missing_methods']:
                    if missing['name'] == method_name:
                        is_missing = True
                        break
                
                status = SYMBOL_OK if not is_missing else SYMBOL_FAIL
                msg = f"  {status} {method_name}({', '.join(method_params)}) -> {method_return}"
                print(msg)
                out_file.write(msg + '\n')
            
            # Si des noms de méthodes incorrects ont été détectés, les afficher
            if has_wrong_method_names:
                for wrong_method in result['analysis_details']['wrong_method_names']:
                    found_name = wrong_method.get('found_name', '')
                    expected_name = wrong_method.get('expected_name', '')
                    msg = f"  {SYMBOL_FAIL} Mauvais nom de méthode trouvé: '{found_name}' (attendu: '{expected_name}')"
                    print(msg)
                    out_file.write(msg + '\n')
            
            # --- Vérifier l'utilisation d'opérateurs non autorisés ---
            if 'analysis_details' in result and 'disallowed_operators' in result['analysis_details']:
                if result['analysis_details']['disallowed_operators']:
                    msg = f"\n{SYMBOL_FAIL} OPÉRATEURS NON AUTORISÉS:"
                    print(msg)
                    out_file.write(msg + '\n')
                    
                    for op_info in result['analysis_details']['disallowed_operators']:
                        operator = op_info.get('operator', '')
                        message = op_info.get('message', '')
                        msg = f"  {SYMBOL_FAIL} {message}"
                        print(msg)
                        out_file.write(msg + '\n')
            
            # --- Rapport des méthodes trouvées (avec signature correspondante) ---
            if 'analysis_details' in result and 'found_methods' in result['analysis_details'] and result['analysis_details']['found_methods']:
                msg = f"\n{SYMBOL_OK} MÉTHODES TROUVÉES (correspondant à la signature):"
                print(msg)
                out_file.write(msg + '\n')
                for method_name, method_list in result['analysis_details']['found_methods'].items():
                    for method in method_list:
                        msg = f"  {SYMBOL_OK} {method_name}({', '.join(method.get('params', []))}) -> {method.get('return', 'void')}"
                        print(msg)
                        out_file.write(msg + '\n')
            else:
                msg = f"\n{SYMBOL_WARNING} AUCUNE MÉTHODE TROUVÉE avec signature correspondante."
                print(msg)
                out_file.write(msg + '\n')
            
            # --- Rapport des patterns requis ---
            custom_patterns = config.get_custom_patterns()
            missing_patterns = result['analysis_details'].get('missing_patterns', [])
            
            msg = f"\n{SYMBOL_OK if not missing_patterns else SYMBOL_WARNING} PATTERNS REQUIS:"
            print(msg)
            out_file.write(msg + '\n')
            
            # Vérifier chaque pattern
            for pattern_info in custom_patterns:
                pattern_desc = fix_encoding(pattern_info.get('description', 'Pattern sans description'))
                required = pattern_info.get('required', False)
                
                if not required:
                    continue  # Ignorer les patterns non requis
                
                # Vérifier si le pattern est manquant
                is_missing = False
                error_msg = ""
                for missing_pattern in missing_patterns:
                    missing_desc = fix_encoding(missing_pattern.get('description', ''))
                    if missing_desc == pattern_desc:
                        is_missing = True
                        error_msg = fix_encoding(missing_pattern.get('errorMessage', ''))
                        break
                
                status = SYMBOL_OK if not is_missing else SYMBOL_FAIL
                msg = f"  {status} {pattern_desc}"
                if is_missing and error_msg:
                    msg += f"\n      {SYMBOL_WARNING} {error_msg}"
                
                print(msg)
                out_file.write(msg + '\n')
            
            # --- Vérifier les structures de contrôle requises ---
            if 'analysis_details' in result and 'control_structures' in result['analysis_details']:
                control_structures = result['analysis_details']['control_structures']
                missing_structures = control_structures.get('missing', [])
                found_structures = control_structures.get('found', [])
                
                structures_status = SYMBOL_OK if not missing_structures else SYMBOL_FAIL
                msg = f"\n{structures_status} STRUCTURES DE CONTRÔLE REQUISES:"
                print(msg)
                out_file.write(msg + '\n')
                
                if found_structures:
                    msg = f"  {SYMBOL_OK} Structures trouvées: {', '.join(found_structures)}"
                    print(msg)
                    out_file.write(msg + '\n')
                
                if missing_structures:
                    msg = f"  {SYMBOL_FAIL} Structures manquantes: {', '.join(missing_structures)}"
                    print(msg)
                    out_file.write(msg + '\n')
            
            # --- Résumé global ---
            syntax_ok = result['is_valid']
            methods_ok = len(result['missing_methods']) == 0 and not has_wrong_method_names
            patterns_ok = len(missing_patterns) == 0
            operators_ok = not ('disallowed_operators' in result['analysis_details'] and result['analysis_details']['disallowed_operators'])
            structures_ok = not ('control_structures' in result['analysis_details'] and result['analysis_details']['control_structures'].get('missing', []))
            
            global_status = SYMBOL_OK if (syntax_ok and methods_ok and patterns_ok and operators_ok and structures_ok) else SYMBOL_FAIL
            
            msg = f"\n{global_status} RÉSULTAT GLOBAL: " + ("SUCCÈS" if (syntax_ok and methods_ok and patterns_ok and operators_ok and structures_ok) else "DES PROBLÈMES ONT ÉTÉ DÉTECTÉS")
            print(msg)
            out_file.write(msg + '\n')
            
            # Détail des problèmes s'il y en a
            if not (syntax_ok and methods_ok and patterns_ok and operators_ok and structures_ok):
                msg = "  Détail des problèmes:"
                print(msg)
                out_file.write(msg + '\n')
                
                if not syntax_ok:
                    msg = f"    {SYMBOL_FAIL} Problèmes de syntaxe"
                    print(msg)
                    out_file.write(msg + '\n')
                
                if not methods_ok:
                    if has_wrong_method_names:
                        msg = f"    {SYMBOL_FAIL} Noms de méthodes incorrects"
                        print(msg)
                        out_file.write(msg + '\n')
                    else:
                        msg = f"    {SYMBOL_FAIL} Méthodes requises manquantes"
                        print(msg)
                        out_file.write(msg + '\n')
                
                if not patterns_ok:
                    msg = f"    {SYMBOL_FAIL} Patterns requis manquants"
                    print(msg)
                    out_file.write(msg + '\n')
                
                if not operators_ok:
                    msg = f"    {SYMBOL_FAIL} Utilisation d'opérateurs non autorisés"
                    print(msg)
                    out_file.write(msg + '\n')
                
                if not structures_ok:
                    msg = f"    {SYMBOL_FAIL} Structures de contrôle requises manquantes"
                    print(msg)
                    out_file.write(msg + '\n')
        
        print("\nAnalysis complete. Results saved to analysis_results_td4.txt")
                
def main():
    """Main function to run tests"""
    # Analyze TD4 files
    analyze_td4_files()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 