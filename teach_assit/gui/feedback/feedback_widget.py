"""
Widget principal pour l'onglet Notes & Feedback.
"""

import os
import json
import logging
import glob
import re
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
                            QProgressBar, QFrame, QGroupBox, QFileDialog, QLineEdit, QMessageBox, QScrollArea, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from teach_assit.gui.styles import MAIN_STYLE
from teach_assit.gui.feedback.feedback_thread import FeedbackThread
from teach_assit.gui.feedback.data_manager import DataManager
from teach_assit.gui.feedback.assessment_loader import AssessmentLoader
from teach_assit.gui.feedback.utils import (extract_note_from_feedback, 
                                          extract_exercise_notes,
                                          test_api_connection,
                                          save_feedback_to_file)
from teach_assit.core.database.db_manager import DatabaseManager

class FeedbackWidget(QWidget):
    """Widget pour l'onglet Notes & Feedback intégrant l'API Gemini"""
    
    API_KEY_SETTING = "api_key_gemini"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FeedbackWidget")
        self.setStyleSheet(MAIN_STYLE)
        
        # État initial
        self.api_key = ""
        self.current_student = ""
        self.selected_exercise = ""
        self.feedback_thread = None
        self.results_widget = None
        
        # Initialiser le gestionnaire de base de données
        self.db_manager = DatabaseManager()
        
        # Initialiser le chargeur d'évaluations
        self.assessment_loader = AssessmentLoader()
        
        # Initialiser le gestionnaire de données
        self.data_manager = DataManager()
        
        # Configuration du layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Setup de l'interface
        self._setup_header()
        self._setup_exercises_section()
        self._setup_feedback_section()
        
        self.main_layout.addStretch(1)
        
        # Charger les paramètres sauvegardés
        self._load_settings()
        
    def _setup_header(self):
        """Configure la section d'en-tête (API Key et sélection d'étudiant)"""
        header_layout = QVBoxLayout()
        
        # Section API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("Clé API Gemini:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Entrez votre clé API Gemini ici...")
        self.api_key_input.textChanged.connect(self._on_api_key_changed)
        api_key_layout.addWidget(self.api_key_input, stretch=1)
        self.test_api_button = QPushButton("Tester la connexion")
        self.test_api_button.clicked.connect(self.test_api_connection)
        api_key_layout.addWidget(self.test_api_button)
        header_layout.addLayout(api_key_layout)
        
        # Section étudiant
        student_layout = QHBoxLayout()
        student_layout.addWidget(QLabel("Étudiant:"))
        self.student_combo = QComboBox()
        self.student_combo.currentIndexChanged.connect(self.on_student_changed)
        student_layout.addWidget(self.student_combo)
        student_layout.addStretch()
        
        # Bouton de synchronisation
        self.sync_button = QPushButton("Synchroniser avec Résultats")
        self.sync_button.clicked.connect(self.sync_with_results)
        student_layout.addWidget(self.sync_button)
        
        # Affichage de la note
        self.note_label = QLabel("Note: --/20")
        student_layout.addWidget(self.note_label)
        header_layout.addLayout(student_layout)
        
        self.main_layout.addLayout(header_layout)
        
    def _setup_exercises_section(self):
        """Configure la section des exercices avec le tableau"""
        exercises_layout = QVBoxLayout()
        exercises_layout.addWidget(QLabel("Exercices:"))
        
        # Tableau des exercices
        self.exercises_table = QTableWidget(0, 3)  # Démarrer avec 0 ligne
        self.exercises_table.setHorizontalHeaderLabels(["Exercice", "Fichier", "État"])
        self.exercises_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.exercises_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.exercises_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.exercises_table.verticalHeader().setVisible(True)
        self.exercises_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.exercises_table.setSelectionMode(QTableWidget.SingleSelection)
        self.exercises_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.exercises_table.cellClicked.connect(self.on_exercise_selected)
        exercises_layout.addWidget(self.exercises_table)
        
        self.main_layout.addLayout(exercises_layout)
        
    def _setup_feedback_section(self):
        """Configure la section de feedback avec la zone de texte et les boutons"""
        feedback_layout = QVBoxLayout()
        
        # Résultats de l'analyse (invisible par défaut, sera rempli lors de la génération)
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(0)  # Caché par défaut
        self.results_text.setVisible(False)
        feedback_layout.addWidget(self.results_text)
        
        # Texte du feedback
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setMinimumHeight(200)
        feedback_layout.addWidget(self.feedback_text)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        feedback_layout.addWidget(self.progress_bar)
        
        # Layout pour les boutons
        buttons_layout = QHBoxLayout()
        
        # Bouton Générer feedback
        self.generate_button = QPushButton("Générer feedback")
        self.generate_button.clicked.connect(self.generate_feedback)
        self.generate_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.generate_button)
        
        # Bouton Télécharger en Markdown
        self.download_button = QPushButton("Télécharger en Markdown")
        self.download_button.clicked.connect(self.download_markdown)
        self.download_button.setMinimumHeight(40)
        self.download_button.setEnabled(False)  # Désactivé jusqu'à ce que le feedback soit généré
        buttons_layout.addWidget(self.download_button)
        
        feedback_layout.addLayout(buttons_layout)
        
        self.main_layout.addLayout(feedback_layout)
    
    def _load_settings(self):
        """Charge la clé API depuis la base de données"""
        try:
            self.api_key = self.db_manager.get_setting(self.API_KEY_SETTING, "")
            if self.api_key:
                self.api_key_input.setText(self.api_key)
                logging.info("Clé API chargée depuis la base de données")
        except Exception as e:
            logging.error(f"Erreur lors du chargement de la clé API: {str(e)}")
    
    def _save_settings(self):
        """Sauvegarde la clé API dans la base de données"""
        try:
            self.db_manager.save_setting(
                self.API_KEY_SETTING, 
                self.api_key, 
                "Clé API Gemini pour la génération de feedback"
            )
            logging.info("Clé API sauvegardée dans la base de données")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de la clé API: {str(e)}")
    
    def _on_api_key_changed(self):
        """Appelé lorsque la clé API est modifiée dans le champ texte"""
        self.api_key = self.api_key_input.text().strip()
        self._save_settings()
        
    def set_results_widget(self, results_widget):
        """Définit la référence au widget de résultats pour récupérer les données"""
        self.results_widget = results_widget
        self.data_manager.results_widget = results_widget
        
        # Synchroniser automatiquement lors de l'initialisation
        self.sync_with_results()
    
    def sync_with_results(self):
        """Synchronise la liste des étudiants avec l'onglet Résultats"""
        if not self.results_widget:
            logging.error("Impossible de synchroniser: pas de référence au widget de résultats")
            QMessageBox.warning(self, "Erreur", "Impossible de synchroniser avec les résultats")
            return
        
        try:
            logging.info("Début de la synchronisation avec les résultats")
            
            # Récupérer la liste des étudiants depuis le widget de résultats
            students = []
            
            # Vérifier si nous avons accès à la méthode get_students
            if hasattr(self.results_widget, 'get_students'):
                students = self.results_widget.get_students()
                logging.info(f"Étudiants récupérés via get_students: {len(students)}")
            # Sinon, essayer de lire le tableau des résultats
            elif hasattr(self.results_widget, 'results_table'):
                # Parcourir le tableau pour extraire tous les étudiants uniques
                for i in range(self.results_widget.results_table.rowCount()):
                    student_item = self.results_widget.results_table.item(i, 0)
                    if student_item:
                        student_name = student_item.text()
                        if student_name and student_name not in students:
                            students.append(student_name)
                logging.info(f"Étudiants extraits du tableau: {len(students)}")
                
            # Si on n'a pas trouvé d'étudiants, essayer avec une méthode alternative
            if not students and hasattr(self.results_widget, 'get_student_list'):
                students = self.results_widget.get_student_list()
                logging.info(f"Étudiants récupérés via get_student_list: {len(students)}")
                
            # Mettre à jour le combobox avec les étudiants
            previous_student = self.student_combo.currentText()
            self.student_combo.clear()
            
            for student in students:
                self.student_combo.addItem(student)
            
            # Récupérer l'évaluation actuelle
            current_assessment = None
            if hasattr(self.results_widget, 'get_current_assessment_name'):
                current_assessment = self.results_widget.get_current_assessment_name()
                logging.info(f"Évaluation actuelle détectée: {current_assessment}")
            
            # Utiliser la nouvelle méthode d'extraction directe des chemins de fichiers
            for student in students:
                # Extrait les chemins de fichiers directement depuis l'écran Results
                if hasattr(self.data_manager, 'extract_file_paths_from_results'):
                    extracted_paths = self.data_manager.extract_file_paths_from_results(student)
                    logging.info(f"Extraction directe: {len(extracted_paths)} fichiers trouvés pour {student}")
                
                # Méthode de secours: tenter d'extraire des exercices
                if hasattr(self.results_widget, 'get_exercises_for_student') and hasattr(self.data_manager, 'store_exercise_file_path'):
                    exercises = self.results_widget.get_exercises_for_student(student)
                    for exercise in exercises:
                        exercise_id = exercise.get('id')
                        file_path = exercise.get('path')
                        if exercise_id and file_path and os.path.exists(file_path):
                            self.data_manager.store_exercise_file_path(student, exercise_id, file_path)
                            logging.info(f"Fichier préchargé pour {student}/{exercise_id}: {file_path}")
            
            # Restaurer l'étudiant précédemment sélectionné si possible
            if previous_student in students:
                index = self.student_combo.findText(previous_student)
                if index >= 0:
                    self.student_combo.setCurrentIndex(index)
                    logging.info(f"Étudiant précédent restauré: {previous_student}")
            
            # Mettre à jour les exercices pour l'étudiant sélectionné
            self.update_exercises_for_student(self.student_combo.currentText())
            
            logging.info(f"Synchronisation terminée, {len(students)} étudiants chargés")
        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue lors de la synchronisation: {str(e)}")
    
    def update_exercises_for_student(self, student):
        """Met à jour la liste des exercices pour un étudiant donné"""
        # Effacer le tableau actuel
        self.exercises_table.setRowCount(0)
        
        if not student:
            return
        
        try:
            # Obtenir l'évaluation actuelle
            current_assessment = None
            if self.results_widget and hasattr(self.results_widget, 'get_current_assessment_name'):
                current_assessment = self.results_widget.get_current_assessment_name()
                logging.info(f"Évaluation actuelle détectée: {current_assessment}")
            
            # 1. D'abord, obtenir la liste de tous les exercices configurés
            all_exercise_ids = []
            normalized_map = {}  # Map pour stocker les correspondances entre les IDs normalisés et originaux
            
            # Obtenir les exercices de l'évaluation actuelle depuis les fichiers de configuration
            if current_assessment:
                assessment_exercises = self.assessment_loader.get_exercise_ids_for_assessment(current_assessment)
                if assessment_exercises:
                    logging.info(f"Exercices trouvés dans la configuration pour {current_assessment}: {assessment_exercises}")
                    for ex_id in assessment_exercises:
                        normalized_id = self._normalize_exercise_id(ex_id)
                        if normalized_id not in normalized_map:
                            normalized_map[normalized_id] = ex_id
                            all_exercise_ids.append(ex_id)
                        else:
                            logging.info(f"Exercice {ex_id} normalisé vers {normalized_id} déjà présent sous {normalized_map[normalized_id]}")
            
            # 2. Ajout des exercices depuis les résultats
            if self.results_widget and hasattr(self.results_widget, 'results_table'):
                # Parcourir tous les résultats pour cet étudiant
                for i in range(self.results_widget.results_table.rowCount()):
                    student_item = self.results_widget.results_table.item(i, 0)
                    if student_item and student_item.text() == student:
                        # Récupérer l'exercice
                        exercise_widget = self.results_widget.results_table.cellWidget(i, 1)
                        if exercise_widget and hasattr(exercise_widget, 'get_exercise_name'):
                            exercise_id = exercise_widget.get_exercise_name()
                            if exercise_id:
                                normalized_id = self._normalize_exercise_id(exercise_id)
                                if normalized_id not in normalized_map:
                                    normalized_map[normalized_id] = exercise_id
                                    all_exercise_ids.append(exercise_id)
                                    logging.info(f"Exercice trouvé dans les résultats: {exercise_id} (normalisé: {normalized_id})")
                                else:
                                    logging.info(f"Exercice {exercise_id} déjà présent sous {normalized_map[normalized_id]}")
            
            # 3. Chercher les fichiers Java des exercices
            exercise_files = {}
            
            # 3.1 Parcourir tous les dossiers des évaluations
            student_dirs = []
            for assessment_dir in glob.glob(os.path.join(os.getcwd(), "tests", "java_samples", "*")):
                if os.path.isdir(assessment_dir):
                    student_dir = os.path.join(assessment_dir, student)
                    if os.path.exists(student_dir):
                        student_dirs.append(student_dir)
                        logging.info(f"Dossier d'étudiant trouvé: {student_dir}")
            
            # 3.2 Chercher tous les fichiers Java de l'étudiant
            for student_dir in student_dirs:
                for java_file in glob.glob(os.path.join(student_dir, "*.java")):
                    file_name = os.path.basename(java_file)
                    logging.info(f"Fichier Java trouvé: {file_name} dans {student_dir}")
                    
                    # Essayer de déterminer à quel exercice ce fichier correspond
                    matched_exercise = None
                    
                    # Parcourir tous les exercices connus
                    for exercise_id in all_exercise_ids:
                        # Obtenir les patterns pour cet exercice
                        patterns = self.assessment_loader.get_exercise_patterns(exercise_id)
                        
                        # Vérifier si le nom du fichier correspond à un pattern
                        for pattern in patterns:
                            if pattern.lower() in file_name.lower():
                                matched_exercise = exercise_id
                                logging.info(f"Fichier {file_name} correspond à l'exercice {exercise_id}")
                                break
                        
                        # Si on a déjà trouvé, pas besoin de continuer
                        if matched_exercise:
                            break
                    
                    # Si on n'a pas trouvé de correspondance, vérifier si l'ID de l'exercice est dans le nom du fichier
                    if not matched_exercise:
                        for exercise_id in all_exercise_ids:
                            if exercise_id.lower() in file_name.lower():
                                matched_exercise = exercise_id
                                logging.info(f"Fichier {file_name} pourrait correspondre à l'exercice {exercise_id}")
                                break
                    
                    # Si on a trouvé une correspondance, l'ajouter
                    if matched_exercise:
                        exercise_files[matched_exercise] = java_file
                    # Sinon, essayer de trouver un exercice qui pourrait correspondre
                    else:
                        # Extraire un identifiant potentiel du fichier (ex: si Exercice01.java -> 01)
                        potential_id = None
                        id_match = re.search(r'exercice[\-_]?(\d+)', file_name, re.IGNORECASE)
                        if id_match:
                            potential_id = id_match.group(1)
                            
                        # Si on a extrait un ID, chercher un exercice qui pourrait correspondre
                        if potential_id:
                            for exercise_id in all_exercise_ids:
                                if potential_id in exercise_id:
                                    matched_exercise = exercise_id
                                    exercise_files[matched_exercise] = java_file
                                    logging.info(f"Fichier {file_name} associé à l'exercice {exercise_id} par ID")
                                    break
            
            # 4. Si on n'a toujours pas assez d'exercices, chercher des fichiers qui pourraient être des exercices
            if len(exercise_files) < len(all_exercise_ids):
                # Parcourir tous les fichiers Java non associés
                for student_dir in student_dirs:
                    for java_file in glob.glob(os.path.join(student_dir, "*.java")):
                        file_name = os.path.basename(java_file)
                        # Vérifier si ce fichier n'est pas déjà associé à un exercice
                        if java_file not in exercise_files.values():
                            # Essayer d'identifier un exercice basé sur le nom du fichier
                            for exercise_id in all_exercise_ids:
                                if exercise_id not in exercise_files:
                                    # Stocker simplement ce fichier pour cet exercice
                                    exercise_files[exercise_id] = java_file
                                    logging.info(f"Association forcée de {file_name} à l'exercice {exercise_id}")
                                    break
            
            # 5. Remplir le tableau avec les exercices et leurs fichiers
            for exercise_id in all_exercise_ids:
                row = self.exercises_table.rowCount()
                self.exercises_table.insertRow(row)
                
                # ID de l'exercice
                self.exercises_table.setItem(row, 0, QTableWidgetItem(exercise_id))
                
                # Fichier associé
                file_path = exercise_files.get(exercise_id, "")
                file_name = os.path.basename(file_path) if file_path else "Non trouvé"
                self.exercises_table.setItem(row, 1, QTableWidgetItem(file_name))
                
                # État initial
                self.exercises_table.setItem(row, 2, QTableWidgetItem("En attente"))
                
                # Stocker le chemin du fichier pour une utilisation ultérieure
                if file_path and hasattr(self.data_manager, 'exercise_file_paths'):
                    self.data_manager.exercise_file_paths[exercise_id] = file_path
            
            # 6. Trier le tableau par identifiant d'exercice
            self.exercises_table.setSortingEnabled(True)
            self.exercises_table.sortItems(0, Qt.AscendingOrder)
            
            logging.info(f"Mise à jour du tableau d'exercices terminée pour {student}: {len(all_exercise_ids)} exercices trouvés")
            
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour des exercices: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
    
    def on_exercise_selected(self, row, column):
        """Appelé lorsqu'un exercice est sélectionné dans le tableau"""
        self.selected_exercise = self.exercises_table.item(row, 0).text()
        student = self.student_combo.currentText()
        
        # Récupérer les données d'analyse et d'exécution réelles
        code, analysis_results, execution_results = self.data_manager.get_analysis_data(student, self.selected_exercise)
        
        # Stocker les données pour une utilisation ultérieure
        self.current_code = code
        self.current_analysis = analysis_results
        self.current_execution = execution_results
        
        # Message de sélection
        self.feedback_text.setText(f"Exercice sélectionné: {self.selected_exercise}\nÉtudiant: {student}\n\nCliquez sur 'Générer feedback' pour obtenir une analyse par IA.")
    
    def test_api_connection(self):
        """Teste la connexion à l'API Gemini"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            self.feedback_text.setText("❌ Veuillez entrer une clé API")
            return
            
        self.feedback_text.setText("Test de connexion en cours...")
        self.test_api_button.setEnabled(False)
        
        success, message = test_api_connection(api_key)
        self.feedback_text.setText(f"{'✅' if success else '❌'} {message}")
        
        if success:
            self.api_key = api_key
            self._save_settings()
            
        self.test_api_button.setEnabled(True)
    
    def generate_feedback(self):
        """Génère le feedback pour tous les exercices de l'étudiant sélectionné"""
        self.current_student = self.student_combo.currentText()
        
        if not self.current_student:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un étudiant.")
            return
        
        try:
            # Afficher la barre de progression
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            
            # Récupérer le nombre total d'exercices
            total_rows = self.exercises_table.rowCount()
            
            # Préparer la liste des données d'exercices
            all_exercises_data = []
            
            for row in range(total_rows):
                exercise_id = self.exercises_table.item(row, 0).text()
                
                # Rechercher le fichier associé à cet exercice
                exercise_file = self._find_exercise_file(self.current_student, exercise_id)
                
                if not exercise_file:
                    logging.warning(f"Fichier non trouvé pour l'exercice {exercise_id} de l'étudiant {self.current_student}.")
                    continue
                    
                # Récupérer les données d'exécution et d'analyse
                execution_results, analysis_results = self.data_manager.get_execution_analysis(
                    self.current_student, exercise_id
                )
                    
                # Récupérer la configuration de l'exercice - essayer plusieurs méthodes
                exercise_config = None
                
                # 1. D'abord via l'AssessmentLoader
                exercise_config = self.assessment_loader.get_exercise_config(exercise_id)
                
                # 2. Essayer avec un ID normalisé
                if not exercise_config:
                    normalized_id = self._normalize_exercise_id(exercise_id)
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
                
                # Vérifier que nous avons bien une configuration
                if not exercise_config:
                    logging.error(f"Aucune configuration trouvée pour l'exercice {exercise_id}")
                    continue
                
                # Récupérer le status actuel et le résultat existant
                status = self.exercises_table.item(row, 2).text() if self.exercises_table.item(row, 2) else "Non évalué"
                
                # Récupérer le code source
                code = ""
                try:
                    with open(exercise_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    logging.info(f"Code source lu depuis {exercise_file} pour l'exercice {exercise_id}: {len(code)} caractères")
                except Exception as e:
                    logging.error(f"Erreur lors de la lecture du fichier {exercise_file}: {str(e)}")
                
                # Ajouter les données de cet exercice
                exercise_data = {
                    'id': exercise_id,
                    'code': code,
                    'file_path': exercise_file,  # Ajout du chemin du fichier pour référence
                    'analysis': analysis_results,
                    'execution': execution_results,
                    'config': exercise_config,
                    'status': status,
                    'result': ""  # Sera rempli si disponible
                }
                    
                # Vérifier si des résultats existent déjà pour cet exercice
                result_data = self.data_manager.get_result_data(self.current_student, exercise_id)
                if result_data:
                    exercise_data['result'] = result_data
                    
                all_exercises_data.append(exercise_data)
            
            # Vérifier si nous avons des exercices à évaluer
            if not all_exercises_data:
                QMessageBox.warning(self, "Attention", "Aucun exercice trouvé pour cet étudiant. Veuillez synchroniser avec les résultats.")
                self.progress_bar.setVisible(False)
                return
                
            # Créer un thread pour l'API Gemini
            self.feedback_thread = FeedbackThread(
                api_key=self.api_key,
                student_name=self.current_student,
                exercises_data=all_exercises_data
            )
            
            # Connecter les signaux
            self.feedback_thread.feedback_ready.connect(self.on_feedback_ready)
            self.feedback_thread.error_occurred.connect(self.on_feedback_error)
            self.feedback_thread.progress_changed.connect(self.progress_bar.setValue)
            
            # Désactiver les boutons pendant le traitement
            self.generate_button.setEnabled(False)
            self.sync_button.setEnabled(False)
            self.student_combo.setEnabled(False)
            self.exercises_table.setEnabled(False)
            
            # Démarrer le thread
            self.feedback_thread.start()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            error_message = f"Erreur lors de la génération du feedback: {str(e)}"
            logging.error(error_message)
            import traceback
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "Erreur", error_message)
    
    def _find_exercise_file(self, student, exercise_id):
        """Trouve le fichier correspondant à l'exercice pour un étudiant donné"""
        file_path = None
        logging.info(f"Recherche du fichier pour l'exercice {exercise_id} de l'étudiant {student}")
        
        # Vérifier d'abord si nous avons déjà le chemin dans le data_manager
        if hasattr(self.data_manager, 'get_exercise_file_path'):
            stored_path = self.data_manager.get_exercise_file_path(student, exercise_id)
            if stored_path and os.path.exists(stored_path):
                logging.info(f"Fichier trouvé dans le cache du data_manager par étudiant/exercice: {stored_path}")
                return stored_path
        
        # D'abord vérifier dans le tableau des exercices
        for row in range(self.exercises_table.rowCount()):
            table_exercise_id = self.exercises_table.item(row, 0).text()
            if table_exercise_id == exercise_id:
                file_item = self.exercises_table.item(row, 1)
                file_name = file_item.text() if file_item else ""
                if file_name and file_name != "Non trouvé":
                    logging.info(f"Fichier trouvé dans le tableau: {file_name}")
                    
                    # Vérifier d'abord dans temp_fixed_files (où les fichiers renommés sont stockés)
                    temp_dir = os.path.join(os.getcwd(), "temp_fixed_files")
                    if os.path.exists(temp_dir):
                        class_name_file = None
                        
                        # Extraire le nom de classe potentiel du fichier original (ex: RacineCarree.java)
                        if "fonction-racine" in exercise_id.lower() or "racine" in file_name.lower():
                            class_name_file = "RacineCarree.java"
                        elif "comptage-mots" in exercise_id.lower() or "mot" in file_name.lower():
                            class_name_file = "CompteurMots.java"
                        
                        # Chercher avec le nom de fichier original
                        potential_path = os.path.join(temp_dir, file_name)
                        if os.path.exists(potential_path):
                            logging.info(f"Fichier trouvé dans temp_fixed_files: {potential_path}")
                            # Stocker dans le data_manager pour utilisation future
                            if hasattr(self.data_manager, 'store_exercise_file_path'):
                                self.data_manager.store_exercise_file_path(student, exercise_id, potential_path)
                            return potential_path
                        
                        # Chercher avec le nom de classe déduit
                        if class_name_file:
                            potential_path = os.path.join(temp_dir, class_name_file)
                            if os.path.exists(potential_path):
                                logging.info(f"Fichier trouvé dans temp_fixed_files avec nom de classe: {potential_path}")
                                # Stocker dans le data_manager pour utilisation future
                                if hasattr(self.data_manager, 'store_exercise_file_path'):
                                    self.data_manager.store_exercise_file_path(student, exercise_id, potential_path)
                                return potential_path
                    
                    # Ensuite chercher dans les répertoires des étudiants
                    for td_dir in glob.glob(os.path.join(os.getcwd(), "tests", "java_samples", "*")):
                        student_dir = os.path.join(td_dir, student)
                        if os.path.exists(student_dir):
                            potential_path = os.path.join(student_dir, file_name)
                            if os.path.exists(potential_path):
                                logging.info(f"Chemin complet trouvé: {potential_path}")
                                # Stocker dans le data_manager pour utilisation future
                                if hasattr(self.data_manager, 'store_exercise_file_path'):
                                    self.data_manager.store_exercise_file_path(student, exercise_id, potential_path)
                                return potential_path
        
        # Ensuite vérifier si le chemin est déjà connu dans la cache générique du data_manager
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
        
        # Déterminer l'évaluation actuelle
        current_assessment = None
        if self.results_widget and hasattr(self.results_widget, 'get_current_assessment_name'):
            try:
                current_assessment = self.results_widget.get_current_assessment_name()
                logging.info(f"Évaluation actuelle: {current_assessment}")
            except Exception as e:
                logging.error(f"Erreur lors de la récupération du TD actuel: {str(e)}")
        
        # Rechercher dans les dossiers potentiels
        search_dirs = []
        
        # Ajouter les dossiers potentiels basés sur l'évaluation actuelle
        if current_assessment:
            search_dirs.append(os.path.join(os.getcwd(), "tests", "java_samples", current_assessment, student))
        
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
            
            for pattern in patterns:
                for java_file in java_files:
                    # Vérifier si le nom du fichier contient le pattern
                    if pattern.lower() in os.path.basename(java_file).lower():
                        file_path = java_file
                        logging.info(f"Fichier trouvé avec pattern '{pattern}': {file_path}")
                        # Stocker pour utilisation future
                        if hasattr(self.data_manager, 'exercise_file_paths'):
                            self.data_manager.exercise_file_paths[exercise_id] = file_path
                        if hasattr(self.data_manager, 'store_exercise_file_path'):
                            self.data_manager.store_exercise_file_path(student, exercise_id, file_path)
                        return file_path
        
        # Si toujours pas trouvé, essayer avec juste l'identifiant de l'exercice
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            java_files = glob.glob(os.path.join(search_dir, "*.java"))
            for java_file in java_files:
                if exercise_id.lower() in os.path.basename(java_file).lower():
                    file_path = java_file
                    logging.info(f"Fichier trouvé avec ID d'exercice: {file_path}")
                    # Stocker pour utilisation future
                    if hasattr(self.data_manager, 'exercise_file_paths'):
                        self.data_manager.exercise_file_paths[exercise_id] = file_path
                    if hasattr(self.data_manager, 'store_exercise_file_path'):
                        self.data_manager.store_exercise_file_path(student, exercise_id, file_path)
                    return file_path
        
        # Si toujours pas trouvé, chercher des fichiers qui pourraient correspondre
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            java_files = glob.glob(os.path.join(search_dir, "*.java"))
            if java_files:
                # Si on a qu'un seul fichier, l'utiliser comme dernier recours
                if len(java_files) == 1:
                    file_path = java_files[0]
                    logging.info(f"Utilisation du seul fichier disponible: {file_path}")
                    # Stocker pour utilisation future
                    if hasattr(self.data_manager, 'exercise_file_paths'):
                        self.data_manager.exercise_file_paths[exercise_id] = file_path
                    if hasattr(self.data_manager, 'store_exercise_file_path'):
                        self.data_manager.store_exercise_file_path(student, exercise_id, file_path)
                    return file_path
                
                # Essayer d'extraire un numéro d'exercice du fichier
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
                            if hasattr(self.data_manager, 'exercise_file_paths'):
                                self.data_manager.exercise_file_paths[exercise_id] = file_path
                            if hasattr(self.data_manager, 'store_exercise_file_path'):
                                self.data_manager.store_exercise_file_path(student, exercise_id, file_path)
                            return file_path
        
        logging.warning(f"Aucun fichier trouvé pour l'exercice {exercise_id} de l'étudiant {student}")
        return None
    
    def _find_file_by_pattern(self, student, pattern):
        """Cherche un fichier pour un étudiant basé sur un pattern."""
        # Chercher dans les dossiers TD*
        for td_dir in glob.glob(os.path.join(os.getcwd(), "tests", "java_samples", "TD*")):
            student_dir = os.path.join(td_dir, student)
            if os.path.exists(student_dir):
                # Chercher tous les fichiers .java
                java_files = glob.glob(os.path.join(student_dir, "*.java"))
                for file_path in java_files:
                    file_name = os.path.basename(file_path).lower()
                    # Vérifier si le pattern est présent dans le nom du fichier
                    if pattern.lower() in file_name:
                        return file_path
        
        # Chercher directement dans le dossier de l'étudiant
        student_dir = os.path.join(os.getcwd(), "tests", "java_samples", student)
        if os.path.exists(student_dir):
            java_files = glob.glob(os.path.join(student_dir, "*.java"))
            for file_path in java_files:
                file_name = os.path.basename(file_path).lower()
                if pattern.lower() in file_name:
                    return file_path
        
        return None
    
    def on_feedback_ready(self, feedback):
        """Appelé lorsque le feedback est prêt"""
        self.progress_bar.setValue(100)
        self.feedback_text.setText(feedback)
        self.progress_bar.setVisible(False)
        
        # Réactiver les contrôles
        self.generate_button.setEnabled(True)
        self.sync_button.setEnabled(True)
        self.student_combo.setEnabled(True)
        self.exercises_table.setEnabled(True)
        
        # Activer le bouton de téléchargement
        self.download_button.setEnabled(True)
        
        # Extraire la note globale
        note_texte = extract_note_from_feedback(feedback)
        self.note_label.setText(f"Note: {note_texte}")
        
        # Extraire les notes individuelles pour chaque exercice
        exercise_notes = extract_exercise_notes(feedback, self.get_exercise_ids())
        
        # Mettre à jour le statut de tous les exercices dans le tableau avec les notes individuelles
        self.update_exercises_status_with_notes(exercise_notes)
    
    def get_exercise_ids(self):
        """Récupère les IDs des exercices actuellement affichés dans le tableau"""
        exercise_ids = []
        for row in range(self.exercises_table.rowCount()):
            exercise_id = self.exercises_table.item(row, 0).text()
            exercise_ids.append(exercise_id)
        return exercise_ids
    
    def update_exercises_status_with_notes(self, exercise_notes):
        """Met à jour le statut des exercices dans le tableau avec les notes individuelles"""
        global_status = f"TD noté"  # Statut par défaut
        
        for row in range(self.exercises_table.rowCount()):
            exercise_id = self.exercises_table.item(row, 0).text()
            note = exercise_notes.get(exercise_id)
            
            if note:
                status = f"Noté: {note}"
            else:
                status = global_status
                
            self.exercises_table.setItem(row, 2, QTableWidgetItem(status))
    
    def on_feedback_error(self, error_msg):
        """Appelé en cas d'erreur lors de la génération du feedback"""
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        # Réactiver les contrôles
        self.generate_button.setEnabled(True)
        self.sync_button.setEnabled(True)
        self.student_combo.setEnabled(True)
        self.exercises_table.setEnabled(True)
        
        # Enregistrer l'erreur dans les logs
        logging.error(f"Erreur du thread de feedback: {error_msg}")
        
        # Afficher l'erreur dans la zone de feedback
        self.feedback_text.setText(f"Erreur lors de la génération du feedback: {error_msg}")
        
        # Afficher une boîte de dialogue avec des informations détaillées
        error_details = f"""
Une erreur s'est produite lors de la génération du feedback:

{error_msg}

Solutions possibles:
- Vérifiez votre clé API Gemini
- Assurez-vous que les fichiers d'exercices sont correctement chargés
- Vérifiez votre connexion Internet
- Réessayez après quelques instants
"""
        QMessageBox.critical(self, "Erreur de génération", error_details)
    
    def on_student_changed(self, index):
        """Appelé lorsque l'étudiant sélectionné change"""
        if index >= 0:
            self.current_student = self.student_combo.currentText()
            self.update_exercises_for_student(self.current_student)
            # Activer automatiquement le bouton de génération de feedback
            self.generate_button.setEnabled(True)
            # Effacer le feedback précédent
            self.feedback_text.clear()
            self.download_button.setEnabled(False)
    
    def download_markdown(self):
        """Télécharge le feedback au format Markdown"""
        if not self.feedback_text.toPlainText():
            return
            
        student_name = self.student_combo.currentText()
        if not student_name:
            student_name = "ETUDIANT"
            
        # Suggérer un nom de fichier basé sur le nom de l'étudiant
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le feedback",
            f"{student_name}.md",
            "Markdown (*.md)"
        )
        
        if filename:
            success, message = save_feedback_to_file(
                self.feedback_text.toPlainText(),
                student_name,
                filename
            )
            
            if success:
                QMessageBox.information(self, "Sauvegarde réussie", f"Le feedback a été enregistré dans {filename}")
            else:
                QMessageBox.warning(self, "Erreur de sauvegarde", f"Erreur lors de l'enregistrement: {message}")
                
    def showEvent(self, event):
        """Appelé lorsque le widget devient visible"""
        super().showEvent(event)
        # Synchroniser avec les résultats si c'est la première fois que le widget est affiché
        if self.results_widget and self.student_combo.count() == 0:
            self.sync_with_results() 

    def _normalize_exercise_id(self, exercise_id):
        """Normalise l'ID d'exercice pour faciliter la correspondance avec les configurations."""
        if not exercise_id:
            return ""
            
        # Supprimer les caractères spéciaux sauf les tirets et les soulignés
        normalized = re.sub(r'[^\w\-]', '', exercise_id)
        
        # Remplacer les tirets et soulignés multiples par un seul
        normalized = re.sub(r'[-_]+', '-', normalized)
        
        # Mettre en minuscules
        normalized = normalized.lower()
        
        # Supprimer les préfixes numériques communs comme "01-", "02-", etc.
        normalized = re.sub(r'^[0-9]+-', '', normalized)
        
        # Si l'ID contient des mots clés spécifiques, les normaliser
        keyword_map = {
            'racinecarree': 'racine-carree',
            'racine': 'racine-carree',
            'comptage': 'comptage-mots',
            'mots': 'comptage-mots',
            'comptage-mot': 'comptage-mots',
            'calcul-moyenne': 'moyenne',
            'moyenne': 'calcul-moyenne',
            'intervalle': 'intervalle'
        }
        
        for keyword, replacement in keyword_map.items():
            if keyword in normalized:
                normalized = replacement
                break
                
        logging.debug(f"ID normalisé: {exercise_id} -> {normalized}")
        return normalized 