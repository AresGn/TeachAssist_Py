from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QCheckBox, QLineEdit
from teach_assit.gui.exercise_form.base_panel import BasePanel

class ExceptionsPanel(BasePanel):
    """Panneau pour la gestion des exceptions."""
    
    def __init__(self, parent=None):
        super().__init__("Gestion des exceptions", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.try_catch_checkbox = QCheckBox("Bloc try/catch requis")
        form.addRow("", self.try_catch_checkbox)
        
        self.specific_exceptions_edit = QLineEdit()
        self.specific_exceptions_edit.setPlaceholderText("Ex: IllegalArgumentException, ArithmeticException")
        form.addRow("Exceptions spécifiques :", self.specific_exceptions_edit)
        
        layout.addLayout(form)
        self.setLayout(layout)
    
    def load_data(self, config):
        """Charger les données de configuration."""
        if not config:
            return
            
        exception_handling = config.rules.get('exceptionHandling', {})
        self.try_catch_checkbox.setChecked(exception_handling.get('requiredTryCatch', False))
        
        specific_exceptions = exception_handling.get('specificExceptions', [])
        self.specific_exceptions_edit.setText(", ".join(specific_exceptions))
    
    def save_data(self, config):
        """Sauvegarder les données dans la configuration."""
        if not config:
            return False
            
        if 'rules' not in config.__dict__:
            config.rules = {}
        
        exception_handling = {}
        exception_handling['requiredTryCatch'] = self.try_catch_checkbox.isChecked()
        
        exception_text = self.specific_exceptions_edit.text().strip()
        if exception_text:
            exception_handling['specificExceptions'] = [e.strip() for e in exception_text.split(',') if e.strip()]
        else:
            exception_handling['specificExceptions'] = []
        
        config.rules['exceptionHandling'] = exception_handling
        return True 