from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from teach_assit.gui.exercise_form.base_panel import BasePanel
from teach_assit.gui.exercise_form.dialogs.domain_check_dialog import DomainCheckDialog

class DomainChecksPanel(BasePanel):
    """Panneau pour les vérifications de domaine."""
    
    def __init__(self, parent=None):
        super().__init__("Vérifications de domaine", parent)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        
        self.domain_checks_list = QListWidget()
        layout.addWidget(self.domain_checks_list)
        
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_domain_check)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_domain_check)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_domain_check)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Double-clic pour éditer
        self.domain_checks_list.itemDoubleClicked.connect(self.edit_domain_check)
    
    def load_data(self, config):
        """Charger les vérifications de domaine."""
        if not config:
            return
            
        self.domain_checks_list.clear()
        domain_checks = config.get_domain_checks() if hasattr(config, 'get_domain_checks') else []
        
        for check in domain_checks:
            if 'pattern' in check:  # Nouveau format avec pattern
                display_name = f"Pattern: {check['pattern']}"
            else:  # Ancien format avec variable/operator/value
                display_name = f"{check.get('variable', '')} {check.get('operator', '')} {check.get('value', '')}"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, check)
            self.domain_checks_list.addItem(item)
    
    def save_data(self, config):
        """Sauvegarder les vérifications de domaine dans la configuration."""
        if not config:
            return False
            
        domain_checks = []
        for i in range(self.domain_checks_list.count()):
            check = self.domain_checks_list.item(i).data(Qt.UserRole)
            domain_checks.append(check)
        
        if hasattr(config, 'set_domain_checks'):
            config.set_domain_checks(domain_checks)
        return True
    
    def add_domain_check(self):
        """Ajouter une vérification de domaine."""
        dialog = DomainCheckDialog(self)
        if dialog.exec_():
            check = dialog.get_domain_check()
            if check:
                display_name = f"{check['variable']} {check['operator']} {check['value']}"
                
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, check)
                self.domain_checks_list.addItem(item)
    
    def edit_domain_check(self, item=None):
        """Éditer une vérification de domaine."""
        if not item:
            item = self.domain_checks_list.currentItem()
        
        if not item:
            return
            
        check = item.data(Qt.UserRole)
        dialog = DomainCheckDialog(self, check)
        
        if dialog.exec_():
            updated_check = dialog.get_domain_check()
            if updated_check:
                display_name = f"{updated_check['variable']} {updated_check['operator']} {updated_check['value']}"
                
                item.setText(display_name)
                item.setData(Qt.UserRole, updated_check)
    
    def delete_domain_check(self):
        """Supprimer une vérification de domaine."""
        current_item = self.domain_checks_list.currentItem()
        if not current_item:
            return
            
        reply = QMessageBox.question(
            self, 
            'Confirmation', 
            'Êtes-vous sûr de vouloir supprimer cette vérification de domaine ?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.domain_checks_list.row(current_item)
            self.domain_checks_list.takeItem(row)