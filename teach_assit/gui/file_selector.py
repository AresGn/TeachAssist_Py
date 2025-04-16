from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog, 
                             QListWidget, QLabel, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal


class FileSelector(QWidget):
    """Widget pour sélectionner un dossier et afficher les fichiers ZIP à l'intérieur."""
    
    folder_selected = pyqtSignal(str)  # Signal émis quand un dossier est sélectionné
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur du sélecteur de fichiers."""
        layout = QVBoxLayout()
        
        # Partie supérieure : sélection de dossier
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Aucun dossier sélectionné")
        folder_layout.addWidget(self.folder_label)
        
        self.select_folder_button = QPushButton("Sélectionner un dossier")
        self.select_folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.select_folder_button)
        
        layout.addLayout(folder_layout)
        
        # Liste des fichiers ZIP
        self.file_label = QLabel("Fichiers ZIP trouvés :")
        layout.addWidget(self.file_label)
        
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        self.setLayout(layout)
        
    def select_folder(self):
        """Ouvrir une boîte de dialogue pour sélectionner un dossier."""
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier de soumissions")
        if folder:
            self.folder_label.setText(folder)
            self.folder_selected.emit(folder)
            self.update_file_list(folder)
    
    def update_file_list(self, folder_path):
        """Mettre à jour la liste des fichiers ZIP dans le dossier sélectionné."""
        import os
        self.file_list.clear()
        try:
            files = [f for f in os.listdir(folder_path) if f.lower().endswith('.zip')]
            for file in files:
                self.file_list.addItem(file)
            self.file_label.setText(f"Fichiers ZIP trouvés ({len(files)}) :")
        except Exception as e:
            self.file_label.setText(f"Erreur lors de la lecture du dossier: {str(e)}") 