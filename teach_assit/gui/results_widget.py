"""
Module pour l'affichage et l'analyse des résultats des étudiants.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QComboBox, 
                            QPushButton, QLineEdit, QFrame, QHeaderView,
                            QTextEdit, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor
import os

from teach_assit.core.analysis.models import ExerciseConfig

# Symboles pour l'UI
SYMBOL_OK = "✅"
SYMBOL_FAIL = "❌"
SYMBOL_WARNING = "⚠️"

def fix_encoding(text):
    """Corriger l'encodage des caractères accentués"""
    if not text:
        return text
    
    # Tentatives de correction d'encodage
    try:
        # Si déjà en UTF-8 mais mal interprété
        return text.encode('latin1').decode('utf-8')
    except:
        try:
            # Si encodé en latin1
            return text.encode('latin1').decode('latin1')
        except:
            pass
    return text


class ResultsWidget(QWidget):
    """Widget pour afficher et analyser les résultats des évaluations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Définir la politique de taille pour que le widget prenne toute la place disponible
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Forcer le widget à prendre tout l'espace disponible
        self.setMinimumSize(800, 600)  # Taille minimale raisonnable
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur de l'onglet résultats."""
        # Créer le layout principal sans marges
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

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
        main_layout.addWidget(header_container)

        # Conteneur principal pour le tableau et les stats
        content_container = QWidget()
        content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 0, 20, 20)
        content_layout.setSpacing(20)

        # Tableau des résultats
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
        
        content_layout.addWidget(self.results_table)

        # Statistiques de résumé
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        def create_stat_box(title, value):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dfe6e9;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            layout = QVBoxLayout(frame)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
            layout.addWidget(title_label)
            
            value_label = QLabel(value)
            value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(value_label)
            
            return frame
        
        # Créer et ajouter les boîtes de statistiques
        self.stats_boxes = {
            'total': create_stat_box("Nombre de fichiers", "0"),
            'success': create_stat_box("Fichiers valides", "0"),
            'syntax_errors': create_stat_box("Erreurs de syntaxe", "0"),
            'missing_methods': create_stat_box("Méthodes manquantes", "0")
        }
        
        for box in self.stats_boxes.values():
            stats_layout.addWidget(box)
        
        content_layout.addLayout(stats_layout)
        main_layout.addWidget(content_container)
    
    def clear(self):
        """Effacer tous les résultats."""
        self.results_table.setRowCount(0)
        self.update_stats({'total': 0, 'success': 0, 'syntax_errors': 0, 'missing_methods': 0})
    
    def update_stats(self, stats):
        """Mettre à jour les statistiques."""
        self.stats_boxes['total'].findChild(QLabel, "", Qt.FindDirectChildrenOnly).setText(str(stats['total']))
        self.stats_boxes['success'].findChild(QLabel, "", Qt.FindDirectChildrenOnly).setText(str(stats['success']))
        self.stats_boxes['syntax_errors'].findChild(QLabel, "", Qt.FindDirectChildrenOnly).setText(str(stats['syntax_errors']))
        self.stats_boxes['missing_methods'].findChild(QLabel, "", Qt.FindDirectChildrenOnly).setText(str(stats['missing_methods']))
    
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
        
        # Compteurs pour les statistiques
        stats = {'total': 0, 'success': 0, 'syntax_errors': 0, 'missing_methods': 0}
        
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
                    exercise_widget = QWidget()
                    exercise_widget.setStyleSheet(row_style)
                    exercise_layout = QVBoxLayout(exercise_widget)
                    exercise_layout.setContentsMargins(8, 8, 8, 8)
                    exercise_layout.setSpacing(3)
                    
                    # Titre de l'exercice
                    title_label = QLabel(exercise_name)
                    title_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
                    exercise_layout.addWidget(title_label)
                    
                    # Nom du fichier
                    file_label = QLabel(file_name)
                    file_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
                    exercise_layout.addWidget(file_label)
                    
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
                    
                    # Widget pour le statut
                    status_widget = QWidget()
                    status_widget.setStyleSheet(row_style)
                    status_layout = QVBoxLayout(status_widget)
                    status_layout.setContentsMargins(5, 5, 5, 5)  # Réduire les marges
                    status_layout.setSpacing(3)  # Réduire l'espacement
                    
                    # Créer une grille 2x3 pour les statuts
                    status_grid = QWidget()
                    grid_layout = QHBoxLayout(status_grid)
                    grid_layout.setContentsMargins(0, 0, 0, 0)  # Pas de marges
                    grid_layout.setSpacing(5)  # Espacement réduit
                    
                    # Colonne gauche
                    left_column = QWidget()
                    left_layout = QVBoxLayout(left_column)
                    left_layout.setContentsMargins(0, 0, 0, 0)
                    left_layout.setSpacing(3)  # Réduire l'espacement
                    
                    # Colonne droite
                    right_column = QWidget()
                    right_layout = QVBoxLayout(right_column)
                    right_layout.setContentsMargins(0, 0, 0, 0)
                    right_layout.setSpacing(3)  # Réduire l'espacement
                    
                    # Ajouter des status checks avec icônes
                    statuses = [
                        {"name": "Syntaxe", "ok": syntax_ok, "warning": False},
                        {"name": "Méthodes", "ok": methods_ok, "warning": True if not methods_ok else False},
                        {"name": "Structures", "ok": control_structures_ok, "warning": False},
                        {"name": "Nommage", "ok": naming_ok, "warning": False},
                        {"name": "Opérateurs", "ok": operators_ok, "warning": False},
                        {"name": "Patterns", "ok": patterns_ok, "warning": True if not patterns_ok else False}
                    ]
                    
                    # Diviser les statuts entre les deux colonnes
                    for j, status in enumerate(statuses):
                        icon = SYMBOL_OK if status["ok"] else SYMBOL_WARNING if status["warning"] else SYMBOL_FAIL
                        color = "#2ecc71" if status["ok"] else "#f39c12" if status["warning"] else "#e74c3c"
                        
                        status_label = QLabel(f"{icon} {status['name']}")
                        status_label.setStyleSheet(f"font-size: 12px; color: {color};")
                        
                        if j < 3:
                            left_layout.addWidget(status_label)
                        else: 
                            right_layout.addWidget(status_label)
                    
                    grid_layout.addWidget(left_column)
                    grid_layout.addWidget(right_column)
                    status_layout.addWidget(status_grid)
                    
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
                    result_widget = QWidget()
                    result_widget.setStyleSheet(row_style)
                    result_layout = QVBoxLayout(result_widget)
                    result_layout.setContentsMargins(5, 5, 5, 5)  # Réduire les marges
                    result_layout.setAlignment(Qt.AlignCenter)  # Centrer le contenu
                    
                    # Texte du résultat global
                    result_color = "#2ecc71" if all_ok else "#e74c3c"
                    result_text = QLabel(f"{passed_checks}/{total_checks} vérifications - {estimated_score}/{max_points} pt")
                    result_text.setStyleSheet(f"font-weight: bold; color: {result_color}; font-size: 13px;")
                    result_layout.addWidget(result_text)
                    
                    self.results_table.setCellWidget(row_index, 3, result_widget)
                    
                    # Widget pour les actions (bouton détails)
                    actions_widget = QWidget()
                    actions_widget.setStyleSheet(row_style)
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(5, 5, 5, 5)  # Réduire les marges
                    actions_layout.setAlignment(Qt.AlignCenter)  # Centrer le bouton
                    
                    # Bouton détails
                    details_button = QPushButton("Détails")
                    details_button.setIcon(QIcon("icons/info.svg"))
                    details_button.setStyleSheet("""
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
                    
                    # Stocker les détails pour affichage ultérieur
                    details_data = self.format_detailed_report(result, exercise_config)
                    details_button.clicked.connect(lambda checked, data=details_data, title=f"{student} - {file_name}": 
                                                 self.show_details_dialog(title, data))
                    
                    actions_layout.addWidget(details_button)
                    actions_layout.addStretch()
                    
                    self.results_table.setCellWidget(row_index, 4, actions_widget)
                    
                    # Mettre à jour les statistiques
                    stats['total'] += 1
                    
                    if all_ok:
                        stats['success'] += 1
                    
                    if not syntax_ok:
                        stats['syntax_errors'] += 1
                    
                    if not methods_ok:
                        stats['missing_methods'] += 1
                
                current_row += num_exercises
        
        # Mettre à jour les statistiques
        self.update_stats(stats)
        
        # Ajuster les hauteurs de ligne pour le contenu
        for i in range(self.results_table.rowCount()):
            self.results_table.setRowHeight(i, 90)  # Augmenter légèrement la hauteur pour mieux afficher le contenu
    
    def show_details_dialog(self, title, details):
        """Afficher les détails dans un dialogue modal."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Détails - {title}")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QScrollArea {
                border: none;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Zone de défilement pour le contenu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Formater le HTML pour les détails
        html_details = details
        html_details = html_details.replace(SYMBOL_OK, f'<span style="color: #2ecc71;">{SYMBOL_OK}</span>')
        html_details = html_details.replace(SYMBOL_FAIL, f'<span style="color: #e74c3c;">{SYMBOL_FAIL}</span>')
        html_details = html_details.replace(SYMBOL_WARNING, f'<span style="color: #f39c12;">{SYMBOL_WARNING}</span>')
        
        # Convertir les sauts de ligne en balises <br>
        html_details = html_details.replace("\n", "<br>")
        
        # Ajouter une mise en forme pour les sections
        for section in ["SYNTAXE:", "MÉTHODES REQUISES:", "MÉTHODES TROUVÉES:", "STRUCTURES DE CONTRÔLE:", 
                       "CONVENTIONS DE NOMMAGE:", "PORTÉE DES VARIABLES:", "OPÉRATEURS NON AUTORISÉS:", 
                       "OPÉRATEURS:", "PATTERNS REQUIS:", "SUGGESTIONS D'AMÉLIORATION:", "RÉSUMÉ GLOBAL:", 
                       "NOTE ESTIMÉE:", "RÉSULTAT GLOBAL:"]:
            html_details = html_details.replace(section, f'<b style="color: #3498db;">{section}</b>')
        
        # Mise en évidence des lignes de séparation
        html_details = html_details.replace("="*30, '<hr style="border: 1px solid #dcdde1;">')
        
        # Pour conserver l'espacement
        html_details = html_details.replace(" ", "&nbsp;")
        
        # Texte détaillé
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setHtml(html_details)
        details_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 15px;
                font-family: monospace;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        content_layout.addWidget(details_text)
        scroll_area.setWidget(content_widget)
        
        # Bouton Fermer
        close_button = QPushButton("Fermer")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        
        # Ajouter les widgets au layout principal
        layout.addWidget(scroll_area)
        layout.addWidget(close_button, 0, Qt.AlignRight)
        
        dialog.exec_()
    
    def format_detailed_report(self, result, exercise_config):
        """Formater un rapport détaillé pour l'affichage dans le tableau."""
        details = ""
        
        # Vérification de la syntaxe
        syntax_ok = not result.get('syntax_errors', []) and 'error' not in result
        syntax_symbol = SYMBOL_OK if syntax_ok else SYMBOL_FAIL
        details += f"{syntax_symbol} SYNTAXE: " + ("Code valide" if syntax_ok else "Code invalide") + "\n"
        
        if 'error' in result:
            error_msg = fix_encoding(result['error'])
            details += f"  {SYMBOL_FAIL} Erreur d'analyse: {error_msg}\n"
        elif result.get('syntax_errors', []):
            for error in result['syntax_errors']:
                error_msg = fix_encoding(error.get('message', 'Erreur inconnue'))
                details += f"  {SYMBOL_FAIL} Ligne {error.get('line', 'inconnue')}: {error_msg}\n"
        
        # Vérification des méthodes
        methods_ok = not result.get('missing_methods', [])
        methods_symbol = SYMBOL_OK if methods_ok else SYMBOL_WARNING
        details += f"\n{methods_symbol} MÉTHODES REQUISES: "
        
        if methods_ok:
            details += "Toutes les méthodes requises sont présentes\n"
        else:
            details += "Méthodes manquantes ou incorrectes\n"
            for m in result.get('missing_methods', []):
                method_name = m.get('name', '')
                method_params = m.get('expected_params', [])
                method_return = m.get('expected_return', 'void')
                details += f"  {SYMBOL_FAIL} {method_return} {method_name}({', '.join(method_params)})\n"
        
        # Méthodes trouvées
        if 'analysis_details' in result and 'found_methods' in result['analysis_details'] and result['analysis_details']['found_methods']:
            details += f"\n{SYMBOL_OK} MÉTHODES TROUVÉES:\n"
            for method_name, method_list in result['analysis_details']['found_methods'].items():
                for method in method_list:
                    params = method.get('params', [])
                    return_type = method.get('return', 'void')
                    details += f"  {SYMBOL_OK} {return_type} {method_name}({', '.join(params)})\n"
        
        # Structures de contrôle
        if 'analysis_details' in result and 'control_structures' in result['analysis_details']:
            control_structures = result['analysis_details']['control_structures']
            found_structures = control_structures.get('found', [])
            missing_structures = control_structures.get('missing', [])
            
            control_symbol = SYMBOL_OK if not missing_structures else SYMBOL_FAIL
            details += f"\n{control_symbol} STRUCTURES DE CONTRÔLE:\n"
            
            if found_structures:
                details += f"  {SYMBOL_OK} Structures trouvées: {', '.join(found_structures)}\n"
            
            if missing_structures:
                details += f"  {SYMBOL_FAIL} Structures manquantes: {', '.join(missing_structures)}\n"
        
        # Conventions de nommage
        if 'analysis_details' in result and 'naming_conventions' in result['analysis_details']:
            naming_errors = result['analysis_details']['naming_conventions'].get('errors', [])
            naming_symbol = SYMBOL_OK if not naming_errors else SYMBOL_FAIL
            
            details += f"\n{naming_symbol} CONVENTIONS DE NOMMAGE:\n"
            
            if naming_errors:
                for error in naming_errors:
                    message = fix_encoding(error.get('message', ''))
                    details += f"  {SYMBOL_FAIL} {message}\n"
            else:
                details += f"  {SYMBOL_OK} Toutes les conventions de nommage sont respectées.\n"
        
        # Portée des variables
        if 'analysis_details' in result and 'variable_scopes' in result['analysis_details']:
            scope_errors = result['analysis_details']['variable_scopes'].get('errors', [])
            scope_symbol = SYMBOL_OK if not scope_errors else SYMBOL_FAIL
            
            details += f"\n{scope_symbol} PORTÉE DES VARIABLES:\n"
            
            if scope_errors:
                for error in scope_errors:
                    message = fix_encoding(error.get('message', ''))
                    details += f"  {SYMBOL_FAIL} {message}\n"
            else:
                details += f"  {SYMBOL_OK} Aucun problème de portée de variables détecté.\n"
        
        # Opérateurs non autorisés
        if 'analysis_details' in result and 'disallowed_operators' in result['analysis_details']:
            disallowed_operators = result['analysis_details']['disallowed_operators']
            operators_symbol = SYMBOL_OK if not disallowed_operators else SYMBOL_FAIL
            
            if disallowed_operators:
                details += f"\n{operators_symbol} OPÉRATEURS NON AUTORISÉS:\n"
                for op_info in disallowed_operators:
                    message = fix_encoding(op_info.get('message', ''))
                    details += f"  {SYMBOL_FAIL} {message}\n"
            else:
                details += f"\n{operators_symbol} OPÉRATEURS: Tous les opérateurs utilisés sont autorisés.\n"
        
        # Patterns requis
        if 'analysis_details' in result and 'missing_patterns' in result['analysis_details']:
            missing_patterns = result['analysis_details']['missing_patterns']
            patterns_ok = not missing_patterns
            patterns_symbol = SYMBOL_OK if patterns_ok else SYMBOL_WARNING
            
            details += f"\n{patterns_symbol} PATTERNS REQUIS:\n"
            
            # Si nous avons un exercise_config, vérifier tous les patterns
            if exercise_config:
                custom_patterns = exercise_config.get_custom_patterns()
                for pattern_info in custom_patterns:
                    pattern_desc = fix_encoding(pattern_info.get('description', 'Pattern sans description'))
                    required = pattern_info.get('required', False)
                    
                    if not required:
                        continue
                    
                    # Vérifier si le pattern est manquant
                    is_missing = False
                    error_msg = ""
                    for missing_pattern in missing_patterns:
                        missing_desc = fix_encoding(missing_pattern.get('description', ''))
                        if missing_desc == pattern_desc:
                            is_missing = True
                            error_msg = fix_encoding(missing_pattern.get('errorMessage', ''))
                            break
                    
                    pattern_status = SYMBOL_FAIL if is_missing else SYMBOL_OK
                    details += f"  {pattern_status} {pattern_desc}\n"
                    
                    if is_missing and error_msg:
                        details += f"      {SYMBOL_WARNING} {error_msg}\n"
            else:
                # Sans config, juste lister les patterns manquants
                if patterns_ok:
                    details += f"  {SYMBOL_OK} Tous les patterns requis sont présents\n"
                else:
                    for pattern in missing_patterns:
                        pattern_desc = fix_encoding(pattern.get('description', ''))
                        error_msg = fix_encoding(pattern.get('errorMessage', ''))
                        details += f"  {SYMBOL_FAIL} {pattern_desc}\n"
                        if error_msg:
                            details += f"      {SYMBOL_WARNING} {error_msg}\n"
        
        # Suggestions
        if 'analysis_details' in result and 'suggestions' in result['analysis_details'] and result['analysis_details']['suggestions']:
            details += f"\n{SYMBOL_WARNING} SUGGESTIONS D'AMÉLIORATION:\n"
            for suggestion in result['analysis_details']['suggestions']:
                details += f"  {SYMBOL_WARNING} {fix_encoding(suggestion)}\n"
        
        # Calcul du résumé
        if exercise_config and 'analysis_details' in result:
            # Vérifier le statut de chaque critère
            syntax_ok = not result.get('syntax_errors', []) and 'error' not in result
            methods_ok = not result.get('missing_methods', [])
            patterns_ok = not (result.get('analysis_details', {}).get('missing_patterns', []))
            
            # Opérateurs
            operators_ok = True
            if 'disallowed_operators' in result['analysis_details']:
                operators_ok = not result['analysis_details']['disallowed_operators']
            
            # Structures de contrôle
            control_structures_ok = True
            if 'control_structures' in result['analysis_details']:
                control_structures_ok = not result['analysis_details']['control_structures'].get('missing', [])
            
            # Conventions de nommage
            naming_ok = True
            if 'naming_conventions' in result['analysis_details']:
                naming_ok = not result['analysis_details']['naming_conventions'].get('errors', [])
            
            # Portée des variables
            scope_ok = True
            if 'variable_scopes' in result['analysis_details']:
                scope_ok = not result['analysis_details']['variable_scopes'].get('errors', [])
            
            # Compter le nombre de vérifications réussies
            total_checks = 7  # syntaxe, méthodes, patterns, opérateurs, structures, nommage, portée
            passed_checks = sum([syntax_ok, methods_ok, patterns_ok, operators_ok, control_structures_ok, naming_ok, scope_ok])
            
            # Note estimée (10 par défaut si non spécifié)
            max_points = exercise_config.max_points if hasattr(exercise_config, 'max_points') else 10
            estimated_score = round((passed_checks / total_checks) * max_points, 1)
            
            # Ajouter le résumé
            details += f"\n{'='*30}\nRÉSUMÉ GLOBAL: {passed_checks}/{total_checks} vérifications réussies\n"
            details += f"NOTE ESTIMÉE: {estimated_score}/{max_points} points\n"
            
            # Résultat global
            all_ok = syntax_ok and methods_ok and patterns_ok and operators_ok and control_structures_ok and naming_ok and scope_ok
            if all_ok:
                details += f"\n{SYMBOL_OK} RÉSULTAT GLOBAL: SUCCÈS"
            else:
                details += f"\n{SYMBOL_FAIL} RÉSULTAT GLOBAL: DES PROBLÈMES ONT ÉTÉ DÉTECTÉS\n  Détail des problèmes:"
                
                if not syntax_ok:
                    details += f"\n    {SYMBOL_FAIL} Problèmes de syntaxe"
                if not methods_ok:
                    details += f"\n    {SYMBOL_FAIL} Méthodes manquantes ou incorrectes"
                if not patterns_ok:
                    details += f"\n    {SYMBOL_FAIL} Patterns requis manquants"
                if not operators_ok:
                    details += f"\n    {SYMBOL_FAIL} Utilisation d'opérateurs non autorisés"
                if not control_structures_ok:
                    details += f"\n    {SYMBOL_FAIL} Structures de contrôle manquantes"
                if not naming_ok:
                    details += f"\n    {SYMBOL_FAIL} Conventions de nommage non respectées"
                if not scope_ok:
                    details += f"\n    {SYMBOL_FAIL} Problèmes de portée des variables"
        
        return details
    
    def add_sample_data(self):
        """Ajouter des données d'exemple au tableau de résultats."""
        # Cette méthode sera utilisée pour ajouter des données réelles plus tard
        # Pour l'instant, le tableau est vide
        self.results_table.setRowCount(0) 