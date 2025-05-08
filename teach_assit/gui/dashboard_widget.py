"""
Module pour l'affichage du tableau de bord principal.
Cette version utilise le tableau de bord amélioré du package dashboard.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from teach_assit.gui.dashboard import EnhancedDashboard


class DashboardWidget(QWidget):
    """Widget pour afficher le tableau de bord principal de l'application.
    Cette classe est un wrapper autour du tableau de bord amélioré.
    """
    
    def __init__(self, submission_manager=None, db_manager=None, parent=None):
        super().__init__(parent)
        self.submission_manager = submission_manager
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur du tableau de bord."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Créer une zone de défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Conteneur pour le tableau de bord amélioré
        dashboard_container = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_container)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        
        # Utiliser le tableau de bord amélioré avec les managers
        self.enhanced_dashboard = EnhancedDashboard(
            submission_manager=self.submission_manager,
            db_manager=self.db_manager,
            parent=self
        )
        dashboard_layout.addWidget(self.enhanced_dashboard)
        
        # Ajouter le conteneur du dashboard à la zone de défilement
        scroll_area.setWidget(dashboard_container)
        
        # Ajouter la zone de défilement au layout principal
        main_layout.addWidget(scroll_area)
    
    def update_dashboard(self):
        """Mettre à jour le tableau de bord."""
        if hasattr(self, 'enhanced_dashboard'):
            print("Mise à jour du dashboard depuis DashboardWidget")
            # Mettre à jour les références aux managers si nécessaire
            if self.submission_manager and hasattr(self.enhanced_dashboard, 'submission_manager'):
                self.enhanced_dashboard.submission_manager = self.submission_manager
            
            if self.db_manager and hasattr(self.enhanced_dashboard, 'db_manager'):
                self.enhanced_dashboard.db_manager = self.db_manager
            
            self.enhanced_dashboard.refresh_data() 