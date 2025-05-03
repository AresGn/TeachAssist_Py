"""
Composants d'interface utilisateur réutilisables pour le widget de résultats.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QTableWidgetItem, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QColor
from teach_assit.gui.results_widget.utils import SYMBOL_OK, SYMBOL_FAIL, SYMBOL_WARNING
import re

class StatusWidget(QWidget):
    """Widget pour afficher les statuts de vérification."""
    
    def __init__(self, parent=None, row_style="", statuses=None):
        """
        Initialiser le widget de statut.
        
        Args:
            parent: Widget parent
            row_style: Style CSS pour la ligne
            statuses: Liste des statuts à afficher
        """
        super().__init__(parent)
        self.statuses = statuses or []
        self.setStyleSheet(row_style)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Créer une grille 2x3 pour les statuts
        status_grid = QWidget()
        grid_layout = QHBoxLayout(status_grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(5)
        
        # Colonne gauche
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(3)
        
        # Colonne droite
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(3)
        
        # Ajouter les statuts
        if statuses:
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
        layout.addWidget(status_grid)
    
    def get_status_text(self):
        """Retourne un résumé textuel des statuts"""
        if not self.statuses:
            return "Non évalué"
            
        total = len(self.statuses)
        passed = sum(1 for status in self.statuses if status.get("ok", False))
        
        if passed == total:
            return "Réussi"
        elif passed == 0:
            return "Échoué"
        else:
            return f"Partiel ({passed}/{total})"
    
    def get_detailed_status(self):
        """Retourne un résumé détaillé des statuts au format texte"""
        if not self.statuses:
            return "Pas de résultats d'analyse disponibles"
            
        result = []
        for status in self.statuses:
            icon = SYMBOL_OK if status.get("ok", False) else SYMBOL_WARNING if status.get("warning", False) else SYMBOL_FAIL
            result.append(f"{icon} {status.get('name', 'Vérification')}")
        
        return "\n".join(result)


class ExerciseWidget(QWidget):
    """Widget pour afficher les informations d'un exercice."""
    
    def __init__(self, parent=None, exercise_name="", file_name="", row_style=""):
        """
        Initialiser le widget d'exercice.
        
        Args:
            parent: Widget parent
            exercise_name: Nom de l'exercice
            file_name: Nom du fichier
            row_style: Style CSS pour la ligne
        """
        super().__init__(parent)
        self.exercise_name = exercise_name  # Stocker le nom de l'exercice comme attribut
        self.file_name = file_name  # Stocker le nom du fichier comme attribut
        self.setStyleSheet(row_style)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(3)
        
        # Titre de l'exercice
        title_label = QLabel(exercise_name)
        title_label.setObjectName("exercise_label")  # Définir un nom d'objet pour faciliter la recherche
        title_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Nom du fichier
        file_label = QLabel(file_name)
        file_label.setObjectName("file_label")  # Définir un nom d'objet pour faciliter la recherche
        file_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(file_label)
    
    def get_exercise_name(self):
        """Récupérer le nom de l'exercice."""
        return self.exercise_name
    
    def get_file_name(self):
        """Récupérer le nom du fichier."""
        return self.file_name


class ResultWidget(QWidget):
    """Widget pour afficher le résultat d'une analyse."""
    
    def __init__(self, parent=None, exercise_name="", passed_checks=0, total_checks=0, 
                 max_points=10, estimated_score=0, row_style="", all_ok=False):
        """
        Initialiser le widget de résultat.
        
        Args:
            parent: Widget parent
            exercise_name: Nom de l'exercice
            passed_checks: Nombre de vérifications réussies
            total_checks: Nombre total de vérifications
            max_points: Points maximum
            estimated_score: Score estimé
            row_style: Style CSS pour la ligne
            all_ok: Si tous les critères sont satisfaits
        """
        super().__init__(parent)
        self.setStyleSheet(row_style)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)
        
        # Titre de l'exercice
        exercise_name_label = QLabel(exercise_name)
        exercise_name_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        layout.addWidget(exercise_name_label)
        
        # Texte du résultat global
        result_color = "#2ecc71" if all_ok else "#e74c3c"
        result_text = QLabel(f"{passed_checks}/{total_checks} vérifications - {estimated_score}/{max_points} pt")
        result_text.setStyleSheet(f"font-weight: bold; color: {result_color}; font-size: 13px;")
        layout.addWidget(result_text)


