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

def detect_wrong_method_names(code, expected_method_name):
    """
    Analyser le code brut pour détecter les méthodes avec un nom différent de celui attendu
    Cette fonction utilise une regex simple pour trouver les déclarations de méthodes
    """
    # Regex pour détecter les déclarations de méthodes
    method_pattern = r'public\s+static\s+double\s+(\w+)\s*\(\s*int\s+\w+\s*,\s*int\s+\w+\s*,\s*int\s+\w+\s*\)'
    matches = re.findall(method_pattern, code)
    
    wrong_methods = []
    for method_name in matches:
        if method_name != expected_method_name:
            wrong_methods.append(method_name)
    
    return wrong_methods

def run_unit_tests():
    """Run the standard unit tests defined in test_static_analyzer.py"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStaticAnalyzer)
    
    print("Running StaticAnalyzer unit tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    return result.wasSuccessful()

def analyze_td2_files():
    """Analyze the Java files in TD2 directory using the TD2.json configuration"""
    print("\nAnalyzing TD2 Java files...")
    
    # Ouvrir un fichier pour écrire les résultats
    with open('analysis_results_td2.txt', 'w', encoding='utf-8') as out_file:
        # Load TD2 configuration
        td2_config_path = os.path.join('assessments', 'TD2.json')
        with open(td2_config_path, 'r', encoding='utf-8') as f:
            td2_config = json.load(f)
        
        # Find exercise ID for calcul-moyenne
        calcul_moyenne_id = None
        for exercise in td2_config['exercises']:
            if exercise['exerciseId'] == '04-calcul-moyenne':
                calcul_moyenne_id = exercise['exerciseId']
                break
        
        if not calcul_moyenne_id:
            msg = "Exercise '04-calcul-moyenne' not found in TD2.json configuration"
            print(msg)
            out_file.write(msg + '\n')
            return
        
        # Load exercise config
        exercise_config_path = os.path.join('configs', f'{calcul_moyenne_id}.json')
        with open(exercise_config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        config = ExerciseConfig(config_dict)
        
        # Initialize analyzer
        analyzer = StaticAnalyzer()
        
        # Get all Java files in TD2 directory
        java_files = glob.glob('tests/java_samples/TD2/**/*.java', recursive=True)
        
        if not java_files:
            msg = "No Java files found in tests/java_samples/TD2/ directory"
            print(msg)
            out_file.write(msg + '\n')
            return
        
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
            
            # --- Résumé global ---
            syntax_ok = result['is_valid']
            methods_ok = len(result['missing_methods']) == 0 and not has_wrong_method_names
            patterns_ok = len(missing_patterns) == 0
            operators_ok = not ('disallowed_operators' in result['analysis_details'] and result['analysis_details']['disallowed_operators'])
            
            global_status = SYMBOL_OK if (syntax_ok and methods_ok and patterns_ok and operators_ok) else SYMBOL_FAIL
            
            msg = f"\n{global_status} RÉSULTAT GLOBAL: " + ("SUCCÈS" if (syntax_ok and methods_ok and patterns_ok and operators_ok) else "DES PROBLÈMES ONT ÉTÉ DÉTECTÉS")
            print(msg)
            out_file.write(msg + '\n')
            
            # Détail des problèmes s'il y en a
            if not (syntax_ok and methods_ok and patterns_ok and operators_ok):
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
        
        print("\nAnalysis complete. Results saved to analysis_results_td2.txt")
                
def main():
    """Main function to run tests"""
    # Run unit tests first
    unit_tests_passed = run_unit_tests()
    
    # Then analyze TD2 files
    analyze_td2_files()
    
    # Return success status based on unit test results
    return 0 if unit_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 