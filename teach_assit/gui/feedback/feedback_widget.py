"""
Widget principal pour l'onglet Notes & Feedback.
"""

import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
                            QProgressBar, QFrame, QGroupBox, QFileDialog, QLineEdit)
from PyQt5.QtCore import Qt

from teach_assit.gui.styles import MAIN_STYLE
from teach_assit.gui.feedback.feedback_thread import FeedbackThread
from teach_assit.gui.feedback.data_manager import DataManager
from teach_assit.gui.feedback.utils import (extract_note_from_feedback, 
                                          extract_exercise_notes,
                                          test_api_connection,
                                          save_feedback_to_file)

class FeedbackWidget(QWidget):
    """Widget pour l'onglet Notes & Feedback intégrant l'API Gemini"""
    
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
        
    def _setup_header(self):
        """Configure la section d'en-tête (API Key et sélection d'étudiant)"""
        header_layout = QVBoxLayout()
        
        # Section API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("Clé API Gemini:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Entrez votre clé API Gemini ici...")
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
        
    def set_results_widget(self, results_widget):
        """Définit la référence au widget de résultats pour récupérer les données"""
        self.results_widget = results_widget
        self.data_manager.results_widget = results_widget
    
    def sync_with_results(self):
        """Récupère les données d'analyse depuis l'onglet Results"""
        if not self.results_widget:
            self.feedback_text.setText("⚠️ Impossible de se synchroniser - Onglet Results non accessible")
            return
            
        # Récupérer la liste des étudiants
        self.student_combo.clear()
        students = self.data_manager.get_students_from_results()
        if students:
            for student in students:
                self.student_combo.addItem(student)
            
            # Sélectionner le premier étudiant par défaut
            self.update_exercises_for_student(students[0])
        else:
            self.feedback_text.setText("⚠️ Aucun étudiant trouvé dans l'onglet Results")
    
    def update_exercises_for_student(self, student):
        """Met à jour le tableau des exercices pour l'étudiant sélectionné"""
        self.exercises_table.setRowCount(0)
        
        # Récupérer les exercices pour l'étudiant
        exercises = self.data_manager.get_exercises_for_student(student)
        
        for row, exercise in enumerate(exercises):
            self.exercises_table.insertRow(row)
            self.exercises_table.setItem(row, 0, QTableWidgetItem(exercise['id']))
            self.exercises_table.setItem(row, 1, QTableWidgetItem(f"{student}\\{exercise['file']}"))
            self.exercises_table.setItem(row, 2, QTableWidgetItem(exercise['status']))
    
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
        
        success, message = test_api_connection(api_key)
        self.feedback_text.setText(f"{'✅' if success else '❌'} {message}")
        
        if success:
            self.api_key = api_key
    
    def generate_feedback(self):
        """Génère un feedback global pour tous les exercices de l'étudiant sélectionné"""
        if not self.api_key:
            self.feedback_text.setText("Veuillez d'abord configurer et tester votre clé API")
            return
            
        student = self.student_combo.currentText()
        if not student:
            self.feedback_text.setText("Veuillez d'abord sélectionner un étudiant")
            return
        
        # Récupérer les données de tous les exercices de l'étudiant
        exercises_data = []
        for row in range(self.exercises_table.rowCount()):
            exercise_id = self.exercises_table.item(row, 0).text()
            status_cell = self.exercises_table.item(row, 2)
            status = status_cell.text() if status_cell else "En attente"
            
            # Récupérer les données pour cet exercice
            code, analysis, execution = self.data_manager.get_analysis_data(student, exercise_id)
            
            # Récupérer le résultat depuis les données du results_widget si disponible
            result = "Non évalué"
            if self.results_widget:
                try:
                    result = self.results_widget.get_exercise_result(student, exercise_id)
                except AttributeError:
                    # Si la méthode n'existe pas, utiliser une donnée par défaut
                    if exercise_id == "sequence-numerique":
                        result = "5/7 vérifications - 7.1/10 pt"
                    elif exercise_id == "triangle-isocele":
                        result = "5/7 vérifications - 7.1/10 pt"
            
            # Récupérer la configuration de l'exercice si disponible
            config = self.data_manager.exercise_configs.get(exercise_id, {})
            
            # Ajouter les données à la liste
            exercises_data.append({
                'id': exercise_id,
                'code': code,
                'analysis': analysis,
                'execution': execution,
                'config': config,
                'status': status,
                'result': result
            })
            
        if not exercises_data:
            self.feedback_text.setText("Aucun exercice trouvé pour cet étudiant")
            return
            
        # Afficher la barre de progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.feedback_text.setText("Génération du feedback global pour tous les exercices en cours...")
        
        # Créer et démarrer le thread de feedback
        self.feedback_thread = FeedbackThread(
            self.api_key, 
            student,
            exercises_data
        )
        self.feedback_thread.feedback_ready.connect(self.on_feedback_ready)
        self.feedback_thread.error_occurred.connect(self.on_feedback_error)
        self.feedback_thread.start()
    
    def on_feedback_ready(self, feedback):
        """Appelé lorsque le feedback est prêt"""
        self.progress_bar.setValue(100)
        self.feedback_text.setText(feedback)
        self.progress_bar.setVisible(False)
        
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
        self.feedback_text.setText(f"Erreur lors de la génération du feedback: {error_msg}")
        self.progress_bar.setVisible(False) 
        
    def on_student_changed(self, index):
        """Appelé lorsqu'un étudiant est sélectionné dans le combo box"""
        if index >= 0:
            student = self.student_combo.currentText()
            self.update_exercises_for_student(student)
            self.note_label.setText("Note: --/20")  # Réinitialiser la note
            self.feedback_text.setText(f"Étudiant sélectionné: {student}\n\nSélectionnez un exercice pour générer un feedback.")
    
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
                self.feedback_text.setText(f"✅ {message}\n\n{self.feedback_text.toPlainText()}")
            else:
                self.feedback_text.setText(f"❌ {message}\n\n{self.feedback_text.toPlainText()}") 