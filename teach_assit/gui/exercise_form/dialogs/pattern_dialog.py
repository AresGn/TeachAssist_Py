from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QCheckBox, QPushButton
)

class PatternDialog(QDialog):
    """Dialogue pour ajouter ou modifier un motif personnalisé."""
    
    def __init__(self, parent=None, pattern=None):
        super().__init__(parent)
        self.pattern = pattern or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        self.setWindowTitle("Motif personnalisé")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.description_edit = QLineEdit()
        if self.pattern.get('description'):
            self.description_edit.setText(self.pattern['description'])
        form.addRow("Description :", self.description_edit)
        
        self.pattern_edit = QTextEdit()
        self.pattern_edit.setPlaceholderText("Motif regex ou syntaxe Java")
        if self.pattern.get('pattern'):
            self.pattern_edit.setText(self.pattern['pattern'])
        form.addRow("Motif :", self.pattern_edit)
        
        self.required_checkbox = QCheckBox("Motif requis")
        self.required_checkbox.setChecked(self.pattern.get('required', False))
        form.addRow("", self.required_checkbox)
        
        self.error_message_edit = QLineEdit()
        if self.pattern.get('errorMessage'):
            self.error_message_edit.setText(self.pattern['errorMessage'])
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
    
    def get_pattern(self):
        """Récupérer les données du motif."""
        description = self.description_edit.text()
        pattern = self.pattern_edit.toPlainText()
        required = self.required_checkbox.isChecked()
        error_message = self.error_message_edit.text()
        
        if not description or not pattern:
            return None
        
        result = {
            'description': description,
            'pattern': pattern,
            'required': required
        }
        
        if error_message:
            result['errorMessage'] = error_message
        
        return result 