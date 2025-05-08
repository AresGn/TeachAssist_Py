"""
Gestionnaires d'événements et callbacks pour le module de feedback.
"""

import os
import re
import glob
import logging
import json
from PyQt5.QtWidgets import QMessageBox

from teach_assit.gui.feedback.utils import test_api_connection, save_feedback_to_file
from teach_assit.gui.feedback.configuration import ExerciseIdNormalizer


class ExerciseFileLocator:
    """Classe utilitaire pour localiser les fichiers d'exercices."""
    
    def __init__(self, data_manager, assessment_loader):
        """
        Initialise le localisateur de fichiers d'exercices.
        
        Args:
            data_manager: Gestionnaire de données pour accéder au cache des chemins de fichiers
            assessment_loader: Chargeur d'évaluations pour obtenir les patterns d'exercices
        """
        self.data_manager = data_manager
        self.assessment_loader = assessment_loader
    
    def find_exercise_file(self, student, exercise_id):
        """
        Trouve le fichier correspondant à l'exercice pour un étudiant donné.
        
        Args:
            student: Nom de l'étudiant
            exercise_id: Identifiant de l'exercice
            
        Returns:
            str: Chemin du fichier trouvé ou None si non trouvé
        """
        file_path = None
        logging.info(f"Recherche du fichier pour l'exercice {exercise_id} de l'étudiant {student}")
        
        # Vérifier d'abord si nous avons déjà le chemin dans le data_manager
        if hasattr(self.data_manager, 'get_exercise_file_path'):
            stored_path = self.data_manager.get_exercise_file_path(student, exercise_id)
            if stored_path and os.path.exists(stored_path):
                logging.info(f"Fichier trouvé dans le cache du data_manager: {stored_path}")
                return stored_path
        
        # Ensuite vérifier si le chemin est déjà connu dans le cache générique du data_manager
        if hasattr(self.data_manager, 'exercise_file_paths') and exercise_id in self.data_manager.exercise_file_paths:
            file_path = self.data_manager.exercise_file_paths.get(exercise_id)
            if os.path.exists(file_path):
                logging.info(f"Fichier trouvé dans le cache générique du data_manager: {file_path}")
                # Stocker dans le data_manager spécifique pour utilisation future
                if hasattr(self.data_manager, 'store_exercise_file_path'):
                    self.data_manager.store_exercise_file_path(student, exercise_id, file_path)
                return file_path
        
        # Obtenir les patterns de recherche pour cet exercice
        patterns = self.assessment_loader.get_exercise_patterns(exercise_id)
        logging.info(f"Patterns de recherche pour {exercise_id}: {patterns}")
        
        # Rechercher dans les dossiers potentiels des TDs
        search_dirs = []
        
        # Ajouter tous les dossiers potentiels pour toutes les évaluations
        for td_dir in glob.glob(os.path.join(os.getcwd(), "tests", "java_samples", "*")):
            student_dir = os.path.join(td_dir, student)
            if os.path.exists(student_dir):
                search_dirs.append(student_dir)
        
        logging.info(f"Dossiers de recherche: {search_dirs}")
        
        # Rechercher dans tous les dossiers avec tous les patterns
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            # Vérifier s'il y a des fichiers Java dans ce dossier
            java_files = glob.glob(os.path.join(search_dir, "*.java"))
            logging.info(f"Fichiers Java trouvés dans {search_dir}: {len(java_files)}")
            
            # Rechercher d'abord avec les patterns
            for pattern in patterns:
                for java_file in java_files:
                    # Vérifier si le nom du fichier contient le pattern
                    if pattern.lower() in os.path.basename(java_file).lower():
                        file_path = java_file
                        logging.info(f"Fichier trouvé avec pattern '{pattern}': {file_path}")
                        # Stocker pour utilisation future
                        self._store_found_path(student, exercise_id, file_path)
                        return file_path
            
            # Si toujours pas trouvé, essayer avec juste l'identifiant de l'exercice
            for java_file in java_files:
                if exercise_id.lower() in os.path.basename(java_file).lower():
                    file_path = java_file
                    logging.info(f"Fichier trouvé avec ID d'exercice: {file_path}")
                    # Stocker pour utilisation future
                    self._store_found_path(student, exercise_id, file_path)
                    return file_path
            
            # Si toujours pas trouvé, chercher avec un ID normalisé
            normalized_id = ExerciseIdNormalizer.normalize(exercise_id)
            for java_file in java_files:
                file_name = os.path.basename(java_file).lower()
                if normalized_id in file_name:
                    file_path = java_file
                    logging.info(f"Fichier trouvé avec ID normalisé '{normalized_id}': {file_path}")
                    # Stocker pour utilisation future
                    self._store_found_path(student, exercise_id, file_path)
                    return file_path
            
            # Si toujours pas trouvé, chercher par analyse des fichiers
            for java_file in java_files:
                file_name = os.path.basename(java_file)
                # Extraire un numéro potentiel (ex: Exercice01.java -> 01)
                number_match = re.search(r'(\d+)', file_name)
                if number_match:
                    number = number_match.group(1)
                    # Vérifier si ce numéro est dans l'ID de l'exercice
                    if number in exercise_id:
                        file_path = java_file
                        logging.info(f"Fichier trouvé par correspondance de numéro: {file_path}")
                        # Stocker pour utilisation future
                        self._store_found_path(student, exercise_id, file_path)
                        return file_path
            
            # Si on a toujours rien trouvé et qu'il n'y a qu'un seul fichier, l'utiliser
            if len(java_files) == 1:
                file_path = java_files[0]
                logging.info(f"Utilisation du seul fichier disponible: {file_path}")
                # Stocker pour utilisation future
                self._store_found_path(student, exercise_id, file_path)
                return file_path
        
        logging.warning(f"Aucun fichier trouvé pour l'exercice {exercise_id} de l'étudiant {student}")
        return None
    
    def _store_found_path(self, student, exercise_id, file_path):
        """Stocke le chemin trouvé dans les caches appropriés."""
        if hasattr(self.data_manager, 'exercise_file_paths'):
            self.data_manager.exercise_file_paths[exercise_id] = file_path
        if hasattr(self.data_manager, 'store_exercise_file_path'):
            self.data_manager.store_exercise_file_path(student, exercise_id, file_path)


