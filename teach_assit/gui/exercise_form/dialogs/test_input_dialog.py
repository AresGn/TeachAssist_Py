from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QPushButton
)

class TestInputDialog(QDialog):
    """Dialogue pour ajouter ou modifier une entrée de test."""
    
    def __init__(self, parent=None, test_input=None):
        super().__init__(parent)
        self.test_input = test_input or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        self.setWindowTitle("Entrée de test")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Valeur(s) de test
        self.value_edit = QTextEdit()
        if self.test_input.get('value'):
            self.value_edit.setText(str(self.test_input['value']))
        self.value_edit.setPlaceholderText("Entrez une valeur ou plusieurs valeurs séparées par des virgules")
        self.value_edit.setMinimumHeight(80)
        form_layout.addRow("Valeur(s) :", self.value_edit)
        
        # Description
        self.description_edit = QLineEdit()
        if self.test_input.get('description'):
            self.description_edit.setText(self.test_input['description'])
        self.description_edit.setPlaceholderText("Ex: Test avec valeurs positives, Test avec balance nulle...")
        form_layout.addRow("Description :", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        buttons.addWidget(ok_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
    
    def get_test_input(self):
        """Récupérer les données de l'entrée de test."""
        value = self.value_edit.toPlainText().strip()
        description = self.description_edit.text().strip()
        
        if not value:
            return None
        
        return {
            'value': value,
            'description': description
        } 