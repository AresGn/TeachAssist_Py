from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QListWidget, QListWidgetItem, QPushButton, QInputDialog
)

class MethodDialog(QDialog):
    """Dialogue pour ajouter ou modifier une méthode requise."""
    
    def __init__(self, parent=None, method=None):
        super().__init__(parent)
        self.method = method or {}
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        self.setWindowTitle("Méthode requise")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        if self.method.get('name'):
            self.name_edit.setText(self.method['name'])
        form.addRow("Nom :", self.name_edit)
        
        self.return_type_edit = QLineEdit()
        self.return_type_edit.setText(self.method.get('returnType', 'void'))
        form.addRow("Type de retour :", self.return_type_edit)
        
        self.params_list = QListWidget()
        for param in self.method.get('params', []):
            self.params_list.addItem(QListWidgetItem(param))
        form.addRow("Paramètres :", self.params_list)
        
        params_buttons = QHBoxLayout()
        add_param_button = QPushButton("Ajouter")
        add_param_button.clicked.connect(self.add_parameter)
        params_buttons.addWidget(add_param_button)
        
        delete_param_button = QPushButton("Supprimer")
        delete_param_button.clicked.connect(self.delete_parameter)
        params_buttons.addWidget(delete_param_button)
        
        layout.addLayout(form)
        layout.addLayout(params_buttons)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        buttons.addWidget(ok_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
    
    def add_parameter(self):
        """Ajouter un paramètre à la méthode."""
        param_type, ok = QInputDialog.getText(
            self, "Type de paramètre", 
            "Entrez le type du paramètre (ex: int, String):"
        )
        if ok and param_type:
            item = QListWidgetItem(param_type)
            self.params_list.addItem(item)
    
    def delete_parameter(self):
        """Supprimer le paramètre sélectionné."""
        current_item = self.params_list.currentItem()
        if current_item:
            row = self.params_list.row(current_item)
            self.params_list.takeItem(row)
    
    def get_method(self):
        """Récupérer les données de la méthode."""
        method_name = self.name_edit.text()
        return_type = self.return_type_edit.text()
        
        parameters = []
        for i in range(self.params_list.count()):
            parameters.append(self.params_list.item(i).text())
        
        if not method_name:
            return None
        
        return {
            'name': method_name,
            'returnType': return_type,
            'params': parameters
        } 