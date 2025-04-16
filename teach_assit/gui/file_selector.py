from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog, 
                             QListWidget, QLabel, QHBoxLayout, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QColor, QPalette


class FileSelector(QWidget):
    """Widget pour sélectionner un dossier et afficher les fichiers ZIP à l'intérieur."""
    
    folder_selected = pyqtSignal(str)  # Signal émis quand un dossier est sélectionné
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur du sélecteur de fichiers."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Conteneur principal avec style
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #dcdde1;
            }
        """)
        container_layout = QVBoxLayout(main_container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(15, 15, 15, 15)
        
        # Partie supérieure : sélection de dossier
        folder_widget = QFrame()
        folder_widget.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        folder_layout = QHBoxLayout(folder_widget)
        folder_layout.setContentsMargins(10, 10, 10, 10)
        
        folder_icon = QLabel()
        folder_icon.setPixmap(QIcon("icons/folder.svg").pixmap(24, 24))
        folder_layout.addWidget(folder_icon)
        
        self.folder_label = QLabel("Aucun dossier sélectionné")
        self.folder_label.setStyleSheet("""
            color: #2c3e50;
            padding: 5px;
        """)
        folder_layout.addWidget(self.folder_label, 1)
        
        self.select_folder_button = QPushButton("Sélectionner")
        self.select_folder_button.setIcon(QIcon("icons/folder-plus.svg"))
        self.select_folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.select_folder_button)
        
        container_layout.addWidget(folder_widget)
        
        # Liste des fichiers ZIP avec en-tête
        files_header = QWidget()
        files_header_layout = QHBoxLayout(files_header)
        files_header_layout.setContentsMargins(0, 0, 0, 0)
        
        zip_icon = QLabel()
        zip_icon.setPixmap(QIcon("icons/file-text.svg").pixmap(20, 20))
        files_header_layout.addWidget(zip_icon)
        
        self.file_label = QLabel("Fichiers ZIP trouvés :")
        self.file_label.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
        """)
        files_header_layout.addWidget(self.file_label)
        files_header_layout.addStretch()
        
        container_layout.addWidget(files_header)
        
        # Liste des fichiers avec style
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }
            QListWidget::item:selected {
                background-color: #f1f2f6;
                color: #2c3e50;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        self.file_list.setAlternatingRowColors(True)
        palette = self.file_list.palette()
        palette.setColor(QPalette.AlternateBase, QColor("#fafbfc"))
        self.file_list.setPalette(palette)
        
        container_layout.addWidget(self.file_list)
        
        layout.addWidget(main_container)
        self.setLayout(layout)
    
    def select_folder(self):
        """Ouvrir une boîte de dialogue pour sélectionner un dossier."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un dossier de soumissions",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            # Animation de transition pour le label
            self.animate_label_change(self.folder_label, folder)
            self.folder_selected.emit(folder)
            self.update_file_list(folder)
    
    def animate_label_change(self, label, new_text):
        """Animer le changement de texte d'un label."""
        # Animation de fondu
        fade_out = QPropertyAnimation(label, b"windowOpacity")
        fade_out.setDuration(150)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.OutQuad)
        
        fade_in = QPropertyAnimation(label, b"windowOpacity")
        fade_in.setDuration(150)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InQuad)
        
        fade_out.finished.connect(lambda: self._update_label_text(label, new_text, fade_in))
        fade_out.start()
    
    def _update_label_text(self, label, text, fade_in):
        """Mettre à jour le texte du label et démarrer l'animation de fondu."""
        label.setText(text)
        fade_in.start()
    
    def update_file_list(self, folder_path):
        """Mettre à jour la liste des fichiers ZIP dans le dossier sélectionné."""
        import os
        self.file_list.clear()
        try:
            files = [f for f in os.listdir(folder_path) if f.lower().endswith('.zip')]
            for file in files:
                self.file_list.addItem(file)
            self.file_label.setText(f"Fichiers ZIP trouvés ({len(files)})")
        except Exception as e:
            self.file_label.setText(f"Erreur lors de la lecture du dossier: {str(e)}")
            self.file_list.addItem("Erreur: Impossible de lire le contenu du dossier") 