"""
Module principal pour le tableau de bord personnalisé avec des statistiques avancées.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QFrame, QPushButton, QSizePolicy,
                            QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from teach_assit.gui.dashboard.stats_widget import StatsWidget
from teach_assit.gui.dashboard.performance_widget import PerformanceWidget
from teach_assit.gui.dashboard.students_widget import StudentsWidget
from teach_assit.gui.dashboard.grades_widget import GradesWidget


class EnhancedDashboard(QWidget):
    """Widget principal pour le tableau de bord amélioré de l'application."""
    
    def __init__(self, submission_manager=None, db_manager=None, parent=None):
        super().__init__(parent)
        self.submission_manager = submission_manager
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur du tableau de bord amélioré."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # En-tête du tableau de bord
        header = QLabel("Tableau de bord")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(header)
        
        # Widgets de statistiques
        self.stats_widget = StatsWidget(self.submission_manager, self.db_manager)
        main_layout.addWidget(self.stats_widget)
        
        # Onglets pour les différentes sections
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dfe6e9;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # Onglet Performances
        self.performance_widget = PerformanceWidget(self.submission_manager, self.db_manager)
        performance_scroll = QScrollArea()
        performance_scroll.setWidget(self.performance_widget)
        performance_scroll.setWidgetResizable(True)
        performance_scroll.setFrameShape(QFrame.NoFrame)
        tabs.addTab(performance_scroll, "Performances des étudiants")
        
        # Onglet Classement des étudiants
        self.students_widget = StudentsWidget(self.submission_manager, self.db_manager)
        students_scroll = QScrollArea()
        students_scroll.setWidget(self.students_widget)
        students_scroll.setWidgetResizable(True)
        students_scroll.setFrameShape(QFrame.NoFrame)
        tabs.addTab(students_scroll, "Classement des étudiants")
        
        # Onglet Relevé de notes
        self.grades_widget = GradesWidget(self.submission_manager, self.db_manager)
        grades_scroll = QScrollArea()
        grades_scroll.setWidget(self.grades_widget)
        grades_scroll.setWidgetResizable(True)
        grades_scroll.setFrameShape(QFrame.NoFrame)
        tabs.addTab(grades_scroll, "Relevé de notes")
        
        main_layout.addWidget(tabs)
    
    def refresh_data(self):
        """Actualiser toutes les données du tableau de bord."""
        self.stats_widget.update_stats()
        self.performance_widget.update_data()
        self.students_widget.update_data()
        self.grades_widget.update_data() 