class FeedbackHandler:
    """Classe pour gérer les événements liés au feedback."""
    
    def __init__(self, widget, config_manager, data_manager, file_locator):
        """
        Initialise le gestionnaire de feedback.
        
        Args:
            widget: Widget de feedback principal
            config_manager: Gestionnaire de configuration
            data_manager: Gestionnaire de données
            file_locator: Localisateur de fichiers d'exercices
        """
        self.widget = widget
        self.config_manager = config_manager
        self.data_manager = data_manager
        self.file_locator = file_locator
    
    def test_api_connection(self, api_key):
        """
        Teste la connexion à l'API Gemini.
        
        Args:
            api_key: Clé API à tester
            
        Returns:
            bool: True si la connexion est réussie
        """
        if not api_key:
            self.widget.feedback_section.set_feedback_text("❌ Veuillez entrer une clé API")
            return False
            
        self.widget.feedback_section.set_feedback_text("Test de connexion en cours...")
        self.widget.header_section.test_api_button.setEnabled(False)
        
        success, message = test_api_connection(api_key)
        self.widget.feedback_section.set_feedback_text(f"{'✅' if success else '❌'} {message}")
        
        if success:
            self.config_manager.save_api_key(api_key)
            
        self.widget.header_section.test_api_button.setEnabled(True)
        return success
    
    def handle_exercise_selection(self, student, exercise_id):
        """
        Gère la sélection d'un exercice.
        
        Args:
            student: Nom de l'étudiant
            exercise_id: Identifiant de l'exercice
        """
        # Récupérer les données d'analyse et d'exécution
        code, analysis_results, execution_results = self.data_manager.get_analysis_data(student, exercise_id)
        
        # Message de sélection
        message = f"Exercice sélectionné: {exercise_id}\nÉtudiant: {student}\n\nCliquez sur 'Générer feedback' pour obtenir une analyse par IA."
        self.widget.feedback_section.set_feedback_text(message)
    
    def download_markdown(self, student_name):
        """
        Télécharge le feedback au format Markdown.
        
        Args:
            student_name: Nom de l'étudiant pour le nom de fichier par défaut
        """
        feedback_text = self.widget.feedback_section.get_feedback_text()
        if not feedback_text:
            return
            
        if not student_name:
            student_name = "ETUDIANT"
            
        # Suggérer un nom de fichier basé sur le nom de l'étudiant
        filename, _ = QMessageBox.QFileDialog.getSaveFileName(
            self.widget,
            "Enregistrer le feedback",
            f"{student_name}.md",
            "Markdown (*.md)"
        )
        
        if filename:
            success, message = save_feedback_to_file(
                feedback_text,
                student_name,
                filename
            )
            
            if success:
                QMessageBox.information(self.widget, "Sauvegarde réussie", f"Le feedback a été enregistré dans {filename}")
            else:
                QMessageBox.warning(self.widget, "Erreur de sauvegarde", f"Erreur lors de l'enregistrement: {message}")


