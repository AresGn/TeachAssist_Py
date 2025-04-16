from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QLabel, QHeaderView, QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor


class SubmissionTreeWidget(QWidget):
    """Widget pour afficher les soumissions extraites dans une arborescence."""
    
    STATUS_ICONS = {
        "Succès": "check-circle",
        "Erreur": "alert-circle",
        "En attente": "clock"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
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
        container_layout.setSpacing(10)
        
        # En-tête avec icône
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("icons/users.svg").pixmap(24, 24))
        header_layout.addWidget(icon_label)
        
        self.info_label = QLabel("Soumissions extraites :")
        self.info_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(self.info_label)
        header_layout.addStretch()
        
        container_layout.addWidget(header)
        
        # Arborescence des soumissions avec style
        self.tree = QTreeWidget()
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: white;
                padding: 5px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }
            QTreeWidget::item:selected {
                background-color: #f1f2f6;
                color: #2c3e50;
            }
            QTreeWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dcdde1;
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        self.tree.setHeaderLabels(["Soumission", "Statut"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tree.setIconSize(QSize(20, 20))
        self.tree.setAlternatingRowColors(True)
        
        container_layout.addWidget(self.tree)
        
        layout.addWidget(main_container)
        self.setLayout(layout)
    
    def _get_status_icon(self, status):
        """Obtenir l'icône correspondant au statut."""
        if not status:
            return QIcon()
        
        icon_name = self.STATUS_ICONS.get(status, "help-circle")
        return QIcon(f"icons/{icon_name}.svg")
    
    def _get_status_color(self, status):
        """Obtenir la couleur correspondant au statut."""
        colors = {
            "Succès": "#2ecc71",
            "Erreur": "#e74c3c",
            "En attente": "#f1c40f"
        }
        return colors.get(status, "#7f8c8d")
    
    def update_tree(self, student_folders, extraction_results=None):
        """Mettre à jour l'arborescence avec les dossiers d'étudiants extraits.
        
        Args:
            student_folders: Dictionnaire {nom_etudiant: {path: chemin, java_files: [liste_fichiers]}}
            extraction_results: Dictionnaire des résultats d'extraction {nom_zip: (succès, message)}
        """
        self.tree.clear()
        
        if not student_folders:
            self.info_label.setText("Aucune soumission extraite")
            empty_item = QTreeWidgetItem(self.tree, ["Aucune soumission disponible", ""])
            empty_item.setIcon(0, QIcon("icons/alert-circle.svg"))
            return
        
        self.info_label.setText(f"Soumissions extraites ({len(student_folders)})")
        
        # Création des éléments d'arborescence pour chaque étudiant
        for student_name, info in student_folders.items():
            # Création de l'élément parent (étudiant)
            status = ""
            if extraction_results and f"{student_name}.zip" in extraction_results:
                success, message = extraction_results[f"{student_name}.zip"]
                status = "Succès" if success else "Erreur"
            
            student_item = QTreeWidgetItem(self.tree, [student_name, status])
            student_item.setIcon(0, QIcon("icons/user.svg"))
            
            if status:
                student_item.setIcon(1, self._get_status_icon(status))
                student_item.setForeground(1, QColor(self._get_status_color(status)))
            
            student_item.setExpanded(True)  # Déplier par défaut
            
            # Ajout des fichiers Java comme enfants
            java_files = info.get('java_files', [])
            
            if not java_files:
                no_files_item = QTreeWidgetItem(student_item, ["Aucun fichier Java trouvé", ""])
                no_files_item.setIcon(0, QIcon("icons/alert-triangle.svg"))
            else:
                for java_file in java_files:
                    file_item = QTreeWidgetItem(student_item, [java_file, ""])
                    file_item.setIcon(0, QIcon("icons/file-text.svg"))
        
        # Ajustement automatique de la largeur des colonnes
        self.tree.resizeColumnToContents(0)
    
    def clear(self):
        """Effacer l'arborescence."""
        self.tree.clear()
        self.info_label.setText("Soumissions extraites") 