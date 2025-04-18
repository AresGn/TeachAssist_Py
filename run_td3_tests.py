import os
import sys
import json
import glob

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import from teach_assit modules
from teach_assit.core.analysis.static_analyzer import StaticAnalyzer
from teach_assit.core.analysis.models import ExerciseConfig

# Symboles ASCII pour le rapport
SYMBOL_OK = "[OK]"
SYMBOL_FAIL = "[FAIL]"
SYMBOL_WARNING = "[WARN]"

def analyze_td3_files():
    """Analyze the Java files in TD3 directory using the TD3.json configuration"""
    print("\nAnalyzing TD3 Java files...")
    
    # Ouvrir un fichier pour écrire les résultats
    with open('analysis_results_td3.txt', 'w', encoding='utf-8') as out_file:
        # Load TD3 configuration
        td3_config_path = os.path.join('assessments', 'TD3.json')
        with open(td3_config_path, 'r', encoding='utf-8') as f:
            td3_config = json.load(f)
        
        # Initialize analyzer
        analyzer = StaticAnalyzer()
        
        # Analyze each exercise in TD3
        for exercise in td3_config['exercises']:
            exercise_id = exercise['exerciseId']
            
            # Load exercise config
            exercise_config_path = os.path.join('configs', f'{exercise_id}.json')
            with open(exercise_config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            config = ExerciseConfig(config_dict)
            
            # Get all Java files for this exercise
            java_files = glob.glob(f'tests/java_samples/TD3/**/{exercise_id}.java', recursive=True)
            
            if not java_files:
                msg = f"No Java files found for exercise {exercise_id}"
                print(msg)
                out_file.write(msg + '\n')
                continue
            
            msg = f"\n{'='*20} EXERCICE: {config.name} (ID: {exercise_id}) {'='*20}"
            print(msg)
            out_file.write(msg + '\n')
            msg = f"Found {len(java_files)} Java files to analyze:"
            print(msg)
            out_file.write(msg + '\n')
            
            # Analyze each file
            for file in java_files:
                student_name = os.path.basename(os.path.dirname(file))
                msg = f"\n{'='*50}\n{SYMBOL_OK} RAPPORT D'ANALYSE: {file} (Étudiant: {student_name})\n{'='*50}"
                print(msg)
                out_file.write(msg + '\n')
                
                # Read the Java code
                with open(file, 'r', encoding='utf-8') as f:
                    java_code = f.read()
                
                # Analyze the code
                result = analyzer.analyze_code(java_code, config)
                
                # --- Rapport de syntaxe ---
                syntax_status = SYMBOL_OK if result['is_valid'] else SYMBOL_FAIL
                msg = f"\n{syntax_status} SYNTAXE: " + ("Code valide" if result['is_valid'] else "Code invalide")
                print(msg)
                out_file.write(msg + '\n')
                
                if result['syntax_errors']:
                    for error in result['syntax_errors']:
                        error_msg = error.get('message', 'Erreur inconnue')
                        msg = f"  {SYMBOL_FAIL} Ligne {error.get('line', 'inconnue')}: {error_msg}"
                        print(msg)
                        out_file.write(msg + '\n')
                
                # --- Rapport des méthodes requises ---
                required_methods = config.get_required_methods()
                methods_status = SYMBOL_OK if not result['missing_methods'] else SYMBOL_FAIL
                        
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
                
                # --- Rapport sur les structures de contrôle ---
                if 'control_structures' in result['analysis_details']:
                    control_status = SYMBOL_OK if not result['analysis_details']['control_structures'].get('missing', []) else SYMBOL_FAIL
                    
                    msg = f"\n{control_status} STRUCTURES DE CONTRÔLE:"
                    print(msg)
                    out_file.write(msg + '\n')
                    
                    # Structures trouvées
                    found_structures = result['analysis_details']['control_structures'].get('found', [])
                    if found_structures:
                        msg = f"  {SYMBOL_OK} Structures trouvées: {', '.join(found_structures)}"
                        print(msg)
                        out_file.write(msg + '\n')
                    
                    # Structures manquantes
                    missing_structures = result['analysis_details']['control_structures'].get('missing', [])
                    if missing_structures:
                        msg = f"  {SYMBOL_FAIL} Structures manquantes: {', '.join(missing_structures)}"
                        print(msg)
                        out_file.write(msg + '\n')
                
                # --- Rapport sur les conventions de nommage ---
                if 'naming_conventions' in result['analysis_details']:
                    naming_errors = result['analysis_details']['naming_conventions'].get('errors', [])
                    naming_status = SYMBOL_OK if not naming_errors else SYMBOL_FAIL
                    
                    msg = f"\n{naming_status} CONVENTIONS DE NOMMAGE:"
                    print(msg)
                    out_file.write(msg + '\n')
                    
                    # Erreurs de convention
                    if naming_errors:
                        for error in naming_errors:
                            msg = f"  {SYMBOL_FAIL} {error.get('message', '')}"
                            print(msg)
                            out_file.write(msg + '\n')
                    else:
                        msg = f"  {SYMBOL_OK} Toutes les conventions de nommage sont respectées."
                        print(msg)
                        out_file.write(msg + '\n')
                
                # --- Rapport sur la portée des variables ---
                if 'variable_scopes' in result['analysis_details']:
                    scope_errors = result['analysis_details']['variable_scopes'].get('errors', [])
                    scope_status = SYMBOL_OK if not scope_errors else SYMBOL_FAIL
                    
                    msg = f"\n{scope_status} PORTÉE DES VARIABLES:"
                    print(msg)
                    out_file.write(msg + '\n')
                    
                    # Erreurs de portée
                    if scope_errors:
                        for error in scope_errors:
                            msg = f"  {SYMBOL_FAIL} {error.get('message', '')}"
                            print(msg)
                            out_file.write(msg + '\n')
                    else:
                        msg = f"  {SYMBOL_OK} Aucun problème de portée de variables détecté."
                        print(msg)
                        out_file.write(msg + '\n')
                
                # --- Vérifier l'utilisation d'opérateurs non autorisés ---
                if 'disallowed_operators' in result['analysis_details']:
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
                    else:
                        msg = f"\n{SYMBOL_OK} OPÉRATEURS: Tous les opérateurs utilisés sont autorisés."
                        print(msg)
                        out_file.write(msg + '\n')
                
                # --- Rapport des patterns requis ---
                custom_patterns = config.get_custom_patterns()
                missing_patterns = result['analysis_details'].get('missing_patterns', [])
                
                msg = f"\n{SYMBOL_OK if not missing_patterns else SYMBOL_FAIL} PATTERNS REQUIS:"
                print(msg)
                out_file.write(msg + '\n')
                
                # Vérifier chaque pattern
                for pattern_info in custom_patterns:
                    pattern_desc = pattern_info.get('description', 'Pattern sans description')
                    required = pattern_info.get('required', False)
                    
                    if not required:
                        continue  # Ignorer les patterns non requis
                    
                    # Vérifier si le pattern est manquant
                    is_missing = False
                    error_msg = ""
                    for missing_pattern in missing_patterns:
                        missing_desc = missing_pattern.get('description', '')
                        if missing_desc == pattern_desc:
                            is_missing = True
                            error_msg = missing_pattern.get('errorMessage', '')
                            break
                    
                    status = SYMBOL_OK if not is_missing else SYMBOL_FAIL
                    msg = f"  {status} {pattern_desc}"
                    if is_missing and error_msg:
                        msg += f"\n      {SYMBOL_WARNING} {error_msg}"
                    
                    print(msg)
                    out_file.write(msg + '\n')
                
                # --- Suggestions ---
                if result['analysis_details']['suggestions']:
                    msg = f"\n{SYMBOL_WARNING} SUGGESTIONS D'AMÉLIORATION:"
                    print(msg)
                    out_file.write(msg + '\n')
                    
                    for suggestion in result['analysis_details']['suggestions']:
                        msg = f"  {SYMBOL_WARNING} {suggestion}"
                        print(msg)
                        out_file.write(msg + '\n')
                
                # --- Résumé global ---
                syntax_ok = result['is_valid']
                methods_ok = len(result['missing_methods']) == 0
                patterns_ok = len(missing_patterns) == 0
                
                # Opérateurs
                operators_ok = True
                if 'disallowed_operators' in result['analysis_details']:
                    operators_ok = not result['analysis_details']['disallowed_operators']
                
                # Structures de contrôle
                control_structures_ok = True
                if 'control_structures' in result['analysis_details']:
                    control_structures_ok = not result['analysis_details']['control_structures'].get('missing', [])
                
                # Conventions de nommage
                naming_ok = True
                if 'naming_conventions' in result['analysis_details']:
                    naming_ok = not result['analysis_details']['naming_conventions'].get('errors', [])
                
                # Portée des variables
                scope_ok = True
                if 'variable_scopes' in result['analysis_details']:
                    scope_ok = not result['analysis_details']['variable_scopes'].get('errors', [])
                
                # Note globale basée sur les vérifications
                checks = [syntax_ok, methods_ok, patterns_ok, operators_ok, control_structures_ok, naming_ok, scope_ok]
                success_count = sum(1 for check in checks if check)
                grade = (success_count / len(checks)) * exercise['maxPoints']
                
                msg = f"\n{'='*30}\nRÉSUMÉ GLOBAL: {success_count}/{len(checks)} vérifications réussies\n"
                msg += f"NOTE ESTIMÉE: {grade:.1f}/{exercise['maxPoints']} points"
                print(msg)
                out_file.write(msg + '\n')

def main():
    # Run the analysis
    analyze_td3_files()
    
    print("\nAnalyse terminée. Résultats disponibles dans analysis_results_td3.txt")

if __name__ == "__main__":
    main() 