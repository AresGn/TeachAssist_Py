"""
Boîtes de dialogue pour le widget de résultats.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QTabWidget, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
import re


class DetailsDialog(QDialog):
    """Boîte de dialogue pour afficher les détails d'un exercice."""
    
    def __init__(self, parent=None, exercise_details=None):
        """
        Initialiser la boîte de dialogue de détails.
        
        Args:
            parent: Widget parent
            exercise_details: Dictionnaire avec les détails de l'exercice
        """
        super().__init__(parent)
        self.setWindowTitle("Détails de l'exercice")
        self.resize(700, 500)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tableau avec onglets pour les différentes sections
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #d0d0d0;
                padding: 5px 10px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
        """)
        
        if exercise_details:
            # Onglet pour les informations générales
            general_tab = QWidget()
            general_layout = QVBoxLayout(general_tab)
            
            # Nom et fichier
            general_text = QTextBrowser()
            general_text.setHtml(f"""
                <h2>{exercise_details.get('exercise_name', 'Nom de l\'exercice')}</h2>
                <p><b>Fichier:</b> {exercise_details.get('file_name', 'Nom du fichier')}</p>
                <p><b>Score estimé:</b> {exercise_details.get('estimated_score', 0)}/{exercise_details.get('max_points', 10)}</p>
                <p><b>Vérifications passées:</b> {exercise_details.get('passed_checks', 0)}/{exercise_details.get('total_checks', 0)}</p>
            """)
            general_layout.addWidget(general_text)
            tab_widget.addTab(general_tab, "Général")
            
            # Onglet pour les vérifications
            if "checks" in exercise_details:
                checks_tab = QWidget()
                checks_layout = QVBoxLayout(checks_tab)
                
                checks_text = QTextBrowser()
                checks_html = "<h3>Résultats des vérifications</h3>"
                for check in exercise_details["checks"]:
                    check_icon = "✅" if check["success"] else "⚠️" if check.get("warning", False) else "❌"
                    check_color = "#2ecc71" if check["success"] else "#f39c12" if check.get("warning", False) else "#e74c3c"
                    
                    checks_html += f"""
                        <div style="margin-bottom: 10px; padding: 10px; border-radius: 5px; background-color: #f8f9fa;">
                            <div style="display: flex; color: {check_color};">
                                <span style="font-weight: bold; margin-right: 5px;">{check_icon} {check["check_name"]}</span>
                            </div>
                            <div style="margin-top: 5px;">
                                <p>{check.get("message", "")}</p>
                            </div>
                        </div>
                    """
                
                checks_text.setHtml(checks_html)
                checks_layout.addWidget(checks_text)
                tab_widget.addTab(checks_tab, "Vérifications")
            
            # Onglet pour le rapport détaillé
            if "report" in exercise_details:
                report_tab = QWidget()
                report_layout = QVBoxLayout(report_tab)
                
                report_text = QTextBrowser()
                report_text.setHtml(f"<pre>{exercise_details['report']}</pre>")
                report_layout.addWidget(report_text)
                tab_widget.addTab(report_tab, "Rapport détaillé")
        
        layout.addWidget(tab_widget)
        
        # Bouton de fermeture
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignRight)
        
        close_button = QPushButton("Fermer")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dfe4ea;
                border-radius: 4px;
                padding: 8px 16px;
                color: #3498db;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(close_button)
        layout.addWidget(button_container)


class OutputDialog(QDialog):
    """Boîte de dialogue pour afficher la sortie d'exécution."""
    
    def __init__(self, parent=None, title="", output_text=""):
        """
        Initialiser la boîte de dialogue de sortie.
        
        Args:
            parent: Widget parent
            title: Titre de la boîte de dialogue
            output_text: Texte de sortie
        """
        super().__init__(parent)
        self.setWindowTitle(f"Sortie d'exécution - {title}")
        self.resize(800, 600)  # Agrandi pour une meilleure visibilité
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre de la section de sortie
        title_label = QLabel("Résultat d'exécution")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Zone de texte pour afficher la sortie
        output_text_browser = QTextBrowser()
        output_text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.5;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        # Formater le texte de sortie
        formatted_output = self.format_output_text(output_text)
        output_text_browser.setHtml(formatted_output)
        
        # Définir une police à espacement fixe
        font = QFont("Courier New", 13)
        output_text_browser.setFont(font)
        
        layout.addWidget(output_text_browser)
        
        # Boutons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignRight)
        
        # Bouton pour copier le texte
        copy_button = QPushButton("Copier")
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dfe4ea;
                border-radius: 4px;
                padding: 8px 16px;
                color: #3498db;
                font-weight: bold;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(output_text))
        
        # Bouton de fermeture
        close_button = QPushButton("Fermer")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dfe4ea;
                border-radius: 4px;
                padding: 8px 16px;
                color: #3498db;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(copy_button)
        button_layout.addWidget(close_button)
        layout.addWidget(button_container)
    
    def copy_to_clipboard(self, text):
        """Copier le texte dans le presse-papier."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
    
    def format_output_text(self, text):
        """
        Formater le texte de sortie pour l'affichage.
        
        Args:
            text: Texte brut à formater
            
        Returns:
            Texte formaté en HTML
        """
        if not text:
            return "<div style='text-align: center; padding: 20px; color: #7f8c8d;'><em>Aucune sortie disponible</em></div>"
        
        # Échapper les caractères HTML
        formatted_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Remplacer les espaces consécutifs par des espaces insécables HTML
        formatted_text = formatted_text.replace("  ", "&nbsp;&nbsp;")
        
        # Remplacer les retours à la ligne par des balises <br>
        formatted_text = formatted_text.replace("\n", "<br>")
        
        # Mettre en évidence les en-têtes standards avec style amélioré
        formatted_text = formatted_text.replace("=== SORTIE STANDARD ===", 
            "<div style='background-color: #e8f4fd; color: #2980b9; padding: 10px; margin: 10px 0; font-weight: bold; border-left: 4px solid #3498db; border-radius: 3px;'>SORTIE STANDARD</div>")
        
        formatted_text = formatted_text.replace("=== ERREURS ===", 
            "<div style='background-color: #fdeded; color: #c0392b; padding: 10px; margin: 10px 0; font-weight: bold; border-left: 4px solid #e74c3c; border-radius: 3px;'>ERREURS</div>")
        
        # Mettre en évidence les en-têtes alternatifs
        formatted_text = formatted_text.replace("STANDARD OUTPUT:", 
            "<div style='background-color: #e8f4fd; color: #2980b9; padding: 10px; margin: 10px 0; font-weight: bold; border-left: 4px solid #3498db; border-radius: 3px;'>SORTIE STANDARD</div>")
        
        formatted_text = formatted_text.replace("ERRORS:", 
            "<div style='background-color: #fdeded; color: #c0392b; padding: 10px; margin: 10px 0; font-weight: bold; border-left: 4px solid #e74c3c; border-radius: 3px;'>ERREURS</div>")

        # Mettre en évidence les nombres
        formatted_text = re.sub(r'(\d+)', r'<span style="color: #3498db; font-weight: bold;">\1</span>', formatted_text)
        
        # Mettre en évidence les messages d'erreur courants
        error_patterns = [
            "SyntaxError", "TypeError", "ValueError", "NameError", "IndexError", 
            "KeyError", "AttributeError", "ImportError", "RuntimeError", "Exception"
        ]
        
        for pattern in error_patterns:
            formatted_text = formatted_text.replace(pattern, 
                f'<span style="color: #e74c3c; font-weight: bold;">{pattern}</span>')
        
        # Encapsuler dans un div avec style
        formatted_text = f"""
        <div style='font-family: "Courier New", monospace; line-height: 1.5;'>
            {formatted_text}
        </div>
        """
        
        return formatted_text