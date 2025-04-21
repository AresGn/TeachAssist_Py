from PyQt5.QtWidgets import QGroupBox, QWidget

class BasePanel(QGroupBox):
    """Classe de base pour tous les panneaux du formulaire d'exercice."""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur. À implémenter dans les sous-classes."""
        pass
    
    def load_data(self, data):
        """Charger les données dans le formulaire. À implémenter dans les sous-classes."""
        pass
    
    def save_data(self):
        """Sauvegarder les données du formulaire. À implémenter dans les sous-classes."""
        pass 