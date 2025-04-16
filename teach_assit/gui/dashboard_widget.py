"""
Module pour l'affichage du tableau de bord principal.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QFrame, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont


class DashboardWidget(QWidget):
    """Widget pour afficher le tableau de bord principal de l'application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur du tableau de bord."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête du tableau de bord
        header = QLabel("Tableau de bord")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        """)
        main_layout.addWidget(header)
        
        # Widgets de statistiques
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        # Fonction pour créer un widget de statistique
        def create_stat_widget(title, value, icon_name, color):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 10px;
                    padding: 15px;
                }}
            """)
            
            layout = QHBoxLayout(frame)
            
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(f"icons/{icon_name}.svg").pixmap(QSize(48, 48)))
            layout.addWidget(icon_label)
            
            info = QVBoxLayout()
            title_label = QLabel(title)
            title_label.setStyleSheet("color: white; font-size: 14px;")
            info.addWidget(title_label)
            
            value_label = QLabel(value)
            value_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
            info.addWidget(value_label)
            
            layout.addLayout(info)
            layout.setStretch(0, 1)
            layout.setStretch(1, 4)
            
            return frame
        
        # Ajouter les widgets de statistiques
        stats_layout.addWidget(create_stat_widget("Soumissions", "0", "file-text", "#3498db"), 0, 0)
        stats_layout.addWidget(create_stat_widget("Étudiants", "0", "users", "#2ecc71"), 0, 1)
        stats_layout.addWidget(create_stat_widget("Exercices", "0", "code", "#e74c3c"), 1, 0)
        stats_layout.addWidget(create_stat_widget("Évaluations", "0", "clipboard", "#9b59b6"), 1, 1)
        
        main_layout.addLayout(stats_layout)
        
        # Actions rapides
        actions_label = QLabel("Actions rapides")
        actions_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-top: 15px;
        """)
        main_layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        
        def create_action_button(text, icon_name):
            button = QPushButton(text)
            button.setIcon(QIcon(f"icons/{icon_name}.svg"))
            button.setIconSize(QSize(24, 24))
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            button.setMinimumHeight(60)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dfe6e9;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
            """)
            return button
        
        actions_layout.addWidget(create_action_button("Extraire des soumissions", "download"))
        actions_layout.addWidget(create_action_button("Analyser des exercices", "activity"))
        actions_layout.addWidget(create_action_button("Gérer les configurations", "settings"))
        actions_layout.addWidget(create_action_button("Voir les résultats", "bar-chart-2"))
        
        main_layout.addLayout(actions_layout)
        
        # Activité récente
        recent_label = QLabel("Activité récente")
        recent_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-top: 15px;
        """)
        main_layout.addWidget(recent_label)
        
        recent_frame = QFrame()
        recent_frame.setFrameShape(QFrame.StyledPanel)
        recent_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dfe6e9;
                padding: 15px;
            }
        """)
        
        recent_layout = QVBoxLayout(recent_frame)
        
        # Message placé au centre quand il n'y a pas d'activité récente
        no_activity = QLabel("Aucune activité récente")
        no_activity.setAlignment(Qt.AlignCenter)
        no_activity.setStyleSheet("color: #7f8c8d; font-size: 16px; padding: 20px;")
        recent_layout.addWidget(no_activity)
        
        main_layout.addWidget(recent_frame)
        
        # Stretch pour prendre l'espace restant
        main_layout.addStretch() 