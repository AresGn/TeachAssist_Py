"""
Module pour l'affichage et l'analyse des résultats des étudiants.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QComboBox, 
                            QPushButton, QLineEdit, QFrame, QHeaderView,
                            QTextEdit)
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
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur de l'onglet résultats."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête des résultats
        header = QLabel("Résultats des évaluations")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        """)
        main_layout.addWidget(header)
        
        # Filtre et actions
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
                padding: 10px;
            }
        """)
        
        filter_layout = QHBoxLayout(filter_frame)
        
        # Recherche
        search_input = QLineEdit()
        search_input.setPlaceholderText("Rechercher...")
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dfe6e9;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
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
                min-width: 180px;
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
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        filter_layout.addWidget(export_button)
        
        main_layout.addWidget(filter_frame)
        
        # Tableau des résultats
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Étudiant", "Fichier", "Exercice", "Statut", "Résultat Global", "Détails"
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
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-right: 1px solid #dfe6e9;
                border-bottom: 1px solid #dfe6e9;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }
        """)
        
        # Ajuster les en-têtes du tableau
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        # Hauteur des lignes
        self.results_table.verticalHeader().setDefaultSectionSize(60)
        
        main_layout.addWidget(self.results_table)
        
        # Statistiques de résumé
        stats_layout = QHBoxLayout()
        
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
        
        self.stats_boxes = {
            'total': create_stat_box("Nombre de fichiers", "0"),
            'success': create_stat_box("Fichiers valides", "0"),
            'syntax_errors': create_stat_box("Erreurs de syntaxe", "0"),
            'missing_methods': create_stat_box("Méthodes manquantes", "0")
        }
        
        stats_layout.addWidget(self.stats_boxes['total'])
        stats_layout.addWidget(self.stats_boxes['success'])
        stats_layout.addWidget(self.stats_boxes['syntax_errors'])
        stats_layout.addWidget(self.stats_boxes['missing_methods'])
        
        main_layout.addLayout(stats_layout)
    
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
        
        # Analyser tous les résultats pour trouver le nombre total de lignes
        total_rows = 0
        for student, student_results in analysis_results.items():
            total_rows += len(student_results)
        
        # Configurer le nombre de lignes
        self.results_table.setRowCount(total_rows)
        
        # Remplir le tableau
        row = 0
        for student, student_results in analysis_results.items():
            for file_path, result in student_results.items():
                # Nom de l'étudiant
                student_item = QTableWidgetItem(student)
                student_item.setTextAlignment(Qt.AlignCenter)
                font = student_item.font()
                font.setBold(True)
                student_item.setFont(font)
                self.results_table.setItem(row, 0, student_item)
                
                # Nom du fichier
                file_name = os.path.basename(file_path)
                file_item = QTableWidgetItem(file_name)
                file_item.setTextAlignment(Qt.AlignCenter)
                self.results_table.setItem(row, 1, file_item)
                
                # Exercice associé
                exercise_id = "Non spécifié"
                for ex_id in exercise_configs.keys():
                    if ex_id.lower() in file_path.lower() or ex_id.split('-')[-1].lower() in file_path.lower():
                        exercise_id = ex_id
                        break
                
                exercise_name = exercise_configs.get(exercise_id, ExerciseConfig({"name": "Inconnu"})).name
                exercise_item = QTableWidgetItem(f"{exercise_id} - {exercise_name}")
                exercise_item.setTextAlignment(Qt.AlignCenter)
                self.results_table.setItem(row, 2, exercise_item)
                
                # Statut détaillé avec icônes
                syntax_ok = not result.get('syntax_errors', []) and 'error' not in result
                methods_ok = not result.get('missing_methods', [])
                patterns_ok = not (result.get('analysis_details', {}).get('missing_patterns', []))
                
                # Statut
                status_text = ""
                
                # Statut de syntaxe
                if syntax_ok:
                    status_text += f"{SYMBOL_OK} Syntaxe\n"
                else:
                    status_text += f"{SYMBOL_FAIL} Syntaxe\n"
                
                # Statut des méthodes
                if methods_ok:
                    status_text += f"{SYMBOL_OK} Méthodes\n"
                else: 
                    status_text += f"{SYMBOL_WARNING} Méthodes\n"
                
                # Statut des patterns
                if 'analysis_details' in result and 'missing_patterns' in result['analysis_details']:
                    if patterns_ok:
                        status_text += f"{SYMBOL_OK} Patterns"
                    else:
                        status_text += f"{SYMBOL_WARNING} Patterns"
                
                status_item = QTableWidgetItem(status_text)
                status_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.results_table.setItem(row, 3, status_item)
                
                # Résultat global
                global_status = "SUCCÈS" if (syntax_ok and methods_ok and patterns_ok) else "PROBLÈMES"
                global_symbol = SYMBOL_OK if (syntax_ok and methods_ok and patterns_ok) else SYMBOL_FAIL
                global_color = "#2ecc71" if (syntax_ok and methods_ok and patterns_ok) else "#e74c3c"
                
                global_item = QTableWidgetItem(f"{global_symbol} {global_status}")
                global_item.setTextAlignment(Qt.AlignCenter)
                global_item.setForeground(QColor(global_color))
                font = global_item.font()
                font.setBold(True)
                global_item.setFont(font)
                self.results_table.setItem(row, 4, global_item)
                
                # Détails
                details = self.format_detailed_report(result, exercise_configs.get(exercise_id))
                
                details_item = QTableWidgetItem(details)
                details_item.setToolTip(details)
                self.results_table.setItem(row, 5, details_item)
                
                # Mettre à jour les compteurs statistiques
                stats['total'] += 1
                
                if syntax_ok and methods_ok and patterns_ok:
                    stats['success'] += 1
                
                if not syntax_ok:
                    stats['syntax_errors'] += 1
                
                if not methods_ok:
                    stats['missing_methods'] += 1
                
                row += 1
        
        # Mettre à jour les statistiques
        self.update_stats(stats)
        
        # Ajuster les hauteurs de ligne pour le contenu
        for i in range(self.results_table.rowCount()):
            details_item = self.results_table.item(i, 5)
            if details_item and "\n" in details_item.text():
                lines_count = details_item.text().count("\n") + 1
                self.results_table.setRowHeight(i, max(60, lines_count * 20))
    
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
        details += f"\n{methods_symbol} MÉTHODES: "
        
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
        
        # Patterns manquants
        if 'analysis_details' in result and 'missing_patterns' in result['analysis_details']:
            missing_patterns = result['analysis_details']['missing_patterns']
            patterns_ok = not missing_patterns
            patterns_symbol = SYMBOL_OK if patterns_ok else SYMBOL_WARNING
            
            details += f"\n{patterns_symbol} PATTERNS REQUIS:\n"
            
            # Si nous avons un exercice_config, vérifier tous les patterns
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
                    
                    status = SYMBOL_OK if not is_missing else SYMBOL_FAIL
                    pattern_detail = f"  {status} {pattern_desc}"
                    if is_missing and error_msg:
                        pattern_detail += f"\n      {SYMBOL_WARNING} {error_msg}"
                    
                    details += pattern_detail + "\n"
            else:
                # Si pas d'exercice_config, juste lister les patterns manquants
                for pattern in missing_patterns:
                    pattern_desc = fix_encoding(pattern.get('description', 'Pattern inconnu'))
                    error_msg = fix_encoding(pattern.get('errorMessage', ''))
                    details += f"  {SYMBOL_FAIL} {pattern_desc}: {error_msg}\n"
        
        return details
    
    def add_sample_data(self):
        """Ajouter des données d'exemple au tableau de résultats."""
        # Cette méthode sera utilisée pour ajouter des données réelles plus tard
        # Pour l'instant, le tableau est vide
        self.results_table.setRowCount(0) 