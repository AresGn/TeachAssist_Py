from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QLineEdit
from teach_assit.gui.exercise_form.base_panel import BasePanel

class OperatorsControlPanel(BasePanel):
    """Panneau pour les opérateurs et structures de contrôle."""
    
    def __init__(self, parent=None):
        super().__init__("Opérateurs et structures de contrôle", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        # Opérateurs autorisés
        form_operators = QFormLayout()
        self.operators_edit = QLineEdit()
        self.operators_edit.setPlaceholderText("Ex: +, -, *, /, ==, <=, >=")
        form_operators.addRow("Opérateurs autorisés (séparés par des virgules) :", self.operators_edit)
        layout.addLayout(form_operators)
        
        # Structures de contrôle requises
        form_control = QFormLayout()
        self.control_edit = QLineEdit()
        self.control_edit.setPlaceholderText("Ex: if, for, while, switch")
        form_control.addRow("Structures de contrôle requises (séparées par des virgules) :", self.control_edit)
        layout.addLayout(form_control)
        
        self.setLayout(layout)
    
    def load_data(self, config):
        """Charger les données de configuration."""
        if not config:
            return
            
        # Opérateurs autorisés
        operators = config.rules.get('allowedOperators', [])
        self.operators_edit.setText(", ".join(operators))
        
        # Structures de contrôle requises
        control_structures = config.rules.get('requiredControlStructures', [])
        self.control_edit.setText(", ".join(control_structures))
    
    def save_data(self, config):
        """Sauvegarder les données dans la configuration."""
        if not config:
            return False
            
        if 'rules' not in config.__dict__:
            config.rules = {}
        
        # Opérateurs autorisés
        operators_text = self.operators_edit.text().strip()
        if operators_text:
            config.rules['allowedOperators'] = [op.strip() for op in operators_text.split(',') if op.strip()]
        else:
            config.rules['allowedOperators'] = []
        
        # Structures de contrôle requises
        control_text = self.control_edit.text().strip()
        if control_text:
            config.rules['requiredControlStructures'] = [ctrl.strip() for ctrl in control_text.split(',') if ctrl.strip()]
        else:
            config.rules['requiredControlStructures'] = []
        
        return True 