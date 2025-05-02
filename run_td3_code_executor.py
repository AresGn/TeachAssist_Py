import os
import sys
import glob
import json
from typing import Dict, List, Any
import logging
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importer les classes nécessaires
from teach_assit.core.execution.code_executor import JavaExecutor
from teach_assit.core.analysis.config_loader import ConfigLoader
from teach_assit.core.analysis.models import ExerciseConfig

# Symboles pour le rapport
SYMBOL_OK = "✅"
SYMBOL_FAIL = "❌"
SYMBOL_WARNING = "⚠️"
SYMBOL_INFO = "ℹ️"

def get_test_inputs(exercise_id: str, exercise_config=None) -> List[str]:
    """
    Détermine les entrées de test appropriées pour un exercice donné
    
    Args:
        exercise_id: Identifiant de l'exercice
        exercise_config: Configuration de l'exercice (si disponible)
    
    Returns:
        Liste des entrées de test
    """
    # Si nous avons une configuration d'exercice, essayer d'obtenir les entrées de test
    if exercise_config:
        logger.info(f"Tentative de récupération des entrées de test pour {exercise_id} depuis la configuration")
        
        # Méthode 1: Utiliser la méthode get_test_inputs si disponible
        if hasattr(exercise_config, 'get_test_inputs') and callable(getattr(exercise_config, 'get_test_inputs')):
            try:
                raw_inputs = exercise_config.get_test_inputs()
                if raw_inputs:
                    # Si les résultats sont des dictionnaires, extraire la valeur
                    if isinstance(raw_inputs[0], dict):
                        test_inputs = [item.get("value", "") for item in raw_inputs]
                        logger.info(f"Entrées de test obtenues via get_test_inputs(): {test_inputs}")
                        return test_inputs
                    else:
                        logger.info(f"Entrées de test obtenues via get_test_inputs(): {raw_inputs}")
                        return raw_inputs
            except Exception as e:
                logger.error(f"Erreur lors de l'appel de get_test_inputs(): {str(e)}")
        
        # Méthode 2: Accéder directement à l'attribut test_inputs
        if hasattr(exercise_config, 'test_inputs'):
            try:
                raw_inputs = exercise_config.test_inputs
                if raw_inputs:
                    # Si les résultats sont des dictionnaires, extraire la valeur
                    if isinstance(raw_inputs[0], dict):
                        test_inputs = [item.get("value", "") for item in raw_inputs]
                        logger.info(f"Entrées de test obtenues via l'attribut test_inputs: {test_inputs}")
                        return test_inputs
                    else:
                        logger.info(f"Entrées de test obtenues via l'attribut test_inputs: {raw_inputs}")
                        return raw_inputs
            except Exception as e:
                logger.error(f"Erreur lors de l'accès à l'attribut test_inputs: {str(e)}")
    
    # Entrées par défaut selon le type d'exercice
    logger.info(f"Utilisation des entrées par défaut pour {exercise_id}")
    
    if "fonction-racine" in exercise_id or "racine-carree" in exercise_id:
        return ["4", "9", "16", "-4", "0"]
    elif "comptage-mots" in exercise_id:
        return ["Ceci est un test", "Un deux trois quatre", ""]
    elif "triangle-isocele" in exercise_id:
        return ["3", "5", "10"]
    elif "sequence-numerique" in exercise_id:
        return [""]  # Pas d'entrée nécessaire pour cet exercice
    else:
        # Entrées génériques par défaut
        return ["1", "5", "10"]

def extract_class_name_from_file(file_path: str) -> str:
    """
    Extrait le nom de la classe principale du fichier Java
    
    Args:
        file_path: Chemin vers le fichier Java
    
    Returns:
        Nom de la classe principale ou None si non trouvé
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Recherche des déclarations de classe publique
            pattern = r'public\s+class\s+(\w+)'
            match = re.search(pattern, content)
            
            if match:
                return match.group(1)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du nom de classe: {str(e)}")
    
    return None

def fix_java_file(file_path: str, temp_dir: str) -> str:
    """
    Crée une copie du fichier Java avec un nom correspondant à sa classe principale
    
    Args:
        file_path: Chemin vers le fichier Java original
        temp_dir: Répertoire temporaire pour la copie
    
    Returns:
        Chemin vers le fichier corrigé ou le fichier original si pas de correction nécessaire
    """
    # Extraire le nom de la classe principale
    class_name = extract_class_name_from_file(file_path)
    
    if not class_name:
        return file_path  # Impossible de trouver le nom de classe
    
    # Vérifier si le nom du fichier correspond déjà au nom de la classe
    file_name = os.path.basename(file_path)
    expected_file_name = f"{class_name}.java"
    
    if file_name == expected_file_name:
        return file_path  # Le fichier a déjà le bon nom
    
    # Créer un répertoire temporaire s'il n'existe pas
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Créer un fichier avec le bon nom
    corrected_file_path = os.path.join(temp_dir, expected_file_name)
    
    try:
        # Copier le contenu du fichier original
        with open(file_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        # Écrire dans le nouveau fichier
        with open(corrected_file_path, 'w', encoding='utf-8') as dest:
            dest.write(content)
        
        logger.info(f"Fichier corrigé créé: {corrected_file_path} (classe: {class_name})")
        return corrected_file_path
    
    except Exception as e:
        logger.error(f"Erreur lors de la correction du fichier: {str(e)}")
        return file_path  # En cas d'erreur, utiliser le fichier original

def analyze_td3_files():
    """Exécuter les fichiers Java du TD3."""
    print("\nExécution des fichiers Java du TD3...")
    
    # Ouvrir un fichier pour écrire les résultats
    with open('execution_results_td3.txt', 'w', encoding='utf-8') as out_file:
        # Créer un répertoire temporaire pour les fichiers corrigés
        temp_dir = os.path.join(os.getcwd(), "temp_fixed_files")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Initialiser le chargeur de configuration
        config_loader = ConfigLoader(os.getcwd())
        
        # S'assurer que toutes les configurations sont chargées depuis la base de données
        config_loader.load_all_configs()
        
        # Récupérer la configuration TD3 depuis la base de données
        td3_config = config_loader.get_assessment_config('TD3')
        
        if not td3_config:
            msg = "Configuration TD3 non trouvée dans la base de données"
            print(msg)
            logger.error(msg)
            out_file.write(msg + '\n')
            
            # Essayer de charger depuis le fichier JSON
            td3_config_path = 'assessments/TD3.json'
            if os.path.exists(td3_config_path):
                msg = f"Chargement de la configuration TD3 depuis le fichier {td3_config_path}"
                print(msg)
                logger.info(msg)
                out_file.write(msg + '\n')
                
                try:
                    with open(td3_config_path, 'r', encoding='utf-8') as f:
                        td3_data = json.load(f)
                    # Créer la config avec les données du fichier
                    from teach_assit.core.analysis.models import AssessmentConfig
                    td3_config = AssessmentConfig(td3_data)
                except Exception as e:
                    msg = f"Erreur lors du chargement du fichier TD3.json: {str(e)}"
                    print(msg)
                    logger.error(msg)
                    out_file.write(msg + '\n')
                    return
            else:
                msg = f"Fichier de configuration TD3 non trouvé: {td3_config_path}"
                print(msg)
                logger.error(msg)
                out_file.write(msg + '\n')
                return
        
        # Récupérer tous les exercices du TD3
        exercise_ids = [ex.get('exerciseId', '') for ex in td3_config.exercises if ex.get('exerciseId', '')]
        if not exercise_ids:
            msg = "Aucun exercice trouvé dans la configuration TD3"
            print(msg)
            logger.error(msg)
            out_file.write(msg + '\n')
            return
        
        msg = f"Exercices identifiés pour TD3: {exercise_ids}"
        print(msg)
        out_file.write(msg + '\n')
        
        # Récupérer toutes les configurations d'exercices
        exercise_configs = config_loader.get_all_exercise_configs()
        
        # Vérifier si toutes les configurations d'exercice sont disponibles
        missing_configs = [ex_id for ex_id in exercise_ids if ex_id not in exercise_configs]
        if missing_configs:
            msg = f"Certaines configurations d'exercice sont manquantes: {missing_configs}"
            print(msg)
            logger.warning(msg)
            out_file.write(msg + '\n')
            
            # Essayer de charger les configurations manquantes depuis les fichiers JSON
            for ex_id in missing_configs:
                config_path = f"configs/{ex_id}.json"
                if os.path.exists(config_path):
                    msg = f"Chargement de la configuration {ex_id} depuis {config_path}"
                    print(msg)
                    logger.info(msg)
                    out_file.write(msg + '\n')
                    
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config_dict = json.load(f)
                        exercise_configs[ex_id] = ExerciseConfig(config_dict)
                    except Exception as e:
                        msg = f"Erreur lors du chargement de {config_path}: {str(e)}"
                        print(msg)
                        logger.error(msg)
                        out_file.write(msg + '\n')
        
        # Initialiser l'exécuteur Java
        executor = JavaExecutor()
        
        # Récupérer tous les fichiers Java dans le dossier TD3
        java_files = glob.glob('tests/java_samples/TD3/**/*.java', recursive=True)
        
        if not java_files:
            msg = "Aucun fichier Java trouvé dans le dossier tests/java_samples/TD3/"
            print(msg)
            out_file.write(msg + '\n')
            return
        
        msg = f"Trouvé {len(java_files)} fichiers Java à exécuter:"
        print(msg)
        out_file.write(msg + '\n')
        
        # Analyser chaque fichier
        for file in java_files:
            student_name = os.path.basename(os.path.dirname(file))
            file_name = os.path.basename(file)
            msg = f"\n{'='*50}\n{SYMBOL_INFO} RAPPORT D'EXÉCUTION: {file} (Étudiant: {student_name})\n{'='*50}"
            print(msg)
            out_file.write(msg + '\n')
            
            # Extraire le nom de la classe principale
            class_name = extract_class_name_from_file(file)
            if class_name:
                msg = f"{SYMBOL_INFO} Classe principale détectée: {class_name}"
                print(msg)
                out_file.write(msg + '\n')
                
                # Vérifier si le nom du fichier correspond au nom de la classe
                expected_file_name = f"{class_name}.java"
                if file_name != expected_file_name:
                    msg = f"{SYMBOL_WARNING} Nom de fichier ({file_name}) ne correspond pas au nom de classe ({class_name})"
                    print(msg)
                    out_file.write(msg + '\n')
                    
                    # Créer une copie du fichier avec le bon nom
                    corrected_file = fix_java_file(file, temp_dir)
                    if corrected_file != file:
                        msg = f"{SYMBOL_INFO} Fichier corrigé créé: {corrected_file}"
                        print(msg)
                        out_file.write(msg + '\n')
                        # Utiliser le fichier corrigé pour les tests
                        file = corrected_file
            
            # Identifier l'exercice associé au fichier
            exercise_id = None
            exercise_config = None
            
            # Essayer de faire correspondre le fichier à un exercice du TD3
            for ex_id in exercise_ids:
                if ex_id in exercise_configs:
                    config = exercise_configs[ex_id]
                    # Vérifier si le nom du fichier correspond à l'exercice
                    keywords = []
                    if '-' in ex_id:
                        keywords.append(ex_id.split('-', 1)[1].lower())
                    for word in config.name.lower().split():
                        if len(word) > 3:  # Ignorer les mots courts
                            keywords.append(word)
                    
                    for keyword in keywords:
                        if keyword in file_name.lower():
                            exercise_id = ex_id
                            exercise_config = config
                            break
                
                if exercise_config:
                    break
            
            if not exercise_config:
                msg = f"{SYMBOL_WARNING} Impossible de déterminer le type d'exercice pour {file_name}"
                print(msg)
                out_file.write(msg + '\n')
                continue
            
            # Récupérer le nom et la description de l'exercice
            exercise_name = exercise_config.name
            exercise_desc = exercise_config.description
            
            msg = f"{SYMBOL_INFO} Exercice identifié: {exercise_name} ({exercise_id})"
            print(msg)
            out_file.write(msg + '\n')
            msg = f"  Description: {exercise_desc}"
            print(msg)
            out_file.write(msg + '\n')
            
            # Déterminer les entrées de test appropriées
            test_inputs = get_test_inputs(exercise_id, exercise_config)
            
            msg = f"{SYMBOL_INFO} Exécution avec {len(test_inputs)} entrées de test: {', '.join(f'[{input}]' for input in test_inputs)}"
            print(msg)
            out_file.write(msg + '\n')
            
            # Exécuter le code avec les entrées de test
            results = executor.test_with_inputs(file, test_inputs)
            
            # Afficher les résultats
            for i, result in enumerate(results):
                input_val = test_inputs[i] if i < len(test_inputs) else ""
                success = result.get('success', False)
                compilation_error = result.get('compilation_error', False)
                stdout = result.get('stdout', '')
                stderr = result.get('stderr', '')
                
                # Déterminer le statut
                if compilation_error:
                    status = SYMBOL_FAIL
                    status_text = "ÉCHEC DE COMPILATION"
                elif success:
                    status = SYMBOL_OK
                    status_text = "SUCCÈS"
                else:
                    status = SYMBOL_FAIL
                    status_text = "ÉCHEC D'EXÉCUTION"
                
                # Afficher le résultat pour cette entrée
                test_name = f"Test #{i+1}" if input_val else "Exécution sans entrée"
                msg = f"\n{status} {test_name} ({input_val}): {status_text}"
                print(msg)
                out_file.write(msg + '\n')
                
                if compilation_error:
                    msg = f"  Erreur de compilation:\n{stderr}"
                    print(msg)
                    out_file.write(msg + '\n')
                    
                    # Après la première erreur de compilation, on peut arrêter
                    break
                else:
                    # Afficher la sortie standard
                    msg = f"  Sortie standard:\n{stdout}"
                    print(msg)
                    out_file.write(msg + '\n')
                    
                    # Afficher les erreurs si présentes
                    if stderr:
                        msg = f"  Erreurs:\n{stderr}"
                        print(msg)
                        out_file.write(msg + '\n')
            
            # Résumé global pour ce fichier
            all_success = all(result.get('success', False) for result in results)
            any_compilation_error = any(result.get('compilation_error', False) for result in results)
            
            if any_compilation_error:
                global_status = SYMBOL_FAIL
                status_text = "ÉCHEC DE COMPILATION"
            elif all_success:
                global_status = SYMBOL_OK
                status_text = "TOUS LES TESTS RÉUSSIS"
            else:
                global_status = SYMBOL_WARNING
                status_text = "CERTAINS TESTS ÉCHOUÉS"
            
            msg = f"\n{global_status} RÉSULTAT GLOBAL: {status_text}"
            print(msg)
            out_file.write(msg + '\n')
        
        # Nettoyage du répertoire temporaire
        try:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                logger.info(f"Répertoire temporaire supprimé: {temp_dir}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des fichiers temporaires: {str(e)}")
        
        print("\nExécution terminée. Résultats sauvegardés dans execution_results_td3.txt")
    
def main():
    """Fonction principale pour exécuter les tests du TD3"""
    analyze_td3_files()
    return 0

if __name__ == "__main__":
    sys.exit(main()) 