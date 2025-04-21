from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QCheckBox, QLineEdit
from teach_assit.gui.exercise_form.base_panel import BasePanel

class OptionsPanel(BasePanel):
    """Panneau pour les options diverses."""
    
    def __init__(self, parent=None):
        super().__init__("Options diverses", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.check_scope = QCheckBox("Vérifier la portée des variables")
        form.addRow("", self.check_scope)
        
        self.naming_edit = QLineEdit()
        self.naming_edit.setPlaceholderText("Ex: camelCase, PascalCase")
        form.addRow("Conventions de nommage :", self.naming_edit)
        
        layout.addLayout(form)
        self.setLayout(layout)
    
    def load_data(self, config):
        """Charger les données de configuration."""
        if not config:
            return
            
        self.check_scope.setChecked(config.rules.get('checkVariableScope', False))
        
        naming_conventions = config.rules.get('checkNamingConventions', [])
        self.naming_edit.setText(", ".join(naming_conventions))
    
    def save_data(self, config):
        """Sauvegarder les données dans la configuration."""
        if not config:
            return False
            
        if 'rules' not in config.__dict__:
            config.rules = {}
        
        config.rules['checkVariableScope'] = self.check_scope.isChecked()
        
        naming_text = self.naming_edit.text().strip()
        if naming_text:
            config.rules['checkNamingConventions'] = [conv.strip() for conv in naming_text.split(',') if conv.strip()]
        else:
            config.rules['checkNamingConventions'] = []
        
        return True 