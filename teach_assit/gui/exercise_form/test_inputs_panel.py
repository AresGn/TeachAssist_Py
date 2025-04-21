from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, 
    QTableWidget, QTableWidgetItem, QHeaderView
)

from teach_assit.gui.exercise_form.base_panel import BasePanel
from teach_assit.gui.exercise_form.dialogs.test_input_dialog import TestInputDialog

class TestInputsPanel(BasePanel):
    """Panneau pour les entrées de test."""
    
    def __init__(self, parent=None):
        super().__init__("Entrées de test", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        # Table pour les entrées de test
        self.test_inputs_table = QTableWidget(0, 2)  # Colonnes: Valeur, Description
        self.test_inputs_table.setHorizontalHeaderLabels(["Valeur", "Description"])
        self.test_inputs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.test_inputs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.test_inputs_table)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_test_input)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_test_input)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_test_input)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_data(self, config):
        """Charger les entrées de test."""
        if not config:
            return
            
        self.test_inputs_table.setRowCount(0)
        for test_input in config.test_inputs:
            row = self.test_inputs_table.rowCount()
            self.test_inputs_table.insertRow(row)
            
            # Valeur
            value_item = QTableWidgetItem(str(test_input.get('value', '')))
            self.test_inputs_table.setItem(row, 0, value_item)
            
            # Description
            descr_item = QTableWidgetItem(str(test_input.get('description', '')))
            self.test_inputs_table.setItem(row, 1, descr_item)
    
    def save_data(self, config):
        """Sauvegarder les entrées de test dans la configuration."""
        if not config:
            return False
            
        test_inputs = []
        for row in range(self.test_inputs_table.rowCount()):
            value = self.test_inputs_table.item(row, 0).text()
            description = self.test_inputs_table.item(row, 1).text()
            test_inputs.append({
                'value': value,
                'description': description
            })
        
        config.test_inputs = test_inputs
        return True
    
    def add_test_input(self):
        """Ajouter une entrée de test."""
        dialog = TestInputDialog(self)
        if dialog.exec_():
            test_input = dialog.get_test_input()
            if test_input:
                row = self.test_inputs_table.rowCount()
                self.test_inputs_table.insertRow(row)
                
                # Valeur
                value_item = QTableWidgetItem(str(test_input.get('value', '')))
                self.test_inputs_table.setItem(row, 0, value_item)
                
                # Description
                descr_item = QTableWidgetItem(str(test_input.get('description', '')))
                self.test_inputs_table.setItem(row, 1, descr_item)
    
    def edit_test_input(self):
        """Éditer une entrée de test."""
        current_row = self.test_inputs_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner une entrée de test à éditer.")
            return
        
        # Récupérer les valeurs actuelles
        current_value = self.test_inputs_table.item(current_row, 0).text()
        current_description = self.test_inputs_table.item(current_row, 1).text()
        
        current_test_input = {
            'value': current_value,
            'description': current_description
        }
        
        dialog = TestInputDialog(self, current_test_input)
        if dialog.exec_():
            updated_test_input = dialog.get_test_input()
            if updated_test_input:
                # Valeur
                value_item = QTableWidgetItem(str(updated_test_input.get('value', '')))
                self.test_inputs_table.setItem(current_row, 0, value_item)
                
                # Description
                descr_item = QTableWidgetItem(str(updated_test_input.get('description', '')))
                self.test_inputs_table.setItem(current_row, 1, descr_item)
    
    def delete_test_input(self):
        """Supprimer une entrée de test."""
        current_row = self.test_inputs_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner une entrée de test à supprimer.")
            return
        
        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            'Êtes-vous sûr de vouloir supprimer cette entrée de test ?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.test_inputs_table.removeRow(current_row) 