from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from teach_assit.gui.exercise_form.base_panel import BasePanel
from teach_assit.gui.exercise_form.dialogs.pattern_dialog import PatternDialog

class PatternsPanel(BasePanel):
    """Panneau pour les motifs personnalisés."""
    
    def __init__(self, parent=None):
        super().__init__("Motifs personnalisés", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        self.patterns_list = QListWidget()
        layout.addWidget(self.patterns_list)
        
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_pattern)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_pattern)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_pattern)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Double-clic pour éditer
        self.patterns_list.itemDoubleClicked.connect(self.edit_pattern)
    
    def load_data(self, config):
        """Charger les motifs personnalisés."""
        if not config:
            return
            
        self.patterns_list.clear()
        for pattern in config.rules.get('customPatterns', []):
            description = pattern.get('description', 'Sans description')
            required = pattern.get('required', False)
            display_name = f"{description} ({'Requis' if required else 'Optionnel'})"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, pattern)
            self.patterns_list.addItem(item)
    
    def save_data(self, config):
        """Sauvegarder les motifs dans la configuration."""
        if not config:
            return False
            
        patterns = []
        for i in range(self.patterns_list.count()):
            pattern = self.patterns_list.item(i).data(Qt.UserRole)
            patterns.append(pattern)
        
        if 'rules' not in config.__dict__:
            config.rules = {}
        
        config.rules['customPatterns'] = patterns
        return True
    
    def add_pattern(self):
        """Ajouter un motif."""
        dialog = PatternDialog(self)
        if dialog.exec_():
            pattern = dialog.get_pattern()
            if pattern:
                description = pattern.get('description', 'Sans description')
                required = pattern.get('required', False)
                display_name = f"{description} ({'Requis' if required else 'Optionnel'})"
                
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, pattern)
                self.patterns_list.addItem(item)
    
    def edit_pattern(self, item=None):
        """Éditer un motif."""
        if not item:
            item = self.patterns_list.currentItem()
        
        if not item:
            return
            
        pattern = item.data(Qt.UserRole)
        dialog = PatternDialog(self, pattern)
        
        if dialog.exec_():
            updated_pattern = dialog.get_pattern()
            if updated_pattern:
                description = updated_pattern.get('description', 'Sans description')
                required = updated_pattern.get('required', False)
                display_name = f"{description} ({'Requis' if required else 'Optionnel'})"
                
                item.setText(display_name)
                item.setData(Qt.UserRole, updated_pattern)
    
    def delete_pattern(self):
        """Supprimer un motif."""
        current_item = self.patterns_list.currentItem()
        if not current_item:
            return
            
        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            'Êtes-vous sûr de vouloir supprimer ce motif ?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.patterns_list.row(current_item)
            self.patterns_list.takeItem(row) 