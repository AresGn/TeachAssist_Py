import sys
import os
import json
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
                            QProgressBar, QFrame, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap

from google import genai

from teach_assit.gui.styles import MAIN_STYLE
from teach_assit.gui.results_widget.main_widget import ResultsWidget  # Pour accéder aux données d'analyse

class FeedbackThread(QThread):
    """Thread pour générer du feedback avec l'API Gemini sans bloquer l'interface."""
    feedback_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key, student_code, analysis_results, execution_results, exercise_config=None):
        super().__init__()
        self.api_key = api_key
        self.student_code = student_code
        self.analysis_results = analysis_results
        self.execution_results = execution_results
        self.exercise_config = exercise_config
        
    def run(self):
        try:
            # Configurer l'API Gemini en utilisant le nouvel API Client
            client = genai.Client(api_key=self.api_key)
            
            # Préparer les informations sur le barème si disponibles
            bareme_info = ""
            if self.exercise_config:
                bareme_info = f"""
                CRITÈRES D'ÉVALUATION:
                - Méthodes requises : {', '.join([m.get('name', '') for m in self.exercise_config.get('rules', {}).get('requiredMethods', [])])}
                - Structures de contrôle requises : {', '.join(self.exercise_config.get('rules', {}).get('requiredControlStructures', []))}
                - Opérateurs autorisés : {', '.join(self.exercise_config.get('rules', {}).get('allowedOperators', []))}
                """
            
            # Préparer le prompt
            prompt = f"""
            Tu es un assistant pédagogique spécialisé dans l'évaluation de code Java pour des étudiants.
            Analyse le code suivant et les résultats d'analyse statique et d'exécution pour fournir un retour détaillé et constructif.
            
            DESCRIPTION DE L'EXERCICE:
            {self.exercise_config.get('description', 'Exercice de programmation Java')}
            
            CODE SOURCE:
            ```java
            {self.student_code}
            ```
            
            RÉSULTATS D'ANALYSE STATIQUE:
            {self.analysis_results}
            
            RÉSULTATS D'EXÉCUTION:
            {self.execution_results}
            
            {bareme_info}
            
            Ton feedback doit inclure:
            1. Une évaluation globale de la qualité du code (2-3 phrases)
            2. Les points forts du code (liste concise)
            3. Les points à améliorer, avec des recommandations concrètes (liste concise)
            4. Une note suggérée sur 20 basée sur ton évaluation, en tenant compte des critères ci-dessus
            
            Utilise un ton encourageant et pédagogique. Si la note est basse, souligne les aspects positifs et donne des conseils constructifs pour s'améliorer.
            """
            
            # Générer le feedback en utilisant la nouvelle syntaxe
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            feedback = response.text
            
            # Émettre le signal avec le feedback
            self.feedback_ready.emit(feedback)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


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
        self.exercise_configs = {}
        
        # Configuration du layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Entête
        header_layout = QVBoxLayout()
        
        # Section API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("Clé API Gemini:"))
        self.api_key_input = QTextEdit()
        self.api_key_input.setMinimumHeight(60)
        self.api_key_input.setMaximumHeight(60)
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
        
        # Section exercices
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
        
        # Zone de feedback
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
        
        # Bouton Générer feedback
        self.generate_button = QPushButton("Générer feedback")
        self.generate_button.clicked.connect(self.generate_feedback)
        self.generate_button.setMinimumHeight(40)
        feedback_layout.addWidget(self.generate_button)
        
        # Assemblage du layout principal
        self.main_layout.addLayout(header_layout)
        self.main_layout.addLayout(exercises_layout)
        self.main_layout.addLayout(feedback_layout)
        self.main_layout.addStretch(1)
        
        # Charger les configurations d'exercices
        self.load_exercise_configs()
        
    def set_results_widget(self, results_widget):
        """Définit la référence au widget de résultats pour récupérer les données"""
        self.results_widget = results_widget
        
    def load_exercise_configs(self):
        """Charge les configurations des exercices depuis les fichiers JSON"""
        configs_dir = os.path.join(os.getcwd(), 'configs')
        if not os.path.exists(configs_dir):
            return
            
        for filename in os.listdir(configs_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(configs_dir, filename), 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        exercise_id = config.get('id')
                        if exercise_id:
                            self.exercise_configs[exercise_id] = config
                except Exception as e:
                    print(f"Erreur lors du chargement de la configuration {filename}: {str(e)}")
        
    def sync_with_results(self):
        """Récupère les données d'analyse depuis l'onglet Results"""
        if not self.results_widget:
            self.feedback_text.setText("⚠️ Impossible de se synchroniser - Onglet Results non accessible")
            return
            
        # Récupérer la liste des étudiants
        self.student_combo.clear()
        students = self.get_students_from_results()
        if students:
            for student in students:
                self.student_combo.addItem(student)
            
            # Sélectionner le premier étudiant par défaut
            self.update_exercises_for_student(students[0])
        else:
            self.feedback_text.setText("⚠️ Aucun étudiant trouvé dans l'onglet Results")
            
    def get_students_from_results(self):
        """Récupère la liste des étudiants depuis l'onglet Results"""
        if self.results_widget:
            try:
                # Get the actual student list from the results widget
                return self.results_widget.get_student_list()
            except AttributeError:
                # If the method doesn't exist, use the sample data we have
                return ["ARES", "CARLOS", "KARL", "SARAH"]
        return []
            
    def update_exercises_for_student(self, student):
        """Met à jour le tableau des exercices pour l'étudiant sélectionné"""
        self.exercises_table.setRowCount(0)
        
        # Fix: Use the actual data from results_widget instead of static data
        exercises = self.get_exercises_for_student(student)
        
        for row, exercise in enumerate(exercises):
            self.exercises_table.insertRow(row)
            self.exercises_table.setItem(row, 0, QTableWidgetItem(exercise['id']))
            self.exercises_table.setItem(row, 1, QTableWidgetItem(f"{student}\\{exercise['file']}"))
            self.exercises_table.setItem(row, 2, QTableWidgetItem(exercise['status']))
            
    def get_exercises_for_student(self, student):
        """Récupère les exercices pour un étudiant donné depuis l'onglet Results"""
        if self.results_widget:
            try:
                # Get the actual exercises from the results widget
                return self.results_widget.get_exercises_for_student(student)
            except AttributeError:
                # If the method doesn't exist, use hardcoded data based on the batch file output
                return [
                    {'id': 'sequence-numerique', 'file': 'sequence-numerique.java', 'status': 'En attente'},
                    {'id': 'triangle-isocele', 'file': 'triangle-isocele.java', 'status': 'En attente'}
                ]
        return []
        
    def on_exercise_selected(self, row, column):
        """Appelé lorsqu'un exercice est sélectionné dans le tableau"""
        self.selected_exercise = self.exercises_table.item(row, 0).text()
        student = self.student_combo.currentText()
        
        # Récupérer les données d'analyse et d'exécution réelles
        code, analysis_results, execution_results = self.get_analysis_data(student, self.selected_exercise)
        
        # Stocker les données pour une utilisation ultérieure
        self.current_code = code
        self.current_analysis = analysis_results
        self.current_execution = execution_results
        
        # Message de sélection
        self.feedback_text.setText(f"Exercice sélectionné: {self.selected_exercise}\nÉtudiant: {student}\n\nCliquez sur 'Générer feedback' pour obtenir une analyse par IA.")
        
    def get_analysis_data(self, student, exercise_id):
        """Récupère les données d'analyse et d'exécution pour un étudiant et un exercice donnés"""
        if self.results_widget:
            try:
                # Get the actual analysis data from the results widget
                return self.results_widget.get_analysis_data(student, exercise_id)
            except AttributeError:
                # If the method doesn't exist, use the hardcoded data
                pass
        
        # Fallback to hardcoded data
        if exercise_id == "triangle-isocele":
            code = "public class Triangle {\n    public static boolean estTriangleIsocele(int a, int b, int c) {\n        return a == b || b == c || a == c;\n    }\n}"
            analysis = "✅ Méthode estTriangleIsocele trouvée\n❌ Test unitaire: Le triangle (3,3,5) devrait être identifié comme isocèle\n✅ Tous les paramètres sont correctement déclarés\n❌ La logique de vérification n'est pas complète"
            execution = "Test #1: Triangle (3,3,5) => Attendu: true, Obtenu: false"
        elif exercise_id == "sequence-numerique":
            code = "public class Sequence {\n    public static int sommeSequence(int n) {\n        int somme = 0;\n        for (int i = 1; i <= n; i++) {\n            somme += i;\n        }\n        return somme;\n    }\n}"
            analysis = "✅ Méthode sommeSequence trouvée\n✅ Tests unitaires réussis\n✅ Tous les paramètres sont correctement déclarés\n✅ Logique correcte"
            execution = "Test #1: sommeSequence(5) => Attendu: 15, Obtenu: 15\nTest #2: sommeSequence(10) => Attendu: 55, Obtenu: 55"
        else:
            code = "// Pas de code disponible pour cet exercice"
            analysis = "Pas de résultats d'analyse disponibles"
            execution = "Pas de résultats d'exécution disponibles"
            
        return code, analysis, execution
        
    def test_api_connection(self):
        """Teste la connexion à l'API Gemini"""
        api_key = self.api_key_input.toPlainText().strip()
        if not api_key:
            self.feedback_text.setText("❌ Veuillez entrer une clé API")
            return
            
        self.api_key = api_key
        
        try:
            # Configurer l'API avec le nouvel API Client
            client = genai.Client(api_key=self.api_key)
            
            # Vérifier si l'API fonctionne avec une requête simple
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents="Réponds simplement par 'OK' pour tester la connexion."
            )
            
            if response.text:
                self.feedback_text.setText("✅ Connexion à l'API Gemini réussie!")
            else:
                self.feedback_text.setText("❌ Échec de connexion: pas de réponse")
                
        except Exception as e:
            self.feedback_text.setText(f"❌ Échec de connexion: {str(e)}")
        
    def generate_feedback(self):
        """Génère un feedback avec l'API Gemini"""
        if not self.api_key:
            self.feedback_text.setText("Veuillez d'abord configurer et tester votre clé API")
            return
            
        if not self.selected_exercise:
            self.feedback_text.setText("Veuillez d'abord sélectionner un exercice")
            return
        
        if not hasattr(self, 'current_code') or not hasattr(self, 'current_analysis'):
            self.feedback_text.setText("Données insuffisantes pour générer un feedback")
            return
            
        # Afficher la barre de progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.feedback_text.setText("Génération du feedback en cours...")
        
        # Récupérer la configuration de l'exercice si disponible
        exercise_config = self.exercise_configs.get(self.selected_exercise, {})
        
        # Créer et démarrer le thread de feedback
        self.feedback_thread = FeedbackThread(
            self.api_key, 
            self.current_code, 
            self.current_analysis, 
            getattr(self, 'current_execution', "Pas de résultats d'exécution disponibles"),
            exercise_config
        )
        self.feedback_thread.feedback_ready.connect(self.on_feedback_ready)
        self.feedback_thread.error_occurred.connect(self.on_feedback_error)
        self.feedback_thread.start()
        
    def on_feedback_ready(self, feedback):
        """Appelé lorsque le feedback est prêt"""
        self.progress_bar.setValue(100)
        self.feedback_text.setText(feedback)
        self.progress_bar.setVisible(False)
        
        # Extraire la note (exemple simple: chercher un chiffre suivi de "/20")
        note_match = re.search(r'(\d+(\.\d+)?)/20', feedback)
        if note_match:
            note = note_match.group(0)
            self.note_label.setText(f"Note: {note}")
            
            # Mettre à jour le statut dans le tableau des exercices
            self.update_exercise_status(self.selected_exercise, note)
        
    def update_exercise_status(self, exercise_id, note):
        """Met à jour le statut de l'exercice dans le tableau"""
        for row in range(self.exercises_table.rowCount()):
            if self.exercises_table.item(row, 0).text() == exercise_id:
                self.exercises_table.setItem(row, 2, QTableWidgetItem(f"Noté: {note}"))
                break
        
    def on_feedback_error(self, error_msg):
        """Appelé en cas d'erreur lors de la génération du feedback"""
        self.progress_bar.setValue(0)
        self.feedback_text.setText(f"Erreur lors de la génération du feedback: {error_msg}")
        self.progress_bar.setVisible(False) 