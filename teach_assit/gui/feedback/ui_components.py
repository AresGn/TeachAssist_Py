"""
Composants d'interface utilisateur pour le module de feedback.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
                            QProgressBar, QFrame, QGroupBox, QFileDialog, QLineEdit, QMessageBox, QScrollArea, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class HeaderSection(QWidget):
    """Section d'en-tête avec l'API Key et la sélection d'étudiant."""
    
    api_key_changed = pyqtSignal(str)
    student_changed = pyqtSignal(int)
    sync_clicked = pyqtSignal()
    test_api_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur de la section."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Section API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("Clé API Gemini:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Entrez votre clé API Gemini ici...")
        self.api_key_input.textChanged.connect(lambda text: self.api_key_changed.emit(text))
        api_key_layout.addWidget(self.api_key_input, stretch=1)
        self.test_api_button = QPushButton("Tester la connexion")
        self.test_api_button.clicked.connect(lambda: self.test_api_clicked.emit())
        api_key_layout.addWidget(self.test_api_button)
        layout.addLayout(api_key_layout)
        
        # Section étudiant
        student_layout = QHBoxLayout()
        student_layout.addWidget(QLabel("Étudiant:"))
        self.student_combo = QComboBox()
        self.student_combo.currentIndexChanged.connect(lambda idx: self.student_changed.emit(idx))
        student_layout.addWidget(self.student_combo)
        student_layout.addStretch()
        
        # Bouton de synchronisation
        self.sync_button = QPushButton("Synchroniser avec Résultats")
        self.sync_button.clicked.connect(lambda: self.sync_clicked.emit())
        student_layout.addWidget(self.sync_button)
        
        # Affichage de la note
        self.note_label = QLabel("Note: --/20")
        student_layout.addWidget(self.note_label)
        layout.addLayout(student_layout)
        
    def set_api_key(self, api_key):
        """Définit la clé API dans le champ d'entrée."""
        self.api_key_input.setText(api_key)
        
    def get_api_key(self):
        """Récupère la clé API du champ d'entrée."""
        return self.api_key_input.text().strip()
    
    def set_student_list(self, students):
        """Remplit la liste déroulante avec les étudiants."""
        previous_student = self.student_combo.currentText()
        self.student_combo.clear()
        
        for student in students:
            self.student_combo.addItem(student)
            
        # Restaurer l'étudiant précédemment sélectionné si possible
        if previous_student in students:
            index = self.student_combo.findText(previous_student)
            if index >= 0:
                self.student_combo.setCurrentIndex(index)
                
    def get_current_student(self):
        """Récupère l'étudiant actuellement sélectionné."""
        return self.student_combo.currentText()
    
    def set_note(self, note):
        """Définit la note affichée."""
        self.note_label.setText(f"Note: {note}")
        
    def enable_controls(self, enabled=True):
        """Active ou désactive les contrôles."""
        self.api_key_input.setEnabled(enabled)
        self.test_api_button.setEnabled(enabled)
        self.student_combo.setEnabled(enabled)
        self.sync_button.setEnabled(enabled)


class ExercisesSection(QWidget):
    """Section des exercices avec tableau."""
    
    exercise_selected = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur de la section."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("Exercices:"))
        
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
        self.exercises_table.cellClicked.connect(lambda row, col: self.exercise_selected.emit(row, col))
        layout.addWidget(self.exercises_table)
        
    def clear_exercises(self):
        """Efface tous les exercices du tableau."""
        self.exercises_table.setRowCount(0)
        
    def add_exercise(self, exercise_id, file_name, status):
        """Ajoute un exercice au tableau."""
        row = self.exercises_table.rowCount()
        self.exercises_table.insertRow(row)
        
        self.exercises_table.setItem(row, 0, QTableWidgetItem(exercise_id))
        self.exercises_table.setItem(row, 1, QTableWidgetItem(file_name))
        self.exercises_table.setItem(row, 2, QTableWidgetItem(status))
        
    def get_selected_exercise(self):
        """Récupère l'ID de l'exercice sélectionné."""
        selected_items = self.exercises_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            return self.exercises_table.item(row, 0).text()
        return None
    
    def get_exercise_count(self):
        """Retourne le nombre d'exercices dans le tableau."""
        return self.exercises_table.rowCount()
    
    def get_exercise_ids(self):
        """Récupère les IDs des exercices dans le tableau."""
        exercise_ids = []
        for row in range(self.exercises_table.rowCount()):
            exercise_id = self.exercises_table.item(row, 0).text()
            exercise_ids.append(exercise_id)
        return exercise_ids
    
    def update_exercise_status(self, row, status):
        """Met à jour le statut d'un exercice."""
        if 0 <= row < self.exercises_table.rowCount():
            self.exercises_table.setItem(row, 2, QTableWidgetItem(status))
            
    def update_exercises_status_with_notes(self, exercise_notes):
        """Met à jour le statut des exercices avec les notes individuelles."""
        for row in range(self.exercises_table.rowCount()):
            exercise_id = self.exercises_table.item(row, 0).text()
            note = exercise_notes.get(exercise_id)
            
            if note:
                status = f"Noté: {note}"
            else:
                status = "TD noté"
                
            self.exercises_table.setItem(row, 2, QTableWidgetItem(status))
            
    def enable_controls(self, enabled=True):
        """Active ou désactive les contrôles."""
        self.exercises_table.setEnabled(enabled)


class FeedbackSection(QWidget):
    """Section de feedback avec zone de texte et boutons."""
    
    generate_clicked = pyqtSignal()
    download_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur de la section."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Résultats de l'analyse (invisible par défaut)
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(0)  # Caché par défaut
        self.results_text.setVisible(False)
        layout.addWidget(self.results_text)
        
        # Texte du feedback
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setMinimumHeight(200)
        layout.addWidget(self.feedback_text)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Layout pour les boutons
        buttons_layout = QHBoxLayout()
        
        # Bouton Générer feedback
        self.generate_button = QPushButton("Générer feedback")
        self.generate_button.clicked.connect(lambda: self.generate_clicked.emit())
        self.generate_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.generate_button)
        
        # Bouton Télécharger en Markdown
        self.download_button = QPushButton("Télécharger en Markdown")
        self.download_button.clicked.connect(lambda: self.download_clicked.emit())
        self.download_button.setMinimumHeight(40)
        self.download_button.setEnabled(False)  # Désactivé jusqu'à ce que le feedback soit généré
        buttons_layout.addWidget(self.download_button)
        
        layout.addLayout(buttons_layout)
        
    def set_feedback_text(self, text):
        """Définit le texte de feedback."""
        self.feedback_text.setText(text)
        
    def get_feedback_text(self):
        """Récupère le texte de feedback."""
        return self.feedback_text.toPlainText()
        
    def set_progress(self, value):
        """Met à jour la valeur de la barre de progression."""
        self.progress_bar.setValue(value)
        
    def show_progress_bar(self, visible=True):
        """Affiche ou masque la barre de progression."""
        self.progress_bar.setVisible(visible)
        
    def enable_download_button(self, enabled=True):
        """Active ou désactive le bouton de téléchargement."""
        self.download_button.setEnabled(enabled)
        
    def enable_generate_button(self, enabled=True):
        """Active ou désactive le bouton de génération."""
        self.generate_button.setEnabled(enabled) 