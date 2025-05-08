"""
Module pour la génération de feedback avec l'API Gemini.
"""

import os
import json
import logging
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox

from teach_assit.gui.feedback.feedback_thread import FeedbackThread
from teach_assit.gui.feedback.utils import extract_note_from_feedback, extract_exercise_notes


class FeedbackGenerator(QObject):
    """Gestionnaire de génération de feedback."""
    
    feedback_generated = pyqtSignal(str)
    generation_error = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, data_manager, file_locator, assessment_loader, db_manager=None):
        """
        Initialise le générateur de feedback.
        
        Args:
            data_manager: Gestionnaire de données
            file_locator: Localisateur de fichiers d'exercices
            assessment_loader: Chargeur d'évaluations
            db_manager: Gestionnaire de base de données pour sauvegarder le feedback
        """
        super().__init__()
        self.data_manager = data_manager
        self.file_locator = file_locator
        self.assessment_loader = assessment_loader
        self.db_manager = db_manager
        self.feedback_thread = None
        self.current_student = ""
        self.current_assessment_id = ""
    
    def generate_feedback(self, api_key, student, exercise_ids):
        """
        Génère le feedback pour les exercices d'un étudiant.
        
        Args:
            api_key: Clé API Gemini
            student: Nom de l'étudiant
            exercise_ids: Liste des identifiants d'exercices
            
        Returns:
            bool: True si la génération a commencé avec succès
        """
        if not api_key:
            self.generation_error.emit("Veuillez configurer une clé API Gemini valide.")
            return False
            
        if not student:
            self.generation_error.emit("Veuillez sélectionner un étudiant.")
            return False
            
        if not exercise_ids:
            self.generation_error.emit("Aucun exercice trouvé pour cet étudiant. Veuillez synchroniser avec les résultats.")
            return False
            
        self.current_student = student
        
        try:
            # Émettre un signal de progression initiale
            self.progress_updated.emit(10)
            
            # Préparer la liste des données d'exercices
            all_exercises_data = self._prepare_exercises_data(student, exercise_ids)
            
            # Vérifier si nous avons des exercices valides
            valid_exercises = sum(1 for ex in all_exercises_data if ex.get('code') and len(ex.get('code', '').strip()) > 100)
            
            if valid_exercises == 0:
                self.generation_error.emit("Aucun exercice avec du code valide n'a été trouvé. Veuillez vérifier les fichiers source.")
                return False
                
            logging.info(f"Préparation de {len(all_exercises_data)} exercices (dont {valid_exercises} valides) pour {student}")
            
            # Créer un thread pour l'API Gemini
            self.feedback_thread = FeedbackThread(
                api_key=api_key,
                student_name=student,
                exercises_data=all_exercises_data
            )
            
            # Connecter les signaux
            self.feedback_thread.feedback_ready.connect(self._on_feedback_ready)
            self.feedback_thread.error_occurred.connect(self._on_feedback_error)
            self.feedback_thread.progress_changed.connect(self.progress_updated)
            
            # Démarrer le thread
            self.feedback_thread.start()
            return True
            
        except Exception as e:
            error_message = f"Erreur lors de la génération du feedback: {str(e)}"
            logging.error(error_message)
            import traceback
            logging.error(traceback.format_exc())
            self.generation_error.emit(error_message)
            return False
    
    def _prepare_exercises_data(self, student, exercise_ids):
        """
        Prépare les données d'exercices pour la génération de feedback.
        
        Args:
            student: Nom de l'étudiant
            exercise_ids: Liste des identifiants d'exercices
            
        Returns:
            list: Liste des données d'exercices préparées
        """
        all_exercises_data = []
        
        for exercise_id in exercise_ids:
            # Rechercher le fichier associé à cet exercice
            exercise_file = self.file_locator.find_exercise_file(student, exercise_id)
            
            if not exercise_file:
                logging.warning(f"Fichier non trouvé pour l'exercice {exercise_id} de l'étudiant {student}.")
                continue
                
            # Récupérer les données d'exécution et d'analyse
            execution_results, analysis_results = self.data_manager.get_execution_analysis(
                student, exercise_id
            )
                
            # Récupérer la configuration de l'exercice
            exercise_config = self._get_exercise_config(exercise_id)
            
            # Récupérer le code source
            code = ""
            try:
                with open(exercise_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                logging.info(f"Code source lu depuis {exercise_file} pour l'exercice {exercise_id}: {len(code)} caractères")
            except Exception as e:
                logging.error(f"Erreur lors de la lecture du fichier {exercise_file}: {str(e)}")
            
            # Déterminer le statut actuel
            status = "Non évalué"
            
            # Vérifier si un résultat existe déjà
            result_data = self.data_manager.get_result_data(student, exercise_id) or ""
            
            # Ajouter les données de cet exercice
            exercise_data = {
                'id': exercise_id,
                'code': code,
                'file_path': exercise_file,
                'analysis': analysis_results,
                'execution': execution_results,
                'config': exercise_config,
                'status': status,
                'result': result_data
            }
            
            # Ajouter l'ID de l'évaluation actuelle si disponible
            if self.current_assessment_id:
                exercise_data['assessment_id'] = self.current_assessment_id
                
            all_exercises_data.append(exercise_data)
            
        return all_exercises_data
    
    def _get_exercise_config(self, exercise_id):
        """
        Récupère la configuration d'un exercice en essayant plusieurs méthodes.
        
        Args:
            exercise_id: Identifiant de l'exercice
            
        Returns:
            dict: Configuration de l'exercice ou un dictionnaire vide si non trouvée
        """
        # 1. D'abord via l'AssessmentLoader
        exercise_config = self.assessment_loader.get_exercise_config(exercise_id)
        
        # 2. Essayer avec un ID normalisé
        if not exercise_config:
            from teach_assit.gui.feedback.configuration import ExerciseIdNormalizer
            normalized_id = ExerciseIdNormalizer.normalize(exercise_id)
            logging.info(f"Tentative avec ID normalisé: {normalized_id}")
            exercise_config = self.assessment_loader.get_exercise_config(normalized_id)
        
        # 3. Essayer directement dans le data_manager
        if not exercise_config and hasattr(self.data_manager, 'get_exercise_config'):
            exercise_config = self.data_manager.get_exercise_config(exercise_id)
        
        # 4. Rechercher par mots-clés dans les IDs connus
        if not exercise_config:
            # Essayer de faire correspondre avec des exercices connus
            all_configs = self.assessment_loader.get_all_exercise_configs()
            for config_id, config in all_configs.items():
                # Vérifier si l'ID contient des mots-clés pertinents
                if ("fonction-racine" in exercise_id.lower() and "racine" in config_id.lower()) or \
                   ("comptage-mots" in exercise_id.lower() and "mot" in config_id.lower()) or \
                   (exercise_id.lower() in config_id.lower()) or (config_id.lower() in exercise_id.lower()):
                    exercise_config = config
                    logging.info(f"Configuration trouvée par correspondance de mots-clés: {config_id}")
                    break
        
        # 5. Utiliser une référence directe au fichier de configuration si elle existe
        if not exercise_config:
            # Construire le chemin direct vers la configuration possible
            config_path = os.path.join(os.getcwd(), "configs", f"{exercise_id}.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        exercise_config = json.load(f)
                        logging.info(f"Configuration chargée directement depuis le fichier: {config_path}")
                except Exception as e:
                    logging.error(f"Erreur lors du chargement direct de la configuration: {str(e)}")
        
        return exercise_config or {}
    
    @pyqtSlot(str)
    def _on_feedback_ready(self, feedback):
        """
        Appelé lorsque le feedback est généré.
        
        Args:
            feedback: Texte du feedback généré
        """
        try:
            # Émettre le signal avec le feedback généré
            self.feedback_generated.emit(feedback)
            
            # Sauvegarder le feedback dans la base de données si disponible
            if self.db_manager and self.current_student:
                # Enregistrer le feedback
                feedback_id = self.db_manager.add_feedback(
                    self.current_student,
                    self.current_assessment_id,
                    feedback
                )
                
                if feedback_id > 0:
                    logging.info(f"Feedback enregistré dans la base de données avec l'ID {feedback_id}")
                else:
                    logging.error("Erreur lors de l'enregistrement du feedback dans la base de données")
            
        except Exception as e:
            logging.error(f"Erreur lors de la finalisation du feedback: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
    
    @pyqtSlot(str)
    def _on_feedback_error(self, error_msg):
        """
        Appelé en cas d'erreur lors de la génération du feedback.
        
        Args:
            error_msg: Message d'erreur
        """
        # Émettre le signal d'erreur
        self.generation_error.emit(error_msg)
        
    def set_current_assessment(self, assessment_id):
        """
        Définit l'ID de l'évaluation actuelle.
        
        Args:
            assessment_id: Identifiant de l'évaluation
        """
        self.current_assessment_id = assessment_id 