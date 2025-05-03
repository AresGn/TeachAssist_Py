"""
Widget principal pour l'affichage et l'analyse des résultats des étudiants.
"""

import os
import logging
import json
import glob
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem, QComboBox, 
                           QPushButton, QLineEdit, QFrame, QHeaderView,
                           QSizePolicy, QMessageBox, QScrollArea, QGroupBox, QDialog, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QFont

from teach_assit.core.analysis.config_loader import ConfigLoader
from teach_assit.core.analysis.models import ExerciseConfig
from teach_assit.gui.results_widget.utils import SYMBOL_OK, SYMBOL_FAIL, SYMBOL_WARNING
from teach_assit.gui.results_widget.dialogs import DetailsDialog, OutputDialog
from teach_assit.gui.results_widget.report import format_detailed_report
from teach_assit.gui.results_widget.execution import CodeExecutor
from teach_assit.gui.results_widget.ui_components import (
    StatusWidget, ExerciseWidget, ResultWidget, ActionsWidget, ExecutionResultWidget
)

class ResultsWidget(QWidget):
    """Widget pour afficher et analyser les résultats des évaluations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Définir la politique de taille pour que le widget prenne toute la place disponible
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Forcer le widget à prendre tout l'espace disponible
        self.setMinimumSize(800, 600)  # Taille minimale raisonnable
        self.init_ui()
        
        # Initialiser l'exécuteur de code
        self.code_executor = CodeExecutor()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur de l'onglet résultats."""
        # Créer le layout principal sans marges
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Créer un widget de défilement pour le contenu principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # Supprime la bordure
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Conteneur pour tout le contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Conteneur pour l'en-tête avec un fond blanc
        header_container = QWidget()
        header_container.setStyleSheet("background-color: white;")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 10)

        # En-tête des résultats
        header = QLabel("Résultats des évaluations")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(header)

        # Filtre et actions
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.NoFrame)
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                padding: 10px;
            }
        """)
        
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 10, 0, 10)
        
        # Recherche avec style amélioré
        search_input = QLineEdit()
        search_input.setPlaceholderText("Rechercher...")
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                min-width: 300px;
            }
        """)
        filter_layout.addWidget(search_input)
        
        # Filtre par exercice
        self.exercise_filter = QComboBox()
        self.exercise_filter.addItem("Tous les exercices")
        self.exercise_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                min-width: 200px;
            }
        """)
        filter_layout.addWidget(self.exercise_filter)
        
        # Filtre par date
        date_filter = QComboBox()
        date_filter.addItem("Toutes les dates")
        date_filter.addItem("Aujourd'hui")
        date_filter.addItem("Cette semaine")
        date_filter.addItem("Ce mois")
        date_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(date_filter)
        
        # Spacer pour pousser le bouton exporter à droite
        filter_layout.addStretch()
        
        # Bouton exporter
        export_button = QPushButton("Exporter")
        export_button.setIcon(QIcon("icons/download.svg"))
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                border-radius: 4px;
                padding: 8px 15px;
                color: white;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        filter_layout.addWidget(export_button)
        
        header_layout.addWidget(filter_frame)
        content_layout.addWidget(header_container)

        # Conteneur principal pour le tableau et les stats
        main_container = QWidget()
        main_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout_inner = QVBoxLayout(main_container)
        main_layout_inner.setContentsMargins(20, 0, 20, 20)
        main_layout_inner.setSpacing(20)

        # Tableau des résultats
        self._init_results_table(main_layout_inner)
        
        # Section pour l'exécution des codes
        self._init_execution_section(main_layout_inner)
        
        content_layout.addWidget(main_container)
        
        # Définir le widget de contenu comme widget de la zone de défilement
        scroll_area.setWidget(content_widget)
        
        # Ajouter la zone de défilement au layout principal
        main_layout.addWidget(scroll_area)
    
    def _init_results_table(self, parent_layout):
        """Initialiser le tableau des résultats."""
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Étudiant", "Exercice", "Statut", "Résultat", "Actions"
        ])
        
        # Style du tableau
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dfe6e9;
                border-radius: 8px;
                gridline-color: #f1f2f6;
            }
            QHeaderView::section {
                background-color: #e9f2fd;
                color: #2c3e50;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #3498db;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }
        """)

        # Configuration du tableau pour qu'il prenne tout l'espace
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        
        # Ajuster les en-têtes du tableau
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Étudiant
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Exercice
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Statut
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Résultat
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Actions - prend l'espace restant
        
        # Définir les largeurs des colonnes
        self.results_table.setColumnWidth(1, 300)  # Largeur fixe pour exercice
        self.results_table.setColumnWidth(2, 250)  # Largeur fixe pour statut
        self.results_table.setColumnWidth(3, 250)  # Largeur fixe pour résultat
        
        # Configuration supplémentaire du tableau
        self.results_table.setShowGrid(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.horizontalHeader().setFixedHeight(50)
        
        # Garantir une hauteur minimale pour le tableau
        self.results_table.setMinimumHeight(300)
        
        parent_layout.addWidget(self.results_table)
    
    def _init_execution_section(self, parent_layout):
        """Initialiser la section d'exécution avec les entrées de test."""
        # Section pour les tests d'exécution
        execution_section = QGroupBox("Exécution des codes étudiants")
        execution_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        execution_layout = QVBoxLayout(execution_section)
        
        # Message explicatif
        info_label = QLabel("Cette section permet d'exécuter les codes des étudiants avec les entrées de test définies dans les configurations d'exercices.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-style: italic; color: #555;")
        execution_layout.addWidget(info_label)
        
        # Bouton d'exécution
        execute_button = QPushButton("Exécuter les codes")
        execute_button.setIcon(QIcon("icons/play.svg"))
        execute_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        # Créer un layout horizontal pour centrer le bouton
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(execute_button)
        button_layout.addStretch()
        
        execution_layout.addLayout(button_layout)
        
        # Connecter le bouton à la fonction d'exécution
        execute_button.clicked.connect(self.execute_all_codes)
        
        # Stocker une référence au bouton d'exécution
        self.execute_button = execute_button
        
        # Tableau des résultats d'exécution
        self._init_execution_results_table(execution_layout)
        
        # Ajouter la section d'exécution au layout parent
        parent_layout.addWidget(execution_section)
    
    def _init_execution_results_table(self, parent_layout):
        """Initialiser le tableau des résultats d'exécution."""
        self.execution_results_table = QTableWidget()
        self.execution_results_table.setColumnCount(5)
        self.execution_results_table.setHorizontalHeaderLabels([
            "Étudiant", 
            "Exercice", 
            "Test", 
            "Résultat", 
            "Actions"
        ])
        
        # Style du tableau
        self.execution_results_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                gridline-color: #e9ecef;
                selection-background-color: #e8f4fd;
                selection-color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #e9ecef;
                border-right: 1px solid #e9ecef;
                font-weight: bold;
                text-align: center;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #e8f4fd;
                color: #2c3e50;
            }
        """)
        
        # Configuration pour une meilleure expérience utilisateur
        self.execution_results_table.setMinimumHeight(350)  # Augmentation significative de la hauteur
        self.execution_results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.execution_results_table.horizontalHeader().setStretchLastSection(True)
        self.execution_results_table.setShowGrid(False)
        self.execution_results_table.setAlternatingRowColors(True)
        self.execution_results_table.verticalHeader().setVisible(False)
        
        # Définir la largeur des colonnes
        self.execution_results_table.setColumnWidth(0, 150)  # Étudiant
        self.execution_results_table.setColumnWidth(1, 200)  # Exercice
        self.execution_results_table.setColumnWidth(2, 150)  # Test
        self.execution_results_table.setColumnWidth(3, 250)  # Résultat
        
        # Ajouter le tableau au layout
        parent_layout.addWidget(self.execution_results_table)
    
    def clear(self):
        """Effacer tous les résultats."""
        self.results_table.setRowCount(0)
    
    def update_analysis_results(self, analysis_results, assessment_name, exercise_configs):
        """Afficher les résultats d'analyse dans le tableau.
        
        Args:
            analysis_results: Dictionnaire {étudiant: {fichier: résultat}}
            assessment_name: Nom de l'évaluation
            exercise_configs: Dictionnaire des configurations d'exercices
        """
        # Effacer les anciennes données
        self.clear()
        
        # Mettre à jour le filtre des exercices
        self.exercise_filter.clear()
        self.exercise_filter.addItem("Tous les exercices")
        for ex_id, config in exercise_configs.items():
            self.exercise_filter.addItem(f"{ex_id} - {config.name}")
        
        # Calculer le nombre total de lignes (somme des exercices pour chaque étudiant)
        total_rows = sum(len(student_results) for student_results in analysis_results.values())
        self.results_table.setRowCount(total_rows)
        
        # Styles de cellules alternés
        even_row_style = "background-color: white;"
        odd_row_style = "background-color: #f9f9f9;"
        
        current_row = 0
        
        # Remplir le tableau avec rowspan pour les étudiants
        for student, student_results in analysis_results.items():
            num_exercises = len(student_results)
            
            # Si l'étudiant a des exercices, on crée un rowspan pour son nom
            if num_exercises > 0:
                # Cellule pour le nom de l'étudiant avec rowspan
                student_item = QTableWidgetItem(student)
                student_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                font = student_item.font()
                font.setBold(True)
                student_item.setFont(font)
                
                # Définir le style selon la parité de la ligne
                student_item.setBackground(QColor("#f8f9fa"))
                
                self.results_table.setItem(current_row, 0, student_item)
                
                # Si plusieurs exercices, utiliser rowspan
                if num_exercises > 1:
                    self.results_table.setSpan(current_row, 0, num_exercises, 1)
                
                # Pour chaque exercice de l'étudiant
                for i, (file_path, result) in enumerate(student_results.items()):
                    row_index = current_row + i
                    
                    # Appliquer le style alterné
                    row_style = even_row_style if i % 2 == 0 else odd_row_style
                    
                    # Nom du fichier et exercice associé
                    file_name = os.path.basename(file_path)
                    
                    # Utiliser l'ID d'exercice stocké dans le résultat de l'analyse
                    # ou le déterminer à partir du chemin du fichier si non disponible
                    exercise_id = result.get('exerciseId', None)
                    
                    # Si l'ID d'exercice n'est pas spécifié dans le résultat, essayer de le déterminer
                    if not exercise_id:
                        # Utiliser uniquement les exercices spécifiés dans exercise_configs
                        for ex_id in exercise_configs.keys():
                            if ex_id.lower() in file_path.lower() or ex_id.split('-')[-1].lower() in file_path.lower():
                                exercise_id = ex_id
                                break
                        
                        # Si toujours pas d'exercice associé, marquer comme "Non spécifié"
                        if not exercise_id:
                            exercise_id = "Non spécifié"
                    
                    # Vérifier si la configuration d'exercice existe
                    exercise_config = exercise_configs.get(exercise_id)
                    if not exercise_config:
                        # Si exercice non trouvé dans les configurations, ce n'est pas pertinent pour cette évaluation
                        continue
                    
                    exercise_name = exercise_config.name
                    
                    # Widget pour l'exercice
                    exercise_widget = ExerciseWidget(
                        exercise_name=exercise_name,
                        file_name=file_name,
                        row_style=row_style
                    )
                    
                    self.results_table.setCellWidget(row_index, 1, exercise_widget)
                    
                    # Vérification des critères
                    syntax_ok = not result.get('syntax_errors', []) and 'error' not in result
                    methods_ok = not result.get('missing_methods', [])
                    patterns_ok = not (result.get('analysis_details', {}).get('missing_patterns', []))
                    
                    # Opérateurs
                    operators_ok = True
                    if 'analysis_details' in result and 'disallowed_operators' in result['analysis_details']:
                        operators_ok = not result['analysis_details']['disallowed_operators']
                    
                    # Structures de contrôle
                    control_structures_ok = True
                    if 'analysis_details' in result and 'control_structures' in result['analysis_details']:
                        control_structures_ok = not result['analysis_details']['control_structures'].get('missing', [])
                    
                    # Conventions de nommage
                    naming_ok = True
                    if 'analysis_details' in result and 'naming_conventions' in result['analysis_details']:
                        naming_ok = not result['analysis_details']['naming_conventions'].get('errors', [])
                    
                    # Portée des variables
                    scope_ok = True
                    if 'analysis_details' in result and 'variable_scopes' in result['analysis_details']:
                        scope_ok = not result['analysis_details']['variable_scopes'].get('errors', [])
                    
                    # Définir les statuts
                    statuses = [
                        {"name": "Syntaxe", "ok": syntax_ok, "warning": False},
                        {"name": "Méthodes", "ok": methods_ok, "warning": True if not methods_ok else False},
                        {"name": "Structures", "ok": control_structures_ok, "warning": False},
                        {"name": "Nommage", "ok": naming_ok, "warning": False},
                        {"name": "Opérateurs", "ok": operators_ok, "warning": False},
                        {"name": "Patterns", "ok": patterns_ok, "warning": True if not patterns_ok else False}
                    ]
                    
                    # Widget pour le statut
                    status_widget = StatusWidget(
                        row_style=row_style,
                        statuses=statuses
                    )
                    
                    self.results_table.setCellWidget(row_index, 2, status_widget)
                    
                    # Résultat global
                    all_ok = syntax_ok and methods_ok and patterns_ok and operators_ok and control_structures_ok and naming_ok and scope_ok
                    
                    # Calculer le score
                    total_checks = 7  # syntaxe, méthodes, patterns, opérateurs, structures, nommage, portée
                    passed_checks = sum([syntax_ok, methods_ok, patterns_ok, operators_ok, control_structures_ok, naming_ok, scope_ok])
                    
                    # Note estimée
                    max_points = exercise_config.max_points if exercise_config and hasattr(exercise_config, 'max_points') else 10
                    estimated_score = round((passed_checks / total_checks) * max_points, 1)
                    
                    # Widget pour le résultat
                    result_widget = ResultWidget(
                        exercise_name=exercise_name,
                        passed_checks=passed_checks,
                        total_checks=total_checks,
                        max_points=max_points,
                        estimated_score=estimated_score,
                        row_style=row_style,
                        all_ok=all_ok
                    )
                    
                    self.results_table.setCellWidget(row_index, 3, result_widget)
                    
                    # Stocker les détails pour affichage ultérieur
                    details_data = format_detailed_report(result, exercise_config)
                    
                    # Widget pour les actions (bouton détails)
                    actions_widget = ActionsWidget(
                        exercise_name=exercise_name,
                        row_style=row_style,
                        on_details_click=lambda checked=False, data=details_data, title=f"{student} - {file_name}": 
                                                 self.show_details_dialog(title, data)
                    )
                    
                    self.results_table.setCellWidget(row_index, 4, actions_widget)
                
                current_row += num_exercises
        
        # Réajuster le tableau après avoir potentiellement filtré des lignes
        if self.results_table.rowCount() > current_row:
            self.results_table.setRowCount(current_row)
        
        # Afficher un message si aucun résultat
        if current_row == 0:
            self.results_table.setRowCount(1)
            info_item = QTableWidgetItem(f"Aucun résultat pour l'évaluation {assessment_name}")
            font = info_item.font()
            font.setItalic(True)
            info_item.setFont(font)
            info_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setSpan(0, 0, 1, 5)
            self.results_table.setItem(0, 0, info_item)
        
        # Ajuster les hauteurs de ligne pour le contenu
        for i in range(self.results_table.rowCount()):
            self.results_table.setRowHeight(i, 90)  # Augmenter légèrement la hauteur pour mieux afficher le contenu
    
    def show_details_dialog(self, title, details):
        """Afficher les détails dans un dialogue modal."""
        # Créer un dictionnaire de détails avec le titre comme nom d'exercice
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Détails d'analyse - {title}")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Afficher les détails
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setHtml(details)
        layout.addWidget(details_text)
        
        # Bouton fermer
        button_layout = QHBoxLayout()
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def show_output_dialog(self, title, output_text):
        """Afficher la sortie complète d'une exécution dans une fenêtre modale."""
        dialog = OutputDialog(self, title, output_text)
        dialog.exec_()
    
    def execute_all_codes(self):
        """Exécuter tous les codes des étudiants avec les entrées de test configurées."""
        # Désactiver le bouton d'exécution pendant le traitement
        self.execute_button.setEnabled(False)
        self.execute_button.setText("Exécution en cours...")
        
        # Initialiser le chargeur de configurations avec le répertoire courant
        config_loader = ConfigLoader(os.getcwd())
        
        # S'assurer que toutes les configurations sont chargées depuis la base de données
        config_loader.load_all_configs()
        
        # Récupérer toutes les configurations d'exercices depuis la base de données
        exercise_configs = config_loader.get_all_exercise_configs()
        
        # Structure de données pour stocker les résultats
        all_results = []
        
        # Obtenir la liste de tous les étudiants du tableau de résultats
        students = set()
        for row in range(self.results_table.rowCount()):
            student_item = self.results_table.item(row, 0)
            if student_item:
                students.add(student_item.text())
        
        # Liste pour stocker les IDs d'exercices
        exercise_ids = set()
        
        # Récupérer l'assessment courant depuis le tableau
        current_assessment = None
        for row in range(self.results_table.rowCount()):
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                if item and "TD" in item.text():
                    # Chercher un pattern "TD1", "TD2", etc.
                    import re
                    match = re.search(r'TD\d+', item.text())
                    if match:
                        current_assessment = match.group(0)
                        break
        
        # Si nous n'avons pas déterminé l'assessment, utiliser la méthode d'origine
        if not current_assessment:
            # MÉTHODE 1: Récupérer les exercices depuis les widgets du tableau
            for row in range(self.results_table.rowCount()):
                exercise_widget = self.results_table.cellWidget(row, 1)
                if exercise_widget and isinstance(exercise_widget, ExerciseWidget):
                    exercise_name = exercise_widget.get_exercise_name()
                    
                    # Chercher l'ID correspondant au nom de l'exercice
                    for ex_id, config in exercise_configs.items():
                        if config.name == exercise_name:
                            exercise_ids.add(ex_id)
                            break
        else:
            # Si nous avons un assessment, récupérer sa configuration
            print(f"Assessment identifié : {current_assessment}")
            assessment_config = config_loader.get_assessment_config(current_assessment)
            
            if assessment_config:
                # Utiliser tous les exercices de cette évaluation
                for ex in assessment_config.exercises:
                    ex_id = ex.get('exerciseId', '')
                    if ex_id:
                        print(f"Ajout de l'exercice {ex_id} depuis la configuration de {current_assessment}")
                        exercise_ids.add(ex_id)
        
        # Si nous n'avons pas encore d'exercices, essayer les méthodes alternatives
        if not exercise_ids:
            # MÉTHODE 2: Analyser les exercices affichés dans le tableau
            current_exercises = set()
            for row in range(self.results_table.rowCount()):
                # Récupérer le widget personnalisé
                exercise_widget = self.results_table.cellWidget(row, 1)
                if exercise_widget and isinstance(exercise_widget, ExerciseWidget):
                    current_exercises.add(exercise_widget.get_exercise_name())
                
            # Pour chaque nom d'exercice, chercher l'ID correspondant
            for exercise_name in current_exercises:
                for ex_id, config in exercise_configs.items():
                    if config.name == exercise_name:
                        exercise_ids.add(ex_id)
        
        # Pour TD3 spécifiquement, on vérifie manuellement les exercices spécifiques
        if current_assessment == "TD3" and not exercise_ids:
            td3_exercises = ['09-fonction-racine-carree', '10-comptage-mots']
            for ex_id in td3_exercises:
                print(f"Vérification manuelle de l'exercice TD3: {ex_id}")
                # Vérifier si l'exercice existe dans notre configuration
                if ex_id in exercise_configs:
                    exercise_ids.add(ex_id)
                    print(f"Exercice {ex_id} ajouté depuis la liste manuelle")
        
        # Log pour le débogage
        print(f"Exercices identifiés à exécuter: {exercise_ids}")
        
        # Charger les configurations directement depuis les fichiers JSON si nécessaires
        missing_configs = [ex_id for ex_id in exercise_ids if ex_id not in exercise_configs]
        if missing_configs:
            print(f"Certains exercices n'ont pas été trouvés dans la base: {missing_configs}")
            for ex_id in missing_configs:
                config_path = f"configs/{ex_id}.json"
                if os.path.exists(config_path):
                    print(f"Chargement manuel de la configuration depuis {config_path}")
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config_dict = json.load(f)
                            exercise_configs[ex_id] = ExerciseConfig(config_dict)
                            print(f"Configuration chargée avec succès: {ex_id}")
                    except Exception as e:
                        print(f"Erreur lors du chargement de {config_path}: {str(e)}")
        
        # Filtrer les configurations pour ne garder que les exercices identifiés
        exercises_to_process = {ex_id: exercise_configs[ex_id] for ex_id in exercise_ids if ex_id in exercise_configs}
        
        # Vérification de sécurité avant de poursuivre
        if not exercises_to_process:
            QMessageBox.warning(self, "Aucun exercice", "Aucun exercice correspondant n'a été trouvé dans les configurations.")
            self.execute_button.setEnabled(True)
            self.execute_button.setText("Exécuter les codes")
            return
        
        # Log des exercices qui seront traités
        print(f"Exercices à traiter: {list(exercises_to_process.keys())}")
        
        try:
            # Pour chaque étudiant, exécuter uniquement les exercices identifiés
            for student_name in students:
                print(f"Traitement des exercices pour l'étudiant: {student_name}")
                
                # Parcourir uniquement les exercices identifiés
                for ex_id, config in exercises_to_process.items():
                    # Déterminer les fichiers possibles pour cet exercice
                    # On adapte les noms de fichiers en fonction de l'ID de l'exercice
                    base_name = ex_id.split('-', 1)[1] if '-' in ex_id else ex_id
                    
                    potential_files = [
                        f"{ex_id}.java",  # Format ID complet
                        f"{base_name}.java",  # Format nom de base
                        f"{base_name}1.java",
                        f"{base_name}2.java",
                        f"{base_name}3.java",
                        f"{base_name}-while.java",
                        f"{base_name}-do-while.java",
                        f"{base_name}-for.java",
                        f"{base_name}-erreur.java"
                    ]
                    
                    # Format spécifique pour certains exercices
                    if "fonction-racine" in ex_id:
                        potential_files.extend([
                            "fonction-racine-carree.java",
                            "racineCarre.java",
                            "RacineCarree.java",
                            "racine-carree.java",
                            "Racine.java"
                        ])
                    elif "comptage-mots" in ex_id:
                        potential_files.extend([
                            "ComptageMots.java",
                            "comptage-mots.java",
                            "CompteMots.java",
                            "Comptage.java",
                            "Mots.java"
                        ])
                    
                    # Récupérer les entrées de test de la configuration
                    test_inputs = []
                    
                    # Méthode 1: Utiliser la méthode get_test_inputs si disponible
                    if hasattr(config, 'get_test_inputs') and callable(getattr(config, 'get_test_inputs')):
                        raw_inputs = config.get_test_inputs()
                        # Si les résultats sont des dictionnaires, extraire la valeur
                        if raw_inputs and isinstance(raw_inputs[0], dict):
                            test_inputs = [item.get("value", "") for item in raw_inputs]
                        else:
                            test_inputs = raw_inputs
                        
                        print(f"Test inputs trouvés pour {ex_id} via get_test_inputs: {test_inputs}")
                    
                    # Méthode 2: Accéder directement à l'attribut test_inputs
                    if not test_inputs and hasattr(config, 'test_inputs'):
                        raw_inputs = config.test_inputs
                        # Si les résultats sont des dictionnaires, extraire la valeur
                        if raw_inputs and isinstance(raw_inputs[0], dict):
                            test_inputs = [item.get("value", "") for item in raw_inputs]
                        else:
                            test_inputs = raw_inputs
                        
                        print(f"Test inputs trouvés pour {ex_id} via attribut test_inputs: {test_inputs}")
                    
                    # Si aucune entrée n'est configurée, utiliser des entrées par défaut
                    if not test_inputs:
                        # Entrées par défaut selon le type d'exercice
                        if "racine" in base_name.lower() or "fonction-racine" in ex_id:
                            test_inputs = ["4", "9", "16", "-4", "0"]
                            print(f"Utilisation d'entrées par défaut pour racine carrée: {test_inputs}")
                        elif "triangle" in base_name.lower():
                            test_inputs = ["3", "5", "10"]
                            print(f"Utilisation d'entrées par défaut pour triangle: {test_inputs}")
                        elif "comptage" in base_name.lower() or "mots" in base_name.lower():
                            test_inputs = ["Ceci est un test", "Un deux trois quatre", ""]
                            print(f"Utilisation d'entrées par défaut pour comptage mots: {test_inputs}")
                        else:
                            # Par défaut, utiliser une entrée vide
                            test_inputs = [""]
                            print(f"Aucune entrée spécifique pour {ex_id}, utilisation de l'entrée vide")
                    
                    # S'assurer que nous avons au moins une entrée
                    if not test_inputs:
                        test_inputs = [""]
                    
                    # Chercher le fichier correspondant
                    file_found = False
                    for file_name in potential_files:
                        file_path = self.code_executor.find_file_path(student_name, file_name)
                        if file_path:
                            print(f"Fichier pour {ex_id} trouvé: {file_path}")
                            file_found = True
                            
                            # Exécuter avec les entrées de test configurées
                            test_results = self.code_executor.execute_code(file_path, test_inputs)
                            
                            # Ajouter les résultats
                            for i, result in enumerate(test_results):
                                input_val = test_inputs[i] if i < len(test_inputs) else ""
                                
                                input_description = ""
                                if hasattr(config, 'get_test_inputs') and config.get_test_inputs() and i < len(config.get_test_inputs()):
                                    test_config = config.get_test_inputs()[i]
                                    if isinstance(test_config, dict):
                                        input_description = test_config.get("description", "")
                                
                                all_results.append({
                                    "student": student_name,
                                    "exercise": config.name,
                                    "exercise_id": ex_id,
                                    "file_path": file_path,
                                    "input": input_val,
                                    "input_description": input_description,
                                    "success": result["success"],
                                    "compilation_error": result.get("compilation_error", False),
                                    "stdout": result.get("stdout", ""),
                                    "stderr": result.get("stderr", "")
                                })
                            
                            # Si on a trouvé un fichier, on passe à l'exercice suivant
                            break
                    
                    if not file_found:
                        print(f"Aucun fichier trouvé pour l'exercice {ex_id} et l'étudiant {student_name}")
            
            # Vérifier si nous avons des résultats à afficher
            if not all_results:
                QMessageBox.warning(
                    self, 
                    "Aucun résultat d'exécution", 
                    f"Aucun fichier n'a pu être exécuté avec les tests spécifiés. Assurez-vous que:\n\n"
                    f"1. Les fichiers correspondent aux exercices: {', '.join(exercises_to_process.keys())}\n"
                    f"2. Les configurations d'exercices contiennent des données d'entrée de test valides.\n"
                    f"3. Les fichiers Java sont correctement nommés et placés dans les dossiers des étudiants."
                )
            else:
                # Afficher les résultats
                self._display_execution_results(all_results)
        
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Exception lors de l'exécution: {str(e)}\n{traceback_str}")
            QMessageBox.critical(self, "Erreur d'exécution", f"Une erreur est survenue lors de l'exécution: {str(e)}")
        
        # Réactiver le bouton d'exécution
        self.execute_button.setEnabled(True)
        self.execute_button.setText("Exécuter les codes")
    
    def _display_execution_results(self, results):
        """Afficher les résultats d'exécution dans le tableau."""
        # Effacer le tableau des résultats d'exécution
        self.execution_results_table.setRowCount(0)
        
        # Ajouter des logs pour diagnostiquer
        logging.info(f"Affichage de {len(results)} résultats d'exécution")
        types_exercices = set()
        for result in results:
            types_exercices.add(result.get("exercise", ""))
        logging.info(f"Types d'exercices dans les résultats: {types_exercices}")
        
        # Filtrer pour n'avoir qu'un seul résultat par étudiant et type d'exercice
        # (pour les exercices qui ont plusieurs entrées comme triangle-isocele)
        grouped_results = {}
        for result in results:
            student = result.get("student", "")
            exercise = result.get("exercise", "")
            key = f"{student}_{exercise}"
            
            # Si c'est un nouveau groupe ou un résultat réussi, le conserver
            if key not in grouped_results or result.get("success", False):
                grouped_results[key] = result
        
        # Convertir de nouveau en liste
        filtered_results = list(grouped_results.values())
        logging.info(f"Après filtrage: {len(filtered_results)} résultats uniques")
        
        # Ajouter les résultats au tableau
        if filtered_results:
            self.execution_results_table.setRowCount(len(filtered_results))
            
            for i, result in enumerate(filtered_results):
                # Étudiant
                student_item = QTableWidgetItem(result["student"])
                student_item.setTextAlignment(Qt.AlignCenter)
                student_item.setFont(QFont("Arial", 10, QFont.Bold))
                self.execution_results_table.setItem(i, 0, student_item)
                
                # Exercice
                exercise_item = QTableWidgetItem(result["exercise"])
                exercise_item.setTextAlignment(Qt.AlignCenter)
                self.execution_results_table.setItem(i, 1, exercise_item)
                
                # Test
                input_value = result["input"]
                input_description = result.get("input_description", "")
                
                if input_description:
                    test_text = f"{input_description} (n = {input_value})"
                elif input_value:
                    test_text = f"n = {input_value}"
                else:
                    test_text = "Exécution sans entrée"
                    
                test_item = QTableWidgetItem(test_text)
                test_item.setTextAlignment(Qt.AlignCenter)
                self.execution_results_table.setItem(i, 2, test_item)
                
                # Résultat
                result_widget = ExecutionResultWidget(
                    success=result["success"],
                    compilation_error=result.get("compilation_error", False),
                    output_text=result.get("stdout", "")
                )
                
                self.execution_results_table.setCellWidget(i, 3, result_widget)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setAlignment(Qt.AlignCenter)
                
                # Bouton pour voir la sortie complète
                view_output_button = QPushButton("Voir la sortie")
                view_output_button.setIcon(QIcon("icons/info.svg"))
                view_output_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f8f9fa;
                        border: 1px solid #dfe4ea;
                        border-radius: 4px;
                        padding: 5px 10px;
                        color: #3498db;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                    }
                """)
                
                # Préparer le texte complet pour l'affichage
                full_output = f"=== SORTIE STANDARD ===\n{result.get('stdout', '')}\n\n"
                if result.get("stderr", ""):
                    full_output += f"=== ERREURS ===\n{result.get('stderr', '')}"
                
                # Stocker la sortie complète et configurer le bouton
                view_output_button.clicked.connect(
                    lambda checked, output=full_output, title=f"{result['student']} - {result['exercise']}": 
                    self.show_output_dialog(title, output)
                )
                
                actions_layout.addWidget(view_output_button)
                
                self.execution_results_table.setCellWidget(i, 4, actions_widget)
            
            # Ajuster les hauteurs de ligne
            for i in range(self.execution_results_table.rowCount()):
                self.execution_results_table.setRowHeight(i, 80)  # Augmenter la hauteur des lignes
        else:
            # Aucun résultat à afficher
            QMessageBox.information(self, "Aucun résultat", "Aucun fichier n'a pu être exécuté avec les tests spécifiés.")
    
    def get_student_list(self):
        """Récupère la liste des étudiants affichés dans le tableau de résultats"""
        students = set()
        for row in range(self.results_table.rowCount()):
            student_item = self.results_table.item(row, 0)
            if student_item:
                students.add(student_item.text())
        return list(students)
    
    def get_exercises_for_student(self, student):
        """Récupère les exercices d'un étudiant spécifique depuis le tableau de résultats"""
        exercises = []
        
        # Trouver la première ligne de l'étudiant
        start_row = -1
        for row in range(self.results_table.rowCount()):
            student_item = self.results_table.item(row, 0)
            if student_item and student_item.text() == student:
                start_row = row
                break
        
        if start_row == -1:
            # Étudiant non trouvé
            return []
        
        # Déterminer le nombre de lignes pour cet étudiant (rowspan)
        span_rows = 1
        if self.results_table.rowSpan(start_row, 0) > 1:
            span_rows = self.results_table.rowSpan(start_row, 0)
        
        # Récupérer les exercices pour chaque ligne
        for row in range(start_row, start_row + span_rows):
            exercise_widget = self.results_table.cellWidget(row, 1)
            if isinstance(exercise_widget, ExerciseWidget):
                exercise_name = exercise_widget.get_exercise_name()
                file_name = exercise_widget.get_file_name()
                
                # Déterminer l'ID de l'exercice (à partir de la configuration)
                exercise_id = None
                # Si une analyse a été effectuée, récupérer l'ID depuis les données d'analyse
                try:
                    # Trouver l'ID dans les configurations actives
                    config_loader = ConfigLoader(os.getcwd())
                    for ex_id, config in config_loader.get_all_exercise_configs().items():
                        if config.name == exercise_name or ex_id.lower() in file_name.lower():
                            exercise_id = ex_id
                            break
                except Exception as e:
                    print(f"Erreur lors de la récupération de l'ID d'exercice: {e}")
                
                # Utiliser le nom d'exercice si on n'a pas pu déterminer l'ID
                if not exercise_id:
                    exercise_id = exercise_name.replace(" ", "-").lower()
                
                # Récupérer le statut depuis le widget
                status_widget = self.results_table.cellWidget(row, 2)
                status = "En attente"
                if isinstance(status_widget, StatusWidget):
                    status = status_widget.get_status_text()
                
                # Essayer d'obtenir le chemin du fichier
                file_path = None
                try:
                    # Format attendu: répertoire étudiant/nom du fichier
                    file_path = os.path.join(os.getcwd(), "tests", "java_samples", student, file_name)
                    if not os.path.exists(file_path):
                        # Chercher dans tous les dossiers possibles
                        for td_dir in glob.glob(os.path.join(os.getcwd(), "tests", "java_samples", "TD*")):
                            possible_path = os.path.join(td_dir, student, file_name)
                            if os.path.exists(possible_path):
                                file_path = possible_path
                                break
                except Exception as e:
                    print(f"Erreur lors de la récupération du chemin du fichier: {e}")
                
                # Ajouter l'exercice à la liste
                exercises.append({
                    'id': exercise_id,
                    'file': file_name,
                    'status': status,
                    'path': file_path
                })
        
        return exercises
    
    def get_current_assessment_name(self):
        """Récupère le nom de l'évaluation actuellement affichée"""
        try:
            # Vérifier si le nom de l'évaluation est stocké dans le tableau
            for row in range(self.results_table.rowCount()):
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item and "TD" in item.text():
                        # Chercher un pattern "TD1", "TD2", etc.
                        import re
                        match = re.search(r'TD\d+', item.text())
                        if match:
                            return match.group(0)
            
            # Si on n'a pas trouvé dans le tableau, essayer dans le titre
            if hasattr(self, 'title_label') and isinstance(self.title_label, QLabel):
                title_text = self.title_label.text()
                if "TD" in title_text:
                    match = re.search(r'TD\d+', title_text)
                    if match:
                        return match.group(0)
            
            # Essayer de déterminer d'après les exercices affichés
            exercise_ids = []
            for row in range(self.results_table.rowCount()):
                exercise_widget = self.results_table.cellWidget(row, 1)
                if isinstance(exercise_widget, ExerciseWidget):
                    exercise_name = exercise_widget.get_exercise_name()
                    exercise_ids.append(exercise_name)
            
            # Associer les noms d'exercices aux TDs
            if any("fonction-racine" in ex.lower() or "comptage-mots" in ex.lower() for ex in exercise_ids):
                return "TD3"
            elif any("triangle" in ex.lower() or "sequence" in ex.lower() for ex in exercise_ids):
                return "TD1"
        except Exception as e:
            print(f"Erreur lors de la récupération du nom de l'évaluation: {e}")
        
        return None
    
    def get_analysis_data(self, student, exercise_id):
        """Récupère les données d'analyse pour un étudiant et un exercice spécifiques"""
        # Chercher l'exercice dans les résultats
        for row in range(self.results_table.rowCount()):
            student_item = self.results_table.item(row, 0)
            if student_item and student_item.text() == student:
                exercise_widget = self.results_table.cellWidget(row, 1)
                if isinstance(exercise_widget, ExerciseWidget):
                    exercise_name = exercise_widget.get_exercise_name()
                    file_name = exercise_widget.get_file_name()
                    
                    # Vérifier si cet exercice correspond à l'ID demandé
                    if (exercise_id == exercise_name.replace(" ", "-").lower() or
                        exercise_id.lower() in file_name.lower()):
                        
                        # Récupérer le code source
                        code = None
                        try:
                            # Format attendu: répertoire étudiant/nom du fichier
                            file_path = None
                            for td_dir in glob.glob(os.path.join(os.getcwd(), "tests", "java_samples", "TD*")):
                                possible_path = os.path.join(td_dir, student, file_name)
                                if os.path.exists(possible_path):
                                    file_path = possible_path
                                    break
                            
                            if file_path and os.path.exists(file_path):
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    code = f.read()
                        except Exception as e:
                            print(f"Erreur lors de la lecture du code source: {e}")
                        
                        # Récupérer les résultats d'analyse depuis le widget de statut
                        status_widget = self.results_table.cellWidget(row, 2)
                        analysis_results = "Analyse effectuée mais résultats non disponibles"
                        if isinstance(status_widget, StatusWidget):
                            analysis_results = status_widget.get_detailed_status()
                        
                        # Récupérer les résultats d'exécution (si disponibles)
                        execution_results = "Pas de résultats d'exécution disponibles"
                        
                        # Si aucun code trouvé, créer un squelette basique
                        if not code:
                            if "triangle" in exercise_id.lower():
                                code = "public class Triangle {\n    public static boolean estTriangleIsocele(int a, int b, int c) {\n        // Code manquant\n        return false;\n    }\n}"
                            elif "sequence" in exercise_id.lower():
                                code = "public class Sequence {\n    public static int sommeSequence(int n) {\n        // Code manquant\n        return 0;\n    }\n}"
                            elif "racine" in exercise_id.lower():
                                code = "public class RacineCarree {\n    public static double calculerRacineCarree(double nombre) {\n        // Code manquant\n        return 0.0;\n    }\n}"
                            elif "comptage" in exercise_id.lower() or "mots" in exercise_id.lower():
                                code = "public class ComptageMots {\n    public static int compterMots(String texte) {\n        // Code manquant\n        return 0;\n    }\n}"
                            else:
                                code = f"// Code pour l'exercice {exercise_id} non disponible"
                        
                        return code, analysis_results, execution_results 
        
        # Si on n'a pas trouvé l'exercice, retourner des valeurs par défaut
        return None, "Pas de résultats d'analyse disponibles", "Pas de résultats d'exécution disponibles" 