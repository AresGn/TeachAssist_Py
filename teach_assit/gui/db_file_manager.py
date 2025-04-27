"""
Widget pour la gestion des fichiers ZIP et dossiers extraits stockés dans la base de données.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                            QFileDialog, QFrame, QTreeWidget, QTreeWidgetItem, QSplitter,
                            QListWidget, QApplication)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
import os


class DatabaseFileManager(QWidget):
    """Widget pour gérer les fichiers ZIP et les dossiers extraits dans la base de données."""
    
    folder_selected = pyqtSignal(str)  # Signal émis quand un dossier est sélectionné
    
    def __init__(self, submission_manager=None, parent=None):
        """
        Initialise le gestionnaire de fichiers de la base de données.
        
        Args:
            submission_manager: Instance du gestionnaire de soumissions
            parent: Widget parent
        """
        super().__init__(parent)
        self.submission_manager = submission_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur du widget."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Titre principal
        title_label = QLabel("Gestionnaire de Fichiers ZIP")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title_label)
        
        # Barre de boutons principale
        main_button_bar = QWidget()
        main_button_layout = QHBoxLayout(main_button_bar)
        main_button_layout.setContentsMargins(0, 0, 0, 10)
        main_button_layout.setSpacing(10)
        
        # Bouton pour sélectionner un dossier avec les fichiers ZIP
        self.folder_button = QPushButton(" Sélectionner un Dossier")
        self.folder_button.setIcon(QIcon("icons/folder-plus.svg"))
        self.folder_button.setIconSize(QSize(28, 28))
        self.folder_button.setMinimumHeight(45)
        self.folder_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.folder_button.clicked.connect(self.select_folder)
        main_button_layout.addWidget(self.folder_button)
        
        # Bouton pour extraire tous les fichiers ZIP
        self.extract_all_button = QPushButton(" Extraire Tous les ZIP")
        self.extract_all_button.setIcon(QIcon("icons/download.svg"))
        self.extract_all_button.setIconSize(QSize(28, 28))
        self.extract_all_button.setMinimumHeight(45)
        self.extract_all_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        self.extract_all_button.clicked.connect(self.extract_all_zip_files)
        self.extract_all_button.setEnabled(False)  # Désactivé par défaut
        main_button_layout.addWidget(self.extract_all_button)
        
        main_button_layout.addStretch()
        
        # Bouton d'actualisation
        refresh_button = QPushButton(" Actualiser")
        refresh_button.setIcon(QIcon("icons/refresh-cw.svg"))
        refresh_button.clicked.connect(self.refresh_data)
        main_button_layout.addWidget(refresh_button)
        
        main_layout.addWidget(main_button_bar)
        
        # Information sur le dossier sélectionné
        self.folder_info = QLabel("Aucun dossier sélectionné")
        self.folder_info.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            padding: 10px;
            background-color: #f5f6fa;
            border-radius: 5px;
        """)
        main_layout.addWidget(self.folder_info)
        
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
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(15)
        
        # Splitter pour diviser la vue
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)
        
        # Section liste des fichiers ZIP
        zip_container = QFrame()
        zip_container.setFrameShape(QFrame.StyledPanel)
        zip_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dcdde1;
            }
        """)
        zip_layout = QVBoxLayout(zip_container)
        
        # En-tête de la liste des fichiers ZIP
        zip_header = QWidget()
        zip_header_layout = QHBoxLayout(zip_header)
        zip_header_layout.setContentsMargins(0, 0, 0, 10)
        
        zip_icon_label = QLabel()
        zip_icon_label.setPixmap(QIcon("icons/file-text.svg").pixmap(24, 24))
        zip_header_layout.addWidget(zip_icon_label)
        
        self.file_label = QLabel("Fichiers ZIP trouvés :")
        self.file_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        zip_header_layout.addWidget(self.file_label)
        zip_header_layout.addStretch()
        
        zip_layout.addWidget(zip_header)
        
        # Liste des fichiers ZIP dans le dossier sélectionné
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
        
        zip_layout.addWidget(self.file_list)
        
        # Ajout du conteneur au splitter
        splitter.addWidget(zip_container)
        
        # Section pour les fichiers extraits et la base de données
        db_container = QFrame()
        db_container.setFrameShape(QFrame.StyledPanel)
        db_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dcdde1;
            }
        """)
        db_layout = QVBoxLayout(db_container)
        
        # En-tête des fichiers extraits
        extract_header = QWidget()
        extract_header_layout = QHBoxLayout(extract_header)
        extract_header_layout.setContentsMargins(0, 0, 0, 10)
        
        extract_icon_label = QLabel()
        extract_icon_label.setPixmap(QIcon("icons/database.svg").pixmap(24, 24))
        extract_header_layout.addWidget(extract_icon_label)
        
        self.extract_title = QLabel("Fichiers dans la base de données")
        self.extract_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        extract_header_layout.addWidget(self.extract_title)
        extract_header_layout.addStretch()
        
        db_layout.addWidget(extract_header)
        
        # Table des fichiers ZIP extraits dans la base de données
        self.zip_table = QTableWidget()
        self.zip_table.setColumnCount(5)  # Suppression de la colonne Actions
        self.zip_table.setHorizontalHeaderLabels([
            "ID", "Nom du fichier", "Taille", "Date d'import", "Hash MD5"
        ])
        self.zip_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Étirer la colonne du nom
        self.zip_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Étirer la colonne du hash
        self.zip_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.zip_table.setSelectionMode(QTableWidget.SingleSelection)
        self.zip_table.setAlternatingRowColors(True)
        self.zip_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ecf0f1;
                alternate-background-color: #f5f6fa;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: 1px solid #dcdde1;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        
        self.zip_table.cellClicked.connect(self.on_zip_selected)
        
        db_layout.addWidget(self.zip_table)
        
        # Ajout du conteneur au splitter
        splitter.addWidget(db_container)
        
        # Section pour visualiser le contenu des fichiers
        content_container = QFrame()
        content_container.setFrameShape(QFrame.StyledPanel)
        content_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dcdde1;
            }
        """)
        content_layout = QVBoxLayout(content_container)
        
        # En-tête du contenu
        content_header = QWidget()
        content_header_layout = QHBoxLayout(content_header)
        content_header_layout.setContentsMargins(0, 0, 0, 10)
        
        content_icon_label = QLabel()
        content_icon_label.setPixmap(QIcon("icons/folder.svg").pixmap(24, 24))
        content_header_layout.addWidget(content_icon_label)
        
        self.content_title = QLabel("Contenu extrait")
        self.content_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        content_header_layout.addWidget(self.content_title)
        content_header_layout.addStretch()
        
        content_layout.addWidget(content_header)
        
        # Arborescence pour visualiser le contenu des fichiers
        self.tree_view = QTreeWidget()
        self.tree_view.setHeaderLabels(["Nom", "Taille", "Type", "Chemin"])
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_view.header().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setStyleSheet("""
            QTreeWidget {
                gridline-color: #ecf0f1;
                alternate-background-color: #f5f6fa;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: 1px solid #dcdde1;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        
        content_layout.addWidget(self.tree_view)
        
        # Ajout du conteneur au splitter
        splitter.addWidget(content_container)
        
        # Définir les tailles initiales du splitter
        splitter.setSizes([250, 250, 400])
        
        # Ajouter le splitter au layout du conteneur
        container_layout.addWidget(splitter)
        
        # Ajouter le conteneur principal au layout
        main_layout.addWidget(main_container)
        
        # Initialiser les données
        self.refresh_data()
    
    def select_folder(self):
        """Ouvrir une boîte de dialogue pour sélectionner un dossier contenant des fichiers ZIP."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un dossier de soumissions",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            # Animation de transition pour le label
            self.animate_label_change(self.folder_info, folder)
            
            # Définir le dossier de base dans le gestionnaire de soumissions
            if self.submission_manager:
                self.submission_manager.set_base_directory(folder)
            
            # Émettre le signal
            self.folder_selected.emit(folder)
            
            # Mettre à jour la liste des fichiers
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
        self.file_list.clear()
        try:
            # Utiliser le gestionnaire de soumissions pour lister les fichiers
            if self.submission_manager:
                files = self.submission_manager.list_zip_files()
            else:
                files = [f for f in os.listdir(folder_path) if f.lower().endswith('.zip')]
            
            for file in files:
                self.file_list.addItem(file)
            self.file_label.setText(f"Fichiers ZIP trouvés ({len(files)})")
            
            # Activer ou désactiver le bouton d'extraction
            self.extract_all_button.setEnabled(len(files) > 0)
        except Exception as e:
            self.file_label.setText(f"Erreur lors de la lecture du dossier: {str(e)}")
            self.file_list.addItem("Erreur: Impossible de lire le contenu du dossier")
            self.extract_all_button.setEnabled(False)
    
    def extract_all_zip_files(self):
        """Extraire tous les fichiers ZIP du dossier sélectionné."""
        if not self.submission_manager:
            QMessageBox.warning(self, "Erreur", "Gestionnaire de soumissions non disponible")
            return
        
        zip_files = self.submission_manager.list_zip_files()
        if not zip_files:
            QMessageBox.warning(self, "Aucun fichier ZIP", 
                              "Aucun fichier ZIP n'a été trouvé dans le dossier sélectionné.")
            return
        
        # Créer une boîte de dialogue de progression
        progress = QMessageBox()
        progress.setWindowTitle("Extraction en cours")
        progress.setText(f"Extraction de {len(zip_files)} fichiers ZIP...\nCette opération peut prendre quelques instants.")
        progress.setStandardButtons(QMessageBox.NoButton)
        progress.setIcon(QMessageBox.Information)
        progress.show()
        QApplication.processEvents()
        
        # Extraire les fichiers ZIP
        try:
            results = self.submission_manager.extract_all_zip_files()
            
            # Fermer la boîte de dialogue de progression
            progress.close()
            
            # Mettre à jour les vues
            self.refresh_data()
            
            # Afficher un résumé dans un message
            success_count = sum(1 for result in results.values() if result[0])
            QMessageBox.information(self, "Extraction terminée", 
                                  f"{success_count} fichier(s) sur {len(results)} ont été extraits avec succès et stockés dans la base de données.")
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Erreur lors de l'extraction", str(e))
    
    def refresh_data(self):
        """Actualise les données depuis la base de données."""
        # Récupérer les fichiers ZIP
        if self.submission_manager:
            # Mettre à jour la liste des fichiers
            if self.submission_manager.base_dir:
                self.update_file_list(self.submission_manager.base_dir)
            
            # Mettre à jour la table des fichiers dans la base de données
            self.update_zip_table()
            
            # Effacer l'arborescence
            self.clear_tree_view()
    
    def update_zip_table(self):
        """Met à jour la table des fichiers ZIP."""
        zip_files = self.submission_manager.get_all_zip_files_from_db()
        
        self.zip_table.setRowCount(len(zip_files))
        self.zip_table.setColumnCount(5)  # Suppression de la colonne Actions
        self.zip_table.setHorizontalHeaderLabels([
            "ID", "Nom du fichier", "Taille", "Date d'import", "Hash MD5"
        ])
        
        for row, zip_file in enumerate(zip_files):
            # ID
            id_item = QTableWidgetItem(str(zip_file[0]))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.zip_table.setItem(row, 0, id_item)
            
            # Nom du fichier
            filename_item = QTableWidgetItem(zip_file[1])
            filename_item.setIcon(QIcon("icons/file-text.svg"))
            self.zip_table.setItem(row, 1, filename_item)
            
            # Taille
            size_bytes = zip_file[3]
            size_display = self.format_file_size(size_bytes)
            size_item = QTableWidgetItem(size_display)
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.zip_table.setItem(row, 2, size_item)
            
            # Date d'import
            date_item = QTableWidgetItem(zip_file[4])
            date_item.setTextAlignment(Qt.AlignCenter)
            self.zip_table.setItem(row, 3, date_item)
            
            # Hash MD5
            hash_item = QTableWidgetItem(zip_file[5] if zip_file[5] else "N/A")
            self.zip_table.setItem(row, 4, hash_item)
    
    def clear_tree_view(self):
        """Efface l'arborescence des fichiers extraits."""
        self.tree_view.clear()
        self.content_title.setText("Contenu extrait")
    
    def on_zip_selected(self, row, column):
        """Gère la sélection d'un fichier ZIP dans la table."""
        if column != 5:  # Ignorer les clics sur la colonne d'actions
            zip_id = int(self.zip_table.item(row, 0).text())
            zip_name = self.zip_table.item(row, 1).text()
            self.show_zip_content(zip_id, zip_name)
    
    def show_zip_content(self, zip_id, zip_name=None):
        """Affiche le contenu d'un fichier ZIP."""
        if not zip_name:
            # Rechercher le nom à partir de l'ID
            for row in range(self.zip_table.rowCount()):
                if int(self.zip_table.item(row, 0).text()) == zip_id:
                    zip_name = self.zip_table.item(row, 1).text()
                    break
        
        self.content_title.setText(f"Contenu de {zip_name}")
        
        # Récupérer les dossiers extraits
        extracted_folders = self.submission_manager.get_extracted_folders_from_db(zip_id)
        
        # Effacer la vue existante
        self.tree_view.clear()
        
        # Ajouter les dossiers extraits à l'arborescence
        for folder in extracted_folders:
            folder_id = folder[0]
            folder_path = folder[1]
            folder_date = folder[2]
            folder_status = folder[3]
            
            # Créer un élément de dossier
            folder_item = QTreeWidgetItem(self.tree_view)
            folder_item.setText(0, os.path.basename(folder_path))
            folder_item.setText(1, "")
            folder_item.setText(2, "Dossier")
            folder_item.setText(3, folder_path)
            folder_item.setIcon(0, QIcon("icons/folder.svg"))
            
            # Marquer le dossier en tant que tel
            folder_item.setData(0, Qt.UserRole, "folder")
            folder_item.setData(0, Qt.UserRole + 1, folder_id)
            
            # Récupérer les fichiers dans ce dossier
            extracted_files = self.submission_manager.get_extracted_files_from_db(folder_id)
            
            # Ajouter les fichiers
            for file in extracted_files:
                file_id = file[0]
                file_path = file[1]
                file_size = file[2]
                file_type = file[3] or "inconnu"
                
                # Créer un élément de fichier
                file_item = QTreeWidgetItem(folder_item)
                file_item.setText(0, os.path.basename(file_path))
                file_item.setText(1, self.format_file_size(file_size))
                file_item.setText(2, file_type)
                file_item.setText(3, file_path)
                
                # Définir l'icône en fonction du type de fichier
                if file_type.lower() in ["java"]:
                    file_item.setIcon(0, QIcon("icons/code.svg"))
                elif file_type.lower() in ["txt", "md", "log"]:
                    file_item.setIcon(0, QIcon("icons/file-text.svg"))
                elif file_type.lower() in ["zip", "tar", "gz"]:
                    file_item.setIcon(0, QIcon("icons/archive.svg"))
                else:
                    file_item.setIcon(0, QIcon("icons/file.svg"))
                
                # Marquer le fichier en tant que tel
                file_item.setData(0, Qt.UserRole, "file")
                file_item.setData(0, Qt.UserRole + 1, file_id)
        
        # Développer tous les éléments
        self.tree_view.expandAll()
    
    def format_file_size(self, size_bytes):
        """Formate une taille en octets en une chaîne lisible."""
        if size_bytes < 1024:
            return f"{size_bytes} o"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} Ko"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} Mo"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} Go" 