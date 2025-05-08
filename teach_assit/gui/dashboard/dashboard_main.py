"""
Module principal pour le tableau de bord personnalisé avec des statistiques avancées.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QFrame, QPushButton, QSizePolicy,
                            QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt, QSize, QTimer
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
        
        print("Initialisation du Dashboard avec:")
        print(f"submission_manager: {self.submission_manager}")
        print(f"db_manager: {self.db_manager}")
        
        self.init_ui()
        
        # Configurer un timer pour rafraîchir les données automatiquement toutes les 30 secondes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # 30 secondes
        
        # Forcer le rafraîchissement des données après l'initialisation
        self.refresh_data()
    
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
        print("Rafraîchissement des données du tableau de bord...")
        
        if not self.submission_manager or not self.db_manager:
            print("ERREUR: Les managers ne sont pas correctement initialisés!")
            print(f"submission_manager: {self.submission_manager}")
            print(f"db_manager: {self.db_manager}")
            return
        
        try:
            # Mettre à jour les statistiques
            if hasattr(self.stats_widget, 'update_stats'):
                self.stats_widget.update_stats()
            else:
                print("ERREUR: stats_widget n'a pas de méthode update_stats")
            
            # Mettre à jour les performances
            if hasattr(self.performance_widget, 'update_data'):
                self.performance_widget.update_data()
            else:
                print("ERREUR: performance_widget n'a pas de méthode update_data")
            
            # Mettre à jour les données des étudiants
            if hasattr(self.students_widget, 'update_data'):
                self.students_widget.update_data()
            else:
                print("ERREUR: students_widget n'a pas de méthode update_data")
            
            # Mettre à jour les notes
            if hasattr(self.grades_widget, 'update_data'):
                self.grades_widget.update_data()
            else:
                print("ERREUR: grades_widget n'a pas de méthode update_data")
            
            print("Rafraîchissement des données terminé avec succès.")
        except Exception as e:
            print(f"ERREUR lors du rafraîchissement des données: {str(e)}")
            import traceback
            traceback.print_exc() 