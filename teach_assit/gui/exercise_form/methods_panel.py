from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from teach_assit.gui.exercise_form.base_panel import BasePanel
from teach_assit.gui.exercise_form.dialogs.method_dialog import MethodDialog

class MethodsPanel(BasePanel):
    """Panneau pour les méthodes requises d'un exercice."""
    
    def __init__(self, parent=None):
        super().__init__("Méthodes requises", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        self.methods_list = QListWidget()
        layout.addWidget(self.methods_list)
        
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_method)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_method)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_method)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Double-clic pour éditer
        self.methods_list.itemDoubleClicked.connect(self.edit_method)
    
    def load_data(self, config):
        """Charger les méthodes requises."""
        if not config:
            return
            
        self.methods_list.clear()
        for method in config.rules.get('requiredMethods', []):
            params = ", ".join(method.get('params', []))
            display_name = f"{method['name']}({params}) -> {method['returnType']}"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, method)
            self.methods_list.addItem(item)
    
    def save_data(self, config):
        """Sauvegarder les méthodes dans la configuration."""
        if not config:
            return False
            
        methods = []
        for i in range(self.methods_list.count()):
            method = self.methods_list.item(i).data(Qt.UserRole)
            methods.append(method)
        
        if 'rules' not in config.__dict__:
            config.rules = {}
        
        config.rules['requiredMethods'] = methods
        return True
    
    def add_method(self):
        """Ajouter une méthode."""
        dialog = MethodDialog(self)
        if dialog.exec_():
            method = dialog.get_method()
            if method:
                params = ", ".join(method.get('params', []))
                display_name = f"{method['name']}({params}) -> {method['returnType']}"
                
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, method)
                self.methods_list.addItem(item)
    
    def edit_method(self, item=None):
        """Éditer une méthode."""
        if not item:
            item = self.methods_list.currentItem()
        
        if not item:
            return
            
        method = item.data(Qt.UserRole)
        dialog = MethodDialog(self, method)
        
        if dialog.exec_():
            updated_method = dialog.get_method()
            if updated_method:
                params = ", ".join(updated_method.get('params', []))
                display_name = f"{updated_method['name']}({params}) -> {updated_method['returnType']}"
                
                item.setText(display_name)
                item.setData(Qt.UserRole, updated_method)
    
    def delete_method(self):
        """Supprimer une méthode."""
        current_item = self.methods_list.currentItem()
        if not current_item:
            return
            
        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            'Êtes-vous sûr de vouloir supprimer cette méthode ?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.methods_list.row(current_item)
            self.methods_list.takeItem(row) 