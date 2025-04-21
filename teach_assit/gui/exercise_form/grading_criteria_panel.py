from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from teach_assit.gui.exercise_form.base_panel import BasePanel
from teach_assit.gui.exercise_form.dialogs.criteria_dialog import CriteriaDialog

class GradingCriteriaPanel(BasePanel):
    """Panneau pour les critères de notation."""
    
    def __init__(self, parent=None):
        super().__init__("Critères de notation", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        self.criteria_list = QListWidget()
        layout.addWidget(self.criteria_list)
        
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_criteria)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_criteria)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_criteria)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Double-clic pour éditer
        self.criteria_list.itemDoubleClicked.connect(self.edit_criteria)
    
    def load_data(self, config):
        """Charger les critères de notation."""
        if not config:
            return
            
        self.criteria_list.clear()
        for criteria in config.grading_criteria:
            item = QListWidgetItem(f"{criteria['title']} ({criteria['points']} points)")
            item.setData(Qt.UserRole, criteria)
            self.criteria_list.addItem(item)
    
    def save_data(self, config):
        """Sauvegarder les critères de notation dans la configuration."""
        if not config:
            return False
            
        criteria_list = []
        for i in range(self.criteria_list.count()):
            criteria = self.criteria_list.item(i).data(Qt.UserRole)
            criteria_list.append(criteria)
        
        config.grading_criteria = criteria_list
        return True
    
    def add_criteria(self):
        """Ajouter un critère de notation."""
        dialog = CriteriaDialog(self)
        if dialog.exec_():
            criteria = dialog.get_criteria()
            if criteria:
                item = QListWidgetItem(f"{criteria['title']} ({criteria['points']} points)")
                item.setData(Qt.UserRole, criteria)
                self.criteria_list.addItem(item)
    
    def edit_criteria(self, item=None):
        """Éditer un critère de notation."""
        if not item:
            item = self.criteria_list.currentItem()
        
        if not item:
            return
            
        criteria = item.data(Qt.UserRole)
        dialog = CriteriaDialog(self, criteria)
        
        if dialog.exec_():
            updated_criteria = dialog.get_criteria()
            if updated_criteria:
                item.setText(f"{updated_criteria['title']} ({updated_criteria['points']} points)")
                item.setData(Qt.UserRole, updated_criteria)
    
    def delete_criteria(self):
        """Supprimer un critère de notation."""
        current_item = self.criteria_list.currentItem()
        if not current_item:
            return
            
        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            'Êtes-vous sûr de vouloir supprimer ce critère de notation ?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.criteria_list.row(current_item)
            self.criteria_list.takeItem(row) 