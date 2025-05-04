"""
Module pour gérer la compilation et l'exécution des codes Java des étudiants.
"""

import os
import subprocess
import tempfile
import time
import shutil
import logging
from typing import Dict, List, Tuple, Any, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JavaExecutor:
    """Classe pour compiler et exécuter du code Java."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialiser l'exécuteur de code Java.
        
        Args:
            temp_dir: Répertoire temporaire pour les fichiers de compilation (optionnel)
        """
        self.temp_dir = temp_dir if temp_dir else tempfile.mkdtemp(prefix="teachassist_")
        logger.info(f"Répertoire temporaire de compilation créé: {self.temp_dir}")
        
        # Vérifier si Java est installé
        try:
            subprocess.run(['javac', '-version'], capture_output=True, check=True)
            logger.info("Java compiler (javac) trouvé et fonctionnel.")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("Le compilateur Java (javac) n'est pas disponible. Veuillez installer le JDK.")
    
    def compile_java(self, file_path: str) -> Tuple[bool, str]:
        """
        Compiler un fichier Java.
        
        Args:
            file_path: Chemin vers le fichier Java à compiler
        
        Returns:
            (success, output): Un tuple avec le statut de succès et la sortie
        """
        # Créer un répertoire pour ce fichier spécifique
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)
        compile_dir = os.path.join(self.temp_dir, os.path.splitext(file_name)[0])
        
        os.makedirs(compile_dir, exist_ok=True)
        
        # Copier le fichier dans le répertoire temporaire
        temp_file_path = os.path.join(compile_dir, file_name)
        shutil.copy2(file_path, temp_file_path)
        
        # Extraire préalablement le nom de la classe du fichier
        real_class_name = self._extract_class_name_from_file(temp_file_path)
        if real_class_name:
            # Si on a trouvé un nom de classe qui pourrait être différent du nom de fichier,
            # créer d'avance un fichier avec le nom correct
            correct_file_name = f"{real_class_name}.java"
            correct_file_path = os.path.join(compile_dir, correct_file_name)
            
            # Ne créer le nouveau fichier que si le nom diffère
            if correct_file_name != file_name:
                logger.info(f"Nom de classe ({real_class_name}) différent du nom de fichier ({file_name}), création d'une copie correcte")
                
                # Copier le contenu du fichier original
                with open(temp_file_path, 'r', encoding='utf-8') as src_file:
                    java_content = src_file.read()
                
                # Écrire dans le nouveau fichier
                with open(correct_file_path, 'w', encoding='utf-8') as dest_file:
                    dest_file.write(java_content)
                
                # Utiliser ce fichier pour la compilation
                temp_file_path = correct_file_path
                # Stocker le vrai nom de classe pour l'exécution
                self._real_class_name = real_class_name
        
        # Exécuter javac pour compiler le fichier
        try:
            logger.info(f"Compilation de {os.path.basename(temp_file_path)}...")
            result = subprocess.run(
                ['javac', temp_file_path],
                capture_output=True,
                text=True,
                timeout=10  # Timeout de 10 secondes pour la compilation
            )
            
            # Vérifier si la compilation a réussi
            if result.returncode == 0:
                logger.info(f"Compilation réussie pour {os.path.basename(temp_file_path)}")
                return True, "Compilation réussie"
            else:
                # Vérifier si l'erreur est due à un nom de classe différent du nom de fichier
                stderr = result.stderr
                if "public class" in stderr and "should be declared in a file named" in stderr:
                    # Extraire le vrai nom de classe à partir du message d'erreur
                    import re
                    match = re.search(r'class\s+(\w+)\s+should\s+be\s+declared', stderr)
                    if match:
                        real_class_name = match.group(1)
                        logger.info(f"Erreur de nom de classe détectée. Classe réelle: {real_class_name}, nom de fichier: {os.path.basename(temp_file_path)}")
                        
                        # Créer un nouveau fichier temporaire avec le bon nom
                        correct_file_name = f"{real_class_name}.java"
                        correct_file_path = os.path.join(compile_dir, correct_file_name)
                        
                        # Copier le contenu du fichier original
                        with open(temp_file_path, 'r', encoding='utf-8') as src_file:
                            java_content = src_file.read()
                        
                        # Écrire dans le nouveau fichier
                        with open(correct_file_path, 'w', encoding='utf-8') as dest_file:
                            dest_file.write(java_content)
                        
                        # Essayer de compiler le nouveau fichier
                        logger.info(f"Tentative de compilation avec le nom de fichier correct: {correct_file_name}")
                        result = subprocess.run(
                            ['javac', correct_file_path],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if result.returncode == 0:
                            logger.info(f"Compilation réussie après correction du nom de fichier pour {real_class_name}")
                            # Stocker le vrai nom de classe pour l'exécution
                            self._real_class_name = real_class_name
                            return True, "Compilation réussie après correction du nom de fichier"
                        else:
                            # La compilation a échoué même avec le bon nom de fichier
                            logger.warning(f"Échec de compilation après correction du nom de fichier: {result.stderr}")
                            return False, result.stderr
                
                # Erreur standard de compilation
                logger.warning(f"Échec de compilation pour {os.path.basename(temp_file_path)}: {stderr}")
                return False, stderr
        
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout lors de la compilation de {os.path.basename(temp_file_path)}")
            return False, "Compilation timeout (> 10s)"
        
        except Exception as e:
            logger.error(f"Erreur lors de la compilation de {os.path.basename(temp_file_path)}: {str(e)}")
            return False, f"Erreur de compilation: {str(e)}"
            
    def _extract_class_name_from_file(self, file_path: str) -> Optional[str]:
        """
        Extrait le nom de la classe publique d'un fichier Java.
        
        Args:
            file_path: Chemin vers le fichier Java
            
        Returns:
            str: Nom de la classe publique ou None si non trouvé
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Recherche d'une classe publique
                import re
                match = re.search(r'public\s+class\s+(\w+)', content)
                if match:
                    return match.group(1)
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du nom de classe: {str(e)}")
            
        return None
    
    def execute_java(self, file_path: str, args: List[str] = None, timeout: int = 5) -> Tuple[bool, str, str]:
        """
        Exécuter un fichier Java compilé.
        
        Args:
            file_path: Chemin vers le fichier Java source
            args: Arguments à passer au programme Java
            timeout: Temps maximum d'exécution en secondes
        
        Returns:
            (success, stdout, stderr): Un tuple avec le statut, la sortie standard et l'erreur standard
        """
        # Déterminer le nom de la classe (sans extension .java)
        file_name = os.path.basename(file_path)
        class_name = os.path.splitext(file_name)[0]
        
        # Vérifier s'il y a un nom de classe réel différent qui a été détecté lors de la compilation
        real_class_name = getattr(self, '_real_class_name', class_name)
        
        # Répertoire où se trouve la classe compilée
        compile_dir = os.path.join(self.temp_dir, class_name)
        
        # Vérifier si la classe compilée existe (soit avec le nom original, soit avec le nom réel)
        class_file_path = os.path.join(compile_dir, f"{real_class_name}.class") 
        if not os.path.exists(class_file_path):
            # Essayer avec le nom original
            original_class_file = os.path.join(compile_dir, f"{class_name}.class")
            if os.path.exists(original_class_file):
                real_class_name = class_name
            else:
                # Chercher tout fichier .class dans le répertoire
                class_files = [f for f in os.listdir(compile_dir) if f.endswith('.class')]
                if class_files:
                    # Utiliser le premier fichier .class trouvé
                    real_class_name = os.path.splitext(class_files[0])[0]
                    logger.info(f"Utilisation de la classe trouvée: {real_class_name}")
                else:
                    logger.error(f"Aucun fichier classe trouvé dans {compile_dir}")
                    return False, "", f"Erreur: Aucun fichier classe trouvé dans le répertoire de compilation"
        
        # Préparer les arguments
        if args is None:
            args = []
        
        # Exécuter la classe Java
        try:
            logger.info(f"Exécution de {real_class_name} avec args={args}...")
            result = subprocess.run(
                ['java', '-cp', compile_dir, real_class_name] + args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Exécution réussie de {real_class_name}")
                return True, result.stdout, result.stderr
            else:
                logger.warning(f"Erreur lors de l'exécution de {real_class_name}: {result.stderr}")
                return False, result.stdout, result.stderr
        
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout lors de l'exécution de {real_class_name}")
            return False, "", f"Exécution timeout (> {timeout}s)"
        
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de {real_class_name}: {str(e)}")
            return False, "", f"Erreur d'exécution: {str(e)}"
    
    def test_with_inputs(self, file_path: str, test_inputs: List[str], timeout: int = 5) -> List[Dict[str, Any]]:
        """
        Tester un programme Java avec plusieurs entrées.
        
        Args:
            file_path: Chemin vers le fichier Java
            test_inputs: Liste des entrées à tester
            timeout: Temps maximum d'exécution en secondes
        
        Returns:
            Liste des résultats de test avec statut, entrée, sortie et erreurs
        """
        results = []
        
        # D'abord compiler le fichier
        compile_success, compile_output = self.compile_java(file_path)
        
        if not compile_success:
            # Si la compilation échoue, retourner une erreur pour tous les tests
            for input_val in test_inputs:
                results.append({
                    "input": input_val,
                    "success": False,
                    "compilation_error": True,
                    "stdout": "",
                    "stderr": compile_output
                })
            return results
        
        # Si la compilation réussit, exécuter chaque test
        for input_val in test_inputs:
            # Extraire le nom de la classe Java pour ce fichier
            file_name = os.path.basename(file_path)
            class_name = os.path.splitext(file_name)[0]
            
            # Vérifier s'il y a un nom de classe réel différent qui a été détecté lors de la compilation
            real_class_name = getattr(self, '_real_class_name', class_name)
            
            compile_dir = os.path.join(self.temp_dir, class_name)
            
            # Vérifier si le fichier .class existe avec le nom réel
            class_file_path = os.path.join(compile_dir, f"{real_class_name}.class")
            if not os.path.exists(class_file_path):
                # Chercher tout fichier .class dans le répertoire
                class_files = [f for f in os.listdir(compile_dir) if f.endswith('.class')]
                if class_files:
                    # Utiliser le premier fichier .class trouvé
                    real_class_name = os.path.splitext(class_files[0])[0]
                    logger.info(f"Utilisation de la classe trouvée: {real_class_name}")
            
            logger.info(f"Test de {real_class_name} avec entrée '{input_val}'")
            
            try:
                # Exécuter le programme avec cette entrée spécifique
                process = subprocess.Popen(
                    ['java', '-cp', compile_dir, real_class_name],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                try:
                    # Fournir l'entrée et récupérer la sortie pour ce test spécifique
                    stdout, stderr = process.communicate(input=input_val, timeout=timeout)
                    success = process.returncode == 0
                    
                    # Ajouter ce résultat spécifique à la liste des résultats
                    results.append({
                        "input": input_val,
                        "success": success,
                        "compilation_error": False,
                        "stdout": stdout,
                        "stderr": stderr
                    })
                    
                    logger.info(f"Test avec entrée '{input_val}' terminé: {'succès' if success else 'échec'}")
                
                except subprocess.TimeoutExpired:
                    process.kill()
                    results.append({
                        "input": input_val,
                        "success": False,
                        "compilation_error": False,
                        "stdout": "",
                        "stderr": f"Exécution timeout (> {timeout}s)"
                    })
                    logger.warning(f"Timeout pour test avec entrée '{input_val}'")
            
            except Exception as e:
                results.append({
                    "input": input_val,
                    "success": False,
                    "compilation_error": False,
                    "stdout": "",
                    "stderr": f"Erreur d'exécution: {str(e)}"
                })
                logger.error(f"Erreur pour test avec entrée '{input_val}': {str(e)}")
        
        return results
    
    def clean_up(self):
        """Nettoyer les fichiers temporaires."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Répertoire temporaire supprimé: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des fichiers temporaires: {str(e)}")
    
    def __del__(self):
        """Destructeur pour nettoyer les ressources."""
        self.clean_up()


# Exemple d'utilisation
if __name__ == "__main__":
    executor = JavaExecutor()
    
    # Exemple de test avec un fichier Java simple
    file_path = "example/HelloWorld.java"
    test_inputs = ["3", "5", "10"]
    
    results = executor.test_with_inputs(file_path, test_inputs)
    
    for result in results:
        print(f"Test avec entrée '{result['input']}':")
        print(f"  Succès: {result['success']}")
        print(f"  Sortie: {result['stdout']}")
        if result['stderr']:
            print(f"  Erreur: {result['stderr']}")
        print("-" * 30) 