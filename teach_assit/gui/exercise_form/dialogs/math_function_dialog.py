from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QPushButton
)

class MathFunctionDialog(QDialog):
    """Dialogue pour ajouter ou modifier une fonction mathématique."""
    
    def __init__(self, parent=None, math_function=None):
        super().__init__(parent)
        self.math_function = math_function or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        self.setWindowTitle("Fonction mathématique")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        if self.math_function.get('name'):
            self.name_edit.setText(self.math_function['name'])
        form.addRow("Nom :", self.name_edit)
        
        self.params_edit = QLineEdit()
        params = self.math_function.get('params', [])
        if params:
            self.params_edit.setText(", ".join(params))
        self.params_edit.setPlaceholderText("Ex: x, y, z")
        form.addRow("Paramètres (séparés par des virgules) :", self.params_edit)
        
        self.expression_edit = QTextEdit()
        if self.math_function.get('expression'):
            self.expression_edit.setText(self.math_function['expression'])
        self.expression_edit.setPlaceholderText("Ex: Math.sqrt(x*x + y*y)")
        form.addRow("Expression :", self.expression_edit)
        
        self.error_message_edit = QLineEdit()
        if self.math_function.get('errorMessage'):
            self.error_message_edit.setText(self.math_function['errorMessage'])
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
    
    def get_math_function(self):
        """Récupérer les données de la fonction mathématique."""
        name = self.name_edit.text().strip()
        params_text = self.params_edit.text().strip()
        params = [p.strip() for p in params_text.split(',') if p.strip()]
        expression = self.expression_edit.toPlainText().strip()
        error_message = self.error_message_edit.text().strip()
        
        if not name or not expression:
            return None
        
        result = {
            'name': name,
            'params': params,
            'expression': expression
        }
        
        if error_message:
            result['errorMessage'] = error_message
        
        return result 