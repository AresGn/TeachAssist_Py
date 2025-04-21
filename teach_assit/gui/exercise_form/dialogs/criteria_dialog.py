from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QSpinBox, QPushButton, QListWidget, QListWidgetItem,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt

class CriteriaDialog(QDialog):
    """Dialogue pour ajouter ou modifier un critère de notation."""
    
    def __init__(self, parent=None, criteria=None):
        super().__init__(parent)
        self.criteria = criteria or {'subcriteria': []}
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        self.setWindowTitle("Critère de notation")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Titre du critère
        self.title_edit = QLineEdit()
        if self.criteria.get('title'):
            self.title_edit.setText(self.criteria['title'])
        form_layout.addRow("Titre du critère :", self.title_edit)
        
        # Points attribués
        self.points_edit = QSpinBox()
        self.points_edit.setMinimum(1)
        self.points_edit.setMaximum(20)
        self.points_edit.setValue(self.criteria.get('points', 4))
        form_layout.addRow("Points :", self.points_edit)
        
        # Description du critère
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        if self.criteria.get('description'):
            self.description_edit.setText(self.criteria['description'])
        self.description_edit.setPlaceholderText("Décrivez les sous-critères et leur évaluation...")
        form_layout.addRow("Description :", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Sous-critères
        form_layout = QFormLayout()
        self.subcriteria_list = QListWidget()
        for subcriteria in self.criteria.get('subcriteria', []):
            item = QListWidgetItem(subcriteria['text'])
            item.setData(Qt.UserRole, subcriteria)
            self.subcriteria_list.addItem(item)
        form_layout.addRow("Sous-critères :", self.subcriteria_list)
        
        # Boutons pour les sous-critères
        subcriteria_buttons = QHBoxLayout()
        
        add_subcriteria_button = QPushButton("Ajouter")
        add_subcriteria_button.clicked.connect(self.add_subcriteria)
        subcriteria_buttons.addWidget(add_subcriteria_button)
        
        edit_subcriteria_button = QPushButton("Éditer")
        edit_subcriteria_button.clicked.connect(self.edit_subcriteria)
        subcriteria_buttons.addWidget(edit_subcriteria_button)
        
        delete_subcriteria_button = QPushButton("Supprimer")
        delete_subcriteria_button.clicked.connect(self.delete_subcriteria)
        subcriteria_buttons.addWidget(delete_subcriteria_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(subcriteria_buttons)
        
        # Boutons principaux
        buttons = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        buttons.addWidget(ok_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
    
    def add_subcriteria(self):
        """Ajouter un sous-critère."""
        text, ok = QInputDialog.getText(
            self, 
            "Ajouter un sous-critère", 
            "Description du sous-critère:"
        )
        
        if ok and text:
            subcriteria = {'text': text}
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, subcriteria)
            self.subcriteria_list.addItem(item)
    
    def edit_subcriteria(self):
        """Éditer un sous-critère."""
        current_item = self.subcriteria_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un sous-critère à éditer.")
            return
        
        subcriteria = current_item.data(Qt.UserRole)
        if not subcriteria:
            return
        
        text, ok = QInputDialog.getText(
            self, 
            "Éditer un sous-critère", 
            "Description du sous-critère:",
            text=subcriteria['text']
        )
        
        if ok and text:
            subcriteria['text'] = text
            current_item.setText(text)
            current_item.setData(Qt.UserRole, subcriteria)
    
    def delete_subcriteria(self):
        """Supprimer un sous-critère."""
        current_item = self.subcriteria_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un sous-critère à supprimer.")
            return
        
        row = self.subcriteria_list.row(current_item)
        self.subcriteria_list.takeItem(row)
    
    def get_criteria(self):
        """Récupérer les données du critère."""
        title = self.title_edit.text().strip()
        points = self.points_edit.value()
        description = self.description_edit.toPlainText().strip()
        
        if not title:
            return None
        
        result = {
            'title': title,
            'points': points,
            'description': description,
            'subcriteria': []
        }
        
        # Récupérer les sous-critères
        for i in range(self.subcriteria_list.count()):
            subcriteria = self.subcriteria_list.item(i).data(Qt.UserRole)
            result['subcriteria'].append(subcriteria)
        
        return result 