class ResultsSynchronizer:
    """Classe pour synchroniser avec l'onglet Résultats."""
    
    def __init__(self, data_manager, assessment_loader):
        """
        Initialise le synchronisateur de résultats.
        
        Args:
            data_manager: Gestionnaire de données
            assessment_loader: Chargeur d'évaluations
        """
        self.data_manager = data_manager
        self.assessment_loader = assessment_loader
    
    def sync_with_results(self, results_widget, student_list_callback):
        """
        Synchronise avec l'onglet Résultats.
        
        Args:
            results_widget: Widget de résultats à synchroniser
            student_list_callback: Fonction à appeler avec la liste des étudiants
            
        Returns:
            list: Liste des étudiants récupérés
        """
        if not results_widget:
            logging.error("Impossible de synchroniser: pas de référence au widget de résultats")
            return []
        
        try:
            logging.info("Début de la synchronisation avec les résultats")
            
            # Récupérer la liste des étudiants depuis le widget de résultats
            students = []
            
            # Vérifier si nous avons accès à la méthode get_students
            if hasattr(results_widget, 'get_students'):
                students = results_widget.get_students()
                logging.info(f"Étudiants récupérés via get_students: {len(students)}")
            # Sinon, essayer de lire le tableau des résultats
            elif hasattr(results_widget, 'results_table'):
                # Parcourir le tableau pour extraire tous les étudiants uniques
                for i in range(results_widget.results_table.rowCount()):
                    student_item = results_widget.results_table.item(i, 0)
                    if student_item:
                        student_name = student_item.text()
                        if student_name and student_name not in students:
                            students.append(student_name)
                logging.info(f"Étudiants extraits du tableau: {len(students)}")
                
            # Si on n'a pas trouvé d'étudiants, essayer avec une méthode alternative
            if not students and hasattr(results_widget, 'get_student_list'):
                students = results_widget.get_student_list()
                logging.info(f"Étudiants récupérés via get_student_list: {len(students)}")
            
            # Récupérer l'évaluation actuelle
            current_assessment = None
            if hasattr(results_widget, 'get_current_assessment_name'):
                current_assessment = results_widget.get_current_assessment_name()
                logging.info(f"Évaluation actuelle détectée: {current_assessment}")
            
            # Extraire les chemins de fichiers pour chaque étudiant
            for student in students:
                # Extrait les chemins de fichiers directement depuis l'écran Results
                if hasattr(self.data_manager, 'extract_file_paths_from_results'):
                    extracted_paths = self.data_manager.extract_file_paths_from_results(student)
                    logging.info(f"Extraction directe: {len(extracted_paths)} fichiers trouvés pour {student}")
                
                # Méthode de secours: tenter d'extraire des exercices
                if hasattr(results_widget, 'get_exercises_for_student') and hasattr(self.data_manager, 'store_exercise_file_path'):
                    exercises = results_widget.get_exercises_for_student(student)
                    for exercise in exercises:
                        exercise_id = exercise.get('id')
                        file_path = exercise.get('path')
                        if exercise_id and file_path and os.path.exists(file_path):
                            self.data_manager.store_exercise_file_path(student, exercise_id, file_path)
                            logging.info(f"Fichier préchargé pour {student}/{exercise_id}: {file_path}")
            
            # Retourner la liste des étudiants
            logging.info(f"Synchronisation terminée, {len(students)} étudiants chargés")
            
            # Appeler le callback avec la liste des étudiants
            if student_list_callback and callable(student_list_callback):
                student_list_callback(students)
                
            return students
            
        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return [] 