from PyQt5.QtWidgets import QFormLayout, QLineEdit, QTextEdit
from teach_assit.gui.exercise_form.base_panel import BasePanel

class BasicInfoPanel(BasePanel):
    """Panneau pour les informations de base d'un exercice."""
    
    def __init__(self, parent=None):
        super().__init__("Informations de base", parent)
        
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QFormLayout()
        
        self.id_edit = QLineEdit()
        self.id_edit.setReadOnly(True)  # L'ID ne peut pas être modifié
        layout.addRow("Identifiant :", self.id_edit)
        
        self.name_edit = QLineEdit()
        layout.addRow("Nom :", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        layout.addRow("Description :", self.description_edit)
        
        self.setLayout(layout)
    
    def load_data(self, config):
        """Charger les données de configuration."""
        if config:
            self.id_edit.setText(config.id)
            self.name_edit.setText(config.name)
            self.description_edit.setText(config.description)
    
    def save_data(self, config):
        """Sauvegarder les données dans la configuration."""
        if config:
            config.name = self.name_edit.text()
            config.description = self.description_edit.toPlainText()
            return True
        return False 