from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from teach_assit.gui.exercise_form.base_panel import BasePanel
from teach_assit.gui.exercise_form.dialogs.math_function_dialog import MathFunctionDialog

class MathFunctionsPanel(BasePanel):
    """Panneau pour les fonctions mathématiques."""
    
    def __init__(self, parent=None):
        super().__init__("Fonctions mathématiques", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        self.math_functions_list = QListWidget()
        layout.addWidget(self.math_functions_list)
        
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_math_function)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_math_function)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_math_function)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Double-clic pour éditer
        self.math_functions_list.itemDoubleClicked.connect(self.edit_math_function)
    
    def load_data(self, config):
        """Charger les fonctions mathématiques."""
        if not config:
            return
            
        self.math_functions_list.clear()
        
        math_functions = []
        if hasattr(config, 'get_math_functions'):
            math_functions = config.get_math_functions()
        
        for func in math_functions:
            try:
                # Gérer le cas où la fonction n'a pas de paramètres explicites
                if isinstance(func, dict):
                    params = func.get('params', [])
                    if not params and 'domainCondition' in func:
                        # Si pas de paramètres mais une condition de domaine, on suppose un paramètre
                        params = ['x']
                    
                    name = func.get('name', '')
                    display_name = f"{name}({', '.join(params)})"
                else:
                    # Si ce n'est pas un dictionnaire, traiter comme une chaîne
                    display_name = str(func)
                    func = {'name': display_name, 'params': []}
                
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, func)
                self.math_functions_list.addItem(item)
            except Exception as e:
                # Ajouter un élément de secours pour éviter un crash
                display_name = f"Erreur: {str(func)[:20]}"
                func_dict = {'name': display_name, 'params': []}
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, func_dict)
                self.math_functions_list.addItem(item)
    
    def save_data(self, config):
        """Sauvegarder les fonctions mathématiques dans la configuration."""
        if not config:
            return False
            
        math_functions = []
        for i in range(self.math_functions_list.count()):
            func = self.math_functions_list.item(i).data(Qt.UserRole)
            math_functions.append(func)
        
        if hasattr(config, 'set_math_functions'):
            config.set_math_functions(math_functions)
        return True
    
    def add_math_function(self):
        """Ajouter une fonction mathématique."""
        dialog = MathFunctionDialog(self)
        if dialog.exec_():
            func = dialog.get_math_function()
            if func:
                display_name = f"{func['name']}({', '.join(func['params'])})"
                
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, func)
                self.math_functions_list.addItem(item)
    
    def edit_math_function(self, item=None):
        """Éditer une fonction mathématique."""
        if not item:
            item = self.math_functions_list.currentItem()
        
        if not item:
            return
            
        func = item.data(Qt.UserRole)
        dialog = MathFunctionDialog(self, func)
        
        if dialog.exec_():
            updated_func = dialog.get_math_function()
            if updated_func:
                display_name = f"{updated_func['name']}({', '.join(updated_func['params'])})"
                
                item.setText(display_name)
                item.setData(Qt.UserRole, updated_func)
    
    def delete_math_function(self):
        """Supprimer une fonction mathématique."""
        current_item = self.math_functions_list.currentItem()
        if not current_item:
            return
            
        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            'Êtes-vous sûr de vouloir supprimer cette fonction mathématique ?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.math_functions_list.row(current_item)
            self.math_functions_list.takeItem(row) 