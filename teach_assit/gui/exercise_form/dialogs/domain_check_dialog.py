from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QComboBox, QPushButton
)

class DomainCheckDialog(QDialog):
    """Dialogue pour ajouter ou modifier une vérification de domaine."""
    
    def __init__(self, parent=None, domain_check=None):
        super().__init__(parent)
        self.domain_check = domain_check or {}
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        self.setWindowTitle("Vérification de domaine")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.variable_edit = QLineEdit()
        if self.domain_check.get('variable'):
            self.variable_edit.setText(self.domain_check['variable'])
        form.addRow("Variable :", self.variable_edit)
        
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["==", "!=", ">", ">=", "<", "<=", "in"])
        if self.domain_check.get('operator'):
            index = self.operator_combo.findText(self.domain_check['operator'])
            if index >= 0:
                self.operator_combo.setCurrentIndex(index)
        form.addRow("Opérateur :", self.operator_combo)
        
        self.value_edit = QLineEdit()
        if self.domain_check.get('value'):
            self.value_edit.setText(str(self.domain_check['value']))
        form.addRow("Valeur :", self.value_edit)
        
        self.error_message_edit = QLineEdit()
        if self.domain_check.get('errorMessage'):
            self.error_message_edit.setText(self.domain_check['errorMessage'])
        form.addRow("Message d'erreur :", self.error_message_edit)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        buttons.addWidget(ok_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
    
    def get_domain_check(self):
        """Récupérer les données de la vérification de domaine."""
        variable = self.variable_edit.text().strip()
        operator = self.operator_combo.currentText()
        value = self.value_edit.text().strip()
        error_message = self.error_message_edit.text().strip()
        
        if not variable or not value:
            return None
        
        result = {
            'variable': variable,
            'operator': operator,
            'value': value
        }
        
        if error_message:
            result['errorMessage'] = error_message
        
        return result 