"""
Module pour l'exécution de code Java.
"""

import os
import logging
from PyQt5.QtCore import qInstallMessageHandler, QtDebugMsg, QtInfoMsg, QtWarningMsg, QtCriticalMsg, QtFatalMsg
from teach_assit.core.execution.code_executor import JavaExecutor

class CodeExecutor:
    """Classe pour exécuter des codes étudiants avec différentes entrées."""
    
    def __init__(self):
        """Initialiser l'exécuteur de code."""
        self._setup_message_handler()
        self.executor = JavaExecutor()
    
    def _setup_message_handler(self):
        """Configurer le gestionnaire de messages Qt pour supprimer les avertissements inutiles."""
        def message_handler(msg_type, context, message):
            if "QFont::setPixelSize: Pixel size <= 0" in message:
                return  # Ignorer ce message spécifique
            if msg_type == QtWarningMsg:
                logging.warning(message)
            elif msg_type == QtCriticalMsg:
                logging.error(message)
            elif msg_type == QtFatalMsg:
                logging.critical(message)
        
        # Installer le gestionnaire de messages Qt
        qInstallMessageHandler(message_handler)
    
    def find_file_path(self, student_name, file_name, working_dir=None):
        """Trouver le chemin d'un fichier étudiant.
        
        Args:
            student_name: Nom de l'étudiant
            file_name: Nom du fichier
            working_dir: Répertoire de travail (par défaut le répertoire courant)
            
        Returns:
            str: Chemin du fichier trouvé ou None si non trouvé
        """
        if not working_dir:
            working_dir = os.getcwd()
        
        logging.info(f"Recherche du fichier '{file_name}' pour l'étudiant '{student_name}'")
        logging.info(f"Répertoire de travail: {working_dir}")
        
        # Normaliser le nom du fichier (sans considérer la casse)
        normalized_filename = file_name.lower()
        
        # Essayer différents chemins pour trouver le fichier
        possible_paths = [
            # Chemin direct (si c'est déjà un chemin absolu)
            file_name,
            # Chemin relatif au répertoire courant
            os.path.join(working_dir, file_name),
            # Chemin dans le répertoire des fichiers extraits
            os.path.join(working_dir, "extracted_files", student_name, file_name),
            # Chemin dans le répertoire des soumissions
            os.path.join(working_dir, "submitted_files", student_name, file_name),
            # Chemin dans un dossier étudiant directement
            os.path.join(working_dir, student_name, file_name),
            # Variantes avec lettres minuscules
            os.path.join(working_dir, "extracted_files", student_name.lower(), file_name),
            os.path.join(working_dir, "submitted_files", student_name.lower(), file_name),
            # Rechercher dans d'autres dossiers communs
            os.path.join(working_dir, "tests", "java_samples", student_name, file_name),
            os.path.join(working_dir, "tests", "java_samples", "TD4", student_name, file_name)
        ]
        
        # Vérifier chaque chemin
        for path in possible_paths:
            if os.path.exists(path):
                logging.info(f"Fichier trouvé: {path}")
                return path
            else:
                logging.debug(f"Chemin non trouvé: {path}")
        
        # Si le fichier n'est toujours pas trouvé, essayer de chercher par nom similaire
        logging.info(f"Fichier non trouvé, recherche de noms similaires...")
        
        # Chercher dans les répertoires d'étudiants tous les fichiers .java
        student_dirs = [
            os.path.join(working_dir, "extracted_files", student_name),
            os.path.join(working_dir, "submitted_files", student_name),
            os.path.join(working_dir, student_name),
            os.path.join(working_dir, "tests", "java_samples", student_name),
            os.path.join(working_dir, "tests", "java_samples", "TD4", student_name)
        ]
        
        for student_dir in student_dirs:
            if not os.path.exists(student_dir):
                continue
                
            for root, _, files in os.walk(student_dir):
                for file in files:
                    if file.lower().endswith('.java'):
                        # Vérifier si le nom de fichier contient des parties du nom recherché
                        # ou si le nom recherché contient des parties du nom de fichier
                        file_lower = file.lower()
                        if (normalized_filename in file_lower or
                            any(part in file_lower for part in normalized_filename.replace('-', ' ').split() if len(part) > 3)):
                            full_path = os.path.join(root, file)
                            logging.info(f"Fichier similaire trouvé: {full_path}")
                            return full_path
        
        logging.warning(f"Aucun fichier trouvé pour '{file_name}' de l'étudiant '{student_name}'")
        return None
    
    def execute_code(self, file_path, test_inputs):
        """Exécuter un code avec différentes entrées.
        
        Args:
            file_path: Chemin du fichier à exécuter
            test_inputs: Liste des entrées de test
            
        Returns:
            list: Liste des résultats d'exécution
        """
        if not file_path or not os.path.exists(file_path):
            return [self._create_error_result(input_val, "Fichier non trouvé") for input_val in test_inputs]
        
        try:
            # Vérifier si le fichier est un fichier Java
            if file_path.lower().endswith('.java'):
                # Prétraiter le fichier pour éviter les erreurs de nom de classe/fichier
                file_path = self._preprocess_java_file(file_path)
                
            return self.executor.test_with_inputs(file_path, test_inputs)
        except Exception as e:
            import traceback
            error_msg = f"Erreur d'exécution: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            return [self._create_error_result(input_val, error_msg) for input_val in test_inputs]
    
    def _preprocess_java_file(self, file_path):
        """Prétraite un fichier Java pour éviter les erreurs de noms de classe/fichier.
        
        Args:
            file_path: Chemin du fichier Java
            
        Returns:
            str: Chemin du fichier Java (potentiellement modifié)
        """
        try:
            # Extraire le nom de la classe du fichier
            real_class_name = self._extract_class_name_from_file(file_path)
            if not real_class_name:
                return file_path  # Impossible de trouver le nom de classe
            
            # Vérifier si le nom du fichier correspond déjà au nom de la classe
            file_name = os.path.basename(file_path)
            expected_file_name = f"{real_class_name}.java"
            
            if file_name == expected_file_name:
                return file_path  # Le fichier a déjà le bon nom
            
            # Créer un répertoire temporaire s'il n'existe pas
            temp_dir = os.path.join(os.path.dirname(file_path), "_temp_java_files")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Créer un fichier avec le bon nom
            corrected_file_path = os.path.join(temp_dir, expected_file_name)
            
            # Copier le contenu du fichier original
            with open(file_path, 'r', encoding='utf-8') as src:
                content = src.read()
            
            # Écrire dans le nouveau fichier
            with open(corrected_file_path, 'w', encoding='utf-8') as dest:
                dest.write(content)
            
            logging.info(f"Fichier Java corrigé créé: {corrected_file_path} (classe: {real_class_name})")
            return corrected_file_path
            
        except Exception as e:
            logging.error(f"Erreur lors du prétraitement du fichier Java: {str(e)}")
            return file_path  # En cas d'erreur, utiliser le fichier original
    
    def _extract_class_name_from_file(self, file_path):
        """Extrait le nom de la classe principale du fichier Java.
        
        Args:
            file_path: Chemin vers le fichier Java
            
        Returns:
            str: Nom de la classe principale ou None si non trouvé
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Recherche des déclarations de classe publique
                import re
                pattern = r'public\s+class\s+(\w+)'
                match = re.search(pattern, content)
                
                if match:
                    return match.group(1)
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction du nom de classe: {str(e)}")
        
        return None
    
    def _create_error_result(self, input_val, error_message):
        """Créer un résultat d'erreur.
        
        Args:
            input_val: Valeur d'entrée concernée
            error_message: Message d'erreur
            
        Returns:
            dict: Résultat formaté
        """
        return {
            "input": input_val,
            "success": False,
            "compilation_error": True,
            "stdout": "",
            "stderr": error_message
        } 