class ActionsWidget(QWidget):
    """Widget pour afficher des boutons d'action."""
    
    def __init__(self, parent=None, exercise_name="", on_details_click=None, row_style=""):
        """
        Initialiser le widget d'actions.
        
        Args:
            parent: Widget parent
            exercise_name: Nom de l'exercice
            on_details_click: Fonction à appeler lors du clic sur Détails
            row_style: Style CSS pour la ligne
        """
        super().__init__(parent)
        self.setStyleSheet(row_style)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label pour l'exercice
        exercise_label = QLabel(exercise_name)
        exercise_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50; margin-bottom: 5px;")
        exercise_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(exercise_label)
        
        # Container pour le bouton
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignCenter)
        
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
        
        if on_details_click:
            details_button.clicked.connect(on_details_click)
        
        button_layout.addWidget(details_button)
        layout.addWidget(button_container)


class ExecutionResultWidget(QWidget):
    """Widget pour afficher le résultat d'une exécution."""
    
    def __init__(self, parent=None, success=False, compilation_error=False, output_text=""):
        """
        Initialiser le widget de résultat d'exécution.
        
        Args:
            parent: Widget parent
            success: Si l'exécution est réussie
            compilation_error: Si une erreur de compilation est survenue
            output_text: Texte de sortie
        """
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Conteneur pour le statut
        status_container = QFrame()
        status_container.setFrameShape(QFrame.NoFrame)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(5)
        
        # Déterminer le statut et l'icône
        if compilation_error:
            status_icon = SYMBOL_FAIL
            status_text = "Erreur de compilation"
            status_color = "#e74c3c"
            status_bg = "#fdeded"
        elif success:
            status_icon = SYMBOL_OK
            status_text = "Succès"
            status_color = "#2ecc71"
            status_bg = "#edfdf5"
        else:
            status_icon = SYMBOL_FAIL
            status_text = "Échec"
            status_color = "#e74c3c"
            status_bg = "#fdeded"
        
        # Ajouter l'icône et le statut avec fond de couleur
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {status_bg};
                border-radius: 4px;
                padding: 2px;
            }}
        """)
        status_frame_layout = QHBoxLayout(status_frame)
        status_frame_layout.setContentsMargins(8, 4, 8, 4)
        
        status_label = QLabel(f"{status_icon} {status_text}")
        status_label.setStyleSheet(f"font-weight: bold; color: {status_color}; font-size: 14px;")
        status_frame_layout.addWidget(status_label)
        
        status_layout.addWidget(status_frame)
        status_layout.addStretch()
        
        layout.addWidget(status_container)
        
        # Afficher la sortie (avec formatage amélioré)
        output_frame = QFrame()
        output_frame.setFrameShape(QFrame.StyledPanel)
        output_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #e9ecef;
            }}
        """)
        
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(10, 10, 10, 10)
        output_layout.setSpacing(0)
        
        # Préparer le texte de sortie (limité à quelques lignes)
        displayed_text = self._format_output_text(output_text)
        
        # Sortie texte en utilisant QTextEdit pour permettre le formatage
        output_display = QTextEdit()
        output_display.setReadOnly(True)
        output_display.setHtml(displayed_text)
        output_display.setMaximumHeight(80)  # Augmenter légèrement la hauteur pour plus de visibilité
        output_display.setFrameShape(QFrame.NoFrame)  # Supprimer la bordure
        
        # Police et style
        font = QFont("Courier New", 12)
        output_display.setFont(font)
        output_display.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #2c3e50;
                padding: 0;
                border: none;
            }
        """)
        
        output_layout.addWidget(output_display)
        layout.addWidget(output_frame)
    
    def _format_output_text(self, text):
        """Formater le texte de sortie pour l'affichage."""
        if not text:
            return "<em style='color: #7f8c8d;'>Aucune sortie</em>"
        
        # Échapper les caractères HTML
        escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Obtenir les premières lignes (limiter à 4)
        lines = escaped_text.split("\n")
        displayed_lines = lines[:4]
        
        # Coloriser les nombres et les accents dans les lignes affichées
        formatted_lines = []
        for line in displayed_lines:
            # Mettre en évidence les nombres
            formatted_line = re.sub(r'(\d+)', r'<span style="color: #3498db; font-weight: bold;">\1</span>', line)
            formatted_lines.append(formatted_line)
        
        # Ajouter une indication s'il y a plus de lignes
        if len(lines) > 4:
            formatted_lines.append(f"<em style='color: #7f8c8d;'>(+ {len(lines) - 4} lignes supplémentaires...)</em>")
        
        # Jointure avec des balises de saut de ligne HTML
        formatted_text = "<br>".join(formatted_lines)
        
        # Préserver les espaces multiples
        formatted_text = formatted_text.replace("  ", "&nbsp;&nbsp;")
        
        return formatted_text 