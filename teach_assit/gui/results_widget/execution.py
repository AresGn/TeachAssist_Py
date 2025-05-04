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
        
        # Déterminer les informations de l'exercice et du TD à partir du nom de fichier
        # Cette méthode plus générique utilise des patterns plutôt que des valeurs codées en dur
        td_info = self._extract_assessment_info(normalized_filename)
        
        # Construire les chemins de recherche dynamiquement en fonction du TD identifié
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
            os.path.join(working_dir, "submitted_files", student_name.lower(), file_name)
        ]
        
        # Ajouter les chemins pour tous les TDs connus
        for td_number in range(1, 10):  # Supporter TD1 à TD9
            td_name = f"TD{td_number}"
            possible_paths.append(os.path.join(working_dir, "tests", "java_samples", td_name, student_name, file_name))
            possible_paths.append(os.path.join(working_dir, "tests", "java_samples", td_name, student_name.lower(), file_name))
        
        # Vérifier chaque chemin
        for path in possible_paths:
            if os.path.exists(path):
                logging.info(f"Fichier trouvé: {path}")
                return path
            else:
                logging.debug(f"Chemin non trouvé: {path}")
        
        # Si le fichier n'a pas été trouvé avec les chemins directs, essayer la recherche par similarité
        return self._find_file_by_similarity(student_name, normalized_filename, td_info, working_dir)
    
    def _extract_assessment_info(self, normalized_filename):
        """Extrait les informations d'évaluation (TD) à partir du nom de fichier.
        
        Args:
            normalized_filename: Nom de fichier normalisé (en minuscules)
            
        Returns:
            dict: Informations sur le TD et l'exercice
        """
        # Initialiser avec des valeurs par défaut
        td_info = {
            "td_name": None,
            "exercise_id": None,
            "keywords": []
        }
        
        # Essayer de détecter le TD à partir d'un pattern comme "01-exercice" ou "TD1"
        import re
        # Détecter les patterns comme "09-fonction" (TD3) ou similaires
        id_match = re.search(r'^(\d{2})-([a-z-]+)', normalized_filename)
        if id_match:
            exercise_number = id_match.group(1)
            keyword = id_match.group(2)
            
            # Associer les numéros d'exercice aux TDs (ceci pourrait être amélioré via une configuration)
            if exercise_number in ["09", "10"]:
                td_info["td_name"] = "TD3"
            elif exercise_number in ["11", "12", "13", "14"]:
                td_info["td_name"] = "TD4"
            elif exercise_number in ["01", "02", "03", "04"]:
                td_info["td_name"] = "TD1"
            elif exercise_number in ["05", "06", "07", "08"]:
                td_info["td_name"] = "TD2"
                
            td_info["exercise_id"] = f"{exercise_number}-{keyword}"
            td_info["keywords"] = keyword.split("-")
        
        # Détecter directement le TD dans le nom du fichier
        td_match = re.search(r'(td|TD)(\d+)', normalized_filename)
        if td_match and not td_info["td_name"]:
            td_info["td_name"] = f"TD{td_match.group(2)}"
        
        # Extraire des mots-clés supplémentaires du nom de fichier
        parts = re.findall(r'[a-z]{3,}', normalized_filename)
        if parts:
            for part in parts:
                if len(part) > 3 and part not in td_info["keywords"]:
                    td_info["keywords"].append(part)
        
        # Associations connues de mots-clés à des exercices
        keyword_to_td = {
            "racine": "TD3",
            "mot": "TD3",
            "comptage": "TD3",
            "triangle": "TD1",
            "isocele": "TD1",
            "sequence": "TD2",
            "numerique": "TD2"
        }
        
        # Si nous n'avons pas encore identifié le TD mais avons des mots-clés, essayer de le déduire
        if not td_info["td_name"] and td_info["keywords"]:
            for keyword in td_info["keywords"]:
                if keyword in keyword_to_td:
                    td_info["td_name"] = keyword_to_td[keyword]
                    break
        
        return td_info
    
    def _find_file_by_similarity(self, student_name, normalized_filename, td_info, working_dir):
        """Trouve un fichier par similarité avec le nom demandé.
        
        Args:
            student_name: Nom de l'étudiant
            normalized_filename: Nom de fichier normalisé
            td_info: Informations sur le TD et l'exercice
            working_dir: Répertoire de travail
            
        Returns:
            str: Chemin du fichier trouvé, ou None si non trouvé
        """
        # Chercher dans les répertoires d'étudiants tous les fichiers .java
        student_dirs = [
            os.path.join(working_dir, "extracted_files", student_name),
            os.path.join(working_dir, "submitted_files", student_name),
            os.path.join(working_dir, student_name)
        ]
        
        # Ajouter les répertoires spécifiques au TD s'ils sont connus
        if td_info["td_name"]:
            student_dirs.append(os.path.join(working_dir, "tests", "java_samples", td_info["td_name"], student_name))
            logging.info(f"Recherche spécifique pour {td_info['td_name']} avec mots-clés: {td_info['keywords']}")
        
        # Ajouter une recherche dans tous les TDs au cas où
        for td_number in range(1, 10):  # Supporter TD1 à TD9
            td_name = f"TD{td_number}"
            student_dirs.append(os.path.join(working_dir, "tests", "java_samples", td_name, student_name))
            
        # Phase 1: Recherche dans les dossiers d'étudiants
        for student_dir in student_dirs:
            if not os.path.exists(student_dir):
                continue
                
            for root, _, files in os.walk(student_dir):
                for file in files:
                    if file.lower().endswith('.java'):
                        # Vérifier la correspondance par mots-clés ou par nom
                        if self._is_matching_file(file.lower(), normalized_filename, td_info["keywords"]):
                            full_path = os.path.join(root, file)
                            logging.info(f"Fichier similaire trouvé: {full_path}")
                            return full_path
        
        # Phase 2: Si un TD spécifique est identifié, chercher dans tout son répertoire
        if td_info["td_name"]:
            td_base_dir = os.path.join(working_dir, "tests", "java_samples", td_info["td_name"])
            if os.path.exists(td_base_dir):
                logging.info(f"Recherche approfondie dans tous les dossiers {td_info['td_name']}")
                
                for root, _, files in os.walk(td_base_dir):
                    for file in files:
                        if file.lower().endswith('.java'):
                            # Vérification plus stricte par mots-clés pour limiter les faux positifs
                            if self._is_matching_file(file.lower(), normalized_filename, td_info["keywords"], strict=True):
                                full_path = os.path.join(root, file)
                                logging.info(f"Fichier {td_info['td_name']} trouvé lors de la recherche approfondie: {full_path}")
                                return full_path
        
        logging.warning(f"Aucun fichier trouvé pour '{normalized_filename}' de l'étudiant '{student_name}'")
        return None
    
    def _is_matching_file(self, file_lower, normalized_filename, keywords, strict=False):
        """Vérifie si un fichier correspond au nom recherché ou aux mots-clés.
        
        Args:
            file_lower: Nom du fichier en minuscules
            normalized_filename: Nom de fichier recherché normalisé
            keywords: Liste de mots-clés à rechercher
            strict: Si True, nécessite une correspondance plus stricte
            
        Returns:
            bool: True si le fichier correspond, False sinon
        """
        # Correspondance directe entre noms
        if normalized_filename in file_lower:
            return True
            
        # Correspondance par mots-clés
        if keywords:
            # En mode strict, exiger au moins un mot-clé dans le nom du fichier
            if strict:
                return any(keyword in file_lower for keyword in keywords if len(keyword) > 3)
            else:
                # En mode normal, accepter des correspondances partielles
                return any(
                    part in file_lower 
                    for part in normalized_filename.replace('-', ' ').split() 
                    if len(part) > 3
                )
    
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
            # Extraire les informations sur l'exercice
            file_name = os.path.basename(file_path)
            base_name, ext = os.path.splitext(file_name)
            
            # Identifier le type d'exercice
            exercise_info = self._extract_assessment_info(file_name.lower())
            exercise_type = "Non déterminé"
            if exercise_info["td_name"]:
                exercise_type = f"{exercise_info['td_name']}"
                if exercise_info["exercise_id"]:
                    exercise_type += f"/{exercise_info['exercise_id']}"
                elif exercise_info["keywords"]:
                    exercise_type += f"/{'-'.join(exercise_info['keywords'])}"
            
            logging.info(f"Exécution de l'exercice {exercise_type} avec {len(test_inputs)} entrées")
            
            # Vérifier si le fichier est un fichier Java
            if ext.lower() == '.java':
                # Prétraiter le fichier pour éviter les erreurs de nom de classe/fichier
                file_path = self._preprocess_java_file(file_path)
                
                # Exécuter le code avec les entrées de test
                results = self.executor.test_with_inputs(file_path, test_inputs)
                
                # Ajouter des informations d'identification pour chaque résultat
                for result in results:
                    # Ajouter une référence au type d'exercice pour identifier 
                    # clairement à quel exercice correspond ce résultat
                    result["exercise_type"] = exercise_type
                    
                    # Enregistrer l'entrée et la sortie pour le débogage
                    input_val = result["input"]
                    stdout = result.get("stdout", "")
                    logging.info(f"Résultat pour {exercise_type}, entrée: '{input_val}'\nSortie: '{stdout[:100]}...'")
                
                return results
            else:
                error_msg = f"Type de fichier non pris en charge: {file_path}"
                logging.error(error_msg)
                return [self._create_error_result(input_val, error_msg) for input_val in test_inputs]
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