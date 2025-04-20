"""
Widget principal pour l'affichage et l'analyse des résultats des étudiants.
"""

import os
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem, QComboBox, 
                           QPushButton, QLineEdit, QFrame, QHeaderView,
                           QSizePolicy, QMessageBox, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QFont

from teach_assit.core.analysis.config_loader import ConfigLoader
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
                    
                    # Déterminer l'exercice associé
                    exercise_id = "Non spécifié"
                    for ex_id in exercise_configs.keys():
                        if ex_id.lower() in file_path.lower() or ex_id.split('-')[-1].lower() in file_path.lower():
                            exercise_id = ex_id
                            break
                    
                    exercise_config = exercise_configs.get(exercise_id)
                    exercise_name = exercise_config.name if exercise_config else "Inconnu"
                    
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
        
        # Ajuster les hauteurs de ligne pour le contenu
        for i in range(self.results_table.rowCount()):
            self.results_table.setRowHeight(i, 90)  # Augmenter légèrement la hauteur pour mieux afficher le contenu
    
    def show_details_dialog(self, title, details):
        """Afficher les détails dans un dialogue modal."""
        # Créer un dictionnaire de détails avec le titre comme nom d'exercice
        exercise_details = {
            "exercise_name": title,
            "report": details
        }
        dialog = DetailsDialog(self, exercise_details)
        dialog.exec_()
    
    def show_output_dialog(self, title, output_text):
        """Afficher la sortie complète d'une exécution dans une fenêtre modale."""
        dialog = OutputDialog(self, title, output_text)
        dialog.exec_()
    
    def execute_all_codes(self):
        """Exécuter tous les codes des étudiants avec les entrées de test configurées."""
        # Définir des entrées de test par défaut au cas où la configuration n'en contiendrait pas
        default_triangle_inputs = ["3", "5", "10"]
        
        # Désactiver le bouton d'exécution pendant le traitement
        self.execute_button.setEnabled(False)
        self.execute_button.setText("Exécution en cours...")
        
        # Initialiser le chargeur de configurations
        config_loader = ConfigLoader()
        config_loader.load_all_configs()
        exercise_configs = config_loader.get_all_exercise_configs()
        
        # Structure de données pour stocker les résultats
        all_results = []
        
        # Obtenir la liste de tous les étudiants du tableau de résultats
        students = set()
        for row in range(self.results_table.rowCount()):
            student_item = self.results_table.item(row, 0)
            if student_item:
                students.add(student_item.text())
        
        # Récupérer les exercices présents dans le tableau des résultats
        current_exercises = set()
        for row in range(self.results_table.rowCount()):
            # Au lieu de chercher un QTableWidgetItem, récupérer le widget personnalisé
            exercise_widget = self.results_table.cellWidget(row, 1)
            if exercise_widget and isinstance(exercise_widget, ExerciseWidget):
                # Récupérer le nom de l'exercice depuis le widget
                current_exercises.add(exercise_widget.get_exercise_name())
        
        # Si aucun exercice n'a été trouvé, essayer une méthode alternative
        if not current_exercises:
            # Essayer de récupérer les exercices depuis les labels dans les widgets
            for row in range(self.results_table.rowCount()):
                exercise_widget = self.results_table.cellWidget(row, 1)
                if exercise_widget:
                    # Tenter de récupérer le nom à partir des widgets enfants
                    for child in exercise_widget.findChildren(QLabel):
                        if child.objectName() == "exercise_label":
                            current_exercises.add(child.text())
                            break
        
        logging.info(f"Exercices actuellement analysés: {current_exercises}")
        
        # Mapper les noms d'exercices aux IDs pour pouvoir filtrer les configurations
        exercise_name_to_id = {}
        for ex_id, config in exercise_configs.items():
            exercise_name_to_id[config.name] = ex_id
        
        # Afficher les noms d'exercices trouvés et leurs correspondances
        logging.info(f"Noms d'exercices configurés: {list(exercise_name_to_id.keys())}")
        
        # Filtrer les exercices à traiter en fonction des exercices actuellement analysés
        exercises_to_process = {}
        for exercise_name in current_exercises:
            # Chercher une correspondance exacte d'abord
            ex_id = exercise_name_to_id.get(exercise_name)
            
            # Si pas de correspondance exacte, chercher des correspondances partielles
            if not ex_id:
                for name, id in exercise_name_to_id.items():
                    # Comparer en minuscules pour être plus flexible
                    if (name.lower() in exercise_name.lower() or 
                        exercise_name.lower() in name.lower()):
                        ex_id = id
                        logging.info(f"Correspondance partielle trouvée: '{exercise_name}' -> '{name}' (ID: {id})")
                        break
            
            if ex_id and ex_id in exercise_configs:
                exercises_to_process[ex_id] = exercise_configs[ex_id]
                logging.info(f"Exercice à traiter: '{exercise_name}' -> ID: {ex_id}")
            else:
                logging.warning(f"Aucune configuration trouvée pour l'exercice '{exercise_name}'")
        
        if not exercises_to_process:
            QMessageBox.warning(self, "Aucun exercice", "Aucun exercice correspondant n'a été trouvé dans les configurations.")
            self.execute_button.setEnabled(True)
            self.execute_button.setText("Exécuter les codes")
            return
        
        logging.info(f"Exercices à traiter: {list(exercises_to_process.keys())}")
        
        try:
            # Pour chaque étudiant, exécuter uniquement les exercices actuellement analysés
            for student_name in students:
                logging.info(f"Traitement des exercices pour l'étudiant: {student_name}")
                
                # Parcourir uniquement les exercices actuellement analysés
                for ex_id, config in exercises_to_process.items():
                    # Déterminer les fichiers possibles pour cet exercice
                    # On adapte les noms de fichiers en fonction de l'ID de l'exercice
                    base_name = ex_id.split('-', 1)[1] if '-' in ex_id else ex_id
                    
                    potential_files = [
                        f"{base_name}.java",
                        f"{base_name}1.java",
                        f"{base_name}2.java",
                        f"{base_name}3.java",
                        f"{base_name}-while.java",
                        f"{base_name}-do-while.java",
                        f"{base_name}-for.java",
                        f"{base_name}-erreur.java"
                    ]
                    
                    # Récupérer les entrées de test de la configuration
                    test_inputs = []
                    if config.get_test_inputs():
                        test_inputs = [input_config["value"] for input_config in config.get_test_inputs()]
                    else:
                        # Utiliser des entrées par défaut si aucune entrée n'est configurée
                        if "triangle" in base_name.lower():
                            test_inputs = default_triangle_inputs
                        else:
                            # Par défaut, utiliser une entrée vide pour les autres exercices
                            test_inputs = [""]
                    
                    # Chercher le fichier correspondant
                    for file_name in potential_files:
                        file_path = self.code_executor.find_file_path(student_name, file_name)
                        if file_path:
                            logging.info(f"Fichier {base_name} trouvé pour {student_name}: {file_path}")
                            
                            # Exécuter avec les entrées de test configurées
                            test_results = self.code_executor.execute_code(file_path, test_inputs)
                            
                            # Ajouter les résultats
                            for i, result in enumerate(test_results):
                                input_val = test_inputs[i] if i < len(test_inputs) else ""
                                
                                input_description = ""
                                if config.get_test_inputs() and i < len(config.get_test_inputs()):
                                    input_description = config.get_test_inputs()[i].get("description", "")
                                
                                all_results.append({
                                    "student": student_name,
                                    "exercise": config.name,
                                    "file_path": file_path,
                                    "input": input_val,
                                    "input_description": input_description,
                                    "success": result["success"],
                                    "compilation_error": result.get("compilation_error", False),
                                    "stdout": result.get("stdout", ""),
                                    "stderr": result.get("stderr", "")
                                })
                            break
